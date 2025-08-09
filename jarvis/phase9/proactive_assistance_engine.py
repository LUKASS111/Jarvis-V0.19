#!/usr/bin/env python3
"""
Proactive Assistance Engine
===========================

Advanced proactive assistance system that anticipates user needs,
provides contextual help, and offers intelligent recommendations.
"""

import time
import json
import threading
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import logging
import uuid
from collections import defaultdict, deque

logger = logging.getLogger(__name__)


class AssistanceType(Enum):
    """Types of proactive assistance"""
    SUGGESTION = "suggestion"
    WARNING = "warning"
    OPTIMIZATION = "optimization"
    TUTORIAL = "tutorial"
    AUTOMATION = "automation"
    PREDICTION = "prediction"


class AssistanceCategory(Enum):
    """Categories of assistance"""
    PRODUCTIVITY = "productivity"
    PERFORMANCE = "performance"
    SECURITY = "security"
    LEARNING = "learning"
    MAINTENANCE = "maintenance"
    WORKFLOW = "workflow"


class UrgencyLevel(Enum):
    """Urgency levels for assistance"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class ProactiveAssistance:
    """Proactive assistance item"""
    assistance_id: str
    assistance_type: AssistanceType
    category: AssistanceCategory
    urgency: UrgencyLevel
    title: str
    description: str
    recommendations: List[str]
    confidence: float  # 0.0 to 1.0
    context: Dict[str, Any] = field(default_factory=dict)
    created_at: datetime = field(default_factory=datetime.now)
    shown_to_user: bool = False
    user_action_taken: Optional[str] = None
    effectiveness_score: Optional[float] = None


@dataclass
class UserContext:
    """User context information"""
    current_task: Optional[str] = None
    recent_actions: List[str] = field(default_factory=list)
    preferences: Dict[str, Any] = field(default_factory=dict)
    skill_level: str = "intermediate"
    common_workflows: List[str] = field(default_factory=list)
    time_patterns: Dict[str, Any] = field(default_factory=dict)
    last_active: datetime = field(default_factory=datetime.now)


@dataclass
class AssistancePattern:
    """Pattern for generating assistance"""
    pattern_id: str
    trigger_conditions: Dict[str, Any]
    assistance_template: Dict[str, Any]
    success_rate: float = 0.0
    usage_count: int = 0


class ProactiveAssistanceEngine:
    """
    Advanced proactive assistance engine for intelligent user support
    """
    
    def __init__(self, node_id: str = "proactive_assistant"):
        self.node_id = node_id
        self.is_active = False
        
        # Assistance state
        self.active_assistance: List[ProactiveAssistance] = []
        self.assistance_history: List[ProactiveAssistance] = []
        self.assistance_patterns: Dict[str, AssistancePattern] = {}
        
        # User context
        self.user_context = UserContext()
        self.user_sessions: Dict[str, Dict[str, Any]] = {}
        self.interaction_history: deque = deque(maxlen=1000)
        
        # Learning and adaptation
        self.behavioral_patterns: Dict[str, Any] = {}
        self.assistance_effectiveness: Dict[str, float] = {}
        self.context_triggers: Dict[str, List[str]] = defaultdict(list)
        
        # Configuration
        self.config = {
            "proactive_mode": True,
            "learning_enabled": True,
            "max_active_assistance": 5,
            "assistance_cooldown": 300,  # seconds
            "confidence_threshold": 0.6,
            "urgency_escalation": True,
            "personalization_enabled": True
        }
        
        # Performance metrics
        self.metrics = {
            "assistance_provided": 0,
            "user_actions_taken": 0,
            "assistance_accuracy": 0.0,
            "user_satisfaction": 0.0,
            "time_saved_minutes": 0.0,
            "proactive_success_rate": 0.0
        }
        
        # Threading
        self.assistance_thread: Optional[threading.Thread] = None
        self.learning_thread: Optional[threading.Thread] = None
        self.context_thread: Optional[threading.Thread] = None
        
        logger.info(f"[PROACTIVE] Assistance engine initialized for {node_id}")
    
    def start(self) -> bool:
        """Start proactive assistance engine"""
        try:
            if self.is_active:
                return True
            
            self.is_active = True
            
            # Initialize assistance patterns
            self._initialize_assistance_patterns()
            
            # Initialize user context
            self._initialize_user_context()
            
            # Start processing threads
            self.assistance_thread = threading.Thread(target=self._assistance_loop, daemon=True)
            self.learning_thread = threading.Thread(target=self._learning_loop, daemon=True)
            self.context_thread = threading.Thread(target=self._context_monitoring_loop, daemon=True)
            
            self.assistance_thread.start()
            self.learning_thread.start()
            self.context_thread.start()
            
            logger.info("[PROACTIVE] Assistance engine started")
            return True
            
        except Exception as e:
            logger.error(f"[PROACTIVE] Failed to start: {e}")
            return False
    
    def stop(self) -> bool:
        """Stop proactive assistance engine"""
        try:
            self.is_active = False
            
            # Wait for threads
            if self.assistance_thread:
                self.assistance_thread.join(timeout=5)
            if self.learning_thread:
                self.learning_thread.join(timeout=5)
            if self.context_thread:
                self.context_thread.join(timeout=5)
            
            logger.info("[PROACTIVE] Assistance engine stopped")
            return True
            
        except Exception as e:
            logger.error(f"[PROACTIVE] Error stopping: {e}")
            return False
    
    def update_user_context(self, action: str, context: Dict[str, Any] = None) -> bool:
        """Update user context with new action"""
        try:
            # Update recent actions
            self.user_context.recent_actions.append(action)
            if len(self.user_context.recent_actions) > 20:
                self.user_context.recent_actions.pop(0)
            
            # Update last active time
            self.user_context.last_active = datetime.now()
            
            # Record interaction
            interaction = {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "context": context or {}
            }
            self.interaction_history.append(interaction)
            
            # Analyze for immediate assistance opportunities
            if self.config["proactive_mode"]:
                self._analyze_immediate_assistance_opportunities(action, context)
            
            return True
            
        except Exception as e:
            logger.error(f"[PROACTIVE] Failed to update user context: {e}")
            return False
    
    def generate_proactive_assistance(self, context: Dict[str, Any] = None) -> List[ProactiveAssistance]:
        """Generate proactive assistance based on current context"""
        try:
            assistance_items = []
            
            # Analyze current context
            current_context = context or self._get_current_context()
            
            # Generate assistance based on patterns
            for pattern_id, pattern in self.assistance_patterns.items():
                if self._matches_pattern(current_context, pattern):
                    assistance = self._create_assistance_from_pattern(pattern, current_context)
                    if assistance and assistance.confidence >= self.config["confidence_threshold"]:
                        assistance_items.append(assistance)
            
            # Sort by urgency and confidence
            assistance_items.sort(key=lambda a: (list(UrgencyLevel).index(a.urgency), a.confidence), reverse=True)
            
            # Limit active assistance
            max_items = self.config["max_active_assistance"]
            assistance_items = assistance_items[:max_items]
            
            # Add to active assistance
            for assistance in assistance_items:
                self.active_assistance.append(assistance)
                self.metrics["assistance_provided"] += 1
            
            logger.info(f"[PROACTIVE] Generated {len(assistance_items)} assistance items")
            return assistance_items
            
        except Exception as e:
            logger.error(f"[PROACTIVE] Error generating assistance: {e}")
            return []
    
    def provide_contextual_help(self, query: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Provide contextual help for specific query"""
        try:
            # Analyze query and context
            help_type = self._analyze_help_query(query)
            current_context = context or self._get_current_context()
            
            # Generate contextual response
            response = self._generate_contextual_response(query, help_type, current_context)
            
            # Create assistance item
            assistance = ProactiveAssistance(
                assistance_id=f"help_{uuid.uuid4().hex[:8]}",
                assistance_type=AssistanceType.TUTORIAL,
                category=AssistanceCategory.LEARNING,
                urgency=UrgencyLevel.MEDIUM,
                title=f"Help: {query}",
                description=response["description"],
                recommendations=response["recommendations"],
                confidence=response["confidence"],
                context=current_context
            )
            
            self.assistance_history.append(assistance)
            
            return {
                "assistance_id": assistance.assistance_id,
                "help_provided": response,
                "follow_up_available": True,
                "related_topics": response.get("related_topics", [])
            }
            
        except Exception as e:
            logger.error(f"[PROACTIVE] Error providing contextual help: {e}")
            return {"error": str(e)}
    
    def suggest_workflow_optimization(self, workflow_name: str) -> Dict[str, Any]:
        """Suggest optimizations for user workflow"""
        try:
            # Analyze workflow patterns
            workflow_analysis = self._analyze_workflow(workflow_name)
            
            # Generate optimization suggestions
            optimizations = self._generate_workflow_optimizations(workflow_analysis)
            
            # Create assistance item
            assistance = ProactiveAssistance(
                assistance_id=f"workflow_opt_{uuid.uuid4().hex[:8]}",
                assistance_type=AssistanceType.OPTIMIZATION,
                category=AssistanceCategory.WORKFLOW,
                urgency=UrgencyLevel.MEDIUM,
                title=f"Optimize {workflow_name} Workflow",
                description=f"Potential optimizations for your {workflow_name} workflow",
                recommendations=optimizations["suggestions"],
                confidence=optimizations["confidence"],
                context={"workflow": workflow_name, "analysis": workflow_analysis}
            )
            
            self.active_assistance.append(assistance)
            
            return {
                "assistance_id": assistance.assistance_id,
                "workflow_analysis": workflow_analysis,
                "optimizations": optimizations,
                "estimated_time_savings": optimizations.get("time_savings", 0)
            }
            
        except Exception as e:
            logger.error(f"[PROACTIVE] Error suggesting workflow optimization: {e}")
            return {"error": str(e)}
    
    def predict_user_needs(self, time_horizon_minutes: int = 60) -> List[Dict[str, Any]]:
        """Predict user needs based on patterns"""
        try:
            predictions = []
            
            # Analyze time patterns
            current_time = datetime.now()
            time_context = {
                "hour": current_time.hour,
                "day_of_week": current_time.weekday(),
                "time_of_day": self._get_time_of_day(current_time)
            }
            
            # Predict based on historical patterns
            historical_predictions = self._predict_from_history(time_context, time_horizon_minutes)
            predictions.extend(historical_predictions)
            
            # Predict based on current context
            context_predictions = self._predict_from_context(self.user_context, time_horizon_minutes)
            predictions.extend(context_predictions)
            
            # Sort by confidence
            predictions.sort(key=lambda p: p.get("confidence", 0), reverse=True)
            
            return predictions[:5]  # Top 5 predictions
            
        except Exception as e:
            logger.error(f"[PROACTIVE] Error predicting user needs: {e}")
            return []
    
    def record_user_action(self, assistance_id: str, action_taken: str, 
                          satisfaction_score: float = None) -> bool:
        """Record user action on assistance"""
        try:
            # Find assistance item
            assistance = None
            for item in self.active_assistance:
                if item.assistance_id == assistance_id:
                    assistance = item
                    break
            
            if not assistance:
                # Check history
                for item in self.assistance_history:
                    if item.assistance_id == assistance_id:
                        assistance = item
                        break
            
            if not assistance:
                return False
            
            # Record action
            assistance.user_action_taken = action_taken
            assistance.shown_to_user = True
            
            if satisfaction_score is not None:
                assistance.effectiveness_score = satisfaction_score
                self._update_pattern_effectiveness(assistance, satisfaction_score)
            
            # Update metrics
            if action_taken != "dismissed":
                self.metrics["user_actions_taken"] += 1
            
            # Learn from interaction
            self._learn_from_user_action(assistance, action_taken, satisfaction_score)
            
            # Move to history if from active
            if assistance in self.active_assistance:
                self.active_assistance.remove(assistance)
                self.assistance_history.append(assistance)
            
            logger.info(f"[PROACTIVE] User action recorded: {assistance_id} -> {action_taken}")
            return True
            
        except Exception as e:
            logger.error(f"[PROACTIVE] Error recording user action: {e}")
            return False
    
    def get_assistance_status(self) -> Dict[str, Any]:
        """Get comprehensive assistance engine status"""
        return {
            "node_id": self.node_id,
            "is_active": self.is_active,
            "proactive_mode": self.config["proactive_mode"],
            "active_assistance_count": len(self.active_assistance),
            "assistance_history_count": len(self.assistance_history),
            "patterns_learned": len(self.assistance_patterns),
            "user_context": {
                "current_task": self.user_context.current_task,
                "recent_actions_count": len(self.user_context.recent_actions),
                "skill_level": self.user_context.skill_level,
                "last_active": self.user_context.last_active.isoformat()
            },
            "metrics": self.metrics.copy(),
            "active_assistance": [
                {
                    "id": a.assistance_id,
                    "type": a.assistance_type.value,
                    "category": a.category.value,
                    "urgency": a.urgency.value,
                    "title": a.title,
                    "confidence": a.confidence,
                    "created": a.created_at.isoformat()
                }
                for a in self.active_assistance
            ],
            "behavioral_insights": self._get_behavioral_insights(),
            "effectiveness_summary": self._get_effectiveness_summary()
        }
    
    def _assistance_loop(self):
        """Main proactive assistance loop"""
        while self.is_active:
            try:
                if self.config["proactive_mode"]:
                    # Generate new assistance opportunities
                    self.generate_proactive_assistance()
                    
                    # Check for urgent assistance needs
                    self._check_urgent_assistance_needs()
                    
                    # Clean up old assistance
                    self._cleanup_old_assistance()
                
                time.sleep(30)  # Assistance generation interval
                
            except Exception as e:
                logger.error(f"[PROACTIVE] Error in assistance loop: {e}")
                time.sleep(60)
    
    def _learning_loop(self):
        """Learning and adaptation loop"""
        while self.is_active:
            try:
                if self.config["learning_enabled"]:
                    # Learn from user interactions
                    self._learn_behavioral_patterns()
                    
                    # Update assistance patterns
                    self._update_assistance_patterns()
                    
                    # Adapt to user preferences
                    self._adapt_to_user_preferences()
                    
                    # Update effectiveness metrics
                    self._update_effectiveness_metrics()
                
                time.sleep(300)  # Learning interval
                
            except Exception as e:
                logger.error(f"[PROACTIVE] Error in learning loop: {e}")
                time.sleep(600)
    
    def _context_monitoring_loop(self):
        """Context monitoring and analysis loop"""
        while self.is_active:
            try:
                # Monitor user activity patterns
                self._monitor_activity_patterns()
                
                # Update time-based patterns
                self._update_time_patterns()
                
                # Detect workflow changes
                self._detect_workflow_changes()
                
                time.sleep(60)  # Context monitoring interval
                
            except Exception as e:
                logger.error(f"[PROACTIVE] Error in context monitoring: {e}")
                time.sleep(120)
    
    def _initialize_assistance_patterns(self):
        """Initialize default assistance patterns"""
        patterns = {
            "performance_optimization": {
                "trigger_conditions": {"slow_response": True, "high_cpu": True},
                "assistance_template": {
                    "type": AssistanceType.OPTIMIZATION,
                    "category": AssistanceCategory.PERFORMANCE,
                    "urgency": UrgencyLevel.MEDIUM,
                    "title": "Performance Optimization Available",
                    "recommendations": [
                        "Clear system cache",
                        "Optimize database queries",
                        "Review background processes"
                    ]
                }
            },
            "security_reminder": {
                "trigger_conditions": {"login_frequency": "high", "security_check_overdue": True},
                "assistance_template": {
                    "type": AssistanceType.WARNING,
                    "category": AssistanceCategory.SECURITY,
                    "urgency": UrgencyLevel.HIGH,
                    "title": "Security Check Recommended",
                    "recommendations": [
                        "Update passwords",
                        "Review access permissions",
                        "Enable two-factor authentication"
                    ]
                }
            },
            "workflow_suggestion": {
                "trigger_conditions": {"repetitive_actions": True, "time_waste_detected": True},
                "assistance_template": {
                    "type": AssistanceType.AUTOMATION,
                    "category": AssistanceCategory.WORKFLOW,
                    "urgency": UrgencyLevel.MEDIUM,
                    "title": "Workflow Automation Opportunity",
                    "recommendations": [
                        "Create automated workflow",
                        "Use batch operations",
                        "Set up recurring tasks"
                    ]
                }
            }
        }
        
        for pattern_id, pattern_data in patterns.items():
            self.assistance_patterns[pattern_id] = AssistancePattern(
                pattern_id=pattern_id,
                trigger_conditions=pattern_data["trigger_conditions"],
                assistance_template=pattern_data["assistance_template"]
            )
        
        logger.info(f"[PROACTIVE] Initialized {len(patterns)} assistance patterns")
    
    def _initialize_user_context(self):
        """Initialize user context with defaults"""
        self.user_context = UserContext(
            skill_level="intermediate",
            preferences={
                "assistance_frequency": "medium",
                "detail_level": "moderate",
                "automation_preference": "suggested"
            },
            common_workflows=["data_analysis", "report_generation", "system_monitoring"],
            time_patterns={
                "most_active_hours": [9, 10, 11, 14, 15, 16],
                "break_patterns": [12, 17],
                "productivity_peak": 10
            }
        )
        
        logger.info("[PROACTIVE] User context initialized")
    
    def _analyze_immediate_assistance_opportunities(self, action: str, context: Dict[str, Any]):
        """Analyze for immediate assistance opportunities"""
        try:
            # Check for repetitive actions
            if self.user_context.recent_actions.count(action) >= 3:
                self._suggest_automation_for_repetitive_action(action)
            
            # Check for error patterns
            if "error" in action.lower() or "failed" in action.lower():
                self._suggest_error_resolution(action, context)
            
            # Check for performance issues
            if context and context.get("response_time", 0) > 2000:  # milliseconds
                self._suggest_performance_optimization(context)
            
        except Exception as e:
            logger.error(f"[PROACTIVE] Error analyzing immediate opportunities: {e}")
    
    def _suggest_automation_for_repetitive_action(self, action: str):
        """Suggest automation for repetitive actions"""
        assistance = ProactiveAssistance(
            assistance_id=f"auto_{uuid.uuid4().hex[:8]}",
            assistance_type=AssistanceType.AUTOMATION,
            category=AssistanceCategory.WORKFLOW,
            urgency=UrgencyLevel.MEDIUM,
            title="Automation Opportunity Detected",
            description=f"You've performed '{action}' multiple times. Consider automating this task.",
            recommendations=[
                "Create automated workflow",
                "Use batch processing",
                "Set up recurring schedule"
            ],
            confidence=0.8,
            context={"action": action, "frequency": self.user_context.recent_actions.count(action)}
        )
        
        self.active_assistance.append(assistance)
    
    def _suggest_error_resolution(self, action: str, context: Dict[str, Any]):
        """Suggest error resolution assistance"""
        assistance = ProactiveAssistance(
            assistance_id=f"error_{uuid.uuid4().hex[:8]}",
            assistance_type=AssistanceType.WARNING,
            category=AssistanceCategory.MAINTENANCE,
            urgency=UrgencyLevel.HIGH,
            title="Error Resolution Assistance",
            description=f"Error detected in '{action}'. Here's how to resolve it.",
            recommendations=[
                "Check system logs",
                "Verify configuration",
                "Restart affected services"
            ],
            confidence=0.7,
            context={"action": action, "error_context": context}
        )
        
        self.active_assistance.append(assistance)
    
    def _suggest_performance_optimization(self, context: Dict[str, Any]):
        """Suggest performance optimization"""
        assistance = ProactiveAssistance(
            assistance_id=f"perf_{uuid.uuid4().hex[:8]}",
            assistance_type=AssistanceType.OPTIMIZATION,
            category=AssistanceCategory.PERFORMANCE,
            urgency=UrgencyLevel.MEDIUM,
            title="Performance Improvement Available",
            description="Slow response time detected. Consider these optimizations.",
            recommendations=[
                "Clear browser cache",
                "Optimize database queries",
                "Check network connectivity"
            ],
            confidence=0.75,
            context=context
        )
        
        self.active_assistance.append(assistance)
    
    def _get_current_context(self) -> Dict[str, Any]:
        """Get current user context"""
        return {
            "current_task": self.user_context.current_task,
            "recent_actions": self.user_context.recent_actions[-5:],
            "skill_level": self.user_context.skill_level,
            "time_of_day": self._get_time_of_day(datetime.now()),
            "session_duration": (datetime.now() - self.user_context.last_active).total_seconds()
        }
    
    def _matches_pattern(self, context: Dict[str, Any], pattern: AssistancePattern) -> bool:
        """Check if context matches assistance pattern"""
        try:
            conditions = pattern.trigger_conditions
            
            # Simple pattern matching (can be enhanced)
            for condition, expected_value in conditions.items():
                if condition in context:
                    if isinstance(expected_value, bool):
                        if bool(context[condition]) != expected_value:
                            return False
                    elif context[condition] != expected_value:
                        return False
                else:
                    # Some conditions might not be present
                    if expected_value:  # Only fail if we expected a truthy value
                        return False
            
            return True
            
        except Exception as e:
            logger.error(f"[PROACTIVE] Error matching pattern: {e}")
            return False
    
    def _create_assistance_from_pattern(self, pattern: AssistancePattern, 
                                      context: Dict[str, Any]) -> Optional[ProactiveAssistance]:
        """Create assistance item from pattern"""
        try:
            template = pattern.assistance_template
            
            assistance = ProactiveAssistance(
                assistance_id=f"pattern_{uuid.uuid4().hex[:8]}",
                assistance_type=template["type"],
                category=template["category"],
                urgency=template["urgency"],
                title=template["title"],
                description=template.get("description", template["title"]),
                recommendations=template["recommendations"],
                confidence=min(0.9, 0.6 + pattern.success_rate * 0.3),
                context=context
            )
            
            return assistance
            
        except Exception as e:
            logger.error(f"[PROACTIVE] Error creating assistance from pattern: {e}")
            return None
    
    def _analyze_help_query(self, query: str) -> str:
        """Analyze help query to determine type"""
        query_lower = query.lower()
        
        if "how to" in query_lower or "tutorial" in query_lower:
            return "tutorial"
        elif "error" in query_lower or "problem" in query_lower:
            return "troubleshooting"
        elif "optimize" in query_lower or "improve" in query_lower:
            return "optimization"
        elif "automate" in query_lower or "workflow" in query_lower:
            return "automation"
        else:
            return "general"
    
    def _generate_contextual_response(self, query: str, help_type: str, 
                                    context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate contextual response for help query"""
        responses = {
            "tutorial": {
                "description": f"Step-by-step guide for: {query}",
                "recommendations": [
                    "Follow the guided tutorial",
                    "Practice with sample data",
                    "Check documentation for details"
                ],
                "confidence": 0.8,
                "related_topics": ["getting_started", "best_practices"]
            },
            "troubleshooting": {
                "description": f"Troubleshooting steps for: {query}",
                "recommendations": [
                    "Check system status",
                    "Review error logs",
                    "Verify configuration"
                ],
                "confidence": 0.7,
                "related_topics": ["common_issues", "error_codes"]
            },
            "optimization": {
                "description": f"Optimization suggestions for: {query}",
                "recommendations": [
                    "Analyze current performance",
                    "Identify bottlenecks",
                    "Apply targeted improvements"
                ],
                "confidence": 0.75,
                "related_topics": ["performance_tuning", "best_practices"]
            },
            "general": {
                "description": f"Information about: {query}",
                "recommendations": [
                    "Explore related features",
                    "Check documentation",
                    "Try interactive examples"
                ],
                "confidence": 0.6,
                "related_topics": ["overview", "advanced_features"]
            }
        }
        
        return responses.get(help_type, responses["general"])
    
    def _analyze_workflow(self, workflow_name: str) -> Dict[str, Any]:
        """Analyze workflow for optimization opportunities"""
        return {
            "workflow_name": workflow_name,
            "frequency": "daily",
            "average_duration": 15,  # minutes
            "complexity": "medium",
            "automation_potential": 0.7,
            "bottlenecks": ["manual_data_entry", "report_formatting"],
            "optimization_score": 75.0
        }
    
    def _generate_workflow_optimizations(self, workflow_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Generate workflow optimization suggestions"""
        return {
            "suggestions": [
                "Automate data entry with templates",
                "Use batch processing for similar tasks",
                "Create reusable report templates"
            ],
            "confidence": 0.8,
            "time_savings": 10,  # minutes
            "difficulty": "easy",
            "priority": "high"
        }
    
    def _predict_from_history(self, time_context: Dict[str, Any], 
                            time_horizon: int) -> List[Dict[str, Any]]:
        """Predict user needs from historical patterns"""
        predictions = []
        
        # Simple time-based predictions
        hour = time_context["hour"]
        
        if 9 <= hour <= 11:  # Morning productivity
            predictions.append({
                "need": "data_analysis_tools",
                "confidence": 0.7,
                "reasoning": "Historical pattern shows data analysis in morning",
                "time_to_need": 30
            })
        
        if hour == 12:  # Lunch break
            predictions.append({
                "need": "break_reminder",
                "confidence": 0.9,
                "reasoning": "Consistent lunch break pattern",
                "time_to_need": 0
            })
        
        return predictions
    
    def _predict_from_context(self, user_context: UserContext, 
                            time_horizon: int) -> List[Dict[str, Any]]:
        """Predict user needs from current context"""
        predictions = []
        
        # Predict based on recent actions
        if "analyze" in " ".join(user_context.recent_actions):
            predictions.append({
                "need": "visualization_tools",
                "confidence": 0.6,
                "reasoning": "Recent analysis activities suggest need for visualization",
                "time_to_need": 15
            })
        
        return predictions
    
    def _get_time_of_day(self, dt: datetime) -> str:
        """Get time of day category"""
        hour = dt.hour
        if 6 <= hour < 12:
            return "morning"
        elif 12 <= hour < 17:
            return "afternoon"
        elif 17 <= hour < 21:
            return "evening"
        else:
            return "night"
    
    def _update_pattern_effectiveness(self, assistance: ProactiveAssistance, score: float):
        """Update pattern effectiveness based on user feedback"""
        try:
            # Find pattern that generated this assistance
            for pattern in self.assistance_patterns.values():
                if (pattern.assistance_template.get("type") == assistance.assistance_type and
                    pattern.assistance_template.get("category") == assistance.category):
                    
                    # Update success rate
                    old_rate = pattern.success_rate
                    new_rate = (old_rate * pattern.usage_count + score) / (pattern.usage_count + 1)
                    pattern.success_rate = new_rate
                    pattern.usage_count += 1
                    break
            
        except Exception as e:
            logger.error(f"[PROACTIVE] Error updating pattern effectiveness: {e}")
    
    def _learn_from_user_action(self, assistance: ProactiveAssistance, 
                              action: str, satisfaction: Optional[float]):
        """Learn from user action on assistance"""
        try:
            # Record action patterns
            action_key = f"{assistance.assistance_type.value}_{action}"
            if action_key not in self.assistance_effectiveness:
                self.assistance_effectiveness[action_key] = []
            
            if satisfaction is not None:
                self.assistance_effectiveness[action_key].append(satisfaction)
            
            # Learn context triggers
            if satisfaction and satisfaction > 0.7:  # Positive feedback
                for key, value in assistance.context.items():
                    self.context_triggers[key].append(assistance.assistance_type.value)
            
        except Exception as e:
            logger.error(f"[PROACTIVE] Error learning from user action: {e}")
    
    def _check_urgent_assistance_needs(self):
        """Check for urgent assistance needs"""
        try:
            # Check for critical system issues
            current_context = self._get_current_context()
            
            # Example: Check if user has been inactive for too long during work hours
            if (self._get_time_of_day(datetime.now()) in ["morning", "afternoon"] and
                current_context.get("session_duration", 0) > 1800):  # 30 minutes
                
                assistance = ProactiveAssistance(
                    assistance_id=f"urgent_{uuid.uuid4().hex[:8]}",
                    assistance_type=AssistanceType.SUGGESTION,
                    category=AssistanceCategory.PRODUCTIVITY,
                    urgency=UrgencyLevel.MEDIUM,
                    title="Extended Inactivity Detected",
                    description="You've been inactive for a while. Consider taking a break or checking if you need assistance.",
                    recommendations=[
                        "Take a short break",
                        "Review current tasks",
                        "Check for system issues"
                    ],
                    confidence=0.6,
                    context=current_context
                )
                
                self.active_assistance.append(assistance)
            
        except Exception as e:
            logger.error(f"[PROACTIVE] Error checking urgent assistance: {e}")
    
    def _cleanup_old_assistance(self):
        """Clean up old assistance items"""
        try:
            current_time = datetime.now()
            cooldown_period = timedelta(seconds=self.config["assistance_cooldown"])
            
            # Remove old assistance items
            self.active_assistance = [
                a for a in self.active_assistance
                if current_time - a.created_at < cooldown_period
            ]
            
        except Exception as e:
            logger.error(f"[PROACTIVE] Error cleaning up assistance: {e}")
    
    def _learn_behavioral_patterns(self):
        """Learn behavioral patterns from user interactions"""
        try:
            # Analyze interaction history
            if len(self.interaction_history) < 10:
                return
            
            # Simple pattern detection
            recent_interactions = list(self.interaction_history)[-50:]  # Last 50 interactions
            
            # Find common action sequences
            action_sequences = {}
            for i in range(len(recent_interactions) - 2):
                sequence = (
                    recent_interactions[i]["action"],
                    recent_interactions[i+1]["action"],
                    recent_interactions[i+2]["action"]
                )
                action_sequences[sequence] = action_sequences.get(sequence, 0) + 1
            
            # Store patterns with frequency > 2
            self.behavioral_patterns["action_sequences"] = {
                seq: count for seq, count in action_sequences.items() if count > 2
            }
            
        except Exception as e:
            logger.error(f"[PROACTIVE] Error learning behavioral patterns: {e}")
    
    def _update_assistance_patterns(self):
        """Update assistance patterns based on learning"""
        try:
            # Update pattern success rates based on effectiveness data
            for pattern_id, pattern in self.assistance_patterns.items():
                pattern_type = pattern.assistance_template.get("type")
                if pattern_type:
                    effectiveness_data = self.assistance_effectiveness.get(f"{pattern_type.value}_accepted", [])
                    if effectiveness_data:
                        pattern.success_rate = sum(effectiveness_data) / len(effectiveness_data)
            
        except Exception as e:
            logger.error(f"[PROACTIVE] Error updating assistance patterns: {e}")
    
    def _adapt_to_user_preferences(self):
        """Adapt assistance to user preferences"""
        try:
            # Adjust assistance frequency based on user responses
            dismissal_rate = len([a for a in self.assistance_history[-20:] 
                                if a.user_action_taken == "dismissed"]) / max(len(self.assistance_history[-20:]), 1)
            
            if dismissal_rate > 0.7:  # High dismissal rate
                self.config["confidence_threshold"] = min(0.9, self.config["confidence_threshold"] + 0.1)
            elif dismissal_rate < 0.3:  # Low dismissal rate
                self.config["confidence_threshold"] = max(0.4, self.config["confidence_threshold"] - 0.1)
            
        except Exception as e:
            logger.error(f"[PROACTIVE] Error adapting to preferences: {e}")
    
    def _update_effectiveness_metrics(self):
        """Update effectiveness metrics"""
        try:
            # Calculate overall assistance accuracy
            if self.assistance_history:
                scored_assistance = [a for a in self.assistance_history if a.effectiveness_score is not None]
                if scored_assistance:
                    self.metrics["assistance_accuracy"] = sum(a.effectiveness_score for a in scored_assistance) / len(scored_assistance)
                    self.metrics["user_satisfaction"] = self.metrics["assistance_accuracy"]
            
            # Calculate proactive success rate
            if self.assistance_history:
                successful_assistance = [a for a in self.assistance_history 
                                       if a.user_action_taken not in [None, "dismissed"]]
                self.metrics["proactive_success_rate"] = len(successful_assistance) / len(self.assistance_history)
            
        except Exception as e:
            logger.error(f"[PROACTIVE] Error updating effectiveness metrics: {e}")
    
    def _monitor_activity_patterns(self):
        """Monitor user activity patterns"""
        try:
            current_time = datetime.now()
            
            # Update time patterns
            hour = current_time.hour
            if "hourly_activity" not in self.behavioral_patterns:
                self.behavioral_patterns["hourly_activity"] = defaultdict(int)
            
            self.behavioral_patterns["hourly_activity"][hour] += 1
            
        except Exception as e:
            logger.error(f"[PROACTIVE] Error monitoring activity patterns: {e}")
    
    def _update_time_patterns(self):
        """Update time-based patterns"""
        try:
            # Update user context time patterns based on activity
            if "hourly_activity" in self.behavioral_patterns:
                activity_data = self.behavioral_patterns["hourly_activity"]
                if activity_data:
                    # Find most active hours
                    sorted_hours = sorted(activity_data.items(), key=lambda x: x[1], reverse=True)
                    self.user_context.time_patterns["most_active_hours"] = [h for h, _ in sorted_hours[:6]]
            
        except Exception as e:
            logger.error(f"[PROACTIVE] Error updating time patterns: {e}")
    
    def _detect_workflow_changes(self):
        """Detect changes in user workflows"""
        try:
            # Simple workflow change detection
            if len(self.interaction_history) > 20:
                recent_actions = [i["action"] for i in list(self.interaction_history)[-20:]]
                action_variety = len(set(recent_actions))
                
                if action_variety > 15:  # High variety suggests workflow change
                    logger.info("[PROACTIVE] Workflow change detected - high action variety")
                    # Could trigger assistance for workflow optimization
            
        except Exception as e:
            logger.error(f"[PROACTIVE] Error detecting workflow changes: {e}")
    
    def _get_behavioral_insights(self) -> Dict[str, Any]:
        """Get behavioral insights summary"""
        return {
            "action_patterns": len(self.behavioral_patterns.get("action_sequences", {})),
            "activity_patterns": "active" if self.behavioral_patterns.get("hourly_activity") else "limited_data",
            "adaptation_level": self.config["confidence_threshold"],
            "learning_progress": len(self.assistance_patterns)
        }
    
    def _get_effectiveness_summary(self) -> Dict[str, Any]:
        """Get assistance effectiveness summary"""
        return {
            "total_assistance_provided": self.metrics["assistance_provided"],
            "user_engagement_rate": self.metrics["proactive_success_rate"],
            "average_satisfaction": self.metrics["user_satisfaction"],
            "assistance_accuracy": self.metrics["assistance_accuracy"],
            "patterns_success_rate": sum(p.success_rate for p in self.assistance_patterns.values()) / max(len(self.assistance_patterns), 1)
        }


def create_proactive_assistance_engine(node_id: str = "proactive_assistant") -> ProactiveAssistanceEngine:
    """Create and configure proactive assistance engine"""
    return ProactiveAssistanceEngine(node_id)


def create_assistance_item(assistance_type: AssistanceType, category: AssistanceCategory,
                          urgency: UrgencyLevel, title: str, description: str,
                          recommendations: List[str], confidence: float = 0.7,
                          **kwargs) -> ProactiveAssistance:
    """Create proactive assistance item"""
    return ProactiveAssistance(
        assistance_id=f"assist_{uuid.uuid4().hex[:8]}",
        assistance_type=assistance_type,
        category=category,
        urgency=urgency,
        title=title,
        description=description,
        recommendations=recommendations,
        confidence=confidence,
        context=kwargs
    )