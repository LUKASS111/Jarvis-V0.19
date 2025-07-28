import json
import os
from datetime import datetime

MEMORY_FILE = "jarvis_mem.json"

# Poprawne dostępne modele zgodnie z ollama list (możesz użyć do walidacji lub informacji)
AVAILABLE_MODELS = [
    "llama3:8b",
    "codellama:13b",
    "codellama:34b",
    "llama3:70b"
]

def load_memory():
    if os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_memory(memory):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)

def remember_fact(fact: str):
    memory = load_memory()
    if " to " not in fact:
        return "❌ Niepoprawny format. Użyj: X to Y"
    key, value = fact.split(" to ", 1)
    memory[key.strip()] = value.strip()
    save_memory(memory)
    return f"✅ Zapamiętano: {key.strip()} → {value.strip()}"

def recall_fact(key: str):
    memory = load_memory()
    return memory.get(key.strip(), "❓ Nie znam tej informacji.")

def forget_fact(key: str):
    memory = load_memory()
    if key.strip() in memory:
        del memory[key.strip()]
        save_memory(memory)
        return f"🗑️ Zapomniano: {key.strip()}"
    return "❓ Nie znam tej informacji."

def export_memory():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_file = f"memory_export_{timestamp}.json"
    memory = load_memory()
    with open(export_file, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)
    return f"📁 Eksportowano pamięć do: {export_file}"

def process_memory_prompt(prompt: str):
    prompt = prompt.strip().lower()
    if prompt.startswith("zapamiętaj") or prompt.startswith("remember"):
        content = prompt.replace("zapamiętaj", "").replace("remember", "").strip()
        return remember_fact(content)
    elif "co wiesz o" in prompt:
        key = prompt.replace("co wiesz o", "").strip()
        return recall_fact(key)
    elif prompt.startswith("recall "):
        key = prompt.replace("recall ", "").strip()
        return recall_fact(key)
    elif prompt.startswith("zapomnij") or prompt.startswith("forget"):
        key = prompt.replace("zapomnij", "").replace("forget", "").strip()
        return forget_fact(key)
    elif "eksportuj pamięć" in prompt or "zapisz pamięć" in prompt or "export memory" in prompt:
        return export_memory()
    return None