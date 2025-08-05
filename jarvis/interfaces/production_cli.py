"""
Production CLI Interface for Jarvis
Uses unified backend service for all operations
"""

import sys
import os
import time
import json
from typing import Dict, List, Any, Optional
from datetime import datetime
import argparse
import threading

# Add the project root to the Python path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from jarvis.backend import get_jarvis_backend, shutdown_jarvis_backend
from jarvis.core.error_handler import error_handler, ErrorLevel
from jarvis.api.api_models import RequestType

class ProductionCLI:
    """
    Production CLI interface using unified backend service
    
    Features:
    - Session-based interactions
    - Full backend integration
    - Command history and persistence
    - Advanced command parsing
    - Real-time system monitoring
    - Batch operation support
    """
    
    def __init__(self):
        self.backend = get_jarvis_backend()
        self.session_id = None
        self.command_history: List[str] = []
        self.is_running = False
        self.config = {
            "auto_save_history": True,
            "history_file": "data/cli_history.json",
            "max_history": 1000,
            "show_timestamps": True,
            "verbose_mode": False,
            "color_output": True
        }
        
        self._initialize_cli()
    
    def _initialize_cli(self):
        """Initialize CLI system"""
        try:
            # Create session
            self.session_id = self.backend.create_session(
                session_type="cli",
                metadata={"interface": "production_cli", "start_time": time.time()}
            )
            
            # Load command history
            self._load_history()
            
            print(f"[CLI] Production CLI initialized - Session: {self.session_id[:8]}")
            
        except Exception as e:
            error_handler.log_error(
                e, "CLI Initialization", ErrorLevel.CRITICAL,
                "Failed to initialize production CLI"
            )
            raise
    
    def _load_history(self):
        """Load command history from file"""
        try:
            history_path = self.config["history_file"]
            os.makedirs(os.path.dirname(history_path), exist_ok=True)
            
            if os.path.exists(history_path):
                with open(history_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.command_history = data.get("commands", [])
                    
        except Exception as e:
            # Don't fail on history loading errors
            self.command_history = []
    
    def _save_history(self):
        """Save command history to file"""
        if not self.config["auto_save_history"]:
            return
            
        try:
            history_path = self.config["history_file"]
            os.makedirs(os.path.dirname(history_path), exist_ok=True)
            
            # Keep only recent commands
            recent_history = self.command_history[-self.config["max_history"]:]
            
            history_data = {
                "commands": recent_history,
                "last_saved": datetime.now().isoformat(),
                "session_id": self.session_id
            }
            
            with open(history_path, 'w', encoding='utf-8') as f:
                json.dump(history_data, f, indent=2, ensure_ascii=False)
                
        except Exception as e:
            error_handler.log_error(
                e, "CLI History Save", ErrorLevel.WARNING,
                "Failed to save command history"
            )
    
    def run(self):
        """Main CLI run loop"""
        self.is_running = True
        
        try:
            self._print_welcome()
            
            while self.is_running:
                try:
                    # Get user input
                    prompt = self._get_prompt()
                    user_input = input(prompt).strip()
                    
                    if not user_input:
                        continue
                    
                    # Add to history
                    self.command_history.append(user_input)
                    
                    # Process command
                    self._process_command(user_input)
                    
                except KeyboardInterrupt:
                    print("\n[CLI] Interrupted by user")
                    if input("Exit? (y/n): ").lower() == 'y':
                        break
                except EOFError:
                    print("\n[CLI] EOF received, exiting")
                    break
                except Exception as e:
                    error_handler.log_error(
                        e, "CLI Main Loop", ErrorLevel.ERROR,
                        "Error in CLI main loop"
                    )
                    print(f"[ERROR] {str(e)}")
        
        finally:
            self._cleanup()
    
    def _print_welcome(self):
        """Print welcome message"""
        print("=" * 70)
        print("🤖 JARVIS v1.0 - Production AI Assistant")
        print("=" * 70)
        print()
        print("Features:")
        print("  • Unified backend with session management")
        print("  • Advanced memory system with search")
        print("  • Multi-model LLM support with failover")
        print("  • File processing (PDF, Excel, TXT)")
        print("  • Real-time system monitoring")
        print()
        print("Commands:")
        print("  chat <message>     - Chat with AI")
        print("  remember <fact>    - Store memory (format: key to value)")
        print("  recall <key>       - Recall memory")
        print("  search <query>     - Search memories")
        print("  file <path>        - Process file")
        print("  status             - System status")
        print("  history            - Command history")
        print("  config             - Configuration")
        print("  help               - Show help")
        print("  exit               - Exit CLI")
        print()
        print(f"Session ID: {self.session_id[:8]}")
        print("=" * 70)
        print()
    
    def _get_prompt(self) -> str:
        """Get CLI prompt string"""
        timestamp = datetime.now().strftime("%H:%M:%S") if self.config["show_timestamps"] else ""
        if timestamp:
            return f"[{timestamp}] jarvis> "
        else:
            return "jarvis> "
    
    def _process_command(self, command: str):
        """Process user command"""
        parts = command.split(maxsplit=1)
        if not parts:
            return
        
        cmd = parts[0].lower()
        args = parts[1] if len(parts) > 1 else ""
        
        start_time = time.time()
        
        try:
            if cmd == "chat":
                self._handle_chat(args)
            elif cmd == "remember":
                self._handle_remember(args)
            elif cmd == "recall":
                self._handle_recall(args)
            elif cmd == "search":
                self._handle_search(args)
            elif cmd == "file":
                self._handle_file(args)
            elif cmd == "status":
                self._handle_status()
            elif cmd == "history":
                self._handle_history()
            elif cmd == "config":
                self._handle_config(args)
            elif cmd == "help":
                self._handle_help()
            elif cmd in ["exit", "quit", "bye"]:
                self.is_running = False
            elif cmd == "clear":
                os.system('clear' if os.name == 'posix' else 'cls')
            else:
                print(f"[ERROR] Unknown command: {cmd}")
                print("Type 'help' for available commands")
        
        except Exception as e:
            error_handler.log_error(
                e, f"CLI Command: {cmd}", ErrorLevel.ERROR,
                f"Command processing failed: {command}"
            )
            print(f"[ERROR] Command failed: {str(e)}")
        
        finally:
            execution_time = time.time() - start_time
            if self.config["verbose_mode"]:
                print(f"[DEBUG] Command executed in {execution_time:.2f}s")
    
    def _handle_chat(self, message: str):
        """Handle chat command"""
        if not message:
            print("[ERROR] Please provide a message")
            return
        
        print(f"[USER] {message}")
        print("[AI] Processing...")
        
        response = self.backend.process_request(
            session_id=self.session_id,
            request_type="chat",
            request_data={"message": message, "model": "auto"}
        )
        
        if response and response["success"]:
            ai_response = response["data"]["chat_response"]["response"]
            print(f"[AI] {ai_response}")
            
            if self.config["verbose_mode"]:
                model_used = response["data"]["chat_response"]["model_used"]
                exec_time = response["execution_time"]
                print(f"[DEBUG] Model: {model_used}, Time: {exec_time:.2f}s")
        else:
            error_msg = response.get("error", "Unknown error") if response else "No response"
            print(f"[ERROR] Chat failed: {error_msg}")
    
    def _handle_remember(self, fact: str):
        """Handle remember command"""
        if not fact:
            print("[ERROR] Please provide a fact (format: key to value)")
            return
        
        if " to " not in fact:
            print("[ERROR] Invalid format. Use: key to value")
            return
        
        key, value = fact.split(" to ", 1)
        
        response = self.backend.process_request(
            session_id=self.session_id,
            request_type="memory_store",
            request_data={"operation": "store", "key": key.strip(), "value": value.strip()}
        )
        
        if response and response["success"]:
            print(f"[MEMORY] {response['data']['result_message']}")
        else:
            error_msg = response.get("error", "Unknown error") if response else "No response"
            print(f"[ERROR] Memory storage failed: {error_msg}")
    
    def _handle_recall(self, key: str):
        """Handle recall command"""
        if not key:
            print("[ERROR] Please provide a key to recall")
            return
        
        response = self.backend.process_request(
            session_id=self.session_id,
            request_type="memory_recall",
            request_data={"operation": "recall", "key": key}
        )
        
        if response and response["success"]:
            memory_response = response["data"]["memory_response"]
            if memory_response["success"]:
                print(f"[MEMORY] {key} -> {memory_response['data']}")
            else:
                print(f"[MEMORY] Key '{key}' not found")
        else:
            error_msg = response.get("error", "Unknown error") if response else "No response"
            print(f"[ERROR] Memory recall failed: {error_msg}")
    
    def _handle_search(self, query: str):
        """Handle search command"""
        if not query:
            print("[ERROR] Please provide a search query")
            return
        
        response = self.backend.process_request(
            session_id=self.session_id,
            request_type="memory_recall",
            request_data={"operation": "search", "query": query}
        )
        
        if response and response["success"]:
            results = response["data"]["memory_response"]["data"]
            if results:
                print(f"[SEARCH] Found {len(results)} results for '{query}':")
                for i, result in enumerate(results[:10], 1):
                    if isinstance(result, dict):
                        print(f"  {i}. {result.get('key', 'Unknown')} -> {result.get('value', 'Unknown')}")
                    else:
                        print(f"  {i}. {result}")
            else:
                print(f"[SEARCH] No results found for '{query}'")
        else:
            error_msg = response.get("error", "Unknown error") if response else "No response"
            print(f"[ERROR] Search failed: {error_msg}")
    
    def _handle_file(self, file_path: str):
        """Handle file processing command"""
        if not file_path:
            print("[ERROR] Please provide a file path")
            return
        
        if not os.path.exists(file_path):
            print(f"[ERROR] File not found: {file_path}")
            return
        
        print(f"[FILE] Processing {file_path}...")
        
        response = self.backend.process_request(
            session_id=self.session_id,
            request_type="file_process",
            request_data={"file_path": file_path, "output_format": "agent"}
        )
        
        if response and response["success"]:
            file_response = response["data"]["file_response"]
            print(f"[FILE] Processed successfully:")
            print(f"  Processor: {file_response['processor_used']}")
            print(f"  Summary: {file_response['content_summary']}")
            print(f"  Processing time: {file_response['processing_time']:.2f}s")
            
            if self.config["verbose_mode"]:
                print(f"  Structured data: {len(file_response['structured_data'])} fields")
        else:
            error_msg = response.get("error", "Unknown error") if response else "No response"
            print(f"[ERROR] File processing failed: {error_msg}")
    
    def _handle_status(self):
        """Handle status command"""
        print("[STATUS] Getting system status...")
        
        status = self.backend.get_system_status()
        
        if status.get("error"):
            print(f"[ERROR] Status check failed: {status['error']}")
            return
        
        print("=" * 50)
        print("SYSTEM STATUS")
        print("=" * 50)
        
        # Service info
        service = status.get("service", {})
        uptime_hours = service.get("uptime", 0) / 3600
        print(f"Service ID: {service.get('id', 'unknown')[:8]}")
        print(f"Status: {service.get('status', 'unknown')}")
        print(f"Uptime: {uptime_hours:.1f} hours")
        print(f"Version: {service.get('version', 'unknown')}")
        print()
        
        # Sessions
        sessions = status.get("sessions", {})
        print(f"Active sessions: {sessions.get('active', 0)}")
        print(f"Total sessions: {sessions.get('total_created', 0)}")
        print()
        
        # Requests
        requests = status.get("requests", {})
        success_rate = requests.get("success_rate", 0) * 100
        print(f"Total requests: {requests.get('total', 0)}")
        print(f"Success rate: {success_rate:.1f}%")
        print()
        
        # Subsystems
        subsystems = status.get("subsystems", {})
        memory_stats = subsystems.get("memory", {})
        llm_stats = subsystems.get("llm", {})
        
        print(f"Memory entries: {memory_stats.get('total_memories', 0)}")
        print(f"LLM requests: {llm_stats.get('total_requests', 0)}")
        print(f"Average latency: {llm_stats.get('average_latency', 0):.2f}s")
        
        print("=" * 50)
    
    def _handle_history(self):
        """Handle history command"""
        if not self.command_history:
            print("[HISTORY] No commands in history")
            return
        
        print(f"[HISTORY] Last {min(20, len(self.command_history))} commands:")
        recent_commands = self.command_history[-20:]
        
        for i, cmd in enumerate(recent_commands, 1):
            print(f"  {i:2d}. {cmd}")
    
    def _handle_config(self, args: str):
        """Handle config command"""
        if not args:
            print("[CONFIG] Current configuration:")
            for key, value in self.config.items():
                print(f"  {key}: {value}")
            return
        
        # Simple config setting: config key value
        parts = args.split(maxsplit=1)
        if len(parts) != 2:
            print("[ERROR] Usage: config <key> <value>")
            return
        
        key, value = parts
        if key in self.config:
            # Convert value to appropriate type
            if isinstance(self.config[key], bool):
                value = value.lower() in ['true', '1', 'yes', 'on']
            elif isinstance(self.config[key], int):
                value = int(value)
            elif isinstance(self.config[key], float):
                value = float(value)
            
            self.config[key] = value
            print(f"[CONFIG] Set {key} = {value}")
        else:
            print(f"[ERROR] Unknown configuration key: {key}")
    
    def _handle_help(self):
        """Handle help command"""
        print("JARVIS CLI COMMANDS:")
        print("=" * 50)
        print("chat <message>     - Chat with AI assistant")
        print("remember <fact>    - Store memory (format: key to value)")
        print("recall <key>       - Recall stored memory")
        print("search <query>     - Search through memories")
        print("file <path>        - Process file (PDF, Excel, TXT)")
        print("status             - Show system status")
        print("history            - Show command history")
        print("config [key value] - Show/set configuration")
        print("clear              - Clear screen")
        print("help               - Show this help")
        print("exit               - Exit CLI")
        print("=" * 50)
        print()
        print("EXAMPLES:")
        print("  chat How do I install Python?")
        print("  remember Python to A programming language")
        print("  recall Python")
        print("  search programming")
        print("  file document.pdf")
        print("  config verbose_mode true")
    
    def _cleanup(self):
        """Cleanup CLI resources"""
        try:
            # Save history
            self._save_history()
            
            # End session
            if self.session_id:
                self.backend.end_session(self.session_id)
            
            print("\n[CLI] Session ended. Goodbye!")
            
        except Exception as e:
            error_handler.log_error(
                e, "CLI Cleanup", ErrorLevel.WARNING,
                "Error during CLI cleanup"
            )

def main():
    """Main entry point for production CLI"""
    parser = argparse.ArgumentParser(
        description='Jarvis Production CLI',
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    
    parser.add_argument('--verbose', '-v', action='store_true',
                       help='Enable verbose mode')
    parser.add_argument('--no-color', action='store_true',
                       help='Disable colored output')
    parser.add_argument('--no-history', action='store_true',
                       help='Disable command history')
    
    args = parser.parse_args()
    
    try:
        cli = ProductionCLI()
        
        # Apply command line options
        if args.verbose:
            cli.config["verbose_mode"] = True
        if args.no_color:
            cli.config["color_output"] = False
        if args.no_history:
            cli.config["auto_save_history"] = False
        
        # Run CLI
        cli.run()
        
    except KeyboardInterrupt:
        print("\n[CLI] Interrupted by user")
    except Exception as e:
        print(f"[FATAL] CLI failed to start: {str(e)}")
        return 1
    finally:
        # Ensure backend is shut down
        try:
            shutdown_jarvis_backend()
        except:
            pass
    
    return 0

if __name__ == "__main__":
    sys.exit(main())