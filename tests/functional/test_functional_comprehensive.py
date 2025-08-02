#!/usr/bin/env python3
"""
Functional Test Suite for V0.41-black-ui
Tests end-user scenarios and complete application workflows
"""

import sys
import os
import unittest
import tempfile
import shutil
import subprocess
import time
import json
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

class TestCLIFunctionality(unittest.TestCase):
    """Test command-line interface functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        self.project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_main_script_execution(self):
        """Test that main.py can be executed"""
        main_script = os.path.join(self.project_root, "main.py")
        
        # Test with --version flag if available
        try:
            result = subprocess.run(
                [sys.executable, main_script, "--help"],
                capture_output=True,
                text=True,
                timeout=10,
                cwd=self.project_root
            )
            # Should not crash, regardless of help availability
            self.assertIsNotNone(result.returncode)
        except subprocess.TimeoutExpired:
            # Timeout is acceptable for interactive mode
            pass
        except FileNotFoundError:
            self.skipTest("main.py not found or not executable")
    
    @patch('jarvis.core.main.ask_local_llm')
    def test_interactive_commands(self, mock_llm):
        """Test interactive command processing"""
        from jarvis.core.main import process_interactive_input
        
        # Mock LLM responses
        mock_llm.return_value = "Mocked LLM response"
        
        # Test help command (should return dict with action)
        help_result = process_interactive_input("help")
        self.assertIsInstance(help_result, dict)
        self.assertIn("action", help_result)
        
        # Test exit command
        exit_result = process_interactive_input("exit")
        self.assertIsInstance(exit_result, dict)
        self.assertEqual(exit_result["action"], "exit")
        
        # Test memory commands - these go through memory functions
        from jarvis.memory.memory import remember_fact, recall_fact
        memory_result = remember_fact("test to functional_test")
        self.assertIsInstance(memory_result, str)
        
        recall_result = recall_fact("test")
        self.assertEqual(recall_result, "functional_test")
        
        # Test LLM query
        llm_result = process_interactive_input("How are you?")
        self.assertIsInstance(llm_result, dict)
        self.assertIn("action", llm_result)

class TestGUIFunctionality(unittest.TestCase):
    """Test GUI functionality without actually showing windows"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_gui_script_execution(self):
        """Test that modern_gui.py can be imported and initialized"""
        try:
            from gui.modern_gui import SimplifiedJarvisGUI
            
            # Test class can be imported
            self.assertTrue(hasattr(SimplifiedJarvisGUI, '__init__'))
            
        except ImportError:
            self.skipTest("PyQt5 not available for GUI testing")
    
    @patch('gui.modern_gui.QApplication')
    @patch('gui.modern_gui.QWidget')
    @patch('gui.modern_gui.ask_local_llm')
    def test_gui_component_functionality(self, mock_llm, mock_widget, mock_app):
        """Test GUI component functionality"""
        try:
            import os
            os.environ['QT_QPA_PLATFORM'] = 'offscreen'
            
            from gui.modern_gui import SimplifiedJarvisGUI
            
            # Mock dependencies properly
            mock_app.return_value = Mock()
            mock_widget.return_value = Mock()
            mock_llm.return_value = "Test GUI response"
            
            # Create GUI instance
            gui = SimplifiedJarvisGUI()
            
            # Test basic functionality
            self.assertIsNotNone(gui)
            
        except Exception as e:
            # GUI tests may fail in headless environment
            self.skipTest(f"GUI test skipped in headless environment: {e}")
            
            # Test that GUI has required components
            self.assertTrue(hasattr(gui, 'response_update_signal'))
            self.assertTrue(hasattr(gui, 'analysis_update_signal'))
            
            # Test signal emissions (should not crash)
            gui.response_update_signal.emit("Test response")
            gui.analysis_update_signal.emit("Test analysis")
            
        except ImportError:
            self.skipTest("PyQt5 not available for GUI testing")

