#!/usr/bin/env python3
"""
Log Cleanup Script for Jarvis-V0.19
Manages log files according to retention policies and storage limits.
"""

import os
import json
import time
import shutil
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Tuple

class LogCleanup:
    """Manages test logs and ensures storage limits are respected."""
    
    def __init__(self, base_path: str = None):
        self.base_path = Path(base_path) if base_path else Path(__file__).parent.parent
        self.logs_dir = self.base_path / "logs"
        self.config_path = self.base_path / "config" / "aggregation_config.json"
        
        # Load configuration
        self.config = self.load_config()
        
    def load_config(self) -> Dict:
        """Load cleanup configuration."""
        default_config = {
            "aggregation_config": {
                "max_log_age_days": 7,
                "max_total_log_size_mb": 500,
                "cleanup_rules": {
                    "delete_old_performance_logs": True,
                    "max_concurrent_log_files": 1000,
                    "max_performance_log_files": 2000,
                    "compress_large_logs": True,
                    "archive_old_reports": True
                }
            }
        }
        
        try:
            if self.config_path.exists():
                with open(self.config_path, 'r') as f:
                    return json.load(f)
            else:
                return default_config
        except Exception as e:
            print(f"[WARN] Could not load config: {e}, using defaults")
            return default_config
    
    def get_file_age_days(self, file_path: Path) -> float:
        """Get file age in days."""
        try:
            file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
            age = datetime.now() - file_time
            return age.total_seconds() / (24 * 3600)
        except:
            return 0
    
    def get_directory_size_mb(self, directory: Path) -> float:
        """Get total size of directory in MB."""
        total_size = 0
        try:
            for path in directory.rglob('*'):
                if path.is_file():
                    total_size += path.stat().st_size
        except:
            pass
        return total_size / (1024 * 1024)
    
    def cleanup_performance_logs(self) -> Tuple[int, float]:
        """Clean up old performance log files."""
        if not self.logs_dir.exists():
            return 0, 0
        
        cleanup_rules = self.config["aggregation_config"]["cleanup_rules"]
        max_age_days = self.config["aggregation_config"]["max_log_age_days"]
        max_concurrent = cleanup_rules.get("max_concurrent_log_files", 1000)
        max_performance = cleanup_rules.get("max_performance_log_files", 2000)
        
        files_deleted = 0
        space_freed = 0
        
        # Get all performance and concurrent log files
        perf_files = list(self.logs_dir.glob("perf_event_*.json"))
        concurrent_files = list(self.logs_dir.glob("concurrent_log_*.json"))
        
        print(f"[INFO] Found {len(perf_files)} performance logs, {len(concurrent_files)} concurrent logs")
        
        # Remove old files first
        for file_pattern in ["perf_event_*.json", "concurrent_log_*.json"]:
            for file_path in self.logs_dir.glob(file_pattern):
                age_days = self.get_file_age_days(file_path)
                if age_days > max_age_days:
                    try:
                        file_size = file_path.stat().st_size
                        file_path.unlink()
                        files_deleted += 1
                        space_freed += file_size / (1024 * 1024)
                    except Exception as e:
                        print(f"[WARN] Could not delete {file_path}: {e}")
        
        # If still too many files, remove oldest ones
        perf_files = list(self.logs_dir.glob("perf_event_*.json"))
        if len(perf_files) > max_performance:
            # Sort by modification time, oldest first
            perf_files.sort(key=lambda x: x.stat().st_mtime)
            files_to_remove = perf_files[:len(perf_files) - max_performance]
            
            for file_path in files_to_remove:
                try:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    files_deleted += 1
                    space_freed += file_size / (1024 * 1024)
                except Exception as e:
                    print(f"[WARN] Could not delete {file_path}: {e}")
        
        # Clean up concurrent logs
        concurrent_files = list(self.logs_dir.glob("concurrent_log_*.json"))
        if len(concurrent_files) > max_concurrent:
            concurrent_files.sort(key=lambda x: x.stat().st_mtime)
            files_to_remove = concurrent_files[:len(concurrent_files) - max_concurrent]
            
            for file_path in files_to_remove:
                try:
                    file_size = file_path.stat().st_size
                    file_path.unlink()
                    files_deleted += 1
                    space_freed += file_size / (1024 * 1024)
                except Exception as e:
                    print(f"[WARN] Could not delete {file_path}: {e}")
        
        return files_deleted, space_freed
    
    def cleanup_old_reports(self) -> Tuple[int, float]:
        """Clean up old aggregate reports."""
        retention_days = self.config["aggregation_config"].get("report_retention_days", 30)
        
        files_deleted = 0
        space_freed = 0
        
        for report_file in self.base_path.glob("TEST_AGGREGATE_REPORT_*"):
            age_days = self.get_file_age_days(report_file)
            if age_days > retention_days:
                try:
                    file_size = report_file.stat().st_size
                    report_file.unlink()
                    files_deleted += 1
                    space_freed += file_size / (1024 * 1024)
                except Exception as e:
                    print(f"[WARN] Could not delete {report_file}: {e}")
        
        return files_deleted, space_freed
    
    def cleanup_large_events(self) -> Tuple[int, float]:
        """Clean up large event files which can be regenerated."""
        files_deleted = 0
        space_freed = 0
        
        if not self.logs_dir.exists():
            return files_deleted, space_freed
        
        for large_event_file in self.logs_dir.glob("large_event_*.json"):
            try:
                file_size = large_event_file.stat().st_size
                # Remove large event files older than 1 day
                age_days = self.get_file_age_days(large_event_file)
                if age_days > 1:
                    large_event_file.unlink()
                    files_deleted += 1
                    space_freed += file_size / (1024 * 1024)
            except Exception as e:
                print(f"[WARN] Could not delete {large_event_file}: {e}")
        
        return files_deleted, space_freed
    
    def check_storage_limits(self) -> bool:
        """Check if storage limits are exceeded."""
        max_size_mb = self.config["aggregation_config"]["max_total_log_size_mb"]
        current_size_mb = self.get_directory_size_mb(self.logs_dir)
        
        print(f"[INFO] Current logs size: {current_size_mb:.1f}MB (limit: {max_size_mb}MB)")
        
        return current_size_mb > max_size_mb
    
    def run_cleanup(self, force: bool = False) -> Dict[str, any]:
        """Run complete cleanup process."""
        print("=" * 60)
        print("[LAUNCH] LOG CLEANUP SYSTEM")
        print("=" * 60)
        
        results = {
            "start_time": datetime.now().isoformat(),
            "initial_size_mb": self.get_directory_size_mb(self.logs_dir),
            "files_deleted": 0,
            "space_freed_mb": 0,
            "operations": []
        }
        
        # Check if cleanup is needed
        if not force and not self.check_storage_limits():
            print("[INFO] Storage within limits, no cleanup needed")
            return results
        
        # Clean up performance logs
        print("[CLEAN] Removing old performance and concurrent logs...")
        deleted, freed = self.cleanup_performance_logs()
        results["files_deleted"] += deleted
        results["space_freed_mb"] += freed
        results["operations"].append(f"Performance logs: {deleted} files, {freed:.1f}MB freed")
        
        # Clean up large events
        print("[CLEAN] Removing large event files...")
        deleted, freed = self.cleanup_large_events()
        results["files_deleted"] += deleted
        results["space_freed_mb"] += freed
        results["operations"].append(f"Large events: {deleted} files, {freed:.1f}MB freed")
        
        # Clean up old reports
        print("[CLEAN] Removing old aggregate reports...")
        deleted, freed = self.cleanup_old_reports()
        results["files_deleted"] += deleted
        results["space_freed_mb"] += freed
        results["operations"].append(f"Old reports: {deleted} files, {freed:.1f}MB freed")
        
        results["final_size_mb"] = self.get_directory_size_mb(self.logs_dir)
        results["end_time"] = datetime.now().isoformat()
        
        print(f"\n[COMPLETE] Cleanup finished:")
        print(f"  Files deleted: {results['files_deleted']}")
        print(f"  Space freed: {results['space_freed_mb']:.1f}MB")
        print(f"  Size reduction: {results['initial_size_mb']:.1f}MB -> {results['final_size_mb']:.1f}MB")
        
        return results


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Clean up Jarvis test logs")
    parser.add_argument("--force", action="store_true", help="Force cleanup even if under storage limits")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be cleaned without actually doing it")
    
    args = parser.parse_args()
    
    if args.dry_run:
        print("[INFO] DRY RUN MODE - No files will be deleted")
        return
    
    cleanup = LogCleanup()
    results = cleanup.run_cleanup(force=args.force)
    
    return 0 if results["files_deleted"] >= 0 else 1


if __name__ == "__main__":
    exit(main())