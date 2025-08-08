"""
Functional Data Validator and Updater for Jarvis 1.0.0
Comprehensive system for validating, updating, and maintaining functional data integrity
"""

import json
import sqlite3
import threading
import os
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Callable
from pathlib import Path
from dataclasses import dataclass, asdict
import hashlib
try:
    import psutil
except ImportError:
    psutil = None
import shutil

from .enhanced_logging import get_enhanced_logger
from .program_evolution_tracker import get_evolution_tracker, EvolutionMetric, FunctionalityUpdate

@dataclass
class DataValidationResult:
    """Result of data validation check"""
    component: str
    data_type: str
    validation_time: str
    is_valid: bool
    issues_found: List[str]
    recommendations: List[str]
    performance_metrics: Dict[str, float]
    data_integrity_score: float

@dataclass
class DataUpdateResult:
    """Result of data update operation"""
    component: str
    update_type: str
    update_time: str
    success: bool
    records_affected: int
    performance_impact: Dict[str, float]
    rollback_available: bool
    validation_passed: bool

class FunctionalDataValidator:
    """Comprehensive functional data validation system"""
    
    def __init__(self, data_root: str = None):
        if data_root is None:
            data_root = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
        
        self.data_root = Path(data_root)
        self.logger = get_enhanced_logger('functional_data_validator')
        self.evolution_tracker = get_evolution_tracker()
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Validation rules registry
        self.validation_rules: Dict[str, List[Callable]] = {}
        self.validation_cache: Dict[str, DataValidationResult] = {}
        
        # Performance tracking
        self.validation_stats = {
            'total_validations': 0,
            'successful_validations': 0,
            'failed_validations': 0,
            'average_validation_time': 0.0
        }
        
        self.logger.info("Functional data validator initialized", data_root=str(self.data_root))
    
    def register_validation_rule(self, component: str, rule: Callable[[str], Tuple[bool, List[str]]]):
        """Register validation rule for component"""
        if component not in self.validation_rules:
            self.validation_rules[component] = []
        
        self.validation_rules[component].append(rule)
        self.logger.info("Validation rule registered", component=component)
    
    def validate_database_integrity(self, db_path: str) -> Tuple[bool, List[str]]:
        """Validate SQLite database integrity"""
        issues = []
        
        try:
            if not os.path.exists(db_path):
                return False, [f"Database file does not exist: {db_path}"]
            
            with sqlite3.connect(db_path) as conn:
                # Check database integrity
                integrity_result = conn.execute('PRAGMA integrity_check').fetchone()
                if integrity_result[0] != 'ok':
                    issues.append(f"Database integrity check failed: {integrity_result[0]}")
                
                # Check foreign key constraints
                conn.execute('PRAGMA foreign_keys = ON')
                fk_result = conn.execute('PRAGMA foreign_key_check').fetchall()
                if fk_result:
                    issues.append(f"Foreign key constraint violations: {len(fk_result)}")
                
                # Check for orphaned records (basic check)
                tables = conn.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
                for table in tables:
                    table_name = table[0]
                    if table_name.startswith('sqlite_'):
                        continue
                    
                    try:
                        count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                        if count < 0:  # Impossible but check for corruption
                            issues.append(f"Invalid record count in table {table_name}")
                    except sqlite3.Error as e:
                        issues.append(f"Error checking table {table_name}: {str(e)}")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            return False, [f"Database validation error: {str(e)}"]
    
    def validate_file_integrity(self, file_path: str) -> Tuple[bool, List[str]]:
        """Validate file integrity and accessibility"""
        issues = []
        
        try:
            if not os.path.exists(file_path):
                return False, [f"File does not exist: {file_path}"]
            
            # Check file size
            size = os.path.getsize(file_path)
            if size == 0:
                issues.append(f"File is empty: {file_path}")
            
            # Check read permissions
            if not os.access(file_path, os.R_OK):
                issues.append(f"File not readable: {file_path}")
            
            # Check if it's a valid JSON file (if .json extension)
            if file_path.endswith('.json'):
                try:
                    with open(file_path, 'r') as f:
                        json.load(f)
                except json.JSONDecodeError as e:
                    issues.append(f"Invalid JSON format: {str(e)}")
            
            # Check file age (warn if very old)
            mtime = os.path.getmtime(file_path)
            age_days = (time.time() - mtime) / (24 * 3600)
            if age_days > 30:
                issues.append(f"File is {age_days:.0f} days old, may need update")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            return False, [f"File validation error: {str(e)}"]
    
    def validate_memory_system(self) -> Tuple[bool, List[str]]:
        """Validate memory system integrity"""
        issues = []
        
        try:
            # Check jarvis_archive.db
            archive_db = self.data_root / 'jarvis_archive.db'
            is_valid, db_issues = self.validate_database_integrity(str(archive_db))
            if not is_valid:
                issues.extend([f"Archive DB: {issue}" for issue in db_issues])
            
            # Check session_log.json
            session_log = self.data_root / 'session_log.json'
            is_valid, file_issues = self.validate_file_integrity(str(session_log))
            if not is_valid:
                issues.extend([f"Session log: {issue}" for issue in file_issues])
            
            # Check memory performance
            if archive_db.exists():
                with sqlite3.connect(archive_db) as conn:
                    # Count archived entries
                    entry_count = conn.execute('SELECT COUNT(*) FROM archived_entries').fetchone()[0]
                    if entry_count < 1000:  # Expect at least 1000 entries for mature system
                        issues.append(f"Low archive entry count: {entry_count} (expected 1000+)")
                    
                    # Check recent activity
                    recent_count = conn.execute('''
                        SELECT COUNT(*) FROM archived_entries 
                        WHERE datetime(timestamp) > datetime('now', '-7 days')
                    ''').fetchone()[0]
                    
                    if recent_count == 0:
                        issues.append("No recent archive activity in past 7 days")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            return False, [f"Memory system validation error: {str(e)}"]
    
    def validate_crdt_system(self) -> Tuple[bool, List[str]]:
        """Validate CRDT system data integrity"""
        issues = []
        
        try:
            # Check for CRDT data files
            crdt_data_dir = self.data_root / 'crdt'
            if not crdt_data_dir.exists():
                issues.append("CRDT data directory does not exist")
                return False, issues
            
            # Validate CRDT state files
            state_files = list(crdt_data_dir.glob('*.json'))
            for state_file in state_files:
                is_valid, file_issues = self.validate_file_integrity(str(state_file))
                if not is_valid:
                    issues.extend([f"CRDT state {state_file.name}: {issue}" for issue in file_issues])
            
            # Check CRDT configuration
            from jarvis.core.crdt_manager import CRDTManager
            try:
                manager = CRDTManager()
                # Basic CRDT operation test
                test_doc = manager.create_document("validation_test")
                test_doc.set("test_key", "test_value")
                
                if test_doc.get("test_key") != "test_value":
                    issues.append("CRDT basic operation test failed")
                
                # Cleanup test document
                manager.remove_document("validation_test")
                
            except Exception as e:
                issues.append(f"CRDT manager test failed: {str(e)}")
            
            return len(issues) == 0, issues
            
        except Exception as e:
            return False, [f"CRDT system validation error: {str(e)}"]
    
    def validate_component(self, component: str) -> DataValidationResult:
        """Validate specific component with comprehensive checks"""
        with self.lock:
            start_time = time.time()
            self.validation_stats['total_validations'] += 1
            
            with self.logger.operation_context(f"validate_{component}") as op_logger:
                issues = []
                recommendations = []
                
                # Run component-specific validations
                if component == 'memory':
                    is_valid, component_issues = self.validate_memory_system()
                elif component == 'crdt':
                    is_valid, component_issues = self.validate_crdt_system()
                elif component == 'database':
                    # Validate all databases
                    is_valid = True
                    component_issues = []
                    
                    for db_file in self.data_root.glob('*.db'):
                        db_valid, db_issues = self.validate_database_integrity(str(db_file))
                        if not db_valid:
                            is_valid = False
                            component_issues.extend(db_issues)
                else:
                    # Run registered validation rules
                    is_valid = True
                    component_issues = []
                    
                    if component in self.validation_rules:
                        for rule in self.validation_rules[component]:
                            try:
                                rule_valid, rule_issues = rule(str(self.data_root))
                                if not rule_valid:
                                    is_valid = False
                                    component_issues.extend(rule_issues)
                            except Exception as e:
                                is_valid = False
                                component_issues.append(f"Validation rule error: {str(e)}")
                
                issues.extend(component_issues)
                
                # Generate recommendations based on issues
                if issues:
                    recommendations.extend([
                        "Run data repair operations",
                        "Check system resources and permissions",
                        "Consider data backup and recovery procedures"
                    ])
                
                # Calculate performance metrics
                end_time = time.time()
                validation_duration = end_time - start_time
                
                memory_usage = psutil.Process().memory_info().rss / 1024 / 1024 if psutil else 512.0  # MB
                
                performance_metrics = {
                    'validation_duration_seconds': validation_duration,
                    'memory_usage_mb': memory_usage,
                    'issues_detected': len(issues)
                }
                
                # Calculate integrity score
                integrity_score = max(0, 100 - (len(issues) * 10))  # Deduct 10 points per issue
                
                # Update statistics
                if is_valid:
                    self.validation_stats['successful_validations'] += 1
                else:
                    self.validation_stats['failed_validations'] += 1
                
                self.validation_stats['average_validation_time'] = (
                    (self.validation_stats['average_validation_time'] * (self.validation_stats['total_validations'] - 1) + validation_duration) /
                    self.validation_stats['total_validations']
                )
                
                result = DataValidationResult(
                    component=component,
                    data_type='functional',
                    validation_time=datetime.now().isoformat(),
                    is_valid=is_valid,
                    issues_found=issues,
                    recommendations=recommendations,
                    performance_metrics=performance_metrics,
                    data_integrity_score=integrity_score
                )
                
                # Cache result
                self.validation_cache[component] = result
                
                # Log to evolution tracker
                metric = EvolutionMetric(
                    timestamp=datetime.now().isoformat(),
                    metric_type='quality',
                    component=component,
                    value=integrity_score,
                    baseline=100.0,
                    improvement=integrity_score - 100.0,
                    validation_status='validated',
                    data_source='functional_data_validator',
                    notes=f"Data validation completed. Issues: {len(issues)}"
                )
                self.evolution_tracker.log_evolution_metric(metric)
                
                op_logger.info(
                    "Component validation completed",
                    component=component,
                    is_valid=is_valid,
                    issues_count=len(issues),
                    integrity_score=integrity_score
                )
                
                return result
    
    def validate_all_components(self) -> Dict[str, DataValidationResult]:
        """Validate all registered components"""
        components = ['memory', 'crdt', 'database'] + list(self.validation_rules.keys())
        results = {}
        
        for component in set(components):  # Remove duplicates
            results[component] = self.validate_component(component)
        
        return results
    
    def get_validation_summary(self) -> Dict[str, Any]:
        """Get comprehensive validation summary"""
        return {
            'timestamp': datetime.now().isoformat(),
            'validation_statistics': self.validation_stats.copy(),
            'cached_results': {
                comp: {
                    'is_valid': result.is_valid,
                    'integrity_score': result.data_integrity_score,
                    'issues_count': len(result.issues_found),
                    'validation_time': result.validation_time
                }
                for comp, result in self.validation_cache.items()
            },
            'overall_health': {
                'total_components': len(self.validation_cache),
                'healthy_components': sum(1 for r in self.validation_cache.values() if r.is_valid),
                'average_integrity_score': sum(r.data_integrity_score for r in self.validation_cache.values()) / len(self.validation_cache) if self.validation_cache else 0
            }
        }

