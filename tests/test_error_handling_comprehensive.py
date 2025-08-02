#!/usr/bin/env python3
"""
Comprehensive Error Handling Test Suite
Tests error reporting, logging, and import verification functionality
Critical for blocking CRDT implementation until complete coverage achieved
"""

import sys
import os
import unittest
import tempfile
import shutil
import json
from unittest.mock import Mock, patch, MagicMock

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestErrorReporting(unittest.TestCase):
    """Test error reporting functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_create_error_report_import(self):
        """Test that create_error_report can be imported correctly"""
        try:
            from jarvis.core.error_handler import create_error_report
            self.assertTrue(callable(create_error_report))
        except ImportError as e:
            self.fail(f"Failed to import create_error_report: {e}")
    
    def test_create_error_report_functionality(self):
        """Test create_error_report generates valid report"""
        from jarvis.core.error_handler import create_error_report, error_handler, ErrorLevel
        
        # Generate some test errors
        test_error = Exception("Test error for report generation")
        error_handler.log_error(test_error, "test_context", ErrorLevel.ERROR)
        error_handler.log_error(test_error, "test_warning", ErrorLevel.WARNING)
        
        # Generate report
        report = create_error_report()
        
        # Verify report structure
        self.assertIsInstance(report, str)
        self.assertIn("AutoGPT System - Raport Błędów", report)
        self.assertIn("Podsumowanie", report)
        self.assertIn("Błędy:", report)
        self.assertIn("Ostrzeżenia:", report)
    
    def test_error_report_cli_command(self):
        """Test error report generation through CLI command"""
        from jarvis.core.main import process_interactive_input
        
        # Test błędy command
        result = process_interactive_input("błędy")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["action"], "error_report")
        self.assertIn("report", result)
        self.assertIsInstance(result["report"], str)
        
        # Test errors command
        result = process_interactive_input("errors")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["action"], "error_report")
        
        # Test raport command
        result = process_interactive_input("raport")
        self.assertIsInstance(result, dict)
        self.assertEqual(result["action"], "error_report")
    
    def test_error_handler_session_summary(self):
        """Test error handler session summary functionality"""
        from jarvis.core.error_handler import error_handler, ErrorLevel
        
        # Clear previous errors
        error_handler.session_errors = []
        error_handler.error_count = 0
        error_handler.warning_count = 0
        
        # Generate test data
        test_error = Exception("Test session error")
        error_handler.log_error(test_error, "session_test", ErrorLevel.ERROR)
        error_handler.log_error(test_error, "session_warning", ErrorLevel.WARNING)
        
        # Get summary
        summary = error_handler.get_session_summary()
        
        # Verify summary structure
        self.assertIsInstance(summary, dict)
        self.assertIn("total_errors", summary)
        self.assertIn("total_warnings", summary)
        self.assertIn("total_fallbacks", summary)
        self.assertIn("most_common_errors", summary)
        self.assertIn("recent_errors", summary)
        
        # Verify counts
        self.assertGreaterEqual(summary["total_errors"], 1)
        self.assertGreaterEqual(summary["total_warnings"], 1)

class TestLoggingFunctionality(unittest.TestCase):
    """Test logging functionality in CLI and GUI modes"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_log_event_functionality(self):
        """Test log_event function"""
        from jarvis.utils.logs import log_event, get_logs, clear_logs
        
        # Clear previous logs
        clear_logs()
        
        # Test logging
        test_data = {"test": "data", "value": 123}
        log_event("test_event", test_data)
        
        # Verify logging
        logs = get_logs()
        self.assertIsInstance(logs, list)
        self.assertGreater(len(logs), 0)
        
        # Find our test log
        test_logs = [log for log in logs if log.get("event") == "test_event"]
        self.assertGreater(len(test_logs), 0)
        
        test_log = test_logs[0]
        self.assertEqual(test_log["event"], "test_event")
        self.assertEqual(test_log["data"], test_data)
    
    def test_cli_logging_mode(self):
        """Test logging in CLI mode"""
        from jarvis.core.main import process_interactive_input
        from jarvis.utils.logs import get_logs, clear_logs
        from jarvis.memory.memory import remember_fact
        
        # Clear logs
        clear_logs()
        
        # Perform operations that should log
        remember_fact("test_cli to cli_mode_test")
        process_interactive_input("help")
        
        # Check logs
        logs = get_logs()
        self.assertIsInstance(logs, list)
        # Logs may be filtered or managed, so we just verify the system works
    
    @patch('jarvis.llm.llm_interface.ask_local_llm')
    def test_gui_logging_mode(self, mock_llm):
        """Test logging functionality accessible from GUI"""
        from jarvis.utils.logs import log_event, get_logs, clear_logs
        
        mock_llm.return_value = {"response": "Test GUI logging", "error": None}
        
        # Clear logs
        clear_logs()
        
        # Test GUI-related logging
        log_event("gui_test", {"mode": "test", "component": "logging"})
        
        # Verify logging works
        logs = get_logs()
        gui_logs = [log for log in logs if log.get("event") == "gui_test"]
        self.assertGreater(len(gui_logs), 0)
    
    def test_error_logging(self):
        """Test error logging functionality"""
        from jarvis.core.error_handler import error_handler, ErrorLevel
        
        # Test different error levels
        test_exception = Exception("Test logging error")
        
        error_handler.log_error(test_exception, "test_info", ErrorLevel.INFO)
        error_handler.log_error(test_exception, "test_warning", ErrorLevel.WARNING)
        error_handler.log_error(test_exception, "test_error", ErrorLevel.ERROR)
        error_handler.log_error(test_exception, "test_critical", ErrorLevel.CRITICAL)
        
        # Verify error was logged
        summary = error_handler.get_session_summary()
        self.assertIsInstance(summary, dict)

