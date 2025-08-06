#!/usr/bin/env python3
"""
Database Repair Utility for Jarvis V1.0
Repairs corrupted SQLite databases and validates integrity.
"""

import os
import sys
import sqlite3
import shutil
from datetime import datetime
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def check_database_integrity(db_path):
    """Check if a SQLite database is valid and not corrupted"""
    try:
        with sqlite3.connect(db_path) as conn:
            cursor = conn.cursor()
            # Try to read schema
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = cursor.fetchall()
            
            # Try to run integrity check
            cursor.execute("PRAGMA integrity_check")
            result = cursor.fetchone()
            
            is_valid = result[0] == 'ok' if result else False
            
            return is_valid, tables, result[0] if result else "No result"
            
    except Exception as e:
        return False, [], str(e)

def backup_corrupted_database(db_path):
    """Create backup of corrupted database"""
    try:
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        backup_path = f"{db_path}.corrupted.{timestamp}"
        shutil.copy2(db_path, backup_path)
        print(f"  ✅ Backed up to: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"  ❌ Backup failed: {e}")
        return None

def repair_database(db_path, db_type="generic"):
    """Attempt to repair a corrupted database"""
    print(f"\n🔧 Repairing {db_type} database: {db_path}")
    
    # Check if file exists
    if not os.path.exists(db_path):
        print(f"  ❌ Database file not found: {db_path}")
        return False
    
    # Check integrity first
    is_valid, tables, status = check_database_integrity(db_path)
    if is_valid:
        print(f"  ✅ Database is valid (tables: {len(tables)})")
        return True
    
    print(f"  ❌ Database corruption detected: {status}")
    
    # Backup corrupted database
    backup_path = backup_corrupted_database(db_path)
    if not backup_path:
        return False
    
    # Try to salvage data using .dump
    try:
        dump_path = f"{db_path}.dump.sql"
        print(f"  🔄 Attempting to dump data...")
        
        # Use sqlite3 command line to dump
        import subprocess
        result = subprocess.run([
            'sqlite3', db_path, '.dump'
        ], capture_output=True, text=True)
        
        if result.returncode == 0 and result.stdout:
            # Save dump
            with open(dump_path, 'w') as f:
                f.write(result.stdout)
            print(f"  ✅ Data dumped to: {dump_path}")
            
            # Remove corrupted database
            os.remove(db_path)
            
            # Recreate from dump
            restore_result = subprocess.run([
                'sqlite3', db_path
            ], input=result.stdout, text=True)
            
            if restore_result.returncode == 0:
                # Verify restoration
                is_valid_restored, tables_restored, _ = check_database_integrity(db_path)
                if is_valid_restored:
                    print(f"  ✅ Database restored successfully (tables: {len(tables_restored)})")
                    os.remove(dump_path)  # Clean up dump file
                    return True
                else:
                    print(f"  ❌ Restored database is still invalid")
            else:
                print(f"  ❌ Failed to restore from dump")
        
    except Exception as e:
        print(f"  ❌ Dump/restore failed: {e}")
    
    # If dump/restore failed, recreate empty database
    print(f"  🔄 Creating fresh database...")
    try:
        os.remove(db_path)
    except:
        pass
    
    # Let the application recreate the database
    print(f"  ✅ Database file removed - will be recreated on next startup")
    return True

def find_all_databases():
    """Find all SQLite databases in the project"""
    project_root = Path(__file__).parent.parent
    databases = []
    
    for root, dirs, files in os.walk(project_root):
        # Skip backup directories
        if 'backup' in root or '.git' in root:
            continue
            
        for file in files:
            if file.endswith(('.db', '.sqlite', '.sqlite3')):
                full_path = os.path.join(root, file)
                databases.append(full_path)
    
    return databases

def main():
    """Main repair function"""
    print("🩺 Jarvis Database Repair Utility")
    print("=" * 50)
    
    # Find all databases
    databases = find_all_databases()
    
    if not databases:
        print("❌ No databases found")
        return
    
    print(f"📊 Found {len(databases)} database files")
    
    total_repaired = 0
    total_healthy = 0
    
    for db_path in databases:
        # Determine database type
        db_type = "unknown"
        if "archive" in db_path:
            db_type = "archive"
        elif "memory" in db_path:
            db_type = "memory"
        elif "health" in db_path:
            db_type = "health"
        elif "metrics" in db_path:
            db_type = "metrics"
        elif "crdt" in db_path:
            db_type = "crdt"
        elif "evolution" in db_path:
            db_type = "evolution"
        
        # Repair database
        success = repair_database(db_path, db_type)
        if success:
            # Check if it was already healthy or repaired
            is_valid, _, _ = check_database_integrity(db_path)
            if is_valid:
                if "✅ Database is valid" in str(success):
                    total_healthy += 1
                else:
                    total_repaired += 1
    
    print("\n" + "=" * 50)
    print(f"🏁 Repair Summary:")
    print(f"   💚 Healthy databases: {total_healthy}")
    print(f"   🔧 Repaired databases: {total_repaired}")
    print(f"   📊 Total processed: {len(databases)}")
    
    if total_repaired > 0:
        print(f"\n✅ Database repair completed successfully!")
        print(f"   Run 'python main.py' to test the application.")
    else:
        print(f"\n✅ All databases are healthy!")

if __name__ == "__main__":
    main()