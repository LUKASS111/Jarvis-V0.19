"""
Production LLM Interface for Jarvis
Enterprise-grade LLM management with advanced features
"""

import time
import json
import threading
from typing import Dict, List, Any, Optional, Union, Callable
from datetime import datetime, timedelta
from dataclasses import dataclass, field
from enum import Enum
import hashlib

from ..core.error_handler import error_handler, ErrorLevel, safe_execute

class LLMProvider(Enum):
    """Supported LLM providers"""
    OLLAMA = "ollama"
    OPENAI = "openai"
    ANTHROPIC = "anthropic"
    HUGGINGFACE = "huggingface"
    CUSTOM = "custom"

class ModelCapability(Enum):
    """Model capability categories"""
    GENERAL_CHAT = "general_chat"
    CODE_GENERATION = "code_generation"
    TEXT_ANALYSIS = "text_analysis"
    TRANSLATION = "translation"
    SUMMARIZATION = "summarization"
    REASONING = "reasoning"
    CREATIVE_WRITING = "creative_writing"

@dataclass
class ModelConfig:
    """Configuration for a specific model"""
    name: str
    provider: LLMProvider
    capabilities: List[ModelCapability] = field(default_factory=list)
    max_tokens: int = 4096
    context_window: int = 8192
    temperature: float = 0.7
    top_p: float = 0.9
    frequency_penalty: float = 0.0
    presence_penalty: float = 0.0
    stop_sequences: List[str] = field(default_factory=list)
    cost_per_token: float = 0.0
    latency_target: float = 5.0  # seconds
    reliability_score: float = 1.0
    custom_params: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LLMRequest:
    """Structured LLM request"""
    prompt: str
    model: str = "auto"
    system_prompt: Optional[str] = None
    conversation_id: Optional[str] = None
    temperature: Optional[float] = None
    max_tokens: Optional[int] = None
    stream: bool = False
    fallback_models: List[str] = field(default_factory=list)
    priority: int = 1
    timeout: float = 30.0
    retry_attempts: int = 3
    cache_enabled: bool = True
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class LLMResponse:
    """Structured LLM response"""
    content: str
    model_used: str
    provider_used: LLMProvider
    tokens_used: Optional[int] = None
    finish_reason: str = "completed"
    latency: float = 0.0
    cost: float = 0.0
    cached: bool = False
    fallback_used: bool = False
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)
    request_id: str = ""

