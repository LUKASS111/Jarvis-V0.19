#!/usr/bin/env python3
"""
Performance Test Suite for V0.41-black-ui
Tests performance characteristics and benchmarks critical functions
"""

import sys
import os
import unittest
import time
import tempfile
import shutil
import threading
import concurrent.futures
from unittest.mock import Mock, patch

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestMemoryPerformance(unittest.TestCase):
    """Test memory system performance"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_bulk_memory_operations(self):
        """Test performance with bulk memory operations"""
        from memory import remember_fact, recall_fact, forget_fact, load_memory
        
        # Test bulk remember performance
        start_time = time.time()
        fact_count = 500
        
        for i in range(fact_count):
            remember_fact(f"bulk_test_{i} to value_{i}")
        
        remember_time = time.time() - start_time
        
        # Test bulk recall performance
        start_time = time.time()
        
        for i in range(fact_count):
            result = recall_fact(f"bulk_test_{i}")
            self.assertEqual(result, f"value_{i}")
        
        recall_time = time.time() - start_time
        
        # Test bulk forget performance
        start_time = time.time()
        
        for i in range(0, fact_count, 2):  # Forget every other fact
            forget_fact(f"bulk_test_{i}")
        
        forget_time = time.time() - start_time
        
        # Performance assertions (adjusted for CI environment)
        self.assertLess(remember_time, 30.0, f"Bulk remember too slow: {remember_time:.2f}s for {fact_count} facts")
        self.assertLess(recall_time, 15.0, f"Bulk recall too slow: {recall_time:.2f}s for {fact_count} facts")
        self.assertLess(forget_time, 15.0, f"Bulk forget too slow: {forget_time:.2f}s for {fact_count//2} facts")
        
        # Print performance metrics
        print(f"\n💾 Memory Performance Metrics:")
        print(f"   Remember: {remember_time:.3f}s ({fact_count/remember_time:.1f} ops/sec)")
        print(f"   Recall:   {recall_time:.3f}s ({fact_count/recall_time:.1f} ops/sec)")
        print(f"   Forget:   {forget_time:.3f}s ({(fact_count//2)/forget_time:.1f} ops/sec)")
    
    def test_memory_size_limits(self):
        """Test memory performance with large data"""
        from memory import remember_fact, recall_fact
        
        # Test with increasingly large values
        sizes = [100, 1000, 5000, 10000]
        
        for size in sizes:
            large_value = "x" * size
            
            start_time = time.time()
            result = remember_fact(f"large_test_{size} to {large_value}")
            remember_time = time.time() - start_time
            
            if "✅" in result:
                start_time = time.time()
                recalled = recall_fact(f"large_test_{size}")
                recall_time = time.time() - start_time
                
                # Verify data integrity
                self.assertEqual(recalled, large_value)
                
                print(f"   Size {size}: Remember {remember_time:.3f}s, Recall {recall_time:.3f}s")
                
                # Performance should degrade gracefully
                self.assertLess(remember_time, 1.0, f"Large value remember too slow for size {size}")
                self.assertLess(recall_time, 0.5, f"Large value recall too slow for size {size}")
    
    def test_concurrent_memory_access(self):
        """Test memory performance under concurrent access"""
        from memory import remember_fact, recall_fact
        
        def worker_remember(start_index, count):
            times = []
            for i in range(start_index, start_index + count):
                start_time = time.time()
                remember_fact(f"concurrent_test_{i} to value_{i}")
                times.append(time.time() - start_time)
            return times
        
        def worker_recall(start_index, count):
            times = []
            for i in range(start_index, start_index + count):
                start_time = time.time()
                recall_fact(f"concurrent_test_{i}")
                times.append(time.time() - start_time)
            return times
        
        # Concurrent operations
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            # Submit remember tasks
            remember_futures = []
            for i in range(0, 200, 50):
                future = executor.submit(worker_remember, i, 50)
                remember_futures.append(future)
            
            # Wait for completion and collect results
            all_remember_times = []
            for future in concurrent.futures.as_completed(remember_futures):
                all_remember_times.extend(future.result())
        
        # Test concurrent recall
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            recall_futures = []
            for i in range(0, 200, 50):
                future = executor.submit(worker_recall, i, 50)
                recall_futures.append(future)
            
            all_recall_times = []
            for future in concurrent.futures.as_completed(recall_futures):
                all_recall_times.extend(future.result())
        
        # Analyze performance
        avg_remember_time = sum(all_remember_times) / len(all_remember_times)
        avg_recall_time = sum(all_recall_times) / len(all_recall_times)
        
        print(f"\n🔄 Concurrent Memory Performance:")
        print(f"   Avg Remember: {avg_remember_time:.4f}s")
        print(f"   Avg Recall:   {avg_recall_time:.4f}s")
        
        # Performance assertions
        self.assertLess(avg_remember_time, 0.1, "Concurrent remember performance degraded")
        self.assertLess(avg_recall_time, 0.05, "Concurrent recall performance degraded")

class TestLoggingPerformance(unittest.TestCase):
    """Test logging system performance"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_bulk_logging_performance(self):
        """Test performance with bulk logging operations"""
        from logs import log_event, get_logs, clear_logs
        
        # Clear previous logs
        clear_logs()
        
        # Test bulk logging
        event_count = 1000
        events_data = []
        
        start_time = time.time()
        
        for i in range(event_count):
            event_data = {
                "index": i,
                "message": f"Performance test event {i}",
                "timestamp": time.time(),
                "metadata": {"test": True, "batch": "performance"}
            }
            events_data.append((f"perf_event_{i}", event_data))
            log_event(f"perf_event_{i}", event_data)
        
        log_time = time.time() - start_time
        
        # Test bulk retrieval
        start_time = time.time()
        logs = get_logs(limit=event_count + 100)  # Get more than we need to be sure
        retrieval_time = time.time() - start_time
        
        # Performance assertions
        self.assertLess(log_time, 20.0, f"Bulk logging too slow: {log_time:.2f}s for {event_count} events")
        self.assertLess(retrieval_time, 2.0, f"Log retrieval too slow: {retrieval_time:.2f}s")
        
        # Verify log count
        self.assertGreaterEqual(len(logs), event_count)
        
        print(f"\n📝 Logging Performance Metrics:")
        print(f"   Logging:   {log_time:.3f}s ({event_count/log_time:.1f} events/sec)")
        print(f"   Retrieval: {retrieval_time:.3f}s")
        print(f"   Total logs: {len(logs)}")
    
    def test_large_event_logging(self):
        """Test logging performance with large events"""
        from logs import log_event
        
        # Test with increasingly large event data
        sizes = [1000, 5000, 10000, 20000]
        
        for size in sizes:
            large_data = {
                "large_field": "x" * size,
                "metadata": {"size": size, "test": "performance"},
                "timestamp": time.time()
            }
            
            start_time = time.time()
            result = log_event(f"large_event_{size}", large_data)
            log_time = time.time() - start_time
            
            self.assertTrue(result, f"Failed to log large event of size {size}")
            
            print(f"   Size {size}: {log_time:.4f}s")
            
            # Performance should degrade gracefully
            self.assertLess(log_time, 0.5, f"Large event logging too slow for size {size}")
    
    def test_concurrent_logging(self):
        """Test logging performance under concurrent access"""
        from logs import log_event
        
        def worker_log(worker_id, event_count):
            times = []
            for i in range(event_count):
                event_data = {
                    "worker_id": worker_id,
                    "event_index": i,
                    "timestamp": time.time(),
                    "data": f"Worker {worker_id} event {i}"
                }
                
                start_time = time.time()
                log_event(f"concurrent_log_{worker_id}_{i}", event_data)
                times.append(time.time() - start_time)
            
            return times
        
        # Concurrent logging
        with concurrent.futures.ThreadPoolExecutor(max_workers=4) as executor:
            futures = []
            for worker_id in range(4):
                future = executor.submit(worker_log, worker_id, 100)
                futures.append(future)
            
            all_times = []
            for future in concurrent.futures.as_completed(futures):
                all_times.extend(future.result())
        
        # Analyze performance
        avg_log_time = sum(all_times) / len(all_times)
        
        print(f"\n🔄 Concurrent Logging Performance:")
        print(f"   Avg Log Time: {avg_log_time:.4f}s")
        print(f"   Total Events: {len(all_times)}")
        
        # Performance assertion
        self.assertLess(avg_log_time, 0.05, "Concurrent logging performance degraded")

