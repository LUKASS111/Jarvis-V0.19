#!/usr/bin/env python3
"""
Archive Purge Management CLI
Command-line interface for managing data archiving purge policies.
"""

import sys
import os
import argparse
import json
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from jarvis.core.archive_purge_manager import (
    get_purge_manager, get_archive_health, auto_purge_startup, auto_purge_version_only
)

def cmd_status():
    """Show current archive status and health"""
    print("Archive Status Report")
    print("=" * 50)
    
    try:
        manager = get_purge_manager()
        analysis = manager.analyze_archive_data()
        health = get_archive_health()
        
        print(f"Database Path: {manager.db_path}")
        print(f"Current Version: {manager.current_version}")
        print(f"Health Score: {health['health_score']}/100")
        print()
        
        print("Archive Statistics:")
        print(f"  Total Entries: {analysis['total_entries']:,}")
        print(f"  Content Size: {analysis['total_content_size_bytes']:,} bytes ({health['archive_size_mb']} MB)")
        print(f"  Versions: {len(analysis['version_stats'])}")
        print(f"  Purgeable: {health['purgeable_entries']:,}")
        print()
        
        print("Top 5 Versions by Entry Count:")
        for i, stat in enumerate(analysis['version_stats'][:5], 1):
            print(f"  {i}. {stat['version']}: {stat['count']:,} entries")
        print()
        
        print("Data Type Distribution:")
        for data_type, versions in analysis['type_distribution'].items():
            total = sum(v['count'] for v in versions)
            print(f"  {data_type}: {total:,} entries")
        print()
        
        if health['recommendations']:
            print("Recommendations:")
            for rec in health['recommendations']:
                print(f"  • {rec}")
        else:
            print("No recommendations - archive is healthy!")
            
    except Exception as e:
        print(f"Error getting status: {e}")
        return False
    
    return True

def cmd_analyze():
    """Analyze archive and identify purgeable entries"""
    print("Archive Purge Analysis")
    print("=" * 50)
    
    try:
        manager = get_purge_manager()
        
        print("Analyzing purgeable entries by policy...")
        print()
        
        for policy_name, policy in manager.policies.items():
            purgeable = manager.identify_purgeable_entries(policy_name)
            print(f"Policy '{policy_name}':")
            print(f"  Max Versions: {policy.max_versions_keep}")
            print(f"  Max Age: {policy.max_age_days} days")
            print(f"  Purgeable Entries: {len(purgeable):,}")
            
            if purgeable:
                print("  Sample entries that would be purged:")
                for entry in purgeable[:3]:
                    print(f"    - {entry['source']} ({entry['version']})")
            print()
            
    except Exception as e:
        print(f"Error during analysis: {e}")
        return False
    
    return True

def cmd_dry_run(policy=None):
    """Perform dry run purge"""
    print(f"Dry Run Purge - Policy: {policy or 'ALL'}")
    print("=" * 50)
    
    try:
        manager = get_purge_manager()
        result = manager.execute_purge(dry_run=True, policy_name=policy)
        
        print(f"Dry Run Results:")
        print(f"  Entries Identified: {result['total_identified']:,}")
        print(f"  Policies Applied: {', '.join(result['policies_applied'])}")
        print(f"  Timestamp: {result['timestamp']}")
        print()
        
        if result.get('purgeable_entries'):
            print("Sample entries that would be purged:")
            for entry in result['purgeable_entries']:
                print(f"  • ID {entry['id']}: {entry['source']} ({entry['version']})")
                print(f"    Reason: {entry['reason']}")
            print()
        
        if result['total_identified'] == 0:
            print("No entries identified for purging!")
        else:
            print(f"To execute this purge, run: {sys.argv[0]} purge --policy {policy or 'all'}")
            
    except Exception as e:
        print(f"Error during dry run: {e}")
        return False
    
    return True

def cmd_purge(policy=None, force=False):
    """Execute actual purge operation"""
    if not force:
        print("DANGER: This will permanently delete archive entries!")
        print("Use --force to confirm this operation.")
        return False
    
    print(f"Executing Purge - Policy: {policy or 'ALL'}")
    print("=" * 50)
    
    try:
        manager = get_purge_manager()
        result = manager.execute_purge(dry_run=False, policy_name=policy)
        
        print(f"Purge Results:")
        print(f"  Entries Purged: {result['purged_count']:,}")
        print(f"  Policies Applied: {', '.join(result['policies_applied'])}")
        print(f"  Timestamp: {result['timestamp']}")
        
        if result.get('errors'):
            print(f"  Errors: {len(result['errors'])}")
            for error in result['errors']:
                print(f"    • {error}")
        
        if result['purged_count'] > 0:
            print(f"\nSuccessfully purged {result['purged_count']} entries!")
        else:
            print("\nNo entries were purged.")
            
    except Exception as e:
        print(f"Error during purge: {e}")
        return False
    
    return True

