#!/usr/bin/env python3
"""
Test suite for CRDT Phase 4 - Integration features
Network synchronization and conflict resolution testing
"""

import unittest
import time
import threading
import json
import sys
import os
from datetime import datetime, timedelta
from unittest.mock import Mock, patch

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis.core.crdt.crdt_network import (
    CRDTNetworkManager, CRDTSynchronizer, PeerInfo, SyncMessage
)
from jarvis.core.crdt.crdt_conflict_resolver import (
    CRDTConflictResolver, ConflictEvent, ConflictType, ResolutionStrategy, ResolutionRule
)


class TestCRDTNetwork(unittest.TestCase):
    """Test CRDT network synchronization"""
    
    def setUp(self):
        """Setup test environment"""
        self.node_id = "test_node_network"
        self.network_manager = CRDTNetworkManager(self.node_id, port=8890)
    
    def tearDown(self):
        """Cleanup test environment"""
        if self.network_manager.running:
            self.network_manager.stop()
    
    def test_network_manager_initialization(self):
        """Test network manager initialization"""
        self.assertEqual(self.network_manager.node_id, self.node_id)
        self.assertEqual(self.network_manager.port, 8890)
        self.assertFalse(self.network_manager.running)
        self.assertEqual(len(self.network_manager.peers), 0)
    
    def test_peer_info_creation(self):
        """Test peer information handling"""
        peer = PeerInfo(
            node_id="peer_1",
            address="192.168.1.100",
            port=8888,
            last_seen=datetime.utcnow()
        )
        
        self.assertEqual(peer.node_id, "peer_1")
        self.assertEqual(peer.address, "192.168.1.100")
        self.assertEqual(peer.port, 8888)
        self.assertIsInstance(peer.capabilities, list)
    
    def test_sync_message_serialization(self):
        """Test sync message serialization"""
        message = SyncMessage(
            message_id="test_msg_001",
            message_type="sync_request",
            source_node="node_1",
            target_node="node_2",
            timestamp=datetime.utcnow(),
            crdt_name="test_crdt",
            data={"test": "data"}
        )
        
        # Test serialization
        json_str = message.to_json()
        self.assertIsInstance(json_str, str)
        
        # Test deserialization
        restored_message = SyncMessage.from_json(json_str)
        self.assertEqual(restored_message.message_id, message.message_id)
        self.assertEqual(restored_message.message_type, message.message_type)
        self.assertEqual(restored_message.source_node, message.source_node)
        self.assertEqual(restored_message.data, message.data)
    
    def test_network_status(self):
        """Test network status reporting"""
        status = self.network_manager.get_network_status()
        
        expected_keys = [
            "node_id", "port", "running", "peer_count", 
            "active_connections", "peers"
        ]
        
        for key in expected_keys:
            self.assertIn(key, status)
        
        self.assertEqual(status["node_id"], self.node_id)
        self.assertEqual(status["port"], 8890)
        self.assertFalse(status["running"])
    
    def test_message_handler_setup(self):
        """Test message handler registration"""
        expected_handlers = [
            "sync_request", "sync_response", "delta", 
            "heartbeat", "peer_discovery", "peer_announcement"
        ]
        
        for handler_type in expected_handlers:
            self.assertIn(handler_type, self.network_manager.message_handlers)
            self.assertIsNotNone(self.network_manager.message_handlers[handler_type])