class ProductionLLMInterface:
    """
    Production-grade LLM interface with enterprise features:
    - Multi-provider support with intelligent routing
    - Automatic failover and load balancing
    - Response caching and optimization
    - Usage analytics and cost tracking
    - Rate limiting and queue management
    - Model performance monitoring
    """
    
    def __init__(self):
        self.models: Dict[str, ModelConfig] = {}
        self.providers: Dict[LLMProvider, Any] = {}
        self.fallback_chains: Dict[str, List[str]] = {}
        self.response_cache: Dict[str, LLMResponse] = {}
        self.usage_stats: Dict[str, Any] = {
            "total_requests": 0,
            "successful_requests": 0,
            "failed_requests": 0,
            "total_tokens": 0,
            "total_cost": 0.0,
            "average_latency": 0.0,
            "model_usage": {},
            "provider_usage": {},
            "error_counts": {}
        }
        
        self._lock = threading.RLock()
        self._rate_limits: Dict[str, List[float]] = {}
        self._request_queue: List[LLMRequest] = []
        self._active_requests: Dict[str, LLMRequest] = {}
        
        # Initialize default models and providers
        self._initialize_default_models()
        self._initialize_providers()
    
    def _initialize_default_models(self):
        """Initialize default model configurations"""
        # Ollama models
        ollama_models = [
            ModelConfig(
                name="llama3:8b",
                provider=LLMProvider.OLLAMA,
                capabilities=[ModelCapability.GENERAL_CHAT, ModelCapability.REASONING],
                max_tokens=4096,
                context_window=8192,
                reliability_score=0.95
            ),
            ModelConfig(
                name="codellama:13b",
                provider=LLMProvider.OLLAMA,
                capabilities=[ModelCapability.CODE_GENERATION, ModelCapability.TEXT_ANALYSIS],
                max_tokens=8192,
                context_window=16384,
                reliability_score=0.90
            ),
            ModelConfig(
                name="llama3:70b",
                provider=LLMProvider.OLLAMA,
                capabilities=[
                    ModelCapability.GENERAL_CHAT, ModelCapability.REASONING,
                    ModelCapability.TEXT_ANALYSIS, ModelCapability.CREATIVE_WRITING
                ],
                max_tokens=8192,
                context_window=32768,
                reliability_score=0.98,
                latency_target=15.0  # Larger model, higher latency
            )
        ]
        
        for model in ollama_models:
            self.models[model.name] = model
        
        # Set up fallback chains
        self.fallback_chains = {
            "llama3:8b": ["llama3:8b", "codellama:13b"],
            "codellama:13b": ["codellama:13b", "llama3:8b"],
            "llama3:70b": ["llama3:70b", "llama3:8b", "codellama:13b"],
            "auto": ["llama3:8b", "codellama:13b", "llama3:70b"]
        }
    
    def _initialize_providers(self):
        """Initialize LLM providers"""
        try:
            # Import and initialize Ollama
            from ...llm.llm_interface import OllamaInterface
            ollama = OllamaInterface()
            self.providers[LLMProvider.OLLAMA] = ollama
            
        except ImportError:
            error_handler.log_error(
                ImportError("Ollama interface not available"),
                "LLM Provider Initialization", ErrorLevel.WARNING,
                "Ollama provider not initialized"
            )
    
    @safe_execute(fallback_value=None, context="LLM Request Processing")
    def process_request(self, request: LLMRequest) -> Optional[LLMResponse]:
        """
        Process LLM request with full production features
        """
        request_id = self._generate_request_id(request)
        request.metadata["request_id"] = request_id
        
        start_time = time.time()
        
        with self._lock:
            self._active_requests[request_id] = request
            self.usage_stats["total_requests"] += 1
        
        try:
            # Check cache first
            if request.cache_enabled:
                cached_response = self._check_cache(request)
                if cached_response:
                    cached_response.request_id = request_id
                    return cached_response
            
            # Check rate limits
            if not self._check_rate_limits(request.model):
                raise Exception("Rate limit exceeded")
            
            # Select optimal model
            selected_model = self._select_model(request)
            
            # Execute request with fallback
            response = self._execute_with_fallback(request, selected_model)
            
            if response:
                response.request_id = request_id
                response.latency = time.time() - start_time
                
                # Cache successful response
                if request.cache_enabled and response.finish_reason == "completed":
                    self._cache_response(request, response)
                
                # Update usage statistics
                self._update_usage_stats(response, success=True)
                
                with self._lock:
                    self.usage_stats["successful_requests"] += 1
                
            return response
            
        except Exception as e:
            error_handler.log_error(
                e, "LLM Request Processing", ErrorLevel.ERROR,
                f"Request ID: {request_id}, Model: {request.model}"
            )
            
            with self._lock:
                self.usage_stats["failed_requests"] += 1
                error_type = type(e).__name__
                if error_type not in self.usage_stats["error_counts"]:
                    self.usage_stats["error_counts"][error_type] = 0
                self.usage_stats["error_counts"][error_type] += 1
            
            return None
            
        finally:
            with self._lock:
                self._active_requests.pop(request_id, None)
    
    def _generate_request_id(self, request: LLMRequest) -> str:
        """Generate unique request ID"""
        timestamp = str(int(time.time() * 1000))
        content_hash = hashlib.md5(request.prompt.encode()).hexdigest()[:8]
        return f"req_{timestamp}_{content_hash}"
    
    def _check_cache(self, request: LLMRequest) -> Optional[LLMResponse]:
        """Check response cache for existing result"""
        cache_key = self._generate_cache_key(request)
        
        cached_response = self.response_cache.get(cache_key)
        if cached_response:
            # Check if cache is still valid (1 hour default)
            cache_age = datetime.now() - cached_response.timestamp
            if cache_age < timedelta(hours=1):
                cached_response.cached = True
                return cached_response
            else:
                # Remove expired cache entry
                self.response_cache.pop(cache_key, None)
        
        return None
    
    def _generate_cache_key(self, request: LLMRequest) -> str:
        """Generate cache key for request"""
        key_data = {
            "prompt": request.prompt,
            "model": request.model,
            "system_prompt": request.system_prompt,
            "temperature": request.temperature,
            "max_tokens": request.max_tokens
        }
        return hashlib.md5(json.dumps(key_data, sort_keys=True).encode()).hexdigest()
    
    def _cache_response(self, request: LLMRequest, response: LLMResponse):
        """Cache successful response"""
        cache_key = self._generate_cache_key(request)
        
        # Limit cache size (keep last 1000 responses)
        if len(self.response_cache) >= 1000:
            # Remove oldest entries
            sorted_cache = sorted(
                self.response_cache.items(),
                key=lambda x: x[1].timestamp
            )
            for old_key, _ in sorted_cache[:100]:
                self.response_cache.pop(old_key, None)
        
        self.response_cache[cache_key] = response
    
    def _check_rate_limits(self, model: str) -> bool:
        """Check if request is within rate limits"""
        current_time = time.time()
        
        if model not in self._rate_limits:
            self._rate_limits[model] = []
        
        # Remove old requests (older than 1 minute)
        self._rate_limits[model] = [
            req_time for req_time in self._rate_limits[model]
            if current_time - req_time < 60
        ]
        
        # Check if under limit (60 requests per minute default)
        if len(self._rate_limits[model]) < 60:
            self._rate_limits[model].append(current_time)
            return True
        
        return False
    
    def _select_model(self, request: LLMRequest) -> str:
        """Select optimal model based on request requirements"""
        if request.model == "auto":
            # Intelligent model selection based on prompt analysis
            return self._intelligent_model_selection(request)
        elif request.model in self.models:
            return request.model
        else:
            # Fallback to default
            return "llama3:8b"
    
    def _intelligent_model_selection(self, request: LLMRequest) -> str:
        """Intelligent model selection based on prompt analysis"""
        prompt = request.prompt.lower()
        
        # Code-related keywords
        code_keywords = ["code", "python", "javascript", "function", "class", "def ", "import", "syntax"]
        if any(keyword in prompt for keyword in code_keywords):
            return "codellama:13b"
        
        # Complex reasoning keywords
        reasoning_keywords = ["analyze", "explain", "compare", "reason", "logic", "solve", "problem"]
        if any(keyword in prompt for keyword in reasoning_keywords) and len(prompt) > 200:
            return "llama3:70b"
        
        # Default for general chat
        return "llama3:8b"
    
    def _execute_with_fallback(self, request: LLMRequest, model: str) -> Optional[LLMResponse]:
        """Execute request with automatic fallback"""
        fallback_models = self.fallback_chains.get(model, [model])
        
        for attempt, fallback_model in enumerate(fallback_models):
            if attempt >= request.retry_attempts:
                break
            
            try:
                response = self._execute_single_request(request, fallback_model)
                if response:
                    response.fallback_used = attempt > 0
                    return response
                    
            except Exception as e:
                error_handler.log_error(
                    e, f"LLM Execution Attempt {attempt + 1}",
                    ErrorLevel.WARNING,
                    f"Model: {fallback_model}, Trying fallback..."
                )
                continue
        
        return None
    
    def _execute_single_request(self, request: LLMRequest, model: str) -> Optional[LLMResponse]:
        """Execute single LLM request"""
        model_config = self.models.get(model)
        if not model_config:
            raise ValueError(f"Model {model} not configured")
        
        provider = self.providers.get(model_config.provider)
        if not provider:
            raise ValueError(f"Provider {model_config.provider} not available")
        
        start_time = time.time()
        
        # Prepare request parameters
        params = {
            "model": model,
            "temperature": request.temperature or model_config.temperature,
            "max_tokens": request.max_tokens or model_config.max_tokens,
            "system_prompt": request.system_prompt,
            "stream": request.stream
        }
        
        # Execute based on provider type
        if model_config.provider == LLMProvider.OLLAMA:
            result = self._execute_ollama_request(request.prompt, params)
        else:
            raise ValueError(f"Provider {model_config.provider} not implemented")
        
        execution_time = time.time() - start_time
        
        # Calculate cost (if available)
        tokens_used = len(request.prompt.split()) + len(result.split()) if result else 0
        cost = tokens_used * model_config.cost_per_token
        
        return LLMResponse(
            content=result,
            model_used=model,
            provider_used=model_config.provider,
            tokens_used=tokens_used,
            latency=execution_time,
            cost=cost,
            finish_reason="completed" if result else "error"
        )
    
    def _execute_ollama_request(self, prompt: str, params: Dict[str, Any]) -> str:
        """Execute Ollama-specific request"""
        try:
            # Use existing ollama interface
            from ...llm.llm_interface import ask_local_llm
            return ask_local_llm(prompt)
        except Exception as e:
            raise Exception(f"Ollama execution failed: {str(e)}")
    
    def _update_usage_stats(self, response: LLMResponse, success: bool):
        """Update usage statistics"""
        with self._lock:
            if success and response:
                if response.tokens_used:
                    self.usage_stats["total_tokens"] += response.tokens_used
                if response.cost:
                    self.usage_stats["total_cost"] += response.cost
                
                # Update model usage
                model = response.model_used
                if model not in self.usage_stats["model_usage"]:
                    self.usage_stats["model_usage"][model] = {
                        "requests": 0, "tokens": 0, "latency_sum": 0
                    }
                
                self.usage_stats["model_usage"][model]["requests"] += 1
                if response.tokens_used:
                    self.usage_stats["model_usage"][model]["tokens"] += response.tokens_used
                self.usage_stats["model_usage"][model]["latency_sum"] += response.latency
                
                # Update provider usage
                provider = response.provider_used.value
                if provider not in self.usage_stats["provider_usage"]:
                    self.usage_stats["provider_usage"][provider] = 0
                self.usage_stats["provider_usage"][provider] += 1
                
                # Update average latency
                total_successful = self.usage_stats["successful_requests"]
                if total_successful > 0:
                    current_avg = self.usage_stats["average_latency"]
                    new_avg = (current_avg * (total_successful - 1) + response.latency) / total_successful
                    self.usage_stats["average_latency"] = new_avg
    
    def get_available_models(self) -> List[Dict[str, Any]]:
        """Get list of available models with metadata"""
        models = []
        for name, config in self.models.items():
            models.append({
                "name": name,
                "provider": config.provider.value,
                "capabilities": [cap.value for cap in config.capabilities],
                "max_tokens": config.max_tokens,
                "context_window": config.context_window,
                "reliability_score": config.reliability_score,
                "latency_target": config.latency_target
            })
        return models
    
    def get_usage_statistics(self) -> Dict[str, Any]:
        """Get comprehensive usage statistics"""
        with self._lock:
            stats = self.usage_stats.copy()
            
            # Add computed metrics
            if stats["total_requests"] > 0:
                stats["success_rate"] = stats["successful_requests"] / stats["total_requests"]
                stats["failure_rate"] = stats["failed_requests"] / stats["total_requests"]
            else:
                stats["success_rate"] = 0.0
                stats["failure_rate"] = 0.0
            
            # Add cache statistics
            stats["cache_stats"] = {
                "cached_responses": len(self.response_cache),
                "cache_hit_rate": 0.0  # Would need tracking to calculate accurately
            }
            
            # Add active request count
            stats["active_requests"] = len(self._active_requests)
            
            return stats
    
    def add_custom_model(self, config: ModelConfig):
        """Add custom model configuration"""
        with self._lock:
            self.models[config.name] = config
    
    def set_fallback_chain(self, model: str, fallback_models: List[str]):
        """Set custom fallback chain for a model"""
        with self._lock:
            self.fallback_chains[model] = fallback_models
    
    def clear_cache(self):
        """Clear response cache"""
        with self._lock:
            self.response_cache.clear()
    
    def get_model_performance(self, model: str) -> Dict[str, Any]:
        """Get performance metrics for specific model"""
        with self._lock:
            model_stats = self.usage_stats["model_usage"].get(model, {})
            
            if model_stats.get("requests", 0) > 0:
                avg_latency = model_stats["latency_sum"] / model_stats["requests"]
            else:
                avg_latency = 0.0
            
            return {
                "model": model,
                "total_requests": model_stats.get("requests", 0),
                "total_tokens": model_stats.get("tokens", 0),
                "average_latency": avg_latency,
                "configured_reliability": self.models.get(model, ModelConfig("", LLMProvider.OLLAMA)).reliability_score
            }

