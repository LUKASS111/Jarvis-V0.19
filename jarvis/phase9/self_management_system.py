#!/usr/bin/env python3
"""
Self-Management System
======================

Advanced self-managing capabilities for autonomous system maintenance,
optimization, and adaptation without human intervention.
"""

import time
import json
import threading
from typing import Dict, List, Any, Optional, Set
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid
from collections import defaultdict

logger = logging.getLogger(__name__)


class ManagementAction(Enum):
    """Types of self-management actions"""
    OPTIMIZATION = "optimization"
    MAINTENANCE = "maintenance"
    SCALING = "scaling"
    HEALING = "healing"
    CONFIGURATION = "configuration"
    MONITORING = "monitoring"


class SystemComponent(Enum):
    """System components that can be managed"""
    DATABASE = "database"
    MEMORY = "memory"
    NETWORK = "network"
    STORAGE = "storage"
    COMPUTE = "compute"
    SECURITY = "security"


@dataclass
class ManagementTask:
    """Self-management task"""
    task_id: str
    action_type: ManagementAction
    component: SystemComponent
    description: str
    priority: int  # 1-10, 10 being highest
    parameters: Dict[str, Any] = field(default_factory=dict)
    scheduled_time: Optional[datetime] = None
    execution_time: Optional[datetime] = None
    status: str = "pending"
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None


@dataclass
class SystemMetric:
    """System performance metric"""
    metric_name: str
    current_value: float
    threshold_warning: float
    threshold_critical: float
    trend: str = "stable"  # increasing, decreasing, stable
    last_updated: datetime = field(default_factory=datetime.now)


