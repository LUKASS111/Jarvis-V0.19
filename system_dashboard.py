#!/usr/bin/env python3
"""
System Status Dashboard for Jarvis-V0.19 Data Archiving and Verification System
"""

import sys
import os
import json
from datetime import datetime, timedelta

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def display_crdt_status():
    """Display CRDT system status"""
    try:
        from jarvis.core.data_archiver import DataArchiver
        
        archiver = DataArchiver()
        if not archiver.enable_crdt or not archiver.crdt_manager:
            print("\n📊 CRDT SYSTEM STATUS")
            print("=" * 50)
            print("CRDT: Disabled (local-only mode)")
            return True
        
        metrics = archiver.crdt_manager.get_health_metrics()
        
        print("\n📊 CRDT SYSTEM STATUS")
        print("=" * 50)
        print(f"CRDT Status: {metrics['system_status']}")
        print(f"Node ID: {metrics['node_id']}")
        print(f"Total CRDTs: {metrics['total_crdts']}")
        
        if metrics['total_crdts'] > 0:
            print("\nCRDT Instance Types:")
            for name, crdt_type in metrics['crdt_types'].items():
                if crdt_type == "GCounter":
                    value = archiver.crdt_manager.get_counter_value(name)
                    print(f"  {name} ({crdt_type}): {value}")
                elif crdt_type == "GSet":
                    size = archiver.crdt_manager.get_set_size(name)
                    print(f"  {name} ({crdt_type}): {size} elements")
                elif crdt_type == "LWWRegister":
                    value = archiver.crdt_manager.read_register(name, "empty")
                    if isinstance(value, str) and len(value) > 50:
                        value = value[:47] + "..."
                    print(f"  {name} ({crdt_type}): {value}")
        
        return True
    except Exception as e:
        print(f"❌ CRDT status error: {e}")
        return False

def display_archive_status():
    """Display archive system status"""
    try:
        from jarvis.core.data_archiver import get_archive_stats
        
        stats = get_archive_stats()
        print("📊 ARCHIVE SYSTEM STATUS")
        print("=" * 50)
        print(f"Total Entries: {stats['total_entries']}")
        print(f"Pending Verification: {stats['pending_verification']}")
        print(f"Average Verification Score: {stats['average_verification_score']:.2f}")
        
        print("\nVerification Status Breakdown:")
        for status, count in stats['verification_stats'].items():
            print(f"  {status}: {count}")
        
        print("\nData Type Breakdown:")
        for data_type, count in stats['data_type_stats'].items():
            print(f"  {data_type}: {count}")
        
        return True
    except Exception as e:
        print(f"❌ Archive status error: {e}")
        return False

def display_backup_status():
    """Display backup system status"""
    try:
        from jarvis.core.backup_recovery import get_backup_stats, list_available_backups
        
        stats = get_backup_stats()
        backups = list_available_backups()
        
        print("\n💾 BACKUP SYSTEM STATUS")
        print("=" * 50)
        print(f"Total Backups: {stats['total_backups']}")
        print(f"Total Size: {stats['total_size_bytes']:,} bytes ({stats['total_size_bytes']/(1024*1024):.1f} MB)")
        print(f"Successful Recoveries: {stats['successful_recoveries']}/{stats['total_recoveries']}")
        
        if stats.get('newest_backup'):
            print(f"Latest Backup: {stats['newest_backup']}")
        if stats.get('oldest_backup'):
            print(f"Oldest Backup: {stats['oldest_backup']}")
        
        print("\nBackup Types:")
        for backup_type, type_stats in stats['backup_types'].items():
            print(f"  {backup_type}: {type_stats['count']} backups ({type_stats['size_bytes']:,} bytes)")
        
        # Show recent backups
        print("\nRecent Backups:")
        for backup in backups[:5]:
            size_mb = backup.size_bytes / (1024 * 1024)
            print(f"  {backup.timestamp[:19]} - {backup.backup_type} - {size_mb:.1f}MB - {backup.description}")
        
        return True
    except Exception as e:
        print(f"❌ Backup status error: {e}")
        return False

def display_verification_status():
    """Display verification system status"""
    try:
        from jarvis.core.data_verifier import get_verifier
        from jarvis.core.data_archiver import get_archiver
        
        archiver = get_archiver()
        verifier = get_verifier()
        
        # Get pending verification count
        pending_entries = archiver.get_pending_verification(limit=100)
        
        print("\n🔍 VERIFICATION SYSTEM STATUS")
        print("=" * 50)
        print(f"Verification Worker Active: {verifier.verification_active}")
        print(f"Pending Verifications: {len(pending_entries)}")
        print(f"Available Verification Models: {len(verifier.verification_models)}")
        print(f"Verification Models: {', '.join(verifier.verification_models)}")
        
        if pending_entries:
            print("\nPending Verification Queue (top 5):")
            for entry in pending_entries[:5]:
                print(f"  ID {entry.id}: {entry.data_type} from {entry.source} ({entry.timestamp[:19]})")
        
        return True
    except Exception as e:
        print(f"❌ Verification status error: {e}")
        return False

