"""
Professional Program Thought Tracker for Jarvis V0.19
Advanced thought tracking system that monitors how the program thinks and what it would do
Generates suggestions for GitHub Copilot without autonomous self-modification
"""

import json
import time
import sqlite3
import threading
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import logging
import structlog

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

@dataclass
class ThoughtProcess:
    """Single thought process with decision analysis"""
    timestamp: str
    component: str
    operation: str  # 'decision', 'analysis', 'pattern_recognition', 'problem_solving'
    context: Dict[str, Any]  # Input context that triggered the thought
    reasoning_steps: List[str]  # Step-by-step reasoning process
    decision_factors: Dict[str, float]  # Factors that influenced the decision
    outcome_prediction: Dict[str, Any]  # What the program thinks will happen
    confidence_level: float  # 0-100% confidence in the decision
    alternative_approaches: List[Dict[str, Any]]  # Other approaches considered
    learning_points: List[str]  # What can be learned from this thought process

@dataclass
class DecisionPattern:
    """Pattern analysis of repeated decision types"""
    pattern_id: str
    pattern_type: str  # 'optimization', 'error_handling', 'resource_management', etc.
    frequency: int
    success_rate: float
    common_factors: Dict[str, float]
    typical_outcomes: Dict[str, Any]
    improvement_opportunities: List[str]
    suggested_optimizations: List[str]

@dataclass
class IntelligentSuggestion:
    """AI-generated suggestion for GitHub Copilot consideration"""
    timestamp: str
    suggestion_id: str
    category: str  # 'performance', 'architecture', 'functionality', 'maintenance'
    priority: str  # 'low', 'medium', 'high', 'critical'
    title: str
    description: str
    rationale: str  # Why this suggestion was generated
    supporting_data: Dict[str, Any]  # Data that supports this suggestion
    implementation_approach: str  # How it could be implemented
    estimated_impact: Dict[str, float]  # Predicted impact scores
    risk_assessment: Dict[str, str]  # Potential risks and mitigations
    copilot_notes: str  # Specific notes for GitHub Copilot

@dataclass
class ThoughtSession:
    """Complete thought tracking session"""
    session_id: str
    start_time: str
    end_time: Optional[str]
    monitoring_objectives: List[str]
    thought_processes: List[ThoughtProcess]
    patterns_identified: List[DecisionPattern]
    suggestions_generated: List[IntelligentSuggestion]
    session_insights: Dict[str, Any]
    quality_metrics: Dict[str, float]

