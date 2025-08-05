"""
Grow-only Set (G-Set) CRDT
===========================

Set supporting only add operations. Elements once added cannot be removed.
Conflict-free merging by taking union of all sets.

Use cases:
- Unique identifiers
- Permanent audit logs
- Non-removable records
- Operation ID tracking
"""

from typing import Dict, Any, Set, TypeVar
from .crdt_base import BaseCRDT

T = TypeVar('T')


class GSet(BaseCRDT):
    """
    Grow-only Set CRDT implementation.
    
    Mathematical guarantees:
    - Monotonic: Set only grows, never shrinks
    - Convergent: All nodes reach same final set
    - Commutative: Merge order doesn't matter
    """
    
    def __init__(self, node_id: str):
        """Initialize G-Set with node ID."""
        super().__init__(node_id)
        self.elements: Set[Any] = set()
    
    def add(self, element: Any) -> None:
        """
        Add element to set.
        
        Args:
            element: Any hashable element
        """
        self.elements.add(element)
        self.update_metadata()
    
    def contains(self, element: Any) -> bool:
        """Check if element exists in set."""
        return element in self.elements
    
    def merge(self, other: 'GSet') -> None:
        """
        Merge with another G-Set.
        Takes union of both sets (convergent).
        """
        self.elements.update(other.elements)
        self.update_metadata()
    
    def value(self) -> Set[Any]:
        """Get set contents."""
        return self.elements.copy()
    
    def size(self) -> int:
        """Get number of elements in set."""
        return len(self.elements)
    
    def to_list(self) -> list:
        """Convert set to list (for JSON serialization)."""
        return list(self.elements)
    
    def to_dict(self) -> Dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "elements": self.to_list(),
            "metadata": self.get_metadata()
        }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Deserialize from dictionary."""
        self.elements = set(data["elements"])
        metadata = data["metadata"]
        self.node_id = metadata["node_id"]
        self.created_at = metadata["created_at"]
        self.last_updated = metadata["last_updated"]
        self.version = metadata["version"]
    
    def __len__(self) -> int:
        return len(self.elements)
    
    def __contains__(self, element: Any) -> bool:
        return element in self.elements
    
    def __iter__(self):
        return iter(self.elements)
    
    def __str__(self) -> str:
        return f"GSet(size={len(self.elements)})"
    
    def __repr__(self) -> str:
        return f"GSet(node_id='{self.node_id}', elements={self.elements})"