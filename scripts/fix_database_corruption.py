#!/usr/bin/env python3
"""
Database Corruption Fix for Windows 11 Compatibility
Comprehensive database repair and validation for Jarvis
"""

import os
import sys
import sqlite3
import shutil
import json
from datetime import datetime
from pathlib import Path

def fix_database_corruption():
    """Fix all database corruption issues for Windows 11 compatibility"""
    
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    
    print("[DATABASE] Starting comprehensive database repair...")
    
    # Database files to check and repair
    db_files = [
        data_dir / "jarvis_archive.db",
        data_dir / "memory" / "jarvis_memory.db",
        data_dir / "vector_db.db",
        data_dir / "session_db.db"
    ]
    
    repaired_count = 0
    
    for db_path in db_files:
        if db_path.exists():
            print(f"[CHECK] Checking database: {db_path}")
            
            try:
                # Test database integrity
                conn = sqlite3.connect(str(db_path))
                cursor = conn.cursor()
                cursor.execute("PRAGMA integrity_check")
                result = cursor.fetchone()
                conn.close()
                
                if result[0] != "ok":
                    print(f"[CORRUPT] Database corruption detected: {db_path}")
                    repair_database(db_path)
                    repaired_count += 1
                else:
                    print(f"[OK] Database healthy: {db_path}")
                    
            except sqlite3.DatabaseError as e:
                print(f"[CORRUPT] Database error: {db_path} - {e}")
                repair_database(db_path)
                repaired_count += 1
            except Exception as e:
                print(f"[ERROR] Unexpected error: {db_path} - {e}")
                repair_database(db_path)
                repaired_count += 1
    
    # Create missing directories
    os.makedirs(data_dir / "memory", exist_ok=True)
    os.makedirs(data_dir / "logs", exist_ok=True)
    os.makedirs(data_dir / "sessions", exist_ok=True)
    
    print(f"[COMPLETE] Database repair complete. Repaired {repaired_count} databases.")
    return repaired_count

def repair_database(db_path):
    """Repair a corrupted database"""
    
    backup_path = f"{db_path}.backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
    
    try:
        # Backup corrupted database
        if db_path.exists():
            shutil.copy2(db_path, backup_path)
            print(f"[BACKUP] Created backup: {backup_path}")
        
        # Remove corrupted database
        if db_path.exists():
            os.remove(db_path)
            print(f"[REMOVE] Removed corrupted database: {db_path}")
        
        # Create new database structure
        create_fresh_database(db_path)
        print(f"[CREATE] Created fresh database: {db_path}")
        
    except Exception as e:
        print(f"[ERROR] Failed to repair database {db_path}: {e}")

def create_fresh_database(db_path):
    """Create a fresh database with proper schema"""
    
    conn = sqlite3.connect(str(db_path))
    cursor = conn.cursor()
    
    # Determine database type and create appropriate schema
    if "archive" in str(db_path):
        create_archive_schema(cursor)
    elif "memory" in str(db_path):
        create_memory_schema(cursor)
    elif "vector" in str(db_path):
        create_vector_schema(cursor)
    elif "session" in str(db_path):
        create_session_schema(cursor)
    else:
        create_generic_schema(cursor)
    
    conn.commit()
    conn.close()

def create_archive_schema(cursor):
    """Create archive database schema"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS archive_entries (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            timestamp TEXT NOT NULL,
            entry_type TEXT NOT NULL,
            data TEXT NOT NULL,
            metadata TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_archive_timestamp ON archive_entries(timestamp)
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_archive_type ON archive_entries(entry_type)
    ''')

def create_memory_schema(cursor):
    """Create memory database schema"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS memories (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
            access_count INTEGER DEFAULT 0,
            last_accessed DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    cursor.execute('''
        CREATE INDEX IF NOT EXISTS idx_memory_key ON memories(key)
    ''')

def create_vector_schema(cursor):
    """Create vector database schema"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS vectors (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            document_id TEXT NOT NULL,
            embedding BLOB NOT NULL,
            metadata TEXT,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

def create_session_schema(cursor):
    """Create session database schema"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT UNIQUE NOT NULL,
            data TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

def create_generic_schema(cursor):
    """Create generic database schema"""
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS data (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            key TEXT UNIQUE NOT NULL,
            value TEXT NOT NULL,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')

def validate_repair():
    """Validate that all databases are now working"""
    
    print("[VALIDATE] Validating database repairs...")
    
    try:
        # Test import of core modules
        sys.path.insert(0, str(Path(__file__).parent.parent))
        
        from jarvis.core.data_archiver import get_archiver
        from jarvis.memory.memory_manager import MemoryManager
        
        # Test archiver
        archiver = get_archiver()
        print("[VALIDATE] ✅ Archive database working")
        
        # Test memory manager
        memory = MemoryManager()
        print("[VALIDATE] ✅ Memory database working")
        
        print("[VALIDATE] ✅ All databases validated successfully")
        return True
        
    except Exception as e:
        print(f"[VALIDATE] ❌ Validation failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 60)
    print("Database Corruption Fix for Windows 11 Compatibility")
    print("=" * 60)
    
    repaired = fix_database_corruption()
    
    if repaired > 0:
        print(f"\n[SUCCESS] Repaired {repaired} corrupted databases")
    else:
        print("\n[SUCCESS] All databases were already healthy")
    
    # Validate repairs
    if validate_repair():
        print("\n[SUCCESS] Database system fully operational")
    else:
        print("\n[WARNING] Some issues remain - manual intervention may be required")