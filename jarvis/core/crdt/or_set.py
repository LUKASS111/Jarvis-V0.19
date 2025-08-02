"""
OR-Set (Observed-Remove Set) CRDT Implementation
===============================================

Provides add/remove semantics with conflict-free merging.
Elements can be safely added and removed across distributed nodes.
"""

import uuid
import time
import json
from typing import Any, Set, Dict, Tuple
from .crdt_base import BaseCRDT


class ORSet(BaseCRDT):
    """
    Observed-Remove Set CRDT implementation.
    
    Allows adding and removing elements with conflict-free merging.
    Each element is tagged with unique identifiers to track operations.
    """
    
    def __init__(self, node_id: str = None):
        super().__init__(node_id)
        self.added: Dict[Any, Set[str]] = {}  # element -> set of unique tags
        self.removed: Set[str] = set()  # set of removed tags
    
    def add(self, element: Any) -> str:
        """
        Add an element to the set.
        
        Args:
            element: Element to add
            
        Returns:
            str: Unique tag for this add operation
        """
        tag = f"{self.node_id}:{uuid.uuid4()}:{time.time_ns()}"
        
        if element not in self.added:
            self.added[element] = set()
        self.added[element].add(tag)
        
        return tag
    
    def remove(self, element: Any) -> bool:
        """
        Remove an element from the set.
        
        Args:
            element: Element to remove
            
        Returns:
            bool: True if element was present and removed
        """
        if element not in self.added:
            return False
        
        # Mark all tags for this element as removed
        removed_count = 0
        for tag in self.added[element].copy():
            if tag not in self.removed:
                self.removed.add(tag)
                removed_count += 1
        
        return removed_count > 0
    
    def contains(self, element: Any) -> bool:
        """
        Check if element is in the set.
        
        Args:
            element: Element to check
            
        Returns:
            bool: True if element is present (has unremoved tags)
        """
        if element not in self.added:
            return False
        
        # Element is present if it has any tags not in removed set
        return any(tag not in self.removed for tag in self.added[element])
    
    def value(self) -> Set[Any]:
        """
        Get current value of the OR-Set.
        
        Returns:
            Set: All elements currently in the set
        """
        return self.elements()
    
    def elements(self) -> Set[Any]:
        """
        Get all elements currently in the set.
        
        Returns:
            Set: All elements with unremoved tags
        """
        result = set()
        for element, tags in self.added.items():
            if any(tag not in self.removed for tag in tags):
                result.add(element)
        return result
    
    def size(self) -> int:
        """
        Get the size of the set.
        
        Returns:
            int: Number of elements currently in the set
        """
        return len(self.elements())
    
    def merge(self, other: 'ORSet') -> None:
        """
        Merge another OR-Set into this one.
        
        Args:
            other: Other OR-Set to merge
        """
        if not isinstance(other, ORSet):
            raise TypeError("Can only merge with another ORSet")
        
        # Merge added elements and their tags
        for element, tags in other.added.items():
            if element not in self.added:
                self.added[element] = set()
            self.added[element].update(tags)
        
        # Merge removed tags
        self.removed.update(other.removed)
    
    def to_dict(self) -> Dict:
        """
        Serialize to dictionary for storage/transmission.
        
        Returns:
            Dict: Serializable representation
        """
        return {
            'type': 'or_set',
            'node_id': self.node_id,
            'added': {
                str(element): list(tags) 
                for element, tags in self.added.items()
            },
            'removed': list(self.removed),
            'timestamp': time.time()
        }
    
    @classmethod
    def from_dict_cls(cls, data: Dict) -> 'ORSet':
        """
        Deserialize from dictionary.
        
        Args:
            data: Dictionary representation
            
        Returns:
            ORSet: Reconstructed OR-Set
        """
        if data.get('type') != 'or_set':
            raise ValueError("Invalid data type for OR-Set")
        
        or_set = cls(data.get('node_id'))
        
        # Reconstruct added elements
        for element_str, tags_list in data.get('added', {}).items():
            # Try to convert back to original type if possible
            try:
                # Try int first
                element = int(element_str)
            except ValueError:
                try:
                    # Try float
                    element = float(element_str)
                except ValueError:
                    # Keep as string
                    element = element_str
            
            or_set.added[element] = set(tags_list)
        
        # Reconstruct removed tags
        or_set.removed = set(data.get('removed', []))
        
        return or_set
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """
        Update this instance from dictionary (for base class compatibility).
        
        Args:
            data: Dictionary representation
        """
        if data.get('type') != 'or_set':
            raise ValueError("Invalid data type for OR-Set")
        
        # Clear current state
        self.added.clear()
        self.removed.clear()
        
        # Reconstruct added elements
        for element_str, tags_list in data.get('added', {}).items():
            # Try to convert back to original type if possible
            try:
                # Try int first
                element = int(element_str)
            except ValueError:
                try:
                    # Try float
                    element = float(element_str)
                except ValueError:
                    # Keep as string
                    element = element_str
            
            self.added[element] = set(tags_list)
        
        # Reconstruct removed tags
        self.removed = set(data.get('removed', []))
    
    def from_dict_inplace(self, data: Dict) -> None:
        """
        Update this instance from dictionary (for base class compatibility).
        
        Args:
            data: Dictionary representation
        """
        if data.get('type') != 'or_set':
            raise ValueError("Invalid data type for OR-Set")
        
        # Clear current state
        self.added.clear()
        self.removed.clear()
        
        # Reconstruct added elements
        for element_str, tags_list in data.get('added', {}).items():
            # Try to convert back to original type if possible
            try:
                # Try int first
                element = int(element_str)
            except ValueError:
                try:
                    # Try float
                    element = float(element_str)
                except ValueError:
                    # Keep as string
                    element = element_str
            
            self.added[element] = set(tags_list)
        
        # Reconstruct removed tags
        self.removed = set(data.get('removed', []))
    
    def get_metadata(self) -> Dict:
        """
        Get metadata about the OR-Set state.
        
        Returns:
            Dict: Metadata including statistics
        """
        return {
            'type': 'or_set',
            'node_id': self.node_id,
            'total_elements': len(self.added),
            'active_elements': len(self.elements()),
            'total_tags': sum(len(tags) for tags in self.added.values()),
            'removed_tags': len(self.removed),
            'elements_preview': list(self.elements())[:10]  # First 10 elements
        }
    
    def cleanup_tombstones(self, cutoff_time: float = None) -> int:
        """
        Clean up old tombstone records (removed tags).
        
        Args:
            cutoff_time: Remove tombstones older than this timestamp
                        (default: 30 days ago)
        
        Returns:
            int: Number of tombstones removed
        """
        if cutoff_time is None:
            cutoff_time = time.time() - (30 * 24 * 3600)  # 30 days
        
        # Find old removed tags to clean up
        old_removed = set()
        for tag in self.removed:
            try:
                # Extract timestamp from tag format: node:uuid:timestamp
                parts = tag.split(':')
                if len(parts) >= 3:
                    tag_time = int(parts[-1]) / 1_000_000_000  # Convert ns to seconds
                    if tag_time < cutoff_time:
                        old_removed.add(tag)
            except (ValueError, IndexError):
                # Keep tags with unexpected format
                continue
        
        # Remove old tombstones
        self.removed -= old_removed
        
        return len(old_removed)
    
    def __str__(self) -> str:
        """String representation of the OR-Set."""
        elements = self.elements()
        if len(elements) <= 5:
            return f"ORSet({elements})"
        else:
            preview = list(elements)[:5]
            return f"ORSet({preview}... +{len(elements)-5} more)"
    
    def __repr__(self) -> str:
        """Detailed representation of the OR-Set."""
        return (f"ORSet(node_id='{self.node_id}', "
                f"elements={len(self.elements())}, "
                f"total_tags={sum(len(tags) for tags in self.added.values())}, "
                f"removed_tags={len(self.removed)})")