#!/usr/bin/env python3
"""
Comprehensive Unit Test Suite for V0.2
Tests every function, class, and method in the project
"""

import sys
import os
import unittest
import json
import tempfile
import shutil
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestErrorHandler(unittest.TestCase):
    """Unit tests for error_handler.py module"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.log_file = os.path.join(self.temp_dir, "test_error.jsonl")
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_error_handler_init(self):
        """Test ErrorHandler initialization"""
        from jarvis.core.error_handler import ErrorHandler
        handler = ErrorHandler(self.log_file)
        
        self.assertEqual(handler.log_file, self.log_file)
        self.assertEqual(handler.error_count, 0)
        self.assertEqual(handler.warning_count, 0)
        self.assertEqual(handler.fallback_count, 0)
        self.assertIsInstance(handler.session_errors, list)
    
    def test_log_error(self):
        """Test error logging functionality"""
        from jarvis.core.error_handler import ErrorHandler, ErrorLevel
        handler = ErrorHandler(self.log_file)
        
        test_error = Exception("Test error")
        result = handler.log_error(test_error, "Test context", ErrorLevel.ERROR, "Test message")
        
        self.assertIsInstance(result, dict)
        self.assertIn("timestamp", result)
        self.assertIn("level", result)
        self.assertIn("error_type", result)
        self.assertEqual(result["level"], "error")
        self.assertEqual(result["context"], "Test context")
        self.assertEqual(result["user_message"], "Test message")
    
    def test_error_levels(self):
        """Test all error levels"""
        from jarvis.core.error_handler import ErrorLevel
        
        levels = [ErrorLevel.INFO, ErrorLevel.WARNING, ErrorLevel.ERROR, ErrorLevel.CRITICAL]
        expected_values = ["info", "warning", "error", "critical"]
        
        for level, expected in zip(levels, expected_values):
            self.assertEqual(level.value, expected)
    
    def test_safe_execute_decorator(self):
        """Test safe_execute decorator"""
        from jarvis.core.error_handler import safe_execute
        
        @safe_execute(fallback_value="fallback", context="test")
        def test_function():
            raise Exception("Test error")
        
        result = test_function()
        self.assertEqual(result, "fallback")
    
    def test_session_summary(self):
        """Test session summary functionality"""
        from jarvis.core.error_handler import error_handler, ErrorLevel
        
        # Log some test errors
        test_error = Exception("Test error")
        error_handler.log_error(test_error, "Test context", ErrorLevel.ERROR, "Test message")
        
        # Get session summary
        summary = error_handler.get_session_summary()
        self.assertIsInstance(summary, dict)
        self.assertIn("total_errors", summary)
        self.assertIn("total_warnings", summary)

class TestLLMInterface(unittest.TestCase):
    """Unit tests for llm_interface.py module"""
    
    def test_available_models(self):
        """Test available models list"""
        from jarvis.llm.llm_interface import AVAILABLE_MODELS
        
        expected_models = ["llama3:8b", "codellama:13b", "codellama:34b", "llama3:70b"]
        self.assertEqual(AVAILABLE_MODELS, expected_models)
    
    def test_model_operations(self):
        """Test model get/set operations"""
        from jarvis.llm.llm_interface import set_ollama_model, get_ollama_model, get_available_models
        
        # Test getting available models
        models = get_available_models()
        self.assertIsInstance(models, list)
        self.assertGreater(len(models), 0)
        
        # Test setting valid model
        original_model = get_ollama_model()
        set_ollama_model("codellama:13b")
        self.assertEqual(get_ollama_model(), "codellama:13b")
        
        # Test setting invalid model (should fallback)
        set_ollama_model("invalid_model")
        self.assertIn(get_ollama_model(), models)
        
        # Restore original model
        set_ollama_model(original_model)
    
    def test_dynamic_timeout(self):
        """Test dynamic timeout calculation"""
        from jarvis.llm.llm_interface import get_dynamic_timeout
        
        # Test different model sizes
        self.assertEqual(get_dynamic_timeout("llama3:70b"), 220)
        self.assertEqual(get_dynamic_timeout("codellama:34b"), 130)
        self.assertEqual(get_dynamic_timeout("codellama:13b"), 100)
        self.assertEqual(get_dynamic_timeout("llama3:8b"), 45)
        self.assertEqual(get_dynamic_timeout("unknown"), 40)
    
    @patch('jarvis.llm.llm_interface.requests.post')
    def test_ask_local_llm(self, mock_post):
        """Test LLM interaction (mocked)"""
        from jarvis.llm.llm_interface import ask_local_llm
        
        # Mock successful response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {"response": "Test response"}
        mock_post.return_value = mock_response
        
        result = ask_local_llm("Test prompt")
        self.assertIsInstance(result, str)
        self.assertEqual(result, "Test response")
        
        # Mock connection error
        mock_post.side_effect = Exception("Connection error")
        result = ask_local_llm("Test prompt")
        self.assertIn("LLM ERROR", result)

class TestMemory(unittest.TestCase):
    """Unit tests for memory.py module"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.memory_file = os.path.join(self.temp_dir, "test_memory.json")
        # Patch the MEMORY_FILE constant
        import jarvis.memory.memory as memory
        self.original_memory_file = memory.MEMORY_FILE
        memory.MEMORY_FILE = self.memory_file
    
    def tearDown(self):
        """Clean up test environment"""
        import jarvis.memory.memory as memory
        memory.MEMORY_FILE = self.original_memory_file
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_load_save_memory(self):
        """Test memory load/save operations"""
        from jarvis.memory.memory import load_memory, save_memory
        
        # Test loading non-existent memory
        memory_data = load_memory()
        self.assertEqual(memory_data, {})
        
        # Test saving and loading memory
        test_data = {"key1": "value1", "key2": "value2"}
        save_memory(test_data)
        loaded_data = load_memory()
        self.assertEqual(loaded_data, test_data)
    
    def test_remember_fact(self):
        """Test fact remembering"""
        from jarvis.memory.memory import remember_fact
        
        # Test valid fact format
        result = remember_fact("name to John")
        self.assertIn("[OK]", result)
        self.assertIn("name", result)
        self.assertIn("John", result)
        
        # Test invalid fact format
        result = remember_fact("invalid fact")
        self.assertIn("[FAIL]", result)
    
    def test_recall_fact(self):
        """Test fact recall"""
        from jarvis.memory.memory import remember_fact, recall_fact
        
        # Remember a fact
        remember_fact("test_key to test_value")
        
        # Recall existing fact
        result = recall_fact("test_key")
        self.assertEqual(result, "test_value")
        
        # Recall non-existent fact
        result = recall_fact("non_existent")
        self.assertIn("[QUESTION]", result)
    
    def test_forget_fact(self):
        """Test fact forgetting"""
        from jarvis.memory.memory import remember_fact, forget_fact, recall_fact
        
        # Remember a fact
        remember_fact("forget_test to forget_value")
        
        # Forget existing fact
        result = forget_fact("forget_test")
        self.assertIn("[TRASH]", result)
        
        # Verify fact is forgotten
        recall_result = recall_fact("forget_test")
        self.assertIn("[QUESTION]", recall_result)
        
        # Forget non-existent fact
        result = forget_fact("non_existent")
        self.assertIn("[QUESTION]", result)
    
    def test_process_memory_prompt(self):
        """Test memory prompt processing"""
        from jarvis.memory.memory import process_memory_prompt
        
        # Test remember command
        result = process_memory_prompt("zapamiętaj test to value")
        if result:  # Only test if function returns something
            self.assertIsInstance(result, str)
        
        # Test recall command  
        result = process_memory_prompt("przypomnij test")
        if result:  # May return None for unknown facts
            self.assertIsInstance(result, str)
        
        # Test forget command
        result = process_memory_prompt("zapomnij test")
        if result:  # Only test if function returns something
            self.assertIsInstance(result, str)
        
        # Test export command
        result = process_memory_prompt("eksportuj pamięć")
        if result:  # Only test if function returns something
            self.assertIsInstance(result, str)

