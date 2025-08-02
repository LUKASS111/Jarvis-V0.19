#!/usr/bin/env python3
"""
AutoGPT v0.4 - Simplified AI Assistant
Main entry point for the clean, modernized AutoGPT system

Features:
- Modern Enhanced GUI with clean interface
- Comprehensive error handling and monitoring
- Simplified, maintainable architecture
"""

import time
import json
import sys
import os

# Version information
VERSION_STRING = "0.4.1-simplified"

print(f"[LAUNCH] AutoGPT {VERSION_STRING} - Simplified AI Assistant")
print("=" * 60)
from jarvis.core.error_handler import (
    error_handler, safe_execute, ErrorLevel
)

# Core imports with error handling
try:
    from jarvis.llm.llm_interface import ask_local_llm, set_ollama_model
except ImportError as e:
    error_handler.log_error(e, "LLM interface import", ErrorLevel.CRITICAL, 
                           "Nie można załadować interfejsu LLM. Sprawdź instalację.")
    sys.exit(1)

try:
    from jarvis.memory.memory import process_memory_prompt
    from jarvis.utils.logs import log_event
except ImportError as e:
    error_handler.log_error(e, "Core modules import", ErrorLevel.ERROR,
                           "Problem z importem podstawowych modułów systemu.")

AVAILABLE_MODELS = [
    "llama3:8b",
    "codellama:13b", 
    "codellama:34b",
    "llama3:70b"
]

chat_history = []

@safe_execute(fallback_value=None, context="Simple logging")
def simple_log_to_file(log_data, log_file="session_log.json"):
    """Simple logging to file with error handling"""
    if not log_data:
        return None
        
    try:
        os.makedirs("data", exist_ok=True)
        log_path = os.path.join("data", log_file)
        
        with open(log_path, "a", encoding="utf-8") as f:
            json.dump(log_data, f, ensure_ascii=False)
            f.write('\n')
        
        return True
        
    except Exception as e:
        error_handler.log_error(e, "Simple logging", ErrorLevel.ERROR,
                               "Błąd podczas zapisywania logów")
        return None

def simple_llm_process(prompt: str) -> dict:
    """Simple LLM processing without complex flow systems"""
    try:
        # Basic LLM response
        response = ask_local_llm(prompt)
        
        result = {
            "prompt": prompt,
            "response": response,
            "timestamp": time.time()
        }
        
        return result
        
    except Exception as e:
        error_handler.log_error(e, "LLM processing", ErrorLevel.ERROR)
        return {
            "prompt": prompt,
            "response": f"Error processing request: {str(e)}",
            "timestamp": time.time(),
            "error": True
        }

@safe_execute(fallback_value=None, context="Interactive input processing")
def process_interactive_input(user_input: str) -> dict:
    """Process interactive user input with comprehensive handling"""
    if not user_input or not user_input.strip():
        return None
    
    user_input = user_input.strip()
    
    # Handle special commands
    if user_input.lower() in {"exit", "quit", "q"}:
        return {"action": "exit", "message": "Goodbye!"}
    
    if user_input.lower() in {"błędy", "errors", "raport"}:
        try:
            from error_handler import create_error_report
            report = create_error_report()
            return {"action": "error_report", "report": report}
        except Exception as e:
            error_handler.log_error(e, "Error report generation", ErrorLevel.WARNING)
            return {"action": "error", "message": "Cannot generate error report"}
    
    if user_input.lower() in {"archiwum", "archive", "purge"}:
        try:
            from jarvis.core.archive_purge_manager import get_archive_health
            health = get_archive_health()
            return {"action": "archive_status", "health": health}
        except Exception as e:
            error_handler.log_error(e, "Archive status", ErrorLevel.WARNING)
            return {"action": "error", "message": "Cannot get archive status"}
    
    if user_input.lower().startswith("model "):
        new_model = user_input[6:].strip()
        if new_model in AVAILABLE_MODELS:
            try:
                set_ollama_model(new_model)
                return {"action": "model_change", "model": new_model, "success": True}
            except Exception as e:
                error_handler.log_error(e, "Model selection", ErrorLevel.WARNING)
                return {"action": "model_change", "model": new_model, "success": False}
        else:
            return {"action": "model_change", "error": "Unknown model", "available": AVAILABLE_MODELS}
    
    if user_input.lower() in {"nowa", "new"}:
        return {"action": "new_session", "message": "New session started"}
    
    # Handle memory operations
    try:
        memory_response = process_memory_prompt(user_input)
        if memory_response:
            return {"action": "memory", "response": memory_response, "prompt": user_input}
    except Exception as e:
        error_handler.log_error(e, "Memory processing", ErrorLevel.WARNING)
    
    # Default LLM processing
    try:
        result = simple_llm_process(user_input)
        return {"action": "llm_response", "result": result}
    except Exception as e:
        error_handler.log_error(e, "Interactive input processing", ErrorLevel.ERROR)
        return {"action": "error", "message": f"Processing error: {str(e)}"}

