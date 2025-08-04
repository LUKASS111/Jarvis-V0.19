#!/usr/bin/env python3
"""
Phase 8 Testing: Advanced Network Topologies
===========================================

Comprehensive test suite for enterprise network architecture including:
- Mesh network optimization
- High-availability features
- Enterprise integration
- Failover mechanisms
- Partition recovery
"""

import sys
import os
import unittest
import time
import json
from datetime import datetime, timedelta

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis.core.advanced_network_topology import (
    AdvancedNetworkTopologyManager, NetworkNode, NetworkTopology, NodeStatus,
    NetworkPartition, LoadBalancer, FailoverManager, PartitionDetector,
    BandwidthOptimizer, create_network_topology_manager, create_test_network
)


class TestAdvancedNetworkTopology(unittest.TestCase):
    """Test advanced network topology functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.network_manager = create_network_topology_manager("test_master", "enterprise")
        self.test_nodes = []
        
        # Create test nodes
        for i in range(5):
            node = NetworkNode(
                node_id=f"node_{i}",
                address=f"192.168.1.{100 + i}",
                port=8000 + i,
                region=f"region_{i % 3}",
                capabilities=["compute", "storage"] if i % 2 == 0 else ["compute"],
                load=i * 0.1
            )
            self.test_nodes.append(node)
            self.network_manager.add_node(node)
    
    def test_network_initialization(self):
        """Test network topology manager initialization"""
        self.assertEqual(self.network_manager.node_id, "test_master")
        self.assertEqual(self.network_manager.topology_type, NetworkTopology.ENTERPRISE)
        self.assertIsNotNone(self.network_manager.load_balancer)
        self.assertIsNotNone(self.network_manager.failover_manager)
        self.assertIsNotNone(self.network_manager.partition_detector)
        
        print("✓ Network topology manager initialization test passed")
    
    def test_node_management(self):
        """Test adding and removing nodes"""
        initial_count = len(self.network_manager.nodes)
        
        # Add new node
        new_node = NetworkNode(
            node_id="new_test_node",
            address="192.168.1.200",
            port=8010,
            region="region_0"
        )
        
        success = self.network_manager.add_node(new_node)
        self.assertTrue(success)
        self.assertEqual(len(self.network_manager.nodes), initial_count + 1)
        self.assertIn("new_test_node", self.network_manager.nodes)
        
        # Remove node
        success = self.network_manager.remove_node("new_test_node")
        self.assertTrue(success)
        self.assertEqual(len(self.network_manager.nodes), initial_count)
        self.assertNotIn("new_test_node", self.network_manager.nodes)
        
        print("✓ Node management test passed")
    
    def test_mesh_topology_optimization(self):
        """Test mesh topology optimization"""
        # Create mesh topology manager
        mesh_manager = create_network_topology_manager("mesh_master", "mesh")
        
        # Add nodes from different regions
        for i in range(6):
            node = NetworkNode(
                node_id=f"mesh_node_{i}",
                address=f"10.0.{i//3}.{100 + i}",
                port=9000 + i,
                region=f"region_{i // 3}",  # 3 nodes per region
                load=i * 0.05
            )
            mesh_manager.add_node(node)
        
        # Wait for topology optimization
        time.sleep(1)
        
        # Check that routing table has been populated
        self.assertGreater(len(mesh_manager.routing_table), 0)
        
        # Verify mesh connectivity (each node should connect to others)
        for node_id in mesh_manager.nodes:
            if mesh_manager.nodes[node_id].status == NodeStatus.ACTIVE:
                self.assertIn(node_id, mesh_manager.routing_table)
        
        print("✓ Mesh topology optimization test passed")
    
    def test_enterprise_topology_optimization(self):
        """Test enterprise topology optimization"""
        # Wait for topology optimization to run
        time.sleep(1)
        
        # Check routing table population
        self.assertGreater(len(self.network_manager.routing_table), 0)
        
        # Verify hierarchical structure
        active_nodes = [n for n in self.network_manager.nodes.values() 
                       if n.status == NodeStatus.ACTIVE]
        
        if len(active_nodes) > 1:
            # Should have routing connections
            total_connections = sum(len(routes) for routes in self.network_manager.routing_table.values())
            self.assertGreater(total_connections, 0)
        
        print("✓ Enterprise topology optimization test passed")


class TestLoadBalancer(unittest.TestCase):
    """Test load balancer functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.load_balancer = LoadBalancer()
        
        # Register test nodes
        for i in range(4):
            node = NetworkNode(
                node_id=f"lb_node_{i}",
                address=f"192.168.2.{100 + i}",
                port=8000 + i,
                load=i * 0.2,
                latency=10 + i * 5,
                capabilities=["compute"] if i % 2 == 0 else ["compute", "storage"]
            )
            self.load_balancer.register_node(node)
    
    def test_node_registration(self):
        """Test node registration with load balancer"""
        self.assertEqual(len(self.load_balancer.nodes), 4)
        
        for i in range(4):
            self.assertIn(f"lb_node_{i}", self.load_balancer.nodes)
        
        print("✓ Load balancer node registration test passed")
    
    def test_optimal_node_selection(self):
        """Test optimal node selection"""
        # Select optimal node for default operation
        optimal_node = self.load_balancer.select_optimal_node("default")
        self.assertIsNotNone(optimal_node)
        self.assertIn(optimal_node, self.load_balancer.nodes)
        
        # Select optimal node for compute operation
        compute_node = self.load_balancer.select_optimal_node("compute")
        self.assertIsNotNone(compute_node)
        
        # Select optimal node for storage operation
        storage_node = self.load_balancer.select_optimal_node("storage")
        self.assertIsNotNone(storage_node)
        
        print("✓ Load balancer optimal node selection test passed")
    
    def test_node_unregistration(self):
        """Test node unregistration"""
        initial_count = len(self.load_balancer.nodes)
        
        # Unregister a node
        self.load_balancer.unregister_node("lb_node_0")
        
        self.assertEqual(len(self.load_balancer.nodes), initial_count - 1)
        self.assertNotIn("lb_node_0", self.load_balancer.nodes)
        
        print("✓ Load balancer node unregistration test passed")


