#!/usr/bin/env python3
"""
Demo script showing archive purge functionality with simulated old versions
"""

import sys
import os
import sqlite3
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jarvis.core.archive_purge_manager import get_purge_manager
from jarvis.core.data_archiver import get_archiver

def create_simulated_old_data():
    """Create some simulated old version data for demonstration"""
    print("Creating simulated old version data...")
    
    archiver = get_archiver()
    
    # Simulate old versions
    old_versions = ["0.3.0", "0.3.5", "0.4.0"]
    old_dates = [
        datetime.now() - timedelta(days=60),  # 0.3.0 - 60 days old
        datetime.now() - timedelta(days=45),  # 0.3.5 - 45 days old  
        datetime.now() - timedelta(days=20),  # 0.4.0 - 20 days old
    ]
    
    # Insert old data directly into database for demo
    with sqlite3.connect(archiver.db_path) as conn:
        cursor = conn.cursor()
        
        created_entries = 0
        for version, old_date in zip(old_versions, old_dates):
            # Create some test entries for each old version
            for i in range(10):
                cursor.execute('''
                    INSERT INTO archive_entries (
                        timestamp, data_type, content, source, operation,
                        content_hash, metadata, verification_status, program_version, created_at
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    old_date.isoformat(),
                    'system',
                    f'Old test data from version {version} - entry {i}',
                    'test_data_generator',
                    'simulate_old_version',
                    f'hash_{version}_{i}',
                    '{}',
                    'verified',
                    version,
                    old_date.isoformat()
                ))
                created_entries += 1
        
        conn.commit()
        print(f"Created {created_entries} simulated old entries")
        return created_entries

def demo_purge_system():
    """Demonstrate the complete purge system functionality"""
    print("\n" + "="*60)
    print("ARCHIVE PURGE SYSTEM DEMONSTRATION")
    print("="*60)
    
    # Step 1: Show initial state
    print("\n1. Initial Archive State:")
    manager = get_purge_manager()
    analysis = manager.analyze_archive_data()
    
    print(f"   Total entries: {analysis['total_entries']:,}")
    print(f"   Versions detected: {len(analysis['version_stats'])}")
    for stat in analysis['version_stats']:
        print(f"     - {stat['version']}: {stat['count']} entries")
    
    # Step 2: Create old data if we only have current version
    if len(analysis['version_stats']) == 1:
        print("\n2. Creating simulated old version data...")
        old_entries = create_simulated_old_data()
        
        # Re-analyze after adding old data
        analysis = manager.analyze_archive_data()
        print(f"   Added {old_entries} old entries")
        print(f"   New total: {analysis['total_entries']:,} entries")
        print(f"   Versions now: {len(analysis['version_stats'])}")
    
    # Step 3: Analyze purgeable entries
    print("\n3. Analyzing Purgeable Entries:")
    for policy_name in ['test_data', 'system_logs']:
        purgeable = manager.identify_purgeable_entries(policy_name)
        print(f"   Policy '{policy_name}': {len(purgeable)} purgeable entries")
        
        if purgeable:
            for entry in purgeable[:3]:  # Show first 3
                print(f"     - {entry['version']}: {entry['source']} ({entry['reason'][:50]}...)")
    
    # Step 4: Dry run demonstration
    print("\n4. Dry Run Purge (test_data policy):")
    dry_result = manager.execute_purge(dry_run=True, policy_name="test_data")
    print(f"   Would purge: {dry_result['total_identified']} entries")
    
    # Step 5: Execute limited purge if we have purgeable entries
    if dry_result['total_identified'] > 0:
        print("\n5. Executing Purge Operation:")
        print("   Creating backup before purge...")
        
        purge_result = manager.execute_purge(dry_run=False, policy_name="test_data")
        print(f"   Purged: {purge_result['purged_count']} entries")
        
        if purge_result.get('errors'):
            print(f"   Errors: {len(purge_result['errors'])}")
            
        # Show final state
        final_analysis = manager.analyze_archive_data()
        print(f"   Final total: {final_analysis['total_entries']:,} entries")
    else:
        print("\n5. No entries to purge - archive is already clean!")
    
    # Step 6: Health report
    print("\n6. Archive Health Report:")
    health = manager.get_archive_health_report()
    print(f"   Health Score: {health['health_score']}/100")
    print(f"   Archive Size: {health['archive_size_mb']} MB")
    print(f"   Active Policies: {health['policies_active']}")
    
    if health['recommendations']:
        print("   Recommendations:")
        for rec in health['recommendations']:
            print(f"     • {rec}")
    else:
        print("   No recommendations - archive is healthy!")
    
    print("\n" + "="*60)
    print("DEMONSTRATION COMPLETE")
    print("="*60)

def main():
    """Run the demo"""
    try:
        demo_purge_system()
        return True
    except Exception as e:
        print(f"Demo failed: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)