class TestLLMInterfacePerformance(unittest.TestCase):
    """Test LLM interface performance"""
    
    @patch('llm_interface.requests.post')
    def test_llm_call_performance(self, mock_post):
        """Test LLM interface call performance"""
        from llm_interface import ask_local_llm
        from main import simple_llm_process
        
        # Mock fast LLM response
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.text = '{"response": "Fast test response"}'
        mock_post.return_value = mock_response
        
        # Test direct LLM calls
        call_count = 50
        direct_times = []
        
        for i in range(call_count):
            start_time = time.time()
            result = ask_local_llm(f"Test prompt {i}")
            direct_times.append(time.time() - start_time)
            
            self.assertIsInstance(result, str)  # ask_local_llm returns string
        
        # Test processed LLM calls
        processed_times = []
        
        for i in range(call_count):
            start_time = time.time()
            result = simple_llm_process(f"Processed test prompt {i}")
            processed_times.append(time.time() - start_time)
            
            self.assertIsInstance(result, dict)
        
        # Analyze performance
        avg_direct_time = sum(direct_times) / len(direct_times)
        avg_processed_time = sum(processed_times) / len(processed_times)
        
        print(f"\n🤖 LLM Interface Performance:")
        print(f"   Direct calls:    {avg_direct_time:.4f}s avg")
        print(f"   Processed calls: {avg_processed_time:.4f}s avg")
        
        # Performance assertions (mocked calls should be very fast)
        self.assertLess(avg_direct_time, 0.1, "Direct LLM calls too slow")
        self.assertLess(avg_processed_time, 0.2, "Processed LLM calls too slow")
    
    def test_model_switching_performance(self):
        """Test model switching performance"""
        from llm_interface import set_ollama_model, get_ollama_model, AVAILABLE_MODELS
        
        original_model = get_ollama_model()
        switch_times = []
        
        # Test switching between models
        for _ in range(20):
            for model in AVAILABLE_MODELS:
                start_time = time.time()
                set_ollama_model(model)
                current_model = get_ollama_model()
                switch_times.append(time.time() - start_time)
                
                self.assertEqual(current_model, model)
        
        # Restore original model
        set_ollama_model(original_model)
        
        # Analyze performance
        avg_switch_time = sum(switch_times) / len(switch_times)
        
        print(f"\n🔄 Model Switching Performance:")
        print(f"   Avg Switch Time: {avg_switch_time:.4f}s")
        
        # Model switching should be instant
        self.assertLess(avg_switch_time, 0.001, "Model switching too slow")