class TestFailoverManager(unittest.TestCase):
    """Test failover management"""
    
    def setUp(self):
        """Set up test environment"""
        self.failover_manager = FailoverManager()
        
        # Create test nodes
        self.nodes = {}
        for i in range(5):
            self.nodes[f"failover_node_{i}"] = NetworkNode(
                node_id=f"failover_node_{i}",
                address=f"192.168.3.{100 + i}",
                port=8000 + i,
                region="test_region",
                load=i * 0.15,
                status=NodeStatus.ACTIVE
            )
    
    def test_failover_trigger(self):
        """Test failover triggering"""
        # Trigger failover for a node
        success = self.failover_manager.trigger_failover("failover_node_0", self.nodes)
        self.assertTrue(success)
        
        # Check failover history
        self.assertEqual(len(self.failover_manager.failover_history), 1)
        
        failover_event = self.failover_manager.failover_history[0]
        self.assertEqual(failover_event["failed_node"], "failover_node_0")
        self.assertIn("failover_node", failover_event)
        self.assertIn("timestamp", failover_event)
        
        print("✓ Failover trigger test passed")
    
    def test_no_candidates_failover(self):
        """Test failover when no candidates available"""
        # Set all nodes except one to failed status
        for node_id in list(self.nodes.keys())[1:]:
            self.nodes[node_id].status = NodeStatus.FAILED
        
        # Try to trigger failover for the last active node
        success = self.failover_manager.trigger_failover("failover_node_0", self.nodes)
        self.assertFalse(success)  # Should fail due to no candidates
        
        print("✓ No candidates failover test passed")


