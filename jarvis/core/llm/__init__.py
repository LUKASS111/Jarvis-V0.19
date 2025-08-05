"""
LLM Provider Interface and Router System
Provides abstraction layer for multiple LLM providers with intelligent routing and fallback
"""

import logging
import time
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass, field
from enum import Enum
import json


class LLMProviderStatus(Enum):
    """LLM Provider status enumeration"""
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    ERROR = "error"
    RATE_LIMITED = "rate_limited"
    MAINTENANCE = "maintenance"


@dataclass
class Message:
    """Chat message structure"""
    role: str  # "system", "user", "assistant"
    content: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompletionRequest:
    """Request structure for LLM completion"""
    messages: List[Message]
    model: str
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class CompletionResponse:
    """Response structure from LLM completion"""
    content: str
    model: str
    provider: str
    usage: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    success: bool = True
    error: Optional[str] = None
    latency: float = 0.0
    timestamp: float = field(default_factory=time.time)


@dataclass
class EmbeddingRequest:
    """Request structure for embeddings"""
    text: str
    model: str
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class EmbeddingResponse:
    """Response structure from embedding"""
    embedding: List[float]
    model: str
    provider: str
    success: bool = True
    error: Optional[str] = None
    latency: float = 0.0
    timestamp: float = field(default_factory=time.time)