class SelfManagementSystem:
    """
    Advanced self-management system for autonomous operation
    """
    
    def __init__(self, node_id: str = "self_manager"):
        self.node_id = node_id
        self.is_active = False
        
        # Management state
        self.management_tasks: List[ManagementTask] = []
        self.completed_tasks: List[ManagementTask] = []
        self.system_metrics: Dict[str, SystemMetric] = {}
        self.management_rules: Dict[str, Any] = {}
        
        # System state
        self.system_health: Dict[str, float] = {}
        self.resource_usage: Dict[str, float] = {}
        self.performance_baselines: Dict[str, float] = {}
        self.optimization_history: List[Dict[str, Any]] = []
        
        # Configuration
        self.config = {
            "auto_optimization": True,
            "auto_healing": True,
            "auto_scaling": False,
            "maintenance_window": "02:00-04:00",
            "monitoring_interval": 30,
            "optimization_threshold": 80.0,
            "healing_threshold": 70.0
        }
        
        # Metrics
        self.metrics = {
            "tasks_executed": 0,
            "optimizations_performed": 0,
            "issues_resolved": 0,
            "uptime_improvement": 0.0,
            "performance_improvement": 0.0,
            "self_management_score": 0.0
        }
        
        # Threading
        self.management_thread: Optional[threading.Thread] = None
        self.monitoring_thread: Optional[threading.Thread] = None
        self.healing_thread: Optional[threading.Thread] = None
        
        logger.info(f"[SELF_MGMT] Self-management system initialized for {node_id}")
    
    def start(self) -> bool:
        """Start self-management system"""
        try:
            if self.is_active:
                return True
            
            self.is_active = True
            
            # Initialize system baselines
            self._initialize_baselines()
            
            # Initialize management rules
            self._initialize_management_rules()
            
            # Start management threads
            self.management_thread = threading.Thread(target=self._management_loop, daemon=True)
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.healing_thread = threading.Thread(target=self._healing_loop, daemon=True)
            
            self.management_thread.start()
            self.monitoring_thread.start()
            self.healing_thread.start()
            
            logger.info("[SELF_MGMT] Self-management system started")
            return True
            
        except Exception as e:
            logger.error(f"[SELF_MGMT] Failed to start: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop self-management system"""
        try:
            self.is_active = False
            
            # Wait for threads
            if self.management_thread:
                self.management_thread.join(timeout=5)
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5)
            if self.healing_thread:
                self.healing_thread.join(timeout=5)
            
            logger.info("[SELF_MGMT] Self-management system stopped")
            return True
            
        except Exception as e:
            logger.error(f"[SELF_MGMT] Error stopping: {e}")
            return False
    
    def add_management_task(self, task: ManagementTask) -> bool:
        """Add self-management task"""
        try:
            # Validate task
            if not task.task_id or not task.description:
                return False
            
            # Check for duplicates
            if any(t.task_id == task.task_id for t in self.management_tasks):
                return False
            
            # Add to queue (sorted by priority)
            self.management_tasks.append(task)
            self.management_tasks.sort(key=lambda t: t.priority, reverse=True)
            
            logger.info(f"[SELF_MGMT] Task added: {task.task_id} ({task.action_type.value})")
            return True
            
        except Exception as e:
            logger.error(f"[SELF_MGMT] Failed to add task: {e}")
            return False
    
    def update_system_metric(self, metric_name: str, value: float, 
                           warning_threshold: float = None, 
                           critical_threshold: float = None) -> bool:
        """Update system metric for monitoring"""
        try:
            if metric_name in self.system_metrics:
                metric = self.system_metrics[metric_name]
                
                # Determine trend
                if value > metric.current_value * 1.05:
                    trend = "increasing"
                elif value < metric.current_value * 0.95:
                    trend = "decreasing"
                else:
                    trend = "stable"
                
                metric.current_value = value
                metric.trend = trend
                metric.last_updated = datetime.now()
            else:
                # Create new metric
                self.system_metrics[metric_name] = SystemMetric(
                    metric_name=metric_name,
                    current_value=value,
                    threshold_warning=warning_threshold or value * 1.2,
                    threshold_critical=critical_threshold or value * 1.5
                )
            
            # Check if action is needed
            self._check_metric_thresholds(metric_name)
            
            return True
            
        except Exception as e:
            logger.error(f"[SELF_MGMT] Failed to update metric: {e}")
            return False
    
    def trigger_optimization(self, component: SystemComponent, 
                           parameters: Dict[str, Any] = None) -> str:
        """Trigger optimization for specific component"""
        try:
            task = ManagementTask(
                task_id=f"opt_{uuid.uuid4().hex[:8]}",
                action_type=ManagementAction.OPTIMIZATION,
                component=component,
                description=f"Optimize {component.value} performance",
                priority=8,
                parameters=parameters or {}
            )
            
            success = self.add_management_task(task)
            return task.task_id if success else ""
            
        except Exception as e:
            logger.error(f"[SELF_MGMT] Failed to trigger optimization: {e}")
            return ""
    
    def trigger_healing(self, component: SystemComponent, 
                       issue_description: str = "") -> str:
        """Trigger self-healing for specific component"""
        try:
            task = ManagementTask(
                task_id=f"heal_{uuid.uuid4().hex[:8]}",
                action_type=ManagementAction.HEALING,
                component=component,
                description=f"Heal {component.value}: {issue_description}",
                priority=9,
                parameters={"issue": issue_description}
            )
            
            success = self.add_management_task(task)
            return task.task_id if success else ""
            
        except Exception as e:
            logger.error(f"[SELF_MGMT] Failed to trigger healing: {e}")
            return ""
    
    def get_management_status(self) -> Dict[str, Any]:
        """Get comprehensive self-management status"""
        return {
            "node_id": self.node_id,
            "is_active": self.is_active,
            "pending_tasks": len(self.management_tasks),
            "completed_tasks": len(self.completed_tasks),
            "system_health": self._calculate_system_health(),
            "metrics": self.metrics.copy(),
            "configuration": self.config.copy(),
            "system_metrics": {
                name: {
                    "value": metric.current_value,
                    "trend": metric.trend,
                    "status": self._get_metric_status(metric)
                }
                for name, metric in self.system_metrics.items()
            },
            "recent_tasks": [
                {
                    "task_id": task.task_id,
                    "action": task.action_type.value,
                    "component": task.component.value,
                    "status": task.status,
                    "execution_time": task.execution_time.isoformat() if task.execution_time else None
                }
                for task in self.completed_tasks[-5:]
            ],
            "optimization_opportunities": self._identify_optimization_opportunities(),
            "management_score": self._calculate_management_score()
        }
    
    def _management_loop(self):
        """Main self-management loop"""
        while self.is_active:
            try:
                # Execute pending tasks
                self._execute_management_tasks()
                
                # Check for automatic optimizations
                if self.config["auto_optimization"]:
                    self._check_optimization_opportunities()
                
                # Perform scheduled maintenance
                self._check_maintenance_schedule()
                
                time.sleep(30)  # Management loop interval
                
            except Exception as e:
                logger.error(f"[SELF_MGMT] Error in management loop: {e}")
                time.sleep(60)
    
    def _monitoring_loop(self):
        """System monitoring loop"""
        while self.is_active:
            try:
                # Update system health metrics
                self._update_system_health()
                
                # Update resource usage
                self._update_resource_usage()
                
                # Check performance against baselines
                self._check_performance_baselines()
                
                time.sleep(self.config["monitoring_interval"])
                
            except Exception as e:
                logger.error(f"[SELF_MGMT] Error in monitoring loop: {e}")
                time.sleep(60)
    
    def _healing_loop(self):
        """Self-healing loop"""
        while self.is_active:
            try:
                # Check for issues requiring healing
                if self.config["auto_healing"]:
                    self._check_healing_opportunities()
                
                # Validate previous healing actions
                self._validate_healing_results()
                
                time.sleep(60)  # Healing check interval
                
            except Exception as e:
                logger.error(f"[SELF_MGMT] Error in healing loop: {e}")
                time.sleep(120)
    
    def _execute_management_tasks(self):
        """Execute pending management tasks"""
        try:
            # Execute top priority tasks
            for task in self.management_tasks[:3]:  # Execute up to 3 tasks
                if task.status == "pending":
                    self._execute_task(task)
            
        except Exception as e:
            logger.error(f"[SELF_MGMT] Error executing tasks: {e}")
    
    def _execute_task(self, task: ManagementTask) -> bool:
        """Execute specific management task"""
        try:
            task.status = "executing"
            task.execution_time = datetime.now()
            
            # Execute based on action type
            result = None
            if task.action_type == ManagementAction.OPTIMIZATION:
                result = self._perform_optimization(task)
            elif task.action_type == ManagementAction.MAINTENANCE:
                result = self._perform_maintenance(task)
            elif task.action_type == ManagementAction.HEALING:
                result = self._perform_healing(task)
            elif task.action_type == ManagementAction.SCALING:
                result = self._perform_scaling(task)
            elif task.action_type == ManagementAction.CONFIGURATION:
                result = self._perform_configuration(task)
            elif task.action_type == ManagementAction.MONITORING:
                result = self._perform_monitoring(task)
            
            # Update task status
            if result and result.get("success"):
                task.status = "completed"
                task.result = result
                self.metrics["tasks_executed"] += 1
            else:
                task.status = "failed"
                task.error = result.get("error", "Unknown error") if result else "No result"
            
            # Move to completed tasks
            self.completed_tasks.append(task)
            self.management_tasks.remove(task)
            
            logger.info(f"[SELF_MGMT] Task executed: {task.task_id} ({task.status})")
            return task.status == "completed"
            
        except Exception as e:
            task.status = "failed"
            task.error = str(e)
            logger.error(f"[SELF_MGMT] Task execution failed: {task.task_id} - {e}")
            return False
    
    def _perform_optimization(self, task: ManagementTask) -> Dict[str, Any]:
        """Perform optimization task"""
        try:
            component = task.component
            
            # Simulate optimization based on component
            improvements = {
                SystemComponent.DATABASE: {"query_performance": 15.0, "index_optimization": True},
                SystemComponent.MEMORY: {"cache_hit_rate": 12.0, "memory_efficiency": 8.0},
                SystemComponent.NETWORK: {"latency_reduction": 20.0, "bandwidth_optimization": True},
                SystemComponent.STORAGE: {"io_performance": 18.0, "compression_enabled": True},
                SystemComponent.COMPUTE: {"cpu_efficiency": 10.0, "load_balancing": True},
                SystemComponent.SECURITY: {"scan_optimization": 25.0, "policy_update": True}
            }
            
            improvement = improvements.get(component, {"performance": 5.0})
            
            # Record optimization
            self.optimization_history.append({
                "component": component.value,
                "improvements": improvement,
                "timestamp": datetime.now().isoformat()
            })
            
            self.metrics["optimizations_performed"] += 1
            
            # Simulate execution time
            time.sleep(0.1)
            
            return {
                "success": True,
                "component": component.value,
                "improvements": improvement,
                "performance_gain": sum(v for v in improvement.values() if isinstance(v, (int, float)))
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _perform_maintenance(self, task: ManagementTask) -> Dict[str, Any]:
        """Perform maintenance task"""
        try:
            component = task.component
            
            # Simulate maintenance actions
            maintenance_actions = {
                SystemComponent.DATABASE: ["index_rebuild", "statistics_update", "log_cleanup"],
                SystemComponent.MEMORY: ["cache_cleanup", "memory_defragmentation"],
                SystemComponent.NETWORK: ["connection_cleanup", "routing_optimization"],
                SystemComponent.STORAGE: ["disk_cleanup", "defragmentation"],
                SystemComponent.COMPUTE: ["process_optimization", "resource_cleanup"],
                SystemComponent.SECURITY: ["log_rotation", "certificate_check"]
            }
            
            actions = maintenance_actions.get(component, ["general_cleanup"])
            
            # Simulate execution
            time.sleep(0.2)
            
            return {
                "success": True,
                "component": component.value,
                "actions_performed": actions,
                "maintenance_score": 95.0
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _perform_healing(self, task: ManagementTask) -> Dict[str, Any]:
        """Perform self-healing task"""
        try:
            component = task.component
            issue = task.parameters.get("issue", "")
            
            # Simulate healing actions
            healing_actions = {
                SystemComponent.DATABASE: ["connection_pool_reset", "query_cache_clear"],
                SystemComponent.MEMORY: ["memory_leak_fix", "garbage_collection"],
                SystemComponent.NETWORK: ["connection_reset", "dns_flush"],
                SystemComponent.STORAGE: ["disk_error_recovery", "file_system_check"],
                SystemComponent.COMPUTE: ["process_restart", "resource_reallocation"],
                SystemComponent.SECURITY: ["threat_mitigation", "access_control_reset"]
            }
            
            actions = healing_actions.get(component, ["system_restart"])
            
            self.metrics["issues_resolved"] += 1
            
            # Simulate execution
            time.sleep(0.15)
            
            return {
                "success": True,
                "component": component.value,
                "issue": issue,
                "healing_actions": actions,
                "recovery_status": "successful"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _perform_scaling(self, task: ManagementTask) -> Dict[str, Any]:
        """Perform scaling task"""
        return {"success": True, "action": "scaling_simulated"}
    
    def _perform_configuration(self, task: ManagementTask) -> Dict[str, Any]:
        """Perform configuration task"""
        return {"success": True, "action": "configuration_updated"}
    
    def _perform_monitoring(self, task: ManagementTask) -> Dict[str, Any]:
        """Perform monitoring task"""
        return {"success": True, "action": "monitoring_enhanced"}
    
    def _initialize_baselines(self):
        """Initialize performance baselines"""
        self.performance_baselines = {
            "cpu_usage": 45.0,
            "memory_usage": 60.0,
            "response_time": 150.0,
            "throughput": 1000.0,
            "error_rate": 0.1
        }
        
        # Initialize system metrics
        for metric_name, baseline in self.performance_baselines.items():
            self.update_system_metric(metric_name, baseline)
        
        logger.info("[SELF_MGMT] Performance baselines initialized")
    
    def _initialize_management_rules(self):
        """Initialize self-management rules"""
        self.management_rules = {
            "optimization_triggers": {
                "cpu_usage_high": {"threshold": 80.0, "action": "optimize_compute"},
                "memory_usage_high": {"threshold": 85.0, "action": "optimize_memory"},
                "response_time_slow": {"threshold": 500.0, "action": "optimize_database"}
            },
            "healing_triggers": {
                "error_rate_high": {"threshold": 1.0, "action": "heal_system"},
                "connection_failures": {"threshold": 5, "action": "heal_network"}
            },
            "maintenance_schedule": {
                "daily": ["log_cleanup", "cache_optimization"],
                "weekly": ["database_maintenance", "performance_analysis"],
                "monthly": ["full_system_review", "security_audit"]
            }
        }
        
        logger.info("[SELF_MGMT] Management rules initialized")
    
    def _check_metric_thresholds(self, metric_name: str):
        """Check if metric exceeds thresholds and trigger actions"""
        try:
            metric = self.system_metrics.get(metric_name)
            if not metric:
                return
            
            # Check critical threshold
            if metric.current_value >= metric.threshold_critical:
                logger.warning(f"[SELF_MGMT] Critical threshold exceeded: {metric_name} = {metric.current_value}")
                self._trigger_emergency_action(metric_name, metric)
            
            # Check warning threshold
            elif metric.current_value >= metric.threshold_warning:
                logger.info(f"[SELF_MGMT] Warning threshold exceeded: {metric_name} = {metric.current_value}")
                self._trigger_optimization_action(metric_name, metric)
            
        except Exception as e:
            logger.error(f"[SELF_MGMT] Error checking thresholds: {e}")
    
    def _trigger_emergency_action(self, metric_name: str, metric: SystemMetric):
        """Trigger emergency action for critical metrics"""
        # Determine appropriate component
        component_map = {
            "cpu_usage": SystemComponent.COMPUTE,
            "memory_usage": SystemComponent.MEMORY,
            "response_time": SystemComponent.DATABASE,
            "error_rate": SystemComponent.SECURITY
        }
        
        component = component_map.get(metric_name, SystemComponent.COMPUTE)
        self.trigger_healing(component, f"Critical {metric_name}: {metric.current_value}")
    
    def _trigger_optimization_action(self, metric_name: str, metric: SystemMetric):
        """Trigger optimization action for warning metrics"""
        component_map = {
            "cpu_usage": SystemComponent.COMPUTE,
            "memory_usage": SystemComponent.MEMORY,
            "response_time": SystemComponent.DATABASE,
            "throughput": SystemComponent.NETWORK
        }
        
        component = component_map.get(metric_name, SystemComponent.COMPUTE)
        self.trigger_optimization(component, {"metric": metric_name, "value": metric.current_value})
    
    def _update_system_health(self):
        """Update overall system health metrics"""
        try:
            # Calculate health based on metrics
            health_scores = {}
            
            for name, metric in self.system_metrics.items():
                # Calculate health score (0-100)
                if metric.current_value <= metric.threshold_warning:
                    health_scores[name] = 100.0
                elif metric.current_value <= metric.threshold_critical:
                    # Linear degradation between warning and critical
                    range_size = metric.threshold_critical - metric.threshold_warning
                    excess = metric.current_value - metric.threshold_warning
                    health_scores[name] = 100.0 - (excess / range_size) * 50.0
                else:
                    # Critical threshold exceeded
                    health_scores[name] = 50.0
            
            self.system_health = health_scores
            
        except Exception as e:
            logger.error(f"[SELF_MGMT] Error updating system health: {e}")
    
    def _update_resource_usage(self):
        """Update resource usage metrics"""
        try:
            # Simulate resource usage updates
            import random
            
            self.resource_usage = {
                "cpu_percentage": random.uniform(30, 70),
                "memory_percentage": random.uniform(40, 80),
                "disk_usage": random.uniform(20, 60),
                "network_utilization": random.uniform(10, 40)
            }
            
            # Update system metrics
            for resource, value in self.resource_usage.items():
                self.update_system_metric(resource, value)
            
        except Exception as e:
            logger.error(f"[SELF_MGMT] Error updating resource usage: {e}")
    
    def _check_performance_baselines(self):
        """Check performance against established baselines"""
        try:
            for metric_name, baseline in self.performance_baselines.items():
                if metric_name in self.system_metrics:
                    current = self.system_metrics[metric_name].current_value
                    deviation = abs(current - baseline) / baseline
                    
                    if deviation > 0.3:  # 30% deviation
                        logger.info(f"[SELF_MGMT] Performance deviation detected: {metric_name} = {current} (baseline: {baseline})")
            
        except Exception as e:
            logger.error(f"[SELF_MGMT] Error checking baselines: {e}")
    
    def _check_optimization_opportunities(self):
        """Check for optimization opportunities"""
        try:
            # Check if system health is below optimization threshold
            avg_health = self._calculate_system_health()
            
            if avg_health < self.config["optimization_threshold"]:
                # Find worst performing component
                worst_metric = min(self.system_health.items(), key=lambda x: x[1], default=(None, 100))
                
                if worst_metric[0]:
                    component_map = {
                        "cpu_percentage": SystemComponent.COMPUTE,
                        "memory_percentage": SystemComponent.MEMORY,
                        "response_time": SystemComponent.DATABASE
                    }
                    
                    component = component_map.get(worst_metric[0], SystemComponent.COMPUTE)
                    self.trigger_optimization(component, {"health_score": worst_metric[1]})
            
        except Exception as e:
            logger.error(f"[SELF_MGMT] Error checking optimization opportunities: {e}")
    
    def _check_healing_opportunities(self):
        """Check for self-healing opportunities"""
        try:
            # Check if system health is below healing threshold
            avg_health = self._calculate_system_health()
            
            if avg_health < self.config["healing_threshold"]:
                # Find critical issues
                critical_metrics = [
                    name for name, health in self.system_health.items() 
                    if health < 60.0
                ]
                
                for metric_name in critical_metrics:
                    component_map = {
                        "cpu_percentage": SystemComponent.COMPUTE,
                        "memory_percentage": SystemComponent.MEMORY,
                        "error_rate": SystemComponent.SECURITY
                    }
                    
                    component = component_map.get(metric_name, SystemComponent.COMPUTE)
                    self.trigger_healing(component, f"Low health score: {self.system_health[metric_name]:.1f}")
            
        except Exception as e:
            logger.error(f"[SELF_MGMT] Error checking healing opportunities: {e}")
    
    def _check_maintenance_schedule(self):
        """Check if scheduled maintenance is due"""
        try:
            current_time = datetime.now()
            current_hour = current_time.hour
            
            # Check if we're in maintenance window
            if self.config["maintenance_window"] == f"{current_hour:02d}:00-{current_hour+1:02d}:00":
                # Trigger daily maintenance
                maintenance_task = ManagementTask(
                    task_id=f"maint_{uuid.uuid4().hex[:8]}",
                    action_type=ManagementAction.MAINTENANCE,
                    component=SystemComponent.DATABASE,
                    description="Scheduled daily maintenance",
                    priority=5
                )
                
                self.add_management_task(maintenance_task)
            
        except Exception as e:
            logger.error(f"[SELF_MGMT] Error checking maintenance schedule: {e}")
    
    def _validate_healing_results(self):
        """Validate results of previous healing actions"""
        try:
            # Check recent healing tasks
            recent_healing = [
                task for task in self.completed_tasks[-5:]
                if task.action_type == ManagementAction.HEALING and task.status == "completed"
            ]
            
            for task in recent_healing:
                # Simulate validation
                if task.result and task.result.get("recovery_status") == "successful":
                    logger.info(f"[SELF_MGMT] Healing validation successful: {task.task_id}")
            
        except Exception as e:
            logger.error(f"[SELF_MGMT] Error validating healing results: {e}")
    
    def _calculate_system_health(self) -> float:
        """Calculate overall system health score"""
        if not self.system_health:
            return 85.0  # Default health
        
        return sum(self.system_health.values()) / len(self.system_health)
    
    def _get_metric_status(self, metric: SystemMetric) -> str:
        """Get status of a metric"""
        if metric.current_value >= metric.threshold_critical:
            return "critical"
        elif metric.current_value >= metric.threshold_warning:
            return "warning"
        else:
            return "normal"
    
    def _identify_optimization_opportunities(self) -> List[Dict[str, Any]]:
        """Identify current optimization opportunities"""
        opportunities = []
        
        for name, metric in self.system_metrics.items():
            if metric.current_value > metric.threshold_warning:
                opportunities.append({
                    "metric": name,
                    "current_value": metric.current_value,
                    "threshold": metric.threshold_warning,
                    "improvement_potential": ((metric.current_value - metric.threshold_warning) / metric.threshold_warning) * 100
                })
        
        return opportunities
    
    def _calculate_management_score(self) -> float:
        """Calculate self-management effectiveness score"""
        try:
            base_score = 80.0
            
            # Adjust based on task success rate
            if self.completed_tasks:
                success_rate = len([t for t in self.completed_tasks if t.status == "completed"]) / len(self.completed_tasks)
                base_score += (success_rate - 0.8) * 50  # Bonus/penalty for success rate
            
            # Adjust based on system health
            avg_health = self._calculate_system_health()
            base_score += (avg_health - 80) * 0.2
            
            # Adjust based on optimization frequency
            if self.metrics["optimizations_performed"] > 0:
                base_score += min(self.metrics["optimizations_performed"] * 2, 10)
            
            return min(max(base_score, 0.0), 100.0)
            
        except Exception as e:
            logger.error(f"[SELF_MGMT] Error calculating management score: {e}")
            return 75.0


def create_self_management_system(node_id: str = "self_manager") -> SelfManagementSystem:
    """Create and configure self-management system"""
    return SelfManagementSystem(node_id)


def create_management_task(action_type: ManagementAction, component: SystemComponent,
                          description: str, priority: int = 5, **kwargs) -> ManagementTask:
    """Create management task"""
    return ManagementTask(
        task_id=f"mgmt_{uuid.uuid4().hex[:8]}",
        action_type=action_type,
        component=component,
        description=description,
        priority=priority,
        parameters=kwargs
    )