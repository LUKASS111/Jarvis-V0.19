# Specialized CRDT Types API Documentation

## Overview

Phase 10 introduces three specialized CRDT types designed for domain-specific use cases while maintaining all mathematical guarantees of conflict-free operations.

## TimeSeriesCRDT

### Purpose
High-frequency time-series data storage with conflict-free ordering and aggregation capabilities. Designed for sensor data, metrics, and chronological information.

### Class Definition
```python
from jarvis.core.crdt.specialized_types import TimeSeriesCRDT

# Create instance
ts_crdt = TimeSeriesCRDT(node_id="node1", max_size=10000)
```

### Key Methods

#### `append_data_point(timestamp, value, metadata=None)`
Append time-series data with conflict-free ordering.

**Parameters:**
- `timestamp` (float): Unix timestamp
- `value` (Any): Data value
- `metadata` (Dict[str, Any], optional): Additional metadata

**Returns:**
- `bool`: Success status

**Example:**
```python
import time

# Append sensor data
success = ts_crdt.append_data_point(
    timestamp=time.time(),
    value=23.5,
    metadata={"sensor_id": "temp_01", "location": "room_a"}
)
```

#### `get_range(start_time, end_time)`
Retrieve data points within time range.

**Parameters:**
- `start_time` (float): Start timestamp
- `end_time` (float): End timestamp

**Returns:**
- `List[Tuple]`: List of (timestamp, value, metadata) tuples

#### `aggregate(start_time, end_time, operation="mean")`
Perform aggregation operations on time range.

**Operations:**
- `"mean"`: Average value
- `"sum"`: Total sum
- `"count"`: Number of points
- `"min"`: Minimum value
- `"max"`: Maximum value

---

## GraphCRDT

### Purpose
Distributed graph data structure supporting conflict-free vertex and edge operations with relationship management.

### Class Definition
```python
from jarvis.core.crdt.specialized_types import GraphCRDT

# Create instance
graph_crdt = GraphCRDT(node_id="node1")
```

### Key Methods

#### `add_vertex(vertex_id, data=None)`
Add vertex to graph with conflict-free operations.

**Parameters:**
- `vertex_id` (str): Unique vertex identifier
- `data` (Dict[str, Any], optional): Vertex data

**Returns:**
- `bool`: Success status

**Example:**
```python
# Add user vertex
graph_crdt.add_vertex("user_123", {
    "name": "Alice",
    "role": "developer",
    "created_at": "2024-01-01"
})
```

#### `add_edge(source, target, edge_data=None)`
Add directed edge between vertices.

**Parameters:**
- `source` (str): Source vertex ID
- `target` (str): Target vertex ID  
- `edge_data` (Dict[str, Any], optional): Edge metadata

**Returns:**
- `bool`: Success status

#### `remove_edge(source, target)`
Remove edge between vertices (conflict-free).

#### `get_neighbors(vertex_id)`
Get all neighboring vertices.

**Returns:**
- `List[str]`: List of neighbor vertex IDs

#### `find_path(source, target, max_depth=10)`
Find path between vertices using breadth-first search.

**Returns:**
- `List[str]`: Path as list of vertex IDs, or empty list if no path

---

## WorkflowCRDT

### Purpose
Complex workflow and state machine coordination with conflict-free state transitions and history tracking.

### Class Definition
```python
from jarvis.core.crdt.specialized_types import WorkflowCRDT

# Create instance
workflow_crdt = WorkflowCRDT(node_id="node1")
```

### Key Methods

#### `transition_to(new_state, data=None)`
Perform state transition with conflict resolution.

**Parameters:**
- `new_state` (str): Target state name
- `data` (Dict[str, Any], optional): Transition data

**Returns:**
- `bool`: Success status

**Example:**
```python
# Initialize workflow
workflow_crdt.transition_to("initialized", {
    "workflow_id": "deploy_001",
    "version": "1.0.0"
})

# Progress through states
workflow_crdt.transition_to("running", {"start_time": time.time()})
workflow_crdt.transition_to("completed", {"end_time": time.time()})
```

#### `get_current_state()`
Get current workflow state.

**Returns:**
- `str`: Current state name

#### `get_state_history()`
Get complete state transition history.

**Returns:**
- `List[Dict]`: History entries with timestamps and data

#### `can_transition_to(target_state)`
Check if transition to target state is valid.

**Returns:**
- `bool`: True if transition is allowed

---

## Factory Functions

### Convenience Creation Functions

