"""
CRDT Implementation Tests
=========================

Test suite for CRDT mathematical properties and integration.
Validates convergence, commutativity, and architectural correctness.
"""

import unittest
import tempfile
import os
from jarvis.core.crdt import GCounter, GSet, LWWRegister
from jarvis.core.crdt_manager import CRDTManager


class TestGCounter(unittest.TestCase):
    """Test G-Counter CRDT implementation."""
    
    def test_increment_basic(self):
        """Test basic increment functionality."""
        counter = GCounter("node1")
        counter.increment(5)
        self.assertEqual(counter.value(), 5)
        
        counter.increment(3)
        self.assertEqual(counter.value(), 8)
    
    def test_increment_negative_raises_error(self):
        """Test that negative increments raise error."""
        counter = GCounter("node1")
        with self.assertRaises(ValueError):
            counter.increment(-1)
    
    def test_merge_convergence(self):
        """Test merge convergence property."""
        counter1 = GCounter("node1")
        counter2 = GCounter("node2")
        
        counter1.increment(3)
        counter2.increment(2)
        
        # Merge counter2 into counter1
        counter1.merge(counter2)
        self.assertEqual(counter1.value(), 5)
        
        # Create another counter and merge in reverse order
        counter3 = GCounter("node3")
        counter3.increment(2)  # Same as counter2
        counter4 = GCounter("node4")
        counter4.increment(3)  # Same as counter1
        
        counter3.merge(counter4)
        self.assertEqual(counter3.value(), 5)
    
    def test_merge_idempotent(self):
        """Test merge idempotence."""
        counter1 = GCounter("node1")
        counter2 = GCounter("node2")
        
        counter1.increment(3)
        counter2.increment(2)
        
        # First merge
        counter1.merge(counter2)
        original_value = counter1.value()
        
        # Second merge (should not change value)
        counter1.merge(counter2)
        self.assertEqual(counter1.value(), original_value)
    
    def test_serialization(self):
        """Test JSON serialization/deserialization."""
        counter = GCounter("node1")
        counter.increment(5)
        
        # Serialize to JSON
        json_str = counter.to_json()
        
        # Create new counter and deserialize
        new_counter = GCounter("node2")
        new_counter.from_json(json_str)
        
        self.assertEqual(new_counter.value(), 5)
        self.assertEqual(new_counter.node_id, "node1")


class TestGSet(unittest.TestCase):
    """Test G-Set CRDT implementation."""
    
    def test_add_basic(self):
        """Test basic add functionality."""
        gset = GSet("node1")
        gset.add("element1")
        gset.add("element2")
        
        self.assertTrue(gset.contains("element1"))
        self.assertTrue(gset.contains("element2"))
        self.assertFalse(gset.contains("element3"))
        self.assertEqual(gset.size(), 2)
    
    def test_add_duplicate(self):
        """Test adding duplicate elements."""
        gset = GSet("node1")
        gset.add("element1")
        gset.add("element1")  # Duplicate
        
        self.assertEqual(gset.size(), 1)
        self.assertTrue(gset.contains("element1"))
    
    def test_merge_convergence(self):
        """Test merge convergence property."""
        set1 = GSet("node1")
        set2 = GSet("node2")
        
        set1.add("a")
        set1.add("b")
        set2.add("b")
        set2.add("c")
        
        # Merge set2 into set1
        set1.merge(set2)
        
        # Should contain union of both sets
        self.assertTrue(set1.contains("a"))
        self.assertTrue(set1.contains("b"))
        self.assertTrue(set1.contains("c"))
        self.assertEqual(set1.size(), 3)
    
    def test_serialization(self):
        """Test JSON serialization/deserialization."""
        gset = GSet("node1")
        gset.add("element1")
        gset.add("element2")
        
        # Serialize to JSON
        json_str = gset.to_json()
        
        # Create new set and deserialize
        new_set = GSet("node2")
        new_set.from_json(json_str)
        
        self.assertEqual(new_set.size(), 2)
        self.assertTrue(new_set.contains("element1"))
        self.assertTrue(new_set.contains("element2"))


