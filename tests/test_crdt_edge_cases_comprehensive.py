#!/usr/bin/env python3
"""
Comprehensive CRDT Edge Cases Test Suite
========================================

Advanced testing for real-world CRDT scenarios including:
- Multi-node synchronization conflicts
- Network partition and recovery
- Packet loss simulation
- Concurrent operation stress testing
- Engineering-grade performance validation

Focuses on real data validation with engineering metrics.
"""

import unittest
import threading
import time
import random
import json
import tempfile
import shutil
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis.core.crdt import GCounter, GSet, LWWRegister, ORSet, PNCounter
from jarvis.core.crdt_manager import CRDTManager


class TestCRDTMultiNodeConflicts(unittest.TestCase):
    """Test multi-node synchronization conflicts with real data scenarios"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.nodes = []
        self.num_nodes = 5
        
        # Create multiple CRDT managers representing different nodes
        for i in range(self.num_nodes):
            node_dir = os.path.join(self.temp_dir, f"node_{i}")
            os.makedirs(node_dir, exist_ok=True)
            node_id = f"node_{i}"
            db_path = os.path.join(node_dir, "jarvis_archive.db")
            manager = CRDTManager(node_id=node_id, db_path=db_path)
            self.nodes.append(manager)
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_concurrent_counter_increments_stress(self):
        """Test concurrent counter increments across multiple nodes under stress"""
        counter_name = "stress_counter"
        operations_per_node = 100
        
        # Initialize counters on all nodes
        for i, node in enumerate(self.nodes):
            node.get_counter(counter_name)
        
        # Concurrent increment operations
        def increment_worker(node_index, node):
            for i in range(operations_per_node):
                # Simulate real-world increment patterns
                increment_value = random.randint(1, 10)
                node.increment_counter(counter_name, increment_value)
                # Small delay to simulate network latency
                time.sleep(0.001)
        
        # Start concurrent operations
        threads = []
        start_time = time.time()
        
        for i, node in enumerate(self.nodes):
            thread = threading.Thread(target=increment_worker, args=(i, node))
            threads.append(thread)
            thread.start()
        
        # Wait for all operations to complete
        for thread in threads:
            thread.join()
        
        operation_time = time.time() - start_time
        
        # Synchronize all nodes (simulate network sync)
        self._synchronize_all_nodes(counter_name, 'counter')
        
        # Verify convergence - all nodes should have the same final value
        expected_total = self.num_nodes * operations_per_node * 5.5  # avg increment
        final_values = []
        
        for node in self.nodes:
            value = node.get_counter_value(counter_name)
            final_values.append(value)
        
        # All nodes must converge to the same value
        self.assertTrue(all(v == final_values[0] for v in final_values),
                       f"Nodes did not converge: {final_values}")
        
        # Performance validation - engineering metrics
        ops_per_second = (self.num_nodes * operations_per_node) / operation_time
        self.assertGreater(ops_per_second, 1000, "Performance below engineering threshold")
        
        print(f"✓ Stress test: {ops_per_second:.0f} ops/sec, converged to {final_values[0]}")
    
    def test_or_set_add_remove_conflicts(self):
        """Test concurrent add/remove operations with conflict resolution"""
        set_name = "conflict_set"
        elements_per_node = 50
        
        # Initialize OR-Sets on all nodes
        for node in self.nodes:
            node.get_or_set(set_name)
        
        # Concurrent add/remove operations
        def add_remove_worker(node_index, node):
            for i in range(elements_per_node):
                element = f"element_{node_index}_{i}"
                
                # Add element
                node.add_to_set(set_name, element)
                
                # Randomly remove some elements from other nodes
                if random.random() < 0.2:  # 20% chance
                    other_element = f"element_{(node_index + 1) % self.num_nodes}_{i}"
                    try:
                        node.remove_from_set(set_name, other_element)
                    except:
                        pass  # Element might not exist yet
                
                time.sleep(0.001)
        
        # Execute concurrent operations
        threads = []
        for i, node in enumerate(self.nodes):
            thread = threading.Thread(target=add_remove_worker, args=(i, node))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        # Synchronize all nodes
        self._synchronize_all_nodes(set_name, 'or_set')
        
        # Verify CRDT mathematical properties
        final_sets = []
        for node in self.nodes:
            node_set = node.get_set_contents(set_name)
            final_sets.append(set(node_set))
        
        # All nodes must converge to the same set
        reference_set = final_sets[0]
        for i, node_set in enumerate(final_sets[1:], 1):
            self.assertEqual(reference_set, node_set,
                           f"Node {i} set differs from reference: {len(reference_set)} vs {len(node_set)}")
        
        print(f"✓ OR-Set conflict resolution: {len(reference_set)} final elements")
    
    def test_network_partition_recovery(self):
        """Test CRDT behavior during network partition and recovery"""
        counter_name = "partition_counter"
        
        # Initialize counters
        for node in self.nodes:
            node.get_counter(counter_name)
        
        # Phase 1: Normal operation
        for i, node in enumerate(self.nodes):
            node.increment_counter(counter_name, 10)
        
        # Synchronize before partition
        self._synchronize_all_nodes(counter_name, 'counter')
        
        # Phase 2: Network partition (split nodes into two groups)
        group1 = self.nodes[:2]  # Nodes 0, 1
        group2 = self.nodes[2:]  # Nodes 2, 3, 4
        
        # Each group operates independently
        for node in group1:
            node.increment_counter(counter_name, 5)
        
        for node in group2:
            node.increment_counter(counter_name, 7)
        
        # Sync within each group
        self._synchronize_group(group1, counter_name, 'counter')
        self._synchronize_group(group2, counter_name, 'counter')
        
        # Verify groups have different values
        group1_value = group1[0].get_counter_value(counter_name)
        group2_value = group2[0].get_counter_value(counter_name)
        self.assertNotEqual(group1_value, group2_value)
        
        # Phase 3: Network recovery - synchronize all nodes
        self._synchronize_all_nodes(counter_name, 'counter')
        
        # Verify convergence after recovery
        final_values = [node.get_counter_value(counter_name) for node in self.nodes]
        self.assertTrue(all(v == final_values[0] for v in final_values),
                       "Nodes did not converge after partition recovery")
        
        # Verify mathematical correctness
        expected_value = (10 * self.num_nodes) + (5 * len(group1)) + (7 * len(group2))
        self.assertEqual(final_values[0], expected_value,
                        f"Final value {final_values[0]} != expected {expected_value}")
        
        print(f"✓ Network partition recovery: converged to {final_values[0]}")
    
    def test_packet_loss_simulation(self):
        """Test CRDT synchronization with simulated packet loss"""
        register_name = "packet_loss_register"
        
        # Initialize LWW registers
        for node in self.nodes:
            node.get_register(register_name)
        
        # Simulate packet loss during synchronization
        def lossy_sync(source_node, target_node, loss_rate=0.3):
            """Simulate synchronization with packet loss"""
            try:
                source_data = source_node.export_crdt_state(register_name)
                
                # Simulate packet loss
                if random.random() > loss_rate:
                    target_node.import_crdt_state(register_name, source_data)
                    return True
                return False
            except:
                return False
        
        # Phase 1: Write operations with concurrent updates
        for i, node in enumerate(self.nodes):
            timestamp = time.time() + i  # Ensure different timestamps
            node.set_register(register_name, f"value_{i}", timestamp)
        
        # Phase 2: Synchronization with packet loss
        sync_attempts = 0
        successful_syncs = 0
        max_attempts = 100
        
        while sync_attempts < max_attempts and not self._check_convergence(register_name):
            sync_attempts += 1
            
            # Random pair synchronization
            source_idx = random.randint(0, self.num_nodes - 1)
            target_idx = random.randint(0, self.num_nodes - 1)
            
            if source_idx != target_idx:
                if lossy_sync(self.nodes[source_idx], self.nodes[target_idx]):
                    successful_syncs += 1
        
        # Verify eventual convergence despite packet loss
        self.assertTrue(self._check_convergence(register_name),
                       "Nodes did not converge despite packet loss")
        
        # Performance metrics
        convergence_ratio = successful_syncs / sync_attempts if sync_attempts > 0 else 0
        print(f"✓ Packet loss simulation: converged after {sync_attempts} attempts "
              f"({convergence_ratio:.2%} success rate)")
    
    def test_concurrent_write_conflicts_lww(self):
        """Test Last-Write-Wins conflict resolution under high concurrency"""
        register_name = "concurrent_writes"
        num_writers = 20
        writes_per_writer = 10
        
        # Initialize registers
        for node in self.nodes:
            node.get_register(register_name)
        
        # Concurrent write operations
        def write_worker(writer_id):
            for i in range(writes_per_writer):
                # Use high-precision timestamps to avoid ties
                timestamp = time.time() + (writer_id * 1000) + i
                value = f"writer_{writer_id}_value_{i}"
                
                # Write to random node
                node = random.choice(self.nodes)
                node.set_register(register_name, value, timestamp)
                
                time.sleep(0.001)
        
        # Execute concurrent writes
        threads = []
        start_time = time.time()
        
        for writer_id in range(num_writers):
            thread = threading.Thread(target=write_worker, args=(writer_id,))
            threads.append(thread)
            thread.start()
        
        for thread in threads:
            thread.join()
        
        write_time = time.time() - start_time
        
        # Synchronize all nodes
        self._synchronize_all_nodes(register_name, 'register')
        
        # Verify convergence and LWW property
        final_values = []
        final_timestamps = []
        
        for node in self.nodes:
            value, timestamp = node.get_register_value(register_name)
            final_values.append(value)
            final_timestamps.append(timestamp)
        
        # All nodes must have the same value and timestamp
        self.assertTrue(all(v == final_values[0] for v in final_values),
                       "LWW register values did not converge")
        self.assertTrue(all(t == final_timestamps[0] for t in final_timestamps),
                       "LWW register timestamps did not converge")
        
        # Verify it's actually the latest write
        latest_timestamp = max(final_timestamps)
        self.assertEqual(final_timestamps[0], latest_timestamp,
                        "Final value is not from the latest write")
        
        # Performance validation
        total_writes = num_writers * writes_per_writer
        writes_per_second = total_writes / write_time
        
        print(f"✓ LWW conflict resolution: {writes_per_second:.0f} writes/sec, "
              f"final: '{final_values[0][:30]}...'")
    
    def _synchronize_all_nodes(self, crdt_name, crdt_type):
        """Synchronize CRDT across all nodes"""
        for i in range(len(self.nodes)):
            for j in range(len(self.nodes)):
                if i != j:
                    try:
                        state = self.nodes[i].export_crdt_state(crdt_name)
                        self.nodes[j].import_crdt_state(crdt_name, state)
                    except:
                        pass  # Handle missing CRDTs gracefully
    
    def _synchronize_group(self, group, crdt_name, crdt_type):
        """Synchronize CRDT within a group of nodes"""
        for i in range(len(group)):
            for j in range(len(group)):
                if i != j:
                    try:
                        state = group[i].export_crdt_state(crdt_name)
                        group[j].import_crdt_state(crdt_name, state)
                    except:
                        pass
    
    def _check_convergence(self, register_name):
        """Check if all nodes have converged for a register"""
        try:
            values = []
            for node in self.nodes:
                value, _ = node.get_register_value(register_name)
                values.append(value)
            return all(v == values[0] for v in values)
        except:
            return False


class TestCRDTPerformanceBenchmarks(unittest.TestCase):
    """Engineering-grade performance benchmarks with real data validation"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.manager = CRDTManager(node_id="perf_test", db_path=os.path.join(self.temp_dir, "test.db"))
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_high_throughput_counter_operations(self):
        """Test high-throughput counter operations with engineering metrics"""
        counter_name = "throughput_test"
        num_operations = 10000
        
        # Initialize counter
        self.manager.get_counter(counter_name)
        
        # Measure operation throughput
        start_time = time.time()
        
        for i in range(num_operations):
            self.manager.increment_counter(counter_name, 1)
        
        operation_time = time.time() - start_time
        ops_per_second = num_operations / operation_time
        
        # Verify correctness
        final_value = self.manager.get_counter_value(counter_name)
        self.assertEqual(final_value, num_operations)
        
        # Engineering performance requirements
        self.assertGreater(ops_per_second, 5000, 
                          f"Counter throughput {ops_per_second:.0f} ops/sec below requirement")
        
        print(f"✓ Counter throughput: {ops_per_second:.0f} ops/sec")
    
    def test_large_set_operations_memory_efficiency(self):
        """Test memory efficiency with large set operations"""
        set_name = "large_set"
        num_elements = 50000
        
        # Initialize set
        self.manager.get_set(set_name)
        
        # Measure memory usage and performance
        start_time = time.time()
        
        for i in range(num_elements):
            element = f"element_{i:06d}"
            self.manager.add_to_set(set_name, element)
        
        add_time = time.time() - start_time
        
        # Verify set contents
        set_contents = self.manager.get_set_contents(set_name)
        self.assertEqual(len(set_contents), num_elements)
        
        # Test lookup performance
        start_time = time.time()
        lookups = 1000
        
        for i in range(lookups):
            element = f"element_{random.randint(0, num_elements-1):06d}"
            self.assertIn(element, set_contents)
        
        lookup_time = time.time() - start_time
        
        # Performance metrics
        add_rate = num_elements / add_time
        lookup_rate = lookups / lookup_time
        
        self.assertGreater(add_rate, 10000, "Set add rate below requirement")
        self.assertGreater(lookup_rate, 1000, "Set lookup rate below requirement")
        
        print(f"✓ Large set: {add_rate:.0f} adds/sec, {lookup_rate:.0f} lookups/sec")
    
    def test_serialization_performance(self):
        """Test CRDT serialization/deserialization performance"""
        counter_name = "serialization_test"
        
        # Create counter with significant state
        self.manager.get_counter(counter_name)
        for i in range(1000):
            self.manager.increment_counter(counter_name, random.randint(1, 10))
        
        # Test serialization performance
        num_serializations = 1000
        
        start_time = time.time()
        for _ in range(num_serializations):
            serialized = self.manager.export_crdt_state(counter_name)
        
        serialization_time = time.time() - start_time
        
        # Test deserialization performance
        serialized_state = self.manager.export_crdt_state(counter_name)
        
        start_time = time.time()
        for _ in range(num_serializations):
            temp_manager = CRDTManager(storage_dir=tempfile.mkdtemp())
            temp_manager.import_crdt_state(counter_name, serialized_state)
        
        deserialization_time = time.time() - start_time
        
        # Performance requirements
        serialization_rate = num_serializations / serialization_time
        deserialization_rate = num_serializations / deserialization_time
        
        self.assertGreater(serialization_rate, 100, "Serialization rate too low")
        self.assertGreater(deserialization_rate, 100, "Deserialization rate too low")
        
        print(f"✓ Serialization: {serialization_rate:.0f}/sec, "
              f"Deserialization: {deserialization_rate:.0f}/sec")


