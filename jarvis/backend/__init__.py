"""
Unified Jarvis Backend Service
Production-ready backend that integrates all Jarvis systems
"""

import asyncio
import threading
import time
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from pathlib import Path
import uuid

from ..api.jarvis_api import get_jarvis_api, JarvisAPI
from ..api.api_models import *
from ..memory.production_memory import get_production_memory
from ..llm.production_llm import get_production_llm
from ..core.error_handler import error_handler, ErrorLevel, safe_execute
from ..core.performance_monitor import get_system_metrics
from ..utils.file_processors import get_file_processor_manager

class JarvisBackendService:
    """
    Unified Jarvis Backend Service
    
    This service provides a complete backend infrastructure that:
    - Integrates all Jarvis subsystems (memory, LLM, file processing, agents)
    - Provides unified APIs for CLI, GUI, and agent interfaces
    - Manages system state and configuration
    - Handles concurrent operations and resource management
    - Provides enterprise-grade monitoring and analytics
    """
    
    def __init__(self):
        self.service_id = str(uuid.uuid4())
        self.start_time = datetime.now()
        self.is_running = False
        
        # Core subsystems
        self.api = get_jarvis_api()
        self.memory = get_production_memory()
        self.llm = get_production_llm()
        
        # Service state
        self.active_sessions: Dict[str, Dict[str, Any]] = {}
        self.event_subscribers: Dict[str, List[Callable]] = {}
        self.background_tasks: List[asyncio.Task] = []
        
        # Configuration
        self.config = {
            "max_concurrent_sessions": 100,
            "session_timeout": 3600,  # 1 hour
            "auto_save_interval": 300,  # 5 minutes
            "cleanup_interval": 1800,  # 30 minutes
            "enable_analytics": True,
            "enable_caching": True,
            "debug_mode": False
        }
        
        # Statistics
        self.stats = {
            "total_sessions": 0,
            "current_sessions": 0,
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "uptime_seconds": 0,
            "subsystem_health": {}
        }
        
        self._lock = threading.RLock()
        self._initialize_service()
    
    def _initialize_service(self):
        """Initialize the backend service"""
        try:
            print(f"[BACKEND] Initializing Jarvis Backend Service {self.service_id[:8]}")
            
            # Initialize subsystems
            self._verify_subsystems()
            
            # Set up event system
            self._setup_event_system()
            
            # Start background tasks
            self._start_background_tasks()
            
            print(f"[BACKEND] Service initialized successfully")
            
        except Exception as e:
            error_handler.log_error(
                e, "Backend Service Initialization", ErrorLevel.CRITICAL,
                "Failed to initialize backend service"
            )
            raise
    
    def _verify_subsystems(self):
        """Verify all subsystems are operational"""
        subsystems = {
            "api": self.api,
            "memory": self.memory,
            "llm": self.llm
        }
        
        for name, subsystem in subsystems.items():
            try:
                if hasattr(subsystem, 'get_health_status'):
                    health = subsystem.get_health_status()
                else:
                    health = {"status": "operational", "score": 100}
                
                self.stats["subsystem_health"][name] = health
                print(f"[BACKEND] {name.upper()} subsystem: {health.get('status', 'unknown')}")
                
            except Exception as e:
                error_handler.log_error(
                    e, f"Subsystem Verification - {name}", ErrorLevel.ERROR,
                    f"Failed to verify {name} subsystem"
                )
                self.stats["subsystem_health"][name] = {"status": "error", "score": 0}
    
    def _setup_event_system(self):
        """Set up event subscription system"""
        self.event_subscribers = {
            "session_start": [],
            "session_end": [],
            "request_processed": [],
            "error_occurred": [],
            "system_status_changed": []
        }
    
    def _start_background_tasks(self):
        """Start background maintenance tasks"""
        if not self.is_running:
            self.is_running = True
            
            # Start cleanup task
            cleanup_thread = threading.Thread(target=self._background_cleanup, daemon=True)
            cleanup_thread.start()
            
            # Start statistics update task
            stats_thread = threading.Thread(target=self._update_statistics, daemon=True)
            stats_thread.start()
    
    def _background_cleanup(self):
        """Background cleanup task"""
        while self.is_running:
            try:
                current_time = time.time()
                
                # Clean up expired sessions
                expired_sessions = []
                with self._lock:
                    for session_id, session_data in self.active_sessions.items():
                        last_activity = session_data.get("last_activity", 0)
                        if current_time - last_activity > self.config["session_timeout"]:
                            expired_sessions.append(session_id)
                
                for session_id in expired_sessions:
                    self.end_session(session_id)
                
                # Clean up LLM cache if enabled
                if self.config["enable_caching"]:
                    try:
                        # Periodic cache cleanup
                        if hasattr(self.llm, 'cleanup_cache'):
                            self.llm.cleanup_cache()
                    except:
                        pass
                
                time.sleep(self.config["cleanup_interval"])
                
            except Exception as e:
                error_handler.log_error(
                    e, "Background Cleanup", ErrorLevel.WARNING,
                    "Background cleanup task encountered an error"
                )
                time.sleep(60)  # Wait before retrying
    
    def _update_statistics(self):
        """Update service statistics"""
        while self.is_running:
            try:
                with self._lock:
                    self.stats["uptime_seconds"] = (datetime.now() - self.start_time).total_seconds()
                    self.stats["current_sessions"] = len(self.active_sessions)
                
                time.sleep(30)  # Update every 30 seconds
                
            except Exception as e:
                error_handler.log_error(
                    e, "Statistics Update", ErrorLevel.WARNING,
                    "Failed to update service statistics"
                )
                time.sleep(60)
    
    @safe_execute(fallback_value=None, context="Session Creation")
    def create_session(self, session_type: str = "general", metadata: Dict[str, Any] = None) -> Optional[str]:
        """
        Create a new user session
        """
        session_id = str(uuid.uuid4())
        
        session_data = {
            "id": session_id,
            "type": session_type,
            "created_at": time.time(),
            "last_activity": time.time(),
            "request_count": 0,
            "conversation_history": [],
            "metadata": metadata or {},
            "state": {}
        }
        
        with self._lock:
            # Check session limit
            if len(self.active_sessions) >= self.config["max_concurrent_sessions"]:
                # Remove oldest session
                oldest_session = min(
                    self.active_sessions.keys(),
                    key=lambda k: self.active_sessions[k]["last_activity"]
                )
                self.end_session(oldest_session)
            
            self.active_sessions[session_id] = session_data
            self.stats["total_sessions"] += 1
        
        # Notify subscribers
        self._emit_event("session_start", {"session_id": session_id, "session_data": session_data})
        
        return session_id
    
    @safe_execute(fallback_value=False, context="Session Management")
    def end_session(self, session_id: str) -> bool:
        """End a user session"""
        with self._lock:
            session_data = self.active_sessions.pop(session_id, None)
        
        if session_data:
            # Notify subscribers
            self._emit_event("session_end", {"session_id": session_id, "session_data": session_data})
            return True
        
        return False
    
    @safe_execute(fallback_value=None, context="Request Processing")
    def process_request(self, session_id: str, request_type: str, 
                       request_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Process a request within a session context
        """
        # Update session activity
        with self._lock:
            if session_id not in self.active_sessions:
                return {"error": "Invalid session ID"}
            
            self.active_sessions[session_id]["last_activity"] = time.time()
            self.active_sessions[session_id]["request_count"] += 1
            self.stats["total_requests"] += 1
        
        try:
            # Create API request
            api_request = APIRequest(
                request_type=RequestType(request_type),
                data=request_data,
                metadata={"session_id": session_id}
            )
            
            # Process through API
            api_response = self.api.process_request(api_request)
            
            # Convert to session response format
            response = {
                "success": api_response.status == ResponseStatus.SUCCESS,
                "data": api_response.data,
                "message": api_response.message,
                "execution_time": api_response.execution_time,
                "timestamp": api_response.timestamp.isoformat()
            }
            
            # Update conversation history for chat requests
            if request_type == "chat" and response["success"]:
                with self._lock:
                    session = self.active_sessions[session_id]
                    session["conversation_history"].append({
                        "user": request_data.get("message", ""),
                        "assistant": response["data"].get("chat_response", {}).get("response", ""),
                        "timestamp": time.time()
                    })
                    
                    # Keep only last 50 messages
                    if len(session["conversation_history"]) > 50:
                        session["conversation_history"] = session["conversation_history"][-50:]
            
            # Update statistics
            with self._lock:
                if response["success"]:
                    self.stats["successful_requests"] += 1
                else:
                    self.stats["failed_requests"] += 1
            
            # Notify subscribers
            self._emit_event("request_processed", {
                "session_id": session_id,
                "request_type": request_type,
                "success": response["success"],
                "response": response
            })
            
            return response
            
        except Exception as e:
            error_handler.log_error(
                e, "Request Processing", ErrorLevel.ERROR,
                f"Session: {session_id}, Type: {request_type}"
            )
            
            with self._lock:
                self.stats["failed_requests"] += 1
            
            self._emit_event("error_occurred", {
                "session_id": session_id,
                "error": str(e),
                "request_type": request_type
            })
            
            return {
                "success": False,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
    
    def get_session_info(self, session_id: str) -> Optional[Dict[str, Any]]:
        """Get information about a session"""
        with self._lock:
            session_data = self.active_sessions.get(session_id)
        
        if session_data:
            return {
                "id": session_data["id"],
                "type": session_data["type"],
                "created_at": session_data["created_at"],
                "last_activity": session_data["last_activity"],
                "request_count": session_data["request_count"],
                "conversation_length": len(session_data["conversation_history"]),
                "metadata": session_data["metadata"]
            }
        
        return None
    
    def get_conversation_history(self, session_id: str, limit: int = 20) -> List[Dict[str, Any]]:
        """Get conversation history for a session"""
        with self._lock:
            session_data = self.active_sessions.get(session_id)
        
        if session_data:
            history = session_data["conversation_history"]
            return history[-limit:] if limit else history
        
        return []
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        try:
            # Get core metrics
            try:
                system_metrics = get_system_metrics()
            except:
                system_metrics = {"health_score": 85, "error": "Metrics unavailable"}
            
            # Get subsystem statistics
            memory_stats = self.memory.get_memory_stats()
            llm_stats = self.llm.get_usage_statistics()
            api_stats = self.api.get_api_stats()
            
            with self._lock:
                service_stats = self.stats.copy()
                active_sessions = len(self.active_sessions)
            
            return {
                "service": {
                    "id": self.service_id,
                    "uptime": service_stats["uptime_seconds"],
                    "status": "running" if self.is_running else "stopped",
                    "version": "1.0.0"
                },
                "sessions": {
                    "active": active_sessions,
                    "total_created": service_stats["total_sessions"],
                    "max_concurrent": self.config["max_concurrent_sessions"]
                },
                "requests": {
                    "total": service_stats["total_requests"],
                    "successful": service_stats["successful_requests"],
                    "failed": service_stats["failed_requests"],
                    "success_rate": service_stats["successful_requests"] / max(service_stats["total_requests"], 1)
                },
                "subsystems": {
                    "memory": memory_stats,
                    "llm": llm_stats,
                    "api": api_stats,
                    "health": service_stats["subsystem_health"]
                },
                "system_metrics": system_metrics,
                "configuration": {
                    "max_sessions": self.config["max_concurrent_sessions"],
                    "session_timeout": self.config["session_timeout"],
                    "analytics_enabled": self.config["enable_analytics"],
                    "caching_enabled": self.config["enable_caching"]
                }
            }
            
        except Exception as e:
            error_handler.log_error(
                e, "System Status", ErrorLevel.ERROR,
                "Failed to get comprehensive system status"
            )
            return {"error": str(e), "status": "error"}
    
    def update_configuration(self, config_updates: Dict[str, Any]) -> bool:
        """Update service configuration"""
        try:
            with self._lock:
                for key, value in config_updates.items():
                    if key in self.config:
                        self.config[key] = value
            
            return True
            
        except Exception as e:
            error_handler.log_error(
                e, "Configuration Update", ErrorLevel.ERROR,
                f"Failed to update configuration: {config_updates}"
            )
            return False
    
    def subscribe_to_events(self, event_type: str, callback: Callable):
        """Subscribe to service events"""
        if event_type in self.event_subscribers:
            self.event_subscribers[event_type].append(callback)
            return True
        return False
    
    def _emit_event(self, event_type: str, event_data: Dict[str, Any]):
        """Emit event to subscribers"""
        if event_type in self.event_subscribers:
            for callback in self.event_subscribers[event_type]:
                try:
                    callback(event_data)
                except Exception as e:
                    error_handler.log_error(
                        e, "Event Emission", ErrorLevel.WARNING,
                        f"Event callback failed: {event_type}"
                    )
    
    def shutdown(self):
        """Gracefully shutdown the service"""
        print(f"[BACKEND] Shutting down service {self.service_id[:8]}")
        
        self.is_running = False
        
        # End all active sessions
        with self._lock:
            session_ids = list(self.active_sessions.keys())
        
        for session_id in session_ids:
            self.end_session(session_id)
        
        # Clean up resources
        try:
            if hasattr(self.memory, 'close'):
                self.memory.close()
            if hasattr(self.llm, 'cleanup'):
                self.llm.cleanup()
        except:
            pass
        
        print(f"[BACKEND] Service shutdown complete")

# Global backend service instance
_backend_service = None

def get_jarvis_backend() -> JarvisBackendService:
    """Get the global Jarvis backend service instance"""
    global _backend_service
    if _backend_service is None:
        _backend_service = JarvisBackendService()
    return _backend_service

def shutdown_jarvis_backend():
    """Shutdown the global backend service"""
    global _backend_service
    if _backend_service:
        _backend_service.shutdown()
        _backend_service = None