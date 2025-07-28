import os
import json
from datetime import datetime

LOG_DIR = "logs"

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

def log_event(event_type: str, data: dict, to_txt: bool = False):
    """
    Zapisuje zdarzenie do pliku JSON (i opcjonalnie .txt).
    Dodaje chain_of_thought do loga jeśli występuje w analizie.
    """
    init_log_folder()
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{event_type}_{timestamp}.json"
    filepath = os.path.join(LOG_DIR, filename)

    # Dodanie chain_of_thought do głównego loga, jeśli występuje w analizie
    if "analysis" in data and isinstance(data["analysis"], dict):
        chain = data["analysis"].get("chain_of_thought")
        if chain:
            data["chain_of_thought"] = chain

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)

    if to_txt:
        textfile = filepath.replace(".json", ".txt")
        with open(textfile, "w", encoding="utf-8") as ftxt:
            ftxt.write(format_log_text(event_type, data))

def format_log_text(event_type: str, data: dict) -> str:
    """
    Zamienia słownik loga w czytelny tekst.
    """
    lines = [f"[{event_type.upper()}] {datetime.now().isoformat()}"]
    for key, value in data.items():
        lines.append(f"- {key}: {value}")
    return "\n".join(lines)

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
                "📌 Rozpoczęcie analizy promptu: 'Czym jest sztuczna inteligencja?'",
                "🧩 Tokenizacja: 5 tokenów",
                "🎯 Rozpoznana intencja: question",
                "🔍 To pytanie – możliwe, że użytkownik oczekuje szczegółowego wyjaśnienia.",
                "✅ Wygenerowano strukturę odpowiedzi."
            ]
        }
    }
    log_event("llm_query", test_log, to_txt=True)
    print("Zapisano testowy log.")