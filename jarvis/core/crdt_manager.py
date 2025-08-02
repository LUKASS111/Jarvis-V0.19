"""
CRDT Manager - Integration Layer
================================

Manages CRDT instances and integrates with existing Jarvis v0.2 architecture.
Provides unified interface for distributed data operations.

Priority: Mathematical correctness and architectural advancement.
"""

import json
import sqlite3
import threading
from typing import Dict, Any, Optional, List
from .crdt import GCounter, GSet, LWWRegister


class CRDTManager:
    """
    Central manager for all CRDT instances.
    Integrates with existing SQLite database and archiving system.
    """
    
    def __init__(self, node_id: str, db_path: str = "data/jarvis_archive.db"):
        """Initialize CRDT manager with node ID and database path."""
        self.node_id = node_id
        self.db_path = db_path
        self.lock = threading.Lock()
        
        # CRDT instances registry
        self.crdts: Dict[str, Any] = {}
        
        # Initialize database schema for CRDT support
        self._initialize_crdt_schema()
        
        # Load existing CRDT states
        self._load_crdt_states()
    
    def _initialize_crdt_schema(self) -> None:
        """Add CRDT tables to existing database schema."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Add CRDT columns to existing archive_entries table
            try:
                cursor.execute("""
                    ALTER TABLE archive_entries ADD COLUMN crdt_type TEXT
                """)
            except sqlite3.OperationalError:
                pass  # Column already exists
            
            try:
                cursor.execute("""
                    ALTER TABLE archive_entries ADD COLUMN crdt_node_id TEXT
                """)
            except sqlite3.OperationalError:
                pass
            
            try:
                cursor.execute("""
                    ALTER TABLE archive_entries ADD COLUMN crdt_operation_id TEXT
                """)
            except sqlite3.OperationalError:
                pass
            
            # Create CRDT states table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS crdt_states (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    crdt_name TEXT UNIQUE NOT NULL,
                    crdt_type TEXT NOT NULL,
                    state_data TEXT NOT NULL,
                    last_updated TEXT NOT NULL,
                    version INTEGER DEFAULT 1,
                    node_id TEXT NOT NULL
                )
            """)
            
            conn.commit()
    
    def _load_crdt_states(self) -> None:
        """Load existing CRDT states from database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT crdt_name, crdt_type, state_data 
                FROM crdt_states
            """)
            
            for name, crdt_type, state_data in cursor.fetchall():
                state_dict = json.loads(state_data)
                
                if crdt_type == "GCounter":
                    crdt = GCounter(self.node_id)
                elif crdt_type == "GSet":
                    crdt = GSet(self.node_id)
                elif crdt_type == "LWWRegister":
                    crdt = LWWRegister(self.node_id)
                else:
                    continue  # Unknown CRDT type
                
                crdt.from_dict(state_dict)
                self.crdts[name] = crdt
    
    def get_or_create_crdt(self, name: str, crdt_type: str, **kwargs) -> Any:
        """Get existing CRDT or create new one."""
        with self.lock:
            if name in self.crdts:
                return self.crdts[name]
            
            # Create new CRDT
            if crdt_type == "GCounter":
                crdt = GCounter(self.node_id)
            elif crdt_type == "GSet":
                crdt = GSet(self.node_id)
            elif crdt_type == "LWWRegister":
                initial_value = kwargs.get("initial_value")
                crdt = LWWRegister(self.node_id, initial_value)
            else:
                raise ValueError(f"Unknown CRDT type: {crdt_type}")
            
            self.crdts[name] = crdt
            self._persist_crdt_state(name, crdt)
            return crdt
    
    def _persist_crdt_state(self, name: str, crdt: Any) -> None:
        """Persist CRDT state to database."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            state_data = crdt.to_json()
            crdt_type = crdt.__class__.__name__
            
            cursor.execute("""
                INSERT OR REPLACE INTO crdt_states 
                (crdt_name, crdt_type, state_data, last_updated, version, node_id)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (name, crdt_type, state_data, crdt.last_updated, crdt.version, self.node_id))
            
            conn.commit()
    
    def increment_counter(self, name: str, amount: int = 1) -> int:
        """Increment a G-Counter."""
        counter = self.get_or_create_crdt(name, "GCounter")
        counter.increment(amount)
        self._persist_crdt_state(name, counter)
        return counter.value()
    
    def add_to_set(self, name: str, element: Any) -> bool:
        """Add element to G-Set."""
        gset = self.get_or_create_crdt(name, "GSet")
        was_present = gset.contains(element)
        gset.add(element)
        self._persist_crdt_state(name, gset)
        return not was_present  # Return True if newly added
    
    def write_register(self, name: str, value: Any) -> Any:
        """Write value to LWW-Register."""
        register = self.get_or_create_crdt(name, "LWWRegister")
        register.write(value)
        self._persist_crdt_state(name, register)
        return register.value()
    
    def read_register(self, name: str, default: Any = None) -> Any:
        """Read value from LWW-Register."""
        if name in self.crdts:
            return self.crdts[name].value()
        return default
    
    def get_counter_value(self, name: str) -> int:
        """Get current value of G-Counter."""
        if name in self.crdts:
            return self.crdts[name].value()
        return 0
    
    def set_contains(self, name: str, element: Any) -> bool:
        """Check if G-Set contains element."""
        if name in self.crdts:
            return self.crdts[name].contains(element)
        return False
    
    def get_set_size(self, name: str) -> int:
        """Get size of G-Set."""
        if name in self.crdts:
            return self.crdts[name].size()
        return 0
    
    def merge_crdt(self, name: str, other_state: Dict[str, Any]) -> None:
        """Merge CRDT with external state."""
        if name not in self.crdts:
            return
        
        with self.lock:
            crdt = self.crdts[name]
            crdt_type = crdt.__class__.__name__
            
            # Create temporary CRDT from other state
            if crdt_type == "GCounter":
                other_crdt = GCounter(self.node_id)
            elif crdt_type == "GSet":
                other_crdt = GSet(self.node_id)
            elif crdt_type == "LWWRegister":
                other_crdt = LWWRegister(self.node_id)
            else:
                return
            
            other_crdt.from_dict(other_state)
            crdt.merge(other_crdt)
            self._persist_crdt_state(name, crdt)
    
    def get_all_crdt_states(self) -> Dict[str, Dict[str, Any]]:
        """Get all CRDT states for synchronization."""
        states = {}
        for name, crdt in self.crdts.items():
            states[name] = crdt.to_dict()
        return states
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """Get CRDT system health metrics."""
        return {
            "total_crdts": len(self.crdts),
            "node_id": self.node_id,
            "crdt_types": {name: crdt.__class__.__name__ for name, crdt in self.crdts.items()},
            "system_status": "operational"
        }