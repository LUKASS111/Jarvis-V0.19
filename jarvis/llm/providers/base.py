"""
Base classes and models for LLM providers
"""

import time
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum


class ProviderType(Enum):
    """LLM Provider types"""
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    MISTRAL = "mistral"
    OLLAMA = "ollama"
    HUGGINGFACE = "huggingface"
    COHERE = "cohere"
    GOOGLE = "google"


class TaskType(Enum):
    """Types of tasks for LLM routing"""
    GENERAL_CHAT = "general_chat"
    CODE_GENERATION = "code_generation"
    REASONING = "reasoning"
    CREATIVE_WRITING = "creative_writing"
    ANALYSIS = "analysis"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    QUESTION_ANSWERING = "question_answering"
    MULTIMODAL = "multimodal"
    FUNCTION_CALLING = "function_calling"


@dataclass
class ProviderCapabilities:
    """Capabilities of an LLM provider"""
    supports_streaming: bool = False
    supports_function_calling: bool = False
    supports_vision: bool = False
    supports_audio: bool = False
    max_context_length: int = 4096
    supports_system_prompt: bool = True
    supports_temperature: bool = True
    supports_top_p: bool = True
    supports_stop_sequences: bool = True
    supports_json_mode: bool = False
    rate_limit_rpm: Optional[int] = None
    cost_per_1k_tokens: Optional[float] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            'supports_streaming': self.supports_streaming,
            'supports_function_calling': self.supports_function_calling,
            'supports_vision': self.supports_vision,
            'supports_audio': self.supports_audio,
            'max_context_length': self.max_context_length,
            'supports_system_prompt': self.supports_system_prompt,
            'supports_temperature': self.supports_temperature,
            'supports_top_p': self.supports_top_p,
            'supports_stop_sequences': self.supports_stop_sequences,
            'supports_json_mode': self.supports_json_mode,
            'rate_limit_rpm': self.rate_limit_rpm,
            'cost_per_1k_tokens': self.cost_per_1k_tokens
        }


@dataclass
class LLMRequest:
    """Request to LLM provider"""
    prompt: str
    system_prompt: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    top_p: Optional[float] = None
    stop_sequences: Optional[List[str]] = None
    stream: bool = False
    json_mode: bool = False
    functions: Optional[List[Dict[str, Any]]] = None
    images: Optional[List[str]] = None  # Base64 encoded or URLs
    audio: Optional[str] = None  # Base64 encoded
    metadata: Optional[Dict[str, Any]] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def requires_multimodal(self) -> bool:
        """Check if request requires multimodal capabilities"""
        return bool(self.images or self.audio)
    
    @property
    def requires_function_calling(self) -> bool:
        """Check if request requires function calling"""
        return bool(self.functions)
    
    @property
    def task_type(self) -> TaskType:
        """Infer task type from request"""
        if self.requires_multimodal:
            return TaskType.MULTIMODAL
        if self.requires_function_calling:
            return TaskType.FUNCTION_CALLING
        if any(keyword in self.prompt.lower() for keyword in ['code', 'program', 'function', 'class']):
            return TaskType.CODE_GENERATION
        if any(keyword in self.prompt.lower() for keyword in ['analyze', 'explain', 'reason', 'logic']):
            return TaskType.REASONING
        if any(keyword in self.prompt.lower() for keyword in ['write', 'story', 'poem', 'creative']):
            return TaskType.CREATIVE_WRITING
        if any(keyword in self.prompt.lower() for keyword in ['summarize', 'summary']):
            return TaskType.SUMMARIZATION
        if any(keyword in self.prompt.lower() for keyword in ['translate', 'translation']):
            return TaskType.TRANSLATION
        return TaskType.GENERAL_CHAT


@dataclass
class LLMResponse:
    """Response from LLM provider"""
    content: str
    provider: str
    model: str
    prompt_tokens: Optional[int] = None
    completion_tokens: Optional[int] = None
    total_tokens: Optional[int] = None
    response_time: float = 0.0
    finish_reason: Optional[str] = None
    function_calls: Optional[List[Dict[str, Any]]] = None
    metadata: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def is_successful(self) -> bool:
        """Check if response was successful"""
        return self.error is None and bool(self.content)
    
    @property
    def tokens_per_second(self) -> float:
        """Calculate tokens per second"""
        if self.response_time > 0 and self.completion_tokens:
            return self.completion_tokens / self.response_time
        return 0.0
    
    @property
    def cost_estimate(self) -> Optional[float]:
        """Estimate cost if token counts are available"""
        # This would need provider-specific pricing
        return None


class LLMError(Exception):
    """Base exception for LLM provider errors"""
    
    def __init__(self, message: str, provider: str = None, error_code: str = None):
        super().__init__(message)
        self.provider = provider
        self.error_code = error_code