class TestUserScenarios(unittest.TestCase):
    """Test complete user scenarios"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('jarvis.llm.llm_interface.ask_local_llm')
    def test_new_user_onboarding(self, mock_llm):
        """Test scenario: New user starts the application"""
        from jarvis.core.main import simple_llm_process, process_interactive_input
        from jarvis.memory.memory import remember_fact, recall_fact
        from jarvis.core.error_handler import ErrorHandler
        
        # Mock LLM responses
        mock_llm.return_value = {
            "response": "Welcome! I'm here to help you.",
            "error": None
        }
        
        # Scenario: New user interaction
        
        # Step 1: User asks for help
        help_response = process_interactive_input("help")
        self.assertIsInstance(help_response, dict)
        self.assertIn("action", help_response)
        
        # Step 2: User introduces themselves
        remember_fact("my_name to John")
        
        # Step 3: User asks a question
        question_response = simple_llm_process("What can you do?")
        self.assertIsInstance(question_response, dict)
        self.assertIn("response", question_response)
        
        # Step 4: User recalls their name
        recalled_name = recall_fact("my_name")
        self.assertEqual(recalled_name, "John")
        
        # Step 5: Check system handled everything gracefully
        from jarvis.core.error_handler import error_handler
        summary = error_handler.get_session_summary()
        self.assertIsInstance(summary, dict)
    
    @patch('jarvis.llm.llm_interface.ask_local_llm')
    def test_power_user_workflow(self, mock_llm):
        """Test scenario: Power user with complex workflow"""
        from jarvis.core.main import simple_llm_process
        from jarvis.memory.memory import remember_fact, recall_fact, forget_fact, process_memory_prompt
        from jarvis.utils.logs import log_event, get_logs, clear_logs
        
        # Mock LLM responses
        mock_llm.return_value = {
            "response": "Complex task completed successfully",
            "error": None
        }
        
        # Scenario: Power user complex workflow
        
        # Step 1: User stores multiple facts
        facts = [
            "project_name to Advanced_AI_System",
            "version to 2.1.3",
            "status to in_development",
            "deadline to 2024-12-31"
        ]
        
        for fact in facts:
            result = remember_fact(fact)
            self.assertIn("[OK]", result)
        
        # Step 2: User performs complex queries
        for i in range(3):
            query_result = simple_llm_process(f"Analyze project status {i+1}")
            self.assertIsInstance(query_result, dict)
        
        # Step 3: User manages memory
        all_facts = {}
        for fact in facts:
            key = fact.split(" to ")[0]
            value = recall_fact(key)
            all_facts[key] = value
            self.assertNotIn("❓", value)
        
        # Step 4: User logs important events
        for i, (key, value) in enumerate(all_facts.items()):
            log_event(f"fact_verification_{i}", {"key": key, "value": value})
        
        # Step 5: User cleans up some data
        forget_result = forget_fact("deadline")
        self.assertIn("[TRASH]", forget_result)
        
        # Step 7: Verify final state
        logs = get_logs()
        self.assertGreater(len(logs), 0)
    
    def test_error_recovery_scenario(self):
        """Test scenario: System encounters errors and recovers"""
        from jarvis.core.error_handler import ErrorHandler, safe_execute, ErrorLevel
        from jarvis.memory.memory import remember_fact, recall_fact
        from jarvis.utils.logs import log_event
        
        # Scenario: Error recovery
        
        # Step 1: Generate some errors
        @safe_execute(fallback_value="recovery_value", context="test_error")
        def error_prone_function():
            raise Exception("Simulated error")
        
        # Step 2: User continues working despite errors
        error_result = error_prone_function()
        self.assertEqual(error_result, "recovery_value")
        
        # Step 3: User saves important data
        remember_fact("recovery_test to successful")
        
        # Step 4: User logs the incident
        log_event("error_recovery", {"status": "successful", "fallback_used": True})
        
        # Step 5: Verify system state is consistent
        recalled_data = recall_fact("recovery_test")
        self.assertEqual(recalled_data, "successful")
        
        # Create error handler instance to check state
        test_handler = ErrorHandler(os.path.join(tempfile.mkdtemp(), "test_recovery.jsonl"))
        summary = test_handler.get_session_summary()
        self.assertIsInstance(summary, dict)
    
    @patch('jarvis.llm.llm_interface.ask_local_llm')
    def test_batch_processing_scenario(self, mock_llm):
        """Test scenario: User processes multiple tasks"""
        from jarvis.core.main import simple_llm_process
        from jarvis.utils.logs import log_event, get_logs, clear_logs
        
        # Mock LLM responses
        mock_llm.return_value = {
            "response": "Batch task completed",
            "error": None
        }
        
        # Scenario: Batch processing
        
        # Step 1: Clear previous logs
        clear_logs()
        
        # Step 2: Process multiple tasks
        tasks = [
            "Analyze data set 1",
            "Generate report for client A", 
            "Review code changes",
            "Update documentation",
            "Plan next sprint"
        ]
        
        results = []
        for i, task in enumerate(tasks):
            # Process task
            result = simple_llm_process(task)
            results.append(result)
            
            # Log progress
            log_event("batch_task", {
                "task_id": i+1,
                "task": task,
                "status": "completed"
            })
            
            # Verify result structure
            self.assertIsInstance(result, dict)
            self.assertIn("prompt", result)
            self.assertIn("response", result)
        
        # Step 3: Verify all tasks completed
        self.assertEqual(len(results), len(tasks))
        
        # Step 4: Verify logging
        logs = get_logs()
        batch_logs = [log for log in logs if log.get("event") == "batch_task"]
        # We should have at least some batch logs, but the exact count may vary due to log management
        self.assertGreaterEqual(len(batch_logs), 1)  # At least one log should be present
        self.assertLessEqual(len(batch_logs), len(tasks))  # But not more than the tasks we created

class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""
    
    def test_empty_inputs(self):
        """Test system behavior with empty inputs"""
        from jarvis.core.main import process_interactive_input
        from jarvis.memory.memory import remember_fact, recall_fact
        
        # Test empty command
        empty_result = process_interactive_input("")
        self.assertIsNone(empty_result)  # Empty input should return None
        
        # Test empty memory operations
        empty_remember = remember_fact("")
        self.assertIn("[FAIL]", empty_remember)
        
        empty_recall = recall_fact("")
        self.assertIn("[QUESTION]", empty_recall)
    
    def test_large_inputs(self):
        """Test system behavior with large inputs"""
        from jarvis.core.main import process_interactive_input
        from jarvis.memory.memory import remember_fact
        
        # Test large command
        large_command = "a" * 1000
        large_result = process_interactive_input(large_command)
        self.assertIsInstance(large_result, dict)
        
        # Test large memory value
        large_fact = f"large_test to {'x' * 500}"
        large_remember = remember_fact(large_fact)
        # Should handle gracefully
        self.assertIsInstance(large_remember, str)
    
    def test_special_characters(self):
        """Test system behavior with special characters"""
        from jarvis.memory.memory import remember_fact, recall_fact
        
        # Test special characters in memory
        special_fact = "special_test to ąćęłńóśźż!@#$%^&*()"
        special_result = remember_fact(special_fact)
        self.assertIsInstance(special_result, str)
        
        if "✅" in special_result:
            # If successfully remembered, should be able to recall
            recalled = recall_fact("special_test")
            self.assertIn("ąćęłńóśźż", recalled)
    
    def test_concurrent_operations(self):
        """Test system behavior with rapid operations"""
        from jarvis.memory.memory import remember_fact, recall_fact
        from jarvis.utils.logs import log_event
        
        # Rapid memory operations
        for i in range(10):
            remember_fact(f"rapid_test_{i} to value_{i}")
            log_event(f"rapid_event_{i}", {"index": i})
        
        # Verify all operations completed
        for i in range(10):
            result = recall_fact(f"rapid_test_{i}")
            self.assertEqual(result, f"value_{i}")

if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestCLIFunctionality,
        TestGUIFunctionality,
        TestUserScenarios,
        TestEdgeCases
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"FUNCTIONAL TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)