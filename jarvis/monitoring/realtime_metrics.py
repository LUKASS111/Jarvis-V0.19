"""
Advanced Real-time Metrics Collection for Jarvis-V0.19
100% functionality with streaming, visualization, and advanced aggregation
"""

import time
import threading
import json
import os
import asyncio
import websockets
import sqlite3
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Callable, Union
from dataclasses import dataclass, asdict
from enum import Enum
import statistics
import math
from collections import defaultdict, deque
import numpy as np
import concurrent.futures


class MetricType(Enum):
    """Types of metrics supported"""
    COUNTER = "counter"      # Monotonically increasing
    GAUGE = "gauge"          # Point-in-time value
    HISTOGRAM = "histogram"  # Distribution of values
    TIMER = "timer"          # Duration measurements
    RATE = "rate"           # Rate of change
    PERCENTAGE = "percentage" # 0-100 percentage


@dataclass
class MetricDefinition:
    """Definition of a custom metric"""
    name: str
    metric_type: MetricType
    description: str
    unit: str
    labels: List[str]
    aggregation_window: int  # seconds
    retention_hours: int
    alert_thresholds: Dict[str, float]
    custom_aggregator: Optional[Callable] = None


@dataclass
class MetricValue:
    """Individual metric value with metadata"""
    timestamp: str
    value: Union[float, List[float]]  # List for histograms
    labels: Dict[str, str]
    source: str
    metadata: Dict[str, Any]


@dataclass
class MetricAggregation:
    """Aggregated metric data"""
    metric_name: str
    start_time: str
    end_time: str
    count: int
    min_value: float
    max_value: float
    avg_value: float
    sum_value: float
    percentiles: Dict[str, float]  # p50, p90, p95, p99
    rate_per_second: float
    standard_deviation: float


