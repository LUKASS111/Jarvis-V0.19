"""
Anthropic Provider for Claude models
"""

import time
import logging
from typing import Dict, Any, List, Optional, Iterator

from .base import BaseLLMProvider, ProviderType, ProviderCapabilities, LLMRequest, LLMResponse, LLMError

logger = logging.getLogger(__name__)


class AnthropicProvider(BaseLLMProvider):
    """
    Anthropic provider supporting Claude models
    """
    
    def __init__(self, 
                 api_key: str = None,
                 base_url: str = None,
                 default_model: str = "claude-3-haiku-20240307"):
        """
        Initialize Anthropic provider
        
        Args:
            api_key: Anthropic API key
            base_url: Custom base URL for API
            default_model: Default model to use
        """
        super().__init__(
            provider_type=ProviderType.ANTHROPIC,
            api_key=api_key,
            base_url=base_url,
            default_model=default_model
        )
        
        # Model configurations
        self.model_configs = {
            "claude-3-opus-20240229": {
                "max_tokens": 200000,
                "supports_vision": True,
                "cost_per_1k_input": 0.015,
                "cost_per_1k_output": 0.075
            },
            "claude-3-sonnet-20240229": {
                "max_tokens": 200000,
                "supports_vision": True,
                "cost_per_1k_input": 0.003,
                "cost_per_1k_output": 0.015
            },
            "claude-3-haiku-20240307": {
                "max_tokens": 200000,
                "supports_vision": True,
                "cost_per_1k_input": 0.00025,
                "cost_per_1k_output": 0.00125
            }
        }
    
    def _get_client(self):
        """Get Anthropic client with lazy loading"""
        if self._client is None:
            try:
                import anthropic
                
                self._client = anthropic.Anthropic(
                    api_key=self.api_key,
                    base_url=self.base_url
                )
                
                logger.info("Anthropic client initialized successfully")
                
            except ImportError:
                raise ImportError("anthropic package not installed. Run: pip install anthropic")
            except Exception as e:
                logger.error(f"Failed to initialize Anthropic client: {e}")
                raise LLMError(f"Anthropic client initialization failed: {e}", "anthropic")
        
        return self._client
    
    def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate response using Anthropic API"""
        if not self.validate_request(request):
            return LLMResponse(
                content="",
                provider="anthropic",
                model=self.default_model,
                error="Request validation failed"
            )
        
        client = self._get_client()
        start_time = time.time()
        
        try:
            # Prepare API parameters
            params = self._prepare_anthropic_request(request)
            
            # Make API call
            response = client.messages.create(**params)
            return self._create_anthropic_response(response, request, time.time() - start_time)
        
        except Exception as e:
            logger.error(f"Anthropic API error: {e}")
            error_response = LLMResponse(
                content="",
                provider="anthropic",
                model=self.default_model,
                response_time=time.time() - start_time,
                error=str(e)
            )
            self._update_stats(error_response)
            return error_response
    
    def get_capabilities(self) -> ProviderCapabilities:
        """Get Anthropic provider capabilities"""
        model_config = self.model_configs.get(self.default_model, {})
        
        return ProviderCapabilities(
            supports_streaming=True,
            supports_function_calling=False,  # Not yet supported
            supports_vision=model_config.get("supports_vision", False),
            supports_audio=False,
            max_context_length=model_config.get("max_tokens", 200000),
            supports_system_prompt=True,
            supports_temperature=True,
            supports_top_p=True,
            supports_stop_sequences=True,
            supports_json_mode=False,
            rate_limit_rpm=1000,
            cost_per_1k_tokens=model_config.get("cost_per_1k_input", 0.001)
        )
    
    def get_available_models(self) -> List[str]:
        """Get list of available Anthropic models"""
        return list(self.model_configs.keys())
    
    def estimate_cost(self, request: LLMRequest) -> float:
        """Estimate cost for Anthropic request"""
        model_config = self.model_configs.get(self.default_model, {})
        
        # Rough token estimation
        input_tokens = (len(request.prompt) + len(request.system_prompt or "")) // 4
        output_tokens = (request.max_tokens or 512) // 2
        
        input_cost = (input_tokens / 1000) * model_config.get("cost_per_1k_input", 0.001)
        output_cost = (output_tokens / 1000) * model_config.get("cost_per_1k_output", 0.002)
        
        return input_cost + output_cost
    
    def _prepare_anthropic_request(self, request: LLMRequest) -> Dict[str, Any]:
        """Prepare request parameters for Anthropic API"""
        params = {
            "model": self.default_model,
            "max_tokens": request.max_tokens or 1024
        }
        
        # Handle system prompt
        if request.system_prompt:
            params["system"] = request.system_prompt
        
        # Prepare messages
        messages = []
        
        # Handle multimodal content
        if request.images and self.get_capabilities().supports_vision:
            content = [{"type": "text", "text": request.prompt}]
            
            for image in request.images:
                if image.startswith("http"):
                    # Note: Anthropic requires base64 images, not URLs
                    continue  # Skip URLs for now
                else:
                    content.append({
                        "type": "image",
                        "source": {
                            "type": "base64",
                            "media_type": "image/jpeg",
                            "data": image
                        }
                    })
            
            messages.append({"role": "user", "content": content})
        else:
            messages.append({"role": "user", "content": request.prompt})
        
        params["messages"] = messages
        
        # Optional parameters
        if request.temperature is not None:
            params["temperature"] = request.temperature
        
        if request.top_p is not None:
            params["top_p"] = request.top_p
        
        if request.stop_sequences:
            params["stop_sequences"] = request.stop_sequences
        
        return params
    
    def _create_anthropic_response(self, 
                                  api_response: Any,
                                  request: LLMRequest,
                                  response_time: float) -> LLMResponse:
        """Create LLMResponse from Anthropic API response"""
        try:
            # Extract content
            content = ""
            if api_response.content:
                for block in api_response.content:
                    if hasattr(block, 'text'):
                        content += block.text
            
            # Extract usage information
            usage = api_response.usage if hasattr(api_response, 'usage') else None
            
            response = LLMResponse(
                content=content,
                provider="anthropic",
                model=api_response.model,
                prompt_tokens=usage.input_tokens if usage else None,
                completion_tokens=usage.output_tokens if usage else None,
                total_tokens=(usage.input_tokens + usage.output_tokens) if usage else None,
                response_time=response_time,
                finish_reason=api_response.stop_reason,
                metadata={
                    "request_id": getattr(api_response, 'id', None),
                    "type": getattr(api_response, 'type', None)
                }
            )
            
            self._update_stats(response)
            return response
            
        except Exception as e:
            logger.error(f"Error parsing Anthropic response: {e}")
            return LLMResponse(
                content="",
                provider="anthropic",
                model=self.default_model,
                response_time=response_time,
                error=f"Response parsing error: {e}"
            )