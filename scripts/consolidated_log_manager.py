#!/usr/bin/env python3
"""
Consolidated Log Manager - Professional Test and System Logging
Designed to minimize file creation while preserving all essential data
"""

import os
import sys
import json
import uuid
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional

class ConsolidatedLogManager:
    """
    Professional logging system that consolidates all test and system logs
    into a minimal set of files while preserving complete functionality
    """
    
    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.session_id = datetime.now().strftime('%Y%m%d_%H%M%S')
        self.log_root = self.project_root / "archive" / "consolidated_logs"
        self.log_root.mkdir(parents=True, exist_ok=True)
        
        # Initialize log storage
        self.logs = {
            'test_execution': [],
            'agent_reports': [],
            'compliance': [],
            'performance': [],
            'errors': [],
            'system': [],
            'crdt': [],
            'network': []
        }
        
        # Session metadata
        self.session_metadata = {
            'session_id': self.session_id,
            'started_at': datetime.now().isoformat(),
            'platform': sys.platform,
            'project_root': str(self.project_root),
            'total_entries': 0
        }
        
        print(f"[LOG_MANAGER] Initialized session {self.session_id}")
    
    def log_entry(self, category: str, data: Dict[str, Any], context: str = None):
        """Add a log entry to the specified category"""
        if category not in self.logs:
            category = 'system'  # Default fallback
        
        entry = {
            'timestamp': datetime.now().isoformat(),
            'session_id': self.session_id,
            'context': context,
            'data': data
        }
        
        self.logs[category].append(entry)
        self.session_metadata['total_entries'] += 1
    
    def get_logs_by_category(self, category: str) -> List[Dict[str, Any]]:
        """Get all logs for a specific category"""
        return self.logs.get(category, [])
    
    def flush_category(self, category: str):
        """Write a specific category to disk"""
        if category not in self.logs or not self.logs[category]:
            return
        
        category_file = self.log_root / f"{category}_{self.session_id}.json"
        
        try:
            with open(category_file, 'w', encoding='utf-8') as f:
                json.dump({
                    'category': category,
                    'session_id': self.session_id,
                    'entries': self.logs[category],
                    'count': len(self.logs[category])
                }, f, indent=2, ensure_ascii=False)
            
            print(f"[LOG_MANAGER] Flushed {len(self.logs[category])} {category} entries")
            
        except Exception as e:
            print(f"[ERROR] Failed to flush {category}: {e}")
    
    def flush_all(self):
        """Write all categories to disk"""
        for category in self.logs.keys():
            if self.logs[category]:  # Only flush non-empty categories
                self.flush_category(category)
    
    def create_session_summary(self) -> Dict[str, Any]:
        """Create a comprehensive session summary"""
        self.session_metadata['completed_at'] = datetime.now().isoformat()
        
        # Calculate category statistics
        category_stats = {}
        for category, entries in self.logs.items():
            category_stats[category] = {
                'count': len(entries),
                'first_entry': entries[0]['timestamp'] if entries else None,
                'last_entry': entries[-1]['timestamp'] if entries else None
            }
        
        summary = {
            **self.session_metadata,
            'category_statistics': category_stats,
            'files_created': [
                f"{category}_{self.session_id}.json" 
                for category in self.logs.keys() 
                if self.logs[category]
            ]
        }
        
        # Write session summary
        summary_file = self.log_root / f"session_summary_{self.session_id}.json"
        
        try:
            with open(summary_file, 'w', encoding='utf-8') as f:
                json.dump(summary, f, indent=2, ensure_ascii=False)
            
            print(f"[LOG_MANAGER] Session summary created: {summary_file}")
            
        except Exception as e:
            print(f"[ERROR] Failed to create session summary: {e}")
        
        return summary
    
    def cleanup_current_sessions(self, keep_days: int = 3) -> List[str]:
        """Clean up old session files"""
        cutoff_date = datetime.now() - timedelta(days=keep_days)
        cleaned_files = []
        
        try:
            for log_file in self.log_root.glob("*.json"):
                file_time = datetime.fromtimestamp(log_file.stat().st_mtime)
                if file_time < cutoff_date:
                    log_file.unlink()
                    cleaned_files.append(str(log_file))
            
            if cleaned_files:
                print(f"[LOG_MANAGER] Cleaned {len(cleaned_files)} old log files")
                
        except Exception as e:
            print(f"[ERROR] Failed to clean old sessions: {e}")
        
        return cleaned_files


class TestLogAdapter:
    """
    Adapter for test-specific logging using ConsolidatedLogManager
    """
    
    def __init__(self, log_manager: ConsolidatedLogManager):
        self.log_manager = log_manager
        self.current_test_suite = None
        self.test_start_time = None
    
    def start_test_suite(self, test_name: str):
        """Mark the start of a test suite"""
        self.current_test_suite = test_name
        self.test_start_time = time.time()
        
        self.log_manager.log_entry('test_execution', {
            'event': 'test_suite_start',
            'test_name': test_name,
            'start_time': datetime.now().isoformat()
        }, context=f"test_suite_{test_name}")
    
    def end_test_suite(self, tests_run: int, failures: int, errors: int):
        """Mark the end of a test suite"""
        if self.current_test_suite and self.test_start_time:
            duration = time.time() - self.test_start_time
            
            self.log_manager.log_entry('test_execution', {
                'event': 'test_suite_end',
                'test_name': self.current_test_suite,
                'tests_run': tests_run,
                'failures': failures,
                'errors': errors,
                'duration': duration,
                'success_rate': ((tests_run - failures - errors) / tests_run * 100) if tests_run > 0 else 0
            }, context=f"test_suite_{self.current_test_suite}")
    
    def log_test_result(self, test_name: str, status: str, duration: float, metadata: Dict[str, Any]):
        """Log individual test result"""
        self.log_manager.log_entry('test_execution', {
            'event': 'individual_test',
            'test_name': test_name,
            'status': status,
            'duration': duration,
            'metadata': metadata
        }, context=f"test_{test_name}")
    
    def log_performance_data(self, performance_data: Dict[str, Any]):
        """Log performance metrics"""
        self.log_manager.log_entry('performance', performance_data, context="performance_metrics")