#!/usr/bin/env python3
"""
Phase 10: Specialized CRDT Extensions
Advanced domain-specific CRDT types for specialized use cases.
"""

import time
import json
from typing import Dict, Any, List, Optional, Set, Tuple, Union
from collections import defaultdict, OrderedDict
from datetime import datetime, timedelta
import threading
import uuid

from .crdt_base import BaseCRDT
from .or_set import ORSet
from .lww_register import LWWRegister
from .pn_counter import PNCounter


class TimeSeriesCRDT(BaseCRDT):
    """
    Specialized CRDT for high-frequency time-series data with conflict-free ordering.
    Designed for sensor data, metrics, and other chronological information.
    """
    
    def __init__(self, node_id: str = None, max_size: int = 10000):
        super().__init__(node_id)
        self.max_size = max_size
        self.data_points = OrderedDict()  # timestamp -> (value, node_id, sequence)
        self.aggregation_cache = LWWRegister(node_id)
        self.sequence_counters = defaultdict(int)
        self.lock = threading.Lock()
    
    def append_data_point(self, timestamp: float, value: Any, metadata: Dict[str, Any] = None) -> bool:
        """
        Append time-series data with conflict-free ordering.
        
        Args:
            timestamp: Unix timestamp
            value: Data value
            metadata: Optional metadata
            
        Returns:
            bool: Success status
        """
        with self.lock:
            self.sequence_counters[self.node_id] += 1
            sequence = self.sequence_counters[self.node_id]
            
            # Create unique key with tie-breaking
            key = (timestamp, self.node_id, sequence)
            
            entry = {
                'value': value,
                'node_id': self.node_id,
                'sequence': sequence,
                'metadata': metadata or {},
                'inserted_at': time.time()
            }
            
            self.data_points[key] = entry
            
            # Maintain size limit
            if len(self.data_points) > self.max_size:
                # Remove oldest entries
                excess = len(self.data_points) - self.max_size
                for _ in range(excess):
                    self.data_points.popitem(last=False)
            
            # Update aggregation cache
            self._update_aggregations()
            
            return True
    
    def get_range(self, start_time: float, end_time: float) -> List[Dict[str, Any]]:
        """Get data points within time range."""
        with self.lock:
            result = []
            for (timestamp, node_id, seq), entry in self.data_points.items():
                if start_time <= timestamp <= end_time:
                    result.append({
                        'timestamp': timestamp,
                        'value': entry['value'],
                        'node_id': node_id,
                        'metadata': entry['metadata']
                    })
            return sorted(result, key=lambda x: x['timestamp'])
    
    def get_latest(self, count: int = 1) -> List[Dict[str, Any]]:
        """Get latest data points."""
        with self.lock:
            items = list(self.data_points.items())[-count:]
            result = []
            for (timestamp, node_id, seq), entry in items:
                result.append({
                    'timestamp': timestamp,
                    'value': entry['value'],
                    'node_id': node_id,
                    'metadata': entry['metadata']
                })
            return result
    
    def _update_aggregations(self):
        """Update aggregation cache with current statistics."""
        if not self.data_points:
            return
            
        values = [entry['value'] for entry in self.data_points.values() 
                 if isinstance(entry['value'], (int, float))]
        
        if values:
            aggregations = {
                'count': len(self.data_points),
                'sum': sum(values),
                'avg': sum(values) / len(values),
                'min': min(values),
                'max': max(values),
                'latest_timestamp': max(key[0] for key in self.data_points.keys()),
                'updated_at': time.time()
            }
            self.aggregation_cache.write(aggregations)
    
    def merge(self, other: 'TimeSeriesCRDT') -> 'TimeSeriesCRDT':
        """Merge with another TimeSeriesCRDT."""
        with self.lock:
            # Merge data points (order preserved due to timestamp-based keys)
            for key, entry in other.data_points.items():
                if key not in self.data_points:
                    self.data_points[key] = entry
            
            # Sort by timestamp to maintain order
            self.data_points = OrderedDict(sorted(self.data_points.items()))
            
            # Merge sequence counters
            for node_id, seq in other.sequence_counters.items():
                self.sequence_counters[node_id] = max(
                    self.sequence_counters[node_id], seq
                )
            
            # Merge aggregation cache
            self.aggregation_cache = self.aggregation_cache.merge(other.aggregation_cache)
            
            # Maintain size limit
            if len(self.data_points) > self.max_size:
                excess = len(self.data_points) - self.max_size
                for _ in range(excess):
                    self.data_points.popitem(last=False)
            
            self._update_aggregations()
            self.update_metadata()
            return self
    
    def value(self) -> List[Dict[str, Any]]:
        """Get current value as list of all data points."""
        with self.lock:
            result = []
            for (timestamp, node_id, seq), entry in self.data_points.items():
                result.append({
                    'timestamp': timestamp,
                    'value': entry['value'],
                    'node_id': node_id,
                    'sequence': seq,
                    'metadata': entry['metadata']
                })
            return result
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Deserialize from dictionary."""
        self.node_id = data.get('node_id', self.node_id)
        self.max_size = data.get('max_size', self.max_size)
        
        # Restore data points
        self.data_points = OrderedDict()
        if 'data_points' in data:
            for key_str, entry in data['data_points'].items():
                # Parse key from string representation
                try:
                    key = eval(key_str)  # Safe for tuple keys
                    self.data_points[key] = entry
                except:
                    continue
        
        # Restore sequence counters
        if 'sequence_counters' in data:
            self.sequence_counters = defaultdict(int, data['sequence_counters'])
        
        # Restore aggregation cache
        if 'aggregation_cache' in data:
            self.aggregation_cache.from_dict(data['aggregation_cache'])
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'node_id': self.node_id,
            'data_points': {str(k): v for k, v in self.data_points.items()},
            'aggregation_cache': self.aggregation_cache.to_dict(),
            'sequence_counters': dict(self.sequence_counters),
            'max_size': self.max_size,
            **self.get_metadata()
        }


class GraphCRDT(BaseCRDT):
    """
    Specialized CRDT for relationship graphs with conflict-free edge and vertex operations.
    Ideal for social networks, knowledge graphs, and dependency modeling.
    """
    
    def __init__(self, node_id: str = None):
        super().__init__(node_id)
        self.vertices = ORSet(node_id)  # Set of vertex IDs
        self.edges = ORSet(node_id)     # Set of edge tuples
        self.vertex_data = {}           # vertex_id -> LWWRegister
        self.edge_data = {}             # edge_id -> LWWRegister
        self.lock = threading.Lock()
    
    def add_vertex(self, vertex_id: str, data: Dict[str, Any] = None) -> bool:
        """Add vertex to graph."""
        with self.lock:
            # Add vertex to set
            self.vertices.add(vertex_id)
            
            # Initialize vertex data
            if vertex_id not in self.vertex_data:
                self.vertex_data[vertex_id] = LWWRegister(self.node_id)
            
            if data:
                self.vertex_data[vertex_id].write(data)
            
            return True
    
    def remove_vertex(self, vertex_id: str) -> bool:
        """Remove vertex and all its edges."""
        with self.lock:
            if vertex_id not in self.vertices.elements():
                return False
            
            # Remove vertex
            self.vertices.remove(vertex_id)
            
            # Remove all edges connected to this vertex
            edges_to_remove = []
            for edge in self.edges.elements():
                if isinstance(edge, tuple) and (edge[0] == vertex_id or edge[1] == vertex_id):
                    edges_to_remove.append(edge)
            
            for edge in edges_to_remove:
                self.edges.remove(edge)
                edge_id = f"{edge[0]}-{edge[1]}"
                if edge_id in self.edge_data:
                    del self.edge_data[edge_id]
            
            # Clean up vertex data
            if vertex_id in self.vertex_data:
                del self.vertex_data[vertex_id]
            
            return True
    
    def add_edge(self, from_vertex: str, to_vertex: str, data: Dict[str, Any] = None, directed: bool = True) -> bool:
        """Add edge between vertices."""
        with self.lock:
            # Ensure vertices exist
            if from_vertex not in self.vertices.elements() or to_vertex not in self.vertices.elements():
                return False
            
            # Create edge tuple
            edge = (from_vertex, to_vertex)
            if not directed:
                # For undirected edges, ensure consistent ordering
                edge = tuple(sorted([from_vertex, to_vertex]))
            
            # Add edge to set
            self.edges.add(edge)
            
            # Initialize edge data
            edge_id = f"{edge[0]}-{edge[1]}"
            if edge_id not in self.edge_data:
                self.edge_data[edge_id] = LWWRegister(self.node_id)
            
            if data:
                self.edge_data[edge_id].write(data)
            
            return True
    
    def remove_edge(self, from_vertex: str, to_vertex: str, directed: bool = True) -> bool:
        """Remove edge between vertices."""
        with self.lock:
            edge = (from_vertex, to_vertex)
            if not directed:
                edge = tuple(sorted([from_vertex, to_vertex]))
            
            if edge in self.edges.elements():
                self.edges.remove(edge)
                edge_id = f"{edge[0]}-{edge[1]}"
                if edge_id in self.edge_data:
                    del self.edge_data[edge_id]
                return True
            
            return False
    
    def get_neighbors(self, vertex_id: str, direction: str = "out") -> List[str]:
        """
        Get neighboring vertices.
        
        Args:
            vertex_id: Source vertex
            direction: "out", "in", or "both"
        """
        with self.lock:
            neighbors = set()
            
            for edge in self.edges.elements():
                if isinstance(edge, tuple) and len(edge) == 2:
                    from_v, to_v = edge
                    
                    if direction in ("out", "both") and from_v == vertex_id:
                        neighbors.add(to_v)
                    
                    if direction in ("in", "both") and to_v == vertex_id:
                        neighbors.add(from_v)
            
            return list(neighbors)
    
    def get_path(self, start: str, end: str, max_depth: int = 10) -> List[str]:
        """Find shortest path between vertices using BFS."""
        with self.lock:
            if start not in self.vertices.elements() or end not in self.vertices.elements():
                return []
            
            if start == end:
                return [start]
            
            queue = [(start, [start])]
            visited = {start}
            
            for _ in range(max_depth):
                if not queue:
                    break
                
                current, path = queue.pop(0)
                
                for neighbor in self.get_neighbors(current, "both"):
                    if neighbor == end:
                        return path + [neighbor]
                    
                    if neighbor not in visited:
                        visited.add(neighbor)
                        queue.append((neighbor, path + [neighbor]))
            
            return []  # No path found
    
    def get_subgraph(self, vertex_ids: List[str]) -> Dict[str, Any]:
        """Extract subgraph containing specified vertices."""
        with self.lock:
            subgraph = {
                'vertices': {},
                'edges': []
            }
            
            # Get vertex data
            for vertex_id in vertex_ids:
                if vertex_id in self.vertices.elements():
                    subgraph['vertices'][vertex_id] = (
                        self.vertex_data[vertex_id].value() 
                        if vertex_id in self.vertex_data 
                        else {}
                    )
            
            # Get edges within subgraph
            for edge in self.edges.elements():
                if isinstance(edge, tuple) and len(edge) == 2:
                    from_v, to_v = edge
                    if from_v in vertex_ids and to_v in vertex_ids:
                        edge_id = f"{from_v}-{to_v}"
                        edge_data = (
                            self.edge_data[edge_id].value
                            if edge_id in self.edge_data
                            else {}
                        )
                        subgraph['edges'].append({
                            'from': from_v,
                            'to': to_v,
                            'data': edge_data
                        })
            
            return subgraph
    
    def merge(self, other: 'GraphCRDT') -> 'GraphCRDT':
        """Merge with another GraphCRDT."""
        with self.lock:
            # Merge vertices and edges
            self.vertices = self.vertices.merge(other.vertices)
            self.edges = self.edges.merge(other.edges)
            
            # Merge vertex data
            for vertex_id, lww_register in other.vertex_data.items():
                if vertex_id not in self.vertex_data:
                    self.vertex_data[vertex_id] = LWWRegister(self.node_id)
                self.vertex_data[vertex_id] = self.vertex_data[vertex_id].merge(lww_register)
            
            # Merge edge data
            for edge_id, lww_register in other.edge_data.items():
                if edge_id not in self.edge_data:
                    self.edge_data[edge_id] = LWWRegister(self.node_id)
                self.edge_data[edge_id] = self.edge_data[edge_id].merge(lww_register)
            
            self.update_metadata()
            return self
    
    def value(self) -> Dict[str, Any]:
        """Get current value as graph representation."""
        with self.lock:
            return {
                'vertices': list(self.vertices.elements()),
                'edges': [list(edge) for edge in self.edges.elements() if isinstance(edge, tuple)],
                'vertex_count': len(self.vertices.elements()),
                'edge_count': len(self.edges.elements())
            }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Deserialize from dictionary."""
        self.node_id = data.get('node_id', self.node_id)
        
        # Restore vertices and edges
        if 'vertices' in data:
            self.vertices.from_dict(data['vertices'])
        if 'edges' in data:
            self.edges.from_dict(data['edges'])
        
        # Restore vertex data
        self.vertex_data = {}
        if 'vertex_data' in data:
            for vertex_id, lww_data in data['vertex_data'].items():
                self.vertex_data[vertex_id] = LWWRegister(self.node_id)
                self.vertex_data[vertex_id].from_dict(lww_data)
        
        # Restore edge data
        self.edge_data = {}
        if 'edge_data' in data:
            for edge_id, lww_data in data['edge_data'].items():
                self.edge_data[edge_id] = LWWRegister(self.node_id)
                self.edge_data[edge_id].from_dict(lww_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'node_id': self.node_id,
            'vertices': self.vertices.to_dict(),
            'edges': self.edges.to_dict(),
            'vertex_data': {k: v.to_dict() for k, v in self.vertex_data.items()},
            'edge_data': {k: v.to_dict() for k, v in self.edge_data.items()},
            **self.get_metadata()
        }


