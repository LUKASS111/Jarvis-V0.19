import requests
import os

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





