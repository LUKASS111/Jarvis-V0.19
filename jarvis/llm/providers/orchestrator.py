"""
LLM Orchestrator for intelligent provider selection and task routing
"""

import time
import logging
from typing import Dict, Any, List, Optional, Union
from dataclasses import dataclass
from enum import Enum

from .base import LLMProvider, LLMRequest, LLMResponse, TaskType, ProviderType

logger = logging.getLogger(__name__)


@dataclass
class ProviderScore:
    """Score for provider selection"""
    provider: LLMProvider
    score: float
    reasoning: str
    estimated_cost: float
    estimated_time: float


class TaskRouter:
    """
    Intelligent task routing for LLM providers
    """
    
    def __init__(self):
        self.routing_rules = {
            TaskType.MULTIMODAL: {
                'preferred_providers': [ProviderType.OPENAI],
                'requirements': ['supports_vision'],
                'weight_factors': {'capability': 0.6, 'cost': 0.2, 'speed': 0.2}
            },
            TaskType.FUNCTION_CALLING: {
                'preferred_providers': [ProviderType.OPENAI],
                'requirements': ['supports_function_calling'],
                'weight_factors': {'capability': 0.7, 'cost': 0.1, 'speed': 0.2}
            },
            TaskType.REASONING: {
                'preferred_providers': [ProviderType.ANTHROPIC, ProviderType.OPENAI],
                'requirements': [],
                'weight_factors': {'capability': 0.8, 'cost': 0.1, 'speed': 0.1}
            },
            TaskType.CODE_GENERATION: {
                'preferred_providers': [ProviderType.OPENAI, ProviderType.OLLAMA],
                'requirements': [],
                'weight_factors': {'capability': 0.6, 'cost': 0.3, 'speed': 0.1}
            },
            TaskType.CREATIVE_WRITING: {
                'preferred_providers': [ProviderType.ANTHROPIC, ProviderType.OPENAI],
                'requirements': [],
                'weight_factors': {'capability': 0.7, 'cost': 0.2, 'speed': 0.1}
            },
            TaskType.GENERAL_CHAT: {
                'preferred_providers': [ProviderType.OLLAMA, ProviderType.OPENAI],
                'requirements': [],
                'weight_factors': {'capability': 0.4, 'cost': 0.4, 'speed': 0.2}
            }
        }
    
    def select_provider(self, 
                       request: LLMRequest,
                       available_providers: List[LLMProvider],
                       preferences: Dict[str, Any] = None) -> Optional[LLMProvider]:
        """
        Select best provider for the request
        
        Args:
            request: LLM request
            available_providers: List of available providers
            preferences: User preferences (cost_priority, speed_priority, etc.)
            
        Returns:
            Selected LLM provider or None
        """
        if not available_providers:
            return None
        
        task_type = request.task_type
        routing_rule = self.routing_rules.get(task_type, self.routing_rules[TaskType.GENERAL_CHAT])
        
        # Score all providers
        provider_scores = []
        
        for provider in available_providers:
            score = self._score_provider(provider, request, routing_rule, preferences or {})
            if score.score > 0:  # Only consider viable providers
                provider_scores.append(score)
        
        if not provider_scores:
            # Fallback to first available provider
            logger.warning(f"No suitable providers found for {task_type}, using first available")
            return available_providers[0]
        
        # Sort by score and return best
        provider_scores.sort(key=lambda x: x.score, reverse=True)
        best_provider = provider_scores[0]
        
        logger.info(f"Selected {best_provider.provider.provider_type.value} for {task_type} "
                   f"(score: {best_provider.score:.2f}, reason: {best_provider.reasoning})")
        
        return best_provider.provider
    
    def _score_provider(self, 
                       provider: LLMProvider,
                       request: LLMRequest,
                       routing_rule: Dict[str, Any],
                       preferences: Dict[str, Any]) -> ProviderScore:
        """Score a provider for the given request"""
        
        capabilities = provider.get_capabilities()
        
        # Check requirements
        requirements = routing_rule.get('requirements', [])
        for requirement in requirements:
            if not getattr(capabilities, requirement, False):
                return ProviderScore(
                    provider=provider,
                    score=0.0,
                    reasoning=f"Missing required capability: {requirement}",
                    estimated_cost=0.0,
                    estimated_time=0.0
                )
        
        # Check if provider can handle the request
        if not provider.validate_request(request):
            return ProviderScore(
                provider=provider,
                score=0.0,
                reasoning="Request validation failed",
                estimated_cost=0.0,
                estimated_time=0.0
            )
        
        # Calculate capability score
        capability_score = self._calculate_capability_score(
            provider, request, routing_rule
        )
        
        # Calculate cost score
        estimated_cost = provider.estimate_cost(request)
        cost_score = self._calculate_cost_score(estimated_cost, preferences)
        
        # Calculate speed score
        estimated_time = self._estimate_response_time(provider, request)
        speed_score = self._calculate_speed_score(estimated_time, preferences)
        
        # Weighted final score
        weight_factors = routing_rule.get('weight_factors', {})
        final_score = (
            capability_score * weight_factors.get('capability', 0.5) +
            cost_score * weight_factors.get('cost', 0.3) +
            speed_score * weight_factors.get('speed', 0.2)
        )
        
        # Apply user preferences
        if preferences.get('cost_priority') == 'high':
            final_score = final_score * 0.7 + cost_score * 0.3
        elif preferences.get('speed_priority') == 'high':
            final_score = final_score * 0.7 + speed_score * 0.3
        
        reasoning = f"capability: {capability_score:.2f}, cost: {cost_score:.2f}, speed: {speed_score:.2f}"
        
        return ProviderScore(
            provider=provider,
            score=final_score,
            reasoning=reasoning,
            estimated_cost=estimated_cost,
            estimated_time=estimated_time
        )
    
    def _calculate_capability_score(self, 
                                   provider: LLMProvider,
                                   request: LLMRequest,
                                   routing_rule: Dict[str, Any]) -> float:
        """Calculate capability score for provider"""
        score = 0.5  # Base score
        
        capabilities = provider.get_capabilities()
        provider_type = provider.provider_type
        
        # Preference bonus
        preferred_providers = routing_rule.get('preferred_providers', [])
        if provider_type in preferred_providers:
            score += 0.3
        
        # Feature support bonuses
        if request.requires_multimodal and capabilities.supports_vision:
            score += 0.2
        
        if request.requires_function_calling and capabilities.supports_function_calling:
            score += 0.2
        
        # Context length consideration
        if capabilities.max_context_length >= 32000:
            score += 0.1
        elif capabilities.max_context_length >= 8000:
            score += 0.05
        
        return min(1.0, score)
    
    def _calculate_cost_score(self, estimated_cost: float, preferences: Dict[str, Any]) -> float:
        """Calculate cost score (higher score = lower cost)"""
        if estimated_cost == 0.0:
            return 1.0  # Free is best
        
        # Normalize cost score (assuming $0.10 as expensive)
        normalized_cost = min(estimated_cost / 0.10, 1.0)
        return 1.0 - normalized_cost
    
    def _calculate_speed_score(self, estimated_time: float, preferences: Dict[str, Any]) -> float:
        """Calculate speed score (higher score = faster)"""
        if estimated_time <= 1.0:
            return 1.0
        elif estimated_time <= 3.0:
            return 0.8
        elif estimated_time <= 5.0:
            return 0.6
        elif estimated_time <= 10.0:
            return 0.4
        else:
            return 0.2
    
    def _estimate_response_time(self, provider: LLMProvider, request: LLMRequest) -> float:
        """Estimate response time for provider"""
        stats = provider.get_stats()
        avg_time = stats.get('avg_response_time', 2.0)
        
        # Adjust for request complexity
        complexity_factor = 1.0
        
        if request.requires_multimodal:
            complexity_factor *= 1.5
        
        if request.max_tokens and request.max_tokens > 1000:
            complexity_factor *= 1.3
        
        return avg_time * complexity_factor


