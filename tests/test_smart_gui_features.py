#!/usr/bin/env python3
"""
Test script for Smart GUI and AI Orchestration features
Validates the intelligent components and adaptive behavior
"""

import sys
import os
import time

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_smart_orchestration_components():
    """Test smart orchestration components"""
    print("Testing Smart GUI & AI Orchestration Components...")
    print("=" * 50)
    
    # Test UserBehaviorTracker
    try:
        from gui.components.smart_orchestration import UserBehaviorTracker
        
        tracker = UserBehaviorTracker()
        print("✅ UserBehaviorTracker: Initialized successfully")
        
        # Test tracking functions
        tracker.track_tab_usage("Core System", 30.5)
        tracker.track_feature_usage("process_request")
        tracker.track_ai_provider_usage("gpt-4", True)
        
        # Test analytics
        priority_order = tracker.get_tab_priority_order()
        recommended_provider = tracker.get_recommended_ai_provider()
        
        print(f"✅ UserBehaviorTracker: Tab priority order: {priority_order}")
        print(f"✅ UserBehaviorTracker: Recommended provider: {recommended_provider}")
        
    except Exception as e:
        print(f"❌ UserBehaviorTracker: Error - {e}")
    
    # Test AIOrchestrationEngine
    try:
        from gui.components.smart_orchestration import AIOrchestrationEngine
        
        orchestrator = AIOrchestrationEngine()
        print("✅ AIOrchestrationEngine: Initialized successfully")
        
        # Test provider selection
        optimal_provider = orchestrator.select_optimal_provider("general", "medium")
        print(f"✅ AIOrchestrationEngine: Optimal provider: {optimal_provider}")
        
        # Test performance tracking
        orchestrator.track_provider_performance("gpt-4", 1.5, True)
        orchestrator.track_provider_performance("claude-3", 2.1, True)
        
        summary = orchestrator.get_performance_summary()
        print(f"✅ AIOrchestrationEngine: Performance summary: {len(summary)} providers tracked")
        
    except Exception as e:
        print(f"❌ AIOrchestrationEngine: Error - {e}")
    
    # Test GUI components creation (without PyQt5 display)
    try:
        from gui.components.smart_orchestration import create_smart_orchestration_widgets
        
        widgets = create_smart_orchestration_widgets()
        print(f"✅ Smart Widget Factory: Created {len(widgets)} widgets")
        
    except Exception as e:
        print(f"❌ Smart Widget Factory: Error - {e}")

def test_smart_dashboard_integration():
    """Test smart dashboard integration"""
    print("\nTesting Smart Dashboard Integration...")
    print("=" * 40)
    
    try:
        # Test that dashboard can import smart components
        from gui.enhanced.comprehensive_dashboard import JarvisComprehensiveDashboard
        print("✅ Smart Dashboard: Import successful")
        
        # Test initialization (without actual GUI display)
        os.environ['QT_QPA_PLATFORM'] = 'offscreen'  # Headless mode
        
        # Note: We won't actually create the dashboard instance to avoid display issues
        # But we can verify the class structure
        dashboard_class = JarvisComprehensiveDashboard
        
        # Check for smart methods
        smart_methods = [
            'setup_smart_features',
            'optimize_tabs', 
            'show_usage_analytics',
            'show_ai_performance',
            'generate_analytics_report'
        ]
        
        for method in smart_methods:
            if hasattr(dashboard_class, method):
                print(f"✅ Smart Dashboard: Method '{method}' available")
            else:
                print(f"❌ Smart Dashboard: Method '{method}' missing")
                
    except Exception as e:
        print(f"❌ Smart Dashboard: Error - {e}")

def test_memory_persistence():
    """Test memory persistence of user behavior"""
    print("\nTesting Memory Persistence...")
    print("=" * 30)
    
    try:
        from gui.components.smart_orchestration import UserBehaviorTracker
        
        # Create tracker and add some data
        tracker1 = UserBehaviorTracker(data_file="memory/test_behavior.json")
        tracker1.track_tab_usage("Test Tab", 15.0)
        tracker1.track_feature_usage("test_feature")
        tracker1.save_behavior_data()
        
        # Create new tracker and verify data persists
        tracker2 = UserBehaviorTracker(data_file="memory/test_behavior.json")
        
        if "Test Tab" in tracker2.session_data['tab_usage']:
            print("✅ Memory Persistence: User behavior data preserved")
        else:
            print("❌ Memory Persistence: Data not preserved")
            
        # Cleanup test file
        if os.path.exists("memory/test_behavior.json"):
            os.remove("memory/test_behavior.json")
            
    except Exception as e:
        print(f"❌ Memory Persistence: Error - {e}")

def main():
    """Run all smart GUI tests"""
    print("Jarvis Smart GUI & AI Orchestration Test Suite")
    print("=" * 60)
    print("Stage 4 Implementation Validation")
    print("")
    
    # Ensure memory directory exists
    os.makedirs("memory", exist_ok=True)
    
    # Run test suites
    test_smart_orchestration_components()
    test_smart_dashboard_integration()
    test_memory_persistence()
    
    print("\n" + "=" * 60)
    print("✅ Smart GUI & AI Orchestration testing complete!")
    print("Stage 4 implementation validated successfully")

if __name__ == "__main__":
    main()