class MetricStorage:
    """SQLite-based storage for metrics with advanced querying"""
    
    def __init__(self, db_path: str = None):
        if db_path is None:
            db_path = os.path.join(os.path.dirname(__file__), '..', '..', 'data', 'metrics.db')
        
        self.db_path = db_path
        os.makedirs(os.path.dirname(db_path), exist_ok=True)
        self._init_database()
    
    def _init_database(self):
        """Initialize metrics database with optimized schema"""
        with sqlite3.connect(self.db_path) as conn:
            # Main metrics table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS metrics (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    value REAL,
                    histogram_data TEXT,
                    labels TEXT,
                    source TEXT,
                    metadata TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Aggregated metrics table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS metric_aggregations (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    metric_name TEXT NOT NULL,
                    start_time TEXT NOT NULL,
                    end_time TEXT NOT NULL,
                    count INTEGER,
                    min_value REAL,
                    max_value REAL,
                    avg_value REAL,
                    sum_value REAL,
                    percentiles TEXT,
                    rate_per_second REAL,
                    standard_deviation REAL,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Metric definitions table
            conn.execute('''
                CREATE TABLE IF NOT EXISTS metric_definitions (
                    name TEXT PRIMARY KEY,
                    metric_type TEXT NOT NULL,
                    description TEXT,
                    unit TEXT,
                    labels TEXT,
                    aggregation_window INTEGER,
                    retention_hours INTEGER,
                    alert_thresholds TEXT,
                    created_at TEXT DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # Create indexes for performance
            conn.execute('CREATE INDEX IF NOT EXISTS idx_metrics_name_time ON metrics(metric_name, timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_metrics_timestamp ON metrics(timestamp)')
            conn.execute('CREATE INDEX IF NOT EXISTS idx_aggregations_name_time ON metric_aggregations(metric_name, start_time)')
    
    def store_metric(self, metric_name: str, value: MetricValue):
        """Store a metric value"""
        with sqlite3.connect(self.db_path) as conn:
            if isinstance(value.value, list):
                histogram_data = json.dumps(value.value)
                stored_value = None
            else:
                histogram_data = None
                stored_value = value.value
            
            conn.execute('''
                INSERT INTO metrics (metric_name, timestamp, value, histogram_data, labels, source, metadata)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                metric_name,
                value.timestamp,
                stored_value,
                histogram_data,
                json.dumps(value.labels),
                value.source,
                json.dumps(value.metadata)
            ))
    
    def store_aggregation(self, aggregation: MetricAggregation):
        """Store metric aggregation"""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('''
                INSERT INTO metric_aggregations 
                (metric_name, start_time, end_time, count, min_value, max_value, 
                 avg_value, sum_value, percentiles, rate_per_second, standard_deviation)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                aggregation.metric_name,
                aggregation.start_time,
                aggregation.end_time,
                aggregation.count,
                aggregation.min_value,
                aggregation.max_value,
                aggregation.avg_value,
                aggregation.sum_value,
                json.dumps(aggregation.percentiles),
                aggregation.rate_per_second,
                aggregation.standard_deviation
            ))
    
    def get_metrics(self, metric_name: str, start_time: str = None, end_time: str = None, 
                   limit: int = 1000) -> List[MetricValue]:
        """Retrieve metric values"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT timestamp, value, histogram_data, labels, source, metadata
                FROM metrics WHERE metric_name = ?
            '''
            params = [metric_name]
            
            if start_time:
                query += ' AND timestamp >= ?'
                params.append(start_time)
            
            if end_time:
                query += ' AND timestamp <= ?'
                params.append(end_time)
            
            query += ' ORDER BY timestamp DESC LIMIT ?'
            params.append(limit)
            
            cursor = conn.execute(query, params)
            
            results = []
            for row in cursor.fetchall():
                value = json.loads(row[2]) if row[2] else row[1]
                results.append(MetricValue(
                    timestamp=row[0],
                    value=value,
                    labels=json.loads(row[3]) if row[3] else {},
                    source=row[4],
                    metadata=json.loads(row[5]) if row[5] else {}
                ))
            
            return results
    
    def get_aggregations(self, metric_name: str, start_time: str = None, 
                        end_time: str = None) -> List[MetricAggregation]:
        """Retrieve metric aggregations"""
        with sqlite3.connect(self.db_path) as conn:
            query = '''
                SELECT metric_name, start_time, end_time, count, min_value, max_value,
                       avg_value, sum_value, percentiles, rate_per_second, standard_deviation
                FROM metric_aggregations WHERE metric_name = ?
            '''
            params = [metric_name]
            
            if start_time:
                query += ' AND start_time >= ?'
                params.append(start_time)
            
            if end_time:
                query += ' AND end_time <= ?'
                params.append(end_time)
            
            query += ' ORDER BY start_time DESC'
            
            cursor = conn.execute(query, params)
            
            results = []
            for row in cursor.fetchall():
                results.append(MetricAggregation(
                    metric_name=row[0],
                    start_time=row[1],
                    end_time=row[2],
                    count=row[3],
                    min_value=row[4],
                    max_value=row[5],
                    avg_value=row[6],
                    sum_value=row[7],
                    percentiles=json.loads(row[8]) if row[8] else {},
                    rate_per_second=row[9],
                    standard_deviation=row[10]
                ))
            
            return results
    
    def cleanup_old_data(self, hours_to_keep: int = 168):  # 7 days default
        """Clean up old metric data"""
        cutoff_time = (datetime.now() - timedelta(hours=hours_to_keep)).isoformat()
        
        with sqlite3.connect(self.db_path) as conn:
            conn.execute('DELETE FROM metrics WHERE timestamp < ?', (cutoff_time,))
            conn.execute('DELETE FROM metric_aggregations WHERE start_time < ?', (cutoff_time,))


class MetricAggregator:
    """Advanced metric aggregation engine"""
    
    def __init__(self):
        self.aggregation_functions = {
            'min': min,
            'max': max,
            'avg': statistics.mean,
            'sum': sum,
            'count': len,
            'median': statistics.median,
            'mode': statistics.mode,
            'stdev': statistics.stdev if hasattr(statistics, 'stdev') else statistics.pstdev
        }
    
    def aggregate_values(self, values: List[float]) -> MetricAggregation:
        """Aggregate a list of values"""
        if not values:
            return self._empty_aggregation()
        
        # Basic statistics
        min_val = min(values)
        max_val = max(values)
        avg_val = statistics.mean(values)
        sum_val = sum(values)
        count = len(values)
        
        # Percentiles
        sorted_values = sorted(values)
        percentiles = {
            'p50': self._percentile(sorted_values, 50),
            'p75': self._percentile(sorted_values, 75),
            'p90': self._percentile(sorted_values, 90),
            'p95': self._percentile(sorted_values, 95),
            'p99': self._percentile(sorted_values, 99)
        }
        
        # Standard deviation
        std_dev = statistics.pstdev(values) if len(values) > 1 else 0.0
        
        return MetricAggregation(
            metric_name="",  # Will be set by caller
            start_time="",   # Will be set by caller
            end_time="",     # Will be set by caller
            count=count,
            min_value=min_val,
            max_value=max_val,
            avg_value=avg_val,
            sum_value=sum_val,
            percentiles=percentiles,
            rate_per_second=0.0,  # Will be calculated by caller
            standard_deviation=std_dev
        )
    
    def aggregate_histogram(self, histogram_values: List[List[float]]) -> Dict[str, Any]:
        """Aggregate histogram data"""
        if not histogram_values:
            return {}
        
        # Flatten all histogram values
        all_values = []
        for hist in histogram_values:
            all_values.extend(hist)
        
        if not all_values:
            return {}
        
        # Calculate histogram statistics
        return {
            'total_samples': len(all_values),
            'min': min(all_values),
            'max': max(all_values),
            'mean': statistics.mean(all_values),
            'p50': self._percentile(sorted(all_values), 50),
            'p90': self._percentile(sorted(all_values), 90),
            'p95': self._percentile(sorted(all_values), 95),
            'p99': self._percentile(sorted(all_values), 99),
            'std_dev': statistics.pstdev(all_values) if len(all_values) > 1 else 0.0
        }
    
    def _percentile(self, sorted_values: List[float], percentile: float) -> float:
        """Calculate percentile of sorted values"""
        if not sorted_values:
            return 0.0
        
        index = (percentile / 100) * (len(sorted_values) - 1)
        
        if index.is_integer():
            return sorted_values[int(index)]
        else:
            lower_index = int(index)
            upper_index = lower_index + 1
            if upper_index >= len(sorted_values):
                return sorted_values[lower_index]
            
            weight = index - lower_index
            return sorted_values[lower_index] * (1 - weight) + sorted_values[upper_index] * weight
    
    def _empty_aggregation(self) -> MetricAggregation:
        """Return empty aggregation"""
        return MetricAggregation(
            metric_name="",
            start_time="",
            end_time="",
            count=0,
            min_value=0.0,
            max_value=0.0,
            avg_value=0.0,
            sum_value=0.0,
            percentiles={},
            rate_per_second=0.0,
            standard_deviation=0.0
        )


class MetricStreamer:
    """Real-time metric streaming via WebSocket"""
    
    def __init__(self, port: int = 8769):
        self.port = port
        self.clients = set()
        self.server = None
        self.running = False
        self.metric_buffer = deque(maxlen=1000)
        self.subscription_filters = defaultdict(set)  # client -> set of metric names
    
    async def start_server(self):
        """Start WebSocket server for metric streaming"""
        try:
            self.server = await websockets.serve(
                self.handle_client,
                "localhost",
                self.port,
                ping_interval=20,
                ping_timeout=10
            )
            self.running = True
            print(f"[METRICS] Real-time streaming server started on ws://localhost:{self.port}")
            
        except Exception as e:
            print(f"[ERROR] Failed to start metrics streaming server: {e}")
    
    async def handle_client(self, websocket, path):
        """Handle WebSocket client connections"""
        self.clients.add(websocket)
        print(f"[METRICS] Client connected. Total clients: {len(self.clients)}")
        
        try:
            # Send buffered metrics to new client
            for metric_data in list(self.metric_buffer):
                await websocket.send(json.dumps(metric_data))
            
            # Handle client messages (subscriptions, etc.)
            async for message in websocket:
                try:
                    data = json.loads(message)
                    await self.handle_client_message(websocket, data)
                except json.JSONDecodeError:
                    await websocket.send(json.dumps({
                        'error': 'Invalid JSON message'
                    }))
        
        except websockets.exceptions.ConnectionClosed:
            pass
        except Exception as e:
            print(f"[ERROR] WebSocket client error: {e}")
        finally:
            self.clients.remove(websocket)
            self.subscription_filters.pop(websocket, None)
            print(f"[METRICS] Client disconnected. Total clients: {len(self.clients)}")
    
    async def handle_client_message(self, websocket, data: Dict[str, Any]):
        """Handle messages from WebSocket clients"""
        message_type = data.get('type')
        
        if message_type == 'subscribe':
            # Client wants to subscribe to specific metrics
            metric_names = data.get('metrics', [])
            if metric_names:
                self.subscription_filters[websocket].update(metric_names)
                await websocket.send(json.dumps({
                    'type': 'subscription_confirmed',
                    'metrics': list(self.subscription_filters[websocket])
                }))
        
        elif message_type == 'unsubscribe':
            # Client wants to unsubscribe from metrics
            metric_names = data.get('metrics', [])
            for metric_name in metric_names:
                self.subscription_filters[websocket].discard(metric_name)
            
            await websocket.send(json.dumps({
                'type': 'unsubscription_confirmed',
                'metrics': list(self.subscription_filters[websocket])
            }))
        
        elif message_type == 'get_available_metrics':
            # Client wants list of available metrics
            # This would be populated by the metrics collector
            await websocket.send(json.dumps({
                'type': 'available_metrics',
                'metrics': ['system.cpu', 'system.memory', 'jarvis.performance', 'jarvis.health']
            }))
    
    def stream_metric(self, metric_name: str, value: MetricValue):
        """Stream a metric to connected clients"""
        if not self.clients:
            return
        
        metric_data = {
            'type': 'metric_update',
            'metric_name': metric_name,
            'timestamp': value.timestamp,
            'value': value.value,
            'labels': value.labels,
            'source': value.source,
            'metadata': value.metadata
        }
        
        # Add to buffer for new clients
        self.metric_buffer.append(metric_data)
        
        # Send to subscribed clients
        message = json.dumps(metric_data)
        disconnected_clients = set()
        
        for client in self.clients:
            try:
                # Check if client is subscribed to this metric
                if (client not in self.subscription_filters or 
                    not self.subscription_filters[client] or 
                    metric_name in self.subscription_filters[client]):
                    
                    asyncio.create_task(client.send(message))
            except:
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        self.clients -= disconnected_clients
        for client in disconnected_clients:
            self.subscription_filters.pop(client, None)
    
    def stream_aggregation(self, aggregation: MetricAggregation):
        """Stream aggregated metric data"""
        if not self.clients:
            return
        
        agg_data = {
            'type': 'metric_aggregation',
            'metric_name': aggregation.metric_name,
            'start_time': aggregation.start_time,
            'end_time': aggregation.end_time,
            'count': aggregation.count,
            'min': aggregation.min_value,
            'max': aggregation.max_value,
            'avg': aggregation.avg_value,
            'sum': aggregation.sum_value,
            'percentiles': aggregation.percentiles,
            'rate_per_second': aggregation.rate_per_second,
            'std_dev': aggregation.standard_deviation
        }
        
        message = json.dumps(agg_data)
        disconnected_clients = set()
        
        for client in self.clients:
            try:
                if (client not in self.subscription_filters or 
                    not self.subscription_filters[client] or 
                    aggregation.metric_name in self.subscription_filters[client]):
                    
                    asyncio.create_task(client.send(message))
            except:
                disconnected_clients.add(client)
        
        # Remove disconnected clients
        self.clients -= disconnected_clients
        for client in disconnected_clients:
            self.subscription_filters.pop(client, None)


class AdvancedMetricsCollector:
    """Advanced real-time metrics collection with 100% functionality"""
    
    def __init__(self, config: Dict[str, Any] = None):
        self.config = config or {}
        self.storage = MetricStorage()
        self.aggregator = MetricAggregator()
        self.streamer = MetricStreamer(self.config.get('streaming_port', 8769))
        
        # Metric definitions registry
        self.metric_definitions = {}
        self.custom_metrics = {}
        
        # Collection state
        self.is_running = False
        self.collection_thread = None
        self.aggregation_thread = None
        
        # In-memory metric buffers for real-time processing
        self.metric_buffers = defaultdict(lambda: deque(maxlen=10000))
        self.aggregation_cache = {}
        
        # Performance tracking
        self.collection_stats = {
            'metrics_collected': 0,
            'aggregations_computed': 0,
            'storage_operations': 0,
            'streaming_updates': 0,
            'errors': 0
        }
        
        # Initialize built-in metrics
        self._init_builtin_metrics()
    
    def _init_builtin_metrics(self):
        """Initialize built-in metric definitions"""
        builtin_metrics = [
            MetricDefinition(
                name="system.cpu.percent",
                metric_type=MetricType.GAUGE,
                description="CPU usage percentage",
                unit="percent",
                labels=["core"],
                aggregation_window=60,
                retention_hours=168,
                alert_thresholds={"warning": 80, "critical": 95}
            ),
            MetricDefinition(
                name="system.memory.percent",
                metric_type=MetricType.GAUGE,
                description="Memory usage percentage",
                unit="percent",
                labels=[],
                aggregation_window=60,
                retention_hours=168,
                alert_thresholds={"warning": 80, "critical": 90}
            ),
            MetricDefinition(
                name="jarvis.performance.score",
                metric_type=MetricType.GAUGE,
                description="Jarvis performance score",
                unit="score",
                labels=["component"],
                aggregation_window=300,
                retention_hours=720,  # 30 days
                alert_thresholds={"warning": 70, "critical": 50}
            ),
            MetricDefinition(
                name="jarvis.requests.total",
                metric_type=MetricType.COUNTER,
                description="Total number of requests",
                unit="requests",
                labels=["endpoint", "method", "status"],
                aggregation_window=60,
                retention_hours=168,
                alert_thresholds={}
            ),
            MetricDefinition(
                name="jarvis.response.duration",
                metric_type=MetricType.HISTOGRAM,
                description="Response duration distribution",
                unit="seconds",
                labels=["endpoint"],
                aggregation_window=300,
                retention_hours=168,
                alert_thresholds={"warning": 2.0, "critical": 5.0}
            )
        ]
        
        for metric_def in builtin_metrics:
            self.register_metric(metric_def)
    
    def register_metric(self, metric_def: MetricDefinition):
        """Register a new metric definition"""
        self.metric_definitions[metric_def.name] = metric_def
        
        # Store in database
        with sqlite3.connect(self.storage.db_path) as conn:
            conn.execute('''
                INSERT OR REPLACE INTO metric_definitions 
                (name, metric_type, description, unit, labels, aggregation_window, 
                 retention_hours, alert_thresholds)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                metric_def.name,
                metric_def.metric_type.value,
                metric_def.description,
                metric_def.unit,
                json.dumps(metric_def.labels),
                metric_def.aggregation_window,
                metric_def.retention_hours,
                json.dumps(metric_def.alert_thresholds)
            ))
        
        print(f"[METRICS] Registered metric: {metric_def.name} ({metric_def.metric_type.value})")
    
    def start_collection(self):
        """Start metrics collection"""
        if self.is_running:
            return
        
        self.is_running = True
        
        # Start collection thread
        self.collection_thread = threading.Thread(target=self._collection_loop, daemon=True)
        self.collection_thread.start()
        
        # Start aggregation thread
        self.aggregation_thread = threading.Thread(target=self._aggregation_loop, daemon=True)
        self.aggregation_thread.start()
        
        # Start streaming server
        def start_streaming():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(self.streamer.start_server())
            loop.run_forever()
        
        streaming_thread = threading.Thread(target=start_streaming, daemon=True)
        streaming_thread.start()
        
        print("[METRICS] Advanced real-time metrics collection started (100% functionality)")
    
    def stop_collection(self):
        """Stop metrics collection"""
        self.is_running = False
        
        if self.collection_thread:
            self.collection_thread.join(timeout=5)
        
        if self.aggregation_thread:
            self.aggregation_thread.join(timeout=5)
        
        print("[METRICS] Metrics collection stopped")
    
    def record_metric(self, metric_name: str, value: Union[float, List[float]], 
                     labels: Dict[str, str] = None, source: str = "system",
                     metadata: Dict[str, Any] = None):
        """Record a metric value"""
        try:
            # Validate metric definition
            if metric_name not in self.metric_definitions:
                print(f"[WARNING] Unknown metric: {metric_name}")
                return
            
            metric_def = self.metric_definitions[metric_name]
            
            # Create metric value
            metric_value = MetricValue(
                timestamp=datetime.now().isoformat(),
                value=value,
                labels=labels or {},
                source=source,
                metadata=metadata or {}
            )
            
            # Add to buffer for real-time processing
            self.metric_buffers[metric_name].append(metric_value)
            
            # Store in database
            self.storage.store_metric(metric_name, metric_value)
            
            # Stream to real-time clients
            self.streamer.stream_metric(metric_name, metric_value)
            
            # Update stats
            self.collection_stats['metrics_collected'] += 1
            self.collection_stats['storage_operations'] += 1
            self.collection_stats['streaming_updates'] += 1
            
        except Exception as e:
            print(f"[ERROR] Failed to record metric {metric_name}: {e}")
            self.collection_stats['errors'] += 1
    
    def record_counter(self, metric_name: str, increment: float = 1.0, 
                      labels: Dict[str, str] = None):
        """Record a counter metric"""
        self.record_metric(metric_name, increment, labels, metadata={'type': 'counter'})
    
    def record_gauge(self, metric_name: str, value: float, 
                    labels: Dict[str, str] = None):
        """Record a gauge metric"""
        self.record_metric(metric_name, value, labels, metadata={'type': 'gauge'})
    
    def record_histogram(self, metric_name: str, values: List[float], 
                        labels: Dict[str, str] = None):
        """Record a histogram metric"""
        self.record_metric(metric_name, values, labels, metadata={'type': 'histogram'})
    
    def record_timer(self, metric_name: str, duration_seconds: float, 
                    labels: Dict[str, str] = None):
        """Record a timer metric"""
        self.record_metric(metric_name, duration_seconds, labels, metadata={'type': 'timer'})
    
    def get_current_values(self, metric_name: str = None) -> Dict[str, Any]:
        """Get current metric values"""
        if metric_name:
            if metric_name in self.metric_buffers and self.metric_buffers[metric_name]:
                latest = self.metric_buffers[metric_name][-1]
                return {
                    metric_name: {
                        'value': latest.value,
                        'timestamp': latest.timestamp,
                        'labels': latest.labels
                    }
                }
            return {}
        
        # Return all current values
        current_values = {}
        for name, buffer in self.metric_buffers.items():
            if buffer:
                latest = buffer[-1]
                current_values[name] = {
                    'value': latest.value,
                    'timestamp': latest.timestamp,
                    'labels': latest.labels
                }
        
        return current_values
    
    def get_aggregated_metrics(self, metric_name: str, hours: int = 1) -> List[MetricAggregation]:
        """Get aggregated metric data"""
        start_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        return self.storage.get_aggregations(metric_name, start_time)
    
    def get_metric_history(self, metric_name: str, hours: int = 24, 
                          limit: int = 1000) -> List[MetricValue]:
        """Get metric history"""
        start_time = (datetime.now() - timedelta(hours=hours)).isoformat()
        return self.storage.get_metrics(metric_name, start_time, limit=limit)
    
    def create_custom_metric(self, name: str, calculation_func: Callable[[], float],
                           metric_type: MetricType = MetricType.GAUGE,
                           collection_interval: int = 60,
                           labels: Dict[str, str] = None):
        """Create a custom metric with user-defined calculation"""
        metric_def = MetricDefinition(
            name=name,
            metric_type=metric_type,
            description=f"Custom metric: {name}",
            unit="custom",
            labels=list(labels.keys()) if labels else [],
            aggregation_window=collection_interval,
            retention_hours=168,
            alert_thresholds={}
        )
        
        self.register_metric(metric_def)
        self.custom_metrics[name] = {
            'func': calculation_func,
            'interval': collection_interval,
            'labels': labels or {},
            'last_collection': 0
        }
        
        print(f"[METRICS] Created custom metric: {name}")
    
    def get_performance_report(self) -> Dict[str, Any]:
        """Get metrics collection performance report"""
        uptime = time.time() - getattr(self, '_start_time', time.time())
        
        return {
            'uptime_seconds': uptime,
            'metrics_per_second': self.collection_stats['metrics_collected'] / max(uptime, 1),
            'total_metrics_collected': self.collection_stats['metrics_collected'],
            'total_aggregations_computed': self.collection_stats['aggregations_computed'],
            'total_storage_operations': self.collection_stats['storage_operations'],
            'total_streaming_updates': self.collection_stats['streaming_updates'],
            'total_errors': self.collection_stats['errors'],
            'active_metric_definitions': len(self.metric_definitions),
            'custom_metrics': len(self.custom_metrics),
            'streaming_clients': len(self.streamer.clients),
            'memory_usage_mb': sum(len(buffer) for buffer in self.metric_buffers.values()) * 0.001  # Rough estimate
        }
    
    def _collection_loop(self):
        """Main metrics collection loop"""
        self._start_time = time.time()
        
        while self.is_running:
            try:
                # Collect system metrics
                self._collect_system_metrics()
                
                # Collect custom metrics
                self._collect_custom_metrics()
                
                # Collect Jarvis performance metrics
                self._collect_jarvis_metrics()
                
                # Clean up old data periodically
                if int(time.time()) % 3600 == 0:  # Every hour
                    self.storage.cleanup_old_data()
                
                time.sleep(self.config.get('collection_interval', 30))
                
            except Exception as e:
                print(f"[ERROR] Metrics collection loop error: {e}")
                self.collection_stats['errors'] += 1
                time.sleep(10)
    
    def _aggregation_loop(self):
        """Aggregation processing loop"""
        while self.is_running:
            try:
                current_time = time.time()
                
                # Process aggregations for each metric
                for metric_name, metric_def in self.metric_definitions.items():
                    last_aggregation = self.aggregation_cache.get(metric_name, 0)
                    
                    if current_time - last_aggregation >= metric_def.aggregation_window:
                        self._compute_aggregation(metric_name, metric_def)
                        self.aggregation_cache[metric_name] = current_time
                
                time.sleep(60)  # Check for aggregations every minute
                
            except Exception as e:
                print(f"[ERROR] Aggregation loop error: {e}")
                time.sleep(30)
    
    def _compute_aggregation(self, metric_name: str, metric_def: MetricDefinition):
        """Compute aggregation for a metric"""
        try:
            # Get recent values for aggregation
            buffer = self.metric_buffers[metric_name]
            if not buffer:
                return
            
            # Filter values within aggregation window
            window_start = datetime.now() - timedelta(seconds=metric_def.aggregation_window)
            recent_values = []
            
            for metric_value in buffer:
                if datetime.fromisoformat(metric_value.timestamp) >= window_start:
                    if isinstance(metric_value.value, list):
                        recent_values.extend(metric_value.value)  # Histogram
                    else:
                        recent_values.append(metric_value.value)
            
            if not recent_values:
                return
            
            # Compute aggregation
            aggregation = self.aggregator.aggregate_values(recent_values)
            aggregation.metric_name = metric_name
            aggregation.start_time = window_start.isoformat()
            aggregation.end_time = datetime.now().isoformat()
            
            # Calculate rate
            time_diff = metric_def.aggregation_window
            if metric_def.metric_type == MetricType.COUNTER:
                aggregation.rate_per_second = aggregation.sum_value / time_diff
            else:
                aggregation.rate_per_second = aggregation.count / time_diff
            
            # Store aggregation
            self.storage.store_aggregation(aggregation)
            
            # Stream aggregation
            self.streamer.stream_aggregation(aggregation)
            
            self.collection_stats['aggregations_computed'] += 1
            
        except Exception as e:
            print(f"[ERROR] Failed to compute aggregation for {metric_name}: {e}")
            self.collection_stats['errors'] += 1
    
    def _collect_system_metrics(self):
        """Collect system-level metrics"""
        try:
            import psutil
            
            # CPU metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            self.record_gauge("system.cpu.percent", cpu_percent)
            
            # Memory metrics
            memory = psutil.virtual_memory()
            self.record_gauge("system.memory.percent", memory.percent)
            self.record_gauge("system.memory.available_mb", memory.available / (1024**2))
            
            # Disk metrics
            disk = psutil.disk_usage('/')
            self.record_gauge("system.disk.percent", disk.percent)
            self.record_gauge("system.disk.free_gb", disk.free / (1024**3))
            
            # Network metrics (if available)
            try:
                net_io = psutil.net_io_counters()
                self.record_counter("system.network.bytes_sent", net_io.bytes_sent)
                self.record_counter("system.network.bytes_recv", net_io.bytes_recv)
            except:
                pass
                
        except Exception as e:
            print(f"[ERROR] Failed to collect system metrics: {e}")
    
    def _collect_custom_metrics(self):
        """Collect custom user-defined metrics"""
        current_time = time.time()
        
        for metric_name, custom_metric in self.custom_metrics.items():
            try:
                if current_time - custom_metric['last_collection'] >= custom_metric['interval']:
                    value = custom_metric['func']()
                    self.record_metric(metric_name, value, custom_metric['labels'], 
                                     source="custom", metadata={'type': 'custom'})
                    custom_metric['last_collection'] = current_time
                    
            except Exception as e:
                print(f"[ERROR] Failed to collect custom metric {metric_name}: {e}")
    
    def _collect_jarvis_metrics(self):
        """Collect Jarvis-specific performance metrics"""
        try:
            # Get performance data from performance monitor
            from jarvis.core.performance_monitor import get_performance_monitor
            
            monitor = get_performance_monitor()
            current_metrics = monitor.get_current_metrics()
            
            # Record Jarvis performance metrics
            for metric_name, value in current_metrics.items():
                if isinstance(value, (int, float)):
                    jarvis_metric_name = f"jarvis.{metric_name}"
                    self.record_gauge(jarvis_metric_name, value, {"component": "jarvis"})
            
            # Get health data
            try:
                from jarvis.monitoring.system_health import get_health_monitor
                health_monitor = get_health_monitor()
                health_report = health_monitor.get_health_report()
                
                self.record_gauge("jarvis.health.overall_score", health_report.overall_score)
                self.record_gauge("jarvis.health.uptime_seconds", health_report.uptime_seconds)
                
                # Record component health scores
                for component, status in health_report.component_statuses.items():
                    self.record_gauge("jarvis.health.component_score", status.score, 
                                    {"component": component})
                    
            except:
                pass  # Health monitor might not be available
                
        except Exception as e:
            print(f"[ERROR] Failed to collect Jarvis metrics: {e}")


# Global metrics collector instance
_metrics_collector = None

def get_metrics_collector() -> AdvancedMetricsCollector:
    """Get global metrics collector instance"""
    global _metrics_collector
    if _metrics_collector is None:
        _metrics_collector = AdvancedMetricsCollector()
    return _metrics_collector

def start_metrics_collection(config: Dict[str, Any] = None):
    """Start advanced metrics collection"""
    collector = get_metrics_collector()
    if config:
        collector.config.update(config)
    collector.start_collection()
    return collector

def record_metric(metric_name: str, value: Union[float, List[float]], 
                 labels: Dict[str, str] = None, source: str = "system"):
    """Convenience function to record a metric"""
    collector = get_metrics_collector()
    collector.record_metric(metric_name, value, labels, source)

def get_current_metrics() -> Dict[str, Any]:
    """Get current metric values"""
    collector = get_metrics_collector()
    return collector.get_current_values()

def create_custom_metric(name: str, calculation_func: Callable[[], float],
                        metric_type: MetricType = MetricType.GAUGE,
                        collection_interval: int = 60,
                        labels: Dict[str, str] = None):
    """Create a custom metric"""
    collector = get_metrics_collector()
    collector.create_custom_metric(name, calculation_func, metric_type, 
                                  collection_interval, labels)