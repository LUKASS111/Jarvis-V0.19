#!/usr/bin/env python3
"""
Test script for version-based automatic purge system.
Demonstrates the automatic cleanup functionality.
"""

import sys
import os
import sqlite3

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jarvis.core.archive_purge_manager import (
    get_purge_manager, auto_purge_version_only, get_archive_health
)
from jarvis.core.data_archiver import get_archiver, ARCHIVE_DB_PATH

def simulate_old_version_data():
    """Add some test data from fake old versions to demonstrate cleanup"""
    
    # Add some entries with different versions for testing using direct DB access
    test_entries = [
        {
            "version": "0.3.0",
            "content": "Test data from version 0.3.0",
            "source": "test_old_version_1"
        },
        {
            "version": "0.3.9", 
            "content": "Test data from version 0.3.9",
            "source": "test_old_version_2"
        },
        {
            "version": "0.4.0-beta",
            "content": "Test data from version 0.4.0-beta",
            "source": "test_old_version_3"
        }
    ]
    
    # Manually insert test entries with old versions
    import threading
    lock = threading.Lock()
    
    with lock:
        conn = sqlite3.connect(ARCHIVE_DB_PATH)
        cursor = conn.cursor()
        
        for entry in test_entries:
            cursor.execute('''
                INSERT INTO archive_entries 
                (timestamp, data_type, content, source, operation, content_hash, 
                 metadata, verification_status, program_version)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                "2024-08-02T10:00:00.000000",
                "test",
                entry["content"],
                entry["source"],
                "test_operation",
                "test_hash",
                "{}",
                "verified",
                entry["version"]
            ))
        
        conn.commit()
        conn.close()
    
    print(f"[TEST] Added {len(test_entries)} test entries from old versions")
    return len(test_entries)

def test_version_purge():
    """Test the version-based purge system"""
    print("Testing Automatic Version-Based Archive Purge System")
    print("=" * 60)
    
    # Get initial status
    print("\n1. Initial Archive Status:")
    manager = get_purge_manager()
    initial_analysis = manager.analyze_archive_data()
    print(f"   Total Entries: {initial_analysis['total_entries']:,}")
    print(f"   Versions: {len(initial_analysis['version_stats'])}")
    print(f"   Current Version: {manager.current_version}")
    
    # Add some old version test data
    print("\n2. Adding Test Data from Old Versions:")
    added_count = simulate_old_version_data()
    
    # Check status after adding test data
    print("\n3. Archive Status After Adding Test Data:")
    analysis_with_old = manager.analyze_archive_data()
    print(f"   Total Entries: {analysis_with_old['total_entries']:,}")
    print(f"   Versions: {len(analysis_with_old['version_stats'])}")
    
    for stat in analysis_with_old['version_stats']:
        print(f"   - {stat['version']}: {stat['count']} entries")
    
    # Run version-based cleanup
    print("\n4. Running Version-Based Cleanup:")
    result = auto_purge_version_only()
    
    if result:
        summary = result.get('summary', {})
        purge_stats = result.get('purge_result', {})
        
        print(f"   Entries Before: {summary.get('entries_before', 0):,}")
        print(f"   Entries After: {summary.get('entries_after', 0):,}")
        print(f"   Entries Removed: {summary.get('entries_removed', 0):,}")
        print(f"   Versions Before: {summary.get('versions_before', 0)}")
        print(f"   Versions After: {summary.get('versions_after', 0)}")
        
        if purge_stats.get('versions_removed'):
            print("   Removed Versions:")
            for version in purge_stats['versions_removed']:
                print(f"     • {version}")
    
    # Final health check
    print("\n5. Final Health Status:")
    health = get_archive_health()
    print(f"   Health Score: {health['health_score']}/100")
    print(f"   Total Entries: {health['total_entries']:,}")
    print(f"   Total Versions: {health['total_versions']}")
    print(f"   Current Version Entries: {health['current_version_entries']:,}")
    print(f"   Purgeable Entries: {health['purgeable_entries']}")
    
    # Verify cleanup worked
    print("\n6. Verification:")
    if result:
        entries_removed = summary.get('entries_removed', 0)
        if entries_removed >= added_count:
            print(f"   ✅ SUCCESS: Removed {entries_removed} old version entries")
            print(f"   ✅ Archive now contains only current version data")
            print(f"   ✅ Health score: {health['health_score']}/100")
        else:
            print(f"   ❌ WARNING: Expected to remove {added_count}, actually removed {entries_removed}")
    
    return True

if __name__ == "__main__":
    try:
        test_version_purge()
        print("\n🎉 Version-based purge system test completed!")
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)