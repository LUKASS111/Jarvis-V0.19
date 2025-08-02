"""
CRDT (Conflict-free Replicated Data Types) Module
==================================================

Mathematical foundation for distributed system architecture.
Priority: Distributed correctness > User experience.

Core CRDT types:
- GCounter: Grow-only counter for metrics aggregation
- GSet: Grow-only set for permanent records
- LWWRegister: Last-Write-Wins for configuration values
- ORSet: Observed-Remove set for dynamic collections
- PNCounter: Positive-Negative counter for balanced operations
"""

from .crdt_base import BaseCRDT
from .g_counter import GCounter
from .g_set import GSet
from .lww_register import LWWRegister

__version__ = "0.2.0"
__all__ = ["BaseCRDT", "GCounter", "GSet", "LWWRegister"]