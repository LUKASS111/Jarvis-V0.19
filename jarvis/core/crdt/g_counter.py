"""
Grow-only Counter (G-Counter) CRDT
==================================

Monotonic counter supporting only increment operations.
Conflict-free merging across distributed nodes.

Use cases:
- Health score aggregation
- Operation counting
- System statistics
- Event tracking
"""

from typing import Dict, Any
from .crdt_base import BaseCRDT


class GCounter(BaseCRDT):
    """
    Grow-only Counter CRDT implementation.
    
    Mathematical guarantees:
    - Monotonic: Value never decreases
    - Convergent: All nodes reach same final count
    - Commutative: Merge order doesn't matter
    """
    
    def __init__(self, node_id: str):
        """Initialize G-Counter with node ID."""
        super().__init__(node_id)
        self.vector = {node_id: 0}  # node_id -> count mapping
    
    def increment(self, amount: int = 1) -> None:
        """
        Increment counter for this node.
        
        Args:
            amount: Positive increment value
        """
        if amount < 0:
            raise ValueError("G-Counter only supports positive increments")
        
        self.vector[self.node_id] = self.vector.get(self.node_id, 0) + amount
        self.update_metadata()
    
    def merge(self, other: 'GCounter') -> None:
        """
        Merge with another G-Counter.
        Takes maximum value for each node (convergent).
        """
        for node_id, count in other.vector.items():
            current_count = self.vector.get(node_id, 0)
            self.vector[node_id] = max(current_count, count)
        
        self.update_metadata()
    
    def value(self) -> int:
        """Get total count across all nodes."""
        return sum(self.vector.values())
    
    def get_node_count(self, node_id: str) -> int:
        """Get count for specific node."""
        return self.vector.get(node_id, 0)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "vector": self.vector,
            "metadata": self.get_metadata()
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Deserialize from dictionary."""
        self.vector = data["vector"]
        metadata = data["metadata"]
        self.node_id = metadata["node_id"]
        self.created_at = metadata["created_at"]
        self.last_updated = metadata["last_updated"]
        self.version = metadata["version"]
    
    def __str__(self) -> str:
        return f"GCounter(value={self.value()}, nodes={len(self.vector)})"
    
    def __repr__(self) -> str:
        return f"GCounter(node_id='{self.node_id}', vector={self.vector})"