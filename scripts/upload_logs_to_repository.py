#!/usr/bin/env python3
"""
Log Upload to Repository Script
Uploads test logs and results to repository for tracking
"""

import os
import sys
import json
import shutil
from datetime import datetime
from pathlib import Path

def upload_logs_to_repository():
    """Upload test logs and results to repository archive"""
    print("📤 Uploading logs to repository...")
    
    # Create logs directory if it doesn't exist
    logs_dir = Path("archive/logs")
    logs_dir.mkdir(parents=True, exist_ok=True)
    
    current_date = datetime.now().strftime('%Y%m%d')
    session_dir = logs_dir / current_date
    session_dir.mkdir(exist_ok=True)
    
    # Find log files to upload - expanded search patterns
    log_files = []
    search_locations = [
        ".",  # Current directory
        "tests/output/logs",  # Test output directory
        "archive/consolidated_logs",  # Consolidated logs
        "logs"  # Main logs directory
    ]
    
    # Comprehensive file patterns for all test artifacts
    search_patterns = [
        "test_results_*.json", "aggregated_test_results_*.json", "*_test_*.log",
        "*validation_report_*.json", "comprehensive_*.json", "session_summary_*.json",
        "*_test_summary.json", "test_execution_*.json", "performance_*.json",
        "agent_reports_*.json", "compliance_*.json", "errors_*.json",
        "system_*.json", "crdt_*.json", "network_*.json"
    ]
    
    # Search all locations for test artifacts
    for location in search_locations:
        location_path = Path(location)
        if location_path.exists():
            for pattern in search_patterns:
                found_files = list(location_path.glob(pattern))
                log_files.extend(found_files)
                if found_files:
                    print(f"📁 Found {len(found_files)} files matching {pattern} in {location}")
    
    # Also check for recent files that might be test-related
    for location in search_locations:
        location_path = Path(location)
        if location_path.exists():
            try:
                for file_path in location_path.glob("*.json"):
                    # Include recently modified JSON files that might be test results
                    file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                    if (datetime.now() - file_time).total_seconds() < 3600:  # Last hour
                        if file_path not in log_files:
                            log_files.append(file_path)
                            print(f"📁 Including recent file: {file_path}")
            except Exception as e:
                print(f"❌ Error scanning {location}: {e}")
    
    uploaded_count = 0
    preserved_count = 0
    
    for log_file in log_files:
        try:
            # Create timestamped filename
            timestamp = datetime.now().strftime('%H%M%S')
            new_filename = f"{timestamp}_{log_file.name}"
            destination = session_dir / new_filename
            
            # Copy file to archive (preserve original)
            shutil.copy2(log_file, destination)
            uploaded_count += 1
            preserved_count += 1
            
            print(f"📁 Uploaded: {log_file.name} -> {destination}")
            
        except Exception as e:
            print(f"❌ Error uploading {log_file}: {e}")
    
    # Create upload summary
    upload_summary = {
        'timestamp': datetime.now().isoformat(),
        'session_date': current_date,
        'files_uploaded': uploaded_count,
        'files_preserved': preserved_count,
        'upload_directory': str(session_dir),
        'search_locations': search_locations,
        'search_patterns': search_patterns,
        'file_types': {
            'test_results': len([f for f in log_files if 'test_result' in f.name]),
            'validation_reports': len([f for f in log_files if 'validation_report' in f.name]),
            'comprehensive_reports': len([f for f in log_files if 'comprehensive' in f.name]),
            'session_summaries': len([f for f in log_files if 'session_summary' in f.name]),
            'performance_logs': len([f for f in log_files if 'performance' in f.name]),
            'other_logs': uploaded_count - len([f for f in log_files if any(keyword in f.name for keyword in ['test_result', 'validation_report', 'comprehensive', 'session_summary', 'performance'])])
        }
    }
    
    # Save upload summary
    summary_file = session_dir / f"upload_summary_{datetime.now().strftime('%H%M%S')}.json"
    with open(summary_file, 'w') as f:
        json.dump(upload_summary, f, indent=2)
    
    print(f"📊 Upload Summary:")
    print(f"   Files uploaded: {uploaded_count}")
    print(f"   Files preserved: {preserved_count}")
    print(f"   Destination: {session_dir}")
    print(f"   Summary saved: {summary_file}")
    
    return uploaded_count

def cleanup_current_logs():
    """Clean up old log files from the main directory AFTER upload is complete"""
    print("🧹 Cleaning up old log files...")
    
    cleanup_patterns = [
        "test_results_*.json",
        "aggregated_test_results_*.json", 
        "*validation_report_*.json",
        "comprehensive_*.json"
    ]
    
    cleaned_count = 0
    
    for pattern in cleanup_patterns:
        for file_path in Path(".").glob(pattern):
            try:
                # Keep files from today, only clean files older than 1 day
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time.date() < datetime.now().date():
                    file_path.unlink()
                    cleaned_count += 1
                    print(f"🗑️ Cleaned: {file_path}")
            except Exception as e:
                print(f"❌ Error cleaning {file_path}: {e}")
    
    print(f"✅ Cleaned {cleaned_count} old log files (preserved today's files)")
    return cleaned_count

def main():
    """Main log upload function"""
    print("🎯 Log Upload to Repository")
    print("=" * 40)
    
    # Change to repository root
    os.chdir('/home/runner/work/Jarvis-1.0.0/Jarvis-1.0.0')
    
    # Upload logs
    uploaded = upload_logs_to_repository()
    
    # Cleanup old logs (optional)
    if uploaded > 0:
        cleanup_current_logs()
    
    print("✅ Log upload completed")

if __name__ == "__main__":
    main()