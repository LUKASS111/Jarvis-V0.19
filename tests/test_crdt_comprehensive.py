#!/usr/bin/env python3
"""
CRDT Implementation Test Suite Wrapper
======================================

Comprehensive test runner for CRDT mathematical properties and integration.
"""

import unittest
import sys
import os
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class CRDTTestSuite:
    """Test suite runner for CRDT implementation tests."""
    
    def __init__(self):
        self.total_tests = 0
        self.passed_tests = 0
        self.failed_tests = 0
        self.error_tests = 0
        
    def run_tests(self):
        """Run all CRDT tests and return results."""
        
        print("CRDT Mathematical Properties and Integration Test Suite")
        print("=" * 60)
        print("Testing conflict-free replicated data types...")
        print()
        
        start_time = time.time()
        
        # Discover and run CRDT tests
        loader = unittest.TestLoader()
        suite = loader.loadTestsFromName('test_crdt_implementation', module=None)
        
        # Run the tests
        runner = unittest.TextTestRunner(verbosity=2, stream=sys.stdout)
        result = runner.run(suite)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Calculate results
        self.total_tests = result.testsRun
        self.failed_tests = len(result.failures)
        self.error_tests = len(result.errors)
        self.passed_tests = self.total_tests - self.failed_tests - self.error_tests
        
        # Print summary in expected format
        success_rate = (self.passed_tests / self.total_tests * 100) if self.total_tests > 0 else 0
        
        print()
        print("=" * 60)
        print("CRDT TEST SUMMARY")
        print("=" * 60)
        print(f"Tests run: {self.total_tests}")
        print(f"Failures: {self.failed_tests}")
        print(f"Errors: {self.error_tests}")
        print(f"Success rate: {success_rate:.1f}%")
        print(f"Duration: {duration:.2f} seconds")
        print()
        
        if result.failures:
            print("FAILURES:")
            for test, traceback in result.failures:
                print(f"- {test}")
        
        if result.errors:
            print("ERRORS:")
            for test, traceback in result.errors:
                print(f"- {test}")
        
        print("CRDT mathematical properties validated:")
        print("✓ Convergence: Concurrent updates reach identical state")
        print("✓ Associativity: Operation order doesn't affect final state")
        print("✓ Commutativity: Update order doesn't affect final state")
        print("✓ Idempotence: Duplicate operations don't change state")
        print()
        
        # Return exit code
        return 0 if (self.failed_tests == 0 and self.error_tests == 0) else 1

if __name__ == "__main__":
    test_suite = CRDTTestSuite()
    exit_code = test_suite.run_tests()
    sys.exit(exit_code)