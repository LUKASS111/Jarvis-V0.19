"""
Base CRDT Abstract Class
========================

Mathematical foundation for conflict-free replicated data types.
Provides convergence guarantees and operational semantics.
"""

import time
import json
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional


class BaseCRDT(ABC):
    """
    Abstract base class for all CRDT implementations.
    
    Ensures mathematical properties:
    - Convergence: Concurrent updates reach identical state
    - Associativity: Operation order doesn't affect final state  
    - Commutativity: Update order doesn't affect final state
    - Idempotence: Duplicate operations don't change state
    """
    
    def __init__(self, node_id: str):
        """Initialize CRDT with node identifier."""
        self.node_id = node_id
        self.created_at = time.time()
        self.last_updated = time.time()
        self.version = 1
        
    @abstractmethod
    def merge(self, other: 'BaseCRDT') -> None:
        """
        Merge state with another CRDT instance.
        Must be idempotent, commutative, and associative.
        """
        pass
    
    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """Serialize CRDT state to dictionary."""
        pass
    
    @abstractmethod
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Deserialize CRDT state from dictionary."""
        pass
    
    @abstractmethod
    def value(self) -> Any:
        """Get current value/state of the CRDT."""
        pass
    
    def to_json(self) -> str:
        """Serialize CRDT to JSON string."""
        return json.dumps(self.to_dict())
    
    def from_json(self, json_str: str) -> None:
        """Deserialize CRDT from JSON string."""
        data = json.loads(json_str)
        self.from_dict(data)
    
    def update_metadata(self) -> None:
        """Update timestamp and version metadata."""
        self.last_updated = time.time()
        self.version += 1
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get CRDT metadata."""
        return {
            "node_id": self.node_id,
            "created_at": self.created_at,
            "last_updated": self.last_updated,
            "version": self.version,
            "crdt_type": self.__class__.__name__
        }