class LLMOrchestrator:
    """
    Main orchestrator for managing multiple LLM providers
    """
    
    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {}
        self.task_router = TaskRouter()
        self.fallback_chain: List[str] = []
        self.usage_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'provider_usage': {},
            'total_cost': 0.0
        }
    
    def register_provider(self, name: str, provider: LLMProvider):
        """Register a new provider"""
        self.providers[name] = provider
        self.usage_stats['provider_usage'][name] = {
            'requests': 0,
            'successes': 0,
            'failures': 0,
            'total_cost': 0.0
        }
        logger.info(f"Registered provider: {name} ({provider.provider_type.value})")
    
    def set_fallback_chain(self, provider_names: List[str]):
        """Set fallback chain for provider failures"""
        self.fallback_chain = provider_names
        logger.info(f"Set fallback chain: {' -> '.join(provider_names)}")
    
    def generate_response(self, 
                         request: LLMRequest,
                         preferred_provider: str = None,
                         preferences: Dict[str, Any] = None) -> LLMResponse:
        """
        Generate response using best available provider
        
        Args:
            request: LLM request
            preferred_provider: Preferred provider name
            preferences: User preferences for provider selection
            
        Returns:
            LLM response
        """
        self.usage_stats['total_requests'] += 1
        
        # Try preferred provider first
        if preferred_provider and preferred_provider in self.providers:
            provider = self.providers[preferred_provider]
            if provider.validate_request(request):
                response = self._try_provider(provider, request, preferred_provider)
                if response.is_successful:
                    return response
        
        # Select best provider using task router
        available_providers = list(self.providers.values())
        selected_provider = self.task_router.select_provider(request, available_providers, preferences)
        
        if selected_provider:
            provider_name = self._get_provider_name(selected_provider)
            response = self._try_provider(selected_provider, request, provider_name)
            if response.is_successful:
                return response
        
        # Try fallback chain
        for provider_name in self.fallback_chain:
            if provider_name in self.providers:
                provider = self.providers[provider_name]
                if provider.validate_request(request):
                    response = self._try_provider(provider, request, provider_name)
                    if response.is_successful:
                        logger.warning(f"Used fallback provider: {provider_name}")
                        return response
        
        # All providers failed
        self.usage_stats['failed_requests'] += 1
        return LLMResponse(
            content="",
            provider="orchestrator",
            model="unknown",
            error="All providers failed or unavailable"
        )
    
    def _try_provider(self, provider: LLMProvider, request: LLMRequest, provider_name: str) -> LLMResponse:
        """Try to get response from a specific provider"""
        try:
            response = provider.generate_response(request)
            
            # Update statistics
            stats = self.usage_stats['provider_usage'][provider_name]
            stats['requests'] += 1
            
            if response.is_successful:
                stats['successes'] += 1
                self.usage_stats['successful_requests'] += 1
                
                # Update cost tracking
                if response.total_tokens and hasattr(provider, 'estimate_cost'):
                    estimated_cost = provider.estimate_cost(request)
                    stats['total_cost'] += estimated_cost
                    self.usage_stats['total_cost'] += estimated_cost
            else:
                stats['failures'] += 1
                self.usage_stats['failed_requests'] += 1
            
            return response
            
        except Exception as e:
            logger.error(f"Provider {provider_name} error: {e}")
            self.usage_stats['provider_usage'][provider_name]['failures'] += 1
            self.usage_stats['failed_requests'] += 1
            
            return LLMResponse(
                content="",
                provider=provider_name,
                model="unknown",
                error=str(e)
            )
    
    def _get_provider_name(self, provider: LLMProvider) -> str:
        """Get provider name from provider instance"""
        for name, p in self.providers.items():
            if p is provider:
                return name
        return "unknown"
    
    def get_orchestrator_stats(self) -> Dict[str, Any]:
        """Get orchestrator statistics"""
        return {
            **self.usage_stats,
            'provider_count': len(self.providers),
            'available_providers': list(self.providers.keys()),
            'fallback_chain': self.fallback_chain,
            'success_rate': (
                self.usage_stats['successful_requests'] / 
                max(1, self.usage_stats['total_requests']) * 100
            )
        }
    
    def get_provider_capabilities(self) -> Dict[str, Dict[str, Any]]:
        """Get capabilities of all registered providers"""
        capabilities = {}
        for name, provider in self.providers.items():
            capabilities[name] = {
                'type': provider.provider_type.value,
                'capabilities': provider.get_capabilities().to_dict(),
                'available_models': provider.get_available_models(),
                'stats': provider.get_stats()
            }
        return capabilities