class LLMProvider(ABC):
    """
    Abstract base class for LLM providers
    """
    
    def __init__(self, provider_type: ProviderType):
        self.provider_type = provider_type
        self.request_count = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.error_count = 0
        self.avg_response_time = 0.0
    
    @abstractmethod
    def generate_response(self, request: LLMRequest) -> LLMResponse:
        """
        Generate response from the language model
        
        Args:
            request: LLM request with prompt and parameters
            
        Returns:
            LLM response with content and metadata
        """
        pass
    
    @abstractmethod
    def get_capabilities(self) -> ProviderCapabilities:
        """Get provider capabilities"""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models"""
        pass
    
    @abstractmethod
    def validate_request(self, request: LLMRequest) -> bool:
        """Validate if request is supported by this provider"""
        pass
    
    def stream_response(self, request: LLMRequest):
        """
        Stream response from the language model (optional)
        
        Args:
            request: LLM request with stream=True
            
        Yields:
            Partial LLM responses
        """
        # Default implementation falls back to non-streaming
        response = self.generate_response(request)
        yield response
    
    def estimate_cost(self, request: LLMRequest) -> float:
        """
        Estimate cost for the request
        
        Args:
            request: LLM request
            
        Returns:
            Estimated cost in USD
        """
        return 0.0  # Override in subclasses
    
    def get_stats(self) -> Dict[str, Any]:
        """Get provider statistics"""
        return {
            'provider_type': self.provider_type.value,
            'request_count': self.request_count,
            'total_tokens': self.total_tokens,
            'total_cost': self.total_cost,
            'error_count': self.error_count,
            'error_rate': self.error_count / max(1, self.request_count),
            'avg_response_time': self.avg_response_time
        }
    
    def _update_stats(self, response: LLMResponse):
        """Update provider statistics"""
        self.request_count += 1
        
        if response.is_successful:
            if response.total_tokens:
                self.total_tokens += response.total_tokens
            
            # Update average response time
            current_avg = self.avg_response_time
            self.avg_response_time = (
                (current_avg * (self.request_count - 1) + response.response_time) / self.request_count
            )
        else:
            self.error_count += 1
    
    def reset_stats(self):
        """Reset provider statistics"""
        self.request_count = 0
        self.total_tokens = 0
        self.total_cost = 0.0
        self.error_count = 0
        self.avg_response_time = 0.0


class BaseLLMProvider(LLMProvider):
    """
    Base implementation with common functionality
    """
    
    def __init__(self, 
                 provider_type: ProviderType,
                 api_key: Optional[str] = None,
                 base_url: Optional[str] = None,
                 default_model: Optional[str] = None):
        super().__init__(provider_type)
        self.api_key = api_key
        self.base_url = base_url
        self.default_model = default_model
        self._client = None
    
    def validate_request(self, request: LLMRequest) -> bool:
        """Basic request validation"""
        capabilities = self.get_capabilities()
        
        # Check multimodal support
        if request.requires_multimodal and not (capabilities.supports_vision or capabilities.supports_audio):
            return False
        
        # Check function calling support
        if request.requires_function_calling and not capabilities.supports_function_calling:
            return False
        
        # Check context length
        prompt_length = len(request.prompt)
        if request.system_prompt:
            prompt_length += len(request.system_prompt)
        
        # Rough token estimation (1 token ≈ 4 characters)
        estimated_tokens = prompt_length // 4
        if estimated_tokens > capabilities.max_context_length:
            return False
        
        return True
    
    def _prepare_request(self, request: LLMRequest) -> Dict[str, Any]:
        """Prepare request parameters for API call"""
        params = {
            'model': self.default_model,
            'messages': []
        }
        
        # Add system prompt if provided
        if request.system_prompt:
            params['messages'].append({
                'role': 'system',
                'content': request.system_prompt
            })
        
        # Add user prompt
        user_message = {'role': 'user', 'content': request.prompt}
        
        # Add images if supported
        if request.images and self.get_capabilities().supports_vision:
            user_message['images'] = request.images
        
        params['messages'].append(user_message)
        
        # Add optional parameters
        if request.temperature is not None:
            params['temperature'] = request.temperature
        
        if request.max_tokens is not None:
            params['max_tokens'] = request.max_tokens
        
        if request.top_p is not None:
            params['top_p'] = request.top_p
        
        if request.stop_sequences:
            params['stop'] = request.stop_sequences
        
        if request.stream:
            params['stream'] = True
        
        if request.json_mode and self.get_capabilities().supports_json_mode:
            params['response_format'] = {'type': 'json_object'}
        
        if request.functions and self.get_capabilities().supports_function_calling:
            params['functions'] = request.functions
        
        return params
    
    def _create_response(self, 
                        api_response: Any,
                        request: LLMRequest,
                        response_time: float) -> LLMResponse:
        """Create LLMResponse from API response"""
        # This should be overridden by specific providers
        return LLMResponse(
            content=str(api_response),
            provider=self.provider_type.value,
            model=self.default_model or "unknown",
            response_time=response_time
        )


# Provider factory function
def create_provider(provider_type: str, **kwargs) -> LLMProvider:
    """
    Factory function to create LLM providers
    
    Args:
        provider_type: Type of provider ("openai", "anthropic", etc.)
        **kwargs: Provider-specific configuration
        
    Returns:
        LLM provider instance
    """
    from .openai_provider import OpenAIProvider
    from .anthropic_provider import AnthropicProvider
    from .mistral_provider import MistralProvider
    from .ollama_provider import OllamaProvider
    
    providers = {
        'openai': OpenAIProvider,
        'anthropic': AnthropicProvider,
        'mistral': MistralProvider,
        'ollama': OllamaProvider
    }
    
    if provider_type not in providers:
        raise ValueError(f"Unknown provider type: {provider_type}")
    
    return providers[provider_type](**kwargs)