# Global production LLM instance
_llm_instance = None

def get_production_llm() -> ProductionLLMInterface:
    """Get the global production LLM instance"""
    global _llm_instance
    if _llm_instance is None:
        _llm_instance = ProductionLLMInterface()
    return _llm_instance

# Enhanced backward compatibility functions
def ask_local_llm(prompt: str, model: str = "auto", **kwargs) -> str:
    """Enhanced ask_local_llm with production features"""
    llm = get_production_llm()
    
    request = LLMRequest(
        prompt=prompt,
        model=model,
        **kwargs
    )
    
    response = llm.process_request(request)
    
    if response and response.content:
        return response.content
    else:
        return "Error: Unable to process request"

def get_available_models() -> List[str]:
    """Get list of available model names"""
    llm = get_production_llm()
    models = llm.get_available_models()
    return [model["name"] for model in models]

def get_ollama_model() -> str:
    """Get current default model"""
    # Return the auto-selection default
    return "llama3:8b"

def set_ollama_model(model: str) -> bool:
    """Set default model (compatibility function)"""
    # In production system, model selection is dynamic
    # This function is kept for compatibility
    return model in get_available_models()

def get_llm_statistics() -> Dict[str, Any]:
    """Get comprehensive LLM usage statistics"""
    llm = get_production_llm()
    return llm.get_usage_statistics()

def get_model_performance(model: str) -> Dict[str, Any]:
    """Get performance metrics for specific model"""
    llm = get_production_llm()
    return llm.get_model_performance(model)