class TestErrorHandlingPerformance(unittest.TestCase):
    """Test error handling performance"""
    
    def setUp(self):
        """Set up test environment"""
        self.temp_dir = tempfile.mkdtemp()
        
    def tearDown(self):
        """Clean up test environment"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    def test_error_logging_performance(self):
        """Test error logging performance"""
        from error_handler import error_handler, ErrorLevel
        
        error_count = 200
        log_times = []
        
        for i in range(error_count):
            test_error = Exception(f"Performance test error {i}")
            
            start_time = time.time()
            error_handler.log_error(
                test_error,
                f"Performance test context {i}",
                ErrorLevel.WARNING,
                f"Performance test message {i}"
            )
            log_times.append(time.time() - start_time)
        
        # Analyze performance
        avg_log_time = sum(log_times) / len(log_times)
        total_time = sum(log_times)
        
        print(f"\n⚠️  Error Logging Performance:")
        print(f"   Avg Log Time: {avg_log_time:.4f}s")
        print(f"   Total Time:   {total_time:.3f}s for {error_count} errors")
        print(f"   Rate:         {error_count/total_time:.1f} errors/sec")
        
        # Error logging should be fast
        self.assertLess(avg_log_time, 0.01, "Error logging too slow")
        self.assertLess(total_time, 2.0, "Bulk error logging too slow")
    
    def test_safe_execute_performance(self):
        """Test safe_execute decorator performance"""
        from error_handler import safe_execute
        
        @safe_execute(fallback_value="fallback", context="performance_test")
        def failing_function():
            raise Exception("Test error")
        
        @safe_execute(fallback_value="success", context="performance_test")
        def success_function():
            return "success"
        
        # Test failing function performance
        fail_times = []
        for i in range(100):
            start_time = time.time()
            result = failing_function()
            fail_times.append(time.time() - start_time)
            self.assertEqual(result, "fallback")
        
        # Test successful function performance
        success_times = []
        for i in range(100):
            start_time = time.time()
            result = success_function()
            success_times.append(time.time() - start_time)
            self.assertEqual(result, "success")
        
        # Analyze performance
        avg_fail_time = sum(fail_times) / len(fail_times)
        avg_success_time = sum(success_times) / len(success_times)
        
        print(f"\n🛡️  Safe Execute Performance:")
        print(f"   Failing functions:    {avg_fail_time:.4f}s avg")
        print(f"   Successful functions: {avg_success_time:.4f}s avg")
        
        # Safe execute should have minimal overhead
        self.assertLess(avg_fail_time, 0.01, "Safe execute with error too slow")
        self.assertLess(avg_success_time, 0.001, "Safe execute without error too slow")

class TestSystemPerformance(unittest.TestCase):
    """Test overall system performance"""
    
    @patch('llm_interface.ask_local_llm')
    def test_complete_workflow_performance(self, mock_llm):
        """Test performance of complete user workflows"""
        from main import simple_llm_process, process_interactive_input
        from memory import remember_fact, recall_fact
        from logs import log_event
        
        # Mock LLM response
        mock_llm.return_value = {
            "response": "Workflow test response",
            "error": None
        }
        
        workflow_times = []
        
        for i in range(10):
            start_time = time.time()
            
            # Complete workflow: remember -> LLM process -> log -> recall
            remember_fact(f"workflow_test_{i} to value_{i}")
            simple_llm_process(f"Workflow test prompt {i}")
            log_event(f"workflow_event_{i}", {"index": i, "test": "performance"})
            recall_fact(f"workflow_test_{i}")
            
            workflow_times.append(time.time() - start_time)
        
        # Analyze performance
        avg_workflow_time = sum(workflow_times) / len(workflow_times)
        
        print(f"\n🔄 Complete Workflow Performance:")
        print(f"   Avg Workflow Time: {avg_workflow_time:.3f}s")
        print(f"   Operations per workflow: 4")
        
        # Complete workflow should be reasonable
        self.assertLess(avg_workflow_time, 1.0, "Complete workflow too slow")

if __name__ == "__main__":
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add all test classes
    test_classes = [
        TestMemoryPerformance,
        TestLoggingPerformance,
        TestLLMInterfacePerformance,
        TestErrorHandlingPerformance,
        TestSystemPerformance
    ]
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
    
    # Run tests with detailed output
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(test_suite)
    
    # Print summary
    print(f"\n{'='*60}")
    print(f"PERFORMANCE TEST SUMMARY")
    print(f"{'='*60}")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    print(f"Success rate: {((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun * 100):.1f}%")
    
    if result.failures:
        print(f"\n⚠️  PERFORMANCE ISSUES:")
        for test, traceback in result.failures:
            print(f"   - {test}")
    
    # Exit with appropriate code
    sys.exit(0 if result.wasSuccessful() else 1)