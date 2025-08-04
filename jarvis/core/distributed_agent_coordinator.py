"""
Advanced Distributed Agent Coordination System for Jarvis-V0.19
Phase 6 Implementation: Multi-Node Agent Intelligence using CRDT Foundation
"""

import json
import time
import uuid
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple, Set
from dataclasses import dataclass, asdict
from enum import Enum
import concurrent.futures
from collections import defaultdict

from .crdt_manager import get_crdt_manager
from .crdt import ORSet, LWWRegister, PNCounter, GCounter
from .agent_workflow import get_workflow_manager, TestScenario
from .performance_monitor import get_performance_monitor

class TaskPriority(Enum):
    """Task priority levels for distributed coordination"""
    CRITICAL = 1
    HIGH = 2
    NORMAL = 3
    LOW = 4
    BACKGROUND = 5

class AgentStatus(Enum):
    """Agent status in distributed system"""
    AVAILABLE = "available"
    BUSY = "busy"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"
    COORDINATING = "coordinating"

@dataclass
class DistributedTask:
    """Task for distributed execution across agent network"""
    task_id: str
    name: str
    description: str
    task_type: str
    priority: TaskPriority
    data: Dict[str, Any]
    requirements: Dict[str, Any]
    deadline: Optional[str]
    dependencies: List[str]
    assigned_agents: List[str]
    created_at: str
    status: str = "pending"
    progress: float = 0.0
    results: Dict[str, Any] = None

@dataclass
class AgentCapabilities:
    """Agent capabilities for task assignment optimization"""
    agent_id: str
    node_id: str
    max_concurrent_tasks: int
    specialized_types: List[str]
    performance_rating: float
    resource_availability: Dict[str, float]
    last_health_check: str
    network_latency: float = 0.0

@dataclass
class CoordinationMetrics:
    """Metrics for distributed coordination performance"""
    total_tasks_coordinated: int
    successful_coordinations: int
    average_coordination_time: float
    network_efficiency: float
    load_balancing_score: float
    agent_utilization: Dict[str, float]
    consensus_time: float

