"""
Backup and Recovery System for Jarvis-V0.19
Comprehensive backup, recovery, and data integrity management.
"""

import os
import shutil
import json
import sqlite3
import threading
import hashlib
import gzip
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
import time

from .data_archiver import get_archiver, ARCHIVE_DB_PATH
from ..memory.memory import MEMORY_FILE

@dataclass
class BackupInfo:
    """Information about a backup"""
    backup_id: str
    timestamp: str
    backup_type: str  # manual, scheduled, pre_change, emergency
    files_included: List[str]
    backup_path: str
    size_bytes: int
    checksum: str
    description: str
    created_by: str

@dataclass
class RecoveryPoint:
    """Recovery point information"""
    recovery_id: str
    timestamp: str
    backup_info: BackupInfo
    system_state: Dict[str, Any]
    verification_status: str  # verified, pending, failed
    notes: str

class BackupRecoveryManager:
    """Comprehensive backup and recovery management system"""
    
    def __init__(self):
        self.backup_root = "data/backups"
        self.recovery_root = "data/recovery"
        self.backup_index_file = "data/backup_index.json"
        self.recovery_log_file = "data/recovery_log.json"
        
        self.backup_lock = threading.Lock()
        self.backup_index = {}
        self.recovery_log = []
        
        self._setup_directories()
        self._load_backup_index()
        self._load_recovery_log()
        self._setup_scheduled_backups()
    
    def _setup_directories(self):
        """Setup backup and recovery directories"""
        for directory in [self.backup_root, self.recovery_root, 
                         f"{self.backup_root}/daily", f"{self.backup_root}/weekly",
                         f"{self.backup_root}/manual", f"{self.backup_root}/pre_change"]:
            os.makedirs(directory, exist_ok=True)
    
    def _load_backup_index(self):
        """Load backup index from file"""
        if os.path.exists(self.backup_index_file):
            try:
                with open(self.backup_index_file, 'r', encoding='utf-8') as f:
                    self.backup_index = json.load(f)
            except Exception as e:
                print(f"[WARN] Failed to load backup index: {e}")
                self.backup_index = {}
    
    def _save_backup_index(self):
        """Save backup index to file"""
        try:
            with open(self.backup_index_file, 'w', encoding='utf-8') as f:
                json.dump(self.backup_index, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Failed to save backup index: {e}")
    
    def _load_recovery_log(self):
        """Load recovery log from file"""
        if os.path.exists(self.recovery_log_file):
            try:
                with open(self.recovery_log_file, 'r', encoding='utf-8') as f:
                    self.recovery_log = json.load(f)
            except Exception as e:
                print(f"[WARN] Failed to load recovery log: {e}")
                self.recovery_log = []
    
    def _save_recovery_log(self):
        """Save recovery log to file"""
        try:
            with open(self.recovery_log_file, 'w', encoding='utf-8') as f:
                json.dump(self.recovery_log, f, indent=2)
        except Exception as e:
            print(f"[ERROR] Failed to save recovery log: {e}")
    
    def _setup_scheduled_backups(self):
        """Setup automatic scheduled backups"""
        # Simple time-based scheduling without external dependencies
        scheduler_thread = threading.Thread(target=self._run_scheduler, daemon=True)
        scheduler_thread.start()
    
    def _run_scheduler(self):
        """Run the backup scheduler"""
        last_daily = None
        last_weekly = None
        
        while True:
            try:
                current_time = datetime.now()
                
                # Daily backup at 2 AM
                if (last_daily is None or 
                    (current_time.hour == 2 and current_time.minute < 5 and
                     (last_daily is None or current_time.date() > last_daily.date()))):
                    self._scheduled_backup("daily")
                    last_daily = current_time
                
                # Weekly backup on Sunday at 3 AM
                if (current_time.weekday() == 6 and current_time.hour == 3 and 
                    current_time.minute < 5 and
                    (last_weekly is None or current_time.date() > last_weekly.date())):
                    self._scheduled_backup("weekly")
                    last_weekly = current_time
                
                time.sleep(300)  # Check every 5 minutes
            except Exception as e:
                print(f"[ERROR] Scheduler error: {e}")
                time.sleep(300)  # Wait 5 minutes on error
    
    def _scheduled_backup(self, backup_type: str):
        """Execute scheduled backup"""
        try:
            backup_info = self.create_backup(
                backup_type=backup_type,
                description=f"Automated {backup_type} backup",
                created_by="scheduler"
            )
            print(f"[INFO] Scheduled {backup_type} backup completed: {backup_info.backup_id}")
        except Exception as e:
            print(f"[ERROR] Scheduled {backup_type} backup failed: {e}")
    
    def create_backup(self, backup_type: str = "manual", description: str = "", 
                     created_by: str = "user", include_files: Optional[List[str]] = None) -> BackupInfo:
        """Create a comprehensive backup"""
        with self.backup_lock:
            timestamp = datetime.now()
            backup_id = f"backup_{timestamp.strftime('%Y%m%d_%H%M%S')}_{backup_type}"
            
            # Default files to include
            if include_files is None:
                include_files = [
                    ARCHIVE_DB_PATH,  # Archive database
                    MEMORY_FILE,      # Memory file
                    "config/",        # Configuration directory
                    "data/test_reports/",  # Test reports
                    "logs/",          # Log files
                ]
            
            backup_dir = os.path.join(self.backup_root, backup_type, backup_id)
            os.makedirs(backup_dir, exist_ok=True)
            
            # Copy files to backup directory
            backed_up_files = []
            total_size = 0
            
            for file_path in include_files:
                try:
                    if os.path.exists(file_path):
                        if os.path.isfile(file_path):
                            dest_file = os.path.join(backup_dir, os.path.basename(file_path))
                            shutil.copy2(file_path, dest_file)
                            backed_up_files.append(file_path)
                            total_size += os.path.getsize(dest_file)
                        elif os.path.isdir(file_path):
                            dest_dir = os.path.join(backup_dir, os.path.basename(file_path.rstrip('/')))
                            shutil.copytree(file_path, dest_dir, dirs_exist_ok=True)
                            backed_up_files.append(file_path)
                            total_size += self._get_directory_size(dest_dir)
                except Exception as e:
                    print(f"[WARN] Failed to backup {file_path}: {e}")
            
            # Create backup metadata
            metadata = {
                'backup_id': backup_id,
                'timestamp': timestamp.isoformat(),
                'backup_type': backup_type,
                'description': description,
                'created_by': created_by,
                'files_included': backed_up_files,
                'system_info': self._get_system_info()
            }
            
            metadata_file = os.path.join(backup_dir, 'backup_metadata.json')
            with open(metadata_file, 'w', encoding='utf-8') as f:
                json.dump(metadata, f, indent=2)
            
            # Calculate checksum
            checksum = self._calculate_backup_checksum(backup_dir)
            
            # Create compressed archive
            archive_path = f"{backup_dir}.tar.gz"
            self._create_compressed_archive(backup_dir, archive_path)
            
            # Remove uncompressed directory
            shutil.rmtree(backup_dir)
            
            # Update size with compressed size
            total_size = os.path.getsize(archive_path)
            
            backup_info = BackupInfo(
                backup_id=backup_id,
                timestamp=timestamp.isoformat(),
                backup_type=backup_type,
                files_included=backed_up_files,
                backup_path=archive_path,
                size_bytes=total_size,
                checksum=checksum,
                description=description,
                created_by=created_by
            )
            
            # Update backup index
            self.backup_index[backup_id] = asdict(backup_info)
            self._save_backup_index()
            
            # Log backup creation
            get_archiver().log_agent_activity(
                'backup_system',
                'backup_created',
                f'Created {backup_type} backup: {backup_id}',
                asdict(backup_info)
            )
            
            return backup_info
    
    def create_pre_change_backup(self, change_description: str) -> BackupInfo:
        """Create backup before making significant changes"""
        return self.create_backup(
            backup_type="pre_change",
            description=f"Pre-change backup: {change_description}",
            created_by="system"
        )
    
    def create_emergency_backup(self, reason: str) -> BackupInfo:
        """Create emergency backup during critical situations"""
        return self.create_backup(
            backup_type="emergency",
            description=f"Emergency backup: {reason}",
            created_by="emergency_system"
        )
    
    def restore_from_backup(self, backup_id: str, target_files: Optional[List[str]] = None,
                          verify_before_restore: bool = True) -> bool:
        """Restore from a specific backup"""
        if backup_id not in self.backup_index:
            raise ValueError(f"Backup {backup_id} not found in index")
        
        backup_info = BackupInfo(**self.backup_index[backup_id])
        
        if not os.path.exists(backup_info.backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_info.backup_path}")
        
        # Verify backup integrity if requested
        if verify_before_restore:
            if not self.verify_backup_integrity(backup_id):
                raise ValueError(f"Backup {backup_id} failed integrity check")
        
        # Create current backup before restore
        current_backup = self.create_backup(
            backup_type="pre_restore",
            description=f"Pre-restore backup before restoring {backup_id}",
            created_by="restore_system"
        )
        
        try:
            # Extract backup
            restore_temp_dir = os.path.join(self.recovery_root, f"restore_{backup_id}")
            os.makedirs(restore_temp_dir, exist_ok=True)
            
            self._extract_compressed_archive(backup_info.backup_path, restore_temp_dir)
            
            # Restore specific files or all files
            files_to_restore = target_files or backup_info.files_included
            
            restored_files = []
            for file_path in files_to_restore:
                try:
                    source_path = os.path.join(restore_temp_dir, os.path.basename(file_path))
                    if os.path.exists(source_path):
                        if os.path.isfile(source_path):
                            # Ensure target directory exists
                            os.makedirs(os.path.dirname(file_path), exist_ok=True)
                            shutil.copy2(source_path, file_path)
                        else:
                            # Handle directory restore
                            if os.path.exists(file_path):
                                shutil.rmtree(file_path)
                            shutil.copytree(source_path, file_path)
                        
                        restored_files.append(file_path)
                        print(f"[INFO] Restored: {file_path}")
                except Exception as e:
                    print(f"[ERROR] Failed to restore {file_path}: {e}")
            
            # Clean up temporary directory
            shutil.rmtree(restore_temp_dir)
            
            # Log recovery
            recovery_entry = {
                'recovery_id': f"recovery_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'timestamp': datetime.now().isoformat(),
                'backup_id': backup_id,
                'restored_files': restored_files,
                'pre_restore_backup': current_backup.backup_id,
                'success': True
            }
            
            self.recovery_log.append(recovery_entry)
            self._save_recovery_log()
            
            get_archiver().log_agent_activity(
                'recovery_system',
                'restore_completed',
                f'Successfully restored from backup: {backup_id}',
                recovery_entry
            )
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Restore failed: {e}")
            
            # Log failed recovery
            recovery_entry = {
                'recovery_id': f"recovery_failed_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                'timestamp': datetime.now().isoformat(),
                'backup_id': backup_id,
                'error': str(e),
                'pre_restore_backup': current_backup.backup_id,
                'success': False
            }
            
            self.recovery_log.append(recovery_entry)
            self._save_recovery_log()
            
            return False
    
    def verify_backup_integrity(self, backup_id: str) -> bool:
        """Verify integrity of a backup"""
        if backup_id not in self.backup_index:
            return False
        
        backup_info = BackupInfo(**self.backup_index[backup_id])
        
        if not os.path.exists(backup_info.backup_path):
            return False
        
        try:
            # Verify file exists and can be read
            temp_dir = os.path.join(self.recovery_root, f"verify_{backup_id}")
            os.makedirs(temp_dir, exist_ok=True)
            
            # Extract and verify
            self._extract_compressed_archive(backup_info.backup_path, temp_dir)
            
            # Check metadata file exists
            metadata_file = os.path.join(temp_dir, 'backup_metadata.json')
            if not os.path.exists(metadata_file):
                shutil.rmtree(temp_dir)
                return False
            
            # Verify metadata
            with open(metadata_file, 'r', encoding='utf-8') as f:
                metadata = json.load(f)
                if metadata['backup_id'] != backup_id:
                    shutil.rmtree(temp_dir)
                    return False
            
            # Calculate checksum and verify
            calculated_checksum = self._calculate_backup_checksum(temp_dir)
            
            # Clean up
            shutil.rmtree(temp_dir)
            
            # Compare checksums
            integrity_ok = calculated_checksum == backup_info.checksum
            
            if not integrity_ok:
                print(f"[WARN] Backup {backup_id} failed integrity check")
            
            return integrity_ok
            
        except Exception as e:
            print(f"[ERROR] Backup verification failed: {e}")
            return False
    
    def list_backups(self, backup_type: Optional[str] = None, 
                    days_back: Optional[int] = None) -> List[BackupInfo]:
        """List available backups"""
        backups = []
        
        for backup_id, backup_data in self.backup_index.items():
            backup_info = BackupInfo(**backup_data)
            
            # Filter by type if specified
            if backup_type and backup_info.backup_type != backup_type:
                continue
            
            # Filter by date if specified
            if days_back:
                backup_date = datetime.fromisoformat(backup_info.timestamp)
                cutoff_date = datetime.now() - timedelta(days=days_back)
                if backup_date < cutoff_date:
                    continue
            
            # Verify backup still exists
            if os.path.exists(backup_info.backup_path):
                backups.append(backup_info)
        
        # Sort by timestamp (newest first)
        backups.sort(key=lambda b: b.timestamp, reverse=True)
        return backups
    
    def cleanup_current_backups(self, days_to_keep: int = 30, 
                          keep_weekly: bool = True, keep_monthly: bool = True):
        """Clean up old backups based on retention policy"""
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        backups_to_remove = []
        
        for backup_id, backup_data in self.backup_index.items():
            backup_info = BackupInfo(**backup_data)
            backup_date = datetime.fromisoformat(backup_info.timestamp)
            
            # Skip if within retention period
            if backup_date >= cutoff_date:
                continue
            
            # Keep weekly backups (first backup of each week)
            if keep_weekly and backup_info.backup_type == "weekly":
                continue
            
            # Keep monthly backups (first backup of each month)
            if keep_monthly and backup_date.day <= 7:  # First week of month
                continue
            
            # Skip emergency and pre_change backups (keep indefinitely)
            if backup_info.backup_type in ["emergency", "pre_change"]:
                continue
            
            backups_to_remove.append(backup_id)
        
        # Remove old backups
        for backup_id in backups_to_remove:
            try:
                backup_info = BackupInfo(**self.backup_index[backup_id])
                if os.path.exists(backup_info.backup_path):
                    os.remove(backup_info.backup_path)
                    print(f"[INFO] Removed old backup: {backup_id}")
                
                del self.backup_index[backup_id]
            except Exception as e:
                print(f"[ERROR] Failed to remove backup {backup_id}: {e}")
        
        self._save_backup_index()
    
    def get_backup_statistics(self) -> Dict[str, Any]:
        """Get backup system statistics"""
        backups = self.list_backups()
        
        stats = {
            'total_backups': len(backups),
            'total_size_bytes': sum(b.size_bytes for b in backups),
            'backup_types': {},
            'oldest_backup': None,
            'newest_backup': None,
            'total_recoveries': len(self.recovery_log),
            'successful_recoveries': sum(1 for r in self.recovery_log if r.get('success', False))
        }
        
        # Count by type
        for backup in backups:
            backup_type = backup.backup_type
            if backup_type not in stats['backup_types']:
                stats['backup_types'][backup_type] = {'count': 0, 'size_bytes': 0}
            stats['backup_types'][backup_type]['count'] += 1
            stats['backup_types'][backup_type]['size_bytes'] += backup.size_bytes
        
        # Find oldest and newest
        if backups:
            stats['oldest_backup'] = min(backups, key=lambda b: b.timestamp).backup_id
            stats['newest_backup'] = max(backups, key=lambda b: b.timestamp).backup_id
        
        return stats
    
    def _get_directory_size(self, directory: str) -> int:
        """Calculate total size of directory"""
        total_size = 0
        for dirpath, dirnames, filenames in os.walk(directory):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    total_size += os.path.getsize(filepath)
                except OSError:
                    pass
        return total_size
    
    def _get_system_info(self) -> Dict[str, Any]:
        """Get current system information"""
        return {
            'timestamp': datetime.now().isoformat(),
            'archive_stats': get_archiver().get_statistics(),
            'python_version': os.sys.version,
            'platform': os.name
        }
    
    def _calculate_backup_checksum(self, backup_dir: str) -> str:
        """Calculate checksum for backup directory"""
        hash_sha256 = hashlib.sha256()
        
        for root, dirs, files in os.walk(backup_dir):
            # Sort to ensure consistent ordering
            dirs.sort()
            files.sort()
            
            for filename in files:
                filepath = os.path.join(root, filename)
                try:
                    with open(filepath, 'rb') as f:
                        for chunk in iter(lambda: f.read(4096), b""):
                            hash_sha256.update(chunk)
                except Exception:
                    pass  # Skip files that can't be read
        
        return hash_sha256.hexdigest()
    
    def _create_compressed_archive(self, source_dir: str, archive_path: str):
        """Create compressed tar.gz archive"""
        import tarfile
        
        with tarfile.open(archive_path, 'w:gz') as tar:
            tar.add(source_dir, arcname=os.path.basename(source_dir))
    
    def _extract_compressed_archive(self, archive_path: str, extract_dir: str):
        """Extract compressed tar.gz archive"""
        import tarfile
        
        with tarfile.open(archive_path, 'r:gz') as tar:
            tar.extractall(extract_dir)

# Global backup manager instance
_backup_manager = None

def get_backup_manager() -> BackupRecoveryManager:
    """Get global backup manager instance (singleton pattern)"""
    global _backup_manager
    if _backup_manager is None:
        _backup_manager = BackupRecoveryManager()
    return _backup_manager

def create_backup(description: str = "Manual backup") -> BackupInfo:
    """Create a manual backup"""
    return get_backup_manager().create_backup(description=description)

def create_pre_change_backup(change_description: str) -> BackupInfo:
    """Create backup before making changes"""
    return get_backup_manager().create_pre_change_backup(change_description)

def restore_from_backup(backup_id: str) -> bool:
    """Restore from backup"""
    return get_backup_manager().restore_from_backup(backup_id)

def list_available_backups() -> List[BackupInfo]:
    """List all available backups"""
    return get_backup_manager().list_backups()

def get_backup_stats() -> Dict[str, Any]:
    """Get backup system statistics"""
    return get_backup_manager().get_backup_statistics()