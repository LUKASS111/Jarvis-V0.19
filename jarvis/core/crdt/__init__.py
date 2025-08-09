"""
CRDT (Conflict-free Replicated Data Types) Module
==================================================

Complete enterprise-grade distributed system architecture.
Priority: Distributed correctness with performance optimization.

Phase 1-5 Implementation Complete:
- Phase 1-3: Core CRDT types with mathematical guarantees
- Phase 4: Network synchronization and conflict resolution
- Phase 5: Performance optimization and enterprise monitoring

Core CRDT types:
- GCounter: Grow-only counter for metrics aggregation
- GSet: Grow-only set for permanent records
- LWWRegister: Last-Write-Wins for configuration values
- ORSet: Observed-Remove set for dynamic collections
- PNCounter: Positive-Negative counter for balanced operations

Advanced Features:
- Network synchronization with P2P communication
- Advanced conflict resolution beyond mathematical guarantees
- Performance optimization with delta compression
- Enterprise monitoring with real-time dashboards
- Automated alerting and health monitoring
"""

try:
    from .crdt_base import BaseCRDT
    from .g_counter import GCounter
    from .g_set import GSet
    from .lww_register import LWWRegister
    from .or_set import ORSet
    from .pn_counter import PNCounter

    # Phase 4-5 Advanced Features
    from .crdt_network import CRDTNetworkManager, CRDTSynchronizer
    from .crdt_conflict_resolver import CRDTConflictResolver
    from .crdt_performance_optimizer import CRDTPerformanceOptimizer
    from .crdt_monitoring_dashboard import CRDTMonitoringCoordinator
    
    ADVANCED_CRDT_AVAILABLE = True
except ImportError:
    ADVANCED_CRDT_AVAILABLE = False

# Always available: basic CRDT manager
from .crdt_manager import CRDTManager, get_crdt_manager, create_test_crdt_scenario

__version__ = "0.2.0"

if ADVANCED_CRDT_AVAILABLE:
    __all__ = [
        # Core CRDT Types
        "BaseCRDT", "GCounter", "GSet", "LWWRegister", "ORSet", "PNCounter",
        # Network & Synchronization
        "CRDTNetworkManager", "CRDTSynchronizer",
        # Conflict Resolution
        "CRDTConflictResolver", 
        # Performance & Monitoring
        "CRDTPerformanceOptimizer", "CRDTMonitoringCoordinator",
        # Basic Manager
        "CRDTManager", "get_crdt_manager", "create_test_crdt_scenario"
    ]
else:
    __all__ = [
        # Basic Manager only
        "CRDTManager", "get_crdt_manager", "create_test_crdt_scenario"
    ]