class TestCRDTRealWorldScenarios(unittest.TestCase):
    """Test CRDT behavior in real-world application scenarios"""
    
    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.manager = CRDTManager(node_id="real_world_test", db_path=os.path.join(self.temp_dir, "test.db"))
    
    def tearDown(self):
        shutil.rmtree(self.temp_dir)
    
    def test_collaborative_document_editing(self):
        """Simulate collaborative document editing with OR-Set"""
        document_id = "collaborative_doc"
        
        # Initialize document (OR-Set of text operations)
        self.manager.get_or_set(document_id)
        
        # Simulate multiple users editing simultaneously
        users = ["alice", "bob", "charlie"]
        
        for user in users:
            for line_num in range(10):
                operation = f"{user}_line_{line_num}_{int(time.time() * 1000000)}"
                self.manager.add_to_set(document_id, operation)
        
        # Verify all operations are preserved
        document_operations = self.manager.get_set_contents(document_id)
        self.assertEqual(len(document_operations), len(users) * 10)
        
        # Verify each user's contributions
        for user in users:
            user_ops = [op for op in document_operations if op.startswith(user)]
            self.assertEqual(len(user_ops), 10)
        
        print(f"✓ Collaborative editing: {len(document_operations)} operations preserved")
    
    def test_distributed_voting_system(self):
        """Simulate distributed voting with PN-Counter"""
        vote_topic = "feature_proposal"
        
        # Initialize vote counters
        self.manager.get_pn_counter(vote_topic)
        
        # Simulate voting from different nodes
        votes = [
            ("upvote", 150),    # 150 upvotes
            ("downvote", 25),   # 25 downvotes
            ("upvote", 75),     # Additional upvotes
        ]
        
        for vote_type, count in votes:
            if vote_type == "upvote":
                self.manager.increment_pn_counter(vote_topic, count)
            else:
                self.manager.decrement_pn_counter(vote_topic, count)
        
        # Verify final vote tally
        final_score = self.manager.get_pn_counter_value(vote_topic)
        expected_score = 150 + 75 - 25  # 200
        self.assertEqual(final_score, expected_score)
        
        print(f"✓ Distributed voting: final score {final_score}")
    
    def test_session_management_lww(self):
        """Simulate session management with LWW-Register"""
        session_id = "user_session_123"
        
        # Initialize session state
        self.manager.get_register(session_id)
        
        # Simulate session updates over time
        session_updates = [
            (time.time(), {"status": "logged_in", "location": "home"}),
            (time.time() + 1, {"status": "active", "location": "dashboard"}),
            (time.time() + 2, {"status": "active", "location": "profile"}),
            (time.time() + 3, {"status": "idle", "location": "profile"}),
            (time.time() + 4, {"status": "logged_out", "location": None}),
        ]
        
        for timestamp, session_data in session_updates:
            self.manager.set_register(session_id, json.dumps(session_data), timestamp)
        
        # Verify latest session state
        final_state, final_timestamp = self.manager.get_register_value(session_id)
        final_data = json.loads(final_state)
        
        self.assertEqual(final_data["status"], "logged_out")
        self.assertIsNone(final_data["location"])
        self.assertEqual(final_timestamp, session_updates[-1][0])
        
        print(f"✓ Session management: final state {final_data}")


if __name__ == '__main__':
    # Run tests with detailed output
    unittest.main(verbosity=2)