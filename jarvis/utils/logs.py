import os
import json
from datetime import datetime

LOG_DIR = "logs"
# Unified test output directory for test-related logs
TEST_LOG_DIR = "tests/output/logs"

# Poprawne dostępne modele zgodnie z ollama list (możesz użyć do walidacji logów/modelu)
AVAILABLE_MODELS = [
    "llama3:8b",
    "codellama:13b",
    "codellama:34b",
    "llama3:70b"
]

def init_log_folder():
    if not os.path.exists(LOG_DIR):
        os.makedirs(LOG_DIR)
    if not os.path.exists(TEST_LOG_DIR):
        os.makedirs(TEST_LOG_DIR, exist_ok=True)

def log_event(event_type: str, data: dict, to_txt: bool = False):
    """
    Zapisuje zdarzenie do pliku JSON (i opcjonalnie .txt).
    Dodaje chain_of_thought do loga jeśli występuje w analizie.
    Test-related events are saved to unified test output directory.
    """
    try:
        init_log_folder()
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{event_type}_{timestamp}.json"
        
        # Determine if this is a test-related event and choose appropriate directory
        is_test_event = any(keyword in event_type.lower() for keyword in [
            'test', 'perf_event', 'concurrent_log', 'workflow_event', 'large_event'
        ])
        
        if is_test_event:
            filepath = os.path.join(TEST_LOG_DIR, filename)
        else:
            filepath = os.path.join(LOG_DIR, filename)

        # Create proper log structure
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event": event_type,
            "data": data.copy()
        }

        # Dodanie chain_of_thought do głównego loga, jeśli występuje w analizie
        if "analysis" in data and isinstance(data["analysis"], dict):
            chain = data["analysis"].get("chain_of_thought")
            if chain:
                log_entry["chain_of_thought"] = chain

        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(log_entry, f, indent=2, ensure_ascii=False)

        if to_txt:
            textfile = filepath.replace(".json", ".txt")
            with open(textfile, "w", encoding="utf-8") as ftxt:
                ftxt.write(format_log_text(event_type, data))
        
        return True
    except Exception as e:
        return False

def format_log_text(event_type: str, data: dict) -> str:
    """
    Zamienia słownik loga w czytelny tekst.
    """
    lines = [f"[{event_type.upper()}] {datetime.now().isoformat()}"]
    for key, value in data.items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)

def get_logs(limit: int = 100) -> list:
    """
    Retrieve recent log entries from log files (including test logs)
    """
    init_log_folder()
    logs = []
    
    try:
        # Get all log files from both directories, sorted by modification time (newest first)
        log_files = []
        
        # Check main logs directory
        if os.path.exists(LOG_DIR):
            for filename in os.listdir(LOG_DIR):
                if filename.endswith('.json'):
                    filepath = os.path.join(LOG_DIR, filename)
                    mtime = os.path.getmtime(filepath)
                    log_files.append((mtime, filepath, filename))
        
        # Check test logs directory
        if os.path.exists(TEST_LOG_DIR):
            for filename in os.listdir(TEST_LOG_DIR):
                if filename.endswith('.json') and not filename.startswith('function_test_results'):
                    filepath = os.path.join(TEST_LOG_DIR, filename)
                    mtime = os.path.getmtime(filepath)
                    log_files.append((mtime, filepath, filename))
        
        log_files.sort(reverse=True)  # Newest first
        
        # Read logs from files
        for mtime, filepath, filename in log_files[:min(limit, len(log_files))]:
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read().strip()
                    if content:
                        # Handle potential malformed JSON
                        try:
                            log_data = json.loads(content)
                            log_data['_filename'] = filename
                            log_data['_timestamp'] = datetime.fromtimestamp(mtime).isoformat()
                            logs.append(log_data)
                        except json.JSONDecodeError:
                            # Try to read as multiple JSON objects (one per line)
                            lines = content.split('\n')
                            for line in lines:
                                if line.strip():
                                    try:
                                        log_data = json.loads(line)
                                        log_data['_filename'] = filename
                                        log_data['_timestamp'] = datetime.fromtimestamp(mtime).isoformat()
                                        logs.append(log_data)
                                    except json.JSONDecodeError:
                                        continue
            except Exception as e:
                # Skip problematic files but don't break the function
                continue
                
    except Exception as e:
        # Return empty list if there's an issue accessing logs
        return []
    
    # Sort by timestamp and limit results
    logs.sort(key=lambda x: x.get('_timestamp', ''), reverse=True)
    return logs[:limit]

def clear_logs() -> bool:
    """
    Clear all log files (for testing purposes)
    """
    try:
        init_log_folder()
        
        # Remove all JSON files in log directory
        for filename in os.listdir(LOG_DIR):
            if filename.endswith('.json'):
                filepath = os.path.join(LOG_DIR, filename)
                os.remove(filepath)
        
        return True
    except Exception as e:
        return False

# Test lokalny
if __name__ == "__main__":
    test_log = {
        "prompt": "Czym jest sztuczna inteligencja?",
        "response": "To zdolność maszyn do uczenia się i działania jak człowiek.",
        "source": "llm_interface",
        "status": "ok",
        "analysis": {
            "intent": "question",
            "chain_of_thought": [
                "[PIN] Rozpoczęcie analizy promptu: 'Czym jest sztuczna inteligencja?'",
                "[PUZZLE] Tokenizacja: 5 tokenów",
                "[TARGET] Rozpoznana intencja: question",
                "[SEARCH] To pytanie – możliwe, że użytkownik oczekuje szczegółowego wyjaśnienia.",
                "✅ Wygenerowano strukturę odpowiedzi."
            ]
        }
    }
    log_event("llm_query", test_log, to_txt=True)
    print("Zapisano testowy log.")