@dataclass
class HealthStatus:
    """Health status structure"""
    healthy: bool
    status: LLMProviderStatus
    message: str = ""
    latency: float = 0.0
    timestamp: float = field(default_factory=time.time)
    metadata: Dict[str, Any] = field(default_factory=dict)


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    def __init__(self, name: str, config: Dict[str, Any] = None):
        self.name = name
        self.config = config or {}
        self.logger = logging.getLogger(f"{__name__}.{name}")
        self.status = LLMProviderStatus.UNAVAILABLE
        self.supported_models: List[str] = []
        self.capabilities = set()
        self.rate_limits = {}
        
    @abstractmethod
    def chat_completion(self, request: CompletionRequest) -> CompletionResponse:
        """Generate chat completion"""
        pass
    
    def embedding(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Generate embeddings - optional for providers"""
        return EmbeddingResponse(
            embedding=[],
            model=request.model,
            provider=self.name,
            success=False,
            error="Embeddings not supported by this provider"
        )
    
    @abstractmethod
    def health_check(self) -> HealthStatus:
        """Check provider health"""
        pass
    
    def supports_model(self, model: str) -> bool:
        """Check if provider supports model"""
        return model in self.supported_models
    
    def supports_capability(self, capability: str) -> bool:
        """Check if provider supports capability"""
        return capability in self.capabilities
    
    def get_model_info(self, model: str) -> Dict[str, Any]:
        """Get information about a specific model"""
        return {
            "model": model,
            "provider": self.name,
            "supported": self.supports_model(model),
            "capabilities": list(self.capabilities)
        }
    
    def get_provider_info(self) -> Dict[str, Any]:
        """Get provider information"""
        return {
            "name": self.name,
            "status": self.status.value,
            "supported_models": self.supported_models,
            "capabilities": list(self.capabilities),
            "config": {k: v for k, v in self.config.items() if not k.startswith('_')}
        }


class LLMRouter:
    """Router for managing multiple LLM providers with intelligent selection"""
    
    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {}
        self.model_mapping: Dict[str, str] = {}  # model -> provider
        self.fallback_chains: Dict[str, List[str]] = {}
        self.load_balancing_strategy = "round_robin"
        self.provider_weights: Dict[str, float] = {}
        self.health_cache: Dict[str, HealthStatus] = {}
        self.health_cache_ttl = 60  # seconds
        self.logger = logging.getLogger(__name__)
        
    def register_provider(self, provider: LLMProvider, weight: float = 1.0) -> bool:
        """Register an LLM provider
        
        Args:
            provider: LLM provider instance
            weight: Provider weight for load balancing
            
        Returns:
            bool: True if registered successfully
        """
        try:
            self.providers[provider.name] = provider
            self.provider_weights[provider.name] = weight
            
            # Map models to provider
            for model in provider.supported_models:
                self.model_mapping[model] = provider.name
            
            self.logger.info(f"Registered LLM provider: {provider.name} with {len(provider.supported_models)} models")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to register provider {provider.name}: {e}")
            return False
    
    def get_provider(self, model: str = None, provider_name: str = None) -> Optional[LLMProvider]:
        """Get best available provider for model or by name
        
        Args:
            model: Model name to find provider for
            provider_name: Specific provider name
            
        Returns:
            LLMProvider or None if not found/available
        """
        if provider_name:
            provider = self.providers.get(provider_name)
            if provider and self._is_provider_healthy(provider_name):
                return provider
            return None
        
        if model:
            provider_name = self.model_mapping.get(model)
            if provider_name:
                provider = self.providers.get(provider_name)
                if provider and self._is_provider_healthy(provider_name):
                    return provider
        
        # Fallback to any healthy provider
        for provider_name, provider in self.providers.items():
            if self._is_provider_healthy(provider_name):
                return provider
        
        return None
    
    def chat_completion(self, request: CompletionRequest) -> CompletionResponse:
        """Execute chat completion with intelligent provider selection"""
        start_time = time.time()
        
        # Try primary provider
        provider = self.get_provider(model=request.model)
        if provider:
            try:
                response = provider.chat_completion(request)
                response.latency = time.time() - start_time
                return response
            except Exception as e:
                self.logger.warning(f"Primary provider {provider.name} failed: {e}")
        
        # Try fallback chain
        fallback_providers = self.fallback_chains.get(request.model, [])
        for fallback_provider_name in fallback_providers:
            provider = self.providers.get(fallback_provider_name)
            if provider and self._is_provider_healthy(fallback_provider_name):
                try:
                    # Adjust request for fallback provider if needed
                    fallback_request = self._adapt_request_for_provider(request, provider)
                    response = provider.chat_completion(fallback_request)
                    response.latency = time.time() - start_time
                    return response
                except Exception as e:
                    self.logger.warning(f"Fallback provider {provider.name} failed: {e}")
        
        # No providers available
        return CompletionResponse(
            content="",
            model=request.model,
            provider="none",
            success=False,
            error="No available providers for request",
            latency=time.time() - start_time
        )
    
    def embedding(self, request: EmbeddingRequest) -> EmbeddingResponse:
        """Execute embedding request with provider selection"""
        provider = self.get_provider(model=request.model)
        if provider:
            return provider.embedding(request)
        
        return EmbeddingResponse(
            embedding=[],
            model=request.model,
            provider="none",
            success=False,
            error="No available providers for embedding request"
        )
    
    def health_check_all(self) -> Dict[str, HealthStatus]:
        """Check health of all providers"""
        health_results = {}
        
        for provider_name, provider in self.providers.items():
            try:
                health = provider.health_check()
                health_results[provider_name] = health
                self.health_cache[provider_name] = health
            except Exception as e:
                health_results[provider_name] = HealthStatus(
                    healthy=False,
                    status=LLMProviderStatus.ERROR,
                    message=f"Health check failed: {e}"
                )
        
        return health_results
    
    def get_available_models(self) -> Dict[str, List[str]]:
        """Get all available models by provider"""
        models_by_provider = {}
        
        for provider_name, provider in self.providers.items():
            if self._is_provider_healthy(provider_name):
                models_by_provider[provider_name] = provider.supported_models
        
        return models_by_provider
    
    def set_fallback_chain(self, model: str, provider_chain: List[str]) -> bool:
        """Set fallback chain for a model
        
        Args:
            model: Model name
            provider_chain: List of provider names in fallback order
            
        Returns:
            bool: True if set successfully
        """
        # Validate providers exist
        for provider_name in provider_chain:
            if provider_name not in self.providers:
                self.logger.error(f"Cannot set fallback chain: provider {provider_name} not registered")
                return False
        
        self.fallback_chains[model] = provider_chain
        self.logger.info(f"Set fallback chain for {model}: {provider_chain}")
        return True
    
    def _is_provider_healthy(self, provider_name: str) -> bool:
        """Check if provider is healthy (with caching)"""
        # Check cache first
        if provider_name in self.health_cache:
            health = self.health_cache[provider_name]
            if time.time() - health.timestamp < self.health_cache_ttl:
                return health.healthy
        
        # Perform health check
        provider = self.providers.get(provider_name)
        if not provider:
            return False
        
        try:
            health = provider.health_check()
            self.health_cache[provider_name] = health
            return health.healthy
        except Exception as e:
            self.logger.warning(f"Health check failed for {provider_name}: {e}")
            return False
    
    def _adapt_request_for_provider(self, request: CompletionRequest, provider: LLMProvider) -> CompletionRequest:
        """Adapt request for specific provider capabilities"""
        # Create a copy of the request
        adapted_request = CompletionRequest(
            messages=request.messages.copy(),
            model=request.model,
            temperature=request.temperature,
            max_tokens=request.max_tokens,
            stream=request.stream,
            metadata=request.metadata.copy()
        )
        
        # Adapt model name if provider has different naming
        if request.model not in provider.supported_models and provider.supported_models:
            # Use first available model as fallback
            adapted_request.model = provider.supported_models[0]
            self.logger.info(f"Adapted model from {request.model} to {adapted_request.model} for provider {provider.name}")
        
        return adapted_request
    
    def get_router_status(self) -> Dict[str, Any]:
        """Get comprehensive router status"""
        health_results = self.health_check_all()
        
        healthy_providers = [name for name, health in health_results.items() if health.healthy]
        total_models = sum(len(provider.supported_models) for provider in self.providers.values())
        available_models = sum(len(provider.supported_models) for provider_name, provider in self.providers.items() 
                             if provider_name in healthy_providers)
        
        return {
            "total_providers": len(self.providers),
            "healthy_providers": len(healthy_providers),
            "total_models": total_models,
            "available_models": available_models,
            "provider_health": {name: health.healthy for name, health in health_results.items()},
            "fallback_chains": len(self.fallback_chains),
            "load_balancing_strategy": self.load_balancing_strategy
        }


# Global router instance
_llm_router: Optional[LLMRouter] = None


def get_llm_router() -> LLMRouter:
    """Get the global LLM router instance"""
    global _llm_router
    if _llm_router is None:
        _llm_router = LLMRouter()
    return _llm_router


def initialize_llm_system(providers: List[LLMProvider] = None) -> LLMRouter:
    """Initialize the LLM routing system
    
    Args:
        providers: List of LLM provider instances to register
        
    Returns:
        LLMRouter: Initialized router
    """
    global _llm_router
    _llm_router = LLMRouter()
    
    if providers:
        for provider in providers:
            _llm_router.register_provider(provider)
    
    return _llm_router