#!/usr/bin/env python3
"""
Test script for Archive Purge Manager functionality
Tests all aspects of the data archiving purge policy implementation.
"""

import sys
import os
import json
import sqlite3
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis.core.archive_purge_manager import (
    DataArchivePurgeManager, get_purge_manager, auto_purge_startup, get_archive_health
)
from jarvis.core.data_archiver import get_archiver, archive_input, archive_output

def test_purge_manager_creation():
    """Test basic purge manager functionality"""
    print("\n=== Testing Purge Manager Creation ===")
    
    try:
        manager = DataArchivePurgeManager()
        print(f"[OK] Purge manager created successfully")
        print(f"[INFO] Current version: {manager.current_version}")
        print(f"[INFO] Policies loaded: {len(manager.policies)}")
        
        for policy_name, policy in manager.policies.items():
            print(f"  - {policy_name}: keep {policy.max_versions_keep} versions, {policy.max_age_days} days max age")
        
        return True
    except Exception as e:
        print(f"[FAIL] Error creating purge manager: {e}")
        return False

def test_version_column_addition():
    """Test adding program_version column to existing database"""
    print("\n=== Testing Version Column Addition ===")
    
    try:
        manager = get_purge_manager()
        
        # Check if column was added
        with sqlite3.connect(manager.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("PRAGMA table_info(archive_entries)")
            columns = [row[1] for row in cursor.fetchall()]
            
            if 'program_version' in columns:
                print("[OK] program_version column exists")
                
                # Check if existing entries were tagged
                cursor.execute("SELECT COUNT(*) FROM archive_entries WHERE program_version = ?", (manager.current_version,))
                tagged_count = cursor.fetchone()[0]
                print(f"[INFO] {tagged_count} entries tagged with current version")
                
                return True
            else:
                print("[FAIL] program_version column missing")
                return False
                
    except Exception as e:
        print(f"[FAIL] Error checking version column: {e}")
        return False

def test_archive_analysis():
    """Test archive data analysis functionality"""
    print("\n=== Testing Archive Analysis ===")
    
    try:
        manager = get_purge_manager()
        analysis = manager.analyze_archive_data()
        
        print(f"[OK] Analysis completed")
        print(f"[INFO] Total entries: {analysis['total_entries']}")
        print(f"[INFO] Total content size: {analysis['total_content_size_bytes']:,} bytes")
        print(f"[INFO] Current version: {analysis['current_version']}")
        print(f"[INFO] Version distribution:")
        
        for version_stat in analysis['version_stats'][:5]:  # Show top 5
            print(f"  - {version_stat['version']}: {version_stat['count']} entries")
        
        print(f"[INFO] Data type distribution:")
        for data_type, versions in analysis['type_distribution'].items():
            total_count = sum(v['count'] for v in versions)
            print(f"  - {data_type}: {total_count} entries")
        
        return True
    except Exception as e:
        print(f"[FAIL] Error in archive analysis: {e}")
        return False

def test_purge_identification():
    """Test identification of purgeable entries"""
    print("\n=== Testing Purge Identification ===")
    
    try:
        manager = get_purge_manager()
        
        # Test with test_data policy (most aggressive)
        purgeable = manager.identify_purgeable_entries("test_data")
        print(f"[OK] Identified {len(purgeable)} purgeable entries with test_data policy")
        
        if purgeable:
            print("[INFO] Sample purgeable entries:")
            for entry in purgeable[:3]:  # Show first 3
                print(f"  - ID {entry['id']}: {entry['source']} ({entry['version']}) - {entry['reason']}")
        
        # Test with all policies
        all_purgeable = manager.identify_purgeable_entries()
        print(f"[INFO] Total purgeable with all policies: {len(all_purgeable)}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Error in purge identification: {e}")
        return False

def test_dry_run_purge():
    """Test dry run purge operation"""
    print("\n=== Testing Dry Run Purge ===")
    
    try:
        manager = get_purge_manager()
        
        # Perform dry run
        purge_result = manager.execute_purge(dry_run=True, policy_name="test_data")
        
        print(f"[OK] Dry run completed")
        print(f"[INFO] Would purge {purge_result['total_identified']} entries")
        print(f"[INFO] Policies applied: {purge_result['policies_applied']}")
        
        if purge_result.get('purgeable_entries'):
            print("[INFO] Sample entries that would be purged:")
            for entry in purge_result['purgeable_entries'][:3]:
                print(f"  - {entry['source']} ({entry['version']}): {entry['reason']}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Error in dry run purge: {e}")
        return False

def test_health_report():
    """Test archive health reporting"""
    print("\n=== Testing Archive Health Report ===")
    
    try:
        health = get_archive_health()
        
        print(f"[OK] Health report generated")
        print(f"[INFO] Health Score: {health['health_score']}/100")
        print(f"[INFO] Total entries: {health['total_entries']}")
        print(f"[INFO] Current version entries: {health['current_version_entries']}")
        print(f"[INFO] Archive size: {health['archive_size_mb']} MB")
        print(f"[INFO] Purgeable entries: {health['purgeable_entries']}")
        
        if health['recommendations']:
            print("[INFO] Recommendations:")
            for rec in health['recommendations']:
                print(f"  - {rec}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Error in health report: {e}")
        return False

def test_version_tagging_in_new_entries():
    """Test that new archive entries get proper version tags"""
    print("\n=== Testing Version Tagging in New Entries ===")
    
    try:
        # Create some test entries
        test_content = f"Test entry created at {datetime.now().isoformat()}"
        
        # Archive some test data
        entry_id = archive_input(test_content, "test_purge_system", "version_tag_test")
        
        # Check if it was tagged properly
        with sqlite3.connect("data/jarvis_archive.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT program_version FROM archive_entries WHERE id = ?", (entry_id,))
            result = cursor.fetchone()
            
            if result and result[0] != 'unknown':
                print(f"[OK] New entry properly tagged with version: {result[0]}")
                return True
            else:
                print(f"[FAIL] New entry not properly tagged: {result}")
                return False
                
    except Exception as e:
        print(f"[FAIL] Error testing version tagging: {e}")
        return False

def test_startup_integration():
    """Test automatic purge on startup"""
    print("\n=== Testing Startup Integration ===")
    
    try:
        result = auto_purge_startup()
        
        print(f"[OK] Startup purge completed")
        
        if result:
            analysis = result.get('analysis', {})
            purge_result = result.get('purge_result', {})
            
            print(f"[INFO] Archive entries before: {analysis.get('total_entries', 'unknown')}")
            print(f"[INFO] Entries purged: {purge_result.get('purged_count', 0)}")
            
            if purge_result.get('errors'):
                print(f"[WARN] Purge errors: {purge_result['errors']}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Error in startup integration: {e}")
        return False

def main():
    """Run all purge manager tests"""
    print("Archive Purge Manager Test Suite")
    print("=" * 50)
    
    tests = [
        test_purge_manager_creation,
        test_version_column_addition,
        test_archive_analysis,
        test_purge_identification,
        test_dry_run_purge,
        test_health_report,
        test_version_tagging_in_new_entries,
        test_startup_integration
    ]
    
    passed = 0
    total = len(tests)
    
    for test in tests:
        try:
            if test():
                passed += 1
        except Exception as e:
            print(f"[ERROR] Test {test.__name__} failed with exception: {e}")
    
    print(f"\n=== Test Results ===")
    print(f"Passed: {passed}/{total}")
    print(f"Success Rate: {(passed/total)*100:.1f}%")
    
    if passed == total:
        print("[EXCELLENT] All purge manager tests passed!")
        return True
    else:
        print(f"[WARNING] {total-passed} tests failed")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)