#!/usr/bin/env python3
"""
Modern Analytics Engine
======================
Enhanced analytics with modern Python patterns and real-time processing.
"""

import logging
from pathlib import Path
from typing import Dict, Any, List, Optional, Union
from datetime import datetime, timedelta
import json
from collections import defaultdict, deque
import threading
import statistics

# Configure logging
logger = logging.getLogger(__name__)

class ModernAnalyticsEngine:
    """Modern analytics engine with real-time metrics and insights"""
    
    def __init__(self, retention_days: int = 30):
        self.retention_days = retention_days
        self.metrics_store = defaultdict(deque)
        self.aggregated_metrics = {}
        self._lock = threading.RLock()
        
        logger.info(f"Analytics engine initialized with {retention_days} days retention")
    
    def record_metric(self, metric_name: str, value: Union[int, float], tags: Dict[str, str] = None) -> bool:
        """Record metric with modern timestamp and metadata"""
        try:
            with self._lock:
                timestamp = datetime.now()
                
                metric_data = {
                    'timestamp': timestamp,
                    'value': value,
                    'tags': tags or {}
                }
                
                self.metrics_store[metric_name].append(metric_data)
                
                logger.debug(f"Recorded metric {metric_name}: {value}")
                return True
                
        except Exception as e:
            logger.error(f"Failed to record metric {metric_name}: {e}")
            return False
    
    def get_metric_stats(self, metric_name: str, time_range_hours: int = 24) -> Dict[str, Any]:
        """Get metric statistics with modern aggregation"""
        try:
            with self._lock:
                if metric_name not in self.metrics_store:
                    return {'error': 'Metric not found'}
                
                cutoff_time = datetime.now() - timedelta(hours=time_range_hours)
                recent_values = []
                
                for metric_data in self.metrics_store[metric_name]:
                    if metric_data['timestamp'] >= cutoff_time:
                        recent_values.append(metric_data['value'])
                
                if not recent_values:
                    return {'error': 'No data in time range'}
                
                stats = {
                    'count': len(recent_values),
                    'min': min(recent_values),
                    'max': max(recent_values),
                    'mean': statistics.mean(recent_values),
                    'median': statistics.median(recent_values),
                    'std_dev': statistics.stdev(recent_values) if len(recent_values) > 1 else 0,
                    'sum': sum(recent_values),
                    'time_range_hours': time_range_hours,
                    'latest_value': recent_values[-1] if recent_values else None
                }
                
                return stats
                
        except Exception as e:
            logger.error(f"Failed to get metric stats for {metric_name}: {e}")
            return {'error': str(e)}

# Initialize global analytics engine
analytics_engine = ModernAnalyticsEngine()

def get_analytics_engine() -> ModernAnalyticsEngine:
    """Get global analytics engine instance"""
    return analytics_engine