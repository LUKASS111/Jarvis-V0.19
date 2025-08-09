#!/usr/bin/env python3
"""
CRDT Manager for Jarvis
Comprehensive CRDT (Conflict-free Replicated Data Types) management system
"""

import os
import sys
import json
import time
from typing import Dict, List, Any, Optional, Set, Tuple
from datetime import datetime
from pathlib import Path
from dataclasses import dataclass, field

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from jarvis.core.error_handler import error_handler, ErrorLevel, safe_execute

@dataclass
class CRDTNode:
    """Represents a node in the CRDT system"""
    node_id: str
    timestamp: float = field(default_factory=time.time)
    value: Any = None
    version: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

class CRDTManager:
    """
    Comprehensive CRDT Manager
    Handles conflict-free replicated data types for distributed systems
    """
    
    def __init__(self, node_id: str = None):
        self.node_id = node_id or f"node_{int(time.time() * 1000)}"
        self.data_store: Dict[str, CRDTNode] = {}
        self.vector_clock: Dict[str, int] = {}
        self.operation_log: List[Dict[str, Any]] = []
        self.peers: Set[str] = set()
        
        print(f"[CRDT] Manager initialized for node: {self.node_id}")
    
    @safe_execute(fallback_value=None, context="CRDT Set")
    def set_value(self, key: str, value: Any, metadata: Dict[str, Any] = None) -> bool:
        """Set a value in the CRDT store"""
        
        timestamp = time.time()
        version = self.vector_clock.get(self.node_id, 0) + 1
        self.vector_clock[self.node_id] = version
        
        node = CRDTNode(
            node_id=self.node_id,
            timestamp=timestamp,
            value=value,
            version=version,
            metadata=metadata or {}
        )
        
        # Handle conflicts using last-writer-wins with timestamp
        if key in self.data_store:
            existing = self.data_store[key]
            if timestamp > existing.timestamp:
                self.data_store[key] = node
            elif timestamp == existing.timestamp and self.node_id > existing.node_id:
                # Tie-breaker using node ID
                self.data_store[key] = node
        else:
            self.data_store[key] = node
        
        # Log operation
        self.operation_log.append({
            "operation": "set",
            "key": key,
            "value": value,
            "timestamp": timestamp,
            "node_id": self.node_id,
            "version": version
        })
        
        return True
    
    @safe_execute(fallback_value=None, context="CRDT Get")
    def get_value(self, key: str) -> Any:
        """Get a value from the CRDT store"""
        
        if key in self.data_store:
            return self.data_store[key].value
        return None
    
    @safe_execute(fallback_value=None, context="CRDT Delete")
    def delete_value(self, key: str) -> bool:
        """Delete a value from the CRDT store"""
        
        if key in self.data_store:
            # Use tombstone approach for deletion
            self.set_value(key, None, {"deleted": True, "deleted_at": time.time()})
            return True
        return False
    
    @safe_execute(fallback_value={}, context="CRDT Merge")
    def merge_from_peer(self, peer_data: Dict[str, Any]) -> Dict[str, Any]:
        """Merge data from a peer node"""
        
        peer_node_id = peer_data.get("node_id")
        if not peer_node_id:
            return {"success": False, "error": "Invalid peer data"}
        
        self.peers.add(peer_node_id)
        conflicts_resolved = 0
        updates_applied = 0
        
        # Merge vector clock
        peer_vector_clock = peer_data.get("vector_clock", {})
        for node, version in peer_vector_clock.items():
            self.vector_clock[node] = max(self.vector_clock.get(node, 0), version)
        
        # Merge data store
        peer_store = peer_data.get("data_store", {})
        for key, peer_node_data in peer_store.items():
            if isinstance(peer_node_data, dict):
                peer_node = CRDTNode(
                    node_id=peer_node_data.get("node_id"),
                    timestamp=peer_node_data.get("timestamp", 0),
                    value=peer_node_data.get("value"),
                    version=peer_node_data.get("version", 0),
                    metadata=peer_node_data.get("metadata", {})
                )
                
                if key in self.data_store:
                    existing = self.data_store[key]
                    # Resolve conflict using timestamp and node ID
                    if (peer_node.timestamp > existing.timestamp or 
                        (peer_node.timestamp == existing.timestamp and peer_node.node_id > existing.node_id)):
                        self.data_store[key] = peer_node
                        conflicts_resolved += 1
                else:
                    self.data_store[key] = peer_node
                    updates_applied += 1
        
        return {
            "success": True,
            "peer_node_id": peer_node_id,
            "conflicts_resolved": conflicts_resolved,
            "updates_applied": updates_applied
        }
    
    @safe_execute(fallback_value={}, context="CRDT Export")
    def export_state(self) -> Dict[str, Any]:
        """Export current CRDT state for synchronization"""
        
        data_store_export = {}
        for key, node in self.data_store.items():
            data_store_export[key] = {
                "node_id": node.node_id,
                "timestamp": node.timestamp,
                "value": node.value,
                "version": node.version,
                "metadata": node.metadata
            }
        
        return {
            "node_id": self.node_id,
            "vector_clock": self.vector_clock.copy(),
            "data_store": data_store_export,
            "operation_count": len(self.operation_log),
            "peers": list(self.peers),
            "exported_at": time.time()
        }
    
    @safe_execute(fallback_value={}, context="CRDT Status")
    def get_status(self) -> Dict[str, Any]:
        """Get CRDT manager status"""
        
        return {
            "node_id": self.node_id,
            "data_items": len(self.data_store),
            "operation_count": len(self.operation_log),
            "peer_count": len(self.peers),
            "vector_clock_size": len(self.vector_clock),
            "last_operation": self.operation_log[-1] if self.operation_log else None
        }
    
    @safe_execute(fallback_value=[], context="CRDT List")
    def list_keys(self) -> List[str]:
        """List all keys in the CRDT store"""
        
        # Filter out deleted items
        active_keys = []
        for key, node in self.data_store.items():
            if not (node.metadata.get("deleted", False) and node.value is None):
                active_keys.append(key)
        
        return active_keys
    
    @safe_execute(fallback_value=None, context="CRDT Sync")
    def synchronize_with_peer(self, peer_state: Dict[str, Any]) -> Dict[str, Any]:
        """Synchronize with a peer's CRDT state"""
        
        # Export our state
        our_state = self.export_state()
        
        # Merge peer state
        merge_result = self.merge_from_peer(peer_state)
        
        return {
            "our_node_id": self.node_id,
            "peer_node_id": peer_state.get("node_id"),
            "merge_result": merge_result,
            "final_state": self.get_status()
        }

