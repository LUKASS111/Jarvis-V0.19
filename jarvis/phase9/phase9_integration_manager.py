#!/usr/bin/env python3
"""
Phase 9 Integration Manager
===========================

Orchestrates all Phase 9 autonomous intelligence and predictive systems,
providing unified interface and comprehensive coordination.
"""

import asyncio
import time
import json
import threading
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass
import logging
import uuid

from .autonomous_intelligence_manager import (
    AutonomousIntelligenceManager, AutonomousMode, AutonomousTask, TaskPriority
)
from .predictive_analytics_engine import (
    PredictiveAnalyticsEngine, PredictionType, simulate_predictive_data
)

logger = logging.getLogger(__name__)


@dataclass
class Phase9Request:
    """Phase 9 request structure"""
    request_id: str
    request_type: str
    content: str
    parameters: Dict[str, Any]
    timestamp: datetime
    autonomous_mode: bool = False
    predictive_analysis: bool = False


class Phase9IntegrationManager:
    """
    Comprehensive Phase 9 integration system for autonomous intelligence
    and predictive analytics coordination
    """
    
    def __init__(self, node_id: str = "phase9_master"):
        self.node_id = node_id
        self.is_active = False
        
        # Core Phase 9 components
        self.autonomous_ai: Optional[AutonomousIntelligenceManager] = None
        self.predictive_engine: Optional[PredictiveAnalyticsEngine] = None
        
        # Request processing
        self.request_queue: List[Phase9Request] = []
        self.processed_requests: List[Phase9Request] = []
        
        # Integration state
        self.system_health = {
            "autonomous_intelligence": 0.0,
            "predictive_analytics": 0.0,
            "integration_status": 0.0,
            "overall_health": 0.0
        }
        
        # Performance metrics
        self.metrics = {
            "requests_processed": 0,
            "autonomous_decisions": 0,
            "predictions_made": 0,
            "system_optimizations": 0,
            "uptime_hours": 0.0,
            "success_rate": 0.0
        }
        
        # Configuration
        self.config = {
            "autonomous_mode": AutonomousMode.PROACTIVE,
            "enable_predictive": True,
            "auto_optimization": True,
            "learning_enabled": True,
            "proactive_assistance": True
        }
        
        # Threading
        self.integration_thread: Optional[threading.Thread] = None
        self.monitoring_thread: Optional[threading.Thread] = None
        self.start_time = datetime.now()
        
        logger.info(f"[PHASE9] Integration manager initialized for {node_id}")
    
    def start(self) -> bool:
        """Start Phase 9 integration system"""
        try:
            if self.is_active:
                return True
            
            self.is_active = True
            
            # Initialize autonomous intelligence
            self.autonomous_ai = AutonomousIntelligenceManager(
                f"{self.node_id}_autonomous", 
                self.config["autonomous_mode"]
            )
            
            # Initialize predictive analytics
            self.predictive_engine = PredictiveAnalyticsEngine(f"{self.node_id}_predictive")
            
            # Start subsystems
            ai_started = self.autonomous_ai.start()
            predictive_started = self.predictive_engine.start()
            
            if not (ai_started and predictive_started):
                logger.error("[PHASE9] Failed to start subsystems")
                return False
            
            # Start integration threads
            self.integration_thread = threading.Thread(target=self._integration_loop, daemon=True)
            self.monitoring_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            
            self.integration_thread.start()
            self.monitoring_thread.start()
            
            # Initialize with sample data
            self._initialize_sample_data()
            
            logger.info("[PHASE9] Integration system started successfully")
            return True
            
        except Exception as e:
            logger.error(f"[PHASE9] Failed to start: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop Phase 9 integration system"""
        try:
            self.is_active = False
            
            # Stop subsystems
            if self.autonomous_ai:
                self.autonomous_ai.stop()
            if self.predictive_engine:
                self.predictive_engine.stop()
            
            # Wait for threads
            if self.integration_thread:
                self.integration_thread.join(timeout=5)
            if self.monitoring_thread:
                self.monitoring_thread.join(timeout=5)
            
            logger.info("[PHASE9] Integration system stopped")
            return True
            
        except Exception as e:
            logger.error(f"[PHASE9] Error stopping: {e}")
            return False
    
    def process_request(self, content: str, request_type: str = "general", 
                       parameters: Dict[str, Any] = None, 
                       autonomous_mode: bool = False) -> Dict[str, Any]:
        """Process Phase 9 request with autonomous intelligence and predictive analytics"""
        try:
            request = Phase9Request(
                request_id=f"phase9_{uuid.uuid4().hex[:8]}",
                request_type=request_type,
                content=content,
                parameters=parameters or {},
                timestamp=datetime.now(),
                autonomous_mode=autonomous_mode,
                predictive_analysis=True
            )
            
            # Process with autonomous intelligence if enabled
            autonomous_result = None
            if autonomous_mode and self.autonomous_ai and self.autonomous_ai.is_active:
                autonomous_result = self._process_with_autonomous_ai(request)
            
            # Perform predictive analysis
            predictive_result = None
            if self.predictive_engine and self.predictive_engine.is_active:
                predictive_result = self._process_with_predictive_analytics(request)
            
            # Combine results
            result = self._combine_processing_results(request, autonomous_result, predictive_result)
            
            # Update metrics
            self.metrics["requests_processed"] += 1
            self.processed_requests.append(request)
            
            logger.info(f"[PHASE9] Request processed: {request.request_id}")
            return result
            
        except Exception as e:
            logger.error(f"[PHASE9] Error processing request: {e}")
            return {"success": False, "error": str(e)}
    
    def get_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive Phase 9 dashboard"""
        return {
            "overview": {
                "node_id": self.node_id,
                "is_active": self.is_active,
                "uptime_hours": (datetime.now() - self.start_time).total_seconds() / 3600,
                "overall_health": self.system_health["overall_health"],
                "autonomous_mode": self.config["autonomous_mode"].value if self.autonomous_ai else "disabled",
                "predictive_enabled": self.config["enable_predictive"]
            },
            "autonomous_intelligence": self._get_autonomous_dashboard(),
            "predictive_analytics": self._get_predictive_dashboard(),
            "integration_status": {
                "request_queue_size": len(self.request_queue),
                "processed_requests": len(self.processed_requests),
                "system_optimizations": self.metrics["system_optimizations"],
                "success_rate": self.metrics.get("success_rate", 0.0)
            },
            "performance_metrics": self.metrics.copy(),
            "system_health": self.system_health.copy(),
            "recent_activity": self._get_recent_activity(),
            "predictive_insights": self._get_predictive_insights(),
            "autonomous_capabilities": self._get_autonomous_capabilities()
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get Phase 9 system health status"""
        # Update health metrics
        self._update_health_metrics()
        
        return {
            "phase": "Phase 9: Autonomous Intelligence & Predictive Systems",
            "status": "operational" if self.system_health["overall_health"] > 80 else "degraded",
            "overall_health": self.system_health["overall_health"],
            "component_health": {
                "autonomous_intelligence": self.system_health["autonomous_intelligence"],
                "predictive_analytics": self.system_health["predictive_analytics"],
                "integration_status": self.system_health["integration_status"]
            },
            "capabilities": {
                "autonomous_decision_making": self.autonomous_ai.is_active if self.autonomous_ai else False,
                "predictive_forecasting": self.predictive_engine.is_active if self.predictive_engine else False,
                "proactive_optimization": self.config["auto_optimization"],
                "continuous_learning": self.config["learning_enabled"]
            },
            "metrics": {
                "uptime_hours": (datetime.now() - self.start_time).total_seconds() / 3600,
                "decisions_made": self.metrics.get("autonomous_decisions", 0),
                "predictions_made": self.metrics.get("predictions_made", 0),
                "optimizations_applied": self.metrics.get("system_optimizations", 0)
            },
            "last_updated": datetime.now().isoformat()
        }
    
    def enable_autonomous_mode(self, mode: AutonomousMode = AutonomousMode.PROACTIVE) -> bool:
        """Enable autonomous operation mode"""
        try:
            if self.autonomous_ai:
                success = self.autonomous_ai.set_mode(mode)
                if success:
                    self.config["autonomous_mode"] = mode
                    logger.info(f"[PHASE9] Autonomous mode set to: {mode.value}")
                return success
            return False
            
        except Exception as e:
            logger.error(f"[PHASE9] Error enabling autonomous mode: {e}")
            return False
    
    def create_autonomous_assistant(self, assistant_name: str, 
                                  capabilities: List[str] = None) -> Dict[str, Any]:
        """Create specialized autonomous assistant"""
        try:
            if not self.autonomous_ai:
                return {"success": False, "error": "Autonomous AI not available"}
            
            # Create autonomous task for assistant creation
            task = AutonomousTask(
                task_id=f"create_assistant_{uuid.uuid4().hex[:8]}",
                task_type="assistant_creation",
                priority=TaskPriority.HIGH,
                description=f"Create autonomous assistant: {assistant_name}",
                parameters={
                    "name": assistant_name,
                    "capabilities": capabilities or ["analysis", "optimization", "monitoring"]
                }
            )
            
            success = self.autonomous_ai.add_autonomous_task(task)
            
            return {
                "success": success,
                "assistant_id": task.task_id,
                "name": assistant_name,
                "capabilities": capabilities or ["analysis", "optimization", "monitoring"],
                "status": "creating" if success else "failed"
            }
            
        except Exception as e:
            logger.error(f"[PHASE9] Error creating autonomous assistant: {e}")
            return {"success": False, "error": str(e)}
    
    def _integration_loop(self):
        """Main integration coordination loop"""
        while self.is_active:
            try:
                # Coordinate autonomous and predictive systems
                self._coordinate_systems()
                
                # Process any queued requests
                self._process_request_queue()
                
                # Perform system optimizations
                if self.config["auto_optimization"]:
                    self._perform_system_optimizations()
                
                # Update metrics
                self._update_metrics()
                
                time.sleep(10)  # Integration loop interval
                
            except Exception as e:
                logger.error(f"[PHASE9] Error in integration loop: {e}")
                time.sleep(30)
    
    def _monitoring_loop(self):
        """System health monitoring loop"""
        while self.is_active:
            try:
                # Monitor subsystem health
                self._update_health_metrics()
                
                # Check for issues
                self._check_system_issues()
                
                # Update uptime
                self.metrics["uptime_hours"] = (datetime.now() - self.start_time).total_seconds() / 3600
                
                time.sleep(30)  # Monitoring interval
                
            except Exception as e:
                logger.error(f"[PHASE9] Error in monitoring loop: {e}")
                time.sleep(60)
    
    def _process_with_autonomous_ai(self, request: Phase9Request) -> Dict[str, Any]:
        """Process request with autonomous intelligence"""
        try:
            if not self.autonomous_ai or not self.autonomous_ai.is_active:
                return {"success": False, "reason": "Autonomous AI not available"}
            
            # Create context for autonomous decision
            context = {
                "request_type": request.request_type,
                "content": request.content,
                "parameters": request.parameters,
                "timestamp": request.timestamp.isoformat()
            }
            
            # Make autonomous decision
            decision = self.autonomous_ai.make_autonomous_decision(context)
            
            if decision:
                self.metrics["autonomous_decisions"] += 1
                
                return {
                    "success": True,
                    "decision_id": decision.decision_id,
                    "decision_type": decision.decision_type.value,
                    "confidence": decision.confidence,
                    "reasoning": decision.reasoning,
                    "action_plan": decision.action_plan,
                    "expected_outcome": decision.expected_outcome
                }
            else:
                return {"success": False, "reason": "No autonomous decision made"}
            
        except Exception as e:
            logger.error(f"[PHASE9] Error in autonomous processing: {e}")
            return {"success": False, "error": str(e)}
    
    def _process_with_predictive_analytics(self, request: Phase9Request) -> Dict[str, Any]:
        """Process request with predictive analytics"""
        try:
            if not self.predictive_engine or not self.predictive_engine.is_active:
                return {"success": False, "reason": "Predictive engine not available"}
            
            # Add current request data
            self.predictive_engine.add_data_point("request_rate", 1.0, {
                "type": request.request_type,
                "timestamp": request.timestamp.isoformat()
            })
            
            # Make predictions based on request
            predictions = []
            
            # Performance prediction
            perf_prediction = self.predictive_engine.make_prediction(
                PredictionType.PERFORMANCE, "request_rate", 3600
            )
            if perf_prediction:
                predictions.append({
                    "type": "performance",
                    "prediction_id": perf_prediction.prediction_id,
                    "confidence": perf_prediction.confidence,
                    "time_horizon": perf_prediction.time_horizon,
                    "prediction": perf_prediction.prediction
                })
            
            # Resource prediction
            resource_prediction = self.predictive_engine.make_prediction(
                PredictionType.RESOURCE, "cpu_usage", 1800
            )
            if resource_prediction:
                predictions.append({
                    "type": "resource",
                    "prediction_id": resource_prediction.prediction_id,
                    "confidence": resource_prediction.confidence,
                    "time_horizon": resource_prediction.time_horizon,
                    "prediction": resource_prediction.prediction
                })
            
            self.metrics["predictions_made"] += len(predictions)
            
            return {
                "success": True,
                "predictions": predictions,
                "insights": self.predictive_engine.get_predictive_insights()
            }
            
        except Exception as e:
            logger.error(f"[PHASE9] Error in predictive processing: {e}")
            return {"success": False, "error": str(e)}
    
    def _combine_processing_results(self, request: Phase9Request, 
                                  autonomous_result: Dict[str, Any], 
                                  predictive_result: Dict[str, Any]) -> Dict[str, Any]:
        """Combine autonomous and predictive processing results"""
        combined_result = {
            "request_id": request.request_id,
            "request_type": request.request_type,
            "processed_at": datetime.now().isoformat(),
            "success": True,
            "phase9_capabilities": {
                "autonomous_intelligence": autonomous_result is not None,
                "predictive_analytics": predictive_result is not None
            }
        }
        
        # Add autonomous results
        if autonomous_result and autonomous_result.get("success"):
            combined_result["autonomous_analysis"] = autonomous_result
        
        # Add predictive results
        if predictive_result and predictive_result.get("success"):
            combined_result["predictive_analysis"] = predictive_result
        
        # Generate recommendations
        combined_result["recommendations"] = self._generate_recommendations(
            request, autonomous_result, predictive_result
        )
        
        return combined_result
    
    def _generate_recommendations(self, request: Phase9Request, 
                                autonomous_result: Dict[str, Any], 
                                predictive_result: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate integrated recommendations"""
        recommendations = []
        
        # Autonomous recommendations
        if autonomous_result and autonomous_result.get("success"):
            if autonomous_result.get("confidence", 0) > 0.8:
                recommendations.append({
                    "type": "autonomous_action",
                    "priority": "high",
                    "description": "Execute autonomous optimization based on high-confidence decision",
                    "source": "autonomous_intelligence"
                })
        
        # Predictive recommendations
        if predictive_result and predictive_result.get("success"):
            predictions = predictive_result.get("predictions", [])
            for pred in predictions:
                if pred.get("confidence", 0) > 0.7:
                    recommendations.append({
                        "type": "predictive_preparation",
                        "priority": "medium",
                        "description": f"Prepare for predicted {pred['type']} changes",
                        "source": "predictive_analytics"
                    })
        
        # Default recommendation
        if not recommendations:
            recommendations.append({
                "type": "monitoring",
                "priority": "low",
                "description": "Continue monitoring system performance",
                "source": "integration_manager"
            })
        
        return recommendations
    
    def _coordinate_systems(self):
        """Coordinate autonomous and predictive systems"""
        try:
            # Share insights between systems
            if (self.autonomous_ai and self.autonomous_ai.is_active and 
                self.predictive_engine and self.predictive_engine.is_active):
                
                # Get autonomous status
                ai_status = self.autonomous_ai.get_autonomous_status()
                
                # Get predictive insights
                predictive_insights = self.predictive_engine.get_predictive_insights()
                
                # Coordinate optimization opportunities
                self._coordinate_optimizations(ai_status, predictive_insights)
            
        except Exception as e:
            logger.error(f"[PHASE9] Error coordinating systems: {e}")
    
    def _coordinate_optimizations(self, ai_status: Dict[str, Any], 
                                predictive_insights: Dict[str, Any]):
        """Coordinate optimization between systems"""
        try:
            # Check if autonomous system can act on predictions
            if (ai_status.get("autonomous_health", 0) > 80 and 
                predictive_insights.get("prediction_accuracy", 0) > 0.7):
                
                # Create optimization task
                if self.autonomous_ai and len(self.autonomous_ai.task_queue) < 3:
                    optimization_task = AutonomousTask(
                        task_id=f"coord_opt_{uuid.uuid4().hex[:8]}",
                        task_type="coordinated_optimization",
                        priority=TaskPriority.MEDIUM,
                        description="Coordinated optimization based on predictive insights",
                        parameters={"insights": predictive_insights}
                    )
                    
                    self.autonomous_ai.add_autonomous_task(optimization_task)
                    self.metrics["system_optimizations"] += 1
            
        except Exception as e:
            logger.error(f"[PHASE9] Error coordinating optimizations: {e}")
    
    def _process_request_queue(self):
        """Process queued requests"""
        try:
            for request in self.request_queue[:3]:  # Process up to 3 at a time
                self.process_request(
                    request.content, 
                    request.request_type, 
                    request.parameters,
                    request.autonomous_mode
                )
                self.request_queue.remove(request)
            
        except Exception as e:
            logger.error(f"[PHASE9] Error processing request queue: {e}")
    
    def _perform_system_optimizations(self):
        """Perform system-wide optimizations"""
        try:
            # Check if optimization is needed
            current_health = self.system_health["overall_health"]
            
            if current_health < 90:
                # Create optimization task
                if self.autonomous_ai and self.autonomous_ai.is_active:
                    opt_task = AutonomousTask(
                        task_id=f"sys_opt_{uuid.uuid4().hex[:8]}",
                        task_type="system_optimization",
                        priority=TaskPriority.HIGH,
                        description="System-wide performance optimization",
                        parameters={"target_health": 95}
                    )
                    
                    self.autonomous_ai.add_autonomous_task(opt_task)
            
        except Exception as e:
            logger.error(f"[PHASE9] Error performing optimizations: {e}")
    
    def _update_metrics(self):
        """Update system metrics"""
        try:
            # Calculate success rate
            if self.processed_requests:
                successful = len([r for r in self.processed_requests[-100:]])  # Last 100 requests
                self.metrics["success_rate"] = (successful / min(len(self.processed_requests), 100)) * 100
            
            # Update component metrics
            if self.autonomous_ai:
                ai_metrics = self.autonomous_ai.get_autonomous_status().get("metrics", {})
                self.metrics["autonomous_decisions"] = ai_metrics.get("decisions_made", 0)
            
            if self.predictive_engine:
                pred_insights = self.predictive_engine.get_predictive_insights()
                self.metrics["predictions_made"] = pred_insights.get("current_predictions", 0)
            
        except Exception as e:
            logger.error(f"[PHASE9] Error updating metrics: {e}")
    
    def _update_health_metrics(self):
        """Update system health metrics"""
        try:
            # Autonomous intelligence health
            if self.autonomous_ai and self.autonomous_ai.is_active:
                ai_status = self.autonomous_ai.get_autonomous_status()
                self.system_health["autonomous_intelligence"] = ai_status.get("autonomous_health", 0)
            else:
                self.system_health["autonomous_intelligence"] = 0
            
            # Predictive analytics health
            if self.predictive_engine and self.predictive_engine.is_active:
                pred_insights = self.predictive_engine.get_predictive_insights()
                accuracy = pred_insights.get("prediction_accuracy", 0.0)
                self.system_health["predictive_analytics"] = accuracy * 100
            else:
                self.system_health["predictive_analytics"] = 0
            
            # Integration health
            if self.is_active:
                self.system_health["integration_status"] = 95.0
            else:
                self.system_health["integration_status"] = 0
            
            # Overall health
            health_values = [
                self.system_health["autonomous_intelligence"],
                self.system_health["predictive_analytics"],
                self.system_health["integration_status"]
            ]
            self.system_health["overall_health"] = sum(health_values) / len(health_values)
            
        except Exception as e:
            logger.error(f"[PHASE9] Error updating health metrics: {e}")
    
    def _check_system_issues(self):
        """Check for system issues and take corrective action"""
        try:
            # Check autonomous AI health
            if (self.autonomous_ai and self.autonomous_ai.is_active and 
                self.system_health["autonomous_intelligence"] < 70):
                logger.warning("[PHASE9] Autonomous intelligence health below threshold")
            
            # Check predictive engine health
            if (self.predictive_engine and self.predictive_engine.is_active and 
                self.system_health["predictive_analytics"] < 60):
                logger.warning("[PHASE9] Predictive analytics health below threshold")
            
            # Check overall health
            if self.system_health["overall_health"] < 70:
                logger.warning(f"[PHASE9] Overall system health low: {self.system_health['overall_health']:.1f}%")
            
        except Exception as e:
            logger.error(f"[PHASE9] Error checking system issues: {e}")
    
    def _initialize_sample_data(self):
        """Initialize with sample data for demonstration"""
        try:
            if self.predictive_engine:
                # Simulate performance data
                simulate_predictive_data(self.predictive_engine, "cpu_usage", 50)
                simulate_predictive_data(self.predictive_engine, "memory_usage", 50)
                simulate_predictive_data(self.predictive_engine, "request_rate", 50)
                
                logger.info("[PHASE9] Sample data initialized")
            
        except Exception as e:
            logger.error(f"[PHASE9] Error initializing sample data: {e}")
    
    def _get_autonomous_dashboard(self) -> Dict[str, Any]:
        """Get autonomous intelligence dashboard data"""
        if self.autonomous_ai and self.autonomous_ai.is_active:
            return self.autonomous_ai.get_autonomous_status()
        else:
            return {"status": "inactive", "reason": "Autonomous AI not active"}
    
    def _get_predictive_dashboard(self) -> Dict[str, Any]:
        """Get predictive analytics dashboard data"""
        if self.predictive_engine and self.predictive_engine.is_active:
            return self.predictive_engine.get_predictive_insights()
        else:
            return {"status": "inactive", "reason": "Predictive engine not active"}
    
    def _get_recent_activity(self) -> List[Dict[str, Any]]:
        """Get recent system activity"""
        activities = []
        
        # Recent requests
        for req in self.processed_requests[-5:]:
            activities.append({
                "type": "request_processed",
                "timestamp": req.timestamp.isoformat(),
                "details": f"Processed {req.request_type} request"
            })
        
        # Autonomous decisions
        if self.autonomous_ai:
            ai_status = self.autonomous_ai.get_autonomous_status()
            if ai_status.get("metrics", {}).get("decisions_made", 0) > 0:
                activities.append({
                    "type": "autonomous_decision",
                    "timestamp": datetime.now().isoformat(),
                    "details": f"Made {ai_status['metrics']['decisions_made']} autonomous decisions"
                })
        
        return activities[-10:]  # Last 10 activities
    
    def _get_predictive_insights(self) -> Dict[str, Any]:
        """Get predictive insights summary"""
        if self.predictive_engine and self.predictive_engine.is_active:
            insights = self.predictive_engine.get_predictive_insights()
            return {
                "predictions_active": insights.get("current_predictions", 0),
                "accuracy": insights.get("prediction_accuracy", 0.0),
                "recent_forecasts": insights.get("system_forecasts", {}),
                "recommendations": insights.get("recommended_actions", [])
            }
        else:
            return {"status": "inactive"}
    
    def _get_autonomous_capabilities(self) -> Dict[str, Any]:
        """Get autonomous capabilities summary"""
        if self.autonomous_ai and self.autonomous_ai.is_active:
            status = self.autonomous_ai.get_autonomous_status()
            return {
                "mode": status.get("mode", "unknown"),
                "active_tasks": status.get("active_tasks", 0),
                "completed_tasks": status.get("completed_tasks", 0),
                "decision_making": "enabled",
                "learning": "active",
                "optimization": "operational"
            }
        else:
            return {"status": "inactive"}


# Module-level functions for easy access
def process_phase9_request(content: str, request_type: str = "general", 
                          parameters: Dict[str, Any] = None, 
                          autonomous_mode: bool = False) -> Dict[str, Any]:
    """Process request with Phase 9 capabilities"""
    manager = Phase9IntegrationManager()
    manager.start()
    result = manager.process_request(content, request_type, parameters, autonomous_mode)
    manager.stop()
    return result


def get_phase9_dashboard() -> Dict[str, Any]:
    """Get Phase 9 system dashboard"""
    manager = Phase9IntegrationManager()
    manager.start()
    dashboard = manager.get_dashboard()
    manager.stop()
    return dashboard


def get_phase9_health() -> Dict[str, Any]:
    """Get Phase 9 system health"""
    manager = Phase9IntegrationManager()
    manager.start()
    health = manager.get_health_status()
    manager.stop()
    return health


def create_autonomous_assistant(name: str, capabilities: List[str] = None) -> Dict[str, Any]:
    """Create autonomous assistant"""
    manager = Phase9IntegrationManager()
    manager.start()
    result = manager.create_autonomous_assistant(name, capabilities)
    manager.stop()
    return result


def enable_predictive_mode() -> bool:
    """Enable predictive analytics mode"""
    manager = Phase9IntegrationManager()
    manager.start()
    # Predictive mode is enabled by default
    success = manager.config["enable_predictive"]
    manager.stop()
    return success