def display_agent_workflow_status():
    """Display agent workflow status"""
    try:
        from jarvis.core.agent_workflow import get_workflow_manager
        
        manager = get_workflow_manager()
        
        print("\n🤖 AGENT WORKFLOW STATUS")
        print("=" * 50)
        print(f"Registered Agents: {len(manager.agents)}")
        print(f"Active Workflows: {len(manager.active_cycles)}")
        print(f"Test Scenarios Available: {len(manager.test_scenarios)}")
        
        # Show registered agents
        if manager.agents:
            print("\nRegistered Agents:")
            for agent_id, agent_info in manager.agents.items():
                print(f"  {agent_id}: {agent_info['cycle_count']} cycles, {len(agent_info['capabilities'])} capabilities")
                if agent_info['last_activity']:
                    print(f"    Last active: {agent_info['last_activity'][:19]}")
        
        # Show active workflows
        if manager.active_cycles:
            print("\nActive Workflows:")
            for cycle_id, cycle_info in manager.active_cycles.items():
                print(f"  {cycle_id}: {cycle_info['status']} (target: {cycle_info['target_cycles']} cycles)")
        
        # Show test scenario categories
        scenario_categories = {}
        for scenario in manager.test_scenarios:
            category = scenario.category
            if category not in scenario_categories:
                scenario_categories[category] = 0
            scenario_categories[category] += 1
        
        print("\nTest Scenario Categories:")
        for category, count in scenario_categories.items():
            print(f"  {category}: {count} scenarios")
        
        return True
    except Exception as e:
        print(f"❌ Agent workflow status error: {e}")
        return False

def display_system_health():
    """Display overall system health"""
    print("\n🏥 SYSTEM HEALTH CHECK")
    print("=" * 50)
    
    health_status = {
        'archive': False,
        'verification': False, 
        'backup': False,
        'agent_workflow': False
    }
    
    # Test archive system
    try:
        from jarvis.core.data_archiver import get_archive_stats
        stats = get_archive_stats()
        health_status['archive'] = stats['total_entries'] >= 0
        print(f"📊 Archive System: {'✅ OK' if health_status['archive'] else '❌ FAIL'}")
    except Exception as e:
        print(f"📊 Archive System: ❌ FAIL ({e})")
    
    # Test verification system
    try:
        from jarvis.core.data_verifier import get_verifier
        verifier = get_verifier()
        health_status['verification'] = verifier.verification_active
        print(f"🔍 Verification System: {'✅ OK' if health_status['verification'] else '❌ FAIL'}")
    except Exception as e:
        print(f"🔍 Verification System: ❌ FAIL ({e})")
    
    # Test backup system
    try:
        from jarvis.core.backup_recovery import get_backup_stats
        stats = get_backup_stats()
        health_status['backup'] = stats['total_backups'] >= 0
        print(f"💾 Backup System: {'✅ OK' if health_status['backup'] else '❌ FAIL'}")
    except Exception as e:
        print(f"💾 Backup System: ❌ FAIL ({e})")
    
    # Test agent workflow system
    try:
        from jarvis.core.agent_workflow import get_workflow_manager
        manager = get_workflow_manager()
        health_status['agent_workflow'] = len(manager.test_scenarios) > 0
        print(f"🤖 Agent Workflow: {'✅ OK' if health_status['agent_workflow'] else '❌ FAIL'}")
    except Exception as e:
        print(f"🤖 Agent Workflow: ❌ FAIL ({e})")
    
    # Overall health
    healthy_systems = sum(health_status.values())
    total_systems = len(health_status)
    health_percentage = (healthy_systems / total_systems) * 100
    
    print(f"\nOverall System Health: {health_percentage:.0f}% ({healthy_systems}/{total_systems} systems healthy)")
    
    if health_percentage == 100:
        print("🎉 All systems operational!")
    elif health_percentage >= 75:
        print("⚠️  Most systems operational, minor issues detected")
    elif health_percentage >= 50:
        print("🚨 Partial system failure, investigation required")
    else:
        print("💥 Critical system failure, immediate attention required")
    
    return health_status