class TestLWWRegister(unittest.TestCase):
    """Test LWW-Register CRDT implementation."""
    
    def test_write_read_basic(self):
        """Test basic write/read functionality."""
        register = LWWRegister("node1")
        register.write("value1")
        
        self.assertEqual(register.read(), "value1")
        self.assertTrue(register.has_value())
    
    def test_merge_latest_wins(self):
        """Test that latest write wins during merge."""
        import time
        
        register1 = LWWRegister("node1")
        register2 = LWWRegister("node2")
        
        register1.write("old_value")
        time.sleep(0.001)  # Ensure timestamp difference
        register2.write("new_value")
        
        # Merge register2 into register1
        register1.merge(register2)
        
        # Should have the newer value
        self.assertEqual(register1.read(), "new_value")
    
    def test_merge_tie_breaker(self):
        """Test tie-breaker by node ID."""
        register1 = LWWRegister("node_a")
        register2 = LWWRegister("node_z")
        
        # Set same timestamp artificially
        timestamp = 1000000
        register1.write("value_a")
        register1.timestamp = timestamp
        register2.write("value_z")
        register2.timestamp = timestamp
        
        # Merge - lexicographically greater node ID should win
        register1.merge(register2)
        self.assertEqual(register1.read(), "value_z")
    
    def test_serialization(self):
        """Test JSON serialization/deserialization."""
        register = LWWRegister("node1")
        register.write("test_value")
        
        # Serialize to JSON
        json_str = register.to_json()
        
        # Create new register and deserialize
        new_register = LWWRegister("node2")
        new_register.from_json(json_str)
        
        self.assertEqual(new_register.read(), "test_value")
        self.assertEqual(new_register.get_writer(), "node1")


class TestCRDTManager(unittest.TestCase):
    """Test CRDT Manager integration."""
    
    def setUp(self):
        """Create temporary database for testing."""
        self.temp_db = tempfile.NamedTemporaryFile(delete=False)
        self.temp_db.close()
        self.manager = CRDTManager("test_node", self.temp_db.name)
    
    def tearDown(self):
        """Clean up temporary database."""
        os.unlink(self.temp_db.name)
    
    def test_counter_operations(self):
        """Test counter operations through manager."""
        # Increment counter
        value = self.manager.increment_counter("test_counter", 5)
        self.assertEqual(value, 5)
        
        # Increment again
        value = self.manager.increment_counter("test_counter", 3)
        self.assertEqual(value, 8)
        
        # Check value
        self.assertEqual(self.manager.get_counter_value("test_counter"), 8)
    
    def test_set_operations(self):
        """Test set operations through manager."""
        # Add elements
        was_new = self.manager.add_to_set("test_set", "element1")
        self.assertTrue(was_new)
        
        was_new = self.manager.add_to_set("test_set", "element1")  # Duplicate
        self.assertFalse(was_new)
        
        # Check membership
        self.assertTrue(self.manager.set_contains("test_set", "element1"))
        self.assertFalse(self.manager.set_contains("test_set", "element2"))
        
        # Check size
        self.assertEqual(self.manager.get_set_size("test_set"), 1)
    
    def test_register_operations(self):
        """Test register operations through manager."""
        # Write value
        value = self.manager.write_register("test_register", "test_value")
        self.assertEqual(value, "test_value")
        
        # Read value
        read_value = self.manager.read_register("test_register")
        self.assertEqual(read_value, "test_value")
        
        # Read non-existent with default
        default_value = self.manager.read_register("nonexistent", "default")
        self.assertEqual(default_value, "default")
    
    def test_persistence(self):
        """Test that CRDT states persist across manager instances."""
        # Create initial state
        self.manager.increment_counter("persistent_counter", 10)
        self.manager.add_to_set("persistent_set", "element1")
        self.manager.write_register("persistent_register", "persistent_value")
        
        # Create new manager with same database
        new_manager = CRDTManager("test_node", self.temp_db.name)
        
        # Check that state was restored
        self.assertEqual(new_manager.get_counter_value("persistent_counter"), 10)
        self.assertTrue(new_manager.set_contains("persistent_set", "element1"))
        self.assertEqual(new_manager.read_register("persistent_register"), "persistent_value")
    
    def test_health_metrics(self):
        """Test health metrics reporting."""
        self.manager.increment_counter("counter1", 1)
        self.manager.add_to_set("set1", "element")
        
        metrics = self.manager.get_health_metrics()
        
        self.assertEqual(metrics["total_crdts"], 2)
        self.assertEqual(metrics["node_id"], "test_node")
        self.assertEqual(metrics["system_status"], "operational")
        self.assertIn("counter1", metrics["crdt_types"])
        self.assertIn("set1", metrics["crdt_types"])


if __name__ == "__main__":
    unittest.main()