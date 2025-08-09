"""
Ollama Provider for local models
"""

import time
import logging
from typing import Dict, Any, List, Optional

from .base import BaseLLMProvider, ProviderType, ProviderCapabilities, LLMRequest, LLMResponse, LLMError

logger = logging.getLogger(__name__)


class OllamaProvider(BaseLLMProvider):
    """
    Ollama provider for local models (integrates with existing Jarvis Ollama interface)
    """
    
    def __init__(self, 
                 base_url: str = "http://localhost:11434",
                 default_model: str = "llama3:8b"):
        super().__init__(
            provider_type=ProviderType.OLLAMA,
            base_url=base_url,
            default_model=default_model
        )
    
    def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Ollama API"""
        start_time = time.time()
        
        try:
            # Import existing Ollama interface
            from ...llm_interface import ask_local_llm
            
            # Use existing Ollama implementation
            response_text = ask_local_llm(
                prompt=request.prompt,
                system_prompt=request.system_prompt,
                temperature=request.temperature,
                max_tokens=request.max_tokens,
                model=self.default_model
            )
            
            # Check for errors
            if response_text.startswith("[LLM ERROR:"):
                return LLMResponse(
                    content="",
                    provider="ollama",
                    model=self.default_model,
                    response_time=time.time() - start_time,
                    error=response_text
                )
            
            response = LLMResponse(
                content=response_text,
                provider="ollama",
                model=self.default_model,
                response_time=time.time() - start_time
            )
            
            self._update_stats(response)
            return response
            
        except Exception as e:
            logger.error(f"Ollama API error: {e}")
            error_response = LLMResponse(
                content="",
                provider="ollama", 
                model=self.default_model,
                response_time=time.time() - start_time,
                error=str(e)
            )
            self._update_stats(error_response)
            return error_response
    
    def get_capabilities(self) -> ProviderCapabilities:
        """Get Ollama provider capabilities"""
        return ProviderCapabilities(
            supports_streaming=False,  # Not implemented in current interface
            supports_function_calling=False,
            supports_vision=False,
            supports_audio=False,
            max_context_length=8192,  # Depends on model
            supports_system_prompt=True,
            supports_temperature=True,
            supports_top_p=True,
            supports_stop_sequences=False,
            supports_json_mode=False,
            rate_limit_rpm=None,  # No rate limits for local
            cost_per_1k_tokens=0.0  # Free local inference
        )
    
    def get_available_models(self) -> List[str]:
        """Get list of available Ollama models"""
        try:
            from ...llm_interface import get_available_models
            return get_available_models()
        except:
            return ["llama3:8b", "codellama:13b", "codellama:34b", "llama3:70b"]
    
    def estimate_cost(self, request: LLMRequest) -> float:
        """Estimate cost for Ollama request (always free)"""
        return 0.0