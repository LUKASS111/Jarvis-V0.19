"""
Advanced System Monitoring and Performance Optimization for Jarvis 1.0.0
Provides comprehensive system monitoring, performance analytics, and optimization recommendations.
"""

import time
import threading
try:
    import psutil
except ImportError:
    psutil = None
import json
import os
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional
from dataclasses import dataclass, asdict
from collections import deque, defaultdict
import logging

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

@dataclass
class PerformanceMetric:
    """Performance metric data structure."""
    timestamp: float
    cpu_percent: float
    memory_percent: float
    memory_usage_mb: float
    disk_usage_mb: float
    network_io_mb: float
    active_threads: int
    open_files: int

@dataclass
class SystemHealth:
    """System health assessment."""
    overall_score: int
    cpu_health: int
    memory_health: int
    disk_health: int
    network_health: int
    recommendations: List[str]
    alerts: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert SystemHealth to dictionary."""
        return asdict(self)
    
    def get(self, key: str, default: Any = None) -> Any:
        """Dictionary-like access for compatibility."""
        data = asdict(self)
        return data.get(key, default)

class PerformanceMonitor:
    """Advanced performance monitoring system."""
    
    def __init__(self, history_size: int = 1000, alert_threshold: float = 80.0):
        """Initialize performance monitor."""
        self.history_size = history_size
        self.alert_threshold = alert_threshold
        self.metrics_history = deque(maxlen=history_size)
        self.alerts = deque(maxlen=100)
        self.running = False
        self.monitor_thread = None
        self.start_time = time.time()
        
        # Performance counters
        self.operation_counters = defaultdict(int)
        self.response_times = defaultdict(list)
        self.error_counts = defaultdict(int)
        
        # System baselines
        self.baseline_metrics = None
        self.peak_metrics = {
            'cpu': 0.0,
            'memory': 0.0,
            'disk': 0.0,
            'network': 0.0
        }
    
    def start_monitoring(self, interval: float = 5.0):
        """Start continuous monitoring."""
        if self.running:
            logger.warning("Monitoring already running")
            return
        
        self.running = True
        self.monitor_thread = threading.Thread(
            target=self._monitoring_loop,
            args=(interval,),
            daemon=True
        )
        self.monitor_thread.start()
        logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop continuous monitoring."""
        self.running = False
        if self.monitor_thread:
            self.monitor_thread.join(timeout=10)
        logger.info("Performance monitoring stopped")
    
    def _monitoring_loop(self, interval: float):
        """Main monitoring loop."""
        while self.running:
            try:
                metric = self._collect_metrics()
                self.metrics_history.append(metric)
                self._check_alerts(metric)
                self._update_peaks(metric)
                time.sleep(interval)
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
                time.sleep(interval)
    
    def _collect_metrics(self) -> PerformanceMetric:
        """Collect current system metrics."""
        if psutil is None:
            # Return mock metrics when psutil is not available
            return PerformanceMetric(
                timestamp=time.time(),
                cpu_percent=15.0,
                memory_percent=35.0,
                memory_usage_mb=512.0,
                disk_usage_mb=1024.0,
                network_io_mb=128.0,
                active_threads=threading.active_count(),
                open_files=10
            )
        
        process = psutil.Process()
        
        # CPU metrics
        cpu_percent = psutil.cpu_percent(interval=1)
        
        # Memory metrics
        memory_info = process.memory_info()
        memory_percent = process.memory_percent()
        memory_usage_mb = memory_info.rss / 1024 / 1024
        
        # Disk usage
        try:
            disk_usage = psutil.disk_usage('/')
            disk_usage_mb = (disk_usage.used) / 1024 / 1024
        except:
            disk_usage_mb = 0
        
        # Network I/O
        try:
            net_io = psutil.net_io_counters()
            network_io_mb = (net_io.bytes_sent + net_io.bytes_recv) / 1024 / 1024
        except:
            network_io_mb = 0
        
        # Thread and file metrics
        active_threads = threading.active_count()
        try:
            open_files = len(process.open_files())
        except:
            open_files = 0
        
        return PerformanceMetric(
            timestamp=time.time(),
            cpu_percent=cpu_percent,
            memory_percent=memory_percent,
            memory_usage_mb=memory_usage_mb,
            disk_usage_mb=disk_usage_mb,
            network_io_mb=network_io_mb,
            active_threads=active_threads,
            open_files=open_files
        )
    
    def _check_alerts(self, metric: PerformanceMetric):
        """Check for performance alerts."""
        alerts = []
        
        if metric.cpu_percent > self.alert_threshold:
            alerts.append(f"High CPU usage: {metric.cpu_percent:.1f}%")
        
        if metric.memory_percent > self.alert_threshold:
            alerts.append(f"High memory usage: {metric.memory_percent:.1f}%")
        
        if metric.memory_usage_mb > 1000:  # 1GB threshold
            alerts.append(f"High memory consumption: {metric.memory_usage_mb:.1f}MB")
        
        if metric.open_files > 100:
            alerts.append(f"High file descriptor usage: {metric.open_files}")
        
        for alert in alerts:
            self.alerts.append({
                'timestamp': metric.timestamp,
                'message': alert,
                'severity': 'warning'
            })
    
    def _update_peaks(self, metric: PerformanceMetric):
        """Update peak performance metrics."""
        self.peak_metrics['cpu'] = max(self.peak_metrics['cpu'], metric.cpu_percent)
        self.peak_metrics['memory'] = max(self.peak_metrics['memory'], metric.memory_percent)
        self.peak_metrics['disk'] = max(self.peak_metrics['disk'], metric.disk_usage_mb)
        self.peak_metrics['network'] = max(self.peak_metrics['network'], metric.network_io_mb)
    
    def record_operation(self, operation: str, response_time: float, success: bool = True):
        """Record operation performance."""
        self.operation_counters[operation] += 1
        self.response_times[operation].append(response_time)
        
        # Keep only recent response times
        if len(self.response_times[operation]) > 100:
            self.response_times[operation] = self.response_times[operation][-100:]
        
        if not success:
            self.error_counts[operation] += 1
    
    def get_current_metrics(self) -> Optional[PerformanceMetric]:
        """Get most recent metrics."""
        return self.metrics_history[-1] if self.metrics_history else None
    
    def collect_metrics(self):
        """Manually collect performance metrics."""
        self._collect_metrics()
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary."""
        if not self.metrics_history:
            return {"error": "No metrics available"}
        
        recent_metrics = list(self.metrics_history)[-20:]  # Last 20 samples
        
        # Calculate averages
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory_mb = sum(m.memory_usage_mb for m in recent_metrics) / len(recent_metrics)
        
        # Operation statistics
        operation_stats = {}
        for op, times in self.response_times.items():
            if times:
                operation_stats[op] = {
                    'count': self.operation_counters[op],
                    'avg_response_time': sum(times) / len(times),
                    'min_response_time': min(times),
                    'max_response_time': max(times),
                    'error_count': self.error_counts[op],
                    'error_rate': self.error_counts[op] / self.operation_counters[op] if self.operation_counters[op] > 0 else 0
                }
        
        uptime = time.time() - self.start_time
        
        return {
            'uptime_seconds': uptime,
            'uptime_formatted': str(timedelta(seconds=int(uptime))),
            'current_metrics': asdict(self.get_current_metrics()) if self.get_current_metrics() else None,
            'averages': {
                'cpu_percent': round(avg_cpu, 2),
                'memory_percent': round(avg_memory, 2),
                'memory_usage_mb': round(avg_memory_mb, 2)
            },
            'peaks': self.peak_metrics,
            'operation_stats': operation_stats,
            'recent_alerts': list(self.alerts)[-10:],  # Last 10 alerts
            'total_samples': len(self.metrics_history)
        }
    
    def assess_system_health(self) -> SystemHealth:
        """Assess overall system health and provide recommendations."""
        if not self.metrics_history:
            return SystemHealth(
                overall_score=0,
                cpu_health=0,
                memory_health=0,
                disk_health=0,
                network_health=0,
                recommendations=["Insufficient data for health assessment"],
                alerts=[]
            )
        
        recent_metrics = list(self.metrics_history)[-10:]  # Last 10 samples
        
        # Calculate health scores (0-100)
        avg_cpu = sum(m.cpu_percent for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m.memory_percent for m in recent_metrics) / len(recent_metrics)
        
        cpu_health = max(0, 100 - avg_cpu)
        memory_health = max(0, 100 - avg_memory)
        disk_health = 90  # Placeholder - would need more sophisticated disk analysis
        network_health = 90  # Placeholder - would need network latency analysis
        
        overall_score = int((cpu_health + memory_health + disk_health + network_health) / 4)
        
        # Generate recommendations
        recommendations = []
        alerts = []
        
        if avg_cpu > 70:
            recommendations.append("Consider optimizing CPU-intensive operations")
            if avg_cpu > 90:
                alerts.append("Critical CPU usage detected")
        
        if avg_memory > 70:
            recommendations.append("Monitor memory usage - consider memory optimization")
            if avg_memory > 90:
                alerts.append("Critical memory usage detected")
        
        # Check error rates
        high_error_ops = []
        for op, stats in self.get_performance_summary().get('operation_stats', {}).items():
            if stats.get('error_rate', 0) > 0.1:  # 10% error rate
                high_error_ops.append(op)
        
        if high_error_ops:
            recommendations.append(f"High error rates detected in: {', '.join(high_error_ops)}")
        
        if overall_score > 90:
            recommendations.append("System performing excellently")
        elif overall_score > 70:
            recommendations.append("System performing well with room for optimization")
        else:
            recommendations.append("System performance needs attention")
        
        return SystemHealth(
            overall_score=overall_score,
            cpu_health=int(cpu_health),
            memory_health=int(memory_health),
            disk_health=int(disk_health),
            network_health=int(network_health),
            recommendations=recommendations,
            alerts=alerts
        )

class PerformanceOptimizer:
    """Performance optimization engine."""
    
    def __init__(self, monitor: PerformanceMonitor):
        """Initialize optimizer with monitor."""
        self.monitor = monitor
        self.optimization_history = []
    
    def analyze_bottlenecks(self) -> Dict[str, Any]:
        """Analyze system bottlenecks and provide optimization suggestions."""
        summary = self.monitor.get_performance_summary()
        
        if not summary or 'operation_stats' not in summary:
            return {"error": "Insufficient data for bottleneck analysis"}
        
        bottlenecks = []
        optimizations = []
        
        # Analyze operation performance
        for op, stats in summary['operation_stats'].items():
            avg_time = stats['avg_response_time']
            error_rate = stats['error_rate']
            
            if avg_time > 5.0:  # 5 second threshold
                bottlenecks.append({
                    'type': 'slow_operation',
                    'operation': op,
                    'avg_response_time': avg_time,
                    'severity': 'high' if avg_time > 10.0 else 'medium'
                })
                
                optimizations.append({
                    'target': op,
                    'suggestion': 'Consider optimizing operation logic or adding caching',
                    'potential_improvement': '30-50% response time reduction'
                })
            
            if error_rate > 0.05:  # 5% error rate
                bottlenecks.append({
                    'type': 'high_error_rate',
                    'operation': op,
                    'error_rate': error_rate,
                    'severity': 'high' if error_rate > 0.1 else 'medium'
                })
                
                optimizations.append({
                    'target': op,
                    'suggestion': 'Investigate and fix error conditions',
                    'potential_improvement': 'Improved reliability and user experience'
                })
        
        # System-level analysis
        avg_cpu = summary['averages']['cpu_percent']
        avg_memory = summary['averages']['memory_percent']
        
        if avg_cpu > 60:
            bottlenecks.append({
                'type': 'high_cpu_usage',
                'value': avg_cpu,
                'severity': 'high' if avg_cpu > 80 else 'medium'
            })
            
            optimizations.append({
                'target': 'system',
                'suggestion': 'Consider CPU optimization: async operations, algorithm improvements',
                'potential_improvement': '20-40% CPU usage reduction'
            })
        
        if avg_memory > 60:
            bottlenecks.append({
                'type': 'high_memory_usage',
                'value': avg_memory,
                'severity': 'high' if avg_memory > 80 else 'medium'
            })
            
            optimizations.append({
                'target': 'system',
                'suggestion': 'Consider memory optimization: object pooling, garbage collection tuning',
                'potential_improvement': '15-30% memory usage reduction'
            })
        
        return {
            'analysis_timestamp': datetime.now().isoformat(),
            'bottlenecks': bottlenecks,
            'optimizations': optimizations,
            'priority_score': len([b for b in bottlenecks if b.get('severity') == 'high']),
            'summary': f"Found {len(bottlenecks)} bottlenecks with {len(optimizations)} optimization opportunities"
        }
    
    def suggest_optimizations(self) -> List[Dict[str, Any]]:
        """Provide specific optimization suggestions."""
        analysis = self.analyze_bottlenecks()
        
        if 'error' in analysis:
            return []
        
        suggestions = []
        
        # Add general optimizations based on system state
        health = self.monitor.assess_system_health()
        
        if health.overall_score < 70:
            suggestions.extend([
                {
                    'category': 'system_tuning',
                    'title': 'Enable Performance Monitoring',
                    'description': 'Implement continuous performance monitoring with alerting',
                    'implementation': 'monitor.start_monitoring(interval=5.0)',
                    'expected_benefit': 'Proactive performance management'
                },
                {
                    'category': 'optimization',
                    'title': 'Implement Response Caching',
                    'description': 'Add caching layer for frequently accessed data',
                    'implementation': 'Use Redis or in-memory caching for hot data',
                    'expected_benefit': '40-60% response time improvement'
                }
            ])
        
        # Add specific optimizations from analysis
        for optimization in analysis.get('optimizations', []):
            suggestions.append({
                'category': 'targeted_optimization',
                'title': f"Optimize {optimization['target']}",
                'description': optimization['suggestion'],
                'expected_benefit': optimization['potential_improvement'],
                'priority': 'high' if 'critical' in optimization['suggestion'].lower() else 'medium'
            })
        
        return suggestions

# Global monitor instance
_global_monitor = None

def get_performance_monitor() -> PerformanceMonitor:
    """Get global performance monitor instance."""
    global _global_monitor
    if _global_monitor is None:
        _global_monitor = PerformanceMonitor()
        _global_monitor.start_monitoring()
    return _global_monitor

def get_performance_optimizer() -> PerformanceOptimizer:
    """Get performance optimizer instance."""
    monitor = get_performance_monitor()
    return PerformanceOptimizer(monitor)

# Decorator for automatic performance monitoring
def monitor_performance(operation_name: str):
    """Decorator to automatically monitor function performance."""
    def decorator(func):
        def wrapper(*args, **kwargs):
            monitor = get_performance_monitor()
            start_time = time.time()
            success = True
            
            try:
                result = func(*args, **kwargs)
                return result
            except Exception as e:
                success = False
                raise
            finally:
                response_time = time.time() - start_time
                monitor.record_operation(operation_name, response_time, success)
        
        return wrapper
    return decorator

# Example usage functions
@monitor_performance("example_operation")
def example_monitored_function():
    """Example function with performance monitoring."""
    time.sleep(0.1)  # Simulate work
    return "Operation completed"

def run_performance_analysis():
    """Run comprehensive performance analysis."""
    print("🔍 Running Performance Analysis...")
    print("=" * 50)
    
    monitor = get_performance_monitor()
    optimizer = get_performance_optimizer()
    
    # Let it collect some data
    print("Collecting performance data...")
    time.sleep(2)
    
    # Run some example operations
    for i in range(5):
        example_monitored_function()
        time.sleep(0.5)
    
    # Get performance summary
    summary = monitor.get_performance_summary()
    print(f"\n📊 Performance Summary:")
    print(f"Uptime: {summary['uptime_formatted']}")
    print(f"Samples collected: {summary['total_samples']}")
    
    if summary['current_metrics']:
        current = summary['current_metrics']
        print(f"Current CPU: {current['cpu_percent']:.1f}%")
        print(f"Current Memory: {current['memory_percent']:.1f}%")
        print(f"Memory Usage: {current['memory_usage_mb']:.1f}MB")
    
    # Health assessment
    health = monitor.assess_system_health()
    print(f"\n🏥 System Health Assessment:")
    print(f"Overall Score: {health.overall_score}/100")
    print(f"CPU Health: {health.cpu_health}/100")
    print(f"Memory Health: {health.memory_health}/100")
    
    if health.recommendations:
        print(f"\n💡 Recommendations:")
        for rec in health.recommendations:
            print(f"  - {rec}")
    
    # Optimization suggestions
    suggestions = optimizer.suggest_optimizations()
    if suggestions:
        print(f"\n⚡ Optimization Opportunities ({len(suggestions)}):")
        for i, suggestion in enumerate(suggestions[:3], 1):
            print(f"  {i}. {suggestion['title']}")
            print(f"     {suggestion['description']}")
            print(f"     Expected benefit: {suggestion['expected_benefit']}")
    
    print(f"\n✅ Performance analysis completed successfully!")
    return summary

if __name__ == "__main__":
    # Run performance analysis demo
    results = run_performance_analysis()
    print(f"\nResults: {len(results)} metrics analyzed")