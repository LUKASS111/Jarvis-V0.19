#!/usr/bin/env python3
"""
Simplified test suite for the modernized AutoGPT system
Tests core functionality without deprecated components
"""

import sys
import os
import time
import json
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def test_core_imports():
    """Test that core modules can be imported"""
    try:
        from jarvis.core.error_handler import ErrorHandler
        import jarvis.llm.llm_interface as llm_interface  
        import jarvis.memory.memory as memory
        import jarvis.utils.logs as logs
        # Don't try to import GUI class as it requires PyQt5
        print("✅ Core imports: PASS")
        return True
    except ImportError as e:
        print(f"[FAIL] Core imports: FAIL - {e}")
        return False

def test_error_handler():
    """Test error handling functionality"""
    try:
        from jarvis.core.error_handler import ErrorHandler, ErrorLevel, log_error
        
        # Test logging with correct signature
        log_error(Exception("Test error"), "Test context", ErrorLevel.INFO)
        
        # Test creating an error handler instance
        handler = ErrorHandler()
        summary = handler.get_session_summary()
        assert isinstance(summary, dict)
        
        print("✅ Error handler: PASS")
        return True
    except Exception as e:
        print(f"[FAIL] Error handler: FAIL - {e}")
        return False

def test_llm_interface():
    """Test LLM interface availability"""
    try:
        from jarvis.llm.llm_interface import get_available_models, get_ollama_model
        
        # Test model functions
        models = get_available_models()
        current_model = get_ollama_model()
        
        print(f"✅ LLM interface: PASS (Current model: {current_model})")
        return True
    except Exception as e:
        print(f"[FAIL] LLM interface: FAIL - {e}")
        return False

def test_memory_system():
    """Test memory system"""
    try:
        from jarvis.memory.memory import process_memory_prompt
        
        # Test memory processing
        result = process_memory_prompt("test prompt")
        
        print("✅ Memory system: PASS")
        return True
    except Exception as e:
        print(f"[FAIL] Memory system: FAIL - {e}")
        return False

def test_logging_system():
    """Test logging system"""
    try:
        from jarvis.utils.logs import log_event
        
        # Test event logging
        log_event("test_event", {"test": "data"})
        
        print("✅ Logging system: PASS")
        return True
    except Exception as e:
        print(f"[FAIL] Logging system: FAIL - {e}")
        return False

def test_gui_imports():
    """Test GUI module imports"""
    try:
        from gui.modern_gui import SimplifiedJarvisGUI
        
        print("✅ GUI imports: PASS")
        return True
    except Exception as e:
        print(f"[FAIL] GUI imports: FAIL - {e}")
        return False

def test_main_processing():
    """Test main processing function"""
    try:
        from jarvis.core.main import simple_llm_process, simple_log_to_file
        
        # Test simple processing (will fail without LLM but should not crash)
        result = simple_llm_process("test prompt")
        assert isinstance(result, dict)
        assert "prompt" in result
        assert "response" in result
        
        # Test logging
        simple_log_to_file({"test": "data"})
        
        print("✅ Main processing: PASS")
        return True
    except Exception as e:
        print(f"[FAIL] Main processing: FAIL - {e}")
        return False

def run_all_tests():
    """Run all test cases"""
    print("[TEST] SIMPLIFIED SYSTEM TEST SUITE")
    print("=" * 50)
    print(f"[TIME1] Started at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    test_functions = [
        test_core_imports,
        test_error_handler,
        test_llm_interface,
        test_memory_system,
        test_logging_system,
        test_gui_imports,
        test_main_processing
    ]
    
    results = []
    total_start_time = time.time()
    
    for test_func in test_functions:
        print(f"[SEARCH] Running {test_func.__name__}...")
        start_time = time.time()
        
        try:
            success = test_func()
            execution_time = time.time() - start_time
            results.append({
                'name': test_func.__name__,
                'success': success,
                'execution_time': execution_time
            })
        except Exception as e:
            execution_time = time.time() - start_time
            results.append({
                'name': test_func.__name__,
                'success': False,
                'execution_time': execution_time,
                'error': str(e)
            })
            print(f"[BOOM] {test_func.__name__}: ERROR - {str(e)}")
        
        print()
    
    # Generate summary
    total_execution_time = time.time() - total_start_time
    passed = sum(1 for r in results if r['success'])
    total = len(results)
    success_rate = (passed / total * 100) if total > 0 else 0
    
    print("[CHART] TEST RESULTS SUMMARY")
    print("=" * 50)
    
    for result in results:
        status = "✅ PASS" if result['success'] else "[FAIL] FAIL"
        print(f"   {status} {result['name']} ({result['execution_time']:.2f}s)")
    
    print(f"\n[TARGET] OVERALL SUMMARY:")
    print(f"   Total Tests: {total}")
    print(f"   Passed: {passed}")
    print(f"   Failed: {total - passed}")
    print(f"   Success Rate: {success_rate:.1f}%")
    print(f"   Total Execution Time: {total_execution_time:.2f}s")
    
    if success_rate >= 90:
        status = "[GREEN] EXCELLENT"
    elif success_rate >= 80:
        status = "[YELLOW] GOOD"
    elif success_rate >= 60:
        status = "[ORANGE] NEEDS IMPROVEMENT"
    else:
        status = "[RED] CRITICAL ISSUES"
    
    print(f"   System Status: {status}")
    print(f"\n[TIME1] Completed at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    
    return success_rate >= 80

if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)