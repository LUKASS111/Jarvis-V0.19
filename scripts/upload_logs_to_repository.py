#!/usr/bin/env python3
"""
Automated Log Upload System for Jarvis V0.19
Uploads all test logs and reports to a centralized repository location after test execution.
"""

import os
import sys
import json
import shutil
import zipfile
from datetime import datetime
from pathlib import Path

class LogUploadSystem:
    """Manages automatic upload of test logs to repository structure"""
    
    def __init__(self, project_root=None):
        self.project_root = Path(project_root) if project_root else Path(__file__).parent.parent
        self.upload_target = self.project_root / "tests" / "output" / "uploaded_logs"
        self.timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
    def collect_all_logs(self):
        """Collect all log files from various locations"""
        log_sources = {
            "test_outputs": self.project_root / "tests" / "output",
            "logs": self.project_root / "logs",
            "agent_reports": self.project_root / "data" / "agent_reports",
            "test_reports": self.project_root.glob("test_report_*.json"),
            "aggregate_reports": self.project_root.glob("TEST_AGGREGATE_REPORT_*.json"),
            "markdown_reports": self.project_root.glob("TEST_AGGREGATE_REPORT_*.md"),
            "compliance_reports": [self.project_root / "PROCESS_COMPLIANCE_REPORT.json"],
        }
        
        collected_files = {}
        total_size = 0
        
        for category, source in log_sources.items():
            collected_files[category] = []
            
            if isinstance(source, Path):
                if source.exists():
                    if source.is_dir():
                        for file_path in source.rglob("*"):
                            if file_path.is_file():
                                collected_files[category].append(file_path)
                                total_size += file_path.stat().st_size
                    else:
                        collected_files[category].append(source)
                        total_size += source.stat().st_size
            elif isinstance(source, list):
                for file_path in source:
                    if file_path.exists():
                        collected_files[category].append(file_path)
                        total_size += file_path.stat().st_size
            else:  # generator
                for file_path in source:
                    if file_path.exists():
                        collected_files[category].append(file_path)
                        total_size += file_path.stat().st_size
        
        return collected_files, total_size
    
    def create_upload_structure(self, collected_files):
        """Create organized upload structure"""
        
        # Create upload directory
        upload_dir = self.upload_target / f"logs_{self.timestamp}"
        upload_dir.mkdir(parents=True, exist_ok=True)
        
        # Copy files to organized structure
        file_count = 0
        total_copied_size = 0
        
        for category, files in collected_files.items():
            if not files:
                continue
                
            category_dir = upload_dir / category
            category_dir.mkdir(exist_ok=True)
            
            for file_path in files:
                try:
                    dest_path = category_dir / file_path.name
                    
                    # Handle name conflicts
                    counter = 1
                    original_dest = dest_path
                    while dest_path.exists():
                        stem = original_dest.stem
                        suffix = original_dest.suffix
                        dest_path = category_dir / f"{stem}_{counter}{suffix}"
                        counter += 1
                    
                    shutil.copy2(file_path, dest_path)
                    file_count += 1
                    total_copied_size += dest_path.stat().st_size
                    
                except Exception as e:
                    print(f"[WARN] Could not copy {file_path}: {e}")
        
        return upload_dir, file_count, total_copied_size
    
    def create_upload_manifest(self, upload_dir, file_count, total_size):
        """Create manifest file for uploaded logs"""
        manifest = {
            "upload_timestamp": datetime.now().isoformat(),
            "upload_session": self.timestamp,
            "file_count": file_count,
            "total_size_bytes": total_size,
            "total_size_mb": round(total_size / (1024*1024), 2),
            "categories": {},
            "system_info": {
                "python_version": sys.version,
                "project_root": str(self.project_root),
                "upload_trigger": "automated_test_completion"
            }
        }
        
        # Analyze uploaded categories
        for category_dir in upload_dir.iterdir():
            if category_dir.is_dir():
                category_files = list(category_dir.glob("*"))
                category_size = sum(f.stat().st_size for f in category_files if f.is_file())
                
                manifest["categories"][category_dir.name] = {
                    "file_count": len(category_files),
                    "size_bytes": category_size,
                    "size_mb": round(category_size / (1024*1024), 2),
                    "files": [f.name for f in category_files if f.is_file()]
                }
        
        # Save manifest
        manifest_path = upload_dir / "upload_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)
        
        return manifest_path, manifest
    
    def create_archive(self, upload_dir):
        """Create compressed archive of uploaded logs"""
        archive_path = upload_dir.parent / f"logs_archive_{self.timestamp}.zip"
        
        with zipfile.ZipFile(archive_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for file_path in upload_dir.rglob("*"):
                if file_path.is_file():
                    arcname = file_path.relative_to(upload_dir.parent)
                    zipf.write(file_path, arcname)
        
        return archive_path
    
    def upload_logs(self):
        """Main upload function"""
        print(f"\n{'='*60}")
        print("[UPLOAD] AUTOMATED LOG UPLOAD SYSTEM")
        print(f"{'='*60}")
        print(f"[TIMESTAMP] Upload session: {self.timestamp}")
        
        # Collect all logs
        print("[COLLECT] Collecting logs from all sources...")
        collected_files, total_size = self.collect_all_logs()
        
        total_files = sum(len(files) for files in collected_files.values())
        print(f"[FOUND] {total_files} log files ({round(total_size/(1024*1024), 1)}MB)")
        
        if total_files == 0:
            print("[INFO] No logs found to upload")
            return None
        
        # Create upload structure
        print("[ORGANIZE] Creating organized upload structure...")
        upload_dir, file_count, copied_size = self.create_upload_structure(collected_files)
        
        # Create manifest
        print("[MANIFEST] Creating upload manifest...")
        manifest_path, manifest = self.create_upload_manifest(upload_dir, file_count, copied_size)
        
        # Create archive
        print("[ARCHIVE] Creating compressed archive...")
        archive_path = self.create_archive(upload_dir)
        
        print(f"\n[SUCCESS] Log upload completed:")
        print(f"  Organized logs: {upload_dir}")
        print(f"  Manifest file: {manifest_path}")
        print(f"  Archive file: {archive_path}")
        print(f"  Files uploaded: {file_count}")
        print(f"  Total size: {manifest['total_size_mb']}MB")
        
        # Summary by category
        print(f"\n[SUMMARY] Upload by category:")
        for category, info in manifest["categories"].items():
            print(f"  {category}: {info['file_count']} files ({info['size_mb']}MB)")
        
        print(f"\n[LOCATION] All logs are now available in the repository at:")
        print(f"  {upload_dir.relative_to(self.project_root)}")
        
        return {
            "upload_dir": upload_dir,
            "manifest_path": manifest_path,
            "archive_path": archive_path,
            "manifest": manifest
        }

def main():
    """Main execution function"""
    try:
        uploader = LogUploadSystem()
        result = uploader.upload_logs()
        
        if result:
            print(f"\n[COMPLETE] Automated log upload successful!")
            return 0
        else:
            print(f"\n[INFO] No logs to upload")
            return 0
            
    except Exception as e:
        print(f"\n[ERROR] Log upload failed: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())