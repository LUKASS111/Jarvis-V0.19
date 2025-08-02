"""
CRDT Network Synchronization Layer
Phase 4 - Integration: Network layer for distributed CRDT synchronization

This module implements the network communication layer for distributed
CRDT synchronization with secure peer-to-peer communication.
"""

import json
import time
import uuid
import socket
import threading
import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import hashlib
import hmac
from pathlib import Path

# from .crdt_base import CRDTOperationResult


logger = logging.getLogger(__name__)


@dataclass
class PeerInfo:
    """Information about a peer node"""
    node_id: str
    address: str
    port: int
    last_seen: datetime
    protocol_version: str = "1.0"
    capabilities: List[str] = None
    
    def __post_init__(self):
        if self.capabilities is None:
            self.capabilities = ["basic_sync", "delta_sync"]


@dataclass
class SyncMessage:
    """Message for CRDT synchronization"""
    message_id: str
    message_type: str  # "sync_request", "sync_response", "delta", "heartbeat"
    source_node: str
    target_node: str
    timestamp: datetime
    crdt_name: str
    data: Any
    sequence_number: int = 0
    
    def to_json(self) -> str:
        """Serialize message to JSON"""
        data = asdict(self)
        data['timestamp'] = self.timestamp.isoformat()
        return json.dumps(data)
    
    @classmethod
    def from_json(cls, json_str: str) -> 'SyncMessage':
        """Deserialize message from JSON"""
        data = json.loads(json_str)
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)


