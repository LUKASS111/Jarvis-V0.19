"""
PN-Counter (Positive-Negative Counter) CRDT Implementation
=========================================================

Provides increment/decrement semantics with conflict-free merging.
Combines two G-Counters to support both positive and negative operations.
"""

import time
from typing import Dict, Any
from .crdt_base import BaseCRDT
from .g_counter import GCounter


class PNCounter(BaseCRDT):
    """
    Positive-Negative Counter CRDT implementation.
    
    Supports both increment and decrement operations by combining
    two G-Counters (one for positive, one for negative operations).
    """
    
    def __init__(self, node_id: str = None):
        super().__init__(node_id)
        self.p_counter = GCounter(node_id)  # Positive increments
        self.n_counter = GCounter(node_id)  # Negative increments (stored as positive)
    
    def increment(self, amount: int = 1) -> None:
        """
        Increment the counter.
        
        Args:
            amount: Amount to increment (must be positive)
            
        Raises:
            ValueError: If amount is not positive
        """
        if amount <= 0:
            raise ValueError("Increment amount must be positive")
        
        self.p_counter.increment(amount)
    
    def decrement(self, amount: int = 1) -> None:
        """
        Decrement the counter.
        
        Args:
            amount: Amount to decrement (must be positive)
            
        Raises:
            ValueError: If amount is not positive
        """
        if amount <= 0:
            raise ValueError("Decrement amount must be positive")
        
        self.n_counter.increment(amount)
    
    def value(self) -> int:
        """
        Get the current counter value.
        
        Returns:
            int: Current value (positive increments - negative increments)
        """
        return self.p_counter.value() - self.n_counter.value()
    
    def merge(self, other: 'PNCounter') -> None:
        """
        Merge another PN-Counter into this one.
        
        Args:
            other: Other PN-Counter to merge
            
        Raises:
            TypeError: If other is not a PNCounter
        """
        if not isinstance(other, PNCounter):
            raise TypeError("Can only merge with another PNCounter")
        
        self.p_counter.merge(other.p_counter)
        self.n_counter.merge(other.n_counter)
    
    def positive_value(self) -> int:
        """
        Get the total positive increments.
        
        Returns:
            int: Sum of all positive increments
        """
        return self.p_counter.value()
    
    def negative_value(self) -> int:
        """
        Get the total negative decrements.
        
        Returns:
            int: Sum of all decrements (as positive number)
        """
        return self.n_counter.value()
    
    def to_dict(self) -> Dict:
        """
        Serialize to dictionary for storage/transmission.
        
        Returns:
            Dict: Serializable representation
        """
        return {
            'type': 'pn_counter',
            'node_id': self.node_id,
            'p_counter': self.p_counter.to_dict(),
            'n_counter': self.n_counter.to_dict(),
            'timestamp': time.time()
        }
    
    @classmethod
    def from_dict_cls(cls, data: Dict) -> 'PNCounter':
        """
        Deserialize from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            PNCounter: Reconstructed PN-Counter
        """
        if data.get('type') != 'pn_counter':
            raise ValueError("Invalid data type for PN-Counter")
        
        counter = cls(data.get('node_id'))
        counter.p_counter.from_dict(data.get('p_counter', {}))
        counter.n_counter.from_dict(data.get('n_counter', {}))
        
        return counter
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Update this instance from dictionary (for base class compatibility).
        
        Args:
            data: Dictionary representation
        """
        if data.get('type') != 'pn_counter':
            raise ValueError("Invalid data type for PN-Counter")
        
        # Update counters
        self.p_counter.from_dict(data.get('p_counter', {}))
        self.n_counter.from_dict(data.get('n_counter', {}))
    
    
    def get_metadata(self) -> Dict:
        """
        Get metadata about the PN-Counter state.
        
        Returns:
            Dict: Metadata including statistics
        """
        return {
            'type': 'pn_counter',
            'node_id': self.node_id,
            'current_value': self.value(),
            'positive_total': self.positive_value(),
            'negative_total': self.negative_value(),
            'positive_nodes': len(self.p_counter.vector),
            'negative_nodes': len(self.n_counter.vector),
            'operation_balance': {
                'positive_ops': self.positive_value(),
                'negative_ops': self.negative_value(),
                'net_value': self.value()
            }
        }
    
    def get_node_breakdown(self) -> Dict:
        """
        Get per-node breakdown of operations.
        
        Returns:
            Dict: Breakdown by node of positive/negative operations
        """
        all_nodes = set(self.p_counter.vector.keys()) | set(self.n_counter.vector.keys())
        
        breakdown = {}
        for node in all_nodes:
            positive = self.p_counter.vector.get(node, 0)
            negative = self.n_counter.vector.get(node, 0)
            breakdown[node] = {
                'positive': positive,
                'negative': negative,
                'net': positive - negative
            }
        
        return breakdown
    
    def reset_node(self, node_id: str = None) -> Dict:
        """
        Reset counters for a specific node (for maintenance).
        
        Args:
            node_id: Node to reset (default: own node)
            
        Returns:
            Dict: Previous values for the node
        """
        if node_id is None:
            node_id = self.node_id
        
        previous = {
            'positive': self.p_counter.vector.get(node_id, 0),
            'negative': self.n_counter.vector.get(node_id, 0)
        }
        
        # Remove node from both counters
        self.p_counter.vector.pop(node_id, None)
        self.n_counter.vector.pop(node_id, None)
        
        return previous
    
    def add_to_value(self, amount: int) -> None:
        """
        Add to the counter value (positive or negative).
        
        Args:
            amount: Amount to add (can be positive or negative)
        """
        if amount > 0:
            self.increment(amount)
        elif amount < 0:
            self.decrement(-amount)
        # If amount is 0, do nothing
    
    def set_minimum(self, minimum: int) -> bool:
        """
        Ensure the counter value is at least the minimum.
        
        Args:
            minimum: Minimum value to ensure
            
        Returns:
            bool: True if counter was incremented
        """
        current = self.value()
        if current < minimum:
            self.increment(minimum - current)
            return True
        return False
    
    def __str__(self) -> str:
        """String representation of the PN-Counter."""
        return f"PNCounter(value={self.value()}, +{self.positive_value()}, -{self.negative_value()})"
    
    def __repr__(self) -> str:
        """Detailed representation of the PN-Counter."""
        return (f"PNCounter(node_id='{self.node_id}', "
                f"value={self.value()}, "
                f"positive={self.positive_value()}, "
                f"negative={self.negative_value()})")
    
    def __eq__(self, other) -> bool:
        """Check equality with another PN-Counter."""
        if not isinstance(other, PNCounter):
            return False
        return (self.p_counter.vector == other.p_counter.vector and 
                self.n_counter.vector == other.n_counter.vector)
    
    def __lt__(self, other) -> bool:
        """Compare values for sorting."""
        if isinstance(other, PNCounter):
            return self.value() < other.value()
        elif isinstance(other, (int, float)):
            return self.value() < other
        return NotImplemented
    
    def __le__(self, other) -> bool:
        """Compare values for sorting."""
        if isinstance(other, PNCounter):
            return self.value() <= other.value()
        elif isinstance(other, (int, float)):
            return self.value() <= other
        return NotImplemented
    
    def __gt__(self, other) -> bool:
        """Compare values for sorting."""
        if isinstance(other, PNCounter):
            return self.value() > other.value()
        elif isinstance(other, (int, float)):
            return self.value() > other
        return NotImplemented
    
    def __ge__(self, other) -> bool:
        """Compare values for sorting."""
        if isinstance(other, PNCounter):
            return self.value() >= other.value()
        elif isinstance(other, (int, float)):
            return self.value() >= other
        return NotImplemented