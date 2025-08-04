#!/usr/bin/env python3
"""
Test Output Collector for Jarvis-V0.19
Collects all test outputs into a unified archive for easy transfer
"""

import os
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

def collect_test_outputs():
    """Collect all test outputs into a transferable archive"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    archive_name = f"jarvis_test_outputs_{timestamp}.zip"
    
    print(f"[COLLECT] Collecting test outputs into {archive_name}")
    
    with zipfile.ZipFile(archive_name, 'w', zipfile.ZIP_DEFLATED) as zipf:
        
        # 1. Unified test output directory (primary location)
        test_output_dir = Path("tests/output")
        if test_output_dir.exists():
            print("[INFO] Adding unified test outputs...")
            for root, dirs, files in os.walk(test_output_dir):
                for file in files:
                    file_path = os.path.join(root, file)
                    arc_path = os.path.relpath(file_path, ".")
                    zipf.write(file_path, arc_path)
        
        # 2. Test aggregate reports from root directory (legacy)
        print("[INFO] Adding test aggregate reports...")
        for file in Path(".").glob("TEST_AGGREGATE_REPORT_*.json"):
            zipf.write(file, file.name)
        for file in Path(".").glob("TEST_AGGREGATE_REPORT_*.md"):
            zipf.write(file, file.name)
        
        # 3. Original logs directory (for compatibility)
        logs_dir = Path("logs")
        if logs_dir.exists():
            print("[INFO] Adding logs directory...")
            for file in logs_dir.glob("*.json"):
                if any(pattern in file.name for pattern in [
                    "function_test_results", "perf_event", "concurrent_log", 
                    "test_event", "workflow_event", "integration_test"
                ]):
                    arc_path = f"legacy_logs/{file.name}"
                    zipf.write(file, arc_path)
        
        # 4. Original agent reports (for compatibility)
        agent_reports_dir = Path("data/agent_reports")
        if agent_reports_dir.exists():
            print("[INFO] Adding agent reports...")
            for file in agent_reports_dir.glob("*.json"):
                arc_path = f"legacy_agent_reports/{file.name}"
                zipf.write(file, arc_path)
    
    # Get file size for reporting
    file_size = os.path.getsize(archive_name)
    file_size_mb = file_size / (1024 * 1024)
    
    print(f"\n[COMPLETE] Test outputs collected successfully!")
    print(f"Archive: {archive_name}")
    print(f"Size: {file_size_mb:.2f} MB")
    print(f"\nThis archive contains all test outputs and can be easily transferred.")
    
    return archive_name

def show_test_output_summary():
    """Show summary of current test outputs"""
    print("=" * 60)
    print("JARVIS TEST OUTPUT SUMMARY")
    print("=" * 60)
    
    # Unified test output directory
    test_output_dir = Path("tests/output")
    if test_output_dir.exists():
        print(f"\n[PRIMARY] Unified Test Output Directory: {test_output_dir}")
        
        for subdir in ["reports", "logs", "agent_reports", "performance", "temp"]:
            subdir_path = test_output_dir / subdir
            if subdir_path.exists():
                files = list(subdir_path.glob("*"))
                total_size = sum(f.stat().st_size for f in files if f.is_file())
                print(f"  {subdir}/: {len(files)} files ({total_size / 1024:.1f} KB)")
    
    # Legacy locations
    print(f"\n[LEGACY] Original Locations (for compatibility):")
    
    # Root test reports
    root_reports = list(Path(".").glob("TEST_AGGREGATE_REPORT_*"))
    if root_reports:
        total_size = sum(f.stat().st_size for f in root_reports)
        print(f"  Root reports: {len(root_reports)} files ({total_size / 1024:.1f} KB)")
    
    # Logs directory
    logs_dir = Path("logs")
    if logs_dir.exists():
        test_logs = [f for f in logs_dir.glob("*.json") if any(pattern in f.name for pattern in [
            "function_test_results", "perf_event", "concurrent_log", "test_event", "workflow_event", "integration_test"
        ])]
        if test_logs:
            total_size = sum(f.stat().st_size for f in test_logs)
            print(f"  logs/ (test files): {len(test_logs)} files ({total_size / 1024:.1f} KB)")
    
    # Agent reports
    agent_reports_dir = Path("data/agent_reports")
    if agent_reports_dir.exists():
        agent_files = list(agent_reports_dir.glob("*.json"))
        if agent_files:
            total_size = sum(f.stat().st_size for f in agent_files)
            print(f"  data/agent_reports/: {len(agent_files)} files ({total_size / 1024:.1f} KB)")
    
    print(f"\n[ACTION] Run 'python scripts/collect_test_outputs.py collect' to create transfer archive")

def main():
    """Main function"""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "collect":
        collect_test_outputs()
    else:
        show_test_output_summary()

if __name__ == "__main__":
    main()