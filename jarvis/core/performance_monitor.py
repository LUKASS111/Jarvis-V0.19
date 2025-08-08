"""
Performance Monitoring and Predictive Analytics for Jarvis-1.0.0
Real-time performance dashboards with comprehensive metrics collection
"""

import time
import threading
import json
import os
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, asdict
import statistics
from collections import defaultdict, deque

@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    timestamp: str
    metric_name: str
    value: float
    category: str
    tags: Dict[str, str]
    source: str

@dataclass
class SystemPerformanceReport:
    """Comprehensive system performance report"""
    timestamp: str
    overall_health_score: float
    system_metrics: Dict[str, float]
    component_metrics: Dict[str, Dict[str, float]]
    alerts: List[Dict[str, Any]]
    predictions: Dict[str, float]
    recommendations: List[str]

class PerformanceMonitor:
    """Enhanced performance monitoring with predictive analytics"""
    
    def __init__(self, data_retention_hours: int = 24):
        self.data_retention_hours = data_retention_hours
        self.metrics = defaultdict(lambda: deque(maxlen=1000))
        self.is_running = False
        self.monitor_thread = None
        self.alert_rules = {}
        self.baseline_metrics = {}
        self.predictive_models = {}
        
        # Performance thresholds
        self.thresholds = {
            'verification_queue_size': {'warning': 1000, 'critical': 5000},
            'agent_compliance_rate': {'warning': 0.7, 'critical': 0.5},
            'archive_operations_per_sec': {'warning': 1.0, 'critical': 0.5},
            'system_health_score': {'warning': 80, 'critical': 60},
            'verification_throughput': {'warning': 10, 'critical': 5},
            'memory_usage_percent': {'warning': 80, 'critical': 90},
            'cpu_usage_percent': {'warning': 75, 'critical': 85}
        }
        
        # Initialize baseline
        self._initialize_baseline()
    
    def start_monitoring(self):
        """Start performance monitoring"""
        if self.is_running:
            return
        
        self.is_running = True
        self.monitor_thread = threading.Thread(target=self._monitor_loop, daemon=True)
        self.monitor_thread.start()
        print("[MONITOR] Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.is_running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=5)
        print("[MONITOR] Performance monitoring stopped")
    
    def record_metric(self, name: str, value: float, category: str = 'general', 
                     tags: Dict[str, str] = None, source: str = 'system'):
        """Record a performance metric"""
        metric = PerformanceMetric(
            timestamp=datetime.now().isoformat(),
            metric_name=name,
            value=value,
            category=category,
            tags=tags or {},
            source=source
        )
        
        self.metrics[name].append(metric)
        
        # Check for alerts
        self._check_alerts(name, value)
    
    def get_current_metrics(self) -> Dict[str, float]:
        """Get current values for all metrics"""
        current_metrics = {}
        
        for metric_name, metric_queue in self.metrics.items():
            if metric_queue:
                current_metrics[metric_name] = metric_queue[-1].value
        
        return current_metrics
    
    def get_metric_history(self, metric_name: str, hours: int = 1) -> List[PerformanceMetric]:
        """Get historical data for a specific metric"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        if metric_name not in self.metrics:
            return []
        
        return [
            metric for metric in self.metrics[metric_name]
            if datetime.fromisoformat(metric.timestamp) >= cutoff_time
        ]
    
    def calculate_trend(self, metric_name: str, hours: int = 1) -> float:
        """Calculate trend for a metric (positive = improving, negative = declining)"""
        history = self.get_metric_history(metric_name, hours)
        
        if len(history) < 2:
            return 0.0
        
        values = [metric.value for metric in history]
        times = [datetime.fromisoformat(metric.timestamp) for metric in history]
        
        # Simple linear regression for trend
        n = len(values)
        time_deltas = [(t - times[0]).total_seconds() for t in times]
        
        # Calculate slope
        sum_xy = sum(t * v for t, v in zip(time_deltas, values))
        sum_x = sum(time_deltas)
        sum_y = sum(values)
        sum_x2 = sum(t * t for t in time_deltas)
        
        if n * sum_x2 - sum_x * sum_x == 0:
            return 0.0
        
        slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
        return slope
    
    def generate_system_report(self) -> SystemPerformanceReport:
        """Generate comprehensive system performance report"""
        current_metrics = self.get_current_metrics()
        component_metrics = self._collect_component_metrics()
        alerts = self._get_active_alerts()
        predictions = self._generate_predictions()
        recommendations = self._generate_recommendations()
        
        # Calculate overall health score
        health_score = self._calculate_health_score(current_metrics, component_metrics)
        
        return SystemPerformanceReport(
            timestamp=datetime.now().isoformat(),
            overall_health_score=health_score,
            system_metrics=current_metrics,
            component_metrics=component_metrics,
            alerts=alerts,
            predictions=predictions,
            recommendations=recommendations
        )
    
    def _monitor_loop(self):
        """Main monitoring loop"""
        while self.is_running:
            try:
                # Collect system metrics
                self._collect_system_metrics()
                
                # Update baseline periodically
                if self._should_update_baseline():
                    self._update_baseline()
                
                # Clean old data
                self._cleanup_current_data()
                
                # Sleep interval
                time.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                print(f"[ERROR] Monitor loop error: {e}")
                time.sleep(10)
    
    def _collect_system_metrics(self):
        """Collect system-level performance metrics"""
        try:
            # Import here to avoid circular dependencies
            from .data_archiver import get_archiver
            from .verification_optimizer import VerificationOptimizer
            from .agent_workflow import AgentWorkflowManager
            
            # Archive system metrics
            archiver = get_archiver()
            archive_stats = archiver.get_stats()
            
            self.record_metric('archive_total_entries', archive_stats.get('total_entries', 0), 'archive')
            self.record_metric('archive_pending_verification', archive_stats.get('pending_verification', 0), 'archive')
            
            # Calculate archive operations per second
            recent_entries = self.get_metric_history('archive_total_entries', hours=0.1)  # 6 minutes
            if len(recent_entries) >= 2:
                ops_per_sec = self._calculate_operations_per_second(recent_entries)
                self.record_metric('archive_operations_per_sec', ops_per_sec, 'performance')
            
            # System health metrics
            health_data = self._get_system_health_data()
            for metric_name, value in health_data.items():
                self.record_metric(metric_name, value, 'health')
            
            # CRDT metrics
            crdt_stats = self._get_crdt_metrics()
            for metric_name, value in crdt_stats.items():
                self.record_metric(metric_name, value, 'crdt')
                
        except Exception as e:
            print(f"[ERROR] Failed to collect system metrics: {e}")
    
    def _collect_component_metrics(self) -> Dict[str, Dict[str, float]]:
        """Collect metrics for individual components"""
        components = {}
        
        try:
            # Verification system
            components['verification'] = {
                'queue_size': self.get_current_metrics().get('archive_pending_verification', 0),
                'throughput': self.get_current_metrics().get('verification_throughput', 0),
                'success_rate': self._calculate_verification_success_rate()
            }
            
            # Archive system
            components['archive'] = {
                'total_entries': self.get_current_metrics().get('archive_total_entries', 0),
                'operations_per_sec': self.get_current_metrics().get('archive_operations_per_sec', 0),
                'health_score': self.get_current_metrics().get('archive_health_score', 100)
            }
            
            # Agent system
            components['agents'] = {
                'compliance_rate': self._calculate_agent_compliance_rate(),
                'active_agents': self._get_active_agent_count(),
                'average_performance': self._calculate_average_agent_performance()
            }
            
            # CRDT system
            components['crdt'] = {
                'total_instances': self.get_current_metrics().get('crdt_total_instances', 0),
                'sync_rate': self.get_current_metrics().get('crdt_sync_rate', 0),
                'conflict_rate': self.get_current_metrics().get('crdt_conflict_rate', 0)
            }
            
        except Exception as e:
            print(f"[ERROR] Failed to collect component metrics: {e}")
        
        return components
    
    def _calculate_health_score(self, system_metrics: Dict[str, float], 
                              component_metrics: Dict[str, Dict[str, float]]) -> float:
        """Calculate overall system health score"""
        scores = []
        
        # Base system health
        base_health = system_metrics.get('system_health_score', 100)
        scores.append(base_health)
        
        # Component health scores
        for component, metrics in component_metrics.items():
            if component == 'verification':
                queue_size = metrics.get('queue_size', 0)
                # Lower queue size is better
                queue_score = max(0, 100 - (queue_size / 100))  # 100 items = 99 score
                scores.append(queue_score)
                
                # Throughput score
                throughput = metrics.get('throughput', 0)
                throughput_score = min(100, throughput * 5)  # 20 items/sec = 100 score
                scores.append(throughput_score)
            
            elif component == 'agents':
                compliance = metrics.get('compliance_rate', 0)
                compliance_score = compliance * 100
                scores.append(compliance_score)
            
            elif component == 'archive':
                ops_per_sec = metrics.get('operations_per_sec', 0)
                ops_score = min(100, ops_per_sec * 25)  # 4 ops/sec = 100 score
                scores.append(ops_score)
        
        # Return weighted average
        return statistics.mean(scores) if scores else 0.0
    
    def _generate_predictions(self) -> Dict[str, float]:
        """Generate predictive analytics"""
        predictions = {}
        
        try:
            # Predict verification queue size in 1 hour
            queue_trend = self.calculate_trend('archive_pending_verification', hours=2)
            current_queue = self.get_current_metrics().get('archive_pending_verification', 0)
            predicted_queue = max(0, current_queue + (queue_trend * 3600))  # 1 hour prediction
            predictions['verification_queue_1h'] = predicted_queue
            
            # Predict agent compliance in 1 hour
            compliance_trend = self.calculate_trend('agent_compliance_rate', hours=2)
            current_compliance = self.get_current_metrics().get('agent_compliance_rate', 0)
            predicted_compliance = max(0, min(1, current_compliance + (compliance_trend * 3600)))
            predictions['agent_compliance_1h'] = predicted_compliance
            
            # Predict system load
            ops_trend = self.calculate_trend('archive_operations_per_sec', hours=1)
            current_ops = self.get_current_metrics().get('archive_operations_per_sec', 0)
            predicted_ops = max(0, current_ops + (ops_trend * 3600))
            predictions['system_load_1h'] = predicted_ops
            
        except Exception as e:
            print(f"[ERROR] Failed to generate predictions: {e}")
        
        return predictions
    
    def _generate_recommendations(self) -> List[str]:
        """Generate performance recommendations"""
        recommendations = []
        current_metrics = self.get_current_metrics()
        
        # Verification queue recommendations
        queue_size = current_metrics.get('archive_pending_verification', 0)
        if queue_size > 5000:
            recommendations.append("CRITICAL: Activate emergency verification queue processing")
            recommendations.append("Consider enabling aggressive verification optimization mode")
        elif queue_size > 1000:
            recommendations.append("WARNING: Verification queue is growing - consider optimization")
        
        # Agent compliance recommendations
        compliance = current_metrics.get('agent_compliance_rate', 0)
        if compliance < 0.5:
            recommendations.append("CRITICAL: Agent compliance is very low - activate emergency mode")
        elif compliance < 0.7:
            recommendations.append("WARNING: Agent compliance needs improvement")
            recommendations.append("Consider enhanced correction strategies")
        elif compliance < 0.9:
            recommendations.append("INFO: Agent compliance approaching target - fine-tune parameters")
        
        # Performance recommendations
        ops_per_sec = current_metrics.get('archive_operations_per_sec', 0)
        if ops_per_sec < 0.5:
            recommendations.append("WARNING: System throughput is low - check system resources")
        
        # Health score recommendations
        health_score = current_metrics.get('system_health_score', 100)
        if health_score < 60:
            recommendations.append("CRITICAL: System health is poor - immediate attention required")
        elif health_score < 80:
            recommendations.append("WARNING: System health needs attention")
        
        return recommendations
    
    def _initialize_baseline(self):
        """Initialize performance baseline"""
        self.baseline_metrics = {
            'verification_queue_size': 100,
            'agent_compliance_rate': 0.8,
            'archive_operations_per_sec': 2.0,
            'system_health_score': 95.0
        }
    
    def _check_alerts(self, metric_name: str, value: float):
        """Check if metric value triggers any alerts"""
        if metric_name in self.thresholds:
            thresholds = self.thresholds[metric_name]
            
            if 'critical' in thresholds and value >= thresholds['critical']:
                self._trigger_alert(metric_name, value, 'critical')
            elif 'warning' in thresholds and value >= thresholds['warning']:
                self._trigger_alert(metric_name, value, 'warning')
    
    def _trigger_alert(self, metric_name: str, value: float, severity: str):
        """Trigger performance alert"""
        alert = {
            'timestamp': datetime.now().isoformat(),
            'metric': metric_name,
            'value': value,
            'severity': severity,
            'message': f"{severity.upper()}: {metric_name} = {value}"
        }
        
        print(f"[ALERT-{severity.upper()}] {alert['message']}")
        
        # Store alert
        if 'alerts' not in self.metrics:
            self.metrics['alerts'] = deque(maxlen=100)
        self.metrics['alerts'].append(alert)
    
    def _get_active_alerts(self) -> List[Dict[str, Any]]:
        """Get currently active alerts"""
        if 'alerts' not in self.metrics:
            return []
        
        # Return alerts from last hour
        cutoff_time = datetime.now() - timedelta(hours=1)
        active_alerts = []
        
        for alert in self.metrics['alerts']:
            alert_time = datetime.fromisoformat(alert['timestamp'])
            if alert_time >= cutoff_time:
                active_alerts.append(alert)
        
        return active_alerts
    
    def _get_system_health_data(self) -> Dict[str, float]:
        """Get system health data"""
        try:
            # Simulate system health metrics
            return {
                'system_health_score': 95.0,  # This would come from actual system monitoring
                'memory_usage_percent': 45.0,
                'cpu_usage_percent': 25.0,
                'disk_usage_percent': 60.0
            }
        except:
            return {}
    
    def _get_crdt_metrics(self) -> Dict[str, float]:
        """Get CRDT system metrics"""
        try:
            from .crdt_manager import get_crdt_manager
            manager = get_crdt_manager()
            stats = manager.get_health_metrics()
            
            return {
                'crdt_total_instances': float(stats.get('total_crdts', 0)),
                'crdt_sync_rate': 95.0,  # Placeholder
                'crdt_conflict_rate': 2.0  # Placeholder
            }
        except:
            return {}
    
    def _calculate_verification_success_rate(self) -> float:
        """Calculate verification success rate"""
        # This would be implemented based on actual verification data
        return 0.85  # Placeholder
    
    def _calculate_agent_compliance_rate(self) -> float:
        """Calculate overall agent compliance rate"""
        try:
            from .agent_workflow import get_workflow_manager
            manager = get_workflow_manager()
            
            # Get recent compliance data
            recent_compliance = []
            for agent_id, agent_data in manager.agents.items():
                history = agent_data.get('performance_history', [])
                if history:
                    recent_history = history[-10:]  # Last 10 cycles
                    success_rate = sum(1 for h in recent_history if h.get('success', False)) / len(recent_history)
                    recent_compliance.append(success_rate)
            
            if recent_compliance:
                avg_compliance = statistics.mean(recent_compliance)
                self.record_metric('agent_compliance_rate', avg_compliance, 'agents')
                return avg_compliance
            
            return 0.0
            
        except:
            return 0.0
    
    def _get_active_agent_count(self) -> float:
        """Get count of active agents"""
        try:
            from .agent_workflow import get_workflow_manager
            manager = get_workflow_manager()
            return float(len(manager.agents))
        except:
            return 0.0
    
    def _calculate_average_agent_performance(self) -> float:
        """Calculate average agent performance"""
        try:
            from .agent_workflow import get_workflow_manager
            manager = get_workflow_manager()
            
            performances = []
            for agent_id, agent_data in manager.agents.items():
                history = agent_data.get('performance_history', [])
                if history:
                    recent_scores = [h.get('score', 0) for h in history[-5:]]
                    avg_score = statistics.mean(recent_scores)
                    performances.append(avg_score)
            
            return statistics.mean(performances) if performances else 0.0
            
        except:
            return 0.0
    
    def _calculate_operations_per_second(self, metrics: List[PerformanceMetric]) -> float:
        """Calculate operations per second from metric history"""
        if len(metrics) < 2:
            return 0.0
        
        first_metric = metrics[0]
        last_metric = metrics[-1]
        
        time_diff = (datetime.fromisoformat(last_metric.timestamp) - 
                    datetime.fromisoformat(first_metric.timestamp)).total_seconds()
        
        if time_diff <= 0:
            return 0.0
        
        value_diff = last_metric.value - first_metric.value
        return max(0, value_diff / time_diff)
    
    def _should_update_baseline(self) -> bool:
        """Check if baseline should be updated"""
        # Update baseline every 4 hours
        return True  # Simplified for now
    
    def _update_baseline(self):
        """Update performance baseline"""
        current_metrics = self.get_current_metrics()
        
        for metric_name in self.baseline_metrics:
            if metric_name in current_metrics:
                # Use rolling average for baseline
                current_value = current_metrics[metric_name]
                baseline_value = self.baseline_metrics[metric_name]
                new_baseline = (baseline_value * 0.9) + (current_value * 0.1)
                self.baseline_metrics[metric_name] = new_baseline
    
    def _cleanup_current_data(self):
        """Clean up old performance data"""
        cutoff_time = datetime.now() - timedelta(hours=self.data_retention_hours)
        
        for metric_name, metric_queue in self.metrics.items():
            # Remove old metrics
            while (metric_queue and 
                   hasattr(metric_queue[0], 'timestamp') and
                   datetime.fromisoformat(metric_queue[0].timestamp) < cutoff_time):
                metric_queue.popleft()


# Global performance monitor instance
_performance_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance"""
    global _performance_monitor
    if _performance_monitor is None:
        _performance_monitor = PerformanceMonitor()
    return _performance_monitor

def start_performance_monitoring():
    """Start performance monitoring"""
    monitor = get_performance_monitor()
    monitor.start_monitoring()
    return monitor

def get_system_performance_report() -> SystemPerformanceReport:
    """Get comprehensive system performance report"""
    monitor = get_performance_monitor()
    return monitor.generate_system_report()

def get_system_metrics() -> Dict[str, Any]:
    """Get basic system metrics for backward compatibility"""
    try:
        monitor = get_performance_monitor()
        report = monitor.generate_system_report()
        
        return {
            "health_score": report.overall_health_score,
            "system_metrics": report.system_metrics,
            "component_metrics": report.component_metrics,
            "timestamp": report.timestamp
        }
    except Exception:
        # Fallback metrics
        return {
            "health_score": 85,
            "system_metrics": {
                "cpu_usage": 50.0,
                "memory_usage": 60.0,
                "disk_usage": 40.0
            },
            "component_metrics": {},
            "timestamp": datetime.now().isoformat()
        }