"""
API Router for Jarvis Production API
Provides convenient routing and helper functions
"""

from typing import Dict, Any, List, Optional
from .api_models import *
from .jarvis_api import get_jarvis_api

class APIRouter:
    """
    Convenient router class for common API operations
    """
    
    def __init__(self):
        self.api = get_jarvis_api()
    
    def chat(self, message: str, model: str = "llama3:8b", **kwargs) -> str:
        """
        Simple chat interface
        Returns just the response text for convenience
        """
        request = APIRequest(
            request_type=RequestType.CHAT,
            data={
                "message": message,
                "model": model,
                **kwargs
            }
        )
        
        response = self.api.process_request(request)
        
        if response.status == ResponseStatus.SUCCESS:
            return response.data["chat_response"]["response"]
        else:
            return f"Error: {response.message}"
    
    def remember(self, key: str, value: str) -> bool:
        """
        Simple memory storage
        Returns True if successful
        """
        request = APIRequest(
            request_type=RequestType.MEMORY_STORE,
            data={
                "operation": "store",
                "key": key,
                "value": value
            }
        )
        
        response = self.api.process_request(request)
        return response.status == ResponseStatus.SUCCESS
    
    def recall(self, key: str) -> Optional[str]:
        """
        Simple memory recall
        Returns the value or None if not found
        """
        request = APIRequest(
            request_type=RequestType.MEMORY_RECALL,
            data={
                "operation": "recall",
                "key": key
            }
        )
        
        response = self.api.process_request(request)
        
        if response.status == ResponseStatus.SUCCESS:
            memory_data = response.data["memory_response"]["data"]
            if "QUESTION" not in memory_data:
                return memory_data
        
        return None
    
    def process_file(self, file_path: str, output_format: str = "agent") -> Dict[str, Any]:
        """
        Simple file processing
        Returns processed file data
        """
        request = APIRequest(
            request_type=RequestType.FILE_PROCESS,
            data={
                "file_path": file_path,
                "processor_type": "auto",
                "output_format": output_format
            }
        )
        
        response = self.api.process_request(request)
        
        if response.status == ResponseStatus.SUCCESS:
            return response.data["file_response"]["structured_data"]
        else:
            return {"error": response.message}
    
    def get_system_status(self) -> Dict[str, Any]:
        """
        Get comprehensive system status
        """
        request = APIRequest(
            request_type=RequestType.SYSTEM_STATUS,
            data={
                "include_performance": True,
                "include_health": True,
                "include_resources": True,
                "detailed": True
            }
        )
        
        response = self.api.process_request(request)
        
        if response.status == ResponseStatus.SUCCESS:
            return response.data
        else:
            return {"error": response.message, "health_score": 0}
    
    def execute_agent_task(self, task_type: str, parameters: Dict[str, Any] = None, async_execution: bool = False) -> Dict[str, Any]:
        """
        Execute agent task
        """
        request = APIRequest(
            request_type=RequestType.AGENT_TASK,
            data={
                "task_type": task_type,
                "parameters": parameters or {},
                "async_execution": async_execution
            }
        )
        
        response = self.api.process_request(request)
        
        if response.status == ResponseStatus.SUCCESS:
            return response.data["task_response"]
        else:
            return {"error": response.message, "status": "failed"}
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available LLM models
        """
        request = APIRequest(
            request_type=RequestType.CONFIGURATION,
            data={}
        )
        
        response = self.api.process_request(request)
        
        if response.status == ResponseStatus.SUCCESS:
            return response.data.get("available_models", [])
        else:
            return []
    
    def get_api_stats(self) -> Dict[str, Any]:
        """
        Get API usage statistics
        """
        return self.api.get_api_stats()

# Convenience functions for direct usage
def quick_chat(message: str, model: str = "llama3:8b") -> str:
    """Quick chat function for simple interactions"""
    router = APIRouter()
    return router.chat(message, model)

def quick_remember(key: str, value: str) -> bool:
    """Quick memory storage function"""
    router = APIRouter()
    return router.remember(key, value)

def quick_recall(key: str) -> Optional[str]:
    """Quick memory recall function"""
    router = APIRouter()
    return router.recall(key)

def quick_process_file(file_path: str) -> Dict[str, Any]:
    """Quick file processing function"""
    router = APIRouter()
    return router.process_file(file_path)

def get_system_health() -> int:
    """Quick system health check"""
    router = APIRouter()
    status = router.get_system_status()
    return status.get("status_response", {}).get("health_score", 0)