#!/usr/bin/env python3
"""
Log Cleanup Utility for Jarvis-V0.19
Cleans up excessive test-generated log files while preserving important logs
"""

import os
import glob
import sys
from datetime import datetime, timedelta

def cleanup_performance_test_logs():
    """Clean up excessive performance test generated logs"""
    logs_dir = "logs"
    
    if not os.path.exists(logs_dir):
        print(f"[INFO] Logs directory not found: {logs_dir}")
        return
    
    # Patterns for test-generated logs to clean up
    cleanup_patterns = [
        "concurrent_log_*.json",
        "perf_event_*.json", 
        "workflow_event_*.json",
        "large_event_*.json"
    ]
    
    total_removed = 0
    total_size_saved = 0
    
    print("[CLEANUP] Starting log cleanup...")
    
    for pattern in cleanup_patterns:
        files = glob.glob(os.path.join(logs_dir, pattern))
        print(f"[PATTERN] {pattern}: Found {len(files)} files")
        
        for file_path in files:
            try:
                file_size = os.path.getsize(file_path)
                os.remove(file_path)
                total_removed += 1
                total_size_saved += file_size
            except Exception as e:
                print(f"[WARN] Could not remove {file_path}: {e}")
    
    print(f"\n[SUMMARY] Cleanup completed:")
    print(f"  Files removed: {total_removed}")
    print(f"  Space saved: {total_size_saved / 1024:.2f} KB")
    
    # Show remaining important logs
    remaining_logs = []
    for file in os.listdir(logs_dir):
        if file.endswith(('.jsonl', '.log')):
            remaining_logs.append(file)
    
    print(f"  Important logs preserved: {len(remaining_logs)}")
    for log in remaining_logs[:10]:  # Show first 10
        print(f"    - {log}")
    if len(remaining_logs) > 10:
        print(f"    ... and {len(remaining_logs) - 10} more")

def organize_log_structure():
    """Organize logs into proper structure"""
    logs_dir = "logs"
    
    # Create subdirectories for better organization
    subdirs = ["error", "performance", "archive", "system"]
    
    for subdir in subdirs:
        subdir_path = os.path.join(logs_dir, subdir)
        os.makedirs(subdir_path, exist_ok=True)
    
    print(f"\n[ORGANIZE] Created log structure in {logs_dir}/")
    for subdir in subdirs:
        print(f"  - {subdir}/")

def main():
    """Main cleanup function"""
    print("[LAUNCH] Log Cleanup Utility")
    print("="*50)
    
    # Change to project root
    if not os.path.exists("logs"):
        script_dir = os.path.dirname(os.path.abspath(__file__))
        project_root = os.path.dirname(script_dir)
        os.chdir(project_root)
    
    cleanup_performance_test_logs()
    organize_log_structure()
    
    print(f"\n[COMPLETE] Log cleanup finished at {datetime.now().strftime('%H:%M:%S')}")

if __name__ == "__main__":
    main()