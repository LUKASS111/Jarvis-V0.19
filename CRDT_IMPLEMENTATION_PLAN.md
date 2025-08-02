# CRDT Implementation Plan for Jarvis AI Assistant
## Conflict-free Replicated Data Types Integration Strategy

### Executive Summary
This document outlines the comprehensive implementation plan for integrating CRDT (Conflict-free Replicated Data Types) into the Jarvis AI Assistant system. The goal is to enable distributed, conflict-free data synchronization while maintaining 100% system functionality and preserving all existing features.

---

## Table of Contents
1. [Current System Analysis](#current-system-analysis)
2. [CRDT Architecture Design](#crdt-architecture-design)
3. [Implementation Phases](#implementation-phases)
4. [Database Schema Evolution](#database-schema-evolution)
5. [CRDT Types Implementation](#crdt-types-implementation)
6. [Integration Points](#integration-points)
7. [Testing Strategy](#testing-strategy)
8. [Migration Plan](#migration-plan)
9. [Performance Optimization](#performance-optimization)
10. [Security Considerations](#security-considerations)
11. [Deployment Strategy](#deployment-strategy)
12. [Monitoring & Maintenance](#monitoring--maintenance)

---

## 1. Current System Analysis

### 1.1 Existing Architecture Assessment (Updated v0.2)
- **Archive System**: SQLite-based `jarvis_archive.db` with 20k+ entries
- **Data Verifier**: Dual-model verification system with confidence scoring
- **Backup System**: Automated backup system with integrity verification
- **Health Scoring**: 100/100 current health score (4/4 systems healthy)
- **Version Management**: Automatic version-based cleanup system (v0.2)
- **Entry Points**: Unified startup system with CLI/GUI modes
- **Agent Workflows**: Autonomous testing with 100+ cycle capability
- **System Dashboard**: Real-time monitoring and health reporting

### 1.2 Integration Points Identified
- `jarvis/core/data_archiver.py` - Primary data storage interface
- `jarvis/core/data_verifier.py` - Verification and conflict detection
- `jarvis/core/backup_recovery.py` - Backup synchronization
- `jarvis/core/archive_purge_manager.py` - Data lifecycle management
- `jarvis/core/agent_workflow.py` - Autonomous testing and validation
- `jarvis/core/error_handler.py` - Enhanced error handling system
- Database schema in `data/jarvis_archive.db`
- `system_dashboard.py` - Real-time system monitoring
- `agent_launcher.py` - Agent workflow management

### 1.3 Current Data Flow
```
Input → Archive → Verify → Store → Backup → Purge (by version) → Agent Testing
```

### 1.4 System Health Status (v0.2)
- **Total Test Coverage**: 72/72 tests passing (100% success rate)
- **Archive Entries**: 20,838 total entries with dual verification
- **System Health**: 100% (4/4 systems operational)
- **Active Features**: Data archiving, verification, backup, agent workflows
- **Performance**: 3+ archive operations/second, background verification
- **Agent Capabilities**: 100+ cycle testing with auto-correction

### 1.5 Compatibility Requirements
- ✅ Preserve all 22 program functions
- ✅ Maintain 100% test coverage (72/72 tests)
- ✅ Keep 100/100 health score
- ✅ Ensure version-based cleanup continues to work (v0.2)
- ✅ Maintain unified entry point system
- ✅ Preserve agent workflow capabilities
- ✅ Maintain system dashboard monitoring
- ✅ Keep backup/recovery system operational

---

## 2. CRDT Architecture Design

### 2.1 High-Level Architecture
```
┌─────────────────────────────────────────────────────────┐
│                 Jarvis CRDT Layer                       │
├─────────────────────────────────────────────────────────┤
│  CRDT Manager  │  Sync Engine  │  Conflict Resolver    │
├─────────────────────────────────────────────────────────┤
│  G-Counter │ G-Set │ 2P-Set │ LWW-Reg │ OR-Set │ PN-Ctr │
├─────────────────────────────────────────────────────────┤
│              Local State Store (SQLite)                 │
├─────────────────────────────────────────────────────────┤
│              Network Transport Layer                     │
└─────────────────────────────────────────────────────────┘
```

### 2.2 Component Responsibilities

#### 2.2.1 CRDT Manager (`jarvis/core/crdt_manager.py`)
- Initialize and manage all CRDT instances
- Route operations to appropriate CRDT types
- Handle state merging and synchronization
- Integrate with existing archive system

#### 2.2.2 Sync Engine (`jarvis/core/crdt_sync.py`)
- Manage peer discovery and connection
- Handle network communication
- Implement delta synchronization
- Queue and retry failed operations

#### 2.2.3 Conflict Resolver (`jarvis/core/crdt_resolver.py`)
- Resolve semantic conflicts beyond CRDT guarantees
- Integrate with existing data verifier
- Maintain audit trail of conflict resolutions
- Generate conflict reports

#### 2.2.4 Local State Store (`jarvis/core/crdt_storage.py`)
- Extend SQLite schema with CRDT metadata
- Implement efficient state persistence
- Handle version vectors and logical clocks
- Manage tombstone records for deletions

#### 2.2.5 Agent Integration (`jarvis/core/crdt_agent.py`)
- Integrate CRDT operations with agent workflows
- Support distributed agent testing scenarios
- Handle agent state synchronization across nodes
- Maintain agent workflow audit trails

#### 2.2.6 Dashboard Integration (`crdt_dashboard.py`)
- Extend system dashboard with CRDT metrics
- Real-time synchronization monitoring
- Conflict resolution reporting
- Network topology visualization

---

## 3. Implementation Phases

### Phase 1: Foundation (Week 1-2)
**Goal**: Establish CRDT infrastructure without breaking existing functionality

#### 3.1.1 Core Infrastructure
- [ ] Create `jarvis/core/crdt/` module structure
- [ ] Implement base CRDT abstract class
- [ ] Add CRDT metadata to database schema
- [ ] Create CRDT configuration system
- [ ] Implement basic unit tests

#### 3.1.2 Integration Preparation
- [ ] Analyze existing data patterns in archive
- [ ] Design backward compatibility layer
- [ ] Create migration utilities
- [ ] Update documentation

#### 3.1.3 Testing Infrastructure
- [ ] Create CRDT test framework
- [ ] Implement distributed test scenarios
- [ ] Add conflict simulation tools
- [ ] Extend existing test suites

### Phase 2: Basic CRDT Types (Week 3-4)
**Goal**: Implement fundamental CRDT types needed for Jarvis operations

#### 3.2.1 G-Counter Implementation
```python
# Use Case: Event counting, health metrics, operation statistics
class GCounter:
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.vector = {}  # node_id -> count
    
    def increment(self, amount: int = 1):
        self.vector[self.node_id] = self.vector.get(self.node_id, 0) + amount
    
    def merge(self, other: 'GCounter'):
        for node, count in other.vector.items():
            self.vector[node] = max(self.vector.get(node, 0), count)
    
    def value(self) -> int:
        return sum(self.vector.values())
```

#### 3.2.2 G-Set Implementation
```python
# Use Case: Unique identifiers, non-removable records
class GSet:
    def __init__(self):
        self.elements = set()
    
    def add(self, element):
        self.elements.add(element)
    
    def merge(self, other: 'GSet'):
        self.elements.update(other.elements)
    
    def contains(self, element) -> bool:
        return element in self.elements
```

#### 3.2.3 LWW-Register Implementation
```python
# Use Case: Configuration values, latest status updates
class LWWRegister:
    def __init__(self):
        self.value = None
        self.timestamp = 0
        self.node_id = None
    
    def write(self, value, node_id: str):
        timestamp = time.time_ns()
        if timestamp > self.timestamp or (timestamp == self.timestamp and node_id > self.node_id):
            self.value = value
            self.timestamp = timestamp
            self.node_id = node_id
    
    def merge(self, other: 'LWWRegister'):
        if other.timestamp > self.timestamp or (other.timestamp == self.timestamp and other.node_id > self.node_id):
            self.value = other.value
            self.timestamp = other.timestamp
            self.node_id = other.node_id
```

### Phase 3: Advanced CRDT Types (Week 5-6)
**Goal**: Implement complex CRDT types for advanced use cases

#### 3.3.1 OR-Set Implementation
```python
# Use Case: Archive entries with add/remove capabilities
class ORSet:
    def __init__(self):
        self.added = {}  # element -> set of unique tags
        self.removed = set()  # set of removed tags
    
    def add(self, element):
        tag = f"{element}:{uuid.uuid4()}"
        if element not in self.added:
            self.added[element] = set()
        self.added[element].add(tag)
        return tag
    
    def remove(self, element):
        if element in self.added:
            for tag in self.added[element]:
                self.removed.add(tag)
    
    def contains(self, element) -> bool:
        if element not in self.added:
            return False
        return any(tag not in self.removed for tag in self.added[element])
```

#### 3.3.2 PN-Counter Implementation
```python
# Use Case: Resource balancing, credit/debit operations
class PNCounter:
    def __init__(self, node_id: str):
        self.p_counter = GCounter(node_id)  # Positive increments
        self.n_counter = GCounter(node_id)  # Negative increments
    
    def increment(self, amount: int = 1):
        self.p_counter.increment(amount)
    
    def decrement(self, amount: int = 1):
        self.n_counter.increment(amount)
    
    def value(self) -> int:
        return self.p_counter.value() - self.n_counter.value()
```

### Phase 4: Integration (Week 7-8)
**Goal**: Integrate CRDT types with existing Jarvis systems

#### 3.4.1 Archive System Integration
- [ ] Wrap archive operations with appropriate CRDT types
- [ ] Implement CRDT-aware backup system
- [ ] Update purge manager for CRDT metadata
- [ ] Ensure version-based cleanup works with CRDTs

#### 3.4.2 Verification System Integration
- [ ] Extend data verifier to handle CRDT conflicts
- [ ] Implement semantic conflict detection
- [ ] Create CRDT-specific verification rules
- [ ] Update health scoring for distributed scenarios

#### 3.4.3 Network Layer
- [ ] Implement peer discovery mechanism
- [ ] Create secure communication protocol
- [ ] Add delta synchronization
- [ ] Handle network partitions gracefully

### Phase 5: Advanced Features (Week 9-10)
**Goal**: Implement production-ready features

#### 3.5.1 Performance Optimization
- [ ] Implement efficient delta compression
- [ ] Add lazy synchronization
- [ ] Create conflict batching
- [ ] Optimize storage format

#### 3.5.2 Monitoring & Observability
- [ ] Add CRDT-specific health metrics
- [ ] Create synchronization dashboards
- [ ] Implement conflict reporting
- [ ] Add performance monitoring

---

## 4. Database Schema Evolution

### 4.1 Current Schema Analysis
```sql
-- Current jarvis_archive.db structure (v0.2)
CREATE TABLE archive_entries (
    id INTEGER PRIMARY KEY,
    operation TEXT,
    input_data TEXT,
    output_data TEXT,
    timestamp TEXT,
    verification_result TEXT,
    confidence_score REAL,
    model_used TEXT,
    program_version TEXT,
    source TEXT,
    data_type TEXT,
    content_hash TEXT,
    metadata TEXT
);
```

### 4.2 CRDT-Enhanced Schema
```sql
-- Enhanced schema with CRDT support (v0.2 compatible)
CREATE TABLE archive_entries (
    id INTEGER PRIMARY KEY,
    operation TEXT,
    input_data TEXT,
    output_data TEXT,
    timestamp TEXT,
    verification_result TEXT,
    confidence_score REAL,
    model_used TEXT,
    program_version TEXT,
    source TEXT,
    data_type TEXT,
    content_hash TEXT,
    metadata TEXT,
    -- CRDT Fields
    crdt_type TEXT,              -- Type of CRDT (g_counter, or_set, etc.)
    crdt_node_id TEXT,           -- Node that created this entry
    crdt_vector_clock TEXT,      -- JSON encoded vector clock
    crdt_logical_time INTEGER,   -- Logical timestamp
    crdt_operation_id TEXT,      -- Unique operation identifier
    crdt_metadata TEXT           -- Additional CRDT-specific data
);

-- CRDT State Table
CREATE TABLE crdt_states (
    id INTEGER PRIMARY KEY,
    crdt_name TEXT UNIQUE,       -- Name/identifier of the CRDT instance
    crdt_type TEXT,              -- Type of CRDT
    state_data TEXT,             -- JSON encoded CRDT state
    last_updated TEXT,           -- Last update timestamp
    version INTEGER              -- State version for optimization
);

-- Synchronization Log
CREATE TABLE sync_log (
    id INTEGER PRIMARY KEY,
    peer_node_id TEXT,           -- ID of peer node
    sync_timestamp TEXT,         -- When sync occurred
    operations_sent INTEGER,     -- Number of operations sent
    operations_received INTEGER, -- Number of operations received
    conflicts_resolved INTEGER,  -- Number of conflicts resolved
    sync_duration_ms INTEGER     -- Sync duration in milliseconds
);

-- Agent Workflow States Table
CREATE TABLE agent_workflow_states (
    id INTEGER PRIMARY KEY,
    agent_id TEXT,
    workflow_id TEXT,
    state_data TEXT,             -- JSON encoded agent state
    crdt_type TEXT,              -- CRDT type for agent state
    last_synchronized TEXT,      -- Last sync timestamp
    node_id TEXT                 -- Node where agent is running
);
-- Conflict Resolution Log
CREATE TABLE conflict_log (
    id INTEGER PRIMARY KEY,
    conflict_timestamp TEXT,     -- When conflict occurred
    crdt_name TEXT,              -- Which CRDT had the conflict
    conflict_type TEXT,          -- Type of conflict
    resolution_strategy TEXT,    -- How it was resolved
    involved_nodes TEXT,         -- JSON array of node IDs
    resolution_details TEXT      -- Additional resolution info
);
```

### 4.3 Migration Strategy
```python
# Migration script structure
class CRDTMigration:
    def migrate_existing_data(self):
        """Migrate existing archive entries to CRDT format"""
        # 1. Add new columns to existing tables
        # 2. Assign CRDT types based on operation patterns
        # 3. Generate initial node IDs and vector clocks
        # 4. Create initial CRDT states
        # 5. Verify data integrity after migration
        
    def rollback_migration(self):
        """Rollback to original schema if needed"""
        # Safety mechanism for migration failures
```

---

## 5. CRDT Types Implementation

### 5.1 Mapping Jarvis Operations to CRDT Types

#### 5.1.1 G-Counter Applications
- **Health Score Metrics**: Aggregate health scores across nodes
- **Operation Counts**: Count successful operations, errors, verifications
- **System Statistics**: Track usage patterns, performance metrics

```python
# Example: Health score aggregation
health_counter = GCounter(node_id="jarvis_node_1")
health_counter.increment(100)  # Perfect health score
# When merging with other nodes, take maximum health achieved
```

#### 5.1.2 G-Set Applications
- **Unique Identifiers**: Store operation IDs, session IDs, node IDs
- **Permanent Records**: Store audit logs that should never be deleted
- **System Capabilities**: Track available features across nodes

```python
# Example: Operation ID tracking
operation_ids = GSet()
operation_ids.add("op_20240802_001")
operation_ids.add("op_20240802_002")
# Across nodes, all operation IDs are preserved
```

#### 5.1.3 OR-Set Applications
- **Archive Entries**: Allow distributed add/remove of archive records
- **Configuration Sets**: Manage distributed configuration changes
- **User Preferences**: Handle user setting changes across instances

```python
# Example: Distributed archive management
archive_set = ORSet()
archive_set.add("memory_entry_001")
archive_set.add("llm_response_002")
# Later, from another node:
archive_set.remove("memory_entry_001")  # Safely removable across nodes
```

#### 5.1.4 LWW-Register Applications
- **System Configuration**: Store latest configuration values
- **Status Updates**: Track current system status
- **Version Information**: Maintain current version across nodes

```python
# Example: Configuration management
config_reg = LWWRegister()
config_reg.write("debug_mode=true", "admin_node")
# Latest configuration wins across all nodes
```

#### 5.1.5 PN-Counter Applications
- **Resource Management**: Track available/used resources
- **Credit Systems**: Manage API credits, usage quotas
- **Load Balancing**: Track node capacity and load

```python
# Example: API credit management
api_credits = PNCounter("jarvis_node_1")
api_credits.increment(1000)  # Add credits
api_credits.decrement(10)    # Use credits
# Balance maintained across distributed nodes
```

### 5.2 CRDT Operation Mapping

```python
# Mapping table for Jarvis v0.2 operations
OPERATION_CRDT_MAPPING = {
    "memory_store": "or_set",           # Can add/remove memories
    "memory_retrieve": "g_counter",     # Count retrievals
    "llm_query": "g_counter",           # Count queries
    "verification": "lww_register",     # Latest verification status
    "health_check": "g_counter",        # Aggregate health metrics
    "configuration": "lww_register",    # Latest config wins
    "archive_entry": "or_set",          # Can add/remove entries
    "backup_create": "g_set",           # Backups are permanent
    "system_status": "lww_register",    # Latest status wins
    "resource_usage": "pn_counter",     # Track usage/availability
    "agent_workflow": "or_set",         # Agent states and results
    "error_handling": "g_set",          # Error logs are permanent
    "dashboard_metrics": "lww_register", # Latest metrics win
}
```

---

## 6. Integration Points

### 6.1 Data Archiver Integration
```python
# Enhanced data_archiver.py with CRDT support
class CRDTDataArchiver(DataArchiver):
    def __init__(self):
        super().__init__()
        self.crdt_manager = CRDTManager()
        
    def archive_data(self, operation, input_data, output_data, metadata=None):
        """Archive data with CRDT semantics"""
        # Determine appropriate CRDT type
        crdt_type = OPERATION_CRDT_MAPPING.get(operation, "lww_register")
        
        # Create CRDT entry
        crdt_entry = self.crdt_manager.create_entry(
            crdt_type=crdt_type,
            operation=operation,
            data={"input": input_data, "output": output_data},
            metadata=metadata
        )
        
        # Store with traditional method (for compatibility)
        traditional_id = super().archive_data(operation, input_data, output_data, metadata)
        
        # Link CRDT entry to traditional entry
        self.crdt_manager.link_entries(crdt_entry.id, traditional_id)
        
        return crdt_entry.id
```

### 6.2 Data Verifier Integration
```python
# Enhanced data_verifier.py with conflict resolution
class CRDTDataVerifier(DataVerifier):
    def __init__(self):
        super().__init__()
        self.conflict_resolver = CRDTConflictResolver()
        
    def verify_crdt_operation(self, crdt_operation):
        """Verify CRDT operation for semantic correctness"""
        # Perform traditional verification
        traditional_result = super().verify_data(
            crdt_operation.input_data, 
            crdt_operation.output_data
        )
        
        # Check for semantic conflicts
        semantic_conflicts = self.conflict_resolver.detect_semantic_conflicts(
            crdt_operation
        )
        
        # Resolve conflicts if found
        if semantic_conflicts:
            resolution = self.conflict_resolver.resolve_conflicts(
                semantic_conflicts, crdt_operation
            )
            return CRDTVerificationResult(
                traditional_result=traditional_result,
                semantic_conflicts=semantic_conflicts,
                resolution=resolution
            )
        
        return CRDTVerificationResult(
            traditional_result=traditional_result,
            semantic_conflicts=None,
            resolution=None
        )
```

### 6.3 Backup System Integration
```python
# Enhanced backup_recovery.py with CRDT state synchronization
class CRDTBackupRecovery(BackupRecovery):
    def create_backup(self):
        """Create backup including CRDT states"""
        # Create traditional backup
        traditional_backup = super().create_backup()
        
        # Create CRDT state snapshot
        crdt_snapshot = self.crdt_manager.create_state_snapshot()
        
        # Combine backups
        combined_backup = CRDTBackup(
            traditional_backup=traditional_backup,
            crdt_snapshot=crdt_snapshot,
            timestamp=datetime.utcnow(),
            node_id=self.node_id
        )
        
        return combined_backup
    
    def restore_backup(self, backup):
        """Restore backup with CRDT state merging"""
        # Restore traditional data
        super().restore_backup(backup.traditional_backup)
        
        # Merge CRDT states
        self.crdt_manager.merge_state_snapshot(backup.crdt_snapshot)
        
        # Verify consistency
        consistency_check = self.verify_crdt_consistency()
        return consistency_check
```

---

## 7. Testing Strategy

### 7.1 Unit Testing
```python
# Test structure for CRDT implementations
class TestGCounter:
    def test_increment(self):
        counter = GCounter("node1")
        counter.increment(5)
        assert counter.value() == 5
    
    def test_merge_idempotent(self):
        counter1 = GCounter("node1")
        counter2 = GCounter("node2")
        counter1.increment(3)
        counter2.increment(2)
        
        # Merge should be idempotent
        counter1.merge(counter2)
        original_value = counter1.value()
        counter1.merge(counter2)
        assert counter1.value() == original_value
    
    def test_merge_commutative(self):
        counter1 = GCounter("node1")
        counter2 = GCounter("node2")
        counter3 = GCounter("node3")
        
        # A.merge(B).merge(C) == A.merge(C).merge(B)
        counter1_copy = copy.deepcopy(counter1)
        
        counter1.merge(counter2)
        counter1.merge(counter3)
        
        counter1_copy.merge(counter3)
        counter1_copy.merge(counter2)
        
        assert counter1.value() == counter1_copy.value()
```

### 7.2 Integration Testing
```python
# Test CRDT integration with existing systems
class TestCRDTIntegration:
    def test_archive_with_crdt(self):
        """Test archiving with CRDT support maintains existing functionality"""
        archiver = CRDTDataArchiver()
        
        # Archive data using CRDT
        crdt_id = archiver.archive_data(
            operation="memory_store",
            input_data="test input",
            output_data="test output"
        )
        
        # Verify traditional retrieval still works
        traditional_data = archiver.retrieve_by_id(crdt_id)
        assert traditional_data is not None
        
        # Verify CRDT semantics
        crdt_state = archiver.crdt_manager.get_state("memory_store")
        assert crdt_state.contains(crdt_id)
    
    def test_health_score_with_crdt(self):
        """Test health scoring works with CRDT enhancements"""
        # Run health check with CRDT features enabled
        health_score = self.run_health_check_with_crdt()
        
        # Should maintain 100/100 score
        assert health_score >= 100
        
        # Should include CRDT-specific metrics
        assert "crdt_sync_status" in health_score.metrics
        assert "conflict_resolution_rate" in health_score.metrics
```

### 7.3 Distributed Testing
```python
# Test distributed scenarios
class TestDistributedCRDT:
    def test_network_partition_tolerance(self):
        """Test CRDT behavior during network partitions"""
        # Create two nodes
        node1 = CRDTNode("node1")
        node2 = CRDTNode("node2")
        
        # Sync initially
        node1.sync_with(node2)
        
        # Simulate network partition
        node1.disconnect_from(node2)
        
        # Perform operations on both nodes
        node1.archive_data("operation1", "data1", "result1")
        node2.archive_data("operation2", "data2", "result2")
        
        # Reconnect and sync
        node1.connect_to(node2)
        node1.sync_with(node2)
        
        # Verify both operations are present on both nodes
        assert node1.has_operation("operation1")
        assert node1.has_operation("operation2")
        assert node2.has_operation("operation1")
        assert node2.has_operation("operation2")
    
    def test_concurrent_modifications(self):
        """Test concurrent modifications merge correctly"""
        # Multiple nodes modify same CRDT simultaneously
        nodes = [CRDTNode(f"node{i}") for i in range(5)]
        
        # Each node increments counter
        for i, node in enumerate(nodes):
            node.increment_counter("global_counter", i + 1)
        
        # Sync all nodes
        for i in range(len(nodes)):
            for j in range(i + 1, len(nodes)):
                nodes[i].sync_with(nodes[j])
        
        # All nodes should have same final value
        expected_value = sum(range(1, 6))  # 1+2+3+4+5 = 15
        for node in nodes:
            assert node.get_counter_value("global_counter") == expected_value
```

### 7.4 Performance Testing
```python
# Test CRDT performance impact
class TestCRDTPerformance:
    def test_sync_performance(self):
        """Test synchronization performance"""
        # Create large dataset
        node1 = CRDTNode("node1")
        for i in range(10000):
            node1.archive_data(f"operation_{i}", f"data_{i}", f"result_{i}")
        
        # Measure sync time
        node2 = CRDTNode("node2")
        start_time = time.time()
        node1.sync_with(node2)
        sync_time = time.time() - start_time
        
        # Should sync within reasonable time (< 30 seconds for 10k entries)
        assert sync_time < 30
        
        # Verify data integrity
        assert node2.get_entry_count() == 10000
    
    def test_memory_usage(self):
        """Test memory usage doesn't grow excessively"""
        node = CRDTNode("test_node")
        initial_memory = self.get_memory_usage()
        
        # Add large number of entries
        for i in range(50000):
            node.archive_data(f"operation_{i}", f"data_{i}", f"result_{i}")
        
        final_memory = self.get_memory_usage()
        memory_growth = final_memory - initial_memory
        
        # Memory growth should be reasonable (< 500MB for 50k entries)
        assert memory_growth < 500 * 1024 * 1024  # 500MB
```

---

## 8. Migration Plan

### 8.1 Pre-Migration Checklist
- [ ] **Backup Current System**: Create complete backup of existing database and configuration
- [ ] **Environment Setup**: Prepare test environment identical to production  
- [ ] **Performance Baseline**: Establish current performance metrics (v0.2 baseline)
- [ ] **Test Coverage**: Ensure 100% test coverage of existing functionality (72/72 tests)
- [ ] **Health Score Verification**: Confirm 100/100 health score baseline
- [ ] **Agent Workflow Testing**: Verify all 8 test scenarios work correctly
- [ ] **Rollback Plan**: Prepare rollback procedures

### 8.2 Migration Steps

#### Step 1: Schema Migration (Low Risk)
```bash
# 1. Create backup
python archive_purge_cli.py backup --full --migration-prep

# 2. Run schema migration
python scripts/migrate_to_crdt.py --dry-run
python scripts/migrate_to_crdt.py --execute

# 3. Verify schema
python scripts/verify_migration.py --schema
```

#### Step 2: Data Migration (Medium Risk)
```bash
# 1. Migrate existing data to CRDT format
python scripts/migrate_to_crdt.py --migrate-data --batch-size 1000

# 2. Verify data integrity
python scripts/verify_migration.py --data-integrity

# 3. Test existing functionality
python run_tests.py --migration-test
```

#### Step 3: CRDT Integration (Medium Risk)
```bash
# 1. Enable CRDT features gradually
python main.py --enable-crdt --read-only  # Read-only CRDT mode first

# 2. Test read operations
python run_tests.py --crdt-read-tests

# 3. Test agent workflows with CRDT
python agent_launcher.py --crdt-test --cycles 10

# 4. Enable write operations
python main.py --enable-crdt --full

# 5. Run full test suite
python run_tests.py --all

# 6. Verify system dashboard
python system_dashboard.py --crdt-enabled
```

#### Step 4: Network Features (High Risk)
```bash
# 1. Enable local-only CRDT operations
python main.py --crdt-local-only

# 2. Test multi-instance on same machine
python scripts/test_multi_instance.py

# 3. Enable network synchronization
python main.py --crdt-network --test-mode

# 4. Gradual rollout to production nodes
```

### 8.3 Rollback Procedures
```python
# Automatic rollback triggers
ROLLBACK_TRIGGERS = {
    "health_score_drop": 85,      # If health drops below 85
    "test_failure_rate": 0.05,    # If >5% tests fail
    "sync_failure_rate": 0.10,    # If >10% syncs fail
    "data_corruption": True,      # Any data corruption detected
    "performance_degradation": 2.0  # If 2x slower than baseline
}

class MigrationManager:
    def check_rollback_conditions(self):
        """Check if rollback is needed"""
        current_health = self.get_health_score()
        if current_health < ROLLBACK_TRIGGERS["health_score_drop"]:
            self.trigger_rollback("Health score dropped to {current_health}")
        
        # Check other conditions...
    
    def execute_rollback(self, reason):
        """Execute automated rollback"""
        logger.critical(f"ROLLBACK TRIGGERED: {reason}")
        
        # 1. Stop CRDT operations
        self.crdt_manager.stop_all_operations()
        
        # 2. Restore from backup
        self.backup_manager.restore_latest_pre_migration_backup()
        
        # 3. Verify system health
        health_check = self.run_health_check()
        
        # 4. Notify administrators
        self.notify_administrators(f"Rollback completed. Health: {health_check}")
```

---

## 9. Performance Optimization

### 9.1 Delta Synchronization
```python
class DeltaSynchronizer:
    """Implement efficient delta-based synchronization"""
    
    def __init__(self):
        self.vector_clocks = {}
        self.operation_log = []
    
    def create_delta(self, target_node_id):
        """Create minimal delta for synchronization"""
        target_clock = self.vector_clocks.get(target_node_id, {})
        
        # Find operations newer than target's knowledge
        delta_operations = []
        for operation in self.operation_log:
            if self.is_newer_than_clock(operation, target_clock):
                delta_operations.append(operation)
        
        return CRDTDelta(
            operations=delta_operations,
            source_node=self.node_id,
            target_node=target_node_id,
            timestamp=time.time()
        )
    
    def apply_delta(self, delta):
        """Apply received delta efficiently"""
        applied_count = 0
        
        for operation in delta.operations:
            if self.should_apply_operation(operation):
                self.apply_operation(operation)
                applied_count += 1
        
        # Update vector clock
        self.update_vector_clock(delta.source_node, delta.timestamp)
        
        return applied_count
```

### 9.2 Compression and Batching
```python
class CRDTCompressor:
    """Compress CRDT operations for efficient storage and transmission"""
    
    def compress_operations(self, operations):
        """Compress batch of operations"""
        # Group similar operations
        grouped = self.group_operations(operations)
        
        # Apply compression algorithms
        compressed = {}
        for operation_type, ops in grouped.items():
            if operation_type == "g_counter_increment":
                compressed[operation_type] = self.compress_counter_ops(ops)
            elif operation_type == "or_set_add":
                compressed[operation_type] = self.compress_set_ops(ops)
            # ... other compressions
        
        return compressed
    
    def compress_counter_ops(self, counter_ops):
        """Compress multiple counter increments into single operation"""
        # Merge increments by node
        merged = {}
        for op in counter_ops:
            node = op.node_id
            merged[node] = merged.get(node, 0) + op.increment_value
        
        return [CounterIncrement(node, total) for node, total in merged.items()]
```

### 9.3 Lazy Synchronization
```python
class LazySynchronizer:
    """Implement lazy synchronization for better performance"""
    
    def __init__(self):
        self.sync_queue = PriorityQueue()
        self.sync_intervals = {}
        
    def schedule_sync(self, peer_node, priority="normal"):
        """Schedule synchronization with adaptive intervals"""
        # Determine sync interval based on activity and priority
        if priority == "critical":
            interval = 1  # 1 second
        elif priority == "high":
            interval = 10  # 10 seconds
        elif priority == "normal":
            interval = 60  # 1 minute
        else:  # low priority
            interval = 300  # 5 minutes
        
        # Adaptive interval based on recent activity
        recent_activity = self.get_recent_activity(peer_node)
        if recent_activity > 100:  # High activity
            interval = max(interval // 2, 1)
        elif recent_activity < 10:  # Low activity
            interval = min(interval * 2, 3600)
        
        sync_time = time.time() + interval
        self.sync_queue.put((sync_time, peer_node, priority))
```

---

## 10. Security Considerations

### 10.1 Authentication and Authorization
```python
class CRDTSecurityManager:
    """Manage security for CRDT operations"""
    
    def __init__(self):
        self.node_certificates = {}
        self.operation_signatures = {}
        
    def authenticate_node(self, node_id, certificate):
        """Authenticate peer node"""
        # Verify certificate against trusted CA
        if not self.verify_certificate(certificate):
            raise AuthenticationError(f"Invalid certificate for node {node_id}")
        
        # Check certificate validity
        if self.is_certificate_expired(certificate):
            raise AuthenticationError(f"Expired certificate for node {node_id}")
        
        # Store for future verification
        self.node_certificates[node_id] = certificate
        return True
    
    def sign_operation(self, operation, private_key):
        """Sign CRDT operation for integrity"""
        operation_hash = self.hash_operation(operation)
        signature = self.create_signature(operation_hash, private_key)
        
        self.operation_signatures[operation.id] = {
            "signature": signature,
            "hash": operation_hash,
            "timestamp": time.time()
        }
        
        return signature
    
    def verify_operation(self, operation, signature, node_certificate):
        """Verify CRDT operation integrity"""
        # Verify signature
        operation_hash = self.hash_operation(operation)
        public_key = self.extract_public_key(node_certificate)
        
        if not self.verify_signature(signature, operation_hash, public_key):
            raise SecurityError(f"Invalid signature for operation {operation.id}")
        
        # Check operation authorization
        if not self.is_operation_authorized(operation, node_certificate):
            raise AuthorizationError(f"Node not authorized for operation {operation.type}")
        
        return True
```

### 10.2 Encrypted Communication
```python
class SecureCRDTChannel:
    """Secure communication channel for CRDT synchronization"""
    
    def __init__(self, node_id, private_key, trusted_certificates):
        self.node_id = node_id
        self.private_key = private_key
        self.trusted_certs = trusted_certificates
        self.session_keys = {}
    
    def establish_secure_channel(self, peer_node_id):
        """Establish encrypted channel with peer"""
        # Key exchange using ECDH
        session_key = self.perform_key_exchange(peer_node_id)
        
        # Store session key
        self.session_keys[peer_node_id] = {
            "key": session_key,
            "established": time.time(),
            "last_used": time.time()
        }
        
        return session_key
    
    def encrypt_message(self, message, peer_node_id):
        """Encrypt message for secure transmission"""
        session_key = self.session_keys.get(peer_node_id)
        if not session_key:
            raise SecurityError(f"No secure channel with {peer_node_id}")
        
        # Encrypt using AES-GCM
        encrypted_data = self.aes_gcm_encrypt(message, session_key["key"])
        
        # Update last used timestamp
        session_key["last_used"] = time.time()
        
        return encrypted_data
    
    def decrypt_message(self, encrypted_message, peer_node_id):
        """Decrypt received message"""
        session_key = self.session_keys.get(peer_node_id)
        if not session_key:
            raise SecurityError(f"No secure channel with {peer_node_id}")
        
        # Decrypt message
        decrypted_data = self.aes_gcm_decrypt(encrypted_message, session_key["key"])
        
        return decrypted_data
```

### 10.3 Access Control
```python
class CRDTAccessControl:
    """Control access to CRDT operations based on roles and policies"""
    
    def __init__(self):
        self.access_policies = {}
        self.node_roles = {}
    
    def define_access_policy(self, crdt_name, policy):
        """Define access policy for CRDT"""
        self.access_policies[crdt_name] = {
            "read_roles": policy.get("read_roles", ["user", "admin"]),
            "write_roles": policy.get("write_roles", ["admin"]),
            "admin_roles": policy.get("admin_roles", ["admin"]),
            "operation_limits": policy.get("operation_limits", {}),
            "time_restrictions": policy.get("time_restrictions", {})
        }
    
    def check_operation_permission(self, node_id, crdt_name, operation_type):
        """Check if node has permission for operation"""
        node_role = self.node_roles.get(node_id, "guest")
        policy = self.access_policies.get(crdt_name)
        
        if not policy:
            # Default policy: admin only
            return node_role == "admin"
        
        # Check role-based permissions
        if operation_type in ["read", "query"]:
            allowed_roles = policy["read_roles"]
        elif operation_type in ["write", "modify", "add", "remove"]:
            allowed_roles = policy["write_roles"]
        else:
            allowed_roles = policy["admin_roles"]
        
        if node_role not in allowed_roles:
            return False
        
        # Check operation limits
        if not self.check_operation_limits(node_id, crdt_name, operation_type, policy):
            return False
        
        # Check time restrictions
        if not self.check_time_restrictions(operation_type, policy):
            return False
        
        return True
```

---

## 11. Deployment Strategy

### 11.1 Gradual Rollout Plan
```python
class CRDTDeploymentManager:
    """Manage gradual CRDT feature rollout"""
    
    def __init__(self):
        self.deployment_phases = {
            "phase_1": {  # Local CRDT only
                "features": ["local_crdt", "basic_types"],
                "nodes": ["primary"],
                "duration": "1 week",
                "success_criteria": {"health_score": 95, "test_pass_rate": 1.0}
            },
            "phase_2": {  # Two-node synchronization
                "features": ["local_crdt", "basic_types", "peer_sync"],
                "nodes": ["primary", "secondary"],
                "duration": "1 week",
                "success_criteria": {"health_score": 95, "sync_success_rate": 0.95}
            },
            "phase_3": {  # Full network
                "features": ["all_crdt_features"],
                "nodes": ["all"],
                "duration": "2 weeks",
                "success_criteria": {"health_score": 95, "network_partition_tolerance": True}
            }
        }
    
    def execute_phase(self, phase_name):
        """Execute deployment phase"""
        phase = self.deployment_phases[phase_name]
        
        # Enable features for specified nodes
        for node in phase["nodes"]:
            self.enable_features(node, phase["features"])
        
        # Monitor for duration
        start_time = time.time()
        duration_seconds = self.parse_duration(phase["duration"])
        
        while time.time() - start_time < duration_seconds:
            # Check success criteria
            if not self.check_success_criteria(phase["success_criteria"]):
                self.rollback_phase(phase_name)
                return False
            
            time.sleep(3600)  # Check hourly
        
        return True
    
    def rollback_phase(self, phase_name):
        """Rollback failed deployment phase"""
        logger.error(f"Rolling back deployment phase: {phase_name}")
        
        # Disable CRDT features
        for node in self.get_active_nodes():
            self.disable_crdt_features(node)
        
        # Restore previous state
        self.restore_pre_deployment_state()
```

### 11.2 Configuration Management
```python
# CRDT configuration file structure
CRDT_CONFIG = {
    "enabled": True,
    "node_id": "auto",  # Auto-generate or specify
    "network": {
        "enabled": True,
        "port": 8888,
        "discovery_method": "multicast",  # multicast, static, dns
        "peers": [],  # Static peer list if needed
        "encryption": True,
        "compression": True
    },
    "storage": {
        "backend": "sqlite",  # sqlite, postgresql, mongodb
        "path": "data/crdt_state.db",
        "backup_interval": "1h",
        "compression": True
    },
    "synchronization": {
        "mode": "lazy",  # lazy, eager, scheduled
        "batch_size": 1000,
        "max_delta_size": "10MB",
        "conflict_resolution": "automatic",
        "retry_attempts": 3,
        "retry_backoff": "exponential"
    },
    "security": {
        "authentication": True,
        "node_certificates": "config/certs/",
        "trusted_ca": "config/ca.pem",
        "operation_signing": True,
        "access_control": True
    },
    "monitoring": {
        "metrics_enabled": True,
        "health_checks": True,
        "performance_monitoring": True,
        "conflict_reporting": True
    },
    "debugging": {
        "log_level": "INFO",
        "operation_logging": False,
        "sync_debugging": False,
        "performance_profiling": False
    }
}
```

### 11.3 Monitoring and Alerting
```python
class CRDTMonitor:
    """Monitor CRDT system health and performance"""
    
    def __init__(self):
        self.metrics = {}
        self.alerts = {}
        
    def collect_metrics(self):
        """Collect CRDT-specific metrics"""
        return {
            "sync_metrics": {
                "successful_syncs": self.count_successful_syncs(),
                "failed_syncs": self.count_failed_syncs(),
                "average_sync_time": self.calculate_average_sync_time(),
                "delta_sizes": self.get_delta_size_stats(),
                "bandwidth_usage": self.calculate_bandwidth_usage()
            },
            "conflict_metrics": {
                "conflicts_detected": self.count_conflicts(),
                "conflicts_resolved": self.count_resolutions(),
                "manual_interventions": self.count_manual_interventions(),
                "conflict_types": self.categorize_conflicts()
            },
            "performance_metrics": {
                "operation_latency": self.measure_operation_latency(),
                "memory_usage": self.measure_memory_usage(),
                "cpu_usage": self.measure_cpu_usage(),
                "storage_growth": self.measure_storage_growth()
            },
            "health_metrics": {
                "node_connectivity": self.check_node_connectivity(),
                "data_consistency": self.verify_data_consistency(),
                "system_health_score": self.calculate_health_score()
            }
        }
    
    def setup_alerts(self):
        """Setup monitoring alerts"""
        self.alerts = {
            "sync_failure_rate_high": {
                "condition": "sync_failure_rate > 0.10",
                "action": "notify_admin",
                "severity": "high"
            },
            "conflict_rate_high": {
                "condition": "conflict_rate > 0.05",
                "action": "investigate_conflicts",
                "severity": "medium"
            },
            "node_disconnected": {
                "condition": "node_connectivity < 0.80",
                "action": "check_network",
                "severity": "high"
            },
            "memory_usage_high": {
                "condition": "memory_usage > 1GB",
                "action": "optimize_storage",
                "severity": "medium"
            }
        }
```

---

## 12. Monitoring & Maintenance

### 12.1 Health Dashboard Integration
```python
# Enhanced system_dashboard.py with CRDT metrics (v0.2 compatible)
class CRDTDashboard(SystemDashboard):
    """Enhanced dashboard with CRDT monitoring"""
    
    def get_crdt_health_metrics(self):
        """Get CRDT-specific health metrics"""
        return {
            "crdt_sync_status": self.check_sync_status(),
            "conflict_resolution_rate": self.calculate_conflict_resolution_rate(),
            "network_partition_resilience": self.test_partition_resilience(),
            "data_consistency_score": self.verify_consistency_across_nodes(),
            "performance_impact": self.measure_crdt_performance_impact(),
            "agent_workflow_sync": self.check_agent_sync_status()
        }
    
    def generate_crdt_health_report(self):
        """Generate comprehensive CRDT health report"""
        metrics = self.get_crdt_health_metrics()
        
        report = {
            "timestamp": datetime.utcnow().isoformat(),
            "overall_health": self.calculate_overall_crdt_health(metrics),
            "sync_health": {
                "status": metrics["crdt_sync_status"],
                "recommendations": self.get_sync_recommendations(metrics)
            },
            "conflict_health": {
                "resolution_rate": metrics["conflict_resolution_rate"],
                "recommendations": self.get_conflict_recommendations(metrics)
            },
            "network_health": {
                "partition_resilience": metrics["network_partition_resilience"],
                "recommendations": self.get_network_recommendations(metrics)
            },
            "consistency_health": {
                "score": metrics["data_consistency_score"],
                "recommendations": self.get_consistency_recommendations(metrics)
            }
        }
        
        return report
```

### 12.2 Automated Maintenance Tasks
```python
class CRDTMaintenanceManager:
    """Automated maintenance for CRDT system"""
    
    def __init__(self):
        self.maintenance_schedule = {
            "daily": [
                "cleanup_expired_vector_clocks",
                "optimize_storage",
                "verify_data_consistency",
                "backup_crdt_state"
            ],
            "weekly": [
                "deep_consistency_check",
                "performance_analysis",
                "conflict_pattern_analysis",
                "network_topology_optimization"
            ],
            "monthly": [
                "full_system_audit",
                "security_review",
                "capacity_planning",
                "disaster_recovery_test"
            ]
        }
    
    def cleanup_expired_vector_clocks(self):
        """Clean up old vector clock entries"""
        cutoff_time = time.time() - (30 * 24 * 3600)  # 30 days
        
        expired_clocks = self.find_expired_vector_clocks(cutoff_time)
        for clock_id in expired_clocks:
            self.remove_vector_clock(clock_id)
        
        logger.info(f"Cleaned up {len(expired_clocks)} expired vector clocks")
    
    def optimize_storage(self):
        """Optimize CRDT storage"""
        # Compress old operations
        old_operations = self.find_old_operations()
        compressed_ops = self.compress_operations(old_operations)
        
        # Remove redundant tombstones
        redundant_tombstones = self.find_redundant_tombstones()
        self.remove_tombstones(redundant_tombstones)
        
        # Vacuum database
        self.vacuum_crdt_database()
        
        logger.info("CRDT storage optimization completed")
    
    def verify_data_consistency(self):
        """Verify data consistency across all CRDT instances"""
        consistency_issues = []
        
        for crdt_name in self.get_all_crdt_names():
            crdt_instance = self.get_crdt_instance(crdt_name)
            
            # Check internal consistency
            if not crdt_instance.verify_internal_consistency():
                consistency_issues.append(f"Internal inconsistency in {crdt_name}")
            
            # Check consistency with peers
            for peer in self.get_active_peers():
                peer_state = self.get_peer_crdt_state(peer, crdt_name)
                if not self.verify_state_compatibility(crdt_instance.state, peer_state):
                    consistency_issues.append(f"Inconsistency with peer {peer} in {crdt_name}")
        
        if consistency_issues:
            logger.warning(f"Found {len(consistency_issues)} consistency issues")
            self.trigger_consistency_repair(consistency_issues)
        else:
            logger.info("All CRDT instances are consistent")
```

### 12.3 Performance Monitoring
```python
class CRDTPerformanceMonitor:
    """Monitor CRDT performance impact"""
    
    def __init__(self):
        self.baseline_metrics = self.establish_baseline()
        self.performance_thresholds = {
            "operation_latency": 100,  # milliseconds
            "sync_time": 5000,  # milliseconds
            "memory_overhead": 0.20,  # 20% increase
            "cpu_overhead": 0.15,  # 15% increase
        }
    
    def measure_operation_performance(self, operation_type):
        """Measure performance of CRDT operations"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss
        start_cpu = psutil.cpu_percent()
        
        # Execute operation
        result = self.execute_crdt_operation(operation_type)
        
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        end_cpu = psutil.cpu_percent()
        
        metrics = {
            "latency_ms": (end_time - start_time) * 1000,
            "memory_delta_mb": (end_memory - start_memory) / (1024 * 1024),
            "cpu_usage_percent": max(end_cpu - start_cpu, 0),
            "operation_success": result.success if result else False
        }
        
        # Check against thresholds
        self.check_performance_thresholds(metrics)
        
        return metrics
    
    def generate_performance_report(self):
        """Generate performance impact report"""
        current_metrics = self.collect_current_metrics()
        baseline_metrics = self.baseline_metrics
        
        impact_analysis = {
            "latency_impact": {
                "baseline": baseline_metrics["average_latency"],
                "current": current_metrics["average_latency"],
                "impact_percent": self.calculate_percentage_change(
                    baseline_metrics["average_latency"],
                    current_metrics["average_latency"]
                )
            },
            "memory_impact": {
                "baseline": baseline_metrics["memory_usage"],
                "current": current_metrics["memory_usage"],
                "impact_percent": self.calculate_percentage_change(
                    baseline_metrics["memory_usage"],
                    current_metrics["memory_usage"]
                )
            },
            "throughput_impact": {
                "baseline": baseline_metrics["operations_per_second"],
                "current": current_metrics["operations_per_second"],
                "impact_percent": self.calculate_percentage_change(
                    baseline_metrics["operations_per_second"],
                    current_metrics["operations_per_second"]
                )
            }
        }
        
        return impact_analysis
```

---

## Implementation Timeline & Resource Requirements

### Timeline Summary
- **Phase 1 (Foundation)**: 2 weeks
- **Phase 2 (Basic CRDT Types)**: 2 weeks  
- **Phase 3 (Advanced CRDT Types)**: 2 weeks
- **Phase 4 (Integration)**: 2 weeks
- **Phase 5 (Advanced Features)**: 2 weeks
- **Total Development Time**: 10 weeks

### Resource Requirements
- **Development**: 1 senior developer, 200+ hours
- **Testing**: Comprehensive test suite with distributed scenarios
- **Infrastructure**: Test environment with multiple nodes
- **Documentation**: Complete API documentation and operational guides

### Success Criteria (Updated for v0.2)
- ✅ Maintain 100/100 health score throughout implementation
- ✅ Preserve all 22 existing program functions (100% compatibility)
- ✅ Achieve 100% test coverage including CRDT scenarios (72+ tests)
- ✅ Support distributed deployment with conflict-free synchronization
- ✅ Maintain performance within 20% of baseline metrics
- ✅ Provide complete monitoring and operational tooling
- ✅ Ensure agent workflow compatibility with distributed operations
- ✅ Maintain system dashboard real-time monitoring capabilities

---

## Conclusion

This comprehensive CRDT implementation plan provides a structured approach to enhancing the Jarvis AI Assistant v0.2 with distributed, conflict-free data synchronization capabilities. The plan prioritizes:

1. **Backward Compatibility**: All existing functionality preserved (72/72 tests)
2. **Gradual Implementation**: Phased approach minimizes risk  
3. **Production Readiness**: Complete monitoring, security, and operational tooling
4. **Performance Optimization**: Efficient algorithms and lazy synchronization
5. **Comprehensive Testing**: Unit, integration, and distributed testing strategies
6. **Agent Workflow Integration**: Distributed agent testing and synchronization
7. **Real-time Monitoring**: Enhanced system dashboard with CRDT metrics

The implementation will transform Jarvis from a single-node system into a distributed, resilient AI assistant capable of operating across multiple nodes while maintaining data consistency, system reliability, and the robust agent workflow capabilities.

**Current System Status**: ✅ Ready for CRDT implementation
- Health Score: 100/100 (4/4 systems operational)
- Test Coverage: 100% (72/72 tests passing)  
- Data Integrity: 20,838 archive entries with verification
- Agent Workflows: 8 test scenarios with 100+ cycle capability
- Backup System: Automated with integrity verification

**Next Steps**: Begin with Phase 1 (Foundation) implementation, starting with the CRDT module structure and basic infrastructure components while preserving all current v0.2 functionality.