class CRDTNetworkManager:
    """
    Network manager for CRDT synchronization
    
    Handles peer discovery, connection management, and message routing
    for distributed CRDT operations.
    """
    
    def __init__(self, node_id: str, port: int = 8888, discovery_port: int = 8889):
        self.node_id = node_id
        self.port = port
        self.discovery_port = discovery_port
        
        # Network state
        self.peers: Dict[str, PeerInfo] = {}
        self.active_connections: Dict[str, socket.socket] = {}
        self.message_handlers: Dict[str, callable] = {}
        self.sequence_counters: Dict[str, int] = {}
        
        # Server sockets
        self.server_socket: Optional[socket.socket] = None
        self.discovery_socket: Optional[socket.socket] = None
        
        # Threading
        self.running = False
        self.server_thread: Optional[threading.Thread] = None
        self.discovery_thread: Optional[threading.Thread] = None
        self.heartbeat_thread: Optional[threading.Thread] = None
        
        # Configuration
        self.heartbeat_interval = 30  # seconds
        self.peer_timeout = 120  # seconds
        self.max_message_size = 1024 * 1024  # 1MB
        
        # Setup message handlers
        self._setup_message_handlers()
        
        logger.info(f"CRDT Network Manager initialized for node {node_id}")
    
    def _setup_message_handlers(self):
        """Setup message handlers for different message types"""
        self.message_handlers = {
            "sync_request": self._handle_sync_request,
            "sync_response": self._handle_sync_response,
            "delta": self._handle_delta,
            "heartbeat": self._handle_heartbeat,
            "peer_discovery": self._handle_peer_discovery,
            "peer_announcement": self._handle_peer_announcement
        }
    
    def start(self) -> bool:
        """Start the network manager"""
        try:
            # Start TCP server for peer connections
            self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.server_socket.bind(('0.0.0.0', self.port))
            self.server_socket.listen(5)
            
            # Start UDP socket for discovery
            self.discovery_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            self.discovery_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            self.discovery_socket.bind(('0.0.0.0', self.discovery_port))
            
            self.running = True
            
            # Start worker threads
            self.server_thread = threading.Thread(target=self._run_server, daemon=True)
            self.discovery_thread = threading.Thread(target=self._run_discovery, daemon=True)
            self.heartbeat_thread = threading.Thread(target=self._run_heartbeat, daemon=True)
            
            self.server_thread.start()
            self.discovery_thread.start()
            self.heartbeat_thread.start()
            
            logger.info(f"CRDT Network Manager started on port {self.port}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to start network manager: {e}")
            self.stop()
            return False
    
    def stop(self):
        """Stop the network manager"""
        self.running = False
        
        # Close all connections
        for connection in self.active_connections.values():
            try:
                connection.close()
            except:
                pass
        self.active_connections.clear()
        
        # Close server sockets
        if self.server_socket:
            try:
                self.server_socket.close()
            except:
                pass
        
        if self.discovery_socket:
            try:
                self.discovery_socket.close()
            except:
                pass
        
        # Wait for threads to finish
        if self.server_thread and self.server_thread.is_alive():
            self.server_thread.join(timeout=1)
        
        if self.discovery_thread and self.discovery_thread.is_alive():
            self.discovery_thread.join(timeout=1)
        
        if self.heartbeat_thread and self.heartbeat_thread.is_alive():
            self.heartbeat_thread.join(timeout=1)
        
        logger.info("CRDT Network Manager stopped")
    
    def _run_server(self):
        """Run the TCP server for peer connections"""
        while self.running:
            try:
                if self.server_socket:
                    client_socket, address = self.server_socket.accept()
                    threading.Thread(
                        target=self._handle_client,
                        args=(client_socket, address),
                        daemon=True
                    ).start()
            except Exception as e:
                if self.running:
                    logger.error(f"Server error: {e}")
                break
    
    def _run_discovery(self):
        """Run UDP discovery service"""
        while self.running:
            try:
                if self.discovery_socket:
                    data, address = self.discovery_socket.recvfrom(1024)
                    self._handle_discovery_message(data, address)
            except Exception as e:
                if self.running:
                    logger.error(f"Discovery error: {e}")
                break
    
    def _run_heartbeat(self):
        """Send periodic heartbeats to peers"""
        while self.running:
            try:
                self._send_heartbeats()
                self._cleanup_stale_peers()
                time.sleep(self.heartbeat_interval)
            except Exception as e:
                logger.error(f"Heartbeat error: {e}")
    
    def _handle_client(self, client_socket: socket.socket, address: Tuple[str, int]):
        """Handle incoming client connection"""
        try:
            while self.running:
                data = client_socket.recv(self.max_message_size)
                if not data:
                    break
                
                message = SyncMessage.from_json(data.decode('utf-8'))
                self._route_message(message)
                
        except Exception as e:
            logger.error(f"Client handler error for {address}: {e}")
        finally:
            client_socket.close()
    
    def _handle_discovery_message(self, data: bytes, address: Tuple[str, int]):
        """Handle UDP discovery message"""
        try:
            message = json.loads(data.decode('utf-8'))
            
            if message.get('type') == 'peer_discovery':
                # Respond with our information
                response = {
                    'type': 'peer_announcement',
                    'node_id': self.node_id,
                    'port': self.port,
                    'protocol_version': '1.0',
                    'capabilities': ['basic_sync', 'delta_sync'],
                    'timestamp': datetime.utcnow().isoformat()
                }
                
                self.discovery_socket.sendto(
                    json.dumps(response).encode('utf-8'),
                    address
                )
                
            elif message.get('type') == 'peer_announcement':
                # Add peer to our list
                node_id = message.get('node_id')
                if node_id and node_id != self.node_id:
                    peer = PeerInfo(
                        node_id=node_id,
                        address=address[0],
                        port=message.get('port', self.port),
                        last_seen=datetime.utcnow(),
                        protocol_version=message.get('protocol_version', '1.0'),
                        capabilities=message.get('capabilities', [])
                    )
                    self.peers[node_id] = peer
                    logger.info(f"Discovered peer: {node_id} at {address[0]}:{peer.port}")
                    
        except Exception as e:
            logger.error(f"Discovery message error from {address}: {e}")
    
    def discover_peers(self) -> List[str]:
        """Discover peers on the network"""
        try:
            discovery_message = {
                'type': 'peer_discovery',
                'node_id': self.node_id,
                'timestamp': datetime.utcnow().isoformat()
            }
            
            # Broadcast discovery message
            broadcast_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            broadcast_socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
            broadcast_socket.settimeout(2)
            
            try:
                broadcast_socket.sendto(
                    json.dumps(discovery_message).encode('utf-8'),
                    ('<broadcast>', self.discovery_port)
                )
                
                # Wait a bit for responses
                time.sleep(2)
                
            finally:
                broadcast_socket.close()
            
            return list(self.peers.keys())
            
        except Exception as e:
            logger.error(f"Peer discovery error: {e}")
            return []
    
    def connect_to_peer(self, peer_id: str) -> bool:
        """Establish connection to a peer"""
        peer = self.peers.get(peer_id)
        if not peer:
            logger.error(f"Unknown peer: {peer_id}")
            return False
        
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((peer.address, peer.port))
            
            self.active_connections[peer_id] = sock
            logger.info(f"Connected to peer: {peer_id}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to peer {peer_id}: {e}")
            return False
    
    def send_message(self, target_node: str, message_type: str, 
                    crdt_name: str, data: Any) -> bool:
        """Send a message to a peer"""
        if target_node not in self.active_connections:
            if not self.connect_to_peer(target_node):
                return False
        
        try:
            message = SyncMessage(
                message_id=str(uuid.uuid4()),
                message_type=message_type,
                source_node=self.node_id,
                target_node=target_node,
                timestamp=datetime.utcnow(),
                crdt_name=crdt_name,
                data=data,
                sequence_number=self._get_next_sequence(target_node)
            )
            
            connection = self.active_connections[target_node]
            connection.send(message.to_json().encode('utf-8'))
            
            logger.debug(f"Sent {message_type} to {target_node}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to send message to {target_node}: {e}")
            # Remove failed connection
            if target_node in self.active_connections:
                del self.active_connections[target_node]
            return False
    
    def _get_next_sequence(self, target_node: str) -> int:
        """Get next sequence number for target node"""
        current = self.sequence_counters.get(target_node, 0)
        self.sequence_counters[target_node] = current + 1
        return current + 1
    
    def _route_message(self, message: SyncMessage):
        """Route incoming message to appropriate handler"""
        handler = self.message_handlers.get(message.message_type)
        if handler:
            try:
                handler(message)
            except Exception as e:
                logger.error(f"Message handler error for {message.message_type}: {e}")
        else:
            logger.warning(f"No handler for message type: {message.message_type}")
    
    def _handle_sync_request(self, message: SyncMessage):
        """Handle sync request from peer"""
        logger.info(f"Received sync request from {message.source_node} for {message.crdt_name}")
        # Implementation will be connected to CRDT manager
        pass
    
    def _handle_sync_response(self, message: SyncMessage):
        """Handle sync response from peer"""
        logger.info(f"Received sync response from {message.source_node} for {message.crdt_name}")
        # Implementation will be connected to CRDT manager
        pass
    
    def _handle_delta(self, message: SyncMessage):
        """Handle delta synchronization message"""
        logger.info(f"Received delta from {message.source_node} for {message.crdt_name}")
        # Implementation will be connected to CRDT manager
        pass
    
    def _handle_heartbeat(self, message: SyncMessage):
        """Handle heartbeat message"""
        if message.source_node in self.peers:
            self.peers[message.source_node].last_seen = datetime.utcnow()
            logger.debug(f"Heartbeat from {message.source_node}")
    
    def _handle_peer_discovery(self, message: SyncMessage):
        """Handle peer discovery message"""
        logger.info(f"Peer discovery from {message.source_node}")
    
    def _handle_peer_announcement(self, message: SyncMessage):
        """Handle peer announcement message"""
        logger.info(f"Peer announcement from {message.source_node}")
    
    def _send_heartbeats(self):
        """Send heartbeats to all connected peers"""
        for peer_id in list(self.active_connections.keys()):
            self.send_message(peer_id, "heartbeat", "", {
                "timestamp": datetime.utcnow().isoformat(),
                "node_id": self.node_id
            })
    
    def _cleanup_stale_peers(self):
        """Remove peers that haven't been seen recently"""
        cutoff_time = datetime.utcnow() - timedelta(seconds=self.peer_timeout)
        
        stale_peers = [
            peer_id for peer_id, peer in self.peers.items()
            if peer.last_seen < cutoff_time
        ]
        
        for peer_id in stale_peers:
            logger.info(f"Removing stale peer: {peer_id}")
            del self.peers[peer_id]
            
            if peer_id in self.active_connections:
                try:
                    self.active_connections[peer_id].close()
                except:
                    pass
                del self.active_connections[peer_id]
    
    def get_network_status(self) -> Dict[str, Any]:
        """Get current network status"""
        return {
            "node_id": self.node_id,
            "port": self.port,
            "running": self.running,
            "peer_count": len(self.peers),
            "active_connections": len(self.active_connections),
            "peers": {
                peer_id: {
                    "address": peer.address,
                    "port": peer.port,
                    "last_seen": peer.last_seen.isoformat(),
                    "capabilities": peer.capabilities
                }
                for peer_id, peer in self.peers.items()
            }
        }