class TestCRDTSynchronizer(unittest.TestCase):
    """Test CRDT synchronization coordinator"""
    
    def setUp(self):
        """Setup test environment"""
        self.network_manager = Mock()
        self.crdt_manager = Mock()
        self.synchronizer = CRDTSynchronizer(self.network_manager, self.crdt_manager)
    
    def test_synchronizer_initialization(self):
        """Test synchronizer initialization"""
        self.assertEqual(self.synchronizer.network_manager, self.network_manager)
        self.assertEqual(self.synchronizer.crdt_manager, self.crdt_manager)
        self.assertIsInstance(self.synchronizer.sync_intervals, dict)
        self.assertIsInstance(self.synchronizer.default_intervals, dict)
    
    def test_crdt_registration(self):
        """Test CRDT registration for synchronization"""
        crdt_name = "test_counter"
        priority = "high"
        
        self.synchronizer.register_crdt_for_sync(crdt_name, priority)
        
        self.assertIn(crdt_name, self.synchronizer.sync_priorities)
        self.assertEqual(self.synchronizer.sync_priorities[crdt_name], priority)
        self.assertIn(crdt_name, self.synchronizer.sync_intervals)
        self.assertEqual(
            self.synchronizer.sync_intervals[crdt_name], 
            self.synchronizer.default_intervals[priority]
        )
    
    def test_sync_status_reporting(self):
        """Test sync status reporting"""
        # Register some CRDTs
        self.synchronizer.register_crdt_for_sync("counter1", "high")
        self.synchronizer.register_crdt_for_sync("set1", "normal")
        
        status = self.synchronizer.get_sync_status()
        
        expected_keys = [
            "registered_crdts", "sync_intervals", "last_sync_times",
            "priorities", "network_status"
        ]
        
        for key in expected_keys:
            self.assertIn(key, status)
        
        self.assertIn("counter1", status["registered_crdts"])
        self.assertIn("set1", status["registered_crdts"])


