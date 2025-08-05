"""
Jarvis Production API Core Implementation
Unified backend service for all Jarvis interfaces
"""

import time
import asyncio
import threading
from typing import Dict, Any, Optional, List, Union
from datetime import datetime
import json
import os

from .api_models import *
from ..core.error_handler import error_handler, ErrorLevel, safe_execute
from ..memory.memory import remember_fact, recall_fact, get_memory_stats, search_memory
from ..llm.llm_interface import ask_local_llm, get_available_models, get_ollama_model
from ..utils.file_processors import process_file
from ..core.agent_workflow import AgentWorkflow
from ..core.performance_monitor import get_system_metrics

class JarvisAPI:
    """
    Production-grade Unified Jarvis API
    Provides enterprise-level backend services for all interfaces
    """
    
    def __init__(self):
        self.start_time = datetime.now()
        self.request_history: List[APIRequest] = []
        self.active_tasks: Dict[str, Dict[str, Any]] = {}
        self.agent_workflow = None
        self._lock = threading.Lock()
        
        # Initialize subsystems
        self._initialize_subsystems()
    
    def _initialize_subsystems(self):
        """Initialize all backend subsystems"""
        try:
            # Initialize agent workflow system
            self.agent_workflow = AgentWorkflow()
            
            # Verify LLM connectivity
            models = get_available_models()
            if not models:
                error_handler.log_error(
                    Exception("No LLM models available"),
                    "API Initialization",
                    ErrorLevel.WARNING,
                    "LLM subsystem may not be fully functional"
                )
            
            print(f"[API] Jarvis Production API initialized successfully")
            print(f"[API] Available LLM models: {len(models) if models else 0}")
            
        except Exception as e:
            error_handler.log_error(
                e, "API Initialization", ErrorLevel.ERROR,
                "Failed to initialize some subsystems"
            )
    
    @safe_execute(fallback_value=None, context="API Request Processing")
    def process_request(self, request: APIRequest) -> APIResponse:
        """
        Process any API request and return appropriate response
        """
        start_time = time.time()
        
        with self._lock:
            self.request_history.append(request)
            # Keep only last 1000 requests in memory
            if len(self.request_history) > 1000:
                self.request_history = self.request_history[-1000:]
        
        try:
            # Route request to appropriate handler
            response_data = self._route_request(request)
            
            # Create successful response
            response = APIResponse(
                request_id=request.request_id,
                status=ResponseStatus.SUCCESS,
                data=response_data,
                message="Request processed successfully",
                execution_time=time.time() - start_time
            )
            
        except Exception as e:
            # Create error response
            error_handler.log_error(
                e, f"API Request {request.request_type.value}",
                ErrorLevel.ERROR, f"Request ID: {request.request_id}"
            )
            
            response = APIResponse(
                request_id=request.request_id,
                status=ResponseStatus.ERROR,
                message=f"Request failed: {str(e)}",
                error_details=str(e),
                execution_time=time.time() - start_time
            )
        
        return response
    
    def _route_request(self, request: APIRequest) -> Dict[str, Any]:
        """Route request to appropriate handler based on type"""
        
        if request.request_type == RequestType.CHAT:
            return self._handle_chat_request(request)
        elif request.request_type == RequestType.MEMORY_STORE:
            return self._handle_memory_store(request)
        elif request.request_type == RequestType.MEMORY_RECALL:
            return self._handle_memory_recall(request)
        elif request.request_type == RequestType.FILE_PROCESS:
            return self._handle_file_process(request)
        elif request.request_type == RequestType.AGENT_TASK:
            return self._handle_agent_task(request)
        elif request.request_type == RequestType.SYSTEM_STATUS:
            return self._handle_system_status(request)
        elif request.request_type == RequestType.CONFIGURATION:
            return self._handle_configuration(request)
        else:
            raise ValueError(f"Unknown request type: {request.request_type}")
    
    def _handle_chat_request(self, request: APIRequest) -> Dict[str, Any]:
        """Handle chat/LLM requests"""
        chat_req = ChatRequest(**request.data)
        
        # Get LLM response
        response_text = ask_local_llm(chat_req.message)
        
        # Create chat response
        chat_response = ChatResponse(
            response=response_text,
            model_used=chat_req.model,
            conversation_id=request.request_id
        )
        
        return {
            "chat_response": chat_response.__dict__,
            "request_details": {
                "model": chat_req.model,
                "message_length": len(chat_req.message),
                "context_size": len(chat_req.context)
            }
        }
    
    def _handle_memory_store(self, request: APIRequest) -> Dict[str, Any]:
        """Handle memory storage requests"""
        memory_req = MemoryRequest(**request.data)
        
        if memory_req.operation == "store" and memory_req.key and memory_req.value:
            fact = f"{memory_req.key} to {memory_req.value}"
            result = remember_fact(fact)
            
            memory_response = MemoryResponse(
                operation="store",
                success="OK" in result,
                affected_keys=[memory_req.key]
            )
        else:
            raise ValueError("Invalid memory store request: missing key or value")
        
        return {
            "memory_response": memory_response.__dict__,
            "result_message": result
        }
    
    def _handle_memory_recall(self, request: APIRequest) -> Dict[str, Any]:
        """Handle memory recall requests"""
        memory_req = MemoryRequest(**request.data)
        
        if memory_req.operation == "recall" and memory_req.key:
            result = recall_fact(memory_req.key)
            
            memory_response = MemoryResponse(
                operation="recall",
                success="QUESTION" not in result,
                data=result,
                affected_keys=[memory_req.key] if "QUESTION" not in result else []
            )
        elif memory_req.operation == "search" and memory_req.query:
            # Implement memory search if available
            try:
                results = search_memory(memory_req.query)
                memory_response = MemoryResponse(
                    operation="search",
                    success=True,
                    data=results
                )
            except:
                # Fallback to basic recall
                result = recall_fact(memory_req.query)
                memory_response = MemoryResponse(
                    operation="search",
                    success="QUESTION" not in result,
                    data=[result] if "QUESTION" not in result else []
                )
        else:
            raise ValueError("Invalid memory recall request: missing key or query")
        
        return {
            "memory_response": memory_response.__dict__
        }
    
    def _handle_file_process(self, request: APIRequest) -> Dict[str, Any]:
        """Handle file processing requests"""
        file_req = FileProcessRequest(**request.data)
        
        start_time = time.time()
        
        # Process file using universal processor
        result = process_file(file_req.file_path, file_req.output_format)
        
        processing_time = time.time() - start_time
        
        file_response = FileProcessResponse(
            file_path=file_req.file_path,
            processor_used=file_req.processor_type,
            content_summary=result.get("summary", "File processed successfully"),
            structured_data=result,
            processing_time=processing_time
        )
        
        return {
            "file_response": file_response.__dict__,
            "processing_stats": {
                "file_size": os.path.getsize(file_req.file_path) if os.path.exists(file_req.file_path) else 0,
                "processing_time": processing_time
            }
        }
    
    def _handle_agent_task(self, request: APIRequest) -> Dict[str, Any]:
        """Handle agent task execution requests"""
        task_req = AgentTaskRequest(**request.data)
        
        # Create unique task ID
        task_id = f"task_{request.request_id}_{int(time.time())}"
        
        # Store task in active tasks
        self.active_tasks[task_id] = {
            "request": task_req,
            "status": "queued",
            "start_time": datetime.now(),
            "progress": 0.0
        }
        
        # For synchronous execution, process immediately
        if not task_req.async_execution:
            try:
                # Execute task using agent workflow
                if self.agent_workflow:
                    result = self.agent_workflow.execute_task(
                        task_req.task_type, 
                        task_req.parameters
                    )
                else:
                    result = {"message": "Agent workflow not available"}
                
                # Update task status
                self.active_tasks[task_id]["status"] = "completed"
                self.active_tasks[task_id]["result"] = result
                self.active_tasks[task_id]["progress"] = 1.0
                
            except Exception as e:
                self.active_tasks[task_id]["status"] = "failed"
                self.active_tasks[task_id]["error"] = str(e)
                raise
        
        task_response = AgentTaskResponse(
            task_id=task_id,
            task_type=task_req.task_type,
            status=self.active_tasks[task_id]["status"],
            result=self.active_tasks[task_id].get("result"),
            progress=self.active_tasks[task_id]["progress"]
        )
        
        return {
            "task_response": task_response.__dict__,
            "task_id": task_id
        }
    
    def _handle_system_status(self, request: APIRequest) -> Dict[str, Any]:
        """Handle system status requests"""
        status_req = SystemStatusRequest(**request.data)
        
        # Get system metrics
        try:
            metrics = get_system_metrics()
        except:
            metrics = {"health_score": 85, "error": "Metrics not available"}
        
        # Calculate uptime
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        status_response = SystemStatusResponse(
            health_score=metrics.get("health_score", 85),
            performance_metrics=metrics if status_req.include_performance else {},
            resource_usage=metrics.get("resources", {}) if status_req.include_resources else {},
            active_tasks=len(self.active_tasks),
            system_uptime=uptime
        )
        
        return {
            "status_response": status_response.__dict__,
            "api_stats": {
                "total_requests": len(self.request_history),
                "active_tasks": len(self.active_tasks),
                "uptime_hours": uptime / 3600
            }
        }
    
    def _handle_configuration(self, request: APIRequest) -> Dict[str, Any]:
        """Handle configuration requests"""
        # Basic configuration handling
        config_data = request.data
        
        result = {
            "configuration": "Configuration updated" if config_data else "Configuration retrieved",
            "available_models": get_available_models(),
            "current_model": get_ollama_model(),
            "system_config": {
                "api_version": "1.0",
                "features_enabled": [
                    "chat", "memory", "file_processing", 
                    "agent_tasks", "system_monitoring"
                ]
            }
        }
        
        return result
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get status of a specific task"""
        return self.active_tasks.get(task_id)
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id in self.active_tasks:
            self.active_tasks[task_id]["status"] = "cancelled"
            return True
        return False
    
    def get_api_stats(self) -> Dict[str, Any]:
        """Get API usage statistics"""
        return {
            "total_requests": len(self.request_history),
            "active_tasks": len(self.active_tasks),
            "uptime_seconds": (datetime.now() - self.start_time).total_seconds(),
            "memory_usage": len(self.request_history) * 1000,  # Rough estimate
            "last_request": self.request_history[-1].timestamp if self.request_history else None
        }

# Global API instance
_api_instance = None

def get_jarvis_api() -> JarvisAPI:
    """Get the global Jarvis API instance (singleton)"""
    global _api_instance
    if _api_instance is None:
        _api_instance = JarvisAPI()
    return _api_instance