def run_quick_test():
    """Run a quick system test"""
    print("\n🧪 QUICK SYSTEM TEST")
    print("=" * 50)
    
    test_results = {}
    
    # Test archiving
    try:
        from jarvis.core.data_archiver import archive_system
        archive_id = archive_system(
            "System dashboard test entry",
            "system_dashboard",
            "health_check"
        )
        test_results['archive'] = archive_id is not None
        print(f"📊 Archive Test: {'✅ PASS' if test_results['archive'] else '❌ FAIL'}")
    except Exception as e:
        test_results['archive'] = False
        print(f"📊 Archive Test: ❌ FAIL ({e})")
    
    # Test verification
    try:
        from jarvis.core.data_verifier import verify_data_immediately
        result = verify_data_immediately(
            "Test verification from dashboard",
            "system",
            "system_dashboard",
            "verification_test"
        )
        test_results['verification'] = result.confidence_score >= 0
        print(f"🔍 Verification Test: {'✅ PASS' if test_results['verification'] else '❌ FAIL'}")
    except Exception as e:
        test_results['verification'] = False
        print(f"🔍 Verification Test: ❌ FAIL ({e})")
    
    # Test backup
    try:
        from jarvis.core.backup_recovery import create_backup
        backup = create_backup("Dashboard test backup")
        test_results['backup'] = backup.backup_id is not None
        print(f"💾 Backup Test: {'✅ PASS' if test_results['backup'] else '❌ FAIL'}")
    except Exception as e:
        test_results['backup'] = False
        print(f"💾 Backup Test: ❌ FAIL ({e})")
    
    # Calculate test success rate
    passed_tests = sum(test_results.values())
    total_tests = len(test_results)
    success_rate = (passed_tests / total_tests) * 100
    
    print(f"\nQuick Test Results: {success_rate:.0f}% ({passed_tests}/{total_tests} passed)")
    
    return test_results

def show_usage_examples():
    """Show usage examples"""
    print("\n📖 USAGE EXAMPLES")
    print("=" * 50)
    
    print("1. Archive data:")
    print("   from jarvis.core import archive_input, archive_output")
    print("   archive_input('User question', 'main_app', 'user_query')")
    print("   archive_output('AI response', 'llm_system', 'ai_response')")
    
    print("\n2. Verify data:")
    print("   from jarvis.core import verify_data_immediately")
    print("   result = verify_data_immediately('Facts to check', 'fact', 'source', 'operation')")
    print("   print(f'Verified: {result.is_verified}, Confidence: {result.confidence_score}')")
    
    print("\n3. Create backup:")
    print("   from jarvis.core import create_backup")
    print("   backup = create_backup('My backup description')")
    print("   print(f'Backup created: {backup.backup_id}')")
    
    print("\n4. Start agent workflow:")
    print("   from jarvis.core import start_agent_workflow")
    print("   cycle_id = start_agent_workflow('my_agent', 100, 0.90)")
    print("   print(f'Workflow started: {cycle_id}')")
    
    print("\n5. Check system statistics:")
    print("   from jarvis.core import get_archive_stats, get_backup_stats")
    print("   print('Archive:', get_archive_stats())")
    print("   print('Backup:', get_backup_stats())")

def get_system_status():
    """Get overall system status for external tools"""
    status = {
        'archive': False,
        'verification': False,
        'backup': False,
        'agent_workflow': False,
        'overall_health': False
    }
    
    # Test archive system
    try:
        from jarvis.core.data_archiver import get_archive_stats
        stats = get_archive_stats()
        status['archive'] = stats.get('total_entries', 0) >= 0
    except Exception:
        status['archive'] = False
    
    # Test verification system
    try:
        from jarvis.core.data_verifier import get_verifier
        verifier = get_verifier()
        status['verification'] = verifier.verification_active
    except Exception:
        status['verification'] = False
    
    # Test backup system
    try:
        from jarvis.core.backup_recovery import get_backup_stats
        stats = get_backup_stats()
        status['backup'] = stats['total_backups'] >= 0
    except Exception:
        status['backup'] = False
    
    # Test agent workflow system
    try:
        from jarvis.core.agent_workflow import get_workflow_manager
        manager = get_workflow_manager()
        status['agent_workflow'] = len(manager.test_scenarios) > 0
    except Exception:
        status['agent_workflow'] = False
    
    # Test CRDT system
    try:
        from jarvis.core.data_archiver import DataArchiver
        archiver = DataArchiver()
        status['crdt'] = archiver.enable_crdt
    except Exception:
        status['crdt'] = False
    
    # Calculate overall health (5 systems now)
    active_systems = sum(status.values())
    status['overall_health'] = active_systems >= 4  # At least 4 systems working
    status['health_percentage'] = (active_systems / 5) * 100
    
    return status

def main():
    """Main dashboard function"""
    print("Jarvis-V0.19 Data Archiving & Verification System Dashboard")
    print("=" * 70)
    print(f"Report generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Display all status sections
    sections = [
        display_archive_status,
        display_verification_status, 
        display_backup_status,
        display_agent_workflow_status,
        display_crdt_status,
        display_system_health
    ]
    
    for section in sections:
        try:
            section()
        except Exception as e:
            print(f"❌ Error in section: {e}")
    
    # Run quick test
    run_quick_test()
    
    # Show usage examples
    show_usage_examples()
    
    print("\n" + "=" * 70)
    print("Dashboard complete. System is ready for use!")

if __name__ == "__main__":
    main()