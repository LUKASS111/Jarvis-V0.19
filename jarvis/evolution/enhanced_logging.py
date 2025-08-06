"""
Enhanced Logging System for Jarvis V0.19
Professional logging with structured data, performance metrics, and integration with evolution tracking
"""

import json
import time
import logging
import structlog
import sys
import os
import threading
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Union
from pathlib import Path
from contextlib import contextmanager
import psutil
import traceback

# Suppress noisy logging unless debug mode
if os.getenv('JARVIS_DEBUG', '').lower() not in ['true', '1', 'yes']:
    logging.getLogger("httpx").setLevel(logging.WARNING)
    logging.getLogger("asyncio").setLevel(logging.WARNING)

class PerformanceMetrics:
    """Track performance metrics for logging"""
    
    def __init__(self):
        self.start_time = time.time()
        self.start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        self.operation_count = 0
        self.error_count = 0
        
    def record_operation(self, success: bool = True):
        """Record an operation completion"""
        self.operation_count += 1
        if not success:
            self.error_count += 1
    
    def get_metrics(self) -> Dict[str, float]:
        """Get current performance metrics"""
        current_time = time.time()
        current_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
        
        duration = current_time - self.start_time
        memory_delta = current_memory - self.start_memory
        
        return {
            'duration_seconds': duration,
            'operations_per_second': self.operation_count / duration if duration > 0 else 0,
            'memory_usage_mb': current_memory,
            'memory_delta_mb': memory_delta,
            'total_operations': self.operation_count,
            'error_rate': (self.error_count / self.operation_count * 100) if self.operation_count > 0 else 0,
            'success_rate': ((self.operation_count - self.error_count) / self.operation_count * 100) if self.operation_count > 0 else 100
        }

class EnhancedFormatter(structlog.stdlib.ProcessorFormatter):
    """Enhanced formatter with performance metrics"""
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.performance_metrics = PerformanceMetrics()
    
    def format(self, record):
        """Format log record with enhanced information"""
        # Add performance context
        if hasattr(record, 'performance_context'):
            record.performance_metrics = self.performance_metrics.get_metrics()
        
        return super().format(record)

class LogAggregator:
    """Aggregate and analyze log data for insights"""
    
    def __init__(self, max_entries: int = 10000):
        self.max_entries = max_entries
        self.entries = []
        self.lock = threading.Lock()
        
        # Statistics
        self.level_counts = {'DEBUG': 0, 'INFO': 0, 'WARNING': 0, 'ERROR': 0, 'CRITICAL': 0}
        self.component_stats = {}
        self.error_patterns = {}
    
    def add_entry(self, level: str, component: str, message: str, extra: Dict[str, Any] = None):
        """Add log entry and update statistics"""
        with self.lock:
            entry = {
                'timestamp': datetime.now().isoformat(),
                'level': level,
                'component': component,
                'message': message,
                'extra': extra or {}
            }
            
            self.entries.append(entry)
            
            # Maintain max entries limit
            if len(self.entries) > self.max_entries:
                self.entries.pop(0)
            
            # Update statistics
            self.level_counts[level] = self.level_counts.get(level, 0) + 1
            self.component_stats[component] = self.component_stats.get(component, 0) + 1
            
            # Track error patterns
            if level in ['ERROR', 'CRITICAL']:
                pattern = self._extract_error_pattern(message)
                self.error_patterns[pattern] = self.error_patterns.get(pattern, 0) + 1
    
    def _extract_error_pattern(self, message: str) -> str:
        """Extract error pattern from message"""
        # Simple pattern extraction - first 50 chars
        return message[:50].replace('\n', ' ').strip()
    
    def get_summary(self, minutes: int = 60) -> Dict[str, Any]:
        """Get summary of recent log activity"""
        cutoff_time = datetime.now() - timedelta(minutes=minutes)
        cutoff_str = cutoff_time.isoformat()
        
        with self.lock:
            recent_entries = [
                entry for entry in self.entries
                if entry['timestamp'] > cutoff_str
            ]
            
            recent_level_counts = {}
            recent_component_stats = {}
            
            for entry in recent_entries:
                level = entry['level']
                component = entry['component']
                
                recent_level_counts[level] = recent_level_counts.get(level, 0) + 1
                recent_component_stats[component] = recent_component_stats.get(component, 0) + 1
            
            return {
                'period_minutes': minutes,
                'total_entries': len(recent_entries),
                'level_distribution': recent_level_counts,
                'component_activity': recent_component_stats,
                'error_rate': (recent_level_counts.get('ERROR', 0) + recent_level_counts.get('CRITICAL', 0)) / len(recent_entries) * 100 if recent_entries else 0,
                'most_active_components': sorted(recent_component_stats.items(), key=lambda x: x[1], reverse=True)[:5],
                'top_error_patterns': sorted(self.error_patterns.items(), key=lambda x: x[1], reverse=True)[:3]
            }