@safe_execute(fallback_value=False, context="Main application")
def main(skip_startup_init=False):
    """Simplified main function with clean interface
    
    Args:
        skip_startup_init (bool): Skip startup initialization if already done by unified entry point
    """
    
    global chat_history
    
    # Initialize archive purge system on startup (only if not already done)
    if not skip_startup_init:
        print("[STARTUP] Initializing automatic version-based archive cleanup...")
        try:
            from jarvis.core.archive_purge_manager import auto_purge_startup, get_archive_health
            purge_result = auto_purge_startup()
            
            if purge_result:
                summary = purge_result.get('summary', {})
                purge_stats = purge_result.get('purge_result', {})
                backup_cleanup = purge_result.get('backup_cleanup', {})
                
                entries_removed = summary.get('entries_removed', 0)
                backups_cleaned = backup_cleanup.get('cleaned_backups', 0)
                
                if entries_removed > 0 or backups_cleaned > 0:
                    print(f"[PURGE] Version cleanup: {entries_removed} old entries removed, {backups_cleaned} old backups cleaned")
                    print(f"[PURGE] Current version: {purge_result.get('current_version', 'unknown')}")
                    
                    if purge_stats.get('versions_removed'):
                        print(f"[PURGE] Removed versions: {', '.join(purge_stats['versions_removed'])}")
                else:
                    print("[PURGE] Archive is clean - no old version data found")
            
            # Show archive health
            health = get_archive_health()
            print(f"[ARCHIVE] Health Score: {health['health_score']}/100, Size: {health['archive_size_mb']}MB, Entries: {health['total_entries']:,}")
            
        except Exception as e:
            error_handler.log_error(e, "Archive purge startup", ErrorLevel.WARNING,
                                   "Could not initialize archive purge system")
            print("[WARN] Archive purge system initialization failed")
    
    print("[BRAIN] Jarvis CLI uruchomiony. Zadaj pytanie (lub wpisz 'exit' by zakończyć).\n"
          "Dostępne modele: " + ", ".join(AVAILABLE_MODELS) + "\n"
          "Aby zmienić model wpisz: 'model <nazwa_modelu>' (np. model codellama:13b)\n"
          "Aby rozpocząć nową rozmowę wpisz: 'nowa'\n"
          "Aby sprawdzić błędy wpisz: 'błędy'")
    
    # Session initialization
    error_handler.session_id = f"main_{int(time.time())}"
    
    while True:
        try:
            prompt = input("\nTy: ").strip()
        except (EOFError, KeyboardInterrupt):
            print("\n[WAVE] Do zobaczenia!")
            break
        except Exception as e:
            error_handler.log_error(e, "User input", ErrorLevel.WARNING,
                                   "Problem z wprowadzaniem danych")
            continue
            
        if not prompt:
            continue
            
        # Exit commands
        if prompt.lower() in {"exit", "quit", "q"}:
            print("[WAVE] Do zobaczenia!")
            break

        # Error report command
        if prompt.lower() in {"błędy", "errors", "raport"}:
            try:
                from error_handler import create_error_report
                report = create_error_report()
                print("\n" + "="*50)
                print(report)
                print("="*50)
            except Exception as e:
                error_handler.log_error(e, "Error report generation", ErrorLevel.WARNING)
                print("[FAIL] Nie można wygenerować raportu błędów")
            continue

        # Model selection with validation
        if prompt.lower().startswith("model "):
            try:
                new_model = prompt[6:].strip()
                if new_model in AVAILABLE_MODELS:
                    set_ollama_model(new_model)
                    print(f"✅ Wybrano model: {new_model}")
                else:
                    print(f"[FAIL] Nieznany model. Dostępne: " + ", ".join(AVAILABLE_MODELS))
            except Exception as e:
                error_handler.log_error(e, "Model selection", ErrorLevel.WARNING,
                                       "Problem z wyborem modelu")
            continue

        # Archive status with management options
        if prompt.lower() in {"archiwum", "archive", "purge"}:
            try:
                from jarvis.core.archive_purge_manager import get_archive_health
                health = get_archive_health()
                print(f"[ARCHIVE] Health Score: {health['health_score']}/100")
                print(f"[ARCHIVE] Size: {health['archive_size_mb']}MB, Entries: {health['total_entries']:,}")
                print(f"[ARCHIVE] Current Version: {health['current_version']}")
                if health['purgeable_entries'] > 0:
                    print(f"[ARCHIVE] Purgeable entries: {health['purgeable_entries']}")
                    print("[ARCHIVE] Run 'python archive_purge_cli.py status' for details")
                else:
                    print("[ARCHIVE] No entries need purging")
                log_event("archive_status", health)
            except Exception as e:
                error_handler.log_error(e, "Archive status", ErrorLevel.WARNING)
            continue
        if prompt.lower() in {"nowa", "new"}:
            try:
                chat_history.clear()
                print("[CLEAN] Rozpoczęto nową sesję rozmowy.")
            except Exception as e:
                error_handler.log_error(e, "Session reset", ErrorLevel.WARNING)
            continue

        # Memory operations with error handling
        try:
            memory_response = process_memory_prompt(prompt)
            if memory_response:
                print(f"[BRAIN] Jarvis (memory): {memory_response}")
                log_event("memory_action", {"prompt": prompt, "response": memory_response})
                continue
        except Exception as e:
            error_handler.log_error(e, "Memory processing", ErrorLevel.WARNING,
                                   "Problem z operacjami pamięci")

        # Main processing with simplified flow
        try:
            result = simple_llm_process(prompt)
            
            if not result.get("error"):
                print(f"\n[ROBOT] Jarvis: {result['response']}")
            else:
                print(f"\n[FAIL] Błąd: {result['response']}")
            
            # Add to chat history with size limit
            chat_history.append(result)
            if len(chat_history) > 50:  # Prevent memory issues
                # Save oldest entries
                old_entries = chat_history[:25]
                simple_log_to_file(old_entries, "old_session.json")
                chat_history = chat_history[25:]
                print("[PACKAGE] Zapisano starsze wpisy")
            
            # Simple logging
            log_event("llm_interaction", {
                "prompt": prompt,
                "response": result.get("response", ""),
                "timestamp": result.get("timestamp")
            })
            
        except Exception as e:
            error_handler.log_error(e, "Main processing", ErrorLevel.ERROR,
                                   "Błąd w głównym przetwarzaniu")
            print("[FAIL] Wystąpił błąd. Sprawdź 'błędy' aby zobaczyć szczegóły.")

        # Brief pause to prevent overwhelming
        try:
            time.sleep(0.5)
        except:
            pass

if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        error_handler.log_error(e, "Application startup", ErrorLevel.CRITICAL,
                               "Krytyczny błąd podczas uruchamiania aplikacji")
        print("[ALERT] Krytyczny błąd systemu. Sprawdź logi błędów.")
        sys.exit(1)
    finally:
        # Generate final error report
        try:
            from error_handler import create_error_report
            summary = error_handler.get_session_summary()
            if summary['total_errors'] > 0 or summary['total_warnings'] > 0:
                print(f"\n[CHART] Podsumowanie sesji: {summary['total_errors']} błędów, "
                      f"{summary['total_warnings']} ostrzeżeń, {summary['total_fallbacks']} fallback'ów")
        except:
            pass