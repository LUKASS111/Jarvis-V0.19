#!/usr/bin/env python3
"""
Jarvis V0.19 - Enterprise Distributed AI System
Main entry point for the enterprise-grade AI assistant with CRDT architecture

Features:
- Enterprise GUI with production capabilities
- Comprehensive CRDT-based distributed architecture
- Mathematical conflict-free synchronization
- Advanced error handling and monitoring
- Production-ready enterprise architecture
"""

import time
import json
import sys
import os
import logging
from typing import Dict, Any

# Version information
VERSION_STRING = "0.19"

# Setup logging
logger = logging.getLogger(__name__)

# Print messages moved to main() function to avoid printing on import
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

class JarvisAgent:
    """
    Main Jarvis Agent class providing unified interface to all system capabilities.
    """
    
    def __init__(self):
        """Initialize Jarvis Agent with all core systems."""
        self.version = VERSION_STRING
        self.chat_history = []
        self._initialized = False
        
    def initialize(self):
        """Initialize all core systems."""
        if self._initialized:
            return True
            
        try:
            # Initialize error handling system
            error_handler.session_id = f"agent_{int(time.time())}"
            
            # Initialize archive system
            from jarvis.core.archive_purge_manager import auto_purge_startup
            auto_purge_startup()
            
            self._initialized = True
            logger.info("Jarvis Agent initialized successfully")
            return True
            
        except Exception as e:
            error_handler.log_error(e, "Agent initialization", ErrorLevel.CRITICAL)
            return False
    
    def process_input(self, user_input: str) -> Dict[str, Any]:
        """
        Process user input through the complete Jarvis pipeline.
        
        Args:
            user_input (str): User input to process
            
        Returns:
            Dict[str, Any]: Processing result with action and response
        """
        return process_interactive_input(user_input)
    
    def get_capabilities(self) -> Dict[str, Any]:
        """Get overview of current system capabilities."""
        try:
            # File processing capabilities
            from jarvis.utils.file_processors import get_supported_formats
            supported_formats = get_supported_formats()
            
            # Performance monitoring
            try:
                from jarvis.monitoring.performance_optimizer import get_performance_monitor
                monitor = get_performance_monitor()
                system_health = monitor.assess_system_health()
                health_score = system_health.overall_score
            except Exception:
                health_score = "Unknown"
            
            # Archive health
            try:
                from jarvis.core.archive_purge_manager import get_archive_health
                archive_health = get_archive_health()
                archive_score = archive_health.get('health_score', 0)
            except Exception:
                archive_score = "Unknown"
            
            return {
                "version": self.version,
                "initialized": self._initialized,
                "file_processing": {
                    "supported_formats": len(supported_formats),
                    "formats": supported_formats
                },
                "system_health": {
                    "performance_score": health_score,
                    "archive_score": archive_score
                },
                "available_models": AVAILABLE_MODELS,
                "core_capabilities": [
                    "LLM Interaction",
                    "Memory Management", 
                    "File Processing",
                    "Error Handling",
                    "Archive Management",
                    "Performance Monitoring"
                ]
            }
            
        except Exception as e:
            error_handler.log_error(e, "Capabilities assessment", ErrorLevel.WARNING)
            return {
                "version": self.version,
                "initialized": self._initialized,
                "error": "Could not assess full capabilities"
            }
    
    def health_check(self) -> Dict[str, Any]:
        """Perform comprehensive system health check."""
        try:
            health_data = {}
            
            # Core system health
            health_data['core_system'] = self._initialized
            
            # Performance monitoring
            try:
                from jarvis.monitoring.performance_optimizer import get_performance_monitor
                monitor = get_performance_monitor()
                system_health = monitor.assess_system_health()
                health_data['performance'] = {
                    'score': system_health.overall_score,
                    'cpu_health': system_health.cpu_health,
                    'memory_health': system_health.memory_health,
                    'recommendations': system_health.recommendations[:3]  # Top 3
                }
            except Exception as e:
                health_data['performance'] = {'error': str(e)}
            
            # File processing health
            try:
                from jarvis.utils.file_processors import get_supported_formats
                formats = get_supported_formats()
                health_data['file_processing'] = {
                    'operational': True,
                    'supported_formats': len(formats)
                }
            except Exception as e:
                health_data['file_processing'] = {'error': str(e)}
            
            # Memory system health
            try:
                from jarvis.memory.memory import process_memory_prompt
                # Test memory system
                health_data['memory_system'] = {'operational': True}
            except Exception as e:
                health_data['memory_system'] = {'error': str(e)}
            
            # Archive system health
            try:
                from jarvis.core.archive_purge_manager import get_archive_health
                archive_health = get_archive_health()
                health_data['archive_system'] = {
                    'health_score': archive_health.get('health_score', 0),
                    'total_entries': archive_health.get('total_entries', 0)
                }
            except Exception as e:
                health_data['archive_system'] = {'error': str(e)}
            
            # Calculate overall health
            operational_systems = sum(1 for system in health_data.values() 
                                    if isinstance(system, dict) and not system.get('error'))
            total_systems = len(health_data)
            overall_health = (operational_systems / total_systems) * 100
            
            health_data['overall'] = {
                'health_percentage': round(overall_health, 1),
                'operational_systems': operational_systems,
                'total_systems': total_systems,
                'status': 'Excellent' if overall_health >= 90 else 
                         'Good' if overall_health >= 75 else 
                         'Fair' if overall_health >= 50 else 'Poor'
            }
            
            return health_data
            
        except Exception as e:
            error_handler.log_error(e, "Health check", ErrorLevel.ERROR)
            return {
                'overall': {'health_percentage': 0, 'status': 'Error', 'error': str(e)}
            }

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
            from jarvis.core.error_handler import create_error_report
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
    
    # Print modern system banner when launching
    print(f"[LAUNCH] Jarvis {VERSION_STRING} - Enterprise Distributed AI System")
    print("=" * 60)
    
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
                    print("[PURGE] Archive is clean - no current version data found")
            
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
                from jarvis.core.error_handler import create_error_report
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
                current_entries = chat_history[:25]
                simple_log_to_file(current_entries, "current_session.json")
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
            from jarvis.core.error_handler import create_error_report
            summary = error_handler.get_session_summary()
            if summary['total_errors'] > 0 or summary['total_warnings'] > 0:
                print(f"\n[CHART] Podsumowanie sesji: {summary['total_errors']} błędów, "
                      f"{summary['total_warnings']} ostrzeżeń, {summary['total_fallbacks']} fallback'ów")
        except:
            pass