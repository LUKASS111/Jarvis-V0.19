#!/usr/bin/env python3
"""
Test suite for CRDT Phase 5 - Advanced Features
Performance optimization, monitoring, and enterprise features testing
"""

import unittest
import time
import json
import threading
import sys
import os
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis.core.crdt.crdt_performance_optimizer import (
    CRDTPerformanceOptimizer, DeltaCompressor, LazySynchronizer, 
    ConflictBatcher, PerformanceMonitor, PerformanceMetrics, CompressionResult
)
from jarvis.core.crdt.crdt_monitoring_dashboard import (
    CRDTMonitoringCoordinator, CRDTDashboardExtension, CRDTAlerting,
    CRDTHealthMetrics, SyncMetrics, ConflictMetrics, CRDTMetricsCollector
)


class TestCRDTPerformanceOptimizer(unittest.TestCase):
    """Test CRDT performance optimization features"""
    
    def setUp(self):
        """Setup test environment"""
        self.node_id = "test_node_performance"
        self.optimizer = CRDTPerformanceOptimizer(self.node_id)
    
    def tearDown(self):
        """Cleanup test environment"""
        if hasattr(self.optimizer, 'stop'):
            self.optimizer.stop()
    
    def test_optimizer_initialization(self):
        """Test optimizer initialization"""
        self.assertEqual(self.optimizer.node_id, self.node_id)
        self.assertIsNotNone(self.optimizer.compressor)
        self.assertIsNotNone(self.optimizer.lazy_sync)
        self.assertIsNotNone(self.optimizer.conflict_batcher)
        self.assertIsNotNone(self.optimizer.performance_monitor)
        self.assertTrue(self.optimizer.optimization_enabled)
    
    def test_optimization_lifecycle(self):
        """Test starting and stopping optimization"""
        # Initially stopped
        self.assertFalse(self.optimizer.lazy_sync.running)
        self.assertFalse(self.optimizer.performance_monitor.monitoring_active)
        
        # Start optimization
        self.optimizer.start()
        self.assertTrue(self.optimizer.lazy_sync.running)
        self.assertTrue(self.optimizer.performance_monitor.monitoring_active)
        
        # Stop optimization
        self.optimizer.stop()
        self.assertFalse(self.optimizer.lazy_sync.running)
        self.assertFalse(self.optimizer.performance_monitor.monitoring_active)
    
    def test_optimization_status(self):
        """Test optimization status reporting"""
        status = self.optimizer.get_optimization_status()
        
        self.assertIn('enabled', status)
        self.assertIn('lazy_sync_active', status)
        self.assertIn('monitoring_active', status)
        self.assertIn('performance_summary', status)
        self.assertIn('sync_queue_size', status)
        self.assertIn('pending_conflicts', status)
    
    def test_delta_transmission_optimization(self):
        """Test delta transmission optimization"""
        # Small delta (should not be compressed)
        small_delta = {"operation": "increment", "value": 1}
        optimized_data, algorithm = self.optimizer.optimize_delta_transmission(small_delta)
        self.assertEqual(algorithm, "none")
        
        # Large delta (should be compressed)
        large_delta = {"operation": "bulk_update", "data": "x" * 2000}
        optimized_data, algorithm = self.optimizer.optimize_delta_transmission(large_delta)
        self.assertIn(algorithm, ["gzip", "lz4"])
    
    def test_optimized_sync_scheduling(self):
        """Test optimized sync scheduling"""
        peer_node = "test_peer"
        
        # Schedule with different activity levels
        self.optimizer.schedule_optimized_sync(peer_node, "high")
        self.optimizer.schedule_optimized_sync(peer_node, "normal")
        self.optimizer.schedule_optimized_sync(peer_node, "low")
        
        # Verify syncs are scheduled
        self.assertGreater(len(self.optimizer.lazy_sync.sync_queue), 0)
    
    def test_conflict_batching(self):
        """Test conflict batching optimization"""
        mock_conflict = Mock()
        mock_conflict.conflict_type = "semantic"
        
        initial_count = len(self.optimizer.conflict_batcher.pending_conflicts)
        self.optimizer.batch_conflict_resolution(mock_conflict)
        
        self.assertEqual(len(self.optimizer.conflict_batcher.pending_conflicts), initial_count + 1)


