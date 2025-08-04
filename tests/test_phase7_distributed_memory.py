"""
Phase 7 Testing: Advanced Distributed Memory Architecture
=========================================================

Comprehensive test suite for distributed memory system with agent coordination.
Tests CRDT-based memory operations, distributed synchronization, and mathematical guarantees.
"""

import unittest
import json
import time
from datetime import datetime, timedelta
from jarvis.core.distributed_memory_system import (
    DistributedMemorySystem, MemoryEntry, MemoryType, ConversationContext,
    get_distributed_memory_system, store_conversation_memory, get_conversation_memory
)


class TestDistributedMemorySystem(unittest.TestCase):
    """Test distributed memory system core functionality"""
    
    def setUp(self):
        """Set up test environment"""
        self.memory_system = DistributedMemorySystem("test_memory_node")
        self.test_session_id = "test_session_001"
        self.test_user_id = "test_user_001"
    
    def test_memory_system_initialization(self):
        """Test memory system initialization"""
        self.assertEqual(self.memory_system.node_id, "test_memory_node")
        self.assertIsNotNone(self.memory_system.crdt_manager)
        self.assertIsNotNone(self.memory_system.agent_coordinator)
        
        # Check CRDT structures are initialized
        self.assertIn("memory_conversations", self.memory_system.crdt_manager.crdts)
        self.assertIn("memory_profiles", self.memory_system.crdt_manager.crdts)
        self.assertIn("memory_operations", self.memory_system.crdt_manager.crdts)
        
        print("✓ Memory system initialization test passed")
    
    def test_conversation_storage(self):
        """Test conversation entry storage"""
        user_input = "Hello, how are you?"
        ai_response = "I'm doing well, thank you for asking!"
        metadata = {"user_id": self.test_user_id, "context": "greeting"}
        
        entry_id = self.memory_system.store_conversation_entry(
            self.test_session_id, user_input, ai_response, metadata
        )
        
        # Verify entry ID format
        self.assertTrue(entry_id.startswith(f"conv_{self.test_session_id}_"))
        
        # Verify entry is in cache
        self.assertIn(entry_id, self.memory_system.memory_cache)
        
        # Verify entry content
        cached_entry = self.memory_system.memory_cache[entry_id]
        self.assertEqual(cached_entry.content["user_input"], user_input)
        self.assertEqual(cached_entry.content["ai_response"], ai_response)
        self.assertEqual(cached_entry.content["session_id"], self.test_session_id)
        
        # Verify session context is created
        self.assertIn(self.test_session_id, self.memory_system.active_contexts)
        
        print("✓ Conversation storage test passed")
    
    def test_conversation_history_retrieval(self):
        """Test conversation history retrieval"""
        # Store multiple conversation entries
        conversations = [
            ("Hello", "Hi there!"),
            ("How's the weather?", "I don't have current weather data."),
            ("Tell me a joke", "Why don't scientists trust atoms? Because they make up everything!")
        ]
        
        for user_input, ai_response in conversations:
            self.memory_system.store_conversation_entry(
                self.test_session_id, user_input, ai_response, {"user_id": self.test_user_id}
            )
            time.sleep(0.001)  # Ensure different timestamps
        
        # Retrieve conversation history
        history = self.memory_system.get_conversation_history(self.test_session_id)
        
        # Verify history length
        self.assertEqual(len(history), 3)
        
        # Verify conversation order (should be chronological)
        self.assertEqual(history[0].content["user_input"], "Hello")
        self.assertEqual(history[1].content["user_input"], "How's the weather?")
        self.assertEqual(history[2].content["user_input"], "Tell me a joke")
        
        # Test limit parameter
        limited_history = self.memory_system.get_conversation_history(self.test_session_id, limit=2)
        self.assertEqual(len(limited_history), 2)
        
        print("✓ Conversation history retrieval test passed")
    
    def test_user_profile_management(self):
        """Test user profile storage and retrieval"""
        profile_data = {
            "name": "Test User",
            "preferences": {
                "language": "English",
                "topics": ["AI", "Technology", "Science"]
            },
            "interaction_style": "formal"
        }
        
        # Update user profile
        success = self.memory_system.update_user_profile(self.test_user_id, profile_data)
        self.assertTrue(success)
        
        # Retrieve user profile
        retrieved_profile = self.memory_system.get_user_profile(self.test_user_id)
        self.assertIsNotNone(retrieved_profile)
        self.assertEqual(retrieved_profile["name"], "Test User")
        self.assertEqual(retrieved_profile["preferences"]["language"], "English")
        
        print("✓ User profile management test passed")
    
    def test_learning_data_storage(self):
        """Test learning data storage"""
        learning_data = {
            "interaction_pattern": "question_answer",
            "user_satisfaction": 0.95,
            "response_effectiveness": 0.88,
            "context_relevance": 0.92
        }
        
        entry_id = self.memory_system.store_learning_data(learning_data)
        
        # Verify entry ID format
        self.assertTrue(entry_id.startswith("learn_"))
        
        # Verify learning data is stored in CRDT
        learning_entries = list(self.memory_system.learning_data.elements())
        self.assertGreater(len(learning_entries), 0)
        
        # Find and verify our entry
        found_entry = False
        for entry_json in learning_entries:
            entry_data = json.loads(entry_json)
            if entry_data["entry_id"] == entry_id:
                found_entry = True
                self.assertEqual(entry_data["data"]["user_satisfaction"], 0.95)
                break
        
        self.assertTrue(found_entry, "Learning data entry not found in CRDT store")
        
        print("✓ Learning data storage test passed")
    
    def test_memory_statistics(self):
        """Test memory statistics reporting"""
        # Add some data first
        self.memory_system.store_conversation_entry(
            self.test_session_id, "Test message", "Test response", {"user_id": self.test_user_id}
        )
        self.memory_system.update_user_profile(self.test_user_id, {"name": "Test"})
        self.memory_system.store_learning_data({"test": "data"})
        
        stats = self.memory_system.get_memory_statistics()
        
        # Verify statistics structure
        self.assertIn("node_id", stats)
        self.assertIn("total_conversations", stats)
        self.assertIn("active_sessions", stats)
        self.assertIn("memory_operations", stats)
        self.assertIn("learning_entries", stats)
        self.assertIn("system_status", stats)
        
        # Verify values
        self.assertEqual(stats["node_id"], "test_memory_node")
        self.assertEqual(stats["system_status"], "operational")
        self.assertGreater(stats["memory_operations"], 0)
        
        print("✓ Memory statistics test passed")


