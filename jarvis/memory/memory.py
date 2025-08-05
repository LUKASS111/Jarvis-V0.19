import json
import os
import threading
from datetime import datetime

# Import archiving system
try:
    from ..core.data_archiver import archive_input, archive_output, archive_system
    ARCHIVING_ENABLED = True
except ImportError:
    ARCHIVING_ENABLED = False

MEMORY_FILE = "data/jarvis_mem.json"
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
            print(f"[WARN] Memory file corrupted, creating backup and new file: {e}")
            # Backup corrupted file
            if os.path.exists(MEMORY_FILE):
                backup_name = f"{MEMORY_FILE}.corrupt_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
                try:
                    os.rename(MEMORY_FILE, backup_name)
                    print(f"[FOLDER] Corrupted memory backed up to: {backup_name}")
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
        print(f"[FAIL] Error saving memory: {e}")
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
            return "[FAIL] Niepoprawny format. Użyj: X to Y"
        key, value = fact.split(" to ", 1)
        memory[key.strip()] = value.strip()
        save_memory(memory)
        
        # Archive the memory operation
        if ARCHIVING_ENABLED:
            try:
                archive_input(
                    content=fact,
                    source="memory_system",
                    operation="remember_fact",
                    metadata={"key": key.strip(), "value": value.strip()}
                )
            except Exception as e:
                print(f"[WARN] Failed to archive memory operation: {e}")
        
        return f"[OK] Zapamiętano: {key.strip()} → {value.strip()}"

def recall_fact(key: str):
    with _memory_lock:
        memory = load_memory()
        result = memory.get(key.strip(), "[QUESTION] Nie znam tej informacji.")
        
        # Archive the recall operation
        if ARCHIVING_ENABLED:
            try:
                archive_output(
                    content=f"Recall '{key}': {result}",
                    source="memory_system", 
                    operation="recall_fact",
                    metadata={"query_key": key.strip(), "found": key.strip() in memory}
                )
            except Exception as e:
                print(f"[WARN] Failed to archive recall operation: {e}")
        
        return result

def forget_fact(key: str):
    with _memory_lock:
        memory = load_memory()
        if key.strip() in memory:
            deleted_value = memory[key.strip()]
            del memory[key.strip()]
            save_memory(memory)
            
            # Archive the forget operation
            if ARCHIVING_ENABLED:
                try:
                    archive_system(
                        content=f"Forgot '{key}': {deleted_value}",
                        source="memory_system",
                        operation="forget_fact",
                        metadata={"key": key.strip(), "deleted_value": deleted_value}
                    )
                except Exception as e:
                    print(f"[WARN] Failed to archive forget operation: {e}")
            
            return f"[TRASH] Zapomniano: {key.strip()}"
        return "[QUESTION] Nie znam tej informacji."

def export_memory():
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    export_file = f"memory_export_{timestamp}.json"
    memory = load_memory()
    with open(export_file, "w", encoding="utf-8") as f:
        json.dump(memory, f, indent=2, ensure_ascii=False)
    return f"[FOLDER] Eksportowano pamięć do: {export_file}"

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

def get_memory_stats():
    """Get memory statistics for backward compatibility"""
    try:
        from .production_memory import get_memory_stats as production_stats
        return production_stats()
    except:
        # Basic stats from current memory
        memory = load_memory()
        return {
            "total_memories": len(memory),
            "total_categories": 1,
            "average_access_count": 1.0,
            "most_accessed": [],
            "recent_memories_7_days": 0,
            "categories": {"general": len(memory)},
            "storage_files": {
                "json_size": os.path.getsize(MEMORY_FILE) if os.path.exists(MEMORY_FILE) else 0
            }
        }

def search_memory(query: str, limit: int = 10):
    """Search memory for backward compatibility"""
    try:
        from .production_memory import search_memory as production_search
        return production_search(query, limit=limit)
    except:
        # Basic search in current memory
        memory = load_memory()
        results = []
        
        query_lower = query.lower()
        for key, value in memory.items():
            if query_lower in key.lower() or query_lower in value.lower():
                results.append({
                    "key": key,
                    "value": value,
                    "category": "general",
                    "tags": [],
                    "created_at": "unknown",
                    "access_count": 1,
                    "version": 1
                })
        
        return results[:limit]