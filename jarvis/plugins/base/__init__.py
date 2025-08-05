"""
Base plugin interfaces and utilities for the Jarvis plugin system
"""

from ...core.plugin_system import PluginInterface, PluginRequest, PluginResponse, PluginContext
from abc import abstractmethod
from typing import Any, List, Dict


class FileProcessorPlugin(PluginInterface):
    """Base class for file processor plugins"""
    
    def __init__(self):
        super().__init__()
        self.supported_extensions: List[str] = []
    
    @abstractmethod
    def process_file(self, file_path: str, output_format: str = "memory") -> Dict[str, Any]:
        """Process a file and return structured data
        
        Args:
            file_path: Path to the file to process
            output_format: Format for output ("memory", "logs", "agent")
            
        Returns:
            Dict containing processed file data
        """
        pass
    
    def supports_file(self, file_path: str) -> bool:
        """Check if this plugin supports the given file"""
        extension = file_path.lower().split('.')[-1] if '.' in file_path else ''
        return extension in self.supported_extensions
    
    def execute(self, request: PluginRequest) -> PluginResponse:
        """Execute file processing request"""
        try:
            action = request.action
            
            if action == "process_file":
                file_path = request.data.get("file_path")
                output_format = request.data.get("output_format", "memory")
                
                if not file_path:
                    return PluginResponse.error_response("Missing file_path in request data")
                
                if not self.supports_file(file_path):
                    return PluginResponse.error_response(f"File type not supported: {file_path}")
                
                result = self.process_file(file_path, output_format)
                return PluginResponse.success_response(result)
            
            elif action == "supports_file":
                file_path = request.data.get("file_path")
                if not file_path:
                    return PluginResponse.error_response("Missing file_path in request data")
                
                supports = self.supports_file(file_path)
                return PluginResponse.success_response({"supports": supports})
            
            else:
                return PluginResponse.error_response(f"Unsupported action: {action}")
                
        except Exception as e:
            return PluginResponse.error_response(f"Error processing file: {e}")
    
    def get_supported_actions(self) -> List[str]:
        """Get supported actions"""
        return ["process_file", "supports_file"]


class LLMProviderPlugin(PluginInterface):
    """Base class for LLM provider plugins"""
    
    def __init__(self):
        super().__init__()
        self.provider_name: str = ""
        self.supported_models: List[str] = []
    
    @abstractmethod
    def chat_completion(self, messages: List[Dict[str, str]], model: str = None, **kwargs) -> Dict[str, Any]:
        """Generate chat completion
        
        Args:
            messages: List of message dictionaries with 'role' and 'content'
            model: Model to use for completion
            **kwargs: Additional parameters
            
        Returns:
            Dict containing completion response
        """
        pass
    
    @abstractmethod
    def health_check(self) -> bool:
        """Check if the LLM provider is healthy"""
        pass
    
    def supports_model(self, model: str) -> bool:
        """Check if this provider supports the given model"""
        return model in self.supported_models
    
    def execute(self, request: PluginRequest) -> PluginResponse:
        """Execute LLM provider request"""
        try:
            action = request.action
            
            if action == "chat_completion":
                messages = request.data.get("messages")
                model = request.data.get("model")
                kwargs = request.data.get("kwargs", {})
                
                if not messages:
                    return PluginResponse.error_response("Missing messages in request data")
                
                result = self.chat_completion(messages, model, **kwargs)
                return PluginResponse.success_response(result)
            
            elif action == "health_check":
                is_healthy = self.health_check()
                return PluginResponse.success_response({"healthy": is_healthy})
            
            elif action == "supports_model":
                model = request.data.get("model")
                if not model:
                    return PluginResponse.error_response("Missing model in request data")
                
                supports = self.supports_model(model)
                return PluginResponse.success_response({"supports": supports})
            
            else:
                return PluginResponse.error_response(f"Unsupported action: {action}")
                
        except Exception as e:
            return PluginResponse.error_response(f"Error in LLM provider: {e}")
    
    def get_supported_actions(self) -> List[str]:
        """Get supported actions"""
        return ["chat_completion", "health_check", "supports_model"]