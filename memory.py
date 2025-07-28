import json
import os
import threading
from datetime import datetime

MEMORY_FILE = "jarvis_mem.json"
_memory_lock = threading.Lock()  # Prevent concurrent access

# Poprawne dostępne modele zgodnie z ollama list (możesz użyć do walidacji lub informacji)
AVAILABLE_MODELS = [
    "llama3:8b",
    "codellama:13b",
    "codellama:34b",
    "llama3:70b"
]

def load_memory():
    if os.path.exists(MEMORY_FILE):
        try:
            with open(MEMORY_FILE, "r", encoding="utf-8") as f:
                content = f.read().strip()
                if not content:
                    return {}
                return json.loads(content)
        except (json.JSONDecodeError, FileNotFoundError, PermissionError) as e:
            print(f"⚠️ Memory file corrupted, creating backup and new file: {e}")
            # Backup corrupted file
            if os.path.exists(MEMORY_FILE):
                backup_name = f"{MEMORY_FILE}.corrupt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                try:
                    os.rename(MEMORY_FILE, backup_name)
                    print(f"📁 Corrupted memory backed up to: {backup_name}")
                except:
                    pass
            return {}
    return {}

def save_memory(memory):
    try:
        # Create a temporary file first to prevent corruption
        temp_file = f"{MEMORY_FILE}.tmp"
        with open(temp_file, "w", encoding="utf-8") as f:
            json.dump(memory, f, indent=2, ensure_ascii=False)
        
        # Verify the JSON is valid before replacing the original
        with open(temp_file, "r", encoding="utf-8") as f:
            json.load(f)  # This will raise an exception if JSON is invalid
        
        # If we get here, the JSON is valid, so replace the original
        os.replace(temp_file, MEMORY_FILE)
    except Exception as e:
        print(f"❌ Error saving memory: {e}")
        # Clean up temp file if it exists
        if os.path.exists(temp_file):
            try:
                os.remove(temp_file)
            except:
                pass
        raise

def remember_fact(fact: str):
    with _memory_lock:
        memory = load_memory()
        if " to " not in fact:
            return "❌ Niepoprawny format. Użyj: X to Y"
        key, value = fact.split(" to ", 1)
        memory[key.strip()] = value.strip()
        save_memory(memory)
        return f"✅ Zapamiętano: {key.strip()} → {value.strip()}"

def recall_fact(key: str):
    with _memory_lock:
        memory = load_memory()
        return memory.get(key.strip(), "❓ Nie znam tej informacji.")

def forget_fact(key: str):
    with _memory_lock:
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