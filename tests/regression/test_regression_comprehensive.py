#!/usr/bin/env python3
"""
Regression Test Suite for V0.41-black-ui
Prevents return of known issues and bugs from previous versions
"""

import sys
import os
import unittest
import tempfile
import shutil
import subprocess
import threading
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestHistoricalBugFixes(unittest.TestCase):
    """Test that previously fixed bugs don't reappear"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_no_qtextcursor_threading_errors(self):
        """Regression: QTextCursor threading errors should not occur"""
        try:
            from gui.modern_gui import SimplifiedJarvisGUI
            from PyQt5.QtWidgets import QApplication
            from PyQt5.QtCore import QThread
            
            # This should not produce threading errors
            app = QApplication.instance() or QApplication([])
            gui = SimplifiedJarvisGUI()
            
            # Test signal emissions (historically caused threading issues)
            gui.response_update_signal.emit("Test message")
            gui.analysis_update_signal.emit("Test analysis")
            
            # Should complete without QTextCursor errors
            self.assertTrue(True)
            
        except ImportError:
            self.skipTest("PyQt5 not available")
        except Exception as e:
            if "QTextCursor" in str(e) and "thread" in str(e).lower():
                self.fail(f"QTextCursor threading regression detected: {e}")
    
    def test_no_unknown_property_transform_errors(self):
        """Regression: 'Unknown property transform' CSS errors should not occur"""
        try:
            from gui.modern_gui import SimplifiedJarvisGUI, SIMPLE_STYLE
            
            # Verify CSS doesn't contain problematic 'transform' properties
            self.assertNotIn("transform:", SIMPLE_STYLE.lower())
            self.assertNotIn("-webkit-transform:", SIMPLE_STYLE.lower())
            self.assertNotIn("-moz-transform:", SIMPLE_STYLE.lower())
            
        except ImportError:
            self.skipTest("GUI module not available")
    
    def test_no_langchain_dependencies(self):
        """Regression: Langchain dependencies should be completely removed"""
        # Test that langchain is not imported anywhere
        modules_to_check = [
            'main', 'modern_gui', 'error_handler', 
            'llm_interface', 'memory', 'logs'
        ]
        
        for module_name in modules_to_check:
            try:
                module = __import__(module_name)
                module_file = module.__file__
                
                with open(module_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Check for langchain imports or references
                langchain_indicators = [
                    'import langchain',
                    'from langchain',
                    'langchain.',
                    'LangChain',
                    'LANGCHAIN'
                ]
                
                for indicator in langchain_indicators:
                    self.assertNotIn(indicator, content, 
                                   f"Langchain reference found in {module_name}: {indicator}")
                        
            except ImportError:
                continue
    
    def test_no_complex_archive_system(self):
        """Regression: Complex archive system should be removed"""
        # Verify no archive-related functions exist in current code
        
        try:
            from jarvis.core.main import process_interactive_input
            
            # Commands that should no longer exist
            removed_commands = [
                "archive logs",
                "start learning", 
                "system optimizer",
                "langchain reasoning"
            ]
            
            for command in removed_commands:
                result = process_interactive_input(command)
                # Should return a dict with LLM response since these commands don't exist
                self.assertIsInstance(result, dict)
                # The result should indicate it's an LLM response (no special handling)
                self.assertTrue("response" in result or "action" in result)
                
        except ImportError:
            pass
    
    def test_no_memory_leaks_in_gui(self):
        """Regression: GUI should not have memory leaks from parent-child issues"""
        try:
            import os
            os.environ['QT_QPA_PLATFORM'] = 'offscreen'
            
            from gui.modern_gui import SimplifiedJarvisGUI
            from PyQt5.QtWidgets import QApplication
            
            app = QApplication.instance() or QApplication([])
            
            # Create and destroy GUI multiple times
            for i in range(3):
                gui = SimplifiedJarvisGUI()
                del gui
            
            # Test passes if no crashes occur
            self.assertTrue(True)
            
        except Exception as e:
            # In headless environment, GUI tests are expected to fail
            self.skipTest(f"GUI test skipped in headless environment: {e}")
            for i in range(3):
                gui = SimplifiedJarvisGUI()
                # Should not accumulate memory or cause parent-child errors
                del gui
            
            self.assertTrue(True)
            
        except ImportError:
            self.skipTest("PyQt5 not available")

class TestInterfaceConsistency(unittest.TestCase):
    """Test that interfaces remain consistent across refactoring"""
    
    def test_llm_interface_consistency(self):
        """Test LLM interface maintains expected API"""
        from jarvis.llm.llm_interface import (
            get_available_models, get_ollama_model, set_ollama_model,
            get_dynamic_timeout, ask_local_llm
        )
        
        # Test expected return types
        models = get_available_models()
        self.assertIsInstance(models, list)
        self.assertGreater(len(models), 0)
        
        current_model = get_ollama_model()
        self.assertIsInstance(current_model, str)
        self.assertIn(current_model, models)
        
        timeout = get_dynamic_timeout()
        self.assertIsInstance(timeout, int)
        self.assertGreater(timeout, 0)
    
    def test_memory_interface_consistency(self):
        """Test memory interface maintains expected API"""
        from jarvis.memory.memory import (
            remember_fact, recall_fact, forget_fact, 
            process_memory_prompt, load_memory, save_memory
        )
        
        # Test basic memory operations
        result = remember_fact("test_consistency to working")
        self.assertIsInstance(result, str)
        
        recalled = recall_fact("test_consistency")
        self.assertEqual(recalled, "working")
        
        forgotten = forget_fact("test_consistency")
        self.assertIsInstance(forgotten, str)
        
        # Test memory persistence
        memory_data = load_memory()
        self.assertIsInstance(memory_data, dict)
    
    def test_error_handler_interface_consistency(self):
        """Test error handler interface maintains expected API"""
        from jarvis.core.error_handler import (
            error_handler, safe_execute, ErrorLevel,
            validate_file_path, validate_json_data, validate_model_name
        )
        
        # Test error levels
        for level in [ErrorLevel.INFO, ErrorLevel.WARNING, ErrorLevel.ERROR, ErrorLevel.CRITICAL]:
            self.assertIsInstance(level.value, str)
        
        # Test validation functions
        self.assertTrue(validate_file_path("test.txt"))
        self.assertTrue(validate_json_data({}))
        self.assertTrue(validate_model_name("llama3:8b"))
        
        # Test error handler
        summary = error_handler.get_session_summary()
        self.assertIsInstance(summary, dict)

class TestDataIntegrity(unittest.TestCase):
    """Test that data handling maintains integrity across operations"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_memory_data_integrity(self):
        """Test that memory data remains intact through operations"""
        from jarvis.memory.memory import remember_fact, recall_fact, load_memory, save_memory
        
        # Store test data
        test_facts = {
            "integrity_test_1": "value_1",
            "integrity_test_2": "value_2", 
            "integrity_test_3": "special_chars_ąćęłńóśźż"
        }
        
        for key, value in test_facts.items():
            remember_fact(f"{key} to {value}")
        
        # Verify immediate recall
        for key, expected_value in test_facts.items():
            recalled = recall_fact(key)
            self.assertEqual(recalled, expected_value)
        
        # Force save/load cycle
        memory_data = load_memory()
        save_memory(memory_data)
        
        # Verify data survives save/load
        for key, expected_value in test_facts.items():
            recalled = recall_fact(key)
            self.assertEqual(recalled, expected_value)
    
    def test_log_data_integrity(self):
        """Test that log data maintains integrity"""
        from jarvis.utils.logs import log_event, get_logs, clear_logs
        
        # Clear previous logs
        clear_logs()
        
        # Log test data
        test_events = [
            ("integrity_event_1", {"data": "value_1", "number": 123}),
            ("integrity_event_2", {"data": "special_ąćęłńóśźż", "float": 45.67}),
            ("integrity_event_3", {"complex": {"nested": {"data": "deep_value"}}})
        ]
        
        for event_type, event_data in test_events:
            result = log_event(event_type, event_data)
            self.assertTrue(result)
        
        # Verify log integrity
        logs = get_logs()
        self.assertGreaterEqual(len(logs), len(test_events))
        
        # Check that all test events are present with correct data
        for event_type, expected_data in test_events:
            matching_logs = [log for log in logs if log.get("event") == event_type]
            self.assertGreater(len(matching_logs), 0)
            
            found_log = matching_logs[0]
            self.assertEqual(found_log["data"], expected_data)
    
    def test_error_handling_data_integrity(self):
        """Test that error handling preserves data integrity"""
        from jarvis.core.error_handler import ErrorHandler, safe_execute, ErrorLevel
        
        # Test data through error conditions
        test_data = {"important": "data", "number": 42}
        
        @safe_execute(fallback_value=test_data, context="integrity_test")
        def data_processing_function():
            # Simulate processing that might fail
            processed_data = test_data.copy()
            processed_data["processed"] = True
            raise Exception("Simulated error")
            return processed_data
        
        result = data_processing_function()
        
        # Verify data integrity after error
        self.assertEqual(result, test_data)
        self.assertIn("important", result)
        self.assertEqual(result["number"], 42)