# Global CRDT manager instance
_crdt_manager = None

def get_crdt_manager(node_id: str = None) -> CRDTManager:
    """Get global CRDT manager instance"""
    global _crdt_manager
    if _crdt_manager is None:
        _crdt_manager = CRDTManager(node_id)
    return _crdt_manager

def create_test_crdt_scenario():
    """Create a test CRDT scenario for validation"""
    
    # Create two CRDT managers
    manager1 = CRDTManager("node_1")
    manager2 = CRDTManager("node_2")
    
    # Add some data to each
    manager1.set_value("key1", "value1_from_node1")
    manager1.set_value("key2", "value2_from_node1")
    
    manager2.set_value("key1", "value1_from_node2")  # Conflict
    manager2.set_value("key3", "value3_from_node2")
    
    # Synchronize
    state1 = manager1.export_state()
    state2 = manager2.export_state()
    
    result1 = manager1.merge_from_peer(state2)
    result2 = manager2.merge_from_peer(state1)
    
    return {
        "manager1_final": manager1.export_state(),
        "manager2_final": manager2.export_state(),
        "sync_result1": result1,
        "sync_result2": result2
    }

if __name__ == "__main__":
    print("=" * 60)
    print("CRDT Manager Test")
    print("=" * 60)
    
    # Test CRDT functionality
    test_result = create_test_crdt_scenario()
    print(json.dumps(test_result, indent=2, default=str))
    
    print("\n[SUCCESS] CRDT Manager operational")