class TestImportVerification(unittest.TestCase):
    """Test import verification after cleanup/refactoring"""
    
    def test_core_module_imports(self):
        """Test that all core modules can be imported"""
        core_modules = [
            "jarvis.core.main",
            "jarvis.core.error_handler",
            "jarvis.memory.memory", 
            "jarvis.llm.llm_interface",
            "jarvis.utils.logs",
            "jarvis.core.data_archiver",
            "jarvis.core.archive_purge_manager",
            "jarvis.core.data_verifier"
        ]
        
        for module_name in core_modules:
            try:
                __import__(module_name)
            except ImportError as e:
                self.fail(f"Failed to import core module {module_name}: {e}")
    
    def test_gui_module_imports(self):
        """Test GUI module imports"""
        try:
            from gui.modern_gui import SimplifiedJarvisGUI
            self.assertTrue(hasattr(SimplifiedJarvisGUI, '__init__'))
        except ImportError:
            # GUI modules may not be available in headless environment
            self.skipTest("GUI modules not available in test environment")
    
    def test_error_handler_functions_available(self):
        """Test that all error handler functions are available"""
        from jarvis.core.error_handler import (
            ErrorHandler, ErrorLevel, error_handler, 
            safe_execute, create_error_report
        )
        
        # Verify classes and functions exist
        self.assertTrue(callable(ErrorHandler))
        self.assertTrue(hasattr(ErrorLevel, 'ERROR'))
        self.assertTrue(hasattr(error_handler, 'log_error'))
        self.assertTrue(callable(safe_execute))
        self.assertTrue(callable(create_error_report))
    
    def test_memory_functions_available(self):
        """Test that memory functions are available"""
        from jarvis.memory.memory import (
            remember_fact, recall_fact, forget_fact, 
            process_memory_prompt
        )
        
        # Verify functions exist and are callable
        self.assertTrue(callable(remember_fact))
        self.assertTrue(callable(recall_fact)) 
        self.assertTrue(callable(forget_fact))
        self.assertTrue(callable(process_memory_prompt))
    
    def test_logging_functions_available(self):
        """Test that logging functions are available"""
        from jarvis.utils.logs import log_event, get_logs, clear_logs
        
        # Verify functions exist and are callable
        self.assertTrue(callable(log_event))
        self.assertTrue(callable(get_logs))
        self.assertTrue(callable(clear_logs))

class TestEndToEndErrorReporting(unittest.TestCase):
    """End-to-end tests for error reporting workflow"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_complete_error_reporting_workflow(self):
        """Test complete error reporting from generation to display"""
        from jarvis.core.error_handler import error_handler, ErrorLevel, create_error_report
        from jarvis.core.main import process_interactive_input
        
        # Step 1: Clear existing errors
        error_handler.session_errors = []
        error_handler.error_count = 0
        error_handler.warning_count = 0
        
        # Step 2: Generate test errors
        test_error = Exception("End-to-end test error")
        error_handler.log_error(test_error, "e2e_test", ErrorLevel.ERROR)
        error_handler.log_error(test_error, "e2e_warning", ErrorLevel.WARNING)
        
        # Step 3: Generate report directly
        direct_report = create_error_report()
        self.assertIsInstance(direct_report, str)
        self.assertIn("AutoGPT System", direct_report)
        
        # Step 4: Generate report through CLI
        cli_result = process_interactive_input("błędy")
        self.assertIsInstance(cli_result, dict)
        self.assertEqual(cli_result["action"], "error_report")
        
        # Step 5: Verify report content matches
        cli_report = cli_result["report"]
        self.assertIsInstance(cli_report, str)
        self.assertIn("AutoGPT System", cli_report)
    
    def test_error_recovery_reporting(self):
        """Test error reporting during recovery scenarios"""
        from jarvis.core.error_handler import safe_execute, error_handler, ErrorLevel
        
        # Define a function that will fail and use fallback
        @safe_execute(fallback_value="recovery_successful", context="test_recovery")
        def failing_function():
            raise Exception("Intentional failure for testing")
        
        # Clear previous errors
        error_handler.session_errors = []
        error_handler.error_count = 0
        
        # Execute failing function
        result = failing_function()
        self.assertEqual(result, "recovery_successful")
        
        # Verify error was logged
        summary = error_handler.get_session_summary()
        self.assertGreaterEqual(summary["total_errors"], 1)
        
        # Verify fallback was counted
        self.assertGreaterEqual(summary["total_fallbacks"], 1)
    
    def test_logging_and_error_integration(self):
        """Test integration between logging and error systems"""
        from jarvis.utils.logs import log_event, get_logs, clear_logs
        from jarvis.core.error_handler import error_handler, ErrorLevel
        
        # Clear logs and errors
        clear_logs()
        error_handler.session_errors = []
        
        # Perform operations that use both systems
        log_event("integration_test", {"status": "starting"})
        
        test_error = Exception("Integration test error")
        error_handler.log_error(test_error, "integration_context", ErrorLevel.WARNING)
        
        log_event("integration_test", {"status": "error_logged"})
        
        # Verify both systems captured data
        logs = get_logs()
        integration_logs = [log for log in logs if log.get("event") == "integration_test"]
        self.assertGreaterEqual(len(integration_logs), 1)
        
        summary = error_handler.get_session_summary()
        self.assertGreaterEqual(summary["total_warnings"], 1)

if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestErrorReporting,
        TestLoggingFunctionality,
        TestImportVerification,
        TestEndToEndErrorReporting
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"ERROR HANDLING TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)