class CRDTSynchronizer:
    """
    High-level CRDT synchronization manager
    
    Coordinates between CRDT instances and the network layer
    for distributed synchronization.
    """
    
    def __init__(self, network_manager: CRDTNetworkManager, crdt_manager):
        self.network_manager = network_manager
        self.crdt_manager = crdt_manager
        
        # Sync state
        self.sync_intervals: Dict[str, int] = {}  # crdt_name -> interval in seconds
        self.last_sync_times: Dict[str, datetime] = {}
        self.sync_priorities: Dict[str, str] = {}  # high, normal, low
        
        # Default sync intervals by priority
        self.default_intervals = {
            "high": 10,    # 10 seconds
            "normal": 60,  # 1 minute
            "low": 300     # 5 minutes
        }
        
        logger.info("CRDT Synchronizer initialized")
    
    def register_crdt_for_sync(self, crdt_name: str, priority: str = "normal"):
        """Register a CRDT for synchronization"""
        self.sync_priorities[crdt_name] = priority
        self.sync_intervals[crdt_name] = self.default_intervals[priority]
        self.last_sync_times[crdt_name] = datetime.utcnow()
        
        logger.info(f"Registered CRDT {crdt_name} for sync with {priority} priority")
    
    def sync_with_peer(self, peer_id: str, crdt_name: str) -> bool:
        """Synchronize specific CRDT with a peer"""
        try:
            # Get current CRDT state
            crdt_state = self.crdt_manager.get_crdt_state(crdt_name)
            if not crdt_state:
                logger.error(f"CRDT {crdt_name} not found")
                return False
            
            # Send sync request
            success = self.network_manager.send_message(
                target_node=peer_id,
                message_type="sync_request",
                crdt_name=crdt_name,
                data={
                    "state_hash": self._calculate_state_hash(crdt_state),
                    "vector_clock": getattr(crdt_state, 'vector_clock', {}),
                    "last_modified": datetime.utcnow().isoformat()
                }
            )
            
            if success:
                self.last_sync_times[crdt_name] = datetime.utcnow()
                logger.info(f"Initiated sync of {crdt_name} with {peer_id}")
            
            return success
            
        except Exception as e:
            logger.error(f"Sync error for {crdt_name} with {peer_id}: {e}")
            return False
    
    def sync_all_with_peer(self, peer_id: str) -> Dict[str, bool]:
        """Synchronize all registered CRDTs with a peer"""
        results = {}
        
        for crdt_name in self.sync_priorities.keys():
            results[crdt_name] = self.sync_with_peer(peer_id, crdt_name)
        
        return results
    
    def auto_sync_check(self):
        """Check and perform automatic synchronization"""
        current_time = datetime.utcnow()
        
        for crdt_name, interval in self.sync_intervals.items():
            last_sync = self.last_sync_times.get(crdt_name, datetime.min)
            time_since_sync = (current_time - last_sync).total_seconds()
            
            if time_since_sync >= interval:
                # Time to sync this CRDT
                peers = list(self.network_manager.peers.keys())
                
                for peer_id in peers:
                    self.sync_with_peer(peer_id, crdt_name)
    
    def _calculate_state_hash(self, crdt_state) -> str:
        """Calculate hash of CRDT state for quick comparison"""
        try:
            state_str = json.dumps(crdt_state.to_dict(), sort_keys=True)
            return hashlib.sha256(state_str.encode()).hexdigest()
        except Exception:
            return ""
    
    def get_sync_status(self) -> Dict[str, Any]:
        """Get synchronization status"""
        return {
            "registered_crdts": list(self.sync_priorities.keys()),
            "sync_intervals": self.sync_intervals.copy(),
            "last_sync_times": {
                name: time.isoformat() for name, time in self.last_sync_times.items()
            },
            "priorities": self.sync_priorities.copy(),
            "network_status": self.network_manager.get_network_status()
        }


# Example usage and testing functions
def create_test_network_setup():
    """Create a test network setup for development"""
    node_id = f"test_node_{int(time.time())}"
    
    network_manager = CRDTNetworkManager(node_id, port=8888)
    
    # In real implementation, this would be the actual CRDT manager
    class MockCRDTManager:
        def get_crdt_state(self, name):
            return {"value": 42, "timestamp": time.time()}
    
    synchronizer = CRDTSynchronizer(network_manager, MockCRDTManager())
    
    return network_manager, synchronizer


if __name__ == "__main__":
    # Test the network layer
    import sys
    
    logging.basicConfig(level=logging.INFO)
    
    network_manager, synchronizer = create_test_network_setup()
    
    try:
        if network_manager.start():
            print(f"Network manager started for node {network_manager.node_id}")
            print("Discovering peers...")
            
            peers = network_manager.discover_peers()
            print(f"Found {len(peers)} peers: {peers}")
            
            # Keep running for a while
            time.sleep(30)
        else:
            print("Failed to start network manager")
            sys.exit(1)
            
    except KeyboardInterrupt:
        print("\nShutting down...")
    finally:
        network_manager.stop()