def cmd_version_cleanup():
    """Run version-only cleanup - removes all data from older versions"""
    print("Version-Only Cleanup")
    print("=" * 50)
    print("WARNING: This will remove ALL data from older program versions!")
    print("Only current version data will be preserved.")
    print()
    
    try:
        result = auto_purge_version_only()
        
        if result:
            summary = result.get('summary', {})
            purge_result = result.get('purge_result', {})
            backup_cleanup = result.get('backup_cleanup', {})
            
            print("Version Cleanup Results:")
            print(f"  Current Version: {result.get('current_version', 'unknown')}")
            print(f"  Entries Before: {summary.get('entries_before', 0):,}")
            print(f"  Entries After: {summary.get('entries_after', 0):,}")
            print(f"  Entries Removed: {summary.get('entries_removed', 0):,}")
            print(f"  Versions Before: {summary.get('versions_before', 0)}")
            print(f"  Versions After: {summary.get('versions_after', 0)}")
            print()
            
            if purge_result.get('versions_removed'):
                print("Removed Versions:")
                for version in purge_result['versions_removed']:
                    print(f"  • {version}")
                print()
            
            print("Backup Cleanup:")
            print(f"  Old Backups Removed: {backup_cleanup.get('cleaned_backups', 0)}")
            
            if backup_cleanup.get('errors'):
                print("  Cleanup Errors:")
                for error in backup_cleanup['errors']:
                    print(f"    • {error}")
            
            if purge_result.get('errors'):
                print(f"\nPurge Errors: {len(purge_result['errors'])}")
                for error in purge_result['errors']:
                    print(f"  • {error}")
        else:
            print("Version cleanup completed with no results.")
            
    except Exception as e:
        print(f"Error during version cleanup: {e}")
        return False
    
    return True

def cmd_startup():
    """Run startup purge routine (version-based cleanup)"""
    print("Startup Purge Routine - Version-Based Cleanup")
    print("=" * 50)
    
    try:
        result = auto_purge_startup()
        
        if result:
            summary = result.get('summary', {})
            purge_result = result.get('purge_result', {})
            backup_cleanup = result.get('backup_cleanup', {})
            
            print("Startup Analysis:")
            print(f"  Current Version: {result.get('current_version', 'unknown')}")
            print(f"  Entries Before: {summary.get('entries_before', 0):,}")
            print(f"  Entries After: {summary.get('entries_after', 0):,}")
            print(f"  Entries Removed: {summary.get('entries_removed', 0):,}")
            print()
            
            print("Purge Results:")
            print(f"  Entries Purged: {purge_result.get('purged_count', 0):,}")
            print(f"  Old Backups Cleaned: {backup_cleanup.get('cleaned_backups', 0)}")
            
            if purge_result.get('errors'):
                print(f"  Errors: {len(purge_result['errors'])}")
        else:
            print("Startup purge completed with no results.")
            
    except Exception as e:
        print(f"Error during startup routine: {e}")
        return False
    
    return True

def cmd_config():
    """Show current configuration"""
    print("Purge Configuration")
    print("=" * 50)
    
    try:
        manager = get_purge_manager()
        
        print(f"Config File: {manager.config_path}")
        print(f"Current Version: {manager.current_version}")
        print()
        
        print("Active Policies:")
        for name, policy in manager.policies.items():
            print(f"  {name}:")
            print(f"    Max Versions: {policy.max_versions_keep}")
            print(f"    Max Age: {policy.max_age_days} days")
            print(f"    Preserve Audit: {policy.preserve_audit_data}")
            print(f"    Preserve Regression: {policy.preserve_regression_tests}")
            if policy.size_limit_mb:
                print(f"    Size Limit: {policy.size_limit_mb} MB")
            print()
            
    except Exception as e:
        print(f"Error showing config: {e}")
        return False
    
    return True

def main():
    """Main CLI interface"""
    parser = argparse.ArgumentParser(
        description="Archive Purge Management CLI",
        epilog="Use with caution - purge operations are permanent!"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Available commands')
    
    # Status command
    subparsers.add_parser('status', help='Show archive status and health')
    
    # Analyze command
    subparsers.add_parser('analyze', help='Analyze purgeable entries')
    
    # Dry run command
    dry_parser = subparsers.add_parser('dry-run', help='Perform dry run purge')
    dry_parser.add_argument('--policy', help='Specific policy to test')
    
    # Purge command
    purge_parser = subparsers.add_parser('purge', help='Execute purge operation')
    purge_parser.add_argument('--policy', help='Specific policy to apply')
    purge_parser.add_argument('--force', action='store_true', help='Confirm purge operation')
    
    # Startup command
    subparsers.add_parser('startup', help='Run startup purge routine (version-based)')
    
    # Version cleanup command  
    subparsers.add_parser('version-cleanup', help='Remove ALL data from older versions')
    
    # Config command
    subparsers.add_parser('config', help='Show current configuration')
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return False
    
    # Execute command
    if args.command == 'status':
        return cmd_status()
    elif args.command == 'analyze':
        return cmd_analyze()
    elif args.command == 'dry-run':
        return cmd_dry_run(args.policy)
    elif args.command == 'purge':
        return cmd_purge(args.policy, args.force)
    elif args.command == 'startup':
        return cmd_startup()
    elif args.command == 'version-cleanup':
        return cmd_version_cleanup()
    elif args.command == 'config':
        return cmd_config()
    else:
        print(f"Unknown command: {args.command}")
        return False

if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\nOperation cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)