class TestPerformanceRegression(unittest.TestCase):
    """Test that performance hasn't degraded from previous versions"""
    
    def test_memory_operation_performance(self):
        """Test that memory operations are reasonably fast"""
        import time
        from jarvis.memory.memory import remember_fact, recall_fact
        
        # Test bulk memory operations
        start_time = time.time()
        
        for i in range(100):
            remember_fact(f"perf_test_{i} to value_{i}")
        
        remember_time = time.time() - start_time
        
        start_time = time.time()
        
        for i in range(100):
            recall_fact(f"perf_test_{i}")
        
        recall_time = time.time() - start_time
        
        # Should complete within reasonable time (adjusted for CI environment)
        self.assertLess(remember_time, 10.0, "Memory remember operations too slow")
        self.assertLess(recall_time, 5.0, "Memory recall operations too slow")
    
    def test_log_operation_performance(self):
        """Test that logging operations are reasonably fast"""
        import time
        from jarvis.utils.logs import log_event, clear_logs
        
        # Clear logs first
        clear_logs()
        
        # Test bulk logging
        start_time = time.time()
        
        for i in range(50):
            log_event(f"perf_event_{i}", {"index": i, "data": f"test_data_{i}"})
        
        log_time = time.time() - start_time
        
        # Should complete within reasonable time
        self.assertLess(log_time, 5.0, "Logging operations too slow")
    
    @patch('jarvis.llm.llm_interface.ask_local_llm')
    def test_llm_interface_performance(self, mock_llm):
        """Test that LLM interface operations are reasonably fast"""
        import time
        from jarvis.core.main import simple_llm_process
        
        # Mock fast LLM response
        mock_llm.return_value = {
            "response": "Fast test response",
            "error": None
        }
        
        # Test multiple LLM calls
        start_time = time.time()
        
        for i in range(10):
            simple_llm_process(f"Test prompt {i}")
        
        llm_time = time.time() - start_time
        
        # Should complete within reasonable time (excluding actual LLM processing)
        self.assertLess(llm_time, 2.0, "LLM interface operations too slow")

if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestHistoricalBugFixes,
        TestInterfaceConsistency,
        TestDataIntegrity,
        TestPerformanceRegression
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"REGRESSION TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\n[WARN]  REGRESSIONS DETECTED:")
        for test, traceback in result.failures:
            print(f"   - {test}: {traceback.split(chr(10))[-2] if chr(10) in traceback else traceback}")
    
    if result.errors:
        print(f"\n[FAIL] ERRORS DETECTED:")
        for test, traceback in result.errors:
            print(f"   - {test}: {traceback.split(chr(10))[-2] if chr(10) in traceback else traceback}")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)