"""
Verification Queue Optimizer for Jarvis-V0.19
Optimizes verification processing for high-throughput scenarios
"""

import time
import threading
import queue
from typing import Dict, Any, List, Optional
from datetime import datetime, timedelta
import logging
from concurrent.futures import ThreadPoolExecutor, as_completed

from .data_verifier import get_verifier

class VerificationOptimizer:
    """Optimizes verification queue processing for better throughput"""
    
    def __init__(self, max_workers: int = 4, batch_size: int = 10):
        self.max_workers = max_workers
        self.batch_size = batch_size
        self.verifier = get_verifier()
        self.is_running = False
        self.worker_thread = None
        self.stats = {
            'processed': 0,
            'successful': 0,
            'failed': 0,
            'start_time': None,
            'throughput': 0.0
        }
        
    def start_optimization(self):
        """Start the verification optimization process"""
        if self.is_running:
            return
            
        self.is_running = True
        self.stats['start_time'] = time.time()
        self.worker_thread = threading.Thread(target=self._optimization_worker, daemon=True)
        self.worker_thread.start()
        print("[OPTIMIZE] Verification optimizer started")
        
    def stop_optimization(self):
        """Stop the verification optimization process"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        print("[OPTIMIZE] Verification optimizer stopped")
        
    def _optimization_worker(self):
        """Main optimization worker loop"""
        while self.is_running:
            try:
                # Get pending verifications
                pending_items = self._get_pending_verifications()
                
                if not pending_items:
                    time.sleep(5)  # Wait if no pending items
                    continue
                
                # Process in batches
                batches = self._create_batches(pending_items, self.batch_size)
                
                for batch in batches:
                    if not self.is_running:
                        break
                        
                    self._process_batch_concurrent(batch)
                    
                # Update throughput statistics
                self._update_stats()
                
                # Brief pause between batch cycles
                time.sleep(1)
                
            except Exception as e:
                logging.error(f"Error in verification optimizer: {e}")
                time.sleep(5)
                
    def _get_pending_verifications(self) -> List[Dict[str, Any]]:
        """Get list of pending verification items"""
        try:
            from .data_archiver import get_archiver
            archiver = get_archiver()
            
            # Query for pending verifications
            query = """
            SELECT id, operation, input_data, output_data, timestamp, data_type, source
            FROM archive_entries 
            WHERE verification_result = 'pending' 
            ORDER BY timestamp ASC 
            LIMIT ?
            """
            
            result = archiver.execute_query(query, (self.batch_size * 3,))
            
            pending_items = []
            for row in result:
                pending_items.append({
                    'id': row[0],
                    'operation': row[1],
                    'input_data': row[2],
                    'output_data': row[3],
                    'timestamp': row[4],
                    'data_type': row[5],
                    'source': row[6]
                })
                
            return pending_items
            
        except Exception as e:
            logging.error(f"Error getting pending verifications: {e}")
            return []
            
    def _create_batches(self, items: List[Dict[str, Any]], batch_size: int) -> List[List[Dict[str, Any]]]:
        """Create batches from list of items"""
        batches = []
        for i in range(0, len(items), batch_size):
            batches.append(items[i:i + batch_size])
        return batches
        
    def _process_batch_concurrent(self, batch: List[Dict[str, Any]]):
        """Process a batch of verifications concurrently"""
        with ThreadPoolExecutor(max_workers=min(self.max_workers, len(batch))) as executor:
            # Submit all verification tasks
            future_to_item = {
                executor.submit(self._verify_single_item, item): item 
                for item in batch
            }
            
            # Process completed verifications
            for future in as_completed(future_to_item):
                item = future_to_item[future]
                try:
                    success = future.result()
                    self.stats['processed'] += 1
                    if success:
                        self.stats['successful'] += 1
                    else:
                        self.stats['failed'] += 1
                        
                except Exception as e:
                    logging.error(f"Error processing verification for item {item['id']}: {e}")
                    self.stats['failed'] += 1
                    
    def _verify_single_item(self, item: Dict[str, Any]) -> bool:
        """Verify a single item"""
        try:
            # Perform verification
            result = self.verifier.verify_data(
                item['input_data'],
                item['output_data'],
                item['data_type'],
                item['source'],
                item['operation']
            )
            
            # Update archive entry with result
            self._update_verification_result(item['id'], result)
            
            return result.is_verified
            
        except Exception as e:
            logging.error(f"Error verifying item {item['id']}: {e}")
            return False
            
    def _update_verification_result(self, entry_id: int, verification_result):
        """Update verification result in database"""
        try:
            from .data_archiver import get_archiver
            archiver = get_archiver()
            
            update_query = """
            UPDATE archive_entries 
            SET verification_result = ?, confidence_score = ?
            WHERE id = ?
            """
            
            result_status = 'verified' if verification_result.is_verified else 'rejected'
            archiver.execute_query(update_query, (
                result_status,
                verification_result.confidence_score,
                entry_id
            ))
            
        except Exception as e:
            logging.error(f"Error updating verification result for entry {entry_id}: {e}")
            
    def _update_stats(self):
        """Update throughput statistics"""
        if self.stats['start_time']:
            elapsed = time.time() - self.stats['start_time']
            if elapsed > 0:
                self.stats['throughput'] = self.stats['processed'] / elapsed
                
    def get_optimization_stats(self) -> Dict[str, Any]:
        """Get current optimization statistics"""
        return {
            'processed': self.stats['processed'],
            'successful': self.stats['successful'],
            'failed': self.stats['failed'],
            'throughput_per_second': round(self.stats['throughput'], 2),
            'success_rate': round(self.stats['successful'] / max(1, self.stats['processed']) * 100, 1),
            'is_running': self.is_running,
            'elapsed_time': round(time.time() - self.stats['start_time'], 1) if self.stats['start_time'] else 0
        }
        
    def optimize_pending_queue(self, target_reduction: float = 0.5) -> Dict[str, Any]:
        """Optimize pending verification queue to reduce backlog"""
        initial_pending = self._get_pending_count()
        target_pending = int(initial_pending * (1 - target_reduction))
        
        optimization_report = {
            'initial_pending': initial_pending,
            'target_pending': target_pending,
            'optimization_started': datetime.now().isoformat(),
            'target_reduction': target_reduction
        }
        
        # Start optimization if not already running
        if not self.is_running:
            self.start_optimization()
            
        print(f"[OPTIMIZE] Starting queue optimization: {initial_pending} → {target_pending} pending items")
        
        return optimization_report
        
    def _get_pending_count(self) -> int:
        """Get count of pending verifications"""
        try:
            from .data_archiver import get_archiver
            archiver = get_archiver()
            
            result = archiver.execute_query(
                "SELECT COUNT(*) FROM archive_entries WHERE verification_result = 'pending'"
            )
            return result[0][0] if result else 0
            
        except Exception as e:
            logging.error(f"Error getting pending count: {e}")
            return 0

# Global optimizer instance
_optimizer_instance = None

def get_verification_optimizer() -> VerificationOptimizer:
    """Get global verification optimizer instance"""
    global _optimizer_instance
    if _optimizer_instance is None:
        _optimizer_instance = VerificationOptimizer()
    return _optimizer_instance

def start_verification_optimization():
    """Start verification optimization"""
    optimizer = get_verification_optimizer()
    optimizer.start_optimization()
    return optimizer.get_optimization_stats()

def stop_verification_optimization():
    """Stop verification optimization"""
    optimizer = get_verification_optimizer()
    optimizer.stop_optimization()
    return optimizer.get_optimization_stats()

def get_optimization_status():
    """Get current optimization status"""
    optimizer = get_verification_optimizer()
    return optimizer.get_optimization_stats()