#!/usr/bin/env python3
"""
Comprehensive test script for the new data archiving and verification system.
"""

import sys
import os
import time
import json
from datetime import datetime

# Add the parent directory to Python path (to access jarvis modules)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_data_archiving():
    """Test basic data archiving functionality"""
    print("\n=== Testing Data Archiving System ===")
    
    try:
        from jarvis.core.data_archiver import archive_input, archive_output, get_archive_stats
        
        # Test input archiving
        input_id = archive_input(
            content="Test user input: What is machine learning?",
            source="test_system",
            operation="user_query_test",
            metadata={"test_run": "initial", "timestamp": datetime.now().isoformat()}
        )
        print(f"[OK] Input archived with ID: {input_id}")
        
        # Test output archiving
        output_id = archive_output(
            content="Machine learning is a subset of artificial intelligence...",
            source="test_llm",
            operation="ai_response_test",
            metadata={"input_id": input_id, "model": "test_model"}
        )
        print(f"[OK] Output archived with ID: {output_id}")
        
        # Check statistics
        stats = get_archive_stats()
        print(f"[OK] Archive statistics: {stats['total_entries']} total entries")
        print(f"[OK] Pending verification: {stats['pending_verification']}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Data archiving test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_data_verification():
    """Test data verification system"""
    print("\n=== Testing Data Verification System ===")
    
    try:
        from jarvis.core.data_verifier import verify_data_immediately, get_verifier
        
        # Test immediate verification
        result = verify_data_immediately(
            content="The Earth is approximately spherical in shape",
            data_type="factual",
            source="test_verification",
            operation="fact_check_test"
        )
        
        print(f"[OK] Verification completed")
        print(f"[OK] Is verified: {result.is_verified}")
        print(f"[OK] Confidence score: {result.confidence_score:.2f}")
        print(f"[OK] Verification type: {result.verification_type}")
        print(f"[OK] Reasoning: {result.reasoning[:100]}...")
        
        # Test verifier instance
        verifier = get_verifier()
        print(f"[OK] Verifier instance created: {type(verifier).__name__}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Data verification test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_backup_system():
    """Test backup and recovery system"""
    print("\n=== Testing Backup & Recovery System ===")
    
    try:
        from jarvis.core.backup_recovery import create_backup, list_available_backups, get_backup_stats
        
        # Create a test backup
        backup_info = create_backup(
            description="Test backup for system validation"
        )
        
        print(f"[OK] Backup created: {backup_info.backup_id}")
        print(f"[OK] Backup size: {backup_info.size_bytes} bytes")
        print(f"[OK] Backup path: {backup_info.backup_path}")
        
        # List backups
        backups = list_available_backups()
        print(f"[OK] Total backups available: {len(backups)}")
        
        # Get statistics
        stats = get_backup_stats()
        print(f"[OK] Backup statistics: {stats['total_backups']} backups")
        print(f"[OK] Total backup size: {stats['total_size_bytes']} bytes")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Backup system test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_agent_workflow():
    """Test agent workflow system"""
    print("\n=== Testing Agent Workflow System ===")
    
    try:
        from jarvis.core.agent_workflow import get_workflow_manager, start_agent_workflow
        
        # Get workflow manager
        manager = get_workflow_manager()
        print(f"[OK] Workflow manager created: {type(manager).__name__}")
        
        # Register a test agent
        manager.register_agent(
            "test_agent_validation",
            capabilities=["testing", "validation"],
            config={"timeout": 15, "test_mode": True}
        )
        print(f"[OK] Test agent registered")
        
        # Start a short workflow (5 cycles for testing)
        cycle_id = start_agent_workflow("test_agent_validation", 5, 0.80)
        print(f"[OK] Workflow started: {cycle_id}")
        
        # Wait a moment for some cycles to complete
        print("[INFO] Waiting for workflow cycles to execute...")
        time.sleep(10)
        
        # Check status
        status = manager.get_cycle_status(cycle_id)
        if status:
            print(f"[OK] Workflow status: {status['status']}")
        else:
            print("[WARN] Workflow status not available")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] Agent workflow test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_system_integration():
    """Test system integration"""
    print("\n=== Testing System Integration ===")
    
    try:
        from jarvis.core import (
            archive_input, verify_data_immediately, create_backup,
            get_archive_stats, start_agent_workflow
        )
        
        # Test integrated workflow
        print("[INFO] Testing integrated data flow...")
        
        # 1. Archive some data
        archive_id = archive_input(
            content="Integration test: System working correctly",
            source="integration_test",
            operation="system_validation"
        )
        print(f"[OK] Integration test data archived: {archive_id}")
        
        # 2. Verify the data
        result = verify_data_immediately(
            content="Integration test: System working correctly",
            data_type="system",
            source="integration_test",
            operation="verification_test"
        )
        print(f"[OK] Integration verification: {result.is_verified} (confidence: {result.confidence_score:.2f})")
        
        # 3. Create backup
        backup = create_backup("Integration test backup")
        print(f"[OK] Integration backup created: {backup.backup_id}")
        
        # 4. Check overall system status
        stats = get_archive_stats()
        print(f"[OK] System status - Total entries: {stats['total_entries']}")
        print(f"[OK] System status - Avg verification score: {stats['average_verification_score']:.2f}")
        
        return True
        
    except Exception as e:
        print(f"[FAIL] System integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False

def run_comprehensive_tests():
    """Run all comprehensive tests"""
    print("Starting Comprehensive Data Archiving and Verification System Tests")
    print("=" * 70)
    
    test_results = []
    
    # Run individual test suites
    test_results.append(("Data Archiving", test_data_archiving()))
    test_results.append(("Data Verification", test_data_verification()))
    test_results.append(("Backup System", test_backup_system()))
    test_results.append(("Agent Workflow", test_agent_workflow()))
    test_results.append(("System Integration", test_system_integration()))
    
    # Print summary
    print("\n" + "=" * 70)
    print("TEST SUMMARY")
    print("=" * 70)
    
    passed = 0
    failed = 0
    
    for test_name, result in test_results:
        status = "[PASS]" if result else "[FAIL]"
        print(f"{status} {test_name}")
        if result:
            passed += 1
        else:
            failed += 1
    
    print("-" * 70)
    print(f"Total Tests: {len(test_results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Success Rate: {(passed/len(test_results)*100):.1f}%")
    
    if failed == 0:
        print("\n[SUCCESS] All tests passed! System ready for production use.")
    else:
        print(f"\n[WARNING] {failed} test(s) failed. Please review errors above.")
    
    return failed == 0

if __name__ == "__main__":
    success = run_comprehensive_tests()
    sys.exit(0 if success else 1)