class EnhancedLogger:
    """Enhanced logger with performance tracking and evolution integration"""
    
    def __init__(self, name: str, log_dir: str = None):
        self.name = name
        
        if log_dir is None:
            log_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'logs', 'enhanced')
        
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Performance tracking
        self.performance_metrics = PerformanceMetrics()
        
        # Log aggregation
        self.aggregator = LogAggregator()
        
        # Configure structured logging
        self._configure_logging()
        
        # Get logger
        self.logger = structlog.get_logger(name)
        
        # Evolution tracking integration
        self._evolution_tracker = None
        try:
            from jarvis.evolution import get_evolution_tracker
            self._evolution_tracker = get_evolution_tracker()
        except ImportError:
            pass  # Evolution tracker not available
    
    def _configure_logging(self):
        """Configure structured logging with enhanced features"""
        # Simpler configuration to avoid conflicts
        try:
            # Configure structlog for console output only
            structlog.configure(
                processors=[
                    structlog.stdlib.filter_by_level,
                    structlog.stdlib.add_logger_name,
                    structlog.stdlib.add_log_level,
                    structlog.stdlib.PositionalArgumentsFormatter(),
                    structlog.processors.TimeStamper(fmt="ISO"),
                    structlog.dev.ConsoleRenderer(colors=False)  # Disable colors to avoid formatting issues
                ],
                context_class=dict,
                logger_factory=structlog.stdlib.LoggerFactory(),
                wrapper_class=structlog.stdlib.BoundLogger,
                cache_logger_on_first_use=True,
            )
            
            # Setup simple file logging
            log_file = self.log_dir / f"{self.name}_{datetime.now().strftime('%Y%m%d')}.log"
            
            # Create a simple file handler with basic formatting
            file_handler = logging.FileHandler(log_file)
            file_handler.setFormatter(logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
            ))
            
            # Configure logger
            logger = logging.getLogger(self.name)
            logger.addHandler(file_handler)
            logger.setLevel(logging.INFO)
            
        except Exception as e:
            # Fallback to basic logging if structlog configuration fails
            logging.basicConfig(level=logging.INFO)
    
    @contextmanager
    def operation_context(self, operation_name: str, **context):
        """Context manager for tracking operations"""
        start_time = time.time()
        start_memory = psutil.Process().memory_info().rss / 1024 / 1024
        
        operation_logger = self.logger.bind(
            operation=operation_name,
            start_time=start_time,
            **context
        )
        
        try:
            operation_logger.info("Operation started", operation=operation_name)
            yield operation_logger
            
            # Record successful operation
            self.performance_metrics.record_operation(success=True)
            
            duration = time.time() - start_time
            memory_delta = psutil.Process().memory_info().rss / 1024 / 1024 - start_memory
            
            operation_logger.info(
                "Operation completed successfully",
                duration_seconds=duration,
                memory_delta_mb=memory_delta
            )
            
            # Log to aggregator
            self.aggregator.add_entry(
                'INFO', self.name,
                f"Operation {operation_name} completed",
                {'duration_seconds': duration, 'memory_delta_mb': memory_delta}
            )
            
        except Exception as e:
            # Record failed operation
            self.performance_metrics.record_operation(success=False)
            
            duration = time.time() - start_time
            memory_delta = psutil.Process().memory_info().rss / 1024 / 1024 - start_memory
            
            operation_logger.error(
                "Operation failed",
                error=str(e),
                error_type=type(e).__name__,
                duration_seconds=duration,
                memory_delta_mb=memory_delta,
                traceback=traceback.format_exc()
            )
            
            # Log to aggregator
            self.aggregator.add_entry(
                'ERROR', self.name,
                f"Operation {operation_name} failed: {str(e)}",
                {'duration_seconds': duration, 'error_type': type(e).__name__}
            )
            
            raise
    
    def info(self, message: str, **kwargs):
        """Log info message with enhancement"""
        self.logger.info(message, **kwargs)
        self.aggregator.add_entry('INFO', self.name, message, kwargs)
    
    def warning(self, message: str, **kwargs):
        """Log warning message with enhancement"""
        self.logger.warning(message, **kwargs)
        self.aggregator.add_entry('WARNING', self.name, message, kwargs)
    
    def error(self, message: str, **kwargs):
        """Log error message with enhancement"""
        self.logger.error(message, **kwargs)
        self.aggregator.add_entry('ERROR', self.name, message, kwargs)
        
        # Track error in evolution system
        if self._evolution_tracker and self._evolution_tracker.current_session:
            from jarvis.evolution import EvolutionMetric
            metric = EvolutionMetric(
                timestamp=datetime.now().isoformat(),
                metric_type='quality',
                component=self.name,
                value=0.0,  # Error reduces quality
                baseline=100.0,
                improvement=-1.0,  # Negative improvement
                validation_status='validated',
                data_source='enhanced_logger',
                notes=f"Error logged: {message}"
            )
            self._evolution_tracker.log_evolution_metric(metric)
    
    def debug(self, message: str, **kwargs):
        """Log debug message with enhancement"""
        self.logger.debug(message, **kwargs)
        self.aggregator.add_entry('DEBUG', self.name, message, kwargs)
    
    def critical(self, message: str, **kwargs):
        """Log critical message with enhancement"""
        self.logger.critical(message, **kwargs)
        self.aggregator.add_entry('CRITICAL', self.name, message, kwargs)
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get comprehensive performance report"""
        metrics = self.performance_metrics.get_metrics()
        log_summary = self.aggregator.get_summary()
        
        return {
            'logger_name': self.name,
            'performance_metrics': metrics,
            'log_activity_summary': log_summary,
            'overall_health': {
                'error_rate': metrics['error_rate'],
                'operations_per_second': metrics['operations_per_second'],
                'memory_efficiency': 'good' if metrics['memory_delta_mb'] < 100 else 'needs_attention',
                'log_volume': log_summary['total_entries']
            }
        }

# Global logger registry
_loggers = {}
_logger_lock = threading.Lock()

def get_enhanced_logger(name: str, log_dir: str = None) -> EnhancedLogger:
    """Get or create enhanced logger instance"""
    with _logger_lock:
        if name not in _loggers:
            _loggers[name] = EnhancedLogger(name, log_dir)
        return _loggers[name]

def get_all_loggers_report() -> Dict[str, Any]:
    """Get comprehensive report from all active loggers"""
    with _logger_lock:
        reports = {}
        total_operations = 0
        total_errors = 0
        
        for name, logger in _loggers.items():
            report = logger.get_performance_report()
            reports[name] = report
            
            metrics = report['performance_metrics']
            total_operations += metrics['total_operations']
            total_errors += metrics['error_rate'] * metrics['total_operations'] / 100
        
        overall_error_rate = (total_errors / total_operations * 100) if total_operations > 0 else 0
        
        return {
            'timestamp': datetime.now().isoformat(),
            'total_loggers': len(_loggers),
            'individual_reports': reports,
            'aggregate_metrics': {
                'total_operations': total_operations,
                'overall_error_rate': overall_error_rate,
                'active_loggers': list(_loggers.keys())
            }
        }