```python
from jarvis.core.crdt.specialized_types import (
    create_timeseries_crdt,
    create_graph_crdt, 
    create_workflow_crdt
)

# Create with defaults
ts = create_timeseries_crdt("sensor_node")
graph = create_graph_crdt("social_network")
workflow = create_workflow_crdt("deployment_pipeline")
```

---

## Integration Examples

### Multi-Node Synchronization

```python
from jarvis.core.crdt_manager import get_crdt_manager

# Get CRDT manager
manager = get_crdt_manager()

# Create and register specialized CRDTs
ts_crdt = create_timeseries_crdt("metrics_collector")
manager.register_crdt("system_metrics", ts_crdt)

# Automatic synchronization with other nodes
sync_result = manager.sync_with_peers()
```

### Cross-CRDT Operations

```python
# Combine different CRDT types
user_graph = create_graph_crdt("users")
user_workflow = create_workflow_crdt("user_onboarding")

# Add user and track workflow
user_graph.add_vertex("user_456", {"name": "Bob"})
user_workflow.transition_to("registration_complete", {
    "user_id": "user_456",
    "timestamp": time.time()
})
```

---

## Mathematical Guarantees

All specialized CRDT types maintain core CRDT properties:

### Convergence
All nodes reach identical state after synchronization, regardless of operation order or network partitions.

### Commutativity  
Operations can be applied in any order with identical results.

### Associativity
Operation grouping does not affect final state.

### Idempotence
Duplicate operations are safely ignored.

---

## Performance Characteristics

### TimeSeriesCRDT
- **Memory**: O(n) where n = number of data points
- **Insertion**: O(log n) with automatic ordering
- **Range Query**: O(log n + k) where k = result size
- **Aggregation**: O(k) for range aggregations

### GraphCRDT
- **Memory**: O(V + E) where V = vertices, E = edges
- **Vertex Operations**: O(1) for add/remove
- **Edge Operations**: O(1) for add/remove
- **Path Finding**: O(V + E) breadth-first search

### WorkflowCRDT
- **Memory**: O(s) where s = number of states
- **State Transition**: O(1) for valid transitions
- **History Retrieval**: O(h) where h = history length
- **Validation**: O(1) for transition checking

---

## Error Handling

### Common Exceptions

```python
from jarvis.core.errors import CRDTException

try:
    # Specialized CRDT operations
    result = ts_crdt.append_data_point(timestamp, value)
except CRDTException as e:
    # Handle CRDT-specific errors
    print(f"CRDT operation failed: {e}")
```

### Validation

All specialized CRDTs include built-in validation:
- Timestamp validation for TimeSeriesCRDT
- Vertex existence checking for GraphCRDT  
- State transition validation for WorkflowCRDT

---

## Best Practices

### TimeSeriesCRDT
1. Use consistent timestamp sources across nodes
2. Set appropriate max_size to prevent memory issues
3. Aggregate data regularly for performance
4. Use metadata for efficient filtering

### GraphCRDT
1. Use meaningful vertex IDs for debugging
2. Validate vertex existence before adding edges
3. Consider graph size for path-finding operations
4. Use edge metadata for relationship types

### WorkflowCRDT
1. Define clear state machine before implementation
2. Use descriptive state names
3. Include relevant data in transitions
4. Monitor workflow history for debugging

---

## Testing

### Unit Testing Examples

```python
import unittest
from jarvis.core.crdt.specialized_types import TimeSeriesCRDT

class TestTimeSeriesCRDT(unittest.TestCase):
    def test_append_data_point(self):
        ts = TimeSeriesCRDT("test_node")
        result = ts.append_data_point(1640995200.0, 42.0)
        self.assertTrue(result)
        
    def test_conflict_free_merge(self):
        ts1 = TimeSeriesCRDT("node1")
        ts2 = TimeSeriesCRDT("node2")
        
        # Add different data points
        ts1.append_data_point(1640995200.0, 10.0)
        ts2.append_data_point(1640995300.0, 20.0)
        
        # Merge should be conflict-free
        ts1.merge(ts2)
        self.assertEqual(len(ts1.data_points), 2)
```

### Integration Testing

```python
def test_distributed_specialization():
    """Test specialized CRDTs in distributed environment"""
    # Create multiple nodes
    nodes = [create_timeseries_crdt(f"node_{i}") for i in range(3)]
    
    # Add data on different nodes
    for i, node in enumerate(nodes):
        node.append_data_point(time.time() + i, i * 10)
    
    # Merge all nodes
    for i in range(1, len(nodes)):
        nodes[0].merge(nodes[i])
    
    # Verify convergence
    assert len(nodes[0].data_points) == 3
```

This documentation provides comprehensive coverage of the Phase 10 specialized CRDT extensions with practical examples and integration guidance.