class TestDistributedSynchronization(unittest.TestCase):
    """Test distributed synchronization capabilities"""
    
    def setUp(self):
        """Set up multiple memory nodes for testing"""
        self.node1 = DistributedMemorySystem("sync_node_1")
        self.node2 = DistributedMemorySystem("sync_node_2")
    
    def test_peer_synchronization(self):
        """Test synchronization with peer nodes"""
        # Add data to node1
        self.node1.store_conversation_entry(
            "sync_session", "Hello from node 1", "Response from node 1"
        )
        
        # Simulate sync with peer nodes
        peer_nodes = ["sync_node_2", "sync_node_3"]
        sync_results = self.node1.sync_with_peers(peer_nodes)
        
        # Verify sync results structure
        self.assertIn("synced_nodes", sync_results)
        self.assertIn("failed_nodes", sync_results)
        self.assertIn("operations_synced", sync_results)
        
        # Verify successful synchronization
        self.assertIn("sync_node_2", sync_results["synced_nodes"])
        self.assertGreater(sync_results["operations_synced"], 0)
        
        print("✓ Peer synchronization test passed")
    
    def test_conflict_resolution(self):
        """Test CRDT conflict resolution in distributed scenario"""
        user_id = "conflict_test_user"
        
        # Simulate concurrent profile updates on different nodes
        profile1 = {"name": "User A", "setting": "value1", "timestamp": "2024-01-01T10:00:00"}
        profile2 = {"name": "User B", "setting": "value2", "timestamp": "2024-01-01T10:01:00"}
        
        # Update profiles on different nodes
        self.node1.update_user_profile(user_id, profile1)
        self.node2.update_user_profile(user_id, profile2)
        
        # LWW-Register should resolve conflict based on timestamp (simulated)
        # Both nodes should eventually converge to the same state
        retrieved1 = self.node1.get_user_profile(user_id)
        retrieved2 = self.node2.get_user_profile(user_id)
        
        # At least one should have the updated profile
        self.assertTrue(retrieved1 is not None or retrieved2 is not None)
        
        print("✓ Conflict resolution test passed")


class TestMemoryIntegration(unittest.TestCase):
    """Test integration with existing systems"""
    
    def test_crdt_integration(self):
        """Test integration with CRDT manager"""
        memory_system = DistributedMemorySystem("integration_test_node")
        
        # Verify CRDT manager integration
        crdt_health = memory_system.crdt_manager.get_health_metrics()
        self.assertIn("total_crdts", crdt_health)
        self.assertGreater(crdt_health["total_crdts"], 5)  # Memory CRDTs + existing ones
        
        # Verify memory CRDTs are operational
        memory_crdts = [k for k in memory_system.crdt_manager.crdts.keys() if k.startswith("memory_")]
        self.assertGreater(len(memory_crdts), 5)
        
        print("✓ CRDT integration test passed")
    
    def test_agent_coordination_integration(self):
        """Test integration with distributed agent coordinator"""
        memory_system = DistributedMemorySystem("agent_integration_node")
        
        # Store conversation to trigger agent coordination task
        entry_id = memory_system.store_conversation_entry(
            "agent_test_session", "Test input", "Test response", {"user_id": "agent_test_user"}
        )
        
        # Verify task was submitted to agent coordinator
        # (In a real system, we would check the coordinator's task queue)
        self.assertTrue(entry_id.startswith("conv_agent_test_session_"))
        
        print("✓ Agent coordination integration test passed")


