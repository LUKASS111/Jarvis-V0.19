#!/usr/bin/env python3
"""
Multi-Node Coordinator for Jarvis V0.19 Load Balancing
Handles distributed node coordination and load balancing.
"""

import asyncio
import json
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import logging

@dataclass
class NodeStatus:
    """Node status tracking"""
    node_id: str
    host: str
    port: int
    is_healthy: bool
    last_health_check: float
    current_load: int
    max_connections: int
    response_time: float

class MultiNodeCoordinator:
    """Multi-node coordinator for load balancing"""
    
    def __init__(self, config_path: str = "deployment/load_balancing/config.json"):
        self.config = self._load_config(config_path)
        self.nodes: Dict[str, NodeStatus] = {}
        self.current_node_index = 0
        self.setup_logging()
        self._initialize_nodes()
        
    def setup_logging(self):
        """Setup logging for coordinator"""
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load load balancing configuration"""
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except Exception as e:
            self.logger.error(f"Failed to load config: {e}")
            return self._get_default_config()
    
    def _get_default_config(self) -> Dict[str, Any]:
        """Get default configuration if file load fails"""
        return {
            "load_balancer": {
                "algorithm": "round_robin",
                "health_check_interval": 30,
                "max_retries": 3
            },
            "nodes": [
                {"id": "node_1", "host": "localhost", "port": 8001, "weight": 1, "max_connections": 100}
            ]
        }
    
    def _initialize_nodes(self):
        """Initialize node status tracking"""
        for node_config in self.config.get("nodes", []):
            node_status = NodeStatus(
                node_id=node_config["id"],
                host=node_config["host"],
                port=node_config["port"],
                is_healthy=False,
                last_health_check=0,
                current_load=0,
                max_connections=node_config.get("max_connections", 100),
                response_time=0.0
            )
            self.nodes[node_config["id"]] = node_status
        
        self.logger.info(f"Initialized {len(self.nodes)} nodes")
    
    async def health_check_all_nodes(self):
        """Perform health check on all nodes"""
        tasks = []
        for node_id in self.nodes:
            tasks.append(self._health_check_node(node_id))
        
        await asyncio.gather(*tasks, return_exceptions=True)
    
    async def _health_check_node(self, node_id: str) -> bool:
        """Perform health check on specific node"""
        node = self.nodes[node_id]
        start_time = time.time()
        
        try:
            # Simulate health check (replace with actual HTTP health check)
            await asyncio.sleep(0.1)  # Simulate network call
            
            # Update node status
            node.is_healthy = True
            node.last_health_check = time.time()
            node.response_time = time.time() - start_time
            
            self.logger.debug(f"Node {node_id} health check: OK ({node.response_time:.3f}s)")
            return True
            
        except Exception as e:
            node.is_healthy = False
            node.last_health_check = time.time()
            self.logger.warning(f"Node {node_id} health check failed: {e}")
            return False
    
    def get_next_node(self) -> Optional[NodeStatus]:
        """Get next available node using load balancing algorithm"""
        algorithm = self.config["load_balancer"].get("algorithm", "round_robin")
        
        if algorithm == "round_robin":
            return self._round_robin_selection()
        elif algorithm == "least_connections":
            return self._least_connections_selection()
        elif algorithm == "weighted_round_robin":
            return self._weighted_round_robin_selection()
        else:
            return self._round_robin_selection()
    
    def _round_robin_selection(self) -> Optional[NodeStatus]:
        """Round robin node selection"""
        healthy_nodes = [node for node in self.nodes.values() if node.is_healthy]
        
        if not healthy_nodes:
            return None
        
        node = healthy_nodes[self.current_node_index % len(healthy_nodes)]
        self.current_node_index += 1
        return node
    
    def _least_connections_selection(self) -> Optional[NodeStatus]:
        """Least connections node selection"""
        healthy_nodes = [node for node in self.nodes.values() if node.is_healthy]
        
        if not healthy_nodes:
            return None
        
        return min(healthy_nodes, key=lambda n: n.current_load)
    
    def _weighted_round_robin_selection(self) -> Optional[NodeStatus]:
        """Weighted round robin selection (simplified)"""
        return self._round_robin_selection()  # Simplified for now
    
    def update_node_load(self, node_id: str, load_change: int):
        """Update node load tracking"""
        if node_id in self.nodes:
            self.nodes[node_id].current_load += load_change
            self.nodes[node_id].current_load = max(0, self.nodes[node_id].current_load)
    
    def get_cluster_status(self) -> Dict[str, Any]:
        """Get overall cluster status"""
        healthy_nodes = sum(1 for node in self.nodes.values() if node.is_healthy)
        total_nodes = len(self.nodes)
        
        return {
            "total_nodes": total_nodes,
            "healthy_nodes": healthy_nodes,
            "cluster_health": healthy_nodes / total_nodes if total_nodes > 0 else 0,
            "nodes": {
                node_id: {
                    "healthy": node.is_healthy,
                    "load": node.current_load,
                    "response_time": node.response_time
                }
                for node_id, node in self.nodes.items()
            }
        }
    
    async def start_coordinator(self):
        """Start the coordinator with health checking"""
        self.logger.info("Starting multi-node coordinator...")
        
        while True:
            await self.health_check_all_nodes()
            await asyncio.sleep(self.config["load_balancer"].get("health_check_interval", 30))

# Example usage
async def main():
    coordinator = MultiNodeCoordinator()
    
    # Start health checking in background
    health_task = asyncio.create_task(coordinator.start_coordinator())
    
    # Example: Get next available node
    node = coordinator.get_next_node()
    if node:
        print(f"Selected node: {node.node_id} at {node.host}:{node.port}")
    
    # Get cluster status
    status = coordinator.get_cluster_status()
    print(f"Cluster health: {status['cluster_health']:.2f}")

if __name__ == "__main__":
    asyncio.run(main())