class TestCRDTConflictResolver(unittest.TestCase):
    """Test CRDT conflict resolution system"""
    
    def setUp(self):
        """Setup test environment"""
        self.node_id = "test_node_resolver"
        self.resolver = CRDTConflictResolver(self.node_id)
    
    def test_resolver_initialization(self):
        """Test conflict resolver initialization"""
        self.assertEqual(self.resolver.node_id, self.node_id)
        self.assertIsInstance(self.resolver.active_conflicts, dict)
        self.assertIsInstance(self.resolver.resolved_conflicts, list)
        self.assertIsInstance(self.resolver.resolution_rules, list)
        
        # Should have default rules
        self.assertGreater(len(self.resolver.resolution_rules), 0)
    
    def test_default_resolution_rules(self):
        """Test default resolution rules setup"""
        rule_ids = [rule.rule_id for rule in self.resolver.resolution_rules]
        
        expected_rules = [
            "config_lww", "counter_merge", 
            "high_priority_manual", "access_control_auto"
        ]
        
        for expected_rule in expected_rules:
            self.assertIn(expected_rule, rule_ids)
    
    def test_conflict_detection_business_logic(self):
        """Test business logic conflict detection"""
        operation1 = {
            "operation_id": "op_001",
            "node_id": "node_1",
            "operation": "archive_data",
            "entry_id": "entry_123",
            "timestamp": time.time()
        }
        
        operation2 = {
            "operation_id": "op_002", 
            "node_id": "node_2",
            "operation": "purge_data",
            "entry_id": "entry_123",
            "timestamp": time.time() + 1
        }
        
        conflict = self.resolver.detect_semantic_conflict(
            "archive_entries", operation1, operation2
        )
        
        self.assertIsNotNone(conflict)
        self.assertEqual(conflict.conflict_type, ConflictType.BUSINESS_LOGIC)
        self.assertEqual(len(conflict.involved_nodes), 2)
        self.assertEqual(len(conflict.conflicting_operations), 2)
    
    def test_conflict_detection_no_conflict(self):
        """Test no conflict detection for compatible operations"""
        operation1 = {
            "operation_id": "op_001",
            "node_id": "node_1", 
            "operation": "archive_data",
            "entry_id": "entry_123",
            "timestamp": time.time()
        }
        
        operation2 = {
            "operation_id": "op_002",
            "node_id": "node_2",
            "operation": "archive_data",
            "entry_id": "entry_456",  # Different entry
            "timestamp": time.time() + 1
        }
        
        conflict = self.resolver.detect_semantic_conflict(
            "archive_entries", operation1, operation2
        )
        
        self.assertIsNone(conflict)
    
    def test_last_write_wins_resolution(self):
        """Test last-write-wins conflict resolution"""
        operations = [
            {
                "operation_id": "op_001",
                "timestamp": 1000,
                "value": "current_value"
            },
            {
                "operation_id": "op_002", 
                "timestamp": 2000,
                "value": "new_value"
            }
        ]
        
        result = self.resolver._resolve_last_write_wins(operations)
        
        self.assertTrue(result.success)
        self.assertEqual(result.result["strategy"], "last_write_wins")
        self.assertEqual(result.result["winning_operation"]["value"], "new_value")
    
    def test_merge_values_resolution_numeric(self):
        """Test merge values resolution for numeric values"""
        operations = [
            {"operation_id": "op_001", "value": 10},
            {"operation_id": "op_002", "value": 20},
            {"operation_id": "op_003", "value": 30}
        ]
        
        result = self.resolver._resolve_merge_values(operations)
        
        self.assertTrue(result.success)
        self.assertEqual(result.result["strategy"], "merge_values")
        self.assertEqual(result.result["merged_value"], 60)
    
    def test_merge_values_resolution_sets(self):
        """Test merge values resolution for set values"""
        operations = [
            {"operation_id": "op_001", "value": [1, 2, 3]},
            {"operation_id": "op_002", "value": [3, 4, 5]},
            {"operation_id": "op_003", "value": [5, 6, 7]}
        ]
        
        result = self.resolver._resolve_merge_values(operations)
        
        self.assertTrue(result.success)
        self.assertEqual(result.result["strategy"], "merge_values")
        merged_set = set(result.result["merged_value"])
        expected_set = {1, 2, 3, 4, 5, 6, 7}
        self.assertEqual(merged_set, expected_set)
    
    def test_highest_priority_resolution(self):
        """Test highest priority conflict resolution"""
        operations = [
            {"operation_id": "op_001", "priority": "normal", "value": "normal_op"},
            {"operation_id": "op_002", "priority": "high", "value": "high_op"},
            {"operation_id": "op_003", "priority": "low", "value": "low_op"}
        ]
        
        result = self.resolver._resolve_highest_priority(operations)
        
        self.assertTrue(result.success)
        self.assertEqual(result.result["strategy"], "highest_priority")
        self.assertEqual(result.result["winning_operation"]["value"], "high_op")
    
    def test_resolution_rule_matching(self):
        """Test resolution rule matching"""
        rule = ResolutionRule(
            rule_id="test_rule",
            conflict_type=ConflictType.SEMANTIC,
            conditions={"crdt_name_pattern": "config"},
            strategy=ResolutionStrategy.LAST_WRITE_WINS,
            priority=100
        )
        
        # Test matching conflict
        matching_conflict = ConflictEvent(
            conflict_id="test_conflict",
            conflict_type=ConflictType.SEMANTIC,
            crdt_name="config_settings",
            involved_nodes=["node1", "node2"],
            conflicting_operations=[],
            detection_time=datetime.utcnow()
        )
        
        self.assertTrue(rule.matches(matching_conflict))
        
        # Test non-matching conflict
        non_matching_conflict = ConflictEvent(
            conflict_id="test_conflict",
            conflict_type=ConflictType.BUSINESS_LOGIC,  # Different type
            crdt_name="config_settings",
            involved_nodes=["node1", "node2"],
            conflicting_operations=[],
            detection_time=datetime.utcnow()
        )
        
        self.assertFalse(rule.matches(non_matching_conflict))
    
    def test_manual_conflict_resolution(self):
        """Test manual conflict resolution"""
        # Create a conflict
        conflict = ConflictEvent(
            conflict_id="manual_conflict",
            conflict_type=ConflictType.BUSINESS_LOGIC,
            crdt_name="test_crdt",
            involved_nodes=["node1", "node2"],
            conflicting_operations=[
                {"operation_id": "op_001", "value": "value1"},
                {"operation_id": "op_002", "value": "value2"}
            ],
            detection_time=datetime.utcnow()
        )
        
        self.resolver.active_conflicts[conflict.conflict_id] = conflict
        
        # Manually resolve
        resolution = {"chosen_operation": "op_002", "reason": "Business requirements"}
        result = self.resolver.manual_resolve_conflict(conflict.conflict_id, resolution)
        
        self.assertTrue(result.success)
        self.assertNotIn(conflict.conflict_id, self.resolver.active_conflicts)
        self.assertEqual(len(self.resolver.resolved_conflicts), 1)
        
        resolved_conflict = self.resolver.resolved_conflicts[0]
        self.assertEqual(resolved_conflict.resolution_strategy, ResolutionStrategy.MANUAL_INTERVENTION)
        self.assertEqual(resolved_conflict.resolution_details, resolution)
    
    def test_conflict_statistics(self):
        """Test conflict statistics collection"""
        # Add some test conflicts
        conflict1 = ConflictEvent(
            conflict_id="conflict_1",
            conflict_type=ConflictType.SEMANTIC,
            crdt_name="test_crdt",
            involved_nodes=["node1"],
            conflicting_operations=[],
            detection_time=datetime.utcnow()
        )
        
        conflict2 = ConflictEvent(
            conflict_id="conflict_2",
            conflict_type=ConflictType.BUSINESS_LOGIC,
            crdt_name="test_crdt",
            involved_nodes=["node2"],
            conflicting_operations=[],
            detection_time=datetime.utcnow(),
            resolution_time=datetime.utcnow(),
            resolution_strategy=ResolutionStrategy.LAST_WRITE_WINS
        )
        
        self.resolver.active_conflicts[conflict1.conflict_id] = conflict1
        self.resolver.resolved_conflicts.append(conflict2)
        self.resolver.conflict_stats["total_detected"] = 2
        self.resolver.conflict_stats["total_resolved"] = 1
        
        stats = self.resolver.get_conflict_statistics()
        
        self.assertIn("statistics", stats)
        self.assertIn("active_conflicts", stats)
        self.assertIn("conflicts_by_type", stats)
        self.assertEqual(stats["active_conflicts"], 1)
        self.assertEqual(stats["statistics"]["total_detected"], 2)
        self.assertEqual(stats["statistics"]["total_resolved"], 1)
    
    def test_add_remove_resolution_rules(self):
        """Test adding and removing resolution rules"""
        initial_count = len(self.resolver.resolution_rules)
        
        # Add a custom rule
        custom_rule = ResolutionRule(
            rule_id="custom_test_rule",
            conflict_type=ConflictType.SEMANTIC,
            conditions={"test": "condition"},
            strategy=ResolutionStrategy.MERGE_VALUES,
            priority=50
        )
        
        self.resolver.add_resolution_rule(custom_rule)
        self.assertEqual(len(self.resolver.resolution_rules), initial_count + 1)
        
        # Remove the rule
        success = self.resolver.remove_resolution_rule("custom_test_rule")
        self.assertTrue(success)
        self.assertEqual(len(self.resolver.resolution_rules), initial_count)
        
        # Try to remove non-existent rule
        success = self.resolver.remove_resolution_rule("non_existent_rule")
        self.assertFalse(success)


