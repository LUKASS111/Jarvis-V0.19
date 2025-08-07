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
    
    # Find log files to upload
    log_files = []
    
    # Test result files
    for pattern in ["test_results_*.json", "aggregated_test_results_*.json", "*_test_*.log"]:
        log_files.extend(Path(".").glob(pattern))
    
    # Validation reports
    for pattern in ["*validation_report_*.json", "comprehensive_*.json"]:
        log_files.extend(Path(".").glob(pattern))
    
    uploaded_count = 0
    
    for log_file in log_files:
        try:
            # Create timestamped filename
            timestamp = datetime.now().strftime('%H%M%S')
            new_filename = f"{timestamp}_{log_file.name}"
            destination = session_dir / new_filename
            
            # Copy file to archive
            shutil.copy2(log_file, destination)
            uploaded_count += 1
            
            print(f"📁 Uploaded: {log_file.name} -> {destination}")
            
        except Exception as e:
            print(f"❌ Error uploading {log_file}: {e}")
    
    # Create upload summary
    upload_summary = {
        'timestamp': datetime.now().isoformat(),
        'session_date': current_date,
        'files_uploaded': uploaded_count,
        'upload_directory': str(session_dir),
        'file_types': {
            'test_results': len([f for f in log_files if 'test_result' in f.name]),
            'validation_reports': len([f for f in log_files if 'validation_report' in f.name]),
            'comprehensive_reports': len([f for f in log_files if 'comprehensive' in f.name]),
            'other_logs': uploaded_count - len([f for f in log_files if any(keyword in f.name for keyword in ['test_result', 'validation_report', 'comprehensive'])])
        }
    }
    
    # Save upload summary
    summary_file = session_dir / f"upload_summary_{datetime.now().strftime('%H%M%S')}.json"
    with open(summary_file, 'w') as f:
        json.dump(upload_summary, f, indent=2)
    
    print(f"📊 Upload Summary:")
    print(f"   Files uploaded: {uploaded_count}")
    print(f"   Destination: {session_dir}")
    print(f"   Summary saved: {summary_file}")
    
    return uploaded_count

def cleanup_old_logs():
    """Clean up old log files from the main directory"""
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
                # Keep files from today
                file_time = datetime.fromtimestamp(file_path.stat().st_mtime)
                if file_time.date() < datetime.now().date():
                    file_path.unlink()
                    cleaned_count += 1
                    print(f"🗑️ Cleaned: {file_path}")
            except Exception as e:
                print(f"❌ Error cleaning {file_path}: {e}")
    
    print(f"✅ Cleaned {cleaned_count} old log files")
    return cleaned_count

def main():
    """Main log upload function"""
    print("🎯 Log Upload to Repository")
    print("=" * 40)
    
    # Change to repository root
    os.chdir('/home/runner/work/Jarvis-V0.19/Jarvis-V0.19')
    
    # Upload logs
    uploaded = upload_logs_to_repository()
    
    # Cleanup old logs (optional)
    if uploaded > 0:
        cleanup_old_logs()
    
    print("✅ Log upload completed")

if __name__ == "__main__":
    main()