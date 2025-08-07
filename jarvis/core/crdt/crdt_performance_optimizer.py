"""
CRDT Performance Optimizer
Phase 5 - Advanced Features: Performance optimization and monitoring

This module implements performance optimization features for CRDT operations
including delta compression, lazy synchronization, and conflict batching.
"""

import json
import time
import gzip
import threading
import logging
from typing import Dict, List, Optional, Any, Tuple, Set
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from pathlib import Path
import hashlib
import heapq
from collections import defaultdict
import os

# Try to import psutil, fall back to basic resource monitoring if not available
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False
    import resource

logger = logging.getLogger(__name__)


@dataclass
class PerformanceMetrics:
    """Performance metrics for CRDT operations"""
    operation_type: str
    latency_ms: float
    memory_usage_mb: float
    cpu_usage_percent: float
    timestamp: datetime
    success: bool
    payload_size_bytes: int = 0
    compression_ratio: float = 1.0


@dataclass
class CompressionResult:
    """Result of compression operation"""
    original_size: int
    compressed_size: int
    compression_ratio: float
    compression_time_ms: float
    algorithm: str


class DeltaCompressor:
    """Compress CRDT deltas for efficient transmission"""
    
    def __init__(self):
        self.compression_cache = {}
        self.algorithm_preference = ["gzip", "lz4", "none"]
        
    def compress_delta(self, delta_data: Any, algorithm: str = "gzip") -> CompressionResult:
        """Compress delta data using specified algorithm"""
        start_time = time.time()
        
        # Serialize delta data
        serialized = json.dumps(delta_data, default=str).encode('utf-8')
        original_size = len(serialized)
        
        if algorithm == "gzip":
            compressed = gzip.compress(serialized)
        elif algorithm == "lz4":
            # LZ4 compression (fallback to gzip if not available)
            try:
                import lz4.frame
                compressed = lz4.frame.compress(serialized)
            except ImportError:
                logger.warning("LZ4 not available, falling back to gzip")
                compressed = gzip.compress(serialized)
                algorithm = "gzip"
        else:
            # No compression
            compressed = serialized
        
        compressed_size = len(compressed)
        compression_time = (time.time() - start_time) * 1000
        
        return CompressionResult(
            original_size=original_size,
            compressed_size=compressed_size,
            compression_ratio=original_size / compressed_size if compressed_size > 0 else 1.0,
            compression_time_ms=compression_time,
            algorithm=algorithm
        )
    
    def decompress_delta(self, compressed_data: bytes, algorithm: str) -> Any:
        """Decompress delta data"""
        if algorithm == "gzip":
            decompressed = gzip.decompress(compressed_data)
        elif algorithm == "lz4":
            try:
                import lz4.frame
                decompressed = lz4.frame.decompress(compressed_data)
            except ImportError:
                # Try gzip as fallback
                decompressed = gzip.decompress(compressed_data)
        else:
            decompressed = compressed_data
        
        return json.loads(decompressed.decode('utf-8'))
    
    def get_optimal_algorithm(self, data_size: int) -> str:
        """Get optimal compression algorithm based on data size"""
        if data_size < 1024:  # < 1KB
            return "none"  # No compression for small data
        elif data_size < 10240:  # < 10KB
            return "lz4"  # Fast compression for medium data
        else:
            return "gzip"  # Better compression for large data


