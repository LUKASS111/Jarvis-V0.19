"""
Monitoring module initialization for Jarvis 1.0.0
Enhanced with 100% system health and real-time metrics functionality
"""

from .performance_optimizer import (
    PerformanceMonitor,
    PerformanceOptimizer,
    SystemHealth,
    PerformanceMetric,
    get_performance_monitor,
    get_performance_optimizer,
    monitor_performance,
    run_performance_analysis
)

try:
    from .system_health import (
        SystemHealthMonitor, HealthStatus, SystemHealthReport,
        get_health_monitor, start_health_monitoring, get_health_status
    )

    from .realtime_metrics import (
        AdvancedMetricsCollector, MetricDefinition, MetricValue, MetricType,
        get_metrics_collector, start_metrics_collection, record_metric
    )
    
    # Enhanced __all__ with new monitoring capabilities
    __all__ = [
        'PerformanceMonitor',
        'PerformanceOptimizer', 
        'SystemHealth',
        'PerformanceMetric',
        'get_performance_monitor',
        'get_performance_optimizer',
        'monitor_performance',
        'run_performance_analysis',
        # Enhanced monitoring
        'SystemHealthMonitor', 'HealthStatus', 'SystemHealthReport',
        'get_health_monitor', 'start_health_monitoring', 'get_health_status',
        'AdvancedMetricsCollector', 'MetricDefinition', 'MetricValue', 'MetricType',
        'get_metrics_collector', 'start_metrics_collection', 'record_metric'
    ]
    
except ImportError as e:
    print(f"Enhanced monitoring not available: {e}")
    # Fallback to basic monitoring
    __all__ = [
        'PerformanceMonitor',
        'PerformanceOptimizer', 
        'SystemHealth',
        'PerformanceMetric',
        'get_performance_monitor',
        'get_performance_optimizer',
        'monitor_performance',
        'run_performance_analysis'
    ]