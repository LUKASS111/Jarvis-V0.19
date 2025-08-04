#!/usr/bin/env python3
"""
Consolidated Log Management System for Jarvis V0.19
Redesigned to minimize file count while preserving all log information.
"""

import os
import sys
import json
import time
import gzip
import threading
from datetime import datetime, timedelta
from pathlib import Path
from collections import defaultdict
import tempfile

class ConsolidatedLogManager:
    """
    Advanced log manager that consolidates multiple log entries into fewer files
    while maintaining all functionality and easy retrieval.
    """
    
    def __init__(self, base_dir=None):
        self.base_dir = Path(base_dir) if base_dir else Path(__file__).parent.parent
        self.log_root = self.base_dir / "tests" / "output" / "consolidated_logs"
        self.log_root.mkdir(parents=True, exist_ok=True)
        
        # Configuration
        self.max_log_size = 10 * 1024 * 1024  # 10MB per consolidated file
        self.max_files_per_category = 5  # Maximum rotated files per category
        self.compression_enabled = True
        self.buffer_size = 1000  # Number of entries to buffer before writing
        
        # Internal state
        self.log_buffers = defaultdict(list)
        self.log_counters = defaultdict(int)
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.lock = threading.Lock()
        
        # Categories for different log types
        self.log_categories = {
            'test_execution': 'test_exec',
            'agent_reports': 'agent',
            'compliance': 'compliance', 
            'performance': 'perf',
            'errors': 'error',
            'system': 'system',
            'crdt': 'crdt',
            'network': 'network'
        }
        
        print(f"[LOG_MANAGER] Initialized consolidated logging system - Session: {self.session_id}")
    
    def log_entry(self, category, data, context=None):
        """
        Add a log entry to the specified category buffer.
        
        Args:
            category: Log category (test_execution, agent_reports, etc.)
            data: The data to log (dict, string, or any JSON-serializable)
            context: Optional context information
        """
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            'timestamp': timestamp,
            'session_id': self.session_id,
            'category': category,
            'context': context,
            'data': data
        }
        
        with self.lock:
            self.log_buffers[category].append(log_entry)
            self.log_counters[category] += 1
            
            # Auto-flush if buffer is full
            if len(self.log_buffers[category]) >= self.buffer_size:
                self._flush_category(category)
    
    def _flush_category(self, category):
        """Flush buffered entries for a category to disk"""
        if not self.log_buffers[category]:
            return
            
        category_code = self.log_categories.get(category, category[:8])
        filename = f"{category_code}_{self.session_id}.jsonl"
        filepath = self.log_root / filename
        
        # Write entries to file
        entries_written = 0
        with open(filepath, 'a', encoding='utf-8') as f:
            for entry in self.log_buffers[category]:
                f.write(json.dumps(entry, ensure_ascii=False) + '\n')
                entries_written += 1
        
        # Clear buffer
        self.log_buffers[category].clear()
        
        # Check if file needs rotation
        if filepath.stat().st_size > self.max_log_size:
            self._rotate_log_file(filepath, category_code)
        
        print(f"[LOG_MANAGER] Flushed {entries_written} entries to {filename}")
    
    def _rotate_log_file(self, current_file, category_code):
        """Rotate log file when it gets too large"""
        base_path = current_file.parent
        base_name = current_file.stem
        
        # Compress and rotate existing files
        for i in range(self.max_files_per_category - 1, 0, -1):
            old_file = base_path / f"{base_name}.{i}.gz"
            new_file = base_path / f"{base_name}.{i + 1}.gz"
            if old_file.exists():
                if i == self.max_files_per_category - 1:
                    old_file.unlink()  # Delete oldest
                else:
                    old_file.rename(new_file)
        
        # Compress current file to .1.gz
        compressed_file = base_path / f"{base_name}.1.gz"
        with open(current_file, 'rb') as f_in:
            with gzip.open(compressed_file, 'wb') as f_out:
                f_out.write(f_in.read())
        
        # Clear current file
        current_file.unlink()
        
        print(f"[LOG_MANAGER] Rotated log file: {compressed_file}")
    
    def flush_all(self):
        """Flush all buffered entries to disk"""
        with self.lock:
            for category in list(self.log_buffers.keys()):
                self._flush_category(category)
        
        print(f"[LOG_MANAGER] Flushed all log buffers for session {self.session_id}")
    
    def create_session_summary(self):
        """Create a comprehensive summary of the current session"""
        summary = {
            'session_id': self.session_id,
            'created_at': datetime.now().isoformat(),
            'categories': {},
            'total_entries': 0,
            'files_created': []
        }
        
        # Scan log directory for session files
        session_files = list(self.log_root.glob(f"*_{self.session_id}*"))
        
        for log_file in session_files:
            category = log_file.stem.split('_')[0]
            
            # Count entries in file
            entry_count = 0
            file_size = 0
            
            try:
                if log_file.suffix == '.gz':
                    with gzip.open(log_file, 'rt', encoding='utf-8') as f:
                        entry_count = sum(1 for _ in f)
                else:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        entry_count = sum(1 for _ in f)
                file_size = log_file.stat().st_size
            except Exception as e:
                print(f"[WARN] Could not read {log_file}: {e}")
            
            summary['categories'][category] = {
                'entries': entry_count,
                'file_size': file_size,
                'file_path': str(log_file.relative_to(self.base_dir))
            }
            
            summary['total_entries'] += entry_count
            summary['files_created'].append(str(log_file.relative_to(self.base_dir)))
        
        # Add buffer counts
        for category, buffer in self.log_buffers.items():
            if category not in summary['categories']:
                summary['categories'][category] = {'entries': 0, 'file_size': 0}
            summary['categories'][category]['buffered_entries'] = len(buffer)
        
        # Save summary
        summary_file = self.log_root / f"session_summary_{self.session_id}.json"
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, indent=2, ensure_ascii=False)
        
        print(f"[LOG_MANAGER] Session summary saved: {summary_file}")
        print(f"               Total entries: {summary['total_entries']}")
        print(f"               Files created: {len(summary['files_created'])}")
        
        return summary
    
    def cleanup_old_sessions(self, keep_days=7):
        """Remove log files older than specified days"""
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        cutoff_timestamp = cutoff_date.strftime("%Y%m%d")
        
        removed_files = []
        for log_file in self.log_root.iterdir():
            if log_file.is_file():
                # Extract timestamp from filename
                parts = log_file.stem.split('_')
                if len(parts) >= 2:
                    try:
                        file_timestamp = parts[-1][:8]  # YYYYMMDD
                        if file_timestamp < cutoff_timestamp:
                            log_file.unlink()
                            removed_files.append(str(log_file))
                    except (ValueError, IndexError):
                        continue
        
        if removed_files:
            print(f"[LOG_MANAGER] Cleaned up {len(removed_files)} old log files")
        
        return removed_files
    
    def get_logs_by_category(self, category, session_id=None):
        """Retrieve all logs for a specific category and session"""
        session_id = session_id or self.session_id
        category_code = self.log_categories.get(category, category[:8])
        
        logs = []
        
        # Check current buffer first
        if session_id == self.session_id:
            logs.extend(self.log_buffers[category])
        
        # Read from files
        pattern = f"{category_code}_{session_id}*"
        for log_file in self.log_root.glob(pattern):
            try:
                if log_file.suffix == '.gz':
                    with gzip.open(log_file, 'rt', encoding='utf-8') as f:
                        for line in f:
                            logs.append(json.loads(line.strip()))
                else:
                    with open(log_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            logs.append(json.loads(line.strip()))
            except Exception as e:
                print(f"[WARN] Could not read {log_file}: {e}")
        
        # Sort by timestamp
        logs.sort(key=lambda x: x.get('timestamp', ''))
        return logs
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.flush_all()
        self.create_session_summary()


class TestLogAdapter:
    """
    Adapter to integrate consolidated logging with existing test infrastructure
    """
    
    def __init__(self, log_manager):
        self.log_manager = log_manager
        self.test_start_time = None
        self.current_test_suite = None
    
    def start_test_suite(self, suite_name):
        """Mark the start of a test suite"""
        self.current_test_suite = suite_name
        self.test_start_time = time.time()
        
        self.log_manager.log_entry('test_execution', {
            'event': 'suite_start',
            'suite_name': suite_name,
            'start_time': datetime.now().isoformat()
        }, context=f"test_suite_{suite_name}")
    
    def log_test_result(self, test_name, status, duration, details=None):
        """Log individual test result"""
        self.log_manager.log_entry('test_execution', {
            'event': 'test_result',
            'suite_name': self.current_test_suite,
            'test_name': test_name,
            'status': status,
            'duration': duration,
            'details': details or {}
        }, context=f"test_{test_name}")
    
    def end_test_suite(self, total_tests, failures, errors):
        """Mark the end of a test suite"""
        duration = time.time() - self.test_start_time if self.test_start_time else 0
        
        self.log_manager.log_entry('test_execution', {
            'event': 'suite_end',
            'suite_name': self.current_test_suite,
            'duration': duration,
            'total_tests': total_tests,
            'failures': failures,
            'errors': errors,
            'success_rate': ((total_tests - failures - errors) / total_tests * 100) if total_tests > 0 else 0
        }, context=f"test_suite_{self.current_test_suite}")
    
    def log_agent_report(self, agent_data):
        """Log agent activity report"""
        self.log_manager.log_entry('agent_reports', agent_data, context='agent_activity')
    
    def log_compliance_data(self, compliance_data):
        """Log compliance information"""
        self.log_manager.log_entry('compliance', compliance_data, context='process_compliance')
    
    def log_performance_data(self, perf_data):
        """Log performance metrics"""
        self.log_manager.log_entry('performance', perf_data, context='performance_monitoring')
    
    def log_error(self, error_data):
        """Log error information"""
        self.log_manager.log_entry('errors', error_data, context='error_tracking')


def create_legacy_compatibility_layer():
    """
    Create compatibility layer for existing logging calls to work with new system
    """
    global _global_log_manager
    _global_log_manager = ConsolidatedLogManager()
    
    # Return adapter functions
    return {
        'log_manager': _global_log_manager,
        'test_adapter': TestLogAdapter(_global_log_manager),
        'legacy_log_function': lambda category, data, context=None: _global_log_manager.log_entry(category, data, context)
    }


if __name__ == "__main__":
    # Test the consolidated log manager
    print("Testing Consolidated Log Manager...")
    
    with ConsolidatedLogManager() as log_manager:
        test_adapter = TestLogAdapter(log_manager)
        
        # Simulate test logging
        test_adapter.start_test_suite("test_consolidated_logging")
        
        for i in range(10):
            test_adapter.log_test_result(f"test_case_{i}", "PASS", 0.1 + i * 0.01)
        
        test_adapter.end_test_suite(10, 0, 0)
        
        # Log some other data
        log_manager.log_entry('agent_reports', {'agent_id': 'test_agent', 'status': 'active'})
        log_manager.log_entry('performance', {'cpu_usage': 45.2, 'memory_usage': 67.8})
    
    print("Test completed. Check tests/output/consolidated_logs/ for results.")