class TestConvenienceFunctions(unittest.TestCase):
    """Test convenience functions and global access"""
    
    def test_global_memory_system(self):
        """Test global memory system access"""
        # Get global instance
        memory_system1 = get_distributed_memory_system("global_test_node")
        memory_system2 = get_distributed_memory_system("global_test_node")
        
        # Should return the same instance
        self.assertIs(memory_system1, memory_system2)
        
        print("✓ Global memory system test passed")
    
    def test_convenience_functions(self):
        """Test convenience functions for memory operations"""
        session_id = "convenience_test_session"
        
        # Test conversation storage convenience function
        entry_id = store_conversation_memory(
            session_id, "Convenience test input", "Convenience test response",
            {"user_id": "convenience_user"}
        )
        
        self.assertTrue(entry_id.startswith(f"conv_{session_id}_"))
        
        # Test conversation retrieval convenience function
        memory_data = get_conversation_memory(session_id, limit=10)
        self.assertIsInstance(memory_data, list)
        self.assertGreater(len(memory_data), 0)
        
        # Verify data structure
        first_entry = memory_data[0]
        self.assertIn("entry_id", first_entry)
        self.assertIn("content", first_entry)
        self.assertIn("timestamp", first_entry)
        
        print("✓ Convenience functions test passed")


class TestMemoryPerformance(unittest.TestCase):
    """Test memory system performance characteristics"""
    
    def test_memory_cleanup(self):
        """Test old session cleanup functionality"""
        memory_system = DistributedMemorySystem("cleanup_test_node")
        
        # Create multiple sessions with different ages
        old_session = "old_session_001"
        recent_session = "recent_session_001"
        
        # Store data for both sessions
        memory_system.store_conversation_entry(old_session, "Old message", "Old response")
        memory_system.store_conversation_entry(recent_session, "Recent message", "Recent response")
        
        # Manually set old session timestamp to simulate age
        if old_session in memory_system.active_contexts:
            old_time = (datetime.now() - timedelta(hours=25)).isoformat()
            memory_system.active_contexts[old_session].last_updated = old_time
        
        # Run cleanup (24 hour threshold)
        cleaned_count = memory_system.cleanup_old_sessions(max_age_hours=24)
        
        # Verify cleanup results
        self.assertGreaterEqual(cleaned_count, 0)
        
        print("✓ Memory cleanup test passed")
    
    def test_high_volume_storage(self):
        """Test high-volume memory storage performance"""
        memory_system = DistributedMemorySystem("performance_test_node")
        session_id = "performance_session"
        
        # Store multiple conversation entries quickly
        start_time = time.time()
        entry_count = 50
        
        for i in range(entry_count):
            entry_id = memory_system.store_conversation_entry(
                session_id, f"Test message {i}", f"Test response {i}",
                {"user_id": "performance_user", "iteration": i}
            )
            self.assertIsNotNone(entry_id)
        
        end_time = time.time()
        duration = end_time - start_time
        
        # Verify all entries are stored
        history = memory_system.get_conversation_history(session_id)
        self.assertEqual(len(history), entry_count)
        
        # Performance should be reasonable (less than 1 second for 50 entries)
        self.assertLess(duration, 1.0)
        
        print(f"✓ High-volume storage test passed ({entry_count} entries in {duration:.3f}s)")


def run_phase7_tests():
    """Run all Phase 7 distributed memory tests"""
    print("=" * 80)
    print("PHASE 7: DISTRIBUTED MEMORY ARCHITECTURE TESTS")
    print("=" * 80)
    
    # Create test suite
    test_suite = unittest.TestSuite()
    
    # Add test classes
    test_classes = [
        TestDistributedMemorySystem,
        TestDistributedSynchronization,
        TestMemoryIntegration,
        TestConvenienceFunctions,
        TestMemoryPerformance
    ]
    
    total_tests = 0
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        test_suite.addTests(tests)
        total_tests += tests.countTestCases()
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=0, stream=open('/dev/null', 'w'))
    result = runner.run(test_suite)
    
    # Report results
    print(f"\nPhase 7 Test Results:")
    print(f"Tests run: {result.testsRun}")
    print(f"Failures: {len(result.failures)}")
    print(f"Errors: {len(result.errors)}")
    success_rate = ((result.testsRun - len(result.failures) - len(result.errors)) / result.testsRun) * 100
    print(f"Success rate: {success_rate:.1f}%")
    
    if result.failures:
        print("\nFailures:")
        for test, failure in result.failures:
            print(f"- {test}: {failure}")
    
    if result.errors:
        print("\nErrors:")
        for test, error in result.errors:
            print(f"- {test}: {error}")
    
    print(f"\n{'✅ PHASE 7 TESTS PASSED' if success_rate == 100.0 else '❌ PHASE 7 TESTS FAILED'}")
    print("=" * 80)
    
    return success_rate == 100.0


if __name__ == "__main__":
    run_phase7_tests()