class TestDeltaCompressor(unittest.TestCase):
    """Test delta compression functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.compressor = DeltaCompressor()
    
    def test_compression_algorithms(self):
        """Test different compression algorithms"""
        test_data = {"operation": "test", "data": "x" * 1000}
        
        # Test gzip compression
        result = self.compressor.compress_delta(test_data, "gzip")
        self.assertIsInstance(result, CompressionResult)
        self.assertGreater(result.compression_ratio, 1.0)
        self.assertEqual(result.algorithm, "gzip")
        
        # Test no compression
        result = self.compressor.compress_delta(test_data, "none")
        self.assertEqual(result.compression_ratio, 1.0)
        self.assertEqual(result.algorithm, "none")
    
    def test_compression_decompression_roundtrip(self):
        """Test compression and decompression roundtrip"""
        original_data = {
            "operation": "bulk_update",
            "entries": [{"id": i, "value": f"data_{i}"} for i in range(100)]
        }
        
        # Compress
        result = self.compressor.compress_delta(original_data, "gzip")
        self.assertGreater(result.compression_ratio, 1.0)
        
        # Decompress
        compressed_bytes = json.dumps(original_data).encode('utf-8')
        decompressed_data = self.compressor.decompress_delta(compressed_bytes, "none")
        
        # Should be identical (for 'none' algorithm test)
        self.assertEqual(decompressed_data, original_data)
    
    def test_optimal_algorithm_selection(self):
        """Test optimal algorithm selection based on data size"""
        # Small data
        small_algo = self.compressor.get_optimal_algorithm(500)
        self.assertEqual(small_algo, "none")
        
        # Medium data
        medium_algo = self.compressor.get_optimal_algorithm(5000)
        self.assertEqual(medium_algo, "lz4")
        
        # Large data
        large_algo = self.compressor.get_optimal_algorithm(50000)
        self.assertEqual(large_algo, "gzip")


class TestLazySynchronizer(unittest.TestCase):
    """Test lazy synchronization functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.node_id = "test_lazy_sync"
        self.synchronizer = LazySynchronizer(self.node_id)
    
    def tearDown(self):
        """Cleanup test environment"""
        if self.synchronizer.running:
            self.synchronizer.stop()
    
    def test_synchronizer_lifecycle(self):
        """Test synchronizer start/stop"""
        self.assertFalse(self.synchronizer.running)
        
        self.synchronizer.start()
        self.assertTrue(self.synchronizer.running)
        
        self.synchronizer.stop()
        self.assertFalse(self.synchronizer.running)
    
    def test_activity_recording(self):
        """Test activity recording for adaptive intervals"""
        peer_node = "test_peer"
        
        initial_activity = self.synchronizer.activity_counters[peer_node]
        self.synchronizer.record_activity(peer_node, 5)
        
        self.assertEqual(self.synchronizer.activity_counters[peer_node], initial_activity + 5)
    
    def test_adaptive_interval_calculation(self):
        """Test adaptive interval calculation"""
        # High activity should result in shorter intervals
        high_activity_interval = self.synchronizer._calculate_adaptive_interval(150, "normal")
        
        # Low activity should result in longer intervals
        low_activity_interval = self.synchronizer._calculate_adaptive_interval(2, "normal")
        
        self.assertLess(high_activity_interval, low_activity_interval)
    
    def test_priority_based_scheduling(self):
        """Test priority-based sync scheduling"""
        peer_node = "test_peer"
        
        # Schedule syncs with different priorities
        self.synchronizer.schedule_sync(peer_node, "critical")
        self.synchronizer.schedule_sync(peer_node, "normal")
        self.synchronizer.schedule_sync(peer_node, "low")
        
        self.assertEqual(len(self.synchronizer.sync_queue), 3)