class TestCRDTIntegrationPhase4(unittest.TestCase):
    """Test Phase 4 integration features"""
    
    def test_network_and_resolver_integration(self):
        """Test integration between network manager and conflict resolver"""
        network_manager = CRDTNetworkManager("integration_test_node", port=8891)
        resolver = CRDTConflictResolver("integration_test_node")
        
        # Test that both components can work together
        self.assertEqual(network_manager.node_id, resolver.node_id)
        
        # Test network status includes resolver-relevant information
        network_status = network_manager.get_network_status()
        resolver_stats = resolver.get_conflict_statistics()
        
        self.assertIsInstance(network_status, dict)
        self.assertIsInstance(resolver_stats, dict)
        
        # Cleanup
        if network_manager.running:
            network_manager.stop()
    
    def test_phase_4_module_imports(self):
        """Test that all Phase 4 modules can be imported without errors"""
        try:
            from jarvis.core.crdt.crdt_network import CRDTNetworkManager, CRDTSynchronizer
            from jarvis.core.crdt.crdt_conflict_resolver import CRDTConflictResolver
            
            # Test instantiation
            network_manager = CRDTNetworkManager("test_node")
            resolver = CRDTConflictResolver("test_node")
            
            self.assertIsNotNone(network_manager)
            self.assertIsNotNone(resolver)
            
        except ImportError as e:
            self.fail(f"Phase 4 module import failed: {e}")


if __name__ == '__main__':
    # Run the tests
    unittest.main(verbosity=2)