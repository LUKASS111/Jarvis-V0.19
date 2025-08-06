"""
OpenAI Provider for GPT-4o and other OpenAI models
"""

import time
import logging
from typing import Dict, Any, List, Optional, Iterator

from .base import BaseLLMProvider, ProviderType, ProviderCapabilities, LLMRequest, LLMResponse, LLMError

logger = logging.getLogger(__name__)


class OpenAIProvider(BaseLLMProvider):
    """
    OpenAI provider supporting GPT-4o, GPT-4, GPT-3.5, and other models
    """
    
    def __init__(self, 
                 api_key: str = None,
                 organization: str = None,
                 base_url: str = None,
                 default_model: str = "gpt-4o"):
        """
        Initialize OpenAI provider
        
        Args:
            api_key: OpenAI API key
            organization: OpenAI organization ID
            base_url: Custom base URL for API
            default_model: Default model to use
        """
        super().__init__(
            provider_type=ProviderType.OPENAI,
            api_key=api_key,
            base_url=base_url,
            default_model=default_model
        )
        self.organization = organization
        
        # Model configurations
        self.model_configs = {
            "gpt-4o": {
                "max_tokens": 128000,
                "supports_vision": True,
                "supports_function_calling": True,
                "cost_per_1k_input": 0.005,
                "cost_per_1k_output": 0.015
            },
            "gpt-4o-mini": {
                "max_tokens": 128000,
                "supports_vision": True,
                "supports_function_calling": True,
                "cost_per_1k_input": 0.00015,
                "cost_per_1k_output": 0.0006
            },
            "gpt-4-turbo": {
                "max_tokens": 128000,
                "supports_vision": True,
                "supports_function_calling": True,
                "cost_per_1k_input": 0.01,
                "cost_per_1k_output": 0.03
            },
            "gpt-4": {
                "max_tokens": 8192,
                "supports_vision": False,
                "supports_function_calling": True,
                "cost_per_1k_input": 0.03,
                "cost_per_1k_output": 0.06
            },
            "gpt-3.5-turbo": {
                "max_tokens": 16385,
                "supports_vision": False,
                "supports_function_calling": True,
                "cost_per_1k_input": 0.0005,
                "cost_per_1k_output": 0.0015
            }
        }
    
    def _get_client(self):
        """Get OpenAI client with lazy loading"""
        if self._client is None:
            try:
                import openai
                
                self._client = openai.OpenAI(
                    api_key=self.api_key,
                    organization=self.organization,
                    base_url=self.base_url
                )
                
                logger.info("OpenAI client initialized successfully")
                
            except ImportError:
                raise ImportError("openai package not installed. Run: pip install openai")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {e}")
                raise LLMError(f"OpenAI client initialization failed: {e}", "openai")
        
        return self._client
    
    def generate_response(self, request: LLMRequest) -> LLMResponse:
        """Generate response using OpenAI API"""
        if not self.validate_request(request):
            return LLMResponse(
                content="",
                provider="openai",
                model=self.default_model,
                error="Request validation failed"
            )
        
        client = self._get_client()
        start_time = time.time()
        
        try:
            # Prepare API parameters
            params = self._prepare_openai_request(request)
            
            # Make API call
            if request.stream:
                return self._handle_streaming_response(client, params, request, start_time)
            else:
                response = client.chat.completions.create(**params)
                return self._create_openai_response(response, request, time.time() - start_time)
        
        except Exception as e:
            logger.error(f"OpenAI API error: {e}")
            error_response = LLMResponse(
                content="",
                provider="openai",
                model=self.default_model,
                response_time=time.time() - start_time,
                error=str(e)
            )
            self._update_stats(error_response)
            return error_response
    
    def stream_response(self, request: LLMRequest) -> Iterator[LLMResponse]:
        """Stream response from OpenAI API"""
        request.stream = True
        
        client = self._get_client()
        start_time = time.time()
        
        try:
            params = self._prepare_openai_request(request)
            stream = client.chat.completions.create(**params)
            
            accumulated_content = ""
            
            for chunk in stream:
                if chunk.choices and chunk.choices[0].delta.content:
                    content_delta = chunk.choices[0].delta.content
                    accumulated_content += content_delta
                    
                    yield LLMResponse(
                        content=content_delta,
                        provider="openai",
                        model=self.default_model,
                        response_time=time.time() - start_time,
                        metadata={"is_partial": True, "accumulated_content": accumulated_content}
                    )
            
            # Final response
            final_response = LLMResponse(
                content=accumulated_content,
                provider="openai",
                model=self.default_model,
                response_time=time.time() - start_time,
                metadata={"is_final": True}
            )
            
            self._update_stats(final_response)
            yield final_response
            
        except Exception as e:
            logger.error(f"OpenAI streaming error: {e}")
            yield LLMResponse(
                content="",
                provider="openai",
                model=self.default_model,
                response_time=time.time() - start_time,
                error=str(e)
            )
    
    def get_capabilities(self) -> ProviderCapabilities:
        """Get OpenAI provider capabilities"""
        model_config = self.model_configs.get(self.default_model, {})
        
        return ProviderCapabilities(
            supports_streaming=True,
            supports_function_calling=model_config.get("supports_function_calling", True),
            supports_vision=model_config.get("supports_vision", False),
            supports_audio=False,  # Not yet supported in chat completions
            max_context_length=model_config.get("max_tokens", 4096),
            supports_system_prompt=True,
            supports_temperature=True,
            supports_top_p=True,
            supports_stop_sequences=True,
            supports_json_mode=True,
            rate_limit_rpm=3500,  # Typical rate limit
            cost_per_1k_tokens=model_config.get("cost_per_1k_input", 0.001)
        )
    
    def get_available_models(self) -> List[str]:
        """Get list of available OpenAI models"""
        return list(self.model_configs.keys())
    
    def estimate_cost(self, request: LLMRequest) -> float:
        """Estimate cost for OpenAI request"""
        model_config = self.model_configs.get(self.default_model, {})
        
        # Rough token estimation (1 token ≈ 4 characters for English)
        input_tokens = (len(request.prompt) + len(request.system_prompt or "")) // 4
        output_tokens = (request.max_tokens or 512) // 2  # Estimate half of max
        
        input_cost = (input_tokens / 1000) * model_config.get("cost_per_1k_input", 0.001)
        output_cost = (output_tokens / 1000) * model_config.get("cost_per_1k_output", 0.002)
        
        return input_cost + output_cost
    
    def _prepare_openai_request(self, request: LLMRequest) -> Dict[str, Any]:
        """Prepare request parameters for OpenAI API"""
        messages = []
        
        # Add system prompt
        if request.system_prompt:
            messages.append({
                "role": "system",
                "content": request.system_prompt
            })
        
        # Prepare user message
        user_message = {"role": "user"}
        
        # Handle multimodal content
        if request.images and self.get_capabilities().supports_vision:
            content = [{"type": "text", "text": request.prompt}]
            
            for image in request.images:
                if image.startswith("http"):
                    # URL image
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": image}
                    })
                else:
                    # Base64 image
                    content.append({
                        "type": "image_url",
                        "image_url": {"url": f"data:image/jpeg;base64,{image}"}
                    })
            
            user_message["content"] = content
        else:
            user_message["content"] = request.prompt
        
        messages.append(user_message)
        
        # Basic parameters
        params = {
            "model": self.default_model,
            "messages": messages
        }
        
        # Optional parameters
        if request.temperature is not None:
            params["temperature"] = request.temperature
        
        if request.max_tokens is not None:
            params["max_tokens"] = request.max_tokens
        
        if request.top_p is not None:
            params["top_p"] = request.top_p
        
        if request.stop_sequences:
            params["stop"] = request.stop_sequences
        
        if request.stream:
            params["stream"] = True
        
        if request.json_mode:
            params["response_format"] = {"type": "json_object"}
        
        if request.functions:
            params["functions"] = request.functions
            params["function_call"] = "auto"
        
        return params
    
    def _create_openai_response(self, 
                               api_response: Any,
                               request: LLMRequest,
                               response_time: float) -> LLMResponse:
        """Create LLMResponse from OpenAI API response"""
        try:
            choice = api_response.choices[0]
            
            # Extract content
            content = choice.message.content or ""
            
            # Extract function calls if present
            function_calls = None
            if hasattr(choice.message, 'function_call') and choice.message.function_call:
                function_calls = [{
                    "name": choice.message.function_call.name,
                    "arguments": choice.message.function_call.arguments
                }]
            
            # Extract usage information
            usage = api_response.usage if hasattr(api_response, 'usage') else None
            
            response = LLMResponse(
                content=content,
                provider="openai",
                model=api_response.model,
                prompt_tokens=usage.prompt_tokens if usage else None,
                completion_tokens=usage.completion_tokens if usage else None,
                total_tokens=usage.total_tokens if usage else None,
                response_time=response_time,
                finish_reason=choice.finish_reason,
                function_calls=function_calls,
                metadata={
                    "request_id": getattr(api_response, 'id', None),
                    "created": getattr(api_response, 'created', None)
                }
            )
            
            self._update_stats(response)
            return response
            
        except Exception as e:
            logger.error(f"Error parsing OpenAI response: {e}")
            return LLMResponse(
                content="",
                provider="openai",
                model=self.default_model,
                response_time=response_time,
                error=f"Response parsing error: {e}"
            )
    
    def _handle_streaming_response(self, 
                                  client, 
                                  params: Dict[str, Any],
                                  request: LLMRequest,
                                  start_time: float) -> LLMResponse:
        """Handle streaming response (fallback for non-streaming interface)"""
        # Remove stream parameter for regular completion
        params["stream"] = False
        
        response = client.chat.completions.create(**params)
        return self._create_openai_response(response, request, time.time() - start_time)