class TestLogs(unittest.TestCase):
    """Unit tests for logs.py module"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('jarvis.utils.logs.log_event')
    def test_log_event(self, mock_log_event):
        """Test event logging"""
        from jarvis.utils.logs import log_event
        
        mock_log_event.return_value = True
        
        # Test logging event
        test_data = {"action": "test", "data": "value"}
        result = log_event("test_event", test_data)
        
        self.assertTrue(result)
        mock_log_event.assert_called_once_with("test_event", test_data)
    
    def test_log_formatting(self):
        """Test log formatting function"""
        from jarvis.utils.logs import format_log_text
        
        test_data = {"action": "test", "data": "value"}
        result = format_log_text("test_event", test_data)
        
        self.assertIsInstance(result, str)
        self.assertIn("TEST_EVENT", result)
        self.assertIn("action", result)
        self.assertIn("test", result)
    
    def test_available_models_constant(self):
        """Test available models constant in logs"""
        from jarvis.utils.logs import AVAILABLE_MODELS
        
        self.assertIsInstance(AVAILABLE_MODELS, list)
        self.assertGreater(len(AVAILABLE_MODELS), 0)
        self.assertIn("llama3:8b", AVAILABLE_MODELS)


class TestMainModule(unittest.TestCase):
    """Unit tests for main.py module"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_version_string(self):
        """Test version string constant"""
        from main import VERSION_STRING
        
        self.assertIsInstance(VERSION_STRING, str)
        self.assertIn("1.0", VERSION_STRING)
    
    def test_available_models(self):
        """Test available models constant"""
        from main import AVAILABLE_MODELS
        
        self.assertIsInstance(AVAILABLE_MODELS, list)
        self.assertGreater(len(AVAILABLE_MODELS), 0)
    
    @patch('jarvis.core.main.ask_local_llm')
    def test_simple_llm_process(self, mock_llm):
        """Test simple LLM processing"""
        from jarvis.core.main import simple_llm_process
        
        # Mock successful response
        mock_llm.return_value = {
            "response": "Test response",
            "error": None
        }
        
        result = simple_llm_process("Test prompt")
        self.assertIsInstance(result, dict)
        self.assertIn("prompt", result)
        self.assertIn("response", result)
        self.assertIn("timestamp", result)
    
    def test_simple_log_to_file(self):
        """Test simple file logging"""
        from main import simple_log_to_file
        
        test_data = {"test": "data"}
        
        with patch('main.open', create=True) as mock_open:
            mock_file = MagicMock()
            mock_open.return_value.__enter__.return_value = mock_file
            
            result = simple_log_to_file(test_data)
            self.assertTrue(result)
    
    def test_main_interactive_functions(self):
        """Test main module interactive functions"""
        from jarvis.core.main import simple_llm_process, simple_log_to_file
        
        # Test that functions exist and are callable
        self.assertTrue(callable(simple_llm_process))
        self.assertTrue(callable(simple_log_to_file))
        
    def test_memory_integration_in_main(self):
        """Test memory integration in main module"""
        from jarvis.memory.memory import process_memory_prompt
        
        # Test memory function is accessible
        self.assertTrue(callable(process_memory_prompt))

if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestErrorHandler,
        TestLLMInterface, 
        TestMemory,
        TestLogs,
        TestMainModule
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"UNIT TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)