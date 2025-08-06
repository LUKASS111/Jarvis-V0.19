import requests
import os
import time
import logging
from typing import Dict, Any, List, Optional, Union
from abc import ABC, abstractmethod

# Setup logging
logger = logging.getLogger(__name__)

# Import archiving system
try:
    from ..core.data_archiver import archive_input, archive_output
    ARCHIVING_ENABLED = True
except ImportError:
    ARCHIVING_ENABLED = False

# Poprawiona lista dostępnych modeli zgodna z ollama list
AVAILABLE_MODELS = [
    "llama3:8b",
    "codellama:13b",
    "codellama:34b",
    "llama3:70b"
]

# Pozwala na ustawienie modelu przez zmienną środowiskową lub domyślnie
DEFAULT_OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3:8b")
OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434/api/generate")

# Globalny aktualnie wybrany model
CURRENT_OLLAMA_MODEL = DEFAULT_OLLAMA_MODEL

DEFAULT_LLM_PARAMS = {
    "temperature": 0.7,
    "top_p": 0.95,
    "max_tokens": 512,
    "repetition_penalty": 1.1,
    "system_prompt": ""
}

def set_ollama_model(model_name):
    global CURRENT_OLLAMA_MODEL
    if model_name in AVAILABLE_MODELS:
        CURRENT_OLLAMA_MODEL = model_name
    else:
        CURRENT_OLLAMA_MODEL = DEFAULT_OLLAMA_MODEL  # fallback

def get_ollama_model():
    return CURRENT_OLLAMA_MODEL

def get_available_models():
    return AVAILABLE_MODELS

def get_dynamic_timeout(model=None):
    model = model or CURRENT_OLLAMA_MODEL
    if "70b" in model:
        return 220
    if "34b" in model:
        return 130
    if "13b" in model:
        return 100
    if "8b" in model:
        return 45
    return 40

def validate_llm_params(**params):
    allowed = {"temperature", "top_p", "max_tokens", "repetition_penalty", "system_prompt", "timeout"}
    for k in params:
        if k not in allowed:
            print(f"Nieobsługiwany parametr dla LLM: {k}")
            return False
    return True

def query_llm(prompt, model=None, stream=False, timeout=None, temperature=None, top_p=None, max_tokens=None, repetition_penalty=None, system_prompt=None):
    model = model or CURRENT_OLLAMA_MODEL
    timeout = timeout if timeout is not None else get_dynamic_timeout(model)
    payload = {
        "model": model,
        "prompt": prompt,
        "stream": stream
    }
    payload["options"] = {}
    payload["options"]["temperature"] = float(temperature) if temperature is not None else DEFAULT_LLM_PARAMS["temperature"]
    payload["options"]["top_p"] = float(top_p) if top_p is not None else DEFAULT_LLM_PARAMS["top_p"]
    payload["options"]["num_predict"] = int(max_tokens) if max_tokens is not None else DEFAULT_LLM_PARAMS["max_tokens"]
    payload["options"]["repeat_penalty"] = float(repetition_penalty) if repetition_penalty is not None else DEFAULT_LLM_PARAMS["repetition_penalty"]
    if (system_prompt is not None and str(system_prompt).strip()):
        payload["system"] = str(system_prompt).strip()
    elif DEFAULT_LLM_PARAMS["system_prompt"]:
        payload["system"] = DEFAULT_LLM_PARAMS["system_prompt"]

    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=timeout)
        response.raise_for_status()
        if stream:
            def stream_response():
                for line in response.iter_lines():
                    if line:
                        try:
                            data = line.decode("utf-8")
                            yield data
                        except Exception:
                            continue
            return stream_response()
        data = response.json()
        if "response" in data:
            return data["response"].strip()
        if isinstance(data, list):
            return "\n".join(str(x) for x in data)
        return str(data)
    except requests.exceptions.Timeout:
        return "[LLM ERROR: timeout]"
    except requests.exceptions.ConnectionError:
        return "[LLM ERROR: nie można połączyć się z Ollama (czy serwer działa?)]"
    except requests.exceptions.RequestException as e:
        return f"[LLM ERROR: {e}]"
    except Exception as e:
        return f"[LLM ERROR: {e}]"

def ask_local_llm(prompt, temperature=None, top_p=None, max_tokens=None, repetition_penalty=None, system_prompt=None, timeout=None, model=None):
    if not validate_llm_params(temperature=temperature, top_p=top_p, max_tokens=max_tokens, repetition_penalty=repetition_penalty, system_prompt=system_prompt, timeout=timeout):
        print("[LLM][ERROR] Nieobsługiwane parametry w ask_local_llm!")
        return "[LLM ERROR: invalid params]"
    
    # Archive the input prompt
    if ARCHIVING_ENABLED:
        try:
            archive_input(
                content=prompt,
                source="llm_interface",
                operation="ask_local_llm",
                metadata={
                    "model": model or CURRENT_OLLAMA_MODEL,
                    "temperature": temperature,
                    "max_tokens": max_tokens,
                    "timeout": timeout
                }
            )
        except Exception as e:
            print(f"[WARN] Failed to archive LLM input: {e}")
    
    # Get LLM response
    response = query_llm(
        prompt,
        model=model,
        temperature=temperature,
        top_p=top_p,
        max_tokens=max_tokens,
        repetition_penalty=repetition_penalty,
        system_prompt=system_prompt,
        timeout=timeout
    )
    
    # Archive the output response
    if ARCHIVING_ENABLED:
        try:
            archive_output(
                content=response,
                source="llm_interface",
                operation="llm_response",
                metadata={
                    "model": model or CURRENT_OLLAMA_MODEL,
                    "prompt_length": len(prompt),
                    "response_length": len(response),
                    "is_error": response.startswith("[LLM ERROR:")
                }
            )
        except Exception as e:
            print(f"[WARN] Failed to archive LLM output: {e}")
    
    return response