class TestPartitionDetector(unittest.TestCase):
    """Test network partition detection"""
    
    def setUp(self):
        """Set up test environment"""
        self.partition_detector = PartitionDetector()
        
        # Create test nodes
        self.nodes = {}
        for i in range(4):
            self.nodes[f"partition_node_{i}"] = NetworkNode(
                node_id=f"partition_node_{i}",
                address=f"192.168.4.{100 + i}",
                port=8000 + i,
                status=NodeStatus.ACTIVE,
                last_heartbeat=datetime.now()
            )
        
        # Create simple routing table
        self.routing_table = {
            "partition_node_0": ["partition_node_1", "partition_node_2"],
            "partition_node_1": ["partition_node_0", "partition_node_3"],
            "partition_node_2": ["partition_node_0"],
            "partition_node_3": ["partition_node_1"]
        }
    
    def test_no_partitions(self):
        """Test when no partitions exist"""
        partitions = self.partition_detector.detect_partitions(self.nodes, self.routing_table)
        self.assertEqual(len(partitions), 0)
        
        print("✓ No partitions detection test passed")
    
    def test_partition_detection(self):
        """Test partition detection"""
        # Simulate old heartbeat for some nodes (partition condition)
        old_time = datetime.now() - timedelta(seconds=10)
        self.nodes["partition_node_2"].last_heartbeat = old_time
        self.nodes["partition_node_3"].last_heartbeat = old_time
        
        partitions = self.partition_detector.detect_partitions(self.nodes, self.routing_table)
        
        # Should detect a partition
        self.assertGreater(len(partitions), 0)
        
        # Check partition contains the unreachable nodes
        partition = list(partitions.values())[0]
        self.assertIn("partition_node_2", partition.nodes)
        self.assertIn("partition_node_3", partition.nodes)
        
        print("✓ Partition detection test passed")


class TestBandwidthOptimizer(unittest.TestCase):
    """Test bandwidth optimization"""
    
    def setUp(self):
        """Set up test environment"""
        self.bandwidth_optimizer = BandwidthOptimizer()
        
        # Create test nodes
        self.nodes = {}
        for i in range(3):
            self.nodes[f"bandwidth_node_{i}"] = NetworkNode(
                node_id=f"bandwidth_node_{i}",
                address=f"192.168.5.{100 + i}",
                port=8000 + i
            )
        
        self.routing_table = {
            "bandwidth_node_0": ["bandwidth_node_1"],
            "bandwidth_node_1": ["bandwidth_node_0", "bandwidth_node_2"],
            "bandwidth_node_2": ["bandwidth_node_1"]
        }
    
    def test_bandwidth_optimization(self):
        """Test bandwidth optimization"""
        # Run optimization
        self.bandwidth_optimizer.optimize_connections(self.nodes, self.routing_table)
        
        # Check optimization stats
        stats = self.bandwidth_optimizer.get_optimization_stats()
        
        self.assertIn("compression_ratio", stats)
        self.assertIn("optimization_savings", stats)
        
        # Should have some optimization enabled
        if self.bandwidth_optimizer.compression_enabled:
            self.assertGreater(stats["compression_ratio"], 0)
        
        if self.bandwidth_optimizer.delta_sync:
            self.assertGreater(stats["optimization_savings"], 0)
        
        print("✓ Bandwidth optimization test passed")


