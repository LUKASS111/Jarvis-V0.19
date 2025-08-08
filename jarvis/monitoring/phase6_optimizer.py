"""
Phase 6 Performance Optimizer
Advanced performance monitoring and optimization for Jarvis 1.0.0
"""

import time
import threading
import psutil
import json
import statistics
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from pathlib import Path
from dataclasses import dataclass, asdict
from collections import defaultdict, deque


@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    name: str
    value: float
    unit: str
    timestamp: datetime
    category: str
    severity: str = "info"  # info, warning, critical


@dataclass
class OptimizationRecommendation:
    """Performance optimization recommendation"""
    component: str
    issue: str
    recommendation: str
    priority: str  # low, medium, high, critical
    expected_improvement: str
    implementation_effort: str  # low, medium, high


class Phase6PerformanceOptimizer:
    """
    Advanced Performance Optimizer for Phase 6 Continuous Improvement
    
    Features:
    - Real-time performance monitoring
    - Automatic optimization recommendations
    - Resource usage optimization
    - Performance regression detection
    - Intelligent caching management
    """
    
    def __init__(self):
        self.start_time = datetime.now()
        self.metrics_history: Dict[str, deque] = defaultdict(lambda: deque(maxlen=1000))
        self.optimization_history: List[OptimizationRecommendation] = []
        self.performance_baselines: Dict[str, float] = {}
        self.monitoring_active = False
        self.optimization_callbacks: List[Callable] = []
        
        # Performance thresholds
        self.thresholds = {
            "cpu_usage": {"warning": 70, "critical": 85},
            "memory_usage": {"warning": 80, "critical": 90},
            "response_time": {"warning": 2.0, "critical": 5.0},
            "error_rate": {"warning": 0.05, "critical": 0.1},
            "cache_hit_rate": {"warning": 0.7, "critical": 0.5}
        }
        
        # Optimization cache
        self.optimization_cache = {}
        self.cache_stats = {
            "hits": 0,
            "misses": 0,
            "evictions": 0,
            "last_cleanup": datetime.now()
        }
        
        self._initialize_monitoring()
    
    def _initialize_monitoring(self):
        """Initialize performance monitoring"""
        try:
            # Establish performance baselines
            self._establish_baselines()
            
            # Start monitoring thread
            self.monitoring_active = True
            self.monitor_thread = threading.Thread(target=self._monitoring_loop, daemon=True)
            self.monitor_thread.start()
            
            print(f"[OPTIMIZER] Phase 6 Performance Optimizer initialized")
            
        except Exception as e:
            print(f"[OPTIMIZER] Failed to initialize monitoring: {e}")
    
    def _establish_baselines(self):
        """Establish performance baselines for comparison"""
        try:
            # System resource baselines
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            
            self.performance_baselines.update({
                "cpu_baseline": cpu_percent,
                "memory_baseline": memory.percent,
                "available_memory": memory.available,
                "boot_time": psutil.boot_time()
            })
            
            print(f"[OPTIMIZER] Performance baselines established")
            print(f"[OPTIMIZER] CPU baseline: {cpu_percent:.1f}%")
            print(f"[OPTIMIZER] Memory baseline: {memory.percent:.1f}%")
            
        except Exception as e:
            print(f"[OPTIMIZER] Failed to establish baselines: {e}")
    
    def _monitoring_loop(self):
        """Main monitoring loop"""
        while self.monitoring_active:
            try:
                # Collect system metrics
                self._collect_system_metrics()
                
                # Analyze performance trends
                self._analyze_performance_trends()
                
                # Generate optimization recommendations
                self._generate_recommendations()
                
                # Cleanup optimization cache
                self._cleanup_cache()
                
                time.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                print(f"[OPTIMIZER] Monitoring error: {e}")
                time.sleep(60)  # Wait longer on error
    
    def _collect_system_metrics(self):
        """Collect comprehensive system metrics"""
        try:
            timestamp = datetime.now()
            
            # System resources
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Process-specific metrics
            process = psutil.Process()
            process_memory = process.memory_info()
            process_cpu = process.cpu_percent()
            
            # Network I/O (if available)
            try:
                network = psutil.net_io_counters()
                network_metrics = {
                    "bytes_sent": network.bytes_sent,
                    "bytes_recv": network.bytes_recv,
                    "packets_sent": network.packets_sent,
                    "packets_recv": network.packets_recv
                }
            except:
                network_metrics = {}
            
            # Store metrics
            metrics = [
                PerformanceMetric("cpu_usage", cpu_percent, "%", timestamp, "system"),
                PerformanceMetric("memory_usage", memory.percent, "%", timestamp, "system"),
                PerformanceMetric("memory_available", memory.available / 1024**3, "GB", timestamp, "system"),
                PerformanceMetric("disk_usage", disk.percent, "%", timestamp, "system"),
                PerformanceMetric("process_memory", process_memory.rss / 1024**2, "MB", timestamp, "process"),
                PerformanceMetric("process_cpu", process_cpu, "%", timestamp, "process"),
            ]
            
            for metric in metrics:
                self.metrics_history[metric.name].append(metric)
                
                # Check thresholds
                self._check_thresholds(metric)
            
        except Exception as e:
            print(f"[OPTIMIZER] Metric collection error: {e}")
    
    def _check_thresholds(self, metric: PerformanceMetric):
        """Check if metric exceeds performance thresholds"""
        if metric.name in self.thresholds:
            thresholds = self.thresholds[metric.name]
            
            if metric.value >= thresholds["critical"]:
                metric.severity = "critical"
                self._generate_threshold_alert(metric, "critical")
            elif metric.value >= thresholds["warning"]:
                metric.severity = "warning"
                self._generate_threshold_alert(metric, "warning")
    
    def _generate_threshold_alert(self, metric: PerformanceMetric, severity: str):
        """Generate alert for threshold violations"""
        alert_msg = f"[OPTIMIZER] {severity.upper()}: {metric.name} = {metric.value:.1f}{metric.unit}"
        print(alert_msg)
        
        # Generate optimization recommendation
        if severity == "critical":
            self._create_urgent_recommendation(metric)
    
    def _create_urgent_recommendation(self, metric: PerformanceMetric):
        """Create urgent optimization recommendation"""
        recommendations_map = {
            "cpu_usage": OptimizationRecommendation(
                component="System Resources",
                issue=f"High CPU usage: {metric.value:.1f}%",
                recommendation="Optimize background processes, implement task queuing",
                priority="critical",
                expected_improvement="20-30% CPU reduction",
                implementation_effort="medium"
            ),
            "memory_usage": OptimizationRecommendation(
                component="Memory Management",
                issue=f"High memory usage: {metric.value:.1f}%",
                recommendation="Implement memory pooling, optimize caching strategy",
                priority="critical",
                expected_improvement="15-25% memory reduction",
                implementation_effort="medium"
            )
        }
        
        if metric.name in recommendations_map:
            recommendation = recommendations_map[metric.name]
            self.optimization_history.append(recommendation)
            self._notify_optimization_callbacks(recommendation)
    
    def _analyze_performance_trends(self):
        """Analyze performance trends and patterns"""
        try:
            # Analyze recent trends (last 10 measurements)
            for metric_name, history in self.metrics_history.items():
                if len(history) >= 10:
                    recent_values = [m.value for m in list(history)[-10:]]
                    
                    # Calculate trend
                    if len(recent_values) > 1:
                        trend = (recent_values[-1] - recent_values[0]) / len(recent_values)
                        
                        # Check for concerning trends
                        if metric_name in ["cpu_usage", "memory_usage"] and trend > 2:
                            self._create_trend_recommendation(metric_name, trend, "increasing")
                        elif metric_name == "cache_hit_rate" and trend < -0.05:
                            self._create_trend_recommendation(metric_name, trend, "decreasing")
            
        except Exception as e:
            print(f"[OPTIMIZER] Trend analysis error: {e}")
    
    def _create_trend_recommendation(self, metric_name: str, trend: float, direction: str):
        """Create recommendation based on performance trends"""
        if direction == "increasing" and metric_name in ["cpu_usage", "memory_usage"]:
            recommendation = OptimizationRecommendation(
                component="Performance Trend",
                issue=f"{metric_name} showing {direction} trend: {trend:+.2f}/period",
                recommendation="Monitor closely, consider proactive optimization",
                priority="medium",
                expected_improvement="Prevent future performance degradation",
                implementation_effort="low"
            )
            self.optimization_history.append(recommendation)
    
    def _generate_recommendations(self):
        """Generate optimization recommendations based on current state"""
        try:
            current_time = datetime.now()
            
            # Only generate recommendations every 5 minutes
            if hasattr(self, 'last_recommendation_time'):
                if current_time - self.last_recommendation_time < timedelta(minutes=5):
                    return
            
            self.last_recommendation_time = current_time
            
            # Analyze cache performance
            if self.cache_stats["hits"] + self.cache_stats["misses"] > 0:
                hit_rate = self.cache_stats["hits"] / (self.cache_stats["hits"] + self.cache_stats["misses"])
                
                if hit_rate < 0.7:  # Less than 70% hit rate
                    recommendation = OptimizationRecommendation(
                        component="Caching System",
                        issue=f"Low cache hit rate: {hit_rate:.1%}",
                        recommendation="Optimize cache strategy, increase cache size, or improve cache key design",
                        priority="medium",
                        expected_improvement="20-40% performance improvement",
                        implementation_effort="medium"
                    )
                    self.optimization_history.append(recommendation)
            
            # Analyze memory efficiency
            if "process_memory" in self.metrics_history and len(self.metrics_history["process_memory"]) > 0:
                current_memory = self.metrics_history["process_memory"][-1].value
                if current_memory > 200:  # More than 200MB
                    recommendation = OptimizationRecommendation(
                        component="Memory Usage",
                        issue=f"High process memory usage: {current_memory:.1f}MB",
                        recommendation="Implement memory profiling, optimize data structures",
                        priority="low",
                        expected_improvement="10-20% memory reduction",
                        implementation_effort="high"
                    )
                    self.optimization_history.append(recommendation)
            
        except Exception as e:
            print(f"[OPTIMIZER] Recommendation generation error: {e}")
    
    def _cleanup_cache(self):
        """Cleanup optimization cache"""
        try:
            current_time = datetime.now()
            
            # Cleanup every hour
            if current_time - self.cache_stats["last_cleanup"] > timedelta(hours=1):
                # Remove old cache entries (older than 1 hour)
                cutoff_time = current_time - timedelta(hours=1)
                old_keys = [k for k, v in self.optimization_cache.items() 
                           if isinstance(v, dict) and v.get("timestamp", current_time) < cutoff_time]
                
                for key in old_keys:
                    del self.optimization_cache[key]
                    self.cache_stats["evictions"] += 1
                
                self.cache_stats["last_cleanup"] = current_time
                
                if old_keys:
                    print(f"[OPTIMIZER] Cache cleanup: removed {len(old_keys)} old entries")
        
        except Exception as e:
            print(f"[OPTIMIZER] Cache cleanup error: {e}")
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get comprehensive performance summary"""
        try:
            current_time = datetime.now()
            uptime = (current_time - self.start_time).total_seconds()
            
            # Calculate recent averages (last 10 measurements)
            recent_averages = {}
            for metric_name, history in self.metrics_history.items():
                if len(history) > 0:
                    recent_values = [m.value for m in list(history)[-10:]]
                    recent_averages[metric_name] = {
                        "current": recent_values[-1] if recent_values else 0,
                        "average": statistics.mean(recent_values) if recent_values else 0,
                        "max": max(recent_values) if recent_values else 0,
                        "min": min(recent_values) if recent_values else 0
                    }
            
            # Cache performance
            cache_hit_rate = 0
            if self.cache_stats["hits"] + self.cache_stats["misses"] > 0:
                cache_hit_rate = self.cache_stats["hits"] / (self.cache_stats["hits"] + self.cache_stats["misses"])
            
            return {
                "uptime_seconds": uptime,
                "monitoring_active": self.monitoring_active,
                "metrics_summary": recent_averages,
                "cache_performance": {
                    "hit_rate": cache_hit_rate,
                    "hits": self.cache_stats["hits"],
                    "misses": self.cache_stats["misses"],
                    "evictions": self.cache_stats["evictions"],
                    "cache_size": len(self.optimization_cache)
                },
                "recent_recommendations": len([r for r in self.optimization_history 
                                             if (current_time - datetime.now()).days == 0]),
                "performance_baselines": self.performance_baselines,
                "thresholds": self.thresholds
            }
            
        except Exception as e:
            print(f"[OPTIMIZER] Performance summary error: {e}")
            return {"error": str(e)}
    
    def get_optimization_recommendations(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent optimization recommendations"""
        recent_recommendations = self.optimization_history[-limit:] if self.optimization_history else []
        return [asdict(rec) for rec in recent_recommendations]
    
    def add_optimization_callback(self, callback: Callable):
        """Add callback for optimization notifications"""
        self.optimization_callbacks.append(callback)
    
    def _notify_optimization_callbacks(self, recommendation: OptimizationRecommendation):
        """Notify registered callbacks of new recommendations"""
        for callback in self.optimization_callbacks:
            try:
                callback(recommendation)
            except Exception as e:
                print(f"[OPTIMIZER] Callback notification error: {e}")
    
    def optimize_cache(self, operation: str, key: str, compute_func: Callable = None):
        """Intelligent caching with optimization"""
        try:
            cache_key = f"{operation}:{key}"
            
            # Check cache
            if cache_key in self.optimization_cache:
                self.cache_stats["hits"] += 1
                cached_result = self.optimization_cache[cache_key]
                
                # Check if cache entry is still fresh (within 10 minutes)
                if isinstance(cached_result, dict) and "timestamp" in cached_result:
                    age = datetime.now() - cached_result["timestamp"]
                    if age < timedelta(minutes=10):
                        return cached_result["data"]
                    else:
                        # Remove stale entry
                        del self.optimization_cache[cache_key]
            
            # Cache miss - compute result
            self.cache_stats["misses"] += 1
            
            if compute_func:
                result = compute_func()
                
                # Store in cache with timestamp
                self.optimization_cache[cache_key] = {
                    "data": result,
                    "timestamp": datetime.now()
                }
                
                return result
            
            return None
            
        except Exception as e:
            print(f"[OPTIMIZER] Cache optimization error: {e}")
            return None
    
    def shutdown(self):
        """Shutdown performance optimizer"""
        print(f"[OPTIMIZER] Shutting down performance optimizer")
        self.monitoring_active = False
        
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.join(timeout=5)
        
        # Generate final performance report
        summary = self.get_performance_summary()
        print(f"[OPTIMIZER] Final performance summary:")
        print(f"[OPTIMIZER] Uptime: {summary.get('uptime_seconds', 0):.1f}s")
        print(f"[OPTIMIZER] Cache hit rate: {summary.get('cache_performance', {}).get('hit_rate', 0):.1%}")
        print(f"[OPTIMIZER] Recommendations generated: {len(self.optimization_history)}")


# Global optimizer instance
_performance_optimizer = None

def get_performance_optimizer() -> Phase6PerformanceOptimizer:
    """Get global performance optimizer instance"""
    global _performance_optimizer
    if _performance_optimizer is None:
        _performance_optimizer = Phase6PerformanceOptimizer()
    return _performance_optimizer

def shutdown_performance_optimizer():
    """Shutdown global performance optimizer"""
    global _performance_optimizer
    if _performance_optimizer:
        _performance_optimizer.shutdown()
        _performance_optimizer = None