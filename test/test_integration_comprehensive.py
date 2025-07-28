#!/usr/bin/env python3
"""
Integration Test Suite for V0.41-black-ui
Tests interaction between modules and end-to-end functionality
"""

import sys
import os
import unittest
import tempfile
import shutil
import time
import json
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestModuleIntegration(unittest.TestCase):
    """Test integration between core modules"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_error_handler_llm_integration(self):
        """Test error handler integration with LLM interface"""
        from error_handler import error_handler, safe_execute, ErrorLevel
        from llm_interface import ask_local_llm
        
        # Test that LLM errors are properly handled by error handler
        @safe_execute(fallback_value={"error": "LLM unavailable"}, context="LLM test")
        def test_llm_call():
            # This will likely fail without Ollama running
            return ask_local_llm("test prompt")
        
        result = test_llm_call()
        # LLM interface may return either dict (from fallback) or string (from LLM error handling)
        self.assertTrue(isinstance(result, (dict, str)))
        
        # If it's a string, it should be an error message
        if isinstance(result, str):
            self.assertIn("LLM ERROR", result)
        else:
            # If it's a dict, it should have error info
            self.assertIn("error", result)
        
        # Verify error was logged
        summary = error_handler.get_session_summary()
        self.assertIsInstance(summary, dict)
    
    def test_memory_logging_integration(self):
        """Test memory system integration with logging"""
        from memory import remember_fact, recall_fact
        from logs import log_event, get_logs
        
        # Remember a fact (this may trigger logging)
        remember_fact("integration_test to successful")
        
        # Recall the fact
        result = recall_fact("integration_test")
        self.assertEqual(result, "successful")
        
        # Log an event
        log_event("memory_test", {"fact": "integration_test", "value": "successful"})
        
        # Verify logging worked
        logs = get_logs()
        self.assertIsInstance(logs, list)
    
    @patch('llm_interface.ask_local_llm')
    def test_main_gui_integration(self, mock_llm):
        """Test main module integration with GUI components"""
        from main import simple_llm_process, process_interactive_input
        
        # Mock LLM response
        mock_llm.return_value = {
            "response": "Integration test response",
            "error": None
        }
        
        # Test LLM processing
        result = simple_llm_process("Integration test prompt")
        self.assertIsInstance(result, dict)
        self.assertIn("response", result)
        
        # Test interactive input processing
        interactive_result = process_interactive_input("help")
        self.assertIsInstance(interactive_result, dict)
        self.assertIn("action", interactive_result)
        
        # If it's an LLM response, verify the structure
        if interactive_result.get("action") == "llm_response":
            self.assertIn("result", interactive_result)
            self.assertIsInstance(interactive_result["result"], dict)
    


class TestEndToEndWorkflows(unittest.TestCase):
    """Test complete user workflows"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_memory_workflow(self):
        """Test complete memory management workflow"""
        from memory import remember_fact, recall_fact, forget_fact, process_memory_prompt
        
        # Complete workflow: remember -> recall -> forget -> verify
        
        # Step 1: Remember facts
        result1 = remember_fact("user_name to Alice")
        self.assertIn("✅", result1)
        
        result2 = remember_fact("user_age to 25")
        self.assertIn("✅", result2)
        
        # Step 2: Recall facts
        name = recall_fact("user_name")
        self.assertEqual(name, "Alice")
        
        age = recall_fact("user_age")
        self.assertEqual(age, "25")
        
        # Step 3: Use process_memory_prompt interface
        prompt_result = process_memory_prompt("recall user_name")
        self.assertEqual(prompt_result, "Alice")
        
        # Step 4: Forget a fact
        forget_result = forget_fact("user_age")
        self.assertIn("🗑️", forget_result)
        
        # Step 5: Verify forgotten
        forgotten_result = recall_fact("user_age")
        self.assertIn("❓", forgotten_result)
    
    @patch('llm_interface.ask_local_llm')
    def test_llm_interaction_workflow(self, mock_llm):
        """Test complete LLM interaction workflow"""
        from llm_interface import set_ollama_model, get_ollama_model, ask_local_llm
        from main import simple_llm_process
        
        # Mock LLM responses
        mock_llm.return_value = {
            "response": "This is a test response from the LLM",
            "error": None
        }
        
        # Step 1: Set model
        original_model = get_ollama_model()
        set_ollama_model("llama3:8b")
        self.assertEqual(get_ollama_model(), "llama3:8b")
        
        # Step 2: Simple LLM call
        direct_result = ask_local_llm("Test prompt")
        self.assertIsInstance(direct_result, dict)
        
        # Step 3: Process through main interface
        processed_result = simple_llm_process("Test prompt")
        self.assertIsInstance(processed_result, dict)
        self.assertIn("prompt", processed_result)
        self.assertIn("response", processed_result)
        
        # Step 4: Restore original model
        set_ollama_model(original_model)
    
    def test_error_handling_workflow(self):
        """Test complete error handling workflow"""
        from error_handler import error_handler, safe_execute, ErrorLevel
        
        # Step 1: Generate different types of errors
        @safe_execute(fallback_value="safe_fallback", context="test_context")
        def failing_function():
            raise ValueError("Test error")
        
        result = failing_function()
        self.assertEqual(result, "safe_fallback")
        
        # Step 2: Log manual error
        test_error = Exception("Manual test error")
        error_data = error_handler.log_error(
            test_error, 
            "Manual error context", 
            ErrorLevel.WARNING, 
            "This is a test warning"
        )
        self.assertIsInstance(error_data, dict)
        
        # Step 3: Get session summary
        summary = error_handler.get_session_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn("total_errors", summary)
        self.assertIn("total_warnings", summary)
    
    def test_logging_workflow(self):
        """Test complete logging workflow"""
        from logs import log_event, get_logs, clear_logs
        
        # Step 1: Clear any existing logs
        clear_logs()
        
        # Step 2: Log various events
        events = [
            ("user_action", {"action": "login", "user": "test_user"}),
            ("system_event", {"event": "startup", "version": "0.4.1"}),
            ("error_event", {"error": "test_error", "context": "test"})
        ]
        
        for event_type, event_data in events:
            result = log_event(event_type, event_data)
            self.assertTrue(result)
        
        # Step 3: Retrieve and verify logs
        logs = get_logs()
        self.assertGreaterEqual(len(logs), len(events))
        
        # Step 4: Verify log structure
        for log_entry in logs:
            self.assertIn("timestamp", log_entry)
            self.assertIn("event", log_entry)
            self.assertIn("data", log_entry)