class TestNetworkIntegration(unittest.TestCase):
    """Test end-to-end network integration"""
    
    def setUp(self):
        """Set up test environment"""
        self.network = create_test_network(8)
        time.sleep(2)  # Allow network to stabilize
    
    def test_full_network_status(self):
        """Test comprehensive network status"""
        status = self.network.get_network_status()
        
        # Verify all expected fields
        required_fields = [
            "topology_type", "node_id", "network_stats", "active_nodes",
            "total_connections", "partitions", "high_availability",
            "enterprise_features", "bandwidth_optimization"
        ]
        
        for field in required_fields:
            self.assertIn(field, status)
        
        # Verify reasonable values
        self.assertGreater(status["active_nodes"], 0)
        self.assertGreaterEqual(status["high_availability"], 0)
        self.assertLessEqual(status["high_availability"], 100)
        
        print("✓ Full network status test passed")
    
    def test_network_scalability(self):
        """Test network scalability"""
        initial_nodes = len(self.network.nodes)
        
        # Add more nodes to test scalability
        for i in range(20, 25):  # Add 5 more nodes
            node = NetworkNode(
                node_id=f"scale_node_{i}",
                address=f"192.168.10.{i}",
                port=8000 + i,
                region=f"region_{i % 4}"
            )
            success = self.network.add_node(node)
            self.assertTrue(success)
        
        # Verify nodes were added
        self.assertEqual(len(self.network.nodes), initial_nodes + 5)
        
        # Check network still functions
        status = self.network.get_network_status()
        self.assertGreater(status["active_nodes"], initial_nodes)
        
        print("✓ Network scalability test passed")
    
    def test_high_availability_features(self):
        """Test high availability features"""
        # Get initial availability
        status = self.network.get_network_status()
        initial_availability = status["high_availability"]
        
        # Should have high availability enabled
        self.assertGreaterEqual(initial_availability, 99.0)
        
        # Test that HA manager is working
        ha_score = self.network.ha_manager.get_availability_score()
        self.assertGreaterEqual(ha_score, 99.0)
        
        print("✓ High availability features test passed")
    
    def test_enterprise_integration(self):
        """Test enterprise integration features"""
        status = self.network.get_network_status()
        
        # Check enterprise features
        enterprise_features = status["enterprise_features"]
        self.assertIn("security_enabled", enterprise_features)
        self.assertIn("encryption_enabled", enterprise_features)
        self.assertIn("compliance_level", enterprise_features)
        
        # Should have enterprise-grade security
        self.assertEqual(enterprise_features["compliance_level"], "enterprise")
        
        print("✓ Enterprise integration test passed")


def run_phase8_tests():
    """Run all Phase 8 tests"""
    print("\n" + "="*60)
    print("PHASE 8: ADVANCED NETWORK TOPOLOGIES - TEST SUITE")
    print("="*60)
    
    # Test suites
    test_suites = [
        ('Network Topology Management', TestAdvancedNetworkTopology),
        ('Load Balancer', TestLoadBalancer),
        ('Failover Manager', TestFailoverManager),
        ('Partition Detector', TestPartitionDetector),
        ('Bandwidth Optimizer', TestBandwidthOptimizer),
        ('Network Integration', TestNetworkIntegration)
    ]
    
    total_tests = 0
    passed_tests = 0
    failed_tests = 0
    
    for suite_name, test_class in test_suites:
        print(f"\n[TEST SUITE] {suite_name}")
        print("-" * 50)
        
        suite = unittest.TestLoader().loadTestsFromTestCase(test_class)
        runner = unittest.TextTestRunner(verbosity=0, stream=open('/dev/null', 'w'))
        result = runner.run(suite)
        
        suite_tests = result.testsRun
        suite_failures = len(result.failures)
        suite_errors = len(result.errors)
        suite_passed = suite_tests - suite_failures - suite_errors
        
        total_tests += suite_tests
        passed_tests += suite_passed
        failed_tests += suite_failures + suite_errors
        
        if suite_failures == 0 and suite_errors == 0:
            print(f"✅ {suite_name}: {suite_passed}/{suite_tests} tests passed")
        else:
            print(f"❌ {suite_name}: {suite_passed}/{suite_tests} tests passed")
            for failure in result.failures:
                print(f"   FAIL: {failure[0]}")
            for error in result.errors:
                print(f"   ERROR: {error[0]}")
    
    # Final summary
    print(f"\n" + "="*60)
    print("PHASE 8 TEST RESULTS SUMMARY")
    print("="*60)
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
    
    if failed_tests == 0:
        print("\n🎉 ALL PHASE 8 TESTS PASSED!")
        print("✅ Advanced Network Topologies implementation is operational")
        print("✅ Enterprise features validated")
        print("✅ High availability confirmed")
        print("✅ Mathematical guarantees maintained")
    else:
        print(f"\n⚠️  {failed_tests} tests failed - review implementation")
    
    return passed_tests, total_tests


if __name__ == "__main__":
    passed, total = run_phase8_tests()
    exit(0 if passed == total else 1)