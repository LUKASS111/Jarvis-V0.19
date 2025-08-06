"""
Data Archiving System for Jarvis-V0.19
Comprehensive data archiving with SQLite backend for all program operations.
"""

import sqlite3
import json
import threading
import hashlib
from datetime import datetime
from typing import Dict, Any, Optional, List, Tuple
from dataclasses import dataclass
import os
import uuid

# Archive database path
ARCHIVE_DB_PATH = "data/jarvis_archive.db"
_archive_lock = threading.Lock()

@dataclass
class ArchiveEntry:
    """Represents a single archived data entry"""
    id: Optional[int]
    timestamp: str
    data_type: str  # input, output, intermediate, system
    content: str
    source: str  # module/function name that generated the data
    operation: str  # describe what operation was performed
    content_hash: str
    metadata: Dict[str, Any]
    verification_status: Optional[str]  # pending, verified, rejected, error
    verification_score: Optional[float]  # 0.0 to 1.0 confidence
    verification_model: Optional[str]
    verification_timestamp: Optional[str]
    verification_details: Optional[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        return {
            'id': self.id,
            'timestamp': self.timestamp,
            'data_type': self.data_type,
            'content': self.content,
            'source': self.source,
            'operation': self.operation,
            'content_hash': self.content_hash,
            'metadata': self.metadata,
            'verification_status': self.verification_status,
            'verification_score': self.verification_score,
            'verification_model': self.verification_model,
            'verification_timestamp': self.verification_timestamp,
            'verification_details': self.verification_details
        }

class DataArchiver:
    """Main data archiving system with SQLite backend and CRDT integration"""
    
    def __init__(self, db_path: str = ARCHIVE_DB_PATH, enable_crdt: bool = True):
        """
        Initialize the data archiver with SQLite backend and optional CRDT integration.
        
        Args:
            db_path (str): Path to SQLite database file (default: data/jarvis_archive.db)
            enable_crdt (bool): Enable CRDT integration for distributed operations
            
        Raises:
            DatabaseInitializationError: If database cannot be created or initialized
            CRDTIntegrationError: If CRDT system cannot be initialized
        """
        self.db_path = db_path
        self.current_version = self._get_current_version()
        self.enable_crdt = enable_crdt
        self._ensure_db_directory()
        self._init_database()
        
        # Initialize CRDT manager if enabled
        self.crdt_manager = None
        if self.enable_crdt:
            self._init_crdt_integration()
    
    def _init_crdt_integration(self):
        """Initialize CRDT manager integration"""
        try:
            from .crdt_manager import CRDTManager
            node_id = self._generate_node_id()
            self.crdt_manager = CRDTManager(node_id, self.db_path)
        except ImportError:
            self.enable_crdt = False
    
    def _generate_node_id(self) -> str:
        """Generate unique node ID for this instance"""
        import socket
        hostname = socket.gethostname()
        process_id = os.getpid()
        return f"jarvis_node_{hostname}_{process_id}"
    
    def _ensure_db_directory(self):
        """Ensure the data directory exists"""
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
    
    def _get_current_version(self) -> str:
        """Get current program version"""
        try:
            from jarvis.core.main import VERSION_STRING
            return VERSION_STRING
        except ImportError:
            # Fallback to git commit hash if version string not available
            import subprocess
            try:
                result = subprocess.run(['git', 'rev-parse', '--short', 'HEAD'], 
                                      capture_output=True, text=True, cwd=os.path.dirname(self.db_path))
                return f"git-{result.stdout.strip()}" if result.returncode == 0 else "unknown"
            except Exception:
                return "unknown"
    
    def _init_database(self):
        """Initialize the SQLite database with required tables"""
        with _archive_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Main archive table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS archive_entries (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    data_type TEXT NOT NULL,
                    content TEXT NOT NULL,
                    source TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    content_hash TEXT NOT NULL,
                    metadata TEXT NOT NULL,
                    verification_status TEXT DEFAULT 'pending',
                    verification_score REAL,
                    verification_model TEXT,
                    verification_timestamp TEXT,
                    verification_details TEXT,
                    program_version TEXT DEFAULT 'unknown',
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes separately
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_timestamp ON archive_entries(timestamp)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_data_type ON archive_entries(data_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_source ON archive_entries(source)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_verification_status ON archive_entries(verification_status)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_content_hash ON archive_entries(content_hash)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_program_version ON archive_entries(program_version)')
            
            # Ensure program_version column exists in existing tables
            cursor.execute("PRAGMA table_info(archive_entries)")
            columns = [row[1] for row in cursor.fetchall()]
            if 'program_version' not in columns:
                cursor.execute('ALTER TABLE archive_entries ADD COLUMN program_version TEXT DEFAULT ?', (self.current_version,))
            
            # Verification queue table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS verification_queue (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    archive_entry_id INTEGER NOT NULL,
                    priority INTEGER DEFAULT 1,
                    attempts INTEGER DEFAULT 0,
                    max_attempts INTEGER DEFAULT 3,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY(archive_entry_id) REFERENCES archive_entries(id)
                )
            ''')
            
            # Agent activities table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS agent_activities (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    agent_id TEXT NOT NULL,
                    activity_type TEXT NOT NULL,
                    description TEXT NOT NULL,
                    data TEXT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for agent activities
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_id ON agent_activities(agent_id)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_activity_type ON agent_activities(activity_type)')
            cursor.execute('CREATE INDEX IF NOT EXISTS idx_agent_timestamp ON agent_activities(timestamp)')
            
            conn.commit()
            conn.close()
    
    def _calculate_content_hash(self, content: str) -> str:
        """Calculate SHA-256 hash of content for deduplication"""
        return hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    def archive_data(self, 
                    data_type: str,
                    content: str, 
                    source: str,
                    operation: str,
                    metadata: Optional[Dict[str, Any]] = None) -> int:
        """
        Archive a piece of data
        
        Args:
            data_type: Type of data (input, output, intermediate, system)
            content: The actual data content
            source: Source module/function
            operation: Description of operation
            metadata: Additional metadata
            
        Returns:
            Archive entry ID
        """
        if metadata is None:
            metadata = {}
            
        content_hash = self._calculate_content_hash(content)
        timestamp = datetime.now().isoformat()
        
        entry = ArchiveEntry(
            id=None,
            timestamp=timestamp,
            data_type=data_type,
            content=content,
            source=source,
            operation=operation,
            content_hash=content_hash,
            metadata=metadata,
            verification_status='pending',
            verification_score=None,
            verification_model=None,
            verification_timestamp=None,
            verification_details=None
        )
        
        with _archive_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO archive_entries (
                    timestamp, data_type, content, source, operation,
                    content_hash, metadata, verification_status, program_version
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                entry.timestamp,
                entry.data_type,
                entry.content,
                entry.source,
                entry.operation,
                entry.content_hash,
                json.dumps(entry.metadata),
                entry.verification_status,
                self.current_version
            ))
            
            entry_id = cursor.lastrowid
            
            # Add to verification queue if it's important data
            if data_type in ['input', 'output']:
                cursor.execute('''
                    INSERT INTO verification_queue (archive_entry_id, priority)
                    VALUES (?, ?)
                ''', (entry_id, 1 if data_type == 'output' else 2))
            
            conn.commit()
            conn.close()
            
        # Update CRDT metrics if enabled
        if self.enable_crdt and self.crdt_manager:
            self._update_crdt_metrics(operation, data_type, entry_id)
            
        return entry_id
    
    def _update_crdt_metrics(self, operation: str, data_type: str, entry_id: int):
        """Update CRDT metrics based on archive operation"""
        try:
            # Increment operation counter
            self.crdt_manager.increment_counter(f"operations_{operation}", 1)
            self.crdt_manager.increment_counter(f"data_type_{data_type}", 1)
            self.crdt_manager.increment_counter("total_operations", 1)
            
            # Add to operation set (for tracking unique operations)
            self.crdt_manager.add_to_set("operation_types", operation)
            self.crdt_manager.add_to_set("data_types", data_type)
            
            # Update system status register
            status_data = {
                "last_operation": operation,
                "last_entry_id": entry_id,
                "timestamp": datetime.now().isoformat()
            }
            self.crdt_manager.write_register("system_status", json.dumps(status_data))
            
        except Exception as e:
            # Don't fail archiving if CRDT update fails
            pass
    
    def update_verification(self,
                          entry_id: int,
                          status: str,
                          score: Optional[float] = None,
                          model: Optional[str] = None,
                          details: Optional[str] = None):
        """Update verification status for an archive entry"""
        verification_timestamp = datetime.now().isoformat()
        
        with _archive_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                UPDATE archive_entries 
                SET verification_status = ?,
                    verification_score = ?,
                    verification_model = ?,
                    verification_timestamp = ?,
                    verification_details = ?
                WHERE id = ?
            ''', (status, score, model, verification_timestamp, details, entry_id))
            
            # Remove from verification queue if verification is complete
            if status in ['verified', 'rejected', 'error']:
                cursor.execute('''
                    DELETE FROM verification_queue WHERE archive_entry_id = ?
                ''', (entry_id,))
            
            conn.commit()
            conn.close()
    
    def get_pending_verification(self, limit: int = 10) -> List[ArchiveEntry]:
        """Get entries pending verification"""
        with _archive_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                SELECT a.* FROM archive_entries a
                JOIN verification_queue q ON a.id = q.archive_entry_id
                WHERE a.verification_status = 'pending'
                ORDER BY q.priority ASC, q.created_at ASC
                LIMIT ?
            ''', (limit,))
            
            entries = []
            for row in cursor.fetchall():
                metadata = json.loads(row[7]) if row[7] else {}
                entry = ArchiveEntry(
                    id=row[0], timestamp=row[1], data_type=row[2],
                    content=row[3], source=row[4], operation=row[5],
                    content_hash=row[6], metadata=metadata,
                    verification_status=row[8], verification_score=row[9],
                    verification_model=row[10], verification_timestamp=row[11],
                    verification_details=row[12]
                )
                entries.append(entry)
            
            conn.close()
            return entries
    
    def get_verified_data(self, 
                         data_type: Optional[str] = None,
                         source: Optional[str] = None,
                         min_score: float = 0.7,
                         limit: int = 100) -> List[ArchiveEntry]:
        """Get verified data entries with minimum confidence score"""
        with _archive_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            query = '''
                SELECT * FROM archive_entries 
                WHERE verification_status = 'verified' 
                AND verification_score >= ?
            '''
            params = [min_score]
            
            if data_type:
                query += ' AND data_type = ?'
                params.append(data_type)
            
            if source:
                query += ' AND source = ?'
                params.append(source)
            
            query += ' ORDER BY verification_score DESC, timestamp DESC LIMIT ?'
            params.append(limit)
            
            cursor.execute(query, params)
            
            entries = []
            for row in cursor.fetchall():
                metadata = json.loads(row[7]) if row[7] else {}
                entry = ArchiveEntry(
                    id=row[0], timestamp=row[1], data_type=row[2],
                    content=row[3], source=row[4], operation=row[5],
                    content_hash=row[6], metadata=metadata,
                    verification_status=row[8], verification_score=row[9],
                    verification_model=row[10], verification_timestamp=row[11],
                    verification_details=row[12]
                )
                entries.append(entry)
            
            conn.close()
            return entries
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get archive statistics"""
        with _archive_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total entries
            cursor.execute('SELECT COUNT(*) FROM archive_entries')
            total_entries = cursor.fetchone()[0]
            
            # Verification status counts
            cursor.execute('''
                SELECT verification_status, COUNT(*) 
                FROM archive_entries 
                GROUP BY verification_status
            ''')
            verification_stats = dict(cursor.fetchall())
            
            # Data type counts
            cursor.execute('''
                SELECT data_type, COUNT(*) 
                FROM archive_entries 
                GROUP BY data_type
            ''')
            data_type_stats = dict(cursor.fetchall())
            
            # Average verification score
            cursor.execute('''
                SELECT AVG(verification_score) 
                FROM archive_entries 
                WHERE verification_score IS NOT NULL
            ''')
            avg_score = cursor.fetchone()[0] or 0.0
            
            conn.close()
            
            return {
                'total_entries': total_entries,
                'verification_stats': verification_stats,
                'data_type_stats': data_type_stats,
                'average_verification_score': round(avg_score, 3),
                'pending_verification': verification_stats.get('pending', 0)
            }
    
    def log_agent_activity(self, agent_id: str, activity_type: str, 
                          description: str, data: Optional[Dict[str, Any]] = None):
        """Log agent activity"""
        with _archive_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            cursor.execute('''
                INSERT INTO agent_activities (agent_id, activity_type, description, data)
                VALUES (?, ?, ?, ?)
            ''', (agent_id, activity_type, description, 
                  json.dumps(data) if data else None))
            
            conn.commit()
            conn.close()
    
    def create_backup(self, backup_path: Optional[str] = None) -> str:
        """Create a backup of the archive database"""
        if not backup_path:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            backup_path = f"data/backups/archive_backup_{timestamp}.db"
        
        os.makedirs(os.path.dirname(backup_path), exist_ok=True)
        
        with _archive_lock:
            # Use SQLite backup API for consistent backup
            source_conn = sqlite3.connect(self.db_path)
            backup_conn = sqlite3.connect(backup_path)
            source_conn.backup(backup_conn)
            source_conn.close()
            backup_conn.close()
        
        return backup_path
    
    def restore_from_backup(self, backup_path: str):
        """Restore archive database from backup"""
        if not os.path.exists(backup_path):
            raise FileNotFoundError(f"Backup file not found: {backup_path}")
        
        with _archive_lock:
            # Create current backup before restore
            current_backup = self.create_backup()
            print(f"[BACKUP] Current database backed up to: {current_backup}")
            
            # Restore from backup
            backup_conn = sqlite3.connect(backup_path)
            restore_conn = sqlite3.connect(self.db_path)
            backup_conn.backup(restore_conn)
            backup_conn.close()
            restore_conn.close()
            
            print(f"[RESTORE] Database restored from: {backup_path}")
    
    def get_stats(self) -> Dict[str, Any]:
        """Get archive statistics"""
        with _archive_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Total entries
            cursor.execute("SELECT COUNT(*) FROM archive_entries")
            total_entries = cursor.fetchone()[0]
            
            # Pending verification
            cursor.execute("SELECT COUNT(*) FROM archive_entries WHERE verification_status = 'pending'")
            pending_verification = cursor.fetchone()[0]
            
            # Verified entries
            cursor.execute("SELECT COUNT(*) FROM archive_entries WHERE verification_status = 'verified'")
            verified_entries = cursor.fetchone()[0]
            
            # Rejected entries
            cursor.execute("SELECT COUNT(*) FROM archive_entries WHERE verification_status = 'rejected'")
            rejected_entries = cursor.fetchone()[0]
            
            # Data type breakdown
            cursor.execute("SELECT data_type, COUNT(*) FROM archive_entries GROUP BY data_type")
            data_types = dict(cursor.fetchall())
            
            conn.close()
            
            return {
                'total_entries': total_entries,
                'pending_verification': pending_verification,
                'verified_entries': verified_entries,
                'rejected_entries': rejected_entries,
                'verification_rate': (verified_entries / max(1, total_entries)) * 100,
                'data_types': data_types,
                'health_score': self._calculate_health_score(total_entries, pending_verification)
            }
    
    def execute_query(self, query: str, params: tuple = ()) -> List[tuple]:
        """Execute a SQL query and return results"""
        with _archive_lock:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(query, params)
            
            if query.strip().upper().startswith('SELECT'):
                results = cursor.fetchall()
            else:
                conn.commit()
                results = []
            
            conn.close()
            return results
    
    def _calculate_health_score(self, total_entries: int, pending_verification: int) -> float:
        """Calculate archive health score"""
        if total_entries == 0:
            return 100.0
        
        pending_ratio = pending_verification / total_entries
        
        # Health score decreases as pending ratio increases
        if pending_ratio < 0.1:  # Less than 10% pending
            return 100.0
        elif pending_ratio < 0.3:  # 10-30% pending
            return 85.0
        elif pending_ratio < 0.5:  # 30-50% pending
            return 70.0
        else:  # More than 50% pending
            return 50.0

# Global archiver instance
_archiver = None

def get_archiver() -> DataArchiver:
    """Get global archiver instance (singleton pattern)"""
    global _archiver
    if _archiver is None:
        _archiver = DataArchiver()
    return _archiver

# Convenience functions for easy use throughout the codebase
def archive_input(content: str, source: str, operation: str, metadata: Dict[str, Any] = None) -> int:
    """Archive input data"""
    return get_archiver().archive_data('input', content, source, operation, metadata)

def archive_output(content: str, source: str, operation: str, metadata: Dict[str, Any] = None) -> int:
    """Archive output data"""
    return get_archiver().archive_data('output', content, source, operation, metadata)

def archive_intermediate(content: str, source: str, operation: str, metadata: Dict[str, Any] = None) -> int:
    """Archive intermediate processing data"""
    return get_archiver().archive_data('intermediate', content, source, operation, metadata)

def archive_system(content: str, source: str, operation: str, metadata: Dict[str, Any] = None) -> int:
    """Archive system/debug data"""
    return get_archiver().archive_data('system', content, source, operation, metadata)

def get_archive_stats() -> Dict[str, Any]:
    """Get archive statistics"""
    return get_archiver().get_statistics()

def create_archive_backup() -> str:
    """Create archive backup"""
    return get_archiver().create_backup()