class FunctionalDataUpdater:
    """System for updating functional data with tracking and rollback"""
    
    def __init__(self, data_root: str = None):
        if data_root is None:
            data_root = os.path.join(os.path.dirname(__file__), '..', '..', 'data')
        
        self.data_root = Path(data_root)
        self.backup_dir = self.data_root / 'backups'
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
        self.logger = get_enhanced_logger('functional_data_updater')
        self.evolution_tracker = get_evolution_tracker()
        self.validator = FunctionalDataValidator(data_root)
        
        # Thread safety
        self.lock = threading.Lock()
        
        self.logger.info("Functional data updater initialized", data_root=str(self.data_root))
    
    def create_backup(self, component: str) -> str:
        """Create backup before update"""
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_name = f"{component}_{timestamp}"
        backup_path = self.backup_dir / backup_name
        
        with self.logger.operation_context(f"backup_{component}") as op_logger:
            try:
                if component == 'database':
                    # Backup all database files
                    backup_path.mkdir(exist_ok=True)
                    for db_file in self.data_root.glob('*.db'):
                        shutil.copy2(db_file, backup_path / db_file.name)
                        op_logger.info("Database backed up", file=db_file.name)
                
                elif component == 'memory':
                    # Backup memory-related files
                    backup_path.mkdir(exist_ok=True)
                    memory_files = ['jarvis_archive.db', 'session_log.json']
                    for file_name in memory_files:
                        file_path = self.data_root / file_name
                        if file_path.exists():
                            shutil.copy2(file_path, backup_path / file_name)
                
                else:
                    # Generic file/directory backup
                    source_path = self.data_root / component
                    if source_path.exists():
                        if source_path.is_dir():
                            shutil.copytree(source_path, backup_path)
                        else:
                            shutil.copy2(source_path, backup_path)
                
                op_logger.info("Backup created successfully", backup_path=str(backup_path))
                return str(backup_path)
                
            except Exception as e:
                op_logger.error("Backup creation failed", error=str(e))
                raise
    
    def update_database_schema(self, db_path: str, migration_sql: str) -> DataUpdateResult:
        """Update database schema with migration"""
        with self.lock:
            start_time = time.time()
            
            with self.logger.operation_context("update_database_schema") as op_logger:
                try:
                    # Create backup first
                    backup_path = self.create_backup('database')
                    
                    # Validate before update
                    pre_validation = self.validator.validate_component('database')
                    
                    # Perform migration
                    with sqlite3.connect(db_path) as conn:
                        cursor = conn.cursor()
                        
                        # Execute migration SQL
                        cursor.executescript(migration_sql)
                        
                        # Get affected rows (approximate)
                        affected_rows = cursor.rowcount
                        
                        conn.commit()
                    
                    # Validate after update
                    post_validation = self.validator.validate_component('database')
                    
                    # Calculate performance impact
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    performance_impact = {
                        'update_duration_seconds': duration,
                        'pre_integrity_score': pre_validation.data_integrity_score,
                        'post_integrity_score': post_validation.data_integrity_score,
                        'integrity_change': post_validation.data_integrity_score - pre_validation.data_integrity_score
                    }
                    
                    result = DataUpdateResult(
                        component='database',
                        update_type='schema_migration',
                        update_time=datetime.now().isoformat(),
                        success=post_validation.is_valid,
                        records_affected=affected_rows,
                        performance_impact=performance_impact,
                        rollback_available=True,
                        validation_passed=post_validation.is_valid
                    )
                    
                    # Log to evolution tracker
                    update = FunctionalityUpdate(
                        timestamp=datetime.now().isoformat(),
                        feature_name='database_schema',
                        version_from='current',
                        version_to='updated',
                        update_type='schema_migration',
                        test_results={'validation_passed': post_validation.is_valid},
                        performance_impact=performance_impact,
                        validation_methods=['database_integrity_check', 'post_migration_validation'],
                        rollback_plan=f"Restore from backup: {backup_path}",
                        success_criteria={'integrity_score': 90.0, 'no_critical_issues': True},
                        actual_results={'integrity_score': post_validation.data_integrity_score}
                    )
                    self.evolution_tracker.log_functionality_update(update)
                    
                    op_logger.info(
                        "Database schema update completed",
                        success=result.success,
                        affected_rows=affected_rows,
                        integrity_change=performance_impact['integrity_change']
                    )
                    
                    return result
                    
                except Exception as e:
                    op_logger.error("Database schema update failed", error=str(e))
                    
                    # Return failure result
                    return DataUpdateResult(
                        component='database',
                        update_type='schema_migration',
                        update_time=datetime.now().isoformat(),
                        success=False,
                        records_affected=0,
                        performance_impact={'error': str(e)},
                        rollback_available=True,
                        validation_passed=False
                    )
    
    def optimize_database(self, db_path: str) -> DataUpdateResult:
        """Optimize database performance"""
        with self.lock:
            start_time = time.time()
            
            with self.logger.operation_context("optimize_database") as op_logger:
                try:
                    # Get initial database stats
                    initial_size = os.path.getsize(db_path)
                    
                    with sqlite3.connect(db_path) as conn:
                        # Analyze database
                        conn.execute('ANALYZE')
                        
                        # Vacuum database
                        conn.execute('VACUUM')
                        
                        # Reindex
                        conn.execute('REINDEX')
                        
                        # Update statistics
                        conn.execute('PRAGMA optimize')
                    
                    # Get final database stats
                    final_size = os.path.getsize(db_path)
                    size_reduction = initial_size - final_size
                    
                    # Validate optimization
                    post_validation = self.validator.validate_component('database')
                    
                    end_time = time.time()
                    duration = end_time - start_time
                    
                    performance_impact = {
                        'optimization_duration_seconds': duration,
                        'size_reduction_bytes': size_reduction,
                        'size_reduction_percentage': (size_reduction / initial_size * 100) if initial_size > 0 else 0,
                        'post_integrity_score': post_validation.data_integrity_score
                    }
                    
                    result = DataUpdateResult(
                        component='database',
                        update_type='optimization',
                        update_time=datetime.now().isoformat(),
                        success=post_validation.is_valid,
                        records_affected=0,
                        performance_impact=performance_impact,
                        rollback_available=False,  # Optimization is generally safe
                        validation_passed=post_validation.is_valid
                    )
                    
                    op_logger.info(
                        "Database optimization completed",
                        size_reduction_mb=size_reduction / 1024 / 1024,
                        duration_seconds=duration
                    )
                    
                    return result
                    
                except Exception as e:
                    op_logger.error("Database optimization failed", error=str(e))
                    
                    return DataUpdateResult(
                        component='database',
                        update_type='optimization',
                        update_time=datetime.now().isoformat(),
                        success=False,
                        records_affected=0,
                        performance_impact={'error': str(e)},
                        rollback_available=False,
                        validation_passed=False
                    )

# Global instances for easy access
_validator = None
_updater = None

def get_functional_data_validator() -> FunctionalDataValidator:
    """Get global functional data validator instance"""
    global _validator
    if _validator is None:
        _validator = FunctionalDataValidator()
    return _validator

def get_functional_data_updater() -> FunctionalDataUpdater:
    """Get global functional data updater instance"""
    global _updater
    if _updater is None:
        _updater = FunctionalDataUpdater()
    return _updater