class ProgramThoughtTracker:
    """Professional program thought tracking system - observes and suggests, never modifies"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'thought_tracking')
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.data_dir / 'thought_tracking.db'
        self.logger = structlog.get_logger("thought_tracker")
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Current session
        self.current_session: Optional[ThoughtSession] = None
        
        # Pattern analysis cache
        self.pattern_cache: Dict[str, DecisionPattern] = {}
        self.suggestion_queue: List[IntelligentSuggestion] = []
        
        # Initialize database
        self._init_database()
        
        self.logger.info("Program Thought Tracker initialized", db_path=str(self.db_path))
    
    def _init_database(self):
        """Initialize thought tracking database"""
        with sqlite3.connect(self.db_path) as conn:
            # Thought processes table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS thought_processes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    component TEXT NOT NULL,
                    operation TEXT NOT NULL,
                    context TEXT NOT NULL,
                    reasoning_steps TEXT NOT NULL,
                    decision_factors TEXT NOT NULL,
                    outcome_prediction TEXT NOT NULL,
                    confidence_level REAL NOT NULL,
                    alternative_approaches TEXT NOT NULL,
                    learning_points TEXT NOT NULL
                )
            ''')
            
            # Decision patterns table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS decision_patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    pattern_id TEXT UNIQUE NOT NULL,
                    pattern_type TEXT NOT NULL,
                    frequency INTEGER NOT NULL,
                    success_rate REAL NOT NULL,
                    common_factors TEXT NOT NULL,
                    typical_outcomes TEXT NOT NULL,
                    improvement_opportunities TEXT NOT NULL,
                    suggested_optimizations TEXT NOT NULL,
                    last_updated TEXT NOT NULL
                )
            ''')
            
            # Intelligent suggestions table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS intelligent_suggestions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    suggestion_id TEXT UNIQUE NOT NULL,
                    category TEXT NOT NULL,
                    priority TEXT NOT NULL,
                    title TEXT NOT NULL,
                    description TEXT NOT NULL,
                    rationale TEXT NOT NULL,
                    supporting_data TEXT NOT NULL,
                    implementation_approach TEXT NOT NULL,
                    estimated_impact TEXT NOT NULL,
                    risk_assessment TEXT NOT NULL,
                    copilot_notes TEXT NOT NULL,
                    status TEXT DEFAULT 'pending'
                )
            ''')
            
            # Thought sessions table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS thought_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    monitoring_objectives TEXT NOT NULL,
                    thought_processes TEXT NOT NULL,
                    patterns_identified TEXT NOT NULL,
                    suggestions_generated TEXT NOT NULL,
                    session_insights TEXT NOT NULL,
                    quality_metrics TEXT NOT NULL
                )
            ''')
            
            # Create indices for performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_thoughts_timestamp ON thought_processes(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_patterns_type ON decision_patterns(pattern_type)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_suggestions_priority ON intelligent_suggestions(priority)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_sessions_id ON thought_sessions(session_id)')
    
    def start_thought_session(self, monitoring_objectives: List[str]) -> str:
        """Start new thought tracking session"""
        with self.lock:
            session_id = f"thought_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self.current_session = ThoughtSession(
                session_id=session_id,
                start_time=datetime.now().isoformat(),
                end_time=None,
                monitoring_objectives=monitoring_objectives,
                thought_processes=[],
                patterns_identified=[],
                suggestions_generated=[],
                session_insights={},
                quality_metrics={}
            )
            
            self.logger.info("Thought tracking session started", 
                           session_id=session_id, 
                           objectives=monitoring_objectives)
            
            return session_id
    
    def track_thought_process(self, thought: ThoughtProcess):
        """Track a single thought process with comprehensive analysis"""
        with self.lock:
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO thought_processes 
                    (timestamp, component, operation, context, reasoning_steps,
                     decision_factors, outcome_prediction, confidence_level,
                     alternative_approaches, learning_points)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    thought.timestamp, thought.component, thought.operation,
                    json.dumps(thought.context), json.dumps(thought.reasoning_steps),
                    json.dumps(thought.decision_factors), json.dumps(thought.outcome_prediction),
                    thought.confidence_level, json.dumps(thought.alternative_approaches),
                    json.dumps(thought.learning_points)
                ))
            
            # Add to current session
            if self.current_session:
                self.current_session.thought_processes.append(thought)
            
            # Analyze for patterns
            self._analyze_thought_patterns(thought)
            
            # Generate suggestions if patterns warrant it
            self._generate_intelligent_suggestions(thought)
            
            self.logger.info("Thought process tracked",
                           component=thought.component,
                           operation=thought.operation,
                           confidence=thought.confidence_level)
    
    def _analyze_thought_patterns(self, thought: ThoughtProcess):
        """Analyze thought for recurring patterns"""
        pattern_key = f"{thought.component}_{thought.operation}"
        
        # Check if we have this pattern
        if pattern_key in self.pattern_cache:
            pattern = self.pattern_cache[pattern_key]
            pattern.frequency += 1
            
            # Update success rate based on confidence
            pattern.success_rate = (pattern.success_rate + thought.confidence_level) / 2
            
            # Update common factors
            for factor, weight in thought.decision_factors.items():
                if factor in pattern.common_factors:
                    pattern.common_factors[factor] = (pattern.common_factors[factor] + weight) / 2
                else:
                    pattern.common_factors[factor] = weight
        else:
            # Create new pattern
            pattern = DecisionPattern(
                pattern_id=pattern_key,
                pattern_type=thought.operation,
                frequency=1,
                success_rate=thought.confidence_level,
                common_factors=thought.decision_factors.copy(),
                typical_outcomes=thought.outcome_prediction.copy(),
                improvement_opportunities=[],
                suggested_optimizations=[]
            )
            
            self.pattern_cache[pattern_key] = pattern
        
        # Analyze for improvement opportunities
        if pattern.frequency >= 5:  # Only analyze patterns we've seen multiple times
            self._identify_improvement_opportunities(pattern, thought)
        
        # Store updated pattern in database
        self._store_pattern(pattern)
    
    def _identify_improvement_opportunities(self, pattern: DecisionPattern, current_thought: ThoughtProcess):
        """Identify opportunities for improvement in decision patterns"""
        opportunities = []
        optimizations = []
        
        # Low confidence pattern
        if pattern.success_rate < 70:
            opportunities.append(f"Pattern '{pattern.pattern_id}' shows low confidence ({pattern.success_rate:.1f}%)")
            optimizations.append("Review decision factors and add more context validation")
        
        # High complexity pattern
        if len(current_thought.reasoning_steps) > 10:
            opportunities.append("Complex reasoning process detected - may benefit from simplification")
            optimizations.append("Break down complex decisions into smaller, more manageable steps")
        
        # Pattern with many alternatives considered
        if len(current_thought.alternative_approaches) > 5:
            opportunities.append("Many alternatives considered - decision framework could be optimized")
            optimizations.append("Implement decision scoring system to quickly identify best approaches")
        
        # Update pattern with new insights
        pattern.improvement_opportunities.extend(opportunities)
        pattern.suggested_optimizations.extend(optimizations)
        
        # Keep only recent opportunities (avoid duplicates)
        pattern.improvement_opportunities = list(set(pattern.improvement_opportunities))[-10:]
        pattern.suggested_optimizations = list(set(pattern.suggested_optimizations))[-10:]
    
    def _generate_intelligent_suggestions(self, thought: ThoughtProcess):
        """Generate intelligent suggestions for GitHub Copilot based on thought analysis"""
        suggestions = []
        
        # Enhanced suggestion generation with broader conditions for 100% efficiency
        
        # Performance optimization suggestions (broader conditions)
        if thought.confidence_level < 85 or 'optimization' in thought.operation.lower() or 'performance' in thought.operation.lower():
            suggestion = IntelligentSuggestion(
                timestamp=datetime.now().isoformat(),
                suggestion_id=f"perf_opt_{int(time.time())}_{thought.component}",
                category='performance',
                priority='high' if thought.confidence_level < 70 else 'medium',
                title=f"Performance Enhancement in {thought.component}",
                description=f"Component {thought.component} shows optimization potential (confidence: {thought.confidence_level:.1f}%)",
                rationale="Performance-related decisions with moderate confidence indicate optimization opportunities",
                supporting_data={
                    'confidence_level': thought.confidence_level,
                    'decision_factors': thought.decision_factors,
                    'alternatives_considered': len(thought.alternative_approaches),
                    'operation_type': thought.operation
                },
                implementation_approach="Review algorithm efficiency, implement caching, optimize data structures, add performance monitoring",
                estimated_impact={
                    'performance_improvement': min(30.0, (100 - thought.confidence_level) * 0.5),
                    'resource_efficiency': 20.0,
                    'user_experience': 15.0
                },
                risk_assessment={
                    'implementation_risk': 'low',
                    'performance_risk': 'minimal',
                    'stability_risk': 'low'
                },
                copilot_notes=f"Optimize {thought.component} decision logic - consider implementing {', '.join([alt['approach'] for alt in thought.alternative_approaches[:2]])}"
            )
            suggestions.append(suggestion)
        
        # Architecture improvement suggestions (enhanced conditions)
        if len(thought.reasoning_steps) > 5 or len(thought.alternative_approaches) > 3:
            complexity_score = len(thought.reasoning_steps) + len(thought.alternative_approaches)
            suggestion = IntelligentSuggestion(
                timestamp=datetime.now().isoformat(),
                suggestion_id=f"arch_improve_{int(time.time())}_{thought.component}",
                category='architecture',
                priority='medium' if complexity_score > 8 else 'low',
                title=f"Architecture Optimization in {thought.component}",
                description=f"Complex decision process ({len(thought.reasoning_steps)} steps, {len(thought.alternative_approaches)} alternatives) suggests architectural improvements",
                rationale="Complex decision processes can be simplified through better architectural patterns",
                supporting_data={
                    'reasoning_complexity': len(thought.reasoning_steps),
                    'alternatives_complexity': len(thought.alternative_approaches),
                    'confidence_level': thought.confidence_level,
                    'complexity_score': complexity_score
                },
                implementation_approach="Extract decision patterns, implement strategy pattern, create decision trees, add configuration-driven logic",
                estimated_impact={
                    'code_maintainability': 25.0,
                    'development_speed': 18.0,
                    'bug_reduction': 12.0,
                    'cognitive_load': -15.0
                },
                risk_assessment={
                    'implementation_risk': 'medium',
                    'performance_risk': 'minimal',
                    'stability_risk': 'low'
                },
                copilot_notes=f"Simplify {thought.component} architecture - the {len(thought.reasoning_steps)}-step decision process could benefit from pattern extraction"
            )
            suggestions.append(suggestion)
        
        # Decision quality improvement suggestions
        if thought.confidence_level > 85 and len(thought.decision_factors) > 3:
            suggestion = IntelligentSuggestion(
                timestamp=datetime.now().isoformat(),
                suggestion_id=f"decision_quality_{int(time.time())}_{thought.component}",
                category='functionality',
                priority='low',
                title=f"Decision Framework Enhancement in {thought.component}",
                description=f"High-quality decision making (confidence: {thought.confidence_level:.1f}%) could be systematized",
                rationale="Successful decision patterns should be captured and reused across the system",
                supporting_data={
                    'confidence_level': thought.confidence_level,
                    'decision_factors': thought.decision_factors,
                    'learning_points': thought.learning_points
                },
                implementation_approach="Create decision framework template, implement scoring system, add decision history tracking",
                estimated_impact={
                    'decision_consistency': 20.0,
                    'knowledge_transfer': 25.0,
                    'system_intelligence': 15.0
                },
                risk_assessment={
                    'implementation_risk': 'low',
                    'performance_risk': 'minimal',
                    'stability_risk': 'improvement'
                },
                copilot_notes=f"Excellent decision quality in {thought.component} - consider creating reusable decision framework"
            )
            suggestions.append(suggestion)
        
        # Context-aware suggestions
        if 'cache' in thought.operation.lower() or 'memory' in thought.component.lower():
            suggestion = IntelligentSuggestion(
                timestamp=datetime.now().isoformat(),
                suggestion_id=f"memory_opt_{int(time.time())}_{thought.component}",
                category='performance',
                priority='medium',
                title=f"Memory Management Enhancement in {thought.component}",
                description=f"Memory-related operations detected with room for optimization",
                rationale="Memory management decisions directly impact system performance and resource usage",
                supporting_data={
                    'operation': thought.operation,
                    'component': thought.component,
                    'context': thought.context
                },
                implementation_approach="Implement smart caching, add memory monitoring, optimize data structures, implement cleanup strategies",
                estimated_impact={
                    'memory_efficiency': 25.0,
                    'response_time': 20.0,
                    'resource_usage': -15.0
                },
                risk_assessment={
                    'implementation_risk': 'low',
                    'performance_risk': 'improvement',
                    'stability_risk': 'low'
                },
                copilot_notes=f"Optimize memory usage in {thought.component} - consider implementing advanced caching strategies"
            )
            suggestions.append(suggestion)
        
        # Error handling and reliability suggestions (enhanced detection)
        if ('error' in str(thought.context).lower() or 'exception' in str(thought.context).lower() or 
            thought.confidence_level < 75 or 'validation' in thought.operation.lower()):
            suggestion = IntelligentSuggestion(
                timestamp=datetime.now().isoformat(),
                suggestion_id=f"reliability_{int(time.time())}_{thought.component}",
                category='functionality',
                priority='high' if thought.confidence_level < 70 else 'medium',
                title=f"Reliability Enhancement in {thought.component}",
                description=f"Reliability concerns detected in decision making process",
                rationale="Low confidence or error-related decisions indicate need for better error handling and validation",
                supporting_data={
                    'confidence_level': thought.confidence_level,
                    'context': thought.context,
                    'alternatives': thought.alternative_approaches
                },
                implementation_approach="Add comprehensive error handling, implement validation layers, create fallback mechanisms, add monitoring",
                estimated_impact={
                    'system_stability': 30.0,
                    'user_experience': 25.0,
                    'debugging_efficiency': 20.0,
                    'error_recovery': 35.0
                },
                risk_assessment={
                    'implementation_risk': 'low',
                    'performance_risk': 'minimal',
                    'stability_risk': 'improvement'
                },
                copilot_notes=f"Enhance error handling in {thought.component} - implement robust validation and recovery mechanisms"
            )
            suggestions.append(suggestion)
        
        # Store suggestions
        for suggestion in suggestions:
            self._store_suggestion(suggestion)
            self.suggestion_queue.append(suggestion)
            
            if self.current_session:
                self.current_session.suggestions_generated.append(suggestion)
    
    def _store_pattern(self, pattern: DecisionPattern):
        """Store decision pattern in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO decision_patterns 
                (pattern_id, pattern_type, frequency, success_rate, common_factors,
                 typical_outcomes, improvement_opportunities, suggested_optimizations, last_updated)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                pattern.pattern_id, pattern.pattern_type, pattern.frequency,
                pattern.success_rate, json.dumps(pattern.common_factors),
                json.dumps(pattern.typical_outcomes), json.dumps(pattern.improvement_opportunities),
                json.dumps(pattern.suggested_optimizations), datetime.now().isoformat()
            ))
    
    def _store_suggestion(self, suggestion: IntelligentSuggestion):
        """Store intelligent suggestion in database"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO intelligent_suggestions 
                (timestamp, suggestion_id, category, priority, title, description,
                 rationale, supporting_data, implementation_approach, estimated_impact,
                 risk_assessment, copilot_notes, status)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                suggestion.timestamp, suggestion.suggestion_id, suggestion.category,
                suggestion.priority, suggestion.title, suggestion.description,
                suggestion.rationale, json.dumps(suggestion.supporting_data),
                suggestion.implementation_approach, json.dumps(suggestion.estimated_impact),
                json.dumps(suggestion.risk_assessment), suggestion.copilot_notes, 'pending'
            ))
    
    def get_pending_suggestions_for_copilot(self, priority_filter: str = None) -> List[IntelligentSuggestion]:
        """Get pending suggestions specifically formatted for GitHub Copilot"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT * FROM intelligent_suggestions 
                WHERE status = 'pending'
            '''
            params = []
            
            if priority_filter:
                query += ' AND priority = ?'
                params.append(priority_filter)
            
            query += ' ORDER BY timestamp DESC'
            
            cursor = conn.execute(query, params)
            rows = cursor.fetchall()
            
            suggestions = []
            for row in rows:
                suggestion = IntelligentSuggestion(
                    timestamp=row[1],
                    suggestion_id=row[2],
                    category=row[3],
                    priority=row[4],
                    title=row[5],
                    description=row[6],
                    rationale=row[7],
                    supporting_data=json.loads(row[8]),
                    implementation_approach=row[9],
                    estimated_impact=json.loads(row[10]),
                    risk_assessment=json.loads(row[11]),
                    copilot_notes=row[12]
                )
                suggestions.append(suggestion)
            
            return suggestions
    
    def end_thought_session(self) -> Dict[str, Any]:
        """End current thought tracking session with comprehensive analysis"""
        if not self.current_session:
            return {'error': 'No active session'}
        
        with self.lock:
            # Calculate session quality metrics
            total_thoughts = len(self.current_session.thought_processes)
            avg_confidence = sum(t.confidence_level for t in self.current_session.thought_processes) / total_thoughts if total_thoughts > 0 else 0
            
            complex_thoughts = sum(1 for t in self.current_session.thought_processes if len(t.reasoning_steps) > 5)
            patterns_found = len(self.current_session.patterns_identified)
            suggestions_made = len(self.current_session.suggestions_generated)
            
            # Update session
            self.current_session.end_time = datetime.now().isoformat()
            self.current_session.quality_metrics = {
                'total_thoughts_tracked': total_thoughts,
                'average_confidence': avg_confidence,
                'complex_thoughts_percentage': (complex_thoughts / total_thoughts * 100) if total_thoughts > 0 else 0,
                'patterns_identified': patterns_found,
                'suggestions_generated': suggestions_made,
                'suggestion_diversity': len(set(s.category for s in self.current_session.suggestions_generated))
            }
            
            # Generate session insights
            insights = self._generate_session_insights()
            self.current_session.session_insights = insights
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO thought_sessions 
                    (session_id, start_time, end_time, monitoring_objectives,
                     thought_processes, patterns_identified, suggestions_generated,
                     session_insights, quality_metrics)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.current_session.session_id,
                    self.current_session.start_time,
                    self.current_session.end_time,
                    json.dumps(self.current_session.monitoring_objectives),
                    json.dumps([asdict(t) for t in self.current_session.thought_processes]),
                    json.dumps([asdict(p) for p in self.current_session.patterns_identified]),
                    json.dumps([asdict(s) for s in self.current_session.suggestions_generated]),
                    json.dumps(self.current_session.session_insights),
                    json.dumps(self.current_session.quality_metrics)
                ))
            
            # Create summary
            summary = {
                'session_id': self.current_session.session_id,
                'duration_minutes': self._calculate_session_duration(),
                'quality_metrics': self.current_session.quality_metrics,
                'insights': insights,
                'copilot_recommendations': self._generate_copilot_summary()
            }
            
            self.logger.info("Thought tracking session completed",
                           session_id=self.current_session.session_id,
                           thoughts_tracked=total_thoughts,
                           suggestions_generated=suggestions_made)
            
            # Reset current session
            self.current_session = None
            
            return summary
    
    def _generate_session_insights(self) -> Dict[str, Any]:
        """Generate insights from the current session"""
        if not self.current_session:
            return {}
        
        thoughts = self.current_session.thought_processes
        
        # Component analysis
        component_usage = {}
        operation_patterns = {}
        
        for thought in thoughts:
            component_usage[thought.component] = component_usage.get(thought.component, 0) + 1
            operation_patterns[thought.operation] = operation_patterns.get(thought.operation, 0) + 1
        
        # Confidence trends
        confidence_by_component = {}
        for thought in thoughts:
            if thought.component not in confidence_by_component:
                confidence_by_component[thought.component] = []
            confidence_by_component[thought.component].append(thought.confidence_level)
        
        avg_confidence_by_component = {
            comp: sum(confs) / len(confs) 
            for comp, confs in confidence_by_component.items()
        }
        
        return {
            'most_active_components': sorted(component_usage.items(), key=lambda x: x[1], reverse=True)[:5],
            'common_operations': sorted(operation_patterns.items(), key=lambda x: x[1], reverse=True)[:5],
            'confidence_by_component': avg_confidence_by_component,
            'overall_thinking_quality': sum(t.confidence_level for t in thoughts) / len(thoughts) if thoughts else 0,
            'decision_complexity_average': sum(len(t.reasoning_steps) for t in thoughts) / len(thoughts) if thoughts else 0,
            'learning_opportunities': sum(len(t.learning_points) for t in thoughts)
        }
    
    def _generate_copilot_summary(self) -> Dict[str, Any]:
        """Generate summary specifically for GitHub Copilot"""
        if not self.current_session:
            return {}
        
        suggestions = self.current_session.suggestions_generated
        
        # Group by priority and category
        by_priority = {}
        by_category = {}
        
        for suggestion in suggestions:
            if suggestion.priority not in by_priority:
                by_priority[suggestion.priority] = []
            by_priority[suggestion.priority].append(suggestion)
            
            if suggestion.category not in by_category:
                by_category[suggestion.category] = []
            by_category[suggestion.category].append(suggestion)
        
        # Generate actionable summary
        return {
            'total_suggestions': len(suggestions),
            'by_priority': {priority: len(sug_list) for priority, sug_list in by_priority.items()},
            'by_category': {category: len(sug_list) for category, sug_list in by_category.items()},
            'high_priority_actions': [s.title for s in suggestions if s.priority == 'high'],
            'quick_wins': [s.title for s in suggestions if s.priority == 'low' and 'simplif' in s.title.lower()],
            'architectural_recommendations': [s.title for s in suggestions if s.category == 'architecture'],
            'copilot_focus_areas': list(set(s.category for s in suggestions))
        }
    
    def _calculate_session_duration(self) -> float:
        """Calculate session duration in minutes"""
        if not self.current_session or not self.current_session.end_time:
            return 0.0
        
        start = datetime.fromisoformat(self.current_session.start_time)
        end = datetime.fromisoformat(self.current_session.end_time)
        return (end - start).total_seconds() / 60

# Global instance for easy access
_thought_tracker = None

def get_thought_tracker() -> ProgramThoughtTracker:
    """Get global thought tracker instance"""
    global _thought_tracker
    if _thought_tracker is None:
        _thought_tracker = ProgramThoughtTracker()
    return _thought_tracker