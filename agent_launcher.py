#!/usr/bin/env python3
"""
Agent Workflow Launcher for Jarvis-V0.19
Convenient script to start and manage agent workflows.
"""

import sys
import os
import time
import argparse
from datetime import datetime

# Add the current directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def start_production_workflow(agent_id="production_agent", cycles=100, compliance=0.95):
    """Start a production-grade agent workflow"""
    print(f"🚀 Starting Production Agent Workflow")
    print("=" * 50)
    print(f"Agent ID: {agent_id}")
    print(f"Target Cycles: {cycles}")
    print(f"Compliance Target: {compliance:.1%}")
    print()
    
    try:
        from jarvis.core.agent_workflow import get_workflow_manager, start_agent_workflow
        
        # Register the agent
        manager = get_workflow_manager()
        manager.register_agent(
            agent_id,
            capabilities=["testing", "verification", "correction", "production"],
            config={
                "timeout": 60,
                "max_retries": 3,
                "production_mode": True,
                "auto_correction": True
            }
        )
        print(f"✅ Agent {agent_id} registered successfully")
        
        # Start the workflow
        cycle_id = start_agent_workflow(agent_id, cycles, compliance)
        print(f"✅ Workflow started: {cycle_id}")
        print()
        
        # Monitor progress
        print("📊 Monitoring workflow progress...")
        print("Press Ctrl+C to stop monitoring (workflow will continue in background)")
        print()
        
        try:
            monitor_workflow(manager, cycle_id, cycles)
        except KeyboardInterrupt:
            print("\n⏸️  Monitoring stopped (workflow continues in background)")
            print(f"   Check status with: python agent_launcher.py --status {cycle_id}")
        
        return cycle_id
        
    except Exception as e:
        print(f"❌ Failed to start workflow: {e}")
        return None

def monitor_workflow(manager, cycle_id, target_cycles):
    """Monitor workflow progress"""
    last_update = time.time()
    
    while True:
        status = manager.get_cycle_status(cycle_id)
        
        if not status:
            print("❌ Workflow not found or completed")
            break
        
        current_time = time.time()
        if current_time - last_update >= 10:  # Update every 10 seconds
            print(f"📈 Status: {status['status']} | "
                  f"Started: {status['start_time'][:19]} | "
                  f"Target: {target_cycles} cycles")
            
            if status['status'] == 'completed':
                print(f"✅ Workflow completed!")
                if status.get('compliance_achieved'):
                    print(f"🎯 Compliance target achieved!")
                else:
                    print(f"⚠️  Compliance target not fully achieved")
                break
            elif status['status'] == 'error':
                print(f"❌ Workflow failed: {status.get('error', 'Unknown error')}")
                break
            
            last_update = current_time
        
        time.sleep(2)

def show_workflow_status(cycle_id=None):
    """Show status of workflows"""
    try:
        from jarvis.core.agent_workflow import get_workflow_manager
        
        manager = get_workflow_manager()
        
        if cycle_id:
            status = manager.get_cycle_status(cycle_id)
            if status:
                print(f"Workflow {cycle_id}:")
                print(f"  Status: {status['status']}")
                print(f"  Agent: {status['agent_id']}")
                print(f"  Started: {status['start_time']}")
                print(f"  Target Cycles: {status['target_cycles']}")
                print(f"  Compliance Target: {status['target_compliance']:.1%}")
                if status.get('end_time'):
                    print(f"  Ended: {status['end_time']}")
                if status.get('compliance_achieved'):
                    print(f"  Compliance Achieved: {status['compliance_achieved']}")
            else:
                print(f"❌ Workflow {cycle_id} not found")
        else:
            # Show all active workflows
            if manager.active_cycles:
                print("Active Workflows:")
                for wf_id, wf_status in manager.active_cycles.items():
                    print(f"  {wf_id}: {wf_status['status']} ({wf_status['agent_id']})")
            else:
                print("No active workflows")
            
            # Show registered agents
            if manager.agents:
                print("\nRegistered Agents:")
                for agent_id, agent_info in manager.agents.items():
                    print(f"  {agent_id}: {agent_info['cycle_count']} cycles completed")
    
    except Exception as e:
        print(f"❌ Error getting workflow status: {e}")

def list_test_scenarios():
    """List available test scenarios"""
    try:
        from jarvis.core.agent_workflow import get_workflow_manager
        
        manager = get_workflow_manager()
        
        print("Available Test Scenarios:")
        print("=" * 50)
        
        for scenario in manager.test_scenarios:
            print(f"ID: {scenario.id}")
            print(f"  Name: {scenario.name}")
            print(f"  Category: {scenario.category}")
            print(f"  Priority: {scenario.priority}")
            print(f"  Description: {scenario.description}")
            print(f"  Expected Outcomes: {', '.join(scenario.expected_outcomes)}")
            print()
    
    except Exception as e:
        print(f"❌ Error listing scenarios: {e}")