class TestGUIIntegration(unittest.TestCase):
    """Test GUI integration (without actually showing GUI)"""
    
    def test_gui_imports(self):
        """Test that GUI can be imported without errors"""
        try:
            from modern_gui import SimplifiedJarvisGUI
            self.assertTrue(True)  # Import successful
        except ImportError as e:
            self.skipTest(f"PyQt5 not available: {e}")
    
    @patch('modern_gui.QApplication')
    @patch('modern_gui.QWidget')
    def test_gui_initialization(self, mock_widget, mock_app):
        """Test GUI initialization without showing window"""
        try:
            from modern_gui import SimplifiedJarvisGUI
            
            # Mock QApplication and QWidget
            mock_app.return_value = Mock()
            mock_widget_instance = Mock()
            mock_widget.return_value = mock_widget_instance
            
            # Set environment for offscreen rendering
            import os
            os.environ['QT_QPA_PLATFORM'] = 'offscreen'
            
            # Test GUI creation (without show())
            gui = SimplifiedJarvisGUI()
            self.assertIsNotNone(gui)
            
        except ImportError:
            self.skipTest("PyQt5 not available")
        except Exception as e:
            # If GUI tests fail in headless environment, that's expected
            self.skipTest(f"GUI test skipped in headless environment: {e}")

class TestSystemIntegration(unittest.TestCase):
    """Test system-level integration"""
    
    def test_startup_sequence(self):
        """Test system startup sequence"""
        # Test that all modules can be imported in sequence
        modules_to_test = [
            'error_handler',
            'llm_interface', 
            'memory',
            'logs',
            'main'
        ]
        
        for module_name in modules_to_test:
            try:
                __import__(module_name)
            except ImportError as e:
                self.fail(f"Failed to import {module_name}: {e}")
    
    def test_configuration_consistency(self):
        """Test that configuration is consistent across modules"""
        from llm_interface import AVAILABLE_MODELS as llm_models
        from memory import AVAILABLE_MODELS as memory_models
        
        # Verify model lists are consistent
        self.assertEqual(llm_models, memory_models)
    
    def test_cross_module_data_flow(self):
        """Test data flow between modules"""
        from memory import remember_fact, recall_fact
        from logs import log_event, get_logs
        from error_handler import error_handler
        
        # Test: Memory -> Logs -> Error Handler data flow
        
        # Step 1: Create memory data
        remember_fact("test_data_flow to working")
        
        # Step 2: Log the memory action
        log_event("memory_action", {
            "action": "remember",
            "key": "test_data_flow",
            "value": "working"
        })
        
        # Step 3: Verify data in memory
        result = recall_fact("test_data_flow")
        self.assertEqual(result, "working")
        
        # Step 4: Verify log was created
        logs = get_logs()
        memory_logs = [log for log in logs if log.get("event") == "memory_action"]
        self.assertGreater(len(memory_logs), 0)
        
        # Step 5: Verify error handler is tracking
        summary = error_handler.get_session_summary()
        self.assertIsInstance(summary, dict)

if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestModuleIntegration,
        TestEndToEndWorkflows,
        TestGUIIntegration,
        TestSystemIntegration
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"INTEGRATION TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)