class LLMInterface(ABC):
    """
    Abstract base class for LLM interfaces providing unified access to language models.
    """
    
    @abstractmethod
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response from the language model."""
        pass
    
    @abstractmethod
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        pass
    
    @abstractmethod
    def set_model(self, model_name: str) -> bool:
        """Set the active model."""
        pass


class OllamaLLMInterface(LLMInterface):
    """
    Enhanced Ollama LLM Interface with advanced capabilities.
    """
    
    def __init__(self, base_url: str = None):
        """Initialize Ollama interface."""
        self.base_url = base_url or OLLAMA_URL
        self.current_model = CURRENT_OLLAMA_MODEL
        self.conversation_history = []
        self.response_stats = {
            'total_requests': 0,
            'successful_requests': 0,
            'failed_requests': 0,
            'average_response_time': 0.0
        }
    
    def generate_response(self, prompt: str, **kwargs) -> str:
        """Generate response with enhanced features."""
        start_time = time.time()
        self.response_stats['total_requests'] += 1
        
        try:
            # Use existing ask_local_llm function
            response = ask_local_llm(
                prompt, 
                model=kwargs.get('model', self.current_model),
                system_prompt=kwargs.get('system_prompt', ''),
                timeout=kwargs.get('timeout')
            )
            
            # Update statistics
            response_time = time.time() - start_time
            self._update_response_stats(response_time, success=True)
            
            # Store in conversation history if enabled
            if kwargs.get('store_history', True):
                self.conversation_history.append({
                    'timestamp': time.time(),
                    'prompt': prompt,
                    'response': response,
                    'model': self.current_model,
                    'response_time': response_time
                })
                
                # Limit history size
                if len(self.conversation_history) > 100:
                    self.conversation_history = self.conversation_history[-50:]
            
            return response
            
        except Exception as e:
            self._update_response_stats(time.time() - start_time, success=False)
            logger.error(f"LLM generation error: {e}")
            return f"[LLM ERROR: {str(e)}]"
    
    def generate_with_context(self, prompt: str, context_messages: int = 5, **kwargs) -> str:
        """Generate response with conversation context."""
        if context_messages > 0 and self.conversation_history:
            # Get recent conversation history
            recent_history = self.conversation_history[-context_messages:]
            context_prompt = self._build_context_prompt(recent_history, prompt)
            return self.generate_response(context_prompt, **kwargs)
        else:
            return self.generate_response(prompt, **kwargs)
    
    def semantic_search_response(self, query: str, **kwargs) -> Dict[str, Any]:
        """Generate response with semantic analysis."""
        # Enhanced prompt for semantic understanding
        semantic_prompt = f"""
Analyze this query semantically and provide a comprehensive response:

Query: {query}

Please provide:
1. Intent analysis
2. Key concepts identified
3. Detailed response
4. Related topics or suggestions

Response:"""
        
        response = self.generate_response(semantic_prompt, **kwargs)
        
        return {
            'query': query,
            'response': response,
            'analysis': {
                'query_length': len(query),
                'query_complexity': 'complex' if len(query.split()) > 10 else 'simple',
                'timestamp': time.time()
            }
        }
    
    def batch_generate(self, prompts: List[str], **kwargs) -> List[Dict[str, Any]]:
        """Generate responses for multiple prompts."""
        results = []
        
        for i, prompt in enumerate(prompts):
            try:
                response = self.generate_response(prompt, **kwargs)
                results.append({
                    'index': i,
                    'prompt': prompt,
                    'response': response,
                    'success': True
                })
            except Exception as e:
                results.append({
                    'index': i,
                    'prompt': prompt,
                    'error': str(e),
                    'success': False
                })
        
        return results
    
    def get_available_models(self) -> List[str]:
        """Get list of available models."""
        return get_available_models()
    
    def set_model(self, model_name: str) -> bool:
        """Set the active model."""
        if model_name in self.get_available_models():
            set_ollama_model(model_name)
            self.current_model = model_name
            return True
        return False
    
    def get_current_model(self) -> str:
        """Get currently active model."""
        return self.current_model
    
    def get_conversation_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get conversation history."""
        if limit:
            return self.conversation_history[-limit:]
        return self.conversation_history.copy()
    
    def clear_history(self):
        """Clear conversation history."""
        self.conversation_history.clear()
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get interface statistics."""
        return {
            'response_stats': self.response_stats.copy(),
            'current_model': self.current_model,
            'history_length': len(self.conversation_history),
            'available_models': self.get_available_models()
        }
    
    def _build_context_prompt(self, history: List[Dict[str, Any]], current_prompt: str) -> str:
        """Build prompt with conversation context."""
        context_parts = []
        
        for entry in history:
            context_parts.append(f"User: {entry['prompt']}")
            context_parts.append(f"Assistant: {entry['response']}")
        
        context_parts.append(f"User: {current_prompt}")
        
        return "\n".join(context_parts)
    
    def _update_response_stats(self, response_time: float, success: bool):
        """Update response statistics."""
        if success:
            self.response_stats['successful_requests'] += 1
        else:
            self.response_stats['failed_requests'] += 1
        
        # Update average response time
        total_successful = self.response_stats['successful_requests']
        if total_successful > 0:
            current_avg = self.response_stats['average_response_time']
            self.response_stats['average_response_time'] = (
                (current_avg * (total_successful - 1) + response_time) / total_successful
            )


# Global interface instance
_llm_interface = None

def get_llm_interface() -> OllamaLLMInterface:
    """Get global LLM interface instance."""
    global _llm_interface
    if _llm_interface is None:
        _llm_interface = OllamaLLMInterface()
    return _llm_interface





