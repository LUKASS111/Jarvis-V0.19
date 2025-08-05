#!/usr/bin/env python3
"""
Simple validation script for the new architecture components
"""

import os
import sys
import traceback

# Add project root to path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

def test_plugin_system():
    """Test plugin system functionality"""
    try:
        from jarvis.core.plugin_system import PluginManager, PluginInterface, PluginContext
        
        print("✓ Plugin system imports successful")
        
        # Create basic plugin manager
        manager = PluginManager([])
        context = PluginContext(config={"test": True})
        manager.set_context(context)
        
        print("✓ Plugin manager creation and context setting successful")
        return True
    except Exception as e:
        print(f"✗ Plugin system test failed: {e}")
        traceback.print_exc()
        return False

def test_llm_system():
    """Test LLM abstraction system"""
    try:
        from jarvis.core.llm import LLMRouter, LLMProvider, CompletionRequest, Message
        
        print("✓ LLM system imports successful")
        
        # Create basic router
        router = LLMRouter()
        available_models = router.get_available_models()
        
        print("✓ LLM router creation successful")
        return True
    except Exception as e:
        print(f"✗ LLM system test failed: {e}")
        traceback.print_exc()
        return False

def test_config_system():
    """Test configuration management system"""
    try:
        from jarvis.core.config import ConfigManager, get_config_manager
        
        print("✓ Configuration system imports successful")
        
        # Create config manager
        config_manager = get_config_manager()
        config_manager.set("test.key", "test_value")
        value = config_manager.get("test.key")
        
        assert value == "test_value", f"Expected 'test_value', got '{value}'"
        
        print("✓ Configuration system basic operations successful")
        return True
    except Exception as e:
        print(f"✗ Configuration system test failed: {e}")
        traceback.print_exc()
        return False

def test_error_system():
    """Test error handling system"""
    try:
        from jarvis.core.errors import ErrorHandler, JarvisException, ErrorSeverity, ErrorCategory
        
        print("✓ Error handling system imports successful")
        
        # Create error handler
        error_handler = ErrorHandler()
        error_report = error_handler.log_error("Test error", ErrorSeverity.LOW, ErrorCategory.SYSTEM)
        
        assert error_report is not None, "Error report should not be None"
        assert error_report.message == "Test error", f"Expected 'Test error', got '{error_report.message}'"
        
        print("✓ Error handling system basic operations successful")
        return True
    except Exception as e:
        print(f"✗ Error handling system test failed: {e}")
        traceback.print_exc()
        return False

def main():
    """Run all architecture validation tests"""
    print("=== Pre-Audit Architecture Validation ===\n")
    
    tests = [
        ("Plugin System", test_plugin_system),
        ("LLM Abstraction", test_llm_system),
        ("Configuration Management", test_config_system),
        ("Error Handling", test_error_system)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        print(f"Testing {test_name}...")
        if test_func():
            passed += 1
            print(f"✅ {test_name} - PASSED\n")
        else:
            print(f"❌ {test_name} - FAILED\n")
    
    print(f"=== Results: {passed}/{total} tests passed ===")
    
    if passed == total:
        print("🎉 All architecture components validated successfully!")
        return True
    else:
        print("⚠️  Some architecture components need attention.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)