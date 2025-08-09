"""
Phase 7: Advanced Distributed Memory Architecture
=================================================

Enterprise-grade memory system using CRDT foundation and distributed agent coordination.
Implements persistent conversation memory with conflict-free distributed storage.

Priority: Technical architecture excellence and mathematical correctness.
"""

import json
import threading
import time
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict, field
from enum import Enum

from .crdt import ORSet, LWWRegister, GCounter, PNCounter
from .crdt_manager import get_crdt_manager
from .distributed_agent_coordinator import get_distributed_coordinator, DistributedTask, AgentCapabilities


class MemoryType(Enum):
    """Types of memory data for different processing requirements"""
    CONVERSATION = "conversation"
    USER_PROFILE = "user_profile"
    SYSTEM_STATE = "system_state"
    LEARNING_DATA = "learning_data"
    CONTEXT_GRAPH = "context_graph"


@dataclass
class MemoryEntry:
    """Individual memory entry with CRDT-compatible structure"""
    entry_id: str
    memory_type: MemoryType
    content: Dict[str, Any]
    timestamp: str
    source_node: str
    confidence_score: float = 1.0
    metadata: Dict[str, Any] = field(default_factory=dict)
    version: int = 1


@dataclass
class ConversationContext:
    """Conversation context with distributed state management"""
    session_id: str
    user_id: str
    conversation_history: List[MemoryEntry]
    context_embedding: Dict[str, float]
    preference_profile: Dict[str, Any]
    last_updated: str
    active_agents: Set[str] = field(default_factory=set)