class LazySynchronizer:
    """Implement lazy synchronization with adaptive intervals"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.sync_intervals = {}
        self.last_sync_times = {}
        self.activity_counters = defaultdict(int)
        self.sync_queue = []
        self.running = False
        self.sync_thread = None
        
        # Configuration
        self.min_interval = 1  # 1 second minimum
        self.max_interval = 3600  # 1 hour maximum
        self.base_interval = 60  # 1 minute base interval
        self.activity_threshcurrent_high = 100
        self.activity_threshcurrent_low = 10
        
    def start(self):
        """Start lazy synchronization"""
        if not self.running:
            self.running = True
            self.sync_thread = threading.Thread(target=self._sync_worker, daemon=True)
            self.sync_thread.start()
            logger.info("Lazy synchronizer started")
    
    def stop(self):
        """Stop lazy synchronization"""
        self.running = False
        if self.sync_thread:
            self.sync_thread.join(timeout=5)
        logger.info("Lazy synchronizer stopped")
    
    def record_activity(self, peer_node: str, activity_count: int = 1):
        """Record activity for adaptive interval calculation"""
        self.activity_counters[peer_node] += activity_count
    
    def schedule_sync(self, peer_node: str, priority: str = "normal"):
        """Schedule synchronization with adaptive timing"""
        current_time = time.time()
        
        # Calculate adaptive interval
        activity_count = self.activity_counters.get(peer_node, 0)
        interval = self._calculate_adaptive_interval(activity_count, priority)
        
        # Schedule sync
        sync_time = current_time + interval
        heapq.heappush(self.sync_queue, (sync_time, peer_node, priority))
        
        logger.debug(f"Scheduled sync with {peer_node} in {interval}s (activity: {activity_count})")
    
    def _calculate_adaptive_interval(self, activity_count: int, priority: str) -> float:
        """Calculate adaptive sync interval based on activity"""
        base = self.base_interval
        
        # Adjust based on activity
        if activity_count > self.activity_threshcurrent_high:
            base = base / 4  # High activity - sync more frequently
        elif activity_count > self.activity_threshcurrent_low:
            base = base / 2  # Medium activity - sync moderately
        elif activity_count < 5:
            base = base * 2  # Low activity - sync less frequently
        
        # Adjust based on priority
        priority_multipliers = {
            "critical": 0.1,
            "high": 0.5,
            "normal": 1.0,
            "low": 2.0
        }
        base *= priority_multipliers.get(priority, 1.0)
        
        # Enforce bounds
        return max(self.min_interval, min(self.max_interval, base))
    
    def _sync_worker(self):
        """Background worker for lazy synchronization"""
        while self.running:
            current_time = time.time()
            
            # Process scheduled syncs
            while self.sync_queue and self.sync_queue[0][0] <= current_time:
                sync_time, peer_node, priority = heapq.heappop(self.sync_queue)
                
                try:
                    self._perform_sync(peer_node, priority)
                    self.last_sync_times[peer_node] = current_time
                    
                    # Reset activity counter after sync
                    self.activity_counters[peer_node] = 0
                    
                except Exception as e:
                    logger.error(f"Sync failed with {peer_node}: {e}")
            
            # Sleep briefly before next check
            time.sleep(1)
    
    def _perform_sync(self, peer_node: str, priority: str):
        """Perform actual synchronization (placeholder)"""
        # This would integrate with the actual CRDT network layer
        logger.debug(f"Performing {priority} sync with {peer_node}")
        time.sleep(0.1)  # Simulate sync operation


class ConflictBatcher:
    """Batch conflicts for efficient resolution"""
    
    def __init__(self, batch_size: int = 10, timeout_seconds: float = 5.0):
        self.batch_size = batch_size
        self.timeout_seconds = timeout_seconds
        self.pending_conflicts = []
        self.batch_timer = None
        self.resolution_handlers = {}
        
    def add_conflict(self, conflict: Any):
        """Add conflict to batch for resolution"""
        self.pending_conflicts.append({
            'conflict': conflict,
            'timestamp': time.time()
        })
        
        # Start timer if this is the first conflict
        if len(self.pending_conflicts) == 1:
            self._start_batch_timer()
        
        # Process immediately if batch is full
        if len(self.pending_conflicts) >= self.batch_size:
            self._process_batch()
    
    def _start_batch_timer(self):
        """Start timer for batch timeout"""
        if self.batch_timer:
            self.batch_timer.cancel()
        
        self.batch_timer = threading.Timer(self.timeout_seconds, self._process_batch)
        self.batch_timer.start()
    
    def _process_batch(self):
        """Process batched conflicts"""
        if not self.pending_conflicts:
            return
        
        # Cancel timer
        if self.batch_timer:
            self.batch_timer.cancel()
            self.batch_timer = None
        
        # Group conflicts by type for efficient processing
        conflict_groups = defaultdict(list)
        for item in self.pending_conflicts:
            conflict = item['conflict']
            conflict_type = getattr(conflict, 'conflict_type', 'unknown')
            conflict_groups[conflict_type].append(item)
        
        # Process each group
        for conflict_type, conflicts in conflict_groups.items():
            try:
                self._resolve_conflict_group(conflict_type, conflicts)
            except Exception as e:
                logger.error(f"Failed to resolve {conflict_type} conflicts: {e}")
        
        # Clear processed conflicts
        self.pending_conflicts.clear()
    
    def _resolve_conflict_group(self, conflict_type: str, conflicts: List[Dict]):
        """Resolve a group of similar conflicts"""
        logger.info(f"Resolving batch of {len(conflicts)} {conflict_type} conflicts")
        
        # Sort by timestamp for consistent ordering
        conflicts.sort(key=lambda x: x['timestamp'])
        
        # Apply batch resolution logic
        for item in conflicts:
            conflict = item['conflict']
            # Placeholder for actual conflict resolution
            logger.debug(f"Resolved conflict: {conflict}")


class PerformanceMonitor:
    """Monitor CRDT performance and collect metrics"""
    
    def __init__(self):
        self.metrics = []
        self.baseline_metrics = {}
        self.monitoring_active = False
        self.monitoring_thread = None
        
    def start_monitoring(self):
        """Start performance monitoring"""
        if not self.monitoring_active:
            self.monitoring_active = True
            self.monitoring_thread = threading.Thread(target=self._monitoring_worker, daemon=True)
            self.monitoring_thread.start()
            logger.info("Performance monitoring started")
    
    def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
        if self.monitoring_thread:
            self.monitoring_thread.join(timeout=5)
        logger.info("Performance monitoring stopped")
    
    def record_metric(self, metric: PerformanceMetrics):
        """Record a performance metric"""
        self.metrics.append(metric)
        
        # Keep only recent metrics (last 1000)
        if len(self.metrics) > 1000:
            self.metrics = self.metrics[-1000:]
    
    def measure_operation(self, operation_type: str, operation_func, *args, **kwargs):
        """Measure performance of a CRDT operation"""
        start_time = time.time()
        
        # Memory and CPU measurement (with fallback)
        start_memory = 0
        start_cpu = 0
        
        if PSUTIL_AVAILABLE:
            start_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
            start_cpu = psutil.cpu_percent()
        else:
            # Fallback to basic resource monitoring
            try:
                start_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024  # KB to MB
            except:
                start_memory = 0
        
        success = False
        result = None
        payload_size = 0
        
        try:
            result = operation_func(*args, **kwargs)
            success = True
            
            # Estimate payload size
            if hasattr(result, '__sizeof__'):
                payload_size = result.__sizeof__()
            
        except Exception as e:
            logger.error(f"Operation {operation_type} failed: {e}")
            
        finally:
            end_time = time.time()
            
            # End measurements (with fallback)
            end_memory = 0
            end_cpu = 0
            
            if PSUTIL_AVAILABLE:
                end_memory = psutil.Process().memory_info().rss / 1024 / 1024  # MB
                end_cpu = psutil.cpu_percent()
            else:
                try:
                    end_memory = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024  # KB to MB
                except:
                    end_memory = start_memory
            
            metric = PerformanceMetrics(
                operation_type=operation_type,
                latency_ms=(end_time - start_time) * 1000,
                memory_usage_mb=max(0, end_memory - start_memory),
                cpu_usage_percent=max(0, end_cpu - start_cpu),
                timestamp=datetime.utcnow(),
                success=success,
                payload_size_bytes=payload_size
            )
            
            self.record_metric(metric)
        
        return result
    
    def get_performance_summary(self, operation_type: Optional[str] = None) -> Dict[str, Any]:
        """Get performance summary for operations"""
        relevant_metrics = self.metrics
        
        if operation_type:
            relevant_metrics = [m for m in self.metrics if m.operation_type == operation_type]
        
        if not relevant_metrics:
            return {"error": "No metrics available"}
        
        latencies = [m.latency_ms for m in relevant_metrics]
        memory_usage = [m.memory_usage_mb for m in relevant_metrics]
        cpu_usage = [m.cpu_usage_percent for m in relevant_metrics]
        success_rate = sum(1 for m in relevant_metrics if m.success) / len(relevant_metrics)
        
        return {
            "total_operations": len(relevant_metrics),
            "success_rate": success_rate,
            "latency": {
                "avg_ms": sum(latencies) / len(latencies),
                "min_ms": min(latencies),
                "max_ms": max(latencies),
                "p95_ms": sorted(latencies)[int(len(latencies) * 0.95)] if latencies else 0
            },
            "memory": {
                "avg_mb": sum(memory_usage) / len(memory_usage),
                "peak_mb": max(memory_usage)
            },
            "cpu": {
                "avg_percent": sum(cpu_usage) / len(cpu_usage),
                "peak_percent": max(cpu_usage)
            }
        }
    
    def _monitoring_worker(self):
        """Background worker for continuous monitoring"""
        while self.monitoring_active:
            try:
                # Collect system metrics (with fallback)
                if PSUTIL_AVAILABLE:
                    memory_info = psutil.virtual_memory()
                    cpu_percent = psutil.cpu_percent()
                    
                    # Log system health periodically
                    if len(self.metrics) % 100 == 0:
                        logger.debug(f"System: CPU {cpu_percent}%, Memory {memory_info.percent}%")
                else:
                    # Basic monitoring without psutil
                    if len(self.metrics) % 100 == 0:
                        logger.debug("System monitoring (basic mode)")
                
            except Exception as e:
                logger.error(f"Monitoring error: {e}")
            
            time.sleep(10)  # Monitor every 10 seconds


class CRDTPerformanceOptimizer:
    """Main coordinator for CRDT performance optimization"""
    
    def __init__(self, node_id: str):
        self.node_id = node_id
        self.compressor = DeltaCompressor()
        self.lazy_sync = LazySynchronizer(node_id)
        self.conflict_batcher = ConflictBatcher()
        self.performance_monitor = PerformanceMonitor()
        
        # Configuration
        self.optimization_enabled = True
        self.compression_threshold = 1024  # Compress deltas > 1KB
        
    def start(self):
        """Start all optimization components"""
        if self.optimization_enabled:
            self.lazy_sync.start()
            self.performance_monitor.start_monitoring()
            logger.info("CRDT performance optimization started")
    
    def stop(self):
        """Stop all optimization components"""
        self.lazy_sync.stop()
        self.performance_monitor.stop_monitoring()
        logger.info("CRDT performance optimization stopped")
    
    def optimize_delta_transmission(self, delta_data: Any) -> Tuple[bytes, str]:
        """Optimize delta for transmission"""
        # Determine if compression is beneficial
        serialized_size = len(json.dumps(delta_data, default=str).encode('utf-8'))
        
        if serialized_size < self.compression_threshold:
            # Skip compression for small deltas
            return json.dumps(delta_data, default=str).encode('utf-8'), "none"
        
        # Use optimal compression
        algorithm = self.compressor.get_optimal_algorithm(serialized_size)
        compression_result = self.compressor.compress_delta(delta_data, algorithm)
        
        logger.debug(f"Compressed delta: {compression_result.compression_ratio:.2f}x reduction")
        
        return json.dumps(delta_data, default=str).encode('utf-8'), algorithm
    
    def schedule_optimized_sync(self, peer_node: str, activity_level: str = "normal"):
        """Schedule sync with optimization"""
        priority_map = {
            "high": "high",
            "normal": "normal", 
            "low": "low"
        }
        
        priority = priority_map.get(activity_level, "normal")
        self.lazy_sync.schedule_sync(peer_node, priority)
    
    def batch_conflict_resolution(self, conflict: Any):
        """Add conflict to batch for optimized resolution"""
        self.conflict_batcher.add_conflict(conflict)
    
    def get_optimization_status(self) -> Dict[str, Any]:
        """Get current optimization status"""
        return {
            "enabled": self.optimization_enabled,
            "lazy_sync_active": self.lazy_sync.running,
            "monitoring_active": self.performance_monitor.monitoring_active,
            "performance_summary": self.performance_monitor.get_performance_summary(),
            "sync_queue_size": len(self.lazy_sync.sync_queue),
            "pending_conflicts": len(self.conflict_batcher.pending_conflicts)
        }