def run_quick_test():
    """Run a quick 10-cycle test"""
    print("🧪 Running Quick Test (10 cycles)")
    print("=" * 40)
    
    try:
        from jarvis.core.agent_workflow import start_agent_workflow, get_workflow_manager
        
        # Start quick test
        cycle_id = start_agent_workflow("quick_test_agent", 10, 0.80)
        print(f"✅ Quick test started: {cycle_id}")
        
        # Wait for completion
        manager = get_workflow_manager()
        print("⏳ Waiting for test completion...")
        
        start_time = time.time()
        while time.time() - start_time < 60:  # Max 1 minute wait
            status = manager.get_cycle_status(cycle_id)
            if status and status['status'] == 'completed':
                print("✅ Quick test completed!")
                if status.get('compliance_achieved'):
                    print("🎯 Test passed with target compliance")
                else:
                    print("⚠️  Test completed but compliance target not met")
                break
            time.sleep(2)
        else:
            print("⏰ Test still running (check status later)")
        
        return cycle_id
    
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return None

def get_workflow_status(cycle_id=None):
    """Get workflow status for external tools"""
    try:
        from jarvis.core.agent_workflow import get_workflow_manager
        manager = get_workflow_manager()
        
        if cycle_id:
            # Get status for specific workflow
            for workflow_id, workflow_data in manager.active_workflows.items():
                if workflow_id == cycle_id:
                    return {
                        'cycle_id': cycle_id,
                        'status': 'active',
                        'cycles_completed': workflow_data.get('cycles_completed', 0),
                        'target_cycles': workflow_data.get('target_cycles', 0),
                        'compliance_target': workflow_data.get('compliance_target', 0.95),
                        'found': True
                    }
            return {'cycle_id': cycle_id, 'status': 'not_found', 'found': False}
        else:
            # Get general workflow system status
            return {
                'active_workflows': len(manager.active_workflows),
                'total_scenarios': len(manager.test_scenarios),
                'system_active': True
            }
    except Exception as e:
        return {'error': str(e), 'system_active': False}

def main():
    """Main function with command line interface"""
    parser = argparse.ArgumentParser(description="Jarvis-V0.19 Agent Workflow Launcher")
    
    parser.add_argument("--start", action="store_true", 
                       help="Start a production workflow")
    parser.add_argument("--agent-id", default="production_agent",
                       help="Agent ID for the workflow (default: production_agent)")
    parser.add_argument("--cycles", type=int, default=100,
                       help="Number of test cycles (default: 100)")
    parser.add_argument("--compliance", type=float, default=0.95,
                       help="Compliance target (default: 0.95)")
    
    parser.add_argument("--status", metavar="CYCLE_ID",
                       help="Show status of a specific workflow")
    parser.add_argument("--list-workflows", action="store_true",
                       help="List all active workflows")
    parser.add_argument("--scenarios", action="store_true",
                       help="List available test scenarios")
    parser.add_argument("--quick-test", action="store_true",
                       help="Run a quick 10-cycle test")
    
    args = parser.parse_args()
    
    if args.start:
        cycle_id = start_production_workflow(args.agent_id, args.cycles, args.compliance)
        if cycle_id:
            print(f"\n📋 Workflow {cycle_id} is running in background")
            print(f"   Check status: python agent_launcher.py --status {cycle_id}")
    
    elif args.status:
        show_workflow_status(args.status)
    
    elif args.list_workflows:
        show_workflow_status()
    
    elif args.scenarios:
        list_test_scenarios()
    
    elif args.quick_test:
        cycle_id = run_quick_test()
        if cycle_id:
            print(f"\n📋 Quick test cycle: {cycle_id}")
    
    else:
        # Interactive mode
        print("Jarvis-V0.19 Agent Workflow Launcher")
        print("=" * 40)
        print("1. Start production workflow")
        print("2. Run quick test (10 cycles)")
        print("3. Show workflow status")
        print("4. List test scenarios")
        print("5. Exit")
        
        while True:
            try:
                choice = input("\nSelect option (1-5): ").strip()
                
                if choice == "1":
                    cycles = int(input("Number of cycles (100): ") or "100")
                    compliance = float(input("Compliance target (0.95): ") or "0.95")
                    agent_id = input("Agent ID (production_agent): ") or "production_agent"
                    
                    cycle_id = start_production_workflow(agent_id, cycles, compliance)
                    if cycle_id:
                        print(f"\n✅ Workflow started: {cycle_id}")
                
                elif choice == "2":
                    cycle_id = run_quick_test()
                    if cycle_id:
                        print(f"\n✅ Quick test started: {cycle_id}")
                
                elif choice == "3":
                    cycle_id = input("Workflow ID (or press Enter for all): ").strip()
                    show_workflow_status(cycle_id if cycle_id else None)
                
                elif choice == "4":
                    list_test_scenarios()
                
                elif choice == "5":
                    print("👋 Goodbye!")
                    break
                
                else:
                    print("❌ Invalid option. Please select 1-5.")
            
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except ValueError as e:
                print(f"❌ Invalid input: {e}")
            except Exception as e:
                print(f"❌ Error: {e}")

if __name__ == "__main__":
    main()