"""
Last-Write-Wins Register (LWW-Register) CRDT
==============================================

Register storing single value with timestamp-based conflict resolution.
Most recent write wins during merge operations.

Use cases:
- Configuration values
- System status updates
- Latest state information
- Current version tracking
"""

import time
from typing import Dict, Any, Optional
from .crdt_base import BaseCRDT


class LWWRegister(BaseCRDT):
    """
    Last-Write-Wins Register CRDT implementation.
    
    Mathematical guarantees:
    - Convergent: All nodes reach same final value
    - Total order: Timestamps provide deterministic ordering
    - Commutative: Merge order doesn't matter
    """
    
    def __init__(self, node_id: str, initial_value: Any = None):
        """Initialize LWW-Register with node ID and optional initial value."""
        super().__init__(node_id)
        self._value = initial_value
        self.timestamp = time.time_ns() if initial_value is not None else 0
        self.writer_node = node_id if initial_value is not None else None
    
    def write(self, value: Any) -> None:
        """
        Write new value with current timestamp.
        
        Args:
            value: New value to store
        """
        self._value = value
        self.timestamp = time.time_ns()
        self.writer_node = self.node_id
        self.update_metadata()
    
    def read(self) -> Any:
        """Read current value."""
        return self._value
    
    def merge(self, other: 'LWWRegister') -> None:
        """
        Merge with another LWW-Register.
        Takes value with highest timestamp (latest write wins).
        """
        if other.timestamp > self.timestamp:
            self._value = other._value
            self.timestamp = other.timestamp
            self.writer_node = other.writer_node
        elif other.timestamp == self.timestamp:
            # Tie-breaker: lexicographically greater node ID wins
            if other.writer_node and (not self.writer_node or other.writer_node > self.writer_node):
                self._value = other._value
                self.timestamp = other.timestamp
                self.writer_node = other.writer_node
        
        self.update_metadata()
    
    def value(self) -> Any:
        """Get current value (alias for read())."""
        return self._value
    
    def has_value(self) -> bool:
        """Check if register contains a value."""
        return self._value is not None
    
    def get_timestamp(self) -> int:
        """Get timestamp of current value."""
        return self.timestamp
    
    def get_writer(self) -> Optional[str]:
        """Get node ID that wrote current value."""
        return self.writer_node
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "value": self._value,
            "timestamp": self.timestamp,
            "writer_node": self.writer_node,
            "metadata": self.get_metadata()
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Deserialize from dictionary."""
        self._value = data["value"]
        self.timestamp = data["timestamp"]
        self.writer_node = data["writer_node"]
        metadata = data["metadata"]
        self.node_id = metadata["node_id"]
        self.created_at = metadata["created_at"]
        self.last_updated = metadata["last_updated"]
        self.version = metadata["version"]
    
    def __str__(self) -> str:
        return f"LWWRegister(value={self._value}, writer={self.writer_node})"
    
    def __repr__(self) -> str:
        return f"LWWRegister(node_id='{self.node_id}', value={self._value}, timestamp={self.timestamp})"