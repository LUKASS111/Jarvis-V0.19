"""
Data Archive Purge Manager for Jarvis-V0.19
Implements intelligent purge policies for version-based data cleanup.
"""

import sqlite3
import json
import os
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass
import hashlib

from jarvis.core.data_archiver import get_archiver, ARCHIVE_DB_PATH

@dataclass
class PurgePolicy:
    """Defines data retention policy for different archive entry types"""
    name: str
    max_versions_keep: int  # How many program versions to keep
    max_age_days: int  # Maximum age in days
    preserve_audit_data: bool  # Whether to preserve for audit purposes
    preserve_regression_tests: bool  # Whether to preserve regression test data
    size_limit_mb: Optional[int] = None  # Optional size limit for this category

class DataArchivePurgeManager:
    """Manages purging of old archive data based on version and retention policies"""
    
    def __init__(self, db_path: str = ARCHIVE_DB_PATH, config_path: str = "config/purge_config.json"):
        self.db_path = db_path
        self.config_path = config_path
        self._lock = threading.Lock()
        self.current_version = self._get_current_version()
        
        # Default purge policies
        self.default_policies = {
            "test_data": PurgePolicy(
                name="test_data",
                max_versions_keep=3,
                max_age_days=30,
                preserve_audit_data=False,
                preserve_regression_tests=True
            ),
            "system_logs": PurgePolicy(
                name="system_logs", 
                max_versions_keep=5,
                max_age_days=14,
                preserve_audit_data=True,
                preserve_regression_tests=False
            ),
            "user_interactions": PurgePolicy(
                name="user_interactions",
                max_versions_keep=10,
                max_age_days=90,
                preserve_audit_data=True,
                preserve_regression_tests=True
            ),
            "verification_data": PurgePolicy(
                name="verification_data",
                max_versions_keep=5,
                max_age_days=45,
                preserve_audit_data=True,
                preserve_regression_tests=True
            )
        }
        
        self.policies = self._load_policies()
        self._ensure_version_column()
    
    def _get_current_version(self) -> str:
        """Get current program version - universal detection"""
        # Priority 1: Try VERSION_STRING from main module
        try:
            from jarvis.core.main import VERSION_STRING
            if VERSION_STRING and VERSION_STRING.strip():
                return VERSION_STRING.strip()
        except ImportError:
            pass
        
        # Priority 2: Try reading from package info
        try:
            import pkg_resources
            version = pkg_resources.get_distribution("jarvis").version
            if version:
                return version
        except Exception:
            pass
        
        # Priority 3: Try git commit hash
        try:
            import subprocess
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(self.db_path)))
            result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], 
                                  capture_output=True, text=True, cwd=base_dir)
            if result.returncode == 0 and result.stdout.strip():
                return f"git-{result.stdout.strip()}"
        except Exception:
            pass
        
        # Priority 4: Try reading from VERSION file
        try:
            base_dir = os.path.dirname(os.path.dirname(os.path.dirname(self.db_path)))
            version_file = os.path.join(base_dir, "VERSION")
            if os.path.exists(version_file):
                with open(version_file, 'r') as f:
                    version = f.read().strip()
                    if version:
                        return version
        except Exception:
            pass
        
        # Fallback: Generate timestamp-based version
        from datetime import datetime
        timestamp = datetime.now().strftime("%Y%m%d")
        return f"auto-{timestamp}"
    
    def _load_policies(self) -> Dict[str, PurgePolicy]:
        """Load purge policies from config file"""
        if os.path.exists(self.config_path):
            try:
                with open(self.config_path, 'r') as f:
                    config = json.load(f)
                    
                policies = {}
                for name, policy_data in config.get('policies', {}).items():
                    policies[name] = PurgePolicy(
                        name=policy_data['name'],
                        max_versions_keep=policy_data['max_versions_keep'],
                        max_age_days=policy_data['max_age_days'],
                        preserve_audit_data=policy_data['preserve_audit_data'],
                        preserve_regression_tests=policy_data['preserve_regression_tests'],
                        size_limit_mb=policy_data.get('size_limit_mb')
                    )
                return policies
            except Exception as e:
                print(f"[PURGE] Warning: Could not load policies from {self.config_path}: {e}")
        
        # Save default policies
        self._save_policies()
        return self.default_policies
    
    def _save_policies(self):
        """Save current policies to config file"""
        os.makedirs(os.path.dirname(self.config_path), exist_ok=True)
        
        config = {
            'policies': {},
            'last_updated': datetime.now().isoformat(),
            'current_version': self.current_version
        }
        
        for name, policy in self.policies.items():
            config['policies'][name] = {
                'name': policy.name,
                'max_versions_keep': policy.max_versions_keep,
                'max_age_days': policy.max_age_days,
                'preserve_audit_data': policy.preserve_audit_data,
                'preserve_regression_tests': policy.preserve_regression_tests,
                'size_limit_mb': policy.size_limit_mb
            }
        
        with open(self.config_path, 'w') as f:
            json.dump(config, f, indent=2)
    
    def _ensure_version_column(self):
        """Ensure program_version column exists in archive_entries table"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Check if program_version column exists
            cursor.execute("PRAGMA table_info(archive_entries)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'program_version' not in columns:
                # Add program_version column
                cursor.execute('''
                    ALTER TABLE archive_entries 
                    ADD COLUMN program_version TEXT DEFAULT 'unknown'
                ''')
                
                # Update existing entries with current version
                cursor.execute('''
                    UPDATE archive_entries 
                    SET program_version = ? 
                    WHERE program_version = 'unknown' OR program_version IS NULL
                ''', (self.current_version,))
                
                print(f"[PURGE] Added program_version column and tagged {cursor.rowcount} existing entries with version {self.current_version}")
            
            # Create index for efficient queries
            cursor.execute('''
                CREATE INDEX IF NOT EXISTS idx_program_version 
                ON archive_entries(program_version)
            ''')
            
            conn.commit()
            conn.close()
    
    def tag_current_version_entries(self):
        """Tag all entries without version with current program version"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE archive_entries 
                SET program_version = ? 
                WHERE program_version = 'unknown' OR program_version IS NULL
            ''', (self.current_version,))
            
            updated_count = cursor.rowcount
            conn.commit()
            conn.close()
            
            if updated_count > 0:
                print(f"[PURGE] Tagged {updated_count} entries with current version: {self.current_version}")
            
            return updated_count
    
    def analyze_archive_data(self) -> Dict[str, Any]:
        """Analyze current archive data for purge planning"""
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Get version distribution
            cursor.execute('''
                SELECT program_version, COUNT(*) as count, 
                       MIN(created_at) as oldest, MAX(created_at) as newest
                FROM archive_entries 
                GROUP BY program_version 
                ORDER BY count DESC
            ''')
            version_stats = []
            for row in cursor.fetchall():
                version_stats.append({
                    'version': row[0],
                    'count': row[1],
                    'oldest': row[2],
                    'newest': row[3]
                })
            
            # Get data type distribution
            cursor.execute('''
                SELECT data_type, program_version, COUNT(*) as count
                FROM archive_entries 
                GROUP BY data_type, program_version
                ORDER BY data_type, count DESC
            ''')
            type_distribution = {}
            for row in cursor.fetchall():
                data_type = row[0]
                if data_type not in type_distribution:
                    type_distribution[data_type] = []
                type_distribution[data_type].append({
                    'version': row[1],
                    'count': row[2]
                })
            
            # Calculate total size estimate
            cursor.execute('''
                SELECT SUM(LENGTH(content)) as total_content_size,
                       COUNT(*) as total_entries
                FROM archive_entries
            ''')
            size_info = cursor.fetchone()
            
            # Get old entries that could be purged
            cutoff_date = (datetime.now() - timedelta(days=30)).isoformat()
            cursor.execute('''
                SELECT program_version, COUNT(*) as purgeable_count
                FROM archive_entries 
                WHERE created_at < ? AND program_version != ?
                GROUP BY program_version
            ''', (cutoff_date, self.current_version))
            
            purgeable_entries = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'version_stats': version_stats,
                'type_distribution': type_distribution,
                'total_content_size_bytes': size_info[0] or 0,
                'total_entries': size_info[1],
                'purgeable_entries': purgeable_entries,
                'current_version': self.current_version,
                'analysis_timestamp': datetime.now().isoformat()
            }
    
    def identify_purgeable_entries(self, policy_name: str = None) -> List[Dict[str, Any]]:
        """Identify entries that can be purged based on policies"""
        if policy_name and policy_name not in self.policies:
            raise ValueError(f"Unknown policy: {policy_name}")
        
        policies_to_check = [self.policies[policy_name]] if policy_name else list(self.policies.values())
        purgeable = []
        
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            for policy in policies_to_check:
                # Find entries that violate this policy
                
                # 1. Entries older than max_age_days
                cutoff_date = (datetime.now() - timedelta(days=policy.max_age_days)).isoformat()
                cursor.execute('''
                    SELECT id, program_version, data_type, source, operation, created_at
                    FROM archive_entries 
                    WHERE created_at < ? AND program_version != ?
                ''', (cutoff_date, self.current_version))
                
                current_entries = cursor.fetchall()
                
                # 2. Check version limits
                cursor.execute('''
                    SELECT DISTINCT program_version 
                    FROM archive_entries 
                    ORDER BY program_version DESC
                ''')
                all_versions = [row[0] for row in cursor.fetchall()]
                
                # Keep only the most recent N versions
                versions_to_purge = all_versions[policy.max_versions_keep:]
                
                for entry in current_entries:
                    entry_id, version, data_type, source, operation, created_at = entry
                    
                    # Apply preservation rules
                    should_preserve = False
                    
                    if policy.preserve_audit_data and 'audit' in source.lower():
                        should_preserve = True
                    
                    if policy.preserve_regression_tests and 'regression' in source.lower():
                        should_preserve = True
                    
                    if version in versions_to_purge and not should_preserve:
                        purgeable.append({
                            'id': entry_id,
                            'version': version,
                            'data_type': data_type,
                            'source': source,
                            'operation': operation,
                            'created_at': created_at,
                            'policy': policy.name,
                            'reason': f"Version {version} outside retention window or age > {policy.max_age_days} days"
                        })
            
            conn.close()
            
        return purgeable
    
    def execute_purge(self, dry_run: bool = True, policy_name: str = None) -> Dict[str, Any]:
        """Execute purge operation"""
        purgeable_entries = self.identify_purgeable_entries(policy_name)
        
        purge_stats = {
            'dry_run': dry_run,
            'total_identified': len(purgeable_entries),
            'purged_count': 0,
            'errors': [],
            'policies_applied': [policy_name] if policy_name else list(self.policies.keys()),
            'timestamp': datetime.now().isoformat()
        }
        
        if dry_run:
            purge_stats['purgeable_entries'] = purgeable_entries[:10]  # Sample for review
            print(f"[PURGE] DRY RUN: Identified {len(purgeable_entries)} entries for purging")
            return purge_stats
        
        if not purgeable_entries:
            print("[PURGE] No entries identified for purging")
            return purge_stats
        
        # Create backup before purging
        archiver = get_archiver()
        backup_path = archiver.create_backup()
        print(f"[PURGE] Created backup before purging: {backup_path}")
        
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                # Delete entries in batches for better performance
                entry_ids = [entry['id'] for entry in purgeable_entries]
                batch_size = 100
                
                for i in range(0, len(entry_ids), batch_size):
                    batch = entry_ids[i:i + batch_size]
                    placeholders = ','.join(['?'] * len(batch))
                    
                    # Also remove from verification queue
                    cursor.execute(f'''
                        DELETE FROM verification_queue 
                        WHERE archive_entry_id IN ({placeholders})
                    ''', batch)
                    
                    # Remove from archive entries
                    cursor.execute(f'''
                        DELETE FROM archive_entries 
                        WHERE id IN ({placeholders})
                    ''', batch)
                    
                    purge_stats['purged_count'] += cursor.rowcount
                
                conn.commit()
                print(f"[PURGE] Successfully purged {purge_stats['purged_count']} entries")
                
            except Exception as e:
                conn.rollback()
                error_msg = f"Error during purge: {e}"
                purge_stats['errors'].append(error_msg)
                print(f"[PURGE] {error_msg}")
            finally:
                conn.close()
        
        return purge_stats
    
    def auto_purge_by_version_only(self):
        """Automatically purge ALL data from older versions - version-based cleanup only"""
        print(f"[PURGE] Starting automatic version-based cleanup for current version: {self.current_version}")
        
        # Tag current entries first
        tagged_count = self.tag_current_version_entries()
        
        # Analyze current state before cleanup
        analysis = self.analyze_archive_data()
        total_before = analysis['total_entries']
        versions_before = len(analysis['version_stats'])
        
        print(f"[PURGE] Pre-cleanup analysis: {total_before} entries across {versions_before} versions")
        
        # Identify all entries NOT from current version
        current_version_entries = []
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT id, program_version, data_type, source, operation, created_at
                FROM archive_entries 
                WHERE program_version != ? AND program_version IS NOT NULL
            ''', (self.current_version,))
            
            current_version_entries = cursor.fetchall()
            conn.close()
        
        if not current_version_entries:
            print("[PURGE] No current version entries found - archive is clean!")
            return {
                'current_version': self.current_version,
                'analysis': analysis,
                'purge_result': {
                    'total_identified': 0,
                    'purged_count': 0,
                    'errors': [],
                    'timestamp': datetime.now().isoformat()
                },
                'backup_cleanup': {'cleaned_backups': 0}
            }
        
        print(f"[PURGE] Found {len(current_version_entries)} entries from current versions to remove")
        
        # Create backup before major cleanup
        try:
            archiver = get_archiver()
            backup_path = archiver.create_backup()
            print(f"[PURGE] Created safety backup: {backup_path}")
        except Exception as e:
            print(f"[PURGE] Warning: Could not create backup: {e}")
        
        # Execute version-based purge
        purge_stats = {
            'total_identified': len(current_version_entries),
            'purged_count': 0,
            'errors': [],
            'timestamp': datetime.now().isoformat(),
            'versions_removed': set()
        }
        
        with self._lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            try:
                # Remove entries in batches for performance
                entry_ids = [entry[0] for entry in current_version_entries]
                versions_being_removed = set(entry[1] for entry in current_version_entries)
                purge_stats['versions_removed'] = list(versions_being_removed)
                
                batch_size = 100
                for i in range(0, len(entry_ids), batch_size):
                    batch = entry_ids[i:i + batch_size]
                    placeholders = ','.join(['?'] * len(batch))
                    
                    # Remove from verification queue first
                    cursor.execute(f'''
                        DELETE FROM verification_queue 
                        WHERE archive_entry_id IN ({placeholders})
                    ''', batch)
                    
                    # Remove from archive entries
                    cursor.execute(f'''
                        DELETE FROM archive_entries 
                        WHERE id IN ({placeholders})
                    ''', batch)
                    
                    purge_stats['purged_count'] += cursor.rowcount
                
                conn.commit()
                print(f"[PURGE] Successfully removed {purge_stats['purged_count']} entries from {len(versions_being_removed)} current versions")
                
            except Exception as e:
                conn.rollback()
                error_msg = f"Error during version-based purge: {e}"
                purge_stats['errors'].append(error_msg)
                print(f"[PURGE] {error_msg}")
            finally:
                conn.close()
        
        # Clean up current version backups
        backup_cleanup = self._cleanup_current_version_backups()
        
        # Final analysis
        final_analysis = self.analyze_archive_data()
        total_after = final_analysis['total_entries']
        versions_after = len(final_analysis['version_stats'])
        
        print(f"[PURGE] Cleanup complete: {total_after} entries remaining ({total_before - total_after} removed)")
        print(f"[PURGE] Versions reduced: {versions_before} → {versions_after}")
        
        return {
            'current_version': self.current_version,
            'analysis': final_analysis,
            'purge_result': purge_stats,
            'backup_cleanup': backup_cleanup,
            'summary': {
                'entries_before': total_before,
                'entries_after': total_after,
                'entries_removed': total_before - total_after,
                'versions_before': versions_before,
                'versions_after': versions_after
            }
        }
    
    def _cleanup_current_version_backups(self):
        """Clean up backup files from older versions"""
        cleaned_count = 0
        errors = []
        
        try:
            # Default backup directory structure
            backup_dir = "data/backups"
            
            if not os.path.exists(backup_dir):
                return {'cleaned_backups': 0, 'errors': []}
            
            # Find backup files that might contain version info
            for filename in os.listdir(backup_dir):
                if filename.startswith('archive_backup_') and filename.endswith('.db'):
                    file_path = os.path.join(backup_dir, filename)
                    
                    try:
                        # Get file modification time
                        file_mtime = os.path.getmtime(file_path)
                        days_old = (datetime.now().timestamp() - file_mtime) / (24 * 3600)
                        
                        # Current versions)
                        if days_old > 7:
                            os.remove(file_path)
                            cleaned_count += 1
                            print(f"[PURGE] Removed old backup: {filename}")
                            
                    except Exception as e:
                        errors.append(f"Error removing {filename}: {e}")
                        
        except Exception as e:
            errors.append(f"Error accessing backup directory: {e}")
        
        return {
            'cleaned_backups': cleaned_count,
            'errors': errors
        }

    def auto_purge_on_startup(self):
        """Automatically purge old data on system startup - now uses version-only cleanup"""
        return self.auto_purge_by_version_only()
    
    def get_archive_health_report(self) -> Dict[str, Any]:
        """Generate health report for archive management"""
        analysis = self.analyze_archive_data()
        
        # Calculate health metrics
        total_versions = len(analysis['version_stats'])
        current_version_entries = 0
        for stat in analysis['version_stats']:
            if stat['version'] == self.current_version:
                current_version_entries = stat['count']
                break
        
        purgeable_count = sum(analysis['purgeable_entries'].values())
        health_score = min(100, max(0, 100 - (total_versions - 1) * 5 - (purgeable_count / analysis['total_entries']) * 50))
        
        return {
            'health_score': round(health_score, 1),
            'total_entries': analysis['total_entries'],
            'total_versions': total_versions,
            'current_version': self.current_version,
            'current_version_entries': current_version_entries,
            'purgeable_entries': purgeable_count,
            'archive_size_mb': round(analysis['total_content_size_bytes'] / 1024 / 1024, 2),
            'policies_active': len(self.policies),
            'recommendations': self._generate_recommendations(analysis)
        }
    
    def _generate_recommendations(self, analysis: Dict[str, Any]) -> List[str]:
        """Generate recommendations for archive management"""
        recommendations = []
        
        if len(analysis['version_stats']) > 10:
            recommendations.append("Consider purging current version data - more than 10 versions detected")
        
        if analysis['total_content_size_bytes'] > 100 * 1024 * 1024:  # 100MB
            recommendations.append("Archive size is large (>100MB) - consider implementing size-based purging")
        
        purgeable_count = sum(analysis['purgeable_entries'].values())
        if purgeable_count > analysis['total_entries'] * 0.3:
            recommendations.append("Over 30% of entries are purgeable - run purge operation")
        
        return recommendations

# Global purge manager instance
_purge_manager = None

def get_purge_manager() -> DataArchivePurgeManager:
    """Get global purge manager instance (singleton pattern)"""
    global _purge_manager
    if _purge_manager is None:
        _purge_manager = DataArchivePurgeManager()
    return _purge_manager

def auto_purge_startup():
    """Run automatic purge on startup - version-based cleanup only"""
    return get_purge_manager().auto_purge_by_version_only()

def auto_purge_version_only():
    """Run version-only cleanup - removes all data from older versions"""
    return get_purge_manager().auto_purge_by_version_only()

def get_archive_health():
    """Get archive health report"""
    return get_purge_manager().get_archive_health_report()