class DistributedAgentCoordinator:
    """
    Advanced coordination system leveraging CRDT foundation for 
    conflict-free distributed agent intelligence
    """
    
    def __init__(self):
        self.coordinator_id = f"coordinator_{uuid.uuid4().hex[:8]}"
        self.crdt_manager = get_crdt_manager()
        self.workflow_manager = get_workflow_manager()
        self.performance_monitor = get_performance_monitor()
        
        # CRDT-based distributed state management
        self.agent_states = ORSet(node_id=self.coordinator_id)
        self.task_assignments = LWWRegister(node_id=self.coordinator_id)
        self.resource_pool = {}  # Use dict instead of PNCounter with multiple keys
        self.coordination_log = ORSet(node_id=self.coordinator_id)
        
        # Initialize resource pool as separate PNCounters
        for resource_type in ["cpu", "memory", "network", "storage"]:
            self.resource_pool[resource_type] = PNCounter(node_id=self.coordinator_id)
        
        # Local state management
        self.agents: Dict[str, AgentCapabilities] = {}
        self.pending_tasks: Dict[str, DistributedTask] = {}
        self.active_tasks: Dict[str, DistributedTask] = {}
        self.completed_tasks: Dict[str, DistributedTask] = {}
        
        # Coordination metrics
        self.metrics = CoordinationMetrics(
            total_tasks_coordinated=0,
            successful_coordinations=0,
            average_coordination_time=0.0,
            network_efficiency=0.0,
            load_balancing_score=0.0,
            agent_utilization={},
            consensus_time=0.0
        )
        
        # Threading for background operations
        self.coordination_thread = None
        self.running = False
        self.coordination_lock = threading.Lock()
        
        self._initialize_crdt_integration()
        
    def _initialize_crdt_integration(self):
        """Initialize CRDT integration for distributed coordination"""
        try:
            # Register coordination CRDTs with manager
            self.crdt_manager.register_crdt("agent_states", self.agent_states)
            self.crdt_manager.register_crdt("task_assignments", self.task_assignments)
            self.crdt_manager.register_crdt("coordination_log", self.coordination_log)
            
            # Register resource pool CRDTs
            for resource_type, counter in self.resource_pool.items():
                self.crdt_manager.register_crdt(f"resource_{resource_type}", counter)
                counter.increment(100)  # Base capacity
                
        except Exception as e:
            print(f"[ERROR] Failed to initialize CRDT integration: {e}")
    
    def start_coordination(self):
        """Start the distributed coordination system"""
        if self.running:
            return
            
        self.running = True
        self.coordination_thread = threading.Thread(target=self._coordination_loop, daemon=True)
        self.coordination_thread.start()
        
        # Log coordination start
        self._log_coordination_event("coordination_started", {
            "coordinator_id": self.coordinator_id,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"[COORDINATOR] Started distributed coordination: {self.coordinator_id}")
    
    def stop_coordination(self):
        """Stop the distributed coordination system"""
        self.running = False
        if self.coordination_thread:
            self.coordination_thread.join(timeout=5.0)
            
        self._log_coordination_event("coordination_stopped", {
            "coordinator_id": self.coordinator_id,
            "timestamp": datetime.now().isoformat()
        })
        
        print(f"[COORDINATOR] Stopped distributed coordination: {self.coordinator_id}")
    
    def register_agent(self, agent_capabilities: AgentCapabilities) -> bool:
        """Register an agent in the distributed system"""
        try:
            with self.coordination_lock:
                self.agents[agent_capabilities.agent_id] = agent_capabilities
                
                # Add agent to CRDT state
                agent_data = {
                    "agent_id": agent_capabilities.agent_id,
                    "node_id": agent_capabilities.node_id,
                    "status": AgentStatus.AVAILABLE.value,
                    "capabilities": asdict(agent_capabilities),
                    "registered_at": datetime.now().isoformat()
                }
                
                self.agent_states.add(json.dumps(agent_data))
                
                # Update resource pool
                for resource, capacity in agent_capabilities.resource_availability.items():
                    if resource in self.resource_pool:
                        self.resource_pool[resource].increment(int(capacity))
                
                self._log_coordination_event("agent_registered", agent_data)
                
                print(f"[COORDINATOR] Registered agent: {agent_capabilities.agent_id}")
                return True
                
        except Exception as e:
            print(f"[ERROR] Failed to register agent: {e}")
            return False
    
    def submit_distributed_task(self, task: DistributedTask) -> bool:
        """Submit a task for distributed execution"""
        try:
            with self.coordination_lock:
                self.pending_tasks[task.task_id] = task
                
                # Update task assignment CRDT
                task_data = {
                    "task_id": task.task_id,
                    "status": "pending",
                    "submitted_at": datetime.now().isoformat(),
                    "coordinator": self.coordinator_id
                }
                
                self.task_assignments.write(json.dumps(task_data))
                
                self._log_coordination_event("task_submitted", {
                    "task_id": task.task_id,
                    "task_type": task.task_type,
                    "priority": task.priority.value
                })
                
                print(f"[COORDINATOR] Submitted task: {task.task_id}")
                return True
                
        except Exception as e:
            print(f"[ERROR] Failed to submit task: {e}")
            return False
    
    def coordinate_agents(self, task_list: List[DistributedTask]) -> Dict[str, Any]:
        """
        Coordinate agents for distributed task execution
        Main coordination algorithm using CRDT-based conflict resolution
        """
        coordination_start = time.time()
        results = {
            "coordinated_tasks": 0,
            "successful_assignments": 0,
            "failed_assignments": 0,
            "coordination_time": 0.0,
            "load_balance_efficiency": 0.0
        }
        
        try:
            # Submit all tasks
            for task in task_list:
                if self.submit_distributed_task(task):
                    results["coordinated_tasks"] += 1
            
            # Perform intelligent task assignment
            assignment_results = self._perform_intelligent_assignment()
            results.update(assignment_results)
            
            # Calculate coordination metrics
            coordination_time = time.time() - coordination_start
            results["coordination_time"] = coordination_time
            results["load_balance_efficiency"] = self._calculate_load_balance_efficiency()
            
            # Update overall metrics
            self.metrics.total_tasks_coordinated += results["coordinated_tasks"]
            self.metrics.successful_coordinations += results["successful_assignments"]
            self.metrics.average_coordination_time = (
                (self.metrics.average_coordination_time * (self.metrics.total_tasks_coordinated - results["coordinated_tasks"]) + 
                 coordination_time) / self.metrics.total_tasks_coordinated
            )
            
            self._log_coordination_event("coordination_completed", results)
            
            return results
            
        except Exception as e:
            print(f"[ERROR] Coordination failed: {e}")
            results["error"] = str(e)
            return results
    
    def _coordination_loop(self):
        """Background coordination loop for continuous optimization"""
        while self.running:
            try:
                # Perform periodic coordination tasks
                self._optimize_task_assignments()
                self._update_agent_health()
                self._balance_resource_allocation()
                self._sync_distributed_state()
                
                # Sleep for coordination interval
                time.sleep(2.0)
                
            except Exception as e:
                print(f"[ERROR] Coordination loop error: {e}")
                time.sleep(5.0)
    
    def _perform_intelligent_assignment(self) -> Dict[str, Any]:
        """Perform intelligent task assignment using agent capabilities"""
        assignment_results = {
            "successful_assignments": 0,
            "failed_assignments": 0,
            "assignment_details": []
        }
        
        try:
            available_agents = [
                agent for agent in self.agents.values()
                if self._get_agent_status(agent.agent_id) == AgentStatus.AVAILABLE
            ]
            
            # Sort pending tasks by priority
            sorted_tasks = sorted(
                self.pending_tasks.values(),
                key=lambda t: (t.priority.value, t.created_at)
            )
            
            for task in sorted_tasks:
                # Find best agent for task
                best_agent = self._find_optimal_agent(task, available_agents)
                
                if best_agent:
                    # Assign task to agent
                    if self._assign_task_to_agent(task, best_agent):
                        assignment_results["successful_assignments"] += 1
                        assignment_results["assignment_details"].append({
                            "task_id": task.task_id,
                            "agent_id": best_agent.agent_id,
                            "assignment_score": self._calculate_assignment_score(task, best_agent)
                        })
                    else:
                        assignment_results["failed_assignments"] += 1
                else:
                    assignment_results["failed_assignments"] += 1
                    
        except Exception as e:
            print(f"[ERROR] Assignment failed: {e}")
            assignment_results["error"] = str(e)
        
        return assignment_results
    
    def _find_optimal_agent(self, task: DistributedTask, available_agents: List[AgentCapabilities]) -> Optional[AgentCapabilities]:
        """Find the optimal agent for a given task"""
        if not available_agents:
            return None
        
        best_agent = None
        best_score = -1.0
        
        for agent in available_agents:
            score = self._calculate_assignment_score(task, agent)
            if score > best_score:
                best_score = score
                best_agent = agent
        
        return best_agent if best_score > 0.5 else None
    
    def _calculate_assignment_score(self, task: DistributedTask, agent: AgentCapabilities) -> float:
        """Calculate assignment score for task-agent pairing"""
        score = 0.0
        
        # Performance rating factor (0-1)
        performance_factor = min(1.0, agent.performance_rating / 10.0)
        score += performance_factor * 0.3
        
        # Specialization factor (0-1)
        specialization_factor = 1.0 if task.task_type in agent.specialized_types else 0.5
        score += specialization_factor * 0.3
        
        # Resource availability factor (0-1)
        resource_factor = min(1.0, sum(agent.resource_availability.values()) / len(agent.resource_availability))
        score += resource_factor * 0.2
        
        # Network latency factor (0-1)
        latency_factor = max(0.0, 1.0 - (agent.network_latency / 1000.0))  # Normalize to seconds
        score += latency_factor * 0.2
        
        return score
    
    def _assign_task_to_agent(self, task: DistributedTask, agent: AgentCapabilities) -> bool:
        """Assign a specific task to a specific agent"""
        try:
            # Move task from pending to active
            if task.task_id in self.pending_tasks:
                del self.pending_tasks[task.task_id]
                
            task.status = "assigned"
            task.assigned_agents = [agent.agent_id]
            self.active_tasks[task.task_id] = task
            
            # Update CRDT task assignment
            assignment_data = {
                "task_id": task.task_id,
                "agent_id": agent.agent_id,
                "status": "assigned",
                "assigned_at": datetime.now().isoformat()
            }
            
            self.task_assignments.write(json.dumps(assignment_data))
            
            # Update resource allocation
            for resource, usage in task.requirements.get("resources", {}).items():
                if resource in self.resource_pool:
                    self.resource_pool[resource].decrement(int(usage))
            
            self._log_coordination_event("task_assigned", assignment_data)
            
            return True
            
        except Exception as e:
            print(f"[ERROR] Task assignment failed: {e}")
            return False
    
    def _get_agent_status(self, agent_id: str) -> AgentStatus:
        """Get current status of an agent"""
        # In real implementation, this would check actual agent status
        # For now, return available for registered agents
        return AgentStatus.AVAILABLE if agent_id in self.agents else AgentStatus.OFFLINE
    
    def _optimize_task_assignments(self):
        """Optimize current task assignments for better performance"""
        try:
            # Check for task reassignment opportunities
            for task_id, task in list(self.active_tasks.items()):
                if task.status == "assigned" and task.progress == 0.0:
                    # Task hasn't started yet, check for better agent
                    current_agent_id = task.assigned_agents[0] if task.assigned_agents else None
                    if current_agent_id and current_agent_id in self.agents:
                        current_agent = self.agents[current_agent_id]
                        
                        # Find potentially better agent
                        available_agents = [
                            agent for agent in self.agents.values()
                            if (self._get_agent_status(agent.agent_id) == AgentStatus.AVAILABLE and
                                agent.agent_id != current_agent_id)
                        ]
                        
                        better_agent = self._find_optimal_agent(task, available_agents)
                        if better_agent:
                            current_score = self._calculate_assignment_score(task, current_agent)
                            better_score = self._calculate_assignment_score(task, better_agent)
                            
                            # Reassign if significantly better (10% improvement)
                            if better_score > current_score * 1.1:
                                self._reassign_task(task, better_agent)
                                
        except Exception as e:
            print(f"[ERROR] Task optimization failed: {e}")
    
    def _reassign_task(self, task: DistributedTask, new_agent: AgentCapabilities):
        """Reassign a task to a different agent"""
        try:
            old_agent_id = task.assigned_agents[0] if task.assigned_agents else None
            
            # Update task assignment
            task.assigned_agents = [new_agent.agent_id]
            
            # Update CRDT
            reassignment_data = {
                "task_id": task.task_id,
                "new_agent_id": new_agent.agent_id,
                "old_agent_id": old_agent_id,
                "reassigned_at": datetime.now().isoformat(),
                "reason": "optimization"
            }
            
            self.task_assignments.write(json.dumps(reassignment_data))
            
            self._log_coordination_event("task_reassigned", reassignment_data)
            
            print(f"[COORDINATOR] Reassigned task {task.task_id} from {old_agent_id} to {new_agent.agent_id}")
            
        except Exception as e:
            print(f"[ERROR] Task reassignment failed: {e}")
    
    def _update_agent_health(self):
        """Update health status of all registered agents"""
        try:
            current_time = datetime.now()
            
            for agent_id, agent in self.agents.items():
                # Simulate health check (in real implementation, this would ping the agent)
                health_check_data = {
                    "agent_id": agent_id,
                    "health_status": "healthy",
                    "last_check": current_time.isoformat(),
                    "response_time": 0.05  # Simulated response time
                }
                
                # Update agent capabilities
                agent.last_health_check = current_time.isoformat()
                agent.network_latency = health_check_data["response_time"] * 1000  # Convert to ms
                
                self._log_coordination_event("health_check", health_check_data)
                
        except Exception as e:
            print(f"[ERROR] Health update failed: {e}")
    
    def _balance_resource_allocation(self):
        """Balance resource allocation across the distributed system"""
        try:
            # Calculate current resource usage
            total_resources = {}
            used_resources = {}
            
            for resource in ["cpu", "memory", "network", "storage"]:
                total_resources[resource] = self.resource_pool[resource].value()
                used_resources[resource] = sum(
                    task.requirements.get("resources", {}).get(resource, 0)
                    for task in self.active_tasks.values()
                )
            
            # Calculate load balancing score
            utilization_scores = []
            for resource, total in total_resources.items():
                if total > 0:
                    utilization = used_resources[resource] / total
                    utilization_scores.append(utilization)
            
            if utilization_scores:
                self.metrics.load_balancing_score = 1.0 - (max(utilization_scores) - min(utilization_scores))
            
        except Exception as e:
            print(f"[ERROR] Resource balancing failed: {e}")
    
    def _sync_distributed_state(self):
        """Synchronize distributed state across CRDT network"""
        try:
            # Trigger CRDT synchronization
            if hasattr(self.crdt_manager, 'sync_all'):
                self.crdt_manager.sync_all()
            
            # Update consensus metrics
            consensus_start = time.time()
            # Simulate consensus calculation
            consensus_time = time.time() - consensus_start
            self.metrics.consensus_time = consensus_time
            
        except Exception as e:
            print(f"[ERROR] State synchronization failed: {e}")
    
    def _calculate_load_balance_efficiency(self) -> float:
        """Calculate the load balancing efficiency of current assignments"""
        if not self.agents:
            return 0.0
        
        # Calculate task distribution across agents
        agent_task_counts = defaultdict(int)
        for task in self.active_tasks.values():
            for agent_id in task.assigned_agents:
                agent_task_counts[agent_id] += 1
        
        # Calculate distribution variance
        task_counts = list(agent_task_counts.values())
        if not task_counts:
            return 1.0
        
        mean_tasks = sum(task_counts) / len(task_counts)
        variance = sum((count - mean_tasks) ** 2 for count in task_counts) / len(task_counts)
        
        # Convert variance to efficiency score (lower variance = higher efficiency)
        efficiency = max(0.0, 1.0 - (variance / (mean_tasks + 1)))
        return efficiency
    
    def _log_coordination_event(self, event_type: str, event_data: Dict[str, Any]):
        """Log coordination events to CRDT log"""
        try:
            log_entry = {
                "event_type": event_type,
                "timestamp": datetime.now().isoformat(),
                "coordinator_id": self.coordinator_id,
                "data": event_data
            }
            
            self.coordination_log.add(json.dumps(log_entry))
            
        except Exception as e:
            print(f"[ERROR] Failed to log coordination event: {e}")
    
    def get_coordination_status(self) -> Dict[str, Any]:
        """Get comprehensive coordination system status"""
        return {
            "coordinator_id": self.coordinator_id,
            "running": self.running,
            "registered_agents": len(self.agents),
            "pending_tasks": len(self.pending_tasks),
            "active_tasks": len(self.active_tasks),
            "completed_tasks": len(self.completed_tasks),
            "metrics": asdict(self.metrics),
            "resource_pool": {
                resource: self.resource_pool[resource].value()
                for resource in ["cpu", "memory", "network", "storage"]
            },
            "agents": {
                agent_id: {
                    "status": self._get_agent_status(agent_id).value,
                    "capabilities": asdict(agent)
                }
                for agent_id, agent in self.agents.items()
            }
        }
    
    def get_health_metrics(self) -> Dict[str, Any]:
        """Get health metrics for monitoring"""
        coordination_efficiency = 0.0
        if self.metrics.total_tasks_coordinated > 0:
            coordination_efficiency = self.metrics.successful_coordinations / self.metrics.total_tasks_coordinated
        
        return {
            "coordination_efficiency": coordination_efficiency,
            "average_coordination_time": self.metrics.average_coordination_time,
            "load_balancing_score": self.metrics.load_balancing_score,
            "network_efficiency": self.metrics.network_efficiency,
            "agent_count": len(self.agents),
            "active_tasks": len(self.active_tasks),
            "system_status": "operational" if self.running else "stopped"
        }

# Global coordinator instance
_distributed_coordinator = None

def get_distributed_coordinator() -> DistributedAgentCoordinator:
    """Get the global distributed agent coordinator instance"""
    global _distributed_coordinator
    if _distributed_coordinator is None:
        _distributed_coordinator = DistributedAgentCoordinator()
    return _distributed_coordinator