class DistributedMemorySystem:
    """
    Enterprise-grade distributed memory system with agent coordination.
    Uses CRDT foundation for conflict-free distributed memory operations.
    """
    
    def __init__(self, node_id: str = "memory_node_0"):
        """Initialize distributed memory system"""
        self.node_id = node_id
        self.memory_lock = threading.Lock()
        
        # CRDT-based memory stores
        self.crdt_manager = get_crdt_manager(node_id)
        self.agent_coordinator = get_distributed_coordinator()
        
        # Memory stores using CRDT types
        self.conversation_entries = ORSet(node_id)  # Conversation history
        self.user_profiles = LWWRegister(node_id)   # Latest user preferences
        self.system_states = LWWRegister(node_id)   # System state tracking
        self.learning_data = ORSet(node_id)         # Distributed learning
        self.context_graphs = ORSet(node_id)        # Relationship mapping
        
        # Performance counters
        self.memory_operations = PNCounter(node_id)
        self.active_sessions = GCounter(node_id)
        
        # Memory management
        self.memory_cache: Dict[str, MemoryEntry] = {}
        self.active_contexts: Dict[str, ConversationContext] = {}
        
        # Initialize memory structures in CRDT manager
        self._initialize_memory_structures()
        
        print(f"[MEMORY] Distributed memory system initialized on node {node_id}")
    
    def _initialize_memory_structures(self):
        """Initialize memory structures in CRDT manager"""
        with self.memory_lock:
            # Register memory CRDT instances
            self.crdt_manager.crdts["memory_conversations"] = self.conversation_entries
            self.crdt_manager.crdts["memory_profiles"] = self.user_profiles
            self.crdt_manager.crdts["memory_states"] = self.system_states
            self.crdt_manager.crdts["memory_learning"] = self.learning_data
            self.crdt_manager.crdts["memory_contexts"] = self.context_graphs
            self.crdt_manager.crdts["memory_operations"] = self.memory_operations
            self.crdt_manager.crdts["memory_sessions"] = self.active_sessions
    
    def store_conversation_entry(self, session_id: str, user_input: str, 
                                ai_response: str, metadata: Dict[str, Any] = None) -> str:
        """
        Store conversation entry with distributed agent coordination.
        Returns entry ID for tracking.
        """
        if metadata is None:
            metadata = {}
            
        entry_id = f"conv_{session_id}_{int(time.time() * 1000)}"
        
        memory_entry = MemoryEntry(
            entry_id=entry_id,
            memory_type=MemoryType.CONVERSATION,
            content={
                "user_input": user_input,
                "ai_response": ai_response,
                "session_id": session_id
            },
            timestamp=datetime.now().isoformat(),
            source_node=self.node_id,
            metadata=metadata
        )
        
        # Store in CRDT conversation set
        with self.memory_lock:
            conversation_data = asdict(memory_entry)
            # Convert enum to string for JSON serialization
            conversation_data['memory_type'] = conversation_data['memory_type'].value
            tag = self.conversation_entries.add(json.dumps(conversation_data))
            self.memory_operations.increment(1)
            
            # Update local cache
            self.memory_cache[entry_id] = memory_entry
            
            # Update session context
            if session_id not in self.active_contexts:
                self.active_contexts[session_id] = ConversationContext(
                    session_id=session_id,
                    user_id=metadata.get("user_id", "unknown"),
                    conversation_history=[],
                    context_embedding={},
                    preference_profile={},
                    last_updated=datetime.now().isoformat()
                )
                self.active_sessions.increment(1)
            
            self.active_contexts[session_id].conversation_history.append(memory_entry)
            self.active_contexts[session_id].last_updated = datetime.now().isoformat()
        
        # Create distributed task for memory processing
        from .distributed_agent_coordinator import DistributedTask, TaskPriority
        
        memory_task = DistributedTask(
            task_id=f"memory_process_{entry_id}",
            name="Memory Processing",
            description="Process stored conversation entry",
            task_type="memory_processing",
            priority=TaskPriority.NORMAL,
            data={
                "entry_id": entry_id,
                "session_id": session_id,
                "action": "store_conversation"
            },
            requirements={"capabilities": ["memory_processing", "nlp"]},
            deadline=(datetime.now() + timedelta(seconds=30)).isoformat(),
            dependencies=[],
            assigned_agents=[],
            created_at=datetime.now().isoformat()
        )
        
        # Submit to agent coordinator for distributed processing
        try:
            self.agent_coordinator.submit_distributed_task(memory_task)
        except Exception as e:
            print(f"[MEMORY] Warning: Could not submit to agent coordinator: {e}")
        
        print(f"[MEMORY] Stored conversation entry: {entry_id}")
        return entry_id
    
    def update_user_profile(self, user_id: str, profile_data: Dict[str, Any]) -> bool:
        """Update user profile with latest-write-wins semantics"""
        try:
            with self.memory_lock:
                profile_entry = {
                    "user_id": user_id,
                    "profile_data": profile_data,
                    "timestamp": datetime.now().isoformat(),
                    "source_node": self.node_id
                }
                
                # Update using LWW-Register for conflict resolution
                self.user_profiles.write(json.dumps(profile_entry))
                self.memory_operations.increment(1)
                
                # Update active context if exists
                for context in self.active_contexts.values():
                    if context.user_id == user_id:
                        context.preference_profile.update(profile_data)
                        context.last_updated = datetime.now().isoformat()
            
            print(f"[MEMORY] Updated user profile: {user_id}")
            return True
            
        except Exception as e:
            print(f"[MEMORY] Error updating user profile: {e}")
            return False
    
    def get_conversation_history(self, session_id: str, limit: int = 50) -> List[MemoryEntry]:
        """Retrieve conversation history for a session"""
        if session_id in self.active_contexts:
            history = self.active_contexts[session_id].conversation_history
            return history[-limit:] if limit > 0 else history
        
        # Fallback: search CRDT store
        conversation_history = []
        for entry_json in self.conversation_entries.elements():
            try:
                entry_data = json.loads(entry_json)
                if entry_data.get("content", {}).get("session_id") == session_id:
                    entry = MemoryEntry(**entry_data)
                    conversation_history.append(entry)
            except (json.JSONDecodeError, TypeError):
                continue
        
        # Sort by timestamp and apply limit
        conversation_history.sort(key=lambda x: x.timestamp)
        return conversation_history[-limit:] if limit > 0 else conversation_history
    
    def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """Get latest user profile"""
        try:
            profile_json = self.user_profiles.read()
            if profile_json:
                profile_data = json.loads(profile_json)
                if profile_data.get("user_id") == user_id:
                    return profile_data.get("profile_data", {})
        except (json.JSONDecodeError, TypeError):
            pass
        return None
    
    def store_learning_data(self, learning_entry: Dict[str, Any]) -> str:
        """Store learning data for distributed agent improvement"""
        entry_id = f"learn_{int(time.time() * 1000)}"
        
        learning_data = {
            "entry_id": entry_id,
            "data": learning_entry,
            "timestamp": datetime.now().isoformat(),
            "source_node": self.node_id
        }
        
        with self.memory_lock:
            tag = self.learning_data.add(json.dumps(learning_data))
            self.memory_operations.increment(1)
        
        print(f"[MEMORY] Stored learning data: {entry_id}")
        return entry_id
    
    def get_memory_statistics(self) -> Dict[str, Any]:
        """Get comprehensive memory system statistics"""
        with self.memory_lock:
            return {
                "node_id": self.node_id,
                "total_conversations": len(self.conversation_entries.elements()),
                "active_sessions": len(self.active_contexts),
                "memory_operations": self.memory_operations.value(),
                "session_counter": self.active_sessions.value(),
                "learning_entries": len(self.learning_data.elements()),
                "cache_size": len(self.memory_cache),
                "crdt_instances": len([k for k in self.crdt_manager.crdts.keys() if k.startswith("memory_")]),
                "system_status": "operational",
                "last_updated": datetime.now().isoformat()
            }
    
    def sync_with_peers(self, peer_nodes: List[str]) -> Dict[str, Any]:
        """Synchronize memory data with peer nodes"""
        sync_results = {
            "synced_nodes": [],
            "failed_nodes": [],
            "operations_synced": 0,
            "conflicts_resolved": 0
        }
        
        for peer_node in peer_nodes:
            try:
                # Simulate distributed synchronization
                # In a real implementation, this would connect to peer nodes
                print(f"[MEMORY] Syncing with peer node: {peer_node}")
                sync_results["synced_nodes"].append(peer_node)
                sync_results["operations_synced"] += 1
                
            except Exception as e:
                print(f"[MEMORY] Failed to sync with {peer_node}: {e}")
                sync_results["failed_nodes"].append(peer_node)
        
        return sync_results
    
    def cleanup_current_sessions(self, max_age_hours: int = 24) -> int:
        """Clean up old inactive sessions"""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)
        cleaned_count = 0
        
        with self.memory_lock:
            sessions_to_remove = []
            for session_id, context in self.active_contexts.items():
                last_update = datetime.fromisoformat(context.last_updated)
                if last_update < cutoff_time:
                    sessions_to_remove.append(session_id)
            
            for session_id in sessions_to_remove:
                del self.active_contexts[session_id]
                cleaned_count += 1
        
        print(f"[MEMORY] Cleaned up {cleaned_count} old sessions")
        return cleaned_count


# Global memory system instance
_memory_system = None

def get_distributed_memory_system(node_id: str = "memory_node_0") -> DistributedMemorySystem:
    """Get the global distributed memory system instance"""
    global _memory_system
    if _memory_system is None:
        _memory_system = DistributedMemorySystem(node_id)
    return _memory_system


def store_conversation_memory(session_id: str, user_input: str, ai_response: str, 
                            metadata: Dict[str, Any] = None) -> str:
    """Convenience function to store conversation memory"""
    memory_system = get_distributed_memory_system()
    return memory_system.store_conversation_entry(session_id, user_input, ai_response, metadata)


def get_conversation_memory(session_id: str, limit: int = 50) -> List[Dict[str, Any]]:
    """Convenience function to get conversation memory"""
    memory_system = get_distributed_memory_system()
    entries = memory_system.get_conversation_history(session_id, limit)
    return [asdict(entry) for entry in entries]