class WorkflowCRDT(BaseCRDT):
    """
    Specialized CRDT for complex workflow and state machine coordination.
    Enables distributed business process automation with conflict-free state transitions.
    """
    
    def __init__(self, node_id: str = None, workflow_id: str = None):
        super().__init__(node_id)
        self.workflow_id = workflow_id or str(uuid.uuid4())
        self.states = ORSet(node_id)                    # Available states
        self.transitions = ORSet(node_id)               # Valid transitions
        self.current_state = LWWRegister(node_id)       # Current workflow state
        self.state_data = {}                            # state -> LWWRegister for state data
        self.transition_history = ORSet(node_id)        # History of transitions
        self.step_counters = PNCounter(node_id)         # Step execution counters
        self.lock = threading.Lock()
    
    def add_state(self, state_id: str, data: Dict[str, Any] = None) -> bool:
        """Add a state to the workflow."""
        with self.lock:
            self.states.add(state_id)
            
            if state_id not in self.state_data:
                self.state_data[state_id] = LWWRegister(self.node_id)
            
            if data:
                self.state_data[state_id].write(data)
            
            return True
    
    def add_transition(self, from_state: str, to_state: str, condition: str = None, action: str = None) -> bool:
        """Add a valid transition between states."""
        with self.lock:
            # Ensure states exist
            if from_state not in self.states.elements() or to_state not in self.states.elements():
                return False
            
            transition = {
                'from': from_state,
                'to': to_state,
                'condition': condition,
                'action': action,
                'id': f"{from_state}->{to_state}"
            }
            
            self.transitions.add(json.dumps(transition, sort_keys=True))
            return True
    
    def transition_to(self, new_state: str, context: Dict[str, Any] = None) -> bool:
        """Attempt to transition to a new state."""
        with self.lock:
            current = self.current_state.value()
            
            # Check if transition is valid
            if current and not self._is_valid_transition(current, new_state):
                return False
            
            # Record transition in history
            transition_record = {
                'from': current,
                'to': new_state,
                'timestamp': time.time(),
                'node_id': self.node_id,
                'context': context or {},
                'id': str(uuid.uuid4())
            }
            
            self.transition_history.add(json.dumps(transition_record, sort_keys=True))
            
            # Update current state
            self.current_state.write(new_state)
            
            # Increment step counter
            self.step_counters.increment()
            
            return True
    
    def _is_valid_transition(self, from_state: str, to_state: str) -> bool:
        """Check if transition is valid based on defined transitions."""
        for transition_json in self.transitions.elements():
            try:
                transition = json.loads(transition_json)
                if transition['from'] == from_state and transition['to'] == to_state:
                    return True
            except (json.JSONDecodeError, KeyError):
                continue
        
        return False
    
    def get_available_transitions(self) -> List[Dict[str, Any]]:
        """Get available transitions from current state."""
        with self.lock:
            current = self.current_state.value()
            if not current:
                return []
            
            available = []
            for transition_json in self.transitions.elements():
                try:
                    transition = json.loads(transition_json)
                    if transition['from'] == current:
                        available.append(transition)
                except (json.JSONDecodeError, KeyError):
                    continue
            
            return available
    
    def get_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get transition history."""
        with self.lock:
            history = []
            for record_json in self.transition_history.elements():
                try:
                    record = json.loads(record_json)
                    history.append(record)
                except json.JSONDecodeError:
                    continue
            
            # Sort by timestamp
            history.sort(key=lambda x: x.get('timestamp', 0))
            
            if limit:
                history = history[-limit:]
            
            return history
    
    def get_state_statistics(self) -> Dict[str, Any]:
        """Get workflow execution statistics."""
        with self.lock:
            history = self.get_history()
            
            state_visits = defaultdict(int)
            transition_counts = defaultdict(int)
            
            for record in history:
                if record.get('to'):
                    state_visits[record['to']] += 1
                
                if record.get('from') and record.get('to'):
                    transition_key = f"{record['from']}->{record['to']}"
                    transition_counts[transition_key] += 1
            
            return {
                'current_state': self.current_state.value(),
                'total_steps': self.step_counters.value(),
                'state_visits': dict(state_visits),
                'transition_counts': dict(transition_counts),
                'total_transitions': len(history),
                'available_states': len(self.states.elements()),
                'defined_transitions': len(self.transitions.elements())
            }
    
    def reset_workflow(self, initial_state: str = None) -> bool:
        """Reset workflow to initial state."""
        with self.lock:
            if initial_state and initial_state not in self.states.elements():
                return False
            
            # Clear current state or set to initial
            if initial_state:
                self.current_state.write(initial_state)
            else:
                self.current_state.write(None)
            
            # Add reset record to history
            reset_record = {
                'from': None,
                'to': initial_state,
                'timestamp': time.time(),
                'node_id': self.node_id,
                'context': {'action': 'reset'},
                'id': str(uuid.uuid4())
            }
            
            self.transition_history.add(json.dumps(reset_record, sort_keys=True))
            
            return True
    
    def merge(self, other: 'WorkflowCRDT') -> 'WorkflowCRDT':
        """Merge with another WorkflowCRDT."""
        with self.lock:
            # Merge basic CRDT components
            self.states = self.states.merge(other.states)
            self.transitions = self.transitions.merge(other.transitions)
            self.current_state = self.current_state.merge(other.current_state)
            self.transition_history = self.transition_history.merge(other.transition_history)
            self.step_counters = self.step_counters.merge(other.step_counters)
            
            # Merge state data
            for state_id, lww_register in other.state_data.items():
                if state_id not in self.state_data:
                    self.state_data[state_id] = LWWRegister(self.node_id)
                self.state_data[state_id] = self.state_data[state_id].merge(lww_register)
            
            self.update_metadata()
            return self
    
    def value(self) -> Dict[str, Any]:
        """Get current value as workflow state."""
        with self.lock:
            return {
                'workflow_id': self.workflow_id,
                'current_state': self.current_state.value(),
                'states': list(self.states.elements()),
                'total_steps': self.step_counters.value(),
                'state_count': len(self.states.elements()),
                'transition_count': len(self.transitions.elements()),
                'history_length': len(self.transition_history.elements())
            }
    
    def from_dict(self, data: Dict[str, Any]) -> None:
        """Deserialize from dictionary."""
        self.node_id = data.get('node_id', self.node_id)
        self.workflow_id = data.get('workflow_id', self.workflow_id)
        
        # Restore CRDT components
        if 'states' in data:
            self.states.from_dict(data['states'])
        if 'transitions' in data:
            self.transitions.from_dict(data['transitions'])
        if 'current_state' in data:
            self.current_state.from_dict(data['current_state'])
        if 'transition_history' in data:
            self.transition_history.from_dict(data['transition_history'])
        if 'step_counters' in data:
            self.step_counters.from_dict(data['step_counters'])
        
        # Restore state data
        self.state_data = {}
        if 'state_data' in data:
            for state_id, lww_data in data['state_data'].items():
                self.state_data[state_id] = LWWRegister(self.node_id)
                self.state_data[state_id].from_dict(lww_data)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            'node_id': self.node_id,
            'workflow_id': self.workflow_id,
            'states': self.states.to_dict(),
            'transitions': self.transitions.to_dict(),
            'current_state': self.current_state.to_dict(),
            'state_data': {k: v.to_dict() for k, v in self.state_data.items()},
            'transition_history': self.transition_history.to_dict(),
            'step_counters': self.step_counters.to_dict(),
            **self.get_metadata()
        }


# Convenience factory functions
def create_time_series(node_id: str = None, max_size: int = 10000) -> TimeSeriesCRDT:
    """Create a new TimeSeriesCRDT instance."""
    return TimeSeriesCRDT(node_id, max_size)


def create_graph(node_id: str = None) -> GraphCRDT:
    """Create a new GraphCRDT instance."""
    return GraphCRDT(node_id)


def create_workflow(node_id: str = None, workflow_id: str = None) -> WorkflowCRDT:
    """Create a new WorkflowCRDT instance."""
    return WorkflowCRDT(node_id, workflow_id)