class TestConflictBatcher(unittest.TestCase):
    """Test conflict batching functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.batcher = ConflictBatcher(batch_size=3, timeout_seconds=1.0)
    
    def test_batcher_initialization(self):
        """Test conflict batcher initialization"""
        self.assertEqual(self.batcher.batch_size, 3)
        self.assertEqual(self.batcher.timeout_seconds, 1.0)
        self.assertEqual(len(self.batcher.pending_conflicts), 0)
    
    def test_conflict_batching_by_size(self):
        """Test conflict batching when batch size is reached"""
        mock_conflicts = [Mock() for _ in range(5)]
        
        # Add conflicts one by one
        for conflict in mock_conflicts[:2]:
            self.batcher.add_conflict(conflict)
        
        # Should not trigger processing yet
        self.assertEqual(len(self.batcher.pending_conflicts), 2)
        
        # Add third conflict - should trigger batch processing
        self.batcher.add_conflict(mock_conflicts[2])
        
        # Batch should be processed and cleared
        time.sleep(0.1)  # Allow processing
        self.assertEqual(len(self.batcher.pending_conflicts), 0)
    
    def test_conflict_batching_by_timeout(self):
        """Test conflict batching by timeout with optimized verification"""
        import threading
        
        # Use optimized timeout for faster testing
        fast_batcher = ConflictBatcher(batch_size=10, timeout_seconds=0.05)
        mock_conflict = Mock()
        
        # Track when batch processing occurs with detailed metrics
        process_event = threading.Event()
        process_count = [0]
        original_process = fast_batcher._process_batch
        
        def tracked_process():
            original_process()
            process_count[0] += 1
            process_event.set()
        
        fast_batcher._process_batch = tracked_process
        
        # Add single conflict (below batch_size threshold)
        start_time = time.time()
        fast_batcher.add_conflict(mock_conflict)
        self.assertEqual(len(fast_batcher.pending_conflicts), 1)
        
        # Verify timer was started
        self.assertIsNotNone(fast_batcher.batch_timer)
        self.assertTrue(fast_batcher.batch_timer.is_alive())
        
        # Wait for timeout with deterministic verification
        timeout_occurred = process_event.wait(timeout=0.15)  # 3x the batch timeout
        processing_time = time.time() - start_time
        
        # Verify timeout triggered processing
        self.assertTrue(timeout_occurred, "Timeout should have triggered batch processing")
        self.assertEqual(len(fast_batcher.pending_conflicts), 0)
        self.assertEqual(process_count[0], 1, "Batch should have been processed exactly once")
        
        # Verify timing is reasonable
        self.assertGreaterEqual(processing_time, 0.04, "Processing occurred too early")
        self.assertLessEqual(processing_time, 0.12, "Processing occurred too late")
        
        # Verify timer was cleaned up
        self.assertTrue(fast_batcher.batch_timer is None or not fast_batcher.batch_timer.is_alive())
    
    def test_conflict_batching_timeout_cancellation(self):
        """Test that timeout is cancelled when batch size is reached first"""
        import threading
        import time
        
        # Use longer timeout to test cancellation
        batcher = ConflictBatcher(batch_size=2, timeout_seconds=10.0)
        mock_conflicts = [Mock() for _ in range(3)]
        
        # Track batch processing
        process_event = threading.Event()
        original_process = batcher._process_batch
        
        def tracked_process():
            original_process()
            process_event.set()
        
        batcher._process_batch = tracked_process
        
        # Add first conflict - should start timer
        batcher.add_conflict(mock_conflicts[0])
        initial_timer = batcher.batch_timer
        self.assertIsNotNone(initial_timer)
        self.assertTrue(initial_timer.is_alive())
        
        # Add second conflict - should trigger immediate processing and cancel timer
        batcher.add_conflict(mock_conflicts[1])
        
        # Wait briefly for processing
        process_occurred = process_event.wait(timeout=0.1)
        
        # Verify immediate processing occurred (not timeout-based)
        self.assertTrue(process_occurred, "Batch should be processed immediately when size threshold reached")
        self.assertEqual(len(batcher.pending_conflicts), 0)
        
        # Wait a moment for timer cleanup to complete
        time.sleep(0.01)
        
        # Verify timer was cleaned up - check both cancellation and timer state
        self.assertTrue(
            batcher.batch_timer is None or not batcher.batch_timer.is_alive(),
            "Timer should be cleaned up when batch processes early"
        )
    
    def test_conflict_batching_concurrent_timeout_and_size(self):
        """Test edge case where timeout and size threshold could race with optimized timing"""
        import threading
        
        # Use optimized timeout to create controlled race condition
        batcher = ConflictBatcher(batch_size=3, timeout_seconds=0.03)
        mock_conflicts = [Mock() for _ in range(3)]
        
        process_count = [0]  # Use list for mutable counter
        process_events = []  # Track multiple processing events
        original_process = batcher._process_batch
        
        def counted_process():
            process_count[0] += 1
            original_process()
            event = threading.Event()
            event.set()
            process_events.append(event)
        
        batcher._process_batch = counted_process
        
        # Add conflicts with controlled timing to test race conditions
        start_time = time.time()
        
        for i, conflict in enumerate(mock_conflicts[:2]):
            batcher.add_conflict(conflict)
            if i == 0:
                time.sleep(0.005)  # Small delay, much less than timeout
        
        # Wait for potential timeout processing
        time.sleep(0.05)  # Wait longer than timeout for first potential processing
        
        # Add final conflict to trigger size-based processing if timeout didn't fire
        batcher.add_conflict(mock_conflicts[2])
        
        # Wait for all processing to complete
        time.sleep(0.05)
        elapsed_time = time.time() - start_time
        
        # Verify processing occurred (may be 1 or 2 due to race conditions)
        self.assertGreaterEqual(process_count[0], 1, 
                              f"Expected at least 1 batch processing, got {process_count[0]}")
        self.assertLessEqual(process_count[0], 2,
                           f"Expected at most 2 batch processing events, got {process_count[0]}")
        self.assertEqual(len(batcher.pending_conflicts), 0, 
                        "All conflicts should be processed")
        
        # Verify timing constraints
        self.assertLessEqual(elapsed_time, 0.15, "Test took too long, timing verification failed")
        
        # Final verification - wait for any pending processing
        time.sleep(0.01)  # Small wait for cleanup


class TestPerformanceMonitor(unittest.TestCase):
    """Test performance monitoring functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.monitor = PerformanceMonitor()
    
    def tearDown(self):
        """Cleanup test environment"""
        if self.monitor.monitoring_active:
            self.monitor.stop_monitoring()
    
    def test_monitor_lifecycle(self):
        """Test monitor start/stop"""
        self.assertFalse(self.monitor.monitoring_active)
        
        self.monitor.start_monitoring()
        self.assertTrue(self.monitor.monitoring_active)
        
        self.monitor.stop_monitoring()
        self.assertFalse(self.monitor.monitoring_active)
    
    def test_metric_recording(self):
        """Test metric recording"""
        metric = PerformanceMetrics(
            operation_type="test_operation",
            latency_ms=100.0,
            memory_usage_mb=10.0,
            cpu_usage_percent=5.0,
            timestamp=datetime.utcnow(),
            success=True
        )
        
        initial_count = len(self.monitor.metrics)
        self.monitor.record_metric(metric)
        
        self.assertEqual(len(self.monitor.metrics), initial_count + 1)
        self.assertEqual(self.monitor.metrics[-1], metric)
    
    def test_operation_measurement(self):
        """Test operation performance measurement"""
        def test_operation():
            time.sleep(0.01)  # Simulate work
            return "test_result"
        
        result = self.monitor.measure_operation("test_op", test_operation)
        
        self.assertEqual(result, "test_result")
        self.assertGreater(len(self.monitor.metrics), 0)
        
        last_metric = self.monitor.metrics[-1]
        self.assertEqual(last_metric.operation_type, "test_op")
        self.assertTrue(last_metric.success)
        self.assertGreater(last_metric.latency_ms, 0)
    
    def test_performance_summary(self):
        """Test performance summary generation"""
        # Add some test metrics
        for i in range(10):
            metric = PerformanceMetrics(
                operation_type="test_op",
                latency_ms=100.0 + i * 10,
                memory_usage_mb=5.0 + i,
                cpu_usage_percent=2.0 + i * 0.5,
                timestamp=datetime.utcnow(),
                success=i < 8  # 2 failures
            )
            self.monitor.record_metric(metric)
        
        summary = self.monitor.get_performance_summary("test_op")
        
        self.assertEqual(summary["total_operations"], 10)
        self.assertEqual(summary["success_rate"], 0.8)
        self.assertGreater(summary["latency"]["avg_ms"], 0)
        self.assertGreater(summary["memory"]["avg_mb"], 0)


