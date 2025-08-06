"""
Professional Program Evolution Tracker for Jarvis V0.19
Advanced evolution tracking with comprehensive logging, metrics, and data validation
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
class EvolutionMetric:
    """Single evolution metric with validation"""
    timestamp: str
    metric_type: str  # 'functionality', 'performance', 'quality', 'coverage'
    component: str
    value: float
    baseline: float
    improvement: float
    validation_status: str  # 'validated', 'pending', 'failed'
    data_source: str
    notes: str = ""

@dataclass
class FunctionalityUpdate:
    """Tracks functionality changes and validation"""
    timestamp: str
    feature_name: str
    version_from: str
    version_to: str
    update_type: str  # 'enhancement', 'new_feature', 'bug_fix', 'optimization'
    test_results: Dict[str, Any]
    performance_impact: Dict[str, float]
    validation_methods: List[str]
    rollback_plan: str
    success_criteria: Dict[str, float]
    actual_results: Dict[str, float]

@dataclass
class EvolutionSession:
    """Complete evolution session tracking"""
    session_id: str
    start_time: str
    end_time: Optional[str]
    objectives: List[str]
    completed_tasks: List[Dict[str, Any]]
    metrics_achieved: List[EvolutionMetric]
    functional_updates: List[FunctionalityUpdate]
    overall_success_rate: float
    next_priorities: List[str]

class ProgramEvolutionTracker:
    """Professional program evolution tracking system"""
    
    def __init__(self, data_dir: str = None):
        if data_dir is None:
            data_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'evolution')
        
        self.data_dir = Path(data_dir)
        self.data_dir.mkdir(parents=True, exist_ok=True)
        
        self.db_path = self.data_dir / 'evolution_tracking.db'
        self.logger = structlog.get_logger("evolution_tracker")
        
        # Thread safety
        self.lock = threading.Lock()
        
        # Current session
        self.current_session: Optional[EvolutionSession] = None
        
        # Initialize database
        self._init_database()
        
        self.logger.info("Evolution tracker initialized", db_path=str(self.db_path))
    
    def _init_database(self):
        """Initialize evolution tracking database"""
        with sqlite3.connect(self.db_path) as conn:
            # Evolution metrics table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS evolution_metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    metric_type TEXT NOT NULL,
                    component TEXT NOT NULL,
                    value REAL NOT NULL,
                    baseline REAL NOT NULL,
                    improvement REAL NOT NULL,
                    validation_status TEXT NOT NULL,
                    data_source TEXT NOT NULL,
                    notes TEXT
                )
            ''')
            
            # Functionality updates table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS functionality_updates (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp TEXT NOT NULL,
                    feature_name TEXT NOT NULL,
                    version_from TEXT NOT NULL,
                    version_to TEXT NOT NULL,
                    update_type TEXT NOT NULL,
                    test_results TEXT NOT NULL,
                    performance_impact TEXT NOT NULL,
                    validation_methods TEXT NOT NULL,
                    rollback_plan TEXT NOT NULL,
                    success_criteria TEXT NOT NULL,
                    actual_results TEXT NOT NULL
                )
            ''')
            
            # Evolution sessions table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS evolution_sessions (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    session_id TEXT UNIQUE NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT,
                    objectives TEXT NOT NULL,
                    completed_tasks TEXT NOT NULL,
                    metrics_achieved TEXT NOT NULL,
                    functional_updates TEXT NOT NULL,
                    overall_success_rate REAL NOT NULL,
                    next_priorities TEXT NOT NULL
                )
            ''')
            
            # Create indices for performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON evolution_metrics(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_updates_timestamp ON functionality_updates(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_sessions_id ON evolution_sessions(session_id)')
    
    def start_evolution_session(self, objectives: List[str]) -> str:
        """Start new evolution tracking session"""
        with self.lock:
            session_id = f"evolution_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
            
            self.current_session = EvolutionSession(
                session_id=session_id,
                start_time=datetime.now().isoformat(),
                end_time=None,
                objectives=objectives,
                completed_tasks=[],
                metrics_achieved=[],
                functional_updates=[],
                overall_success_rate=0.0,
                next_priorities=[]
            )
            
            self.logger.info("Evolution session started", 
                           session_id=session_id, 
                           objectives=objectives)
            
            return session_id
    
    def log_evolution_metric(self, metric: EvolutionMetric):
        """Log evolution metric with validation"""
        with self.lock:
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO evolution_metrics 
                    (timestamp, metric_type, component, value, baseline, improvement, 
                     validation_status, data_source, notes)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    metric.timestamp, metric.metric_type, metric.component,
                    metric.value, metric.baseline, metric.improvement,
                    metric.validation_status, metric.data_source, metric.notes
                ))
            
            # Add to current session
            if self.current_session:
                self.current_session.metrics_achieved.append(metric)
            
            self.logger.info("Evolution metric logged",
                           metric_type=metric.metric_type,
                           component=metric.component,
                           improvement=metric.improvement,
                           validation_status=metric.validation_status)
    
    def log_functionality_update(self, update: FunctionalityUpdate):
        """Log functionality update with comprehensive tracking"""
        with self.lock:
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT INTO functionality_updates 
                    (timestamp, feature_name, version_from, version_to, update_type,
                     test_results, performance_impact, validation_methods,
                     rollback_plan, success_criteria, actual_results)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    update.timestamp, update.feature_name, update.version_from,
                    update.version_to, update.update_type,
                    json.dumps(update.test_results),
                    json.dumps(update.performance_impact),
                    json.dumps(update.validation_methods),
                    update.rollback_plan,
                    json.dumps(update.success_criteria),
                    json.dumps(update.actual_results)
                ))
            
            # Add to current session
            if self.current_session:
                self.current_session.functional_updates.append(update)
            
            self.logger.info("Functionality update logged",
                           feature_name=update.feature_name,
                           update_type=update.update_type,
                           version_from=update.version_from,
                           version_to=update.version_to)
    
    def complete_task(self, task_name: str, result: Dict[str, Any]):
        """Mark task as completed with results"""
        if self.current_session:
            task_completion = {
                'task_name': task_name,
                'completion_time': datetime.now().isoformat(),
                'result': result,
                'success': result.get('success', False)
            }
            
            self.current_session.completed_tasks.append(task_completion)
            
            self.logger.info("Task completed",
                           task_name=task_name,
                           success=result.get('success', False))
    
    def end_evolution_session(self, next_priorities: List[str]) -> Dict[str, Any]:
        """End current evolution session with summary"""
        if not self.current_session:
            return {'error': 'No active session'}
        
        with self.lock:
            # Calculate success rate
            successful_tasks = sum(1 for task in self.current_session.completed_tasks 
                                 if task.get('result', {}).get('success', False))
            total_tasks = len(self.current_session.completed_tasks)
            success_rate = (successful_tasks / total_tasks * 100) if total_tasks > 0 else 0
            
            # Update session
            self.current_session.end_time = datetime.now().isoformat()
            self.current_session.overall_success_rate = success_rate
            self.current_session.next_priorities = next_priorities
            
            # Store in database
            with sqlite3.connect(self.db_path) as conn:
                conn.execute('''
                    INSERT OR REPLACE INTO evolution_sessions 
                    (session_id, start_time, end_time, objectives, completed_tasks,
                     metrics_achieved, functional_updates, overall_success_rate, next_priorities)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    self.current_session.session_id,
                    self.current_session.start_time,
                    self.current_session.end_time,
                    json.dumps(self.current_session.objectives),
                    json.dumps([asdict(task) for task in self.current_session.completed_tasks]),
                    json.dumps([asdict(metric) for metric in self.current_session.metrics_achieved]),
                    json.dumps([asdict(update) for update in self.current_session.functional_updates]),
                    self.current_session.overall_success_rate,
                    json.dumps(self.current_session.next_priorities)
                ))
            
            # Create session summary
            summary = {
                'session_id': self.current_session.session_id,
                'duration_minutes': self._calculate_session_duration(),
                'objectives_completed': len(self.current_session.completed_tasks),
                'success_rate': success_rate,
                'metrics_improved': len([m for m in self.current_session.metrics_achieved 
                                       if m.improvement > 0]),
                'functional_updates': len(self.current_session.functional_updates),
                'next_priorities': next_priorities
            }
            
            self.logger.info("Evolution session completed",
                           session_id=self.current_session.session_id,
                           success_rate=success_rate,
                           objectives_completed=len(self.current_session.completed_tasks))
            
            # Reset current session
            self.current_session = None
            
            return summary
    
    def _calculate_session_duration(self) -> float:
        """Calculate session duration in minutes"""
        if not self.current_session or not self.current_session.end_time:
            return 0.0
        
        start = datetime.fromisoformat(self.current_session.start_time)
        end = datetime.fromisoformat(self.current_session.end_time)
        return (end - start).total_seconds() / 60
    
    def get_evolution_report(self, days: int = 7) -> Dict[str, Any]:
        """Generate comprehensive evolution report"""
        cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            # Get recent metrics
            metrics_cursor = conn.execute('''
                SELECT * FROM evolution_metrics 
                WHERE timestamp > ? 
                ORDER BY timestamp DESC
            ''', (cutoff_date,))
            
            metrics = metrics_cursor.fetchall()
            
            # Get recent functionality updates
            updates_cursor = conn.execute('''
                SELECT * FROM functionality_updates 
                WHERE timestamp > ? 
                ORDER BY timestamp DESC
            ''', (cutoff_date,))
            
            updates = updates_cursor.fetchall()
            
            # Get recent sessions
            sessions_cursor = conn.execute('''
                SELECT * FROM evolution_sessions 
                WHERE start_time > ? 
                ORDER BY start_time DESC
            ''', (cutoff_date,))
            
            sessions = sessions_cursor.fetchall()
        
        # Calculate summary statistics
        total_improvements = sum(1 for metric in metrics if metric[6] > 0)  # improvement > 0
        avg_success_rate = sum(session[8] for session in sessions) / len(sessions) if sessions else 0
        
        return {
            'report_generated': datetime.now().isoformat(),
            'period_days': days,
            'summary': {
                'total_metrics_tracked': len(metrics),
                'total_improvements': total_improvements,
                'total_functionality_updates': len(updates),
                'total_sessions': len(sessions),
                'average_success_rate': avg_success_rate
            },
            'recent_metrics': metrics[:10],  # Last 10 metrics
            'recent_updates': updates[:5],   # Last 5 updates
            'recent_sessions': sessions[:3]  # Last 3 sessions
        }

    def validate_functional_data(self) -> Dict[str, Any]:
        """Validate all functional data integrity"""
        validation_results = {
            'timestamp': datetime.now().isoformat(),
            'database_integrity': True,
            'data_consistency': True,
            'performance_metrics': {},
            'issues_found': [],
            'recommendations': []
        }
        
        try:
            with sqlite3.connect(self.db_path) as conn:
                # Check database integrity
                integrity_check = conn.execute('PRAGMA integrity_check').fetchone()
                if integrity_check[0] != 'ok':
                    validation_results['database_integrity'] = False
                    validation_results['issues_found'].append(f"Database integrity issue: {integrity_check[0]}")
                
                # Check for orphaned records or inconsistencies
                metrics_count = conn.execute('SELECT COUNT(*) FROM evolution_metrics').fetchone()[0]
                updates_count = conn.execute('SELECT COUNT(*) FROM functionality_updates').fetchone()[0]
                sessions_count = conn.execute('SELECT COUNT(*) FROM evolution_sessions').fetchone()[0]
                
                validation_results['performance_metrics'] = {
                    'total_metrics': metrics_count,
                    'total_updates': updates_count,
                    'total_sessions': sessions_count,
                    'database_size_mb': os.path.getsize(self.db_path) / (1024 * 1024)
                }
                
                # Data consistency checks
                recent_metrics = conn.execute('''
                    SELECT COUNT(*) FROM evolution_metrics 
                    WHERE validation_status = 'validated'
                ''').fetchone()[0]
                
                if metrics_count > 0:
                    validation_rate = (recent_metrics / metrics_count) * 100
                    if validation_rate < 80:
                        validation_results['issues_found'].append(
                            f"Low validation rate: {validation_rate:.1f}% (target: 80%+)"
                        )
                        validation_results['recommendations'].append(
                            "Increase validation frequency for evolution metrics"
                        )
                
        except Exception as e:
            validation_results['database_integrity'] = False
            validation_results['issues_found'].append(f"Database error: {str(e)}")
            self.logger.error("Functional data validation failed", error=str(e))
        
        return validation_results

# Global instance for easy access
_evolution_tracker = None

def get_evolution_tracker() -> ProgramEvolutionTracker:
    """Get global evolution tracker instance"""
    global _evolution_tracker
    if _evolution_tracker is None:
        _evolution_tracker = ProgramEvolutionTracker()
    return _evolution_tracker