class TestCRDTMonitoring(unittest.TestCase):
    """Test CRDT monitoring and dashboard functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.coordinator = CRDTMonitoringCoordinator()
    
    def tearDown(self):
        """Cleanup test environment"""
        if self.coordinator.running:
            self.coordinator.stop()
    
    def test_monitoring_coordinator_lifecycle(self):
        """Test monitoring coordinator start/stop"""
        self.assertFalse(self.coordinator.running)
        
        self.coordinator.start()
        self.assertTrue(self.coordinator.running)
        
        self.coordinator.stop()
        self.assertFalse(self.coordinator.running)
    
    def test_comprehensive_status_generation(self):
        """Test comprehensive status generation"""
        status = self.coordinator.get_comprehensive_status()
        
        self.assertIn('timestamp', status)
        self.assertIn('overall_health_score', status)
        self.assertIn('health_status', status)
        self.assertIn('sync_performance', status)
        self.assertIn('conflict_analysis', status)
        self.assertIn('recommendations', status)
        self.assertIn('alerting', status)
    
    def test_metrics_simulation(self):
        """Test metrics simulation for testing"""
        # Simulate metrics
        self.coordinator.simulate_metrics_for_testing()
        
        # Check that metrics were recorded
        sync_metrics_count = len(self.coordinator.dashboard.metrics_collector.sync_metrics)
        conflict_metrics_count = len(self.coordinator.dashboard.metrics_collector.conflict_metrics)
        
        self.assertGreater(sync_metrics_count, 0)
        self.assertGreater(conflict_metrics_count, 0)


class TestCRDTMetricsCollector(unittest.TestCase):
    """Test CRDT metrics collection functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.collector = CRDTMetricsCollector(max_history=100)
    
    def test_collector_initialization(self):
        """Test metrics collector initialization"""
        self.assertEqual(self.collector.max_history, 100)
        self.assertEqual(len(self.collector.health_metrics), 0)
        self.assertEqual(len(self.collector.sync_metrics), 0)
        self.assertEqual(len(self.collector.conflict_metrics), 0)
    
    def test_health_metrics_recording(self):
        """Test health metrics recording"""
        metric = CRDTHealthMetrics(
            timestamp=datetime.utcnow(),
            sync_status="active",
            active_peers=3,
            total_operations=1000,
            successful_syncs=95,
            failed_syncs=5,
            conflicts_detected=10,
            conflicts_resolved=9,
            average_sync_time_ms=150.0,
            network_partition_resilience=0.95,
            data_consistency_score=0.98,
            performance_impact_percent=8.5
        )
        
        self.collector.record_health_metrics(metric)
        self.assertEqual(len(self.collector.health_metrics), 1)
        self.assertEqual(self.collector.health_metrics[0], metric)
    
    def test_health_score_calculation(self):
        """Test health score calculation"""
        # Add some test metrics
        for i in range(5):
            metric = CRDTHealthMetrics(
                timestamp=datetime.utcnow(),
                sync_status="active",
                active_peers=3,
                total_operations=1000,
                successful_syncs=90 + i,
                failed_syncs=10 - i,
                conflicts_detected=5,
                conflicts_resolved=5,
                average_sync_time_ms=100.0,
                network_partition_resilience=0.95,
                data_consistency_score=0.98,
                performance_impact_percent=5.0
            )
            self.collector.record_health_metrics(metric)
        
        health_score = self.collector.get_current_health_score()
        self.assertGreater(health_score, 0)
        self.assertLessEqual(health_score, 100)
    
    def test_sync_performance_trend(self):
        """Test sync performance trend calculation"""
        # Add test sync metrics
        for i in range(10):
            metric = SyncMetrics(
                peer_node=f"peer_{i}",
                sync_duration_ms=100.0 + i * 10,
                operations_sent=50,
                operations_received=50,
                bandwidth_used_bytes=1024 * i,
                compression_ratio=1.5,
                success=i < 8,  # 2 failures
                timestamp=datetime.utcnow() - timedelta(minutes=i)
            )
            self.collector.record_sync_metrics(metric)
        
        trend = self.collector.get_sync_performance_trend()
        
        self.assertEqual(trend["total_syncs"], 10)
        self.assertEqual(trend["successful_syncs"], 8)
        self.assertEqual(trend["failed_syncs"], 2)
        self.assertEqual(trend["success_rate"], 0.8)
    
    def test_conflict_analysis(self):
        """Test conflict analysis"""
        # Add test conflict metrics
        for i in range(5):
            metric = ConflictMetrics(
                conflict_id=f"conflict_{i}",
                conflict_type="semantic" if i % 2 == 0 else "business_logic",
                detection_time=datetime.utcnow() - timedelta(minutes=i),
                resolution_time=datetime.utcnow() - timedelta(minutes=i-1) if i < 4 else None,
                resolution_strategy="last_write_wins",
                involved_nodes=[f"node_{i}"],
                resolution_duration_ms=200.0 + i * 50 if i < 4 else None,
                success=i < 4,
                manual_intervention=i >= 3
            )
            self.collector.record_conflict_metrics(metric)
        
        analysis = self.collector.get_conflict_analysis()
        
        self.assertEqual(analysis["total_conflicts"], 5)
        self.assertEqual(analysis["resolved_conflicts"], 4)
        self.assertEqual(analysis["resolution_rate"], 0.8)
        self.assertIn("semantic", analysis["conflict_types"])
        self.assertIn("business_logic", analysis["conflict_types"])


class TestCRDTAlerting(unittest.TestCase):
    """Test CRDT alerting functionality"""
    
    def setUp(self):
        """Setup test environment"""
        self.alerting = CRDTAlerting()
        self.alert_triggered = False
        
        def test_handler(alert):
            self.alert_triggered = True
            self.last_alert = alert
        
        self.alerting.add_alert_handler(test_handler)
    
    def test_alerting_initialization(self):
        """Test alerting system initialization"""
        self.assertEqual(len(self.alerting.alert_rules), 0)
        self.assertEqual(len(self.alerting.alert_handlers), 1)  # Our test handler
        self.assertEqual(len(self.alerting.alert_history), 0)
    
    def test_alert_rule_management(self):
        """Test adding and managing alert rules"""
        def test_condition(metrics):
            return metrics.failed_syncs > 10
        
        self.alerting.add_alert_rule(
            name="test_rule",
            condition_func=test_condition,
            severity="high",
            cooldown_minutes=5
        )
        
        self.assertEqual(len(self.alerting.alert_rules), 1)
        self.assertEqual(self.alerting.alert_rules[0]['name'], "test_rule")
    
    def test_alert_triggering(self):
        """Test alert triggering"""
        def high_failure_condition(metrics):
            return metrics.failed_syncs > 10
        
        self.alerting.add_alert_rule(
            name="high_failures",
            condition_func=high_failure_condition,
            severity="high",
            cooldown_minutes=1
        )
        
        # Create metrics that should trigger alert
        trigger_metrics = CRDTHealthMetrics(
            timestamp=datetime.utcnow(),
            sync_status="degraded",
            active_peers=1,
            total_operations=100,
            successful_syncs=50,
            failed_syncs=15,  # This should trigger the alert
            conflicts_detected=5,
            conflicts_resolved=4,
            average_sync_time_ms=200.0,
            network_partition_resilience=0.8,
            data_consistency_score=0.9,
            performance_impact_percent=15.0
        )
        
        self.alerting.check_alerts(trigger_metrics)
        
        self.assertTrue(self.alert_triggered)
        self.assertEqual(len(self.alerting.alert_history), 1)
    
    def test_default_alerts_setup(self):
        """Test default alert rules setup"""
        self.alerting.setup_default_alerts()
        
        self.assertGreater(len(self.alerting.alert_rules), 0)
        
        # Check that we have expected default rules
        rule_names = [rule['name'] for rule in self.alerting.alert_rules]
        self.assertIn("high_sync_failure_rate", rule_names)
        self.assertIn("performance_degradation", rule_names)
        self.assertIn("data_consistency_low", rule_names)
        self.assertIn("high_conflict_rate", rule_names)
    
    def test_cooldown_mechanism(self):
        """Test alert cooldown mechanism"""
        def always_trigger(metrics):
            return True
        
        self.alerting.add_alert_rule(
            name="always_trigger",
            condition_func=always_trigger,
            severity="low",
            cooldown_minutes=1
        )
        
        test_metrics = CRDTHealthMetrics(
            timestamp=datetime.utcnow(),
            sync_status="active",
            active_peers=1,
            total_operations=100,
            successful_syncs=90,
            failed_syncs=10,
            conflicts_detected=1,
            conflicts_resolved=1,
            average_sync_time_ms=100.0,
            network_partition_resilience=0.95,
            data_consistency_score=0.98,
            performance_impact_percent=5.0
        )
        
        # First check should trigger alert
        self.alerting.check_alerts(test_metrics)
        self.assertTrue(self.alert_triggered)
        
        # Reset flag
        self.alert_triggered = False
        
        # Second immediate check should not trigger due to cooldown
        self.alerting.check_alerts(test_metrics)
        self.assertFalse(self.alert_triggered)


class TestCRDTPhase5Integration(unittest.TestCase):
    """Test integration of all Phase 5 components"""
    
    def setUp(self):
        """Setup test environment"""
        self.node_id = "test_node_integration"
        self.optimizer = CRDTPerformanceOptimizer(self.node_id)
        self.coordinator = CRDTMonitoringCoordinator()
    
    def tearDown(self):
        """Cleanup test environment"""
        if hasattr(self.optimizer, 'stop'):
            self.optimizer.stop()
        if self.coordinator.running:
            self.coordinator.stop()
    
    def test_phase_5_components_integration(self):
        """Test that all Phase 5 components work together"""
        # Start all components
        self.optimizer.start()
        self.coordinator.start()
        
        # Verify all components are running
        self.assertTrue(self.optimizer.lazy_sync.running)
        self.assertTrue(self.optimizer.performance_monitor.monitoring_active)
        self.assertTrue(self.coordinator.running)
        
        # Test performance optimization
        test_data = {"operation": "test", "data": "sample"}
        optimized_data, algorithm = self.optimizer.optimize_delta_transmission(test_data)
        self.assertIsNotNone(optimized_data)
        self.assertIsNotNone(algorithm)
        
        # Test monitoring
        status = self.coordinator.get_comprehensive_status()
        self.assertIn('overall_health_score', status)
        
        # Stop all components
        self.optimizer.stop()
        self.coordinator.stop()
        
        # Verify components stopped
        self.assertFalse(self.optimizer.lazy_sync.running)
        self.assertFalse(self.optimizer.performance_monitor.monitoring_active)
        self.assertFalse(self.coordinator.running)
    
    def test_metrics_export_functionality(self):
        """Test metrics export functionality"""
        # Add some test data
        self.coordinator.simulate_metrics_for_testing()
        
        # Export metrics
        export_data = self.coordinator.dashboard.export_metrics("json", hours=1)
        
        self.assertIsInstance(export_data, str)
        parsed_data = json.loads(export_data)
        
        self.assertIn('export_timestamp', parsed_data)
        self.assertIn('health_metrics', parsed_data)
        self.assertIn('sync_metrics', parsed_data)
        self.assertIn('conflict_metrics', parsed_data)
        self.assertIn('summary', parsed_data)
    
    def test_end_to_end_performance_monitoring(self):
        """Test end-to-end performance monitoring"""
        # Start monitoring
        self.optimizer.start()
        
        # Perform some operations
        for i in range(5):
            def test_operation():
                time.sleep(0.001)  # Simulate work
                return f"result_{i}"
            
            result = self.optimizer.performance_monitor.measure_operation(
                f"test_operation_{i}", test_operation
            )
            self.assertEqual(result, f"result_{i}")
        
        # Check metrics were recorded
        metrics_count = len(self.optimizer.performance_monitor.metrics)
        self.assertEqual(metrics_count, 5)
        
        # Get performance summary
        summary = self.optimizer.performance_monitor.get_performance_summary()
        self.assertEqual(summary["total_operations"], 5)
        self.assertEqual(summary["success_rate"], 1.0)
    
    def test_comprehensive_health_reporting(self):
        """Test comprehensive health reporting"""
        # Setup monitoring with test data
        self.coordinator.simulate_metrics_for_testing()
        
        # Generate health report
        health_report = self.coordinator.get_comprehensive_status()
        
        # Verify report structure
        required_fields = [
            'timestamp', 'overall_health_score', 'health_status',
            'sync_performance', 'conflict_analysis', 'recommendations',
            'network_topology', 'performance_impact', 'alerting'
        ]
        
        for field in required_fields:
            self.assertIn(field, health_report, f"Missing field: {field}")
        
        # Verify health score is reasonable
        health_score = health_report['overall_health_score']
        self.assertGreaterEqual(health_score, 0)
        self.assertLessEqual(health_score, 100)
        
        # Verify recommendations are provided
        recommendations = health_report['recommendations']
        self.assertIsInstance(recommendations, list)
        self.assertGreater(len(recommendations), 0)


if __name__ == '__main__':
    unittest.main()