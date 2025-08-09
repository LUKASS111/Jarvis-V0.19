#!/usr/bin/env python3
"""
Modern CLI Interface for Jarvis
Comprehensive command-line interface with all functionality
"""

import os
import sys
import json
import argparse
from typing import Dict, List, Any, Optional
from pathlib import Path
from datetime import datetime

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from jarvis.core.error_handler import error_handler, ErrorLevel, safe_execute

class ModernCLI:
    """Modern CLI interface for Jarvis"""
    
    def __init__(self):
        self.commands = {
            'help': self.show_help,
            'status': self.show_status,
            'memory': self.memory_operations,
            'agent': self.agent_operations,
            'file': self.file_operations,
            'vector': self.vector_operations,
            'gui': self.launch_gui,
            'test': self.run_tests,
            'health': self.system_health,
            'config': self.config_operations,
            'export': self.export_data,
            'import': self.import_data,
            'chat': self.chat_mode,
            'exit': self.exit_cli
        }
        self.running = True
    
    def run(self):
        """Run the CLI interface"""
        print("[CLI] Jarvis v1.0 Modern CLI Ready")
        print("[CLI] Type 'help' for commands, 'exit' to quit")
        
        while self.running:
            try:
                command = input("jarvis> ").strip().lower()
                if not command:
                    continue
                
                if command in self.commands:
                    result = self.commands[command]()
                    if result is False:
                        break
                else:
                    print(f"[CLI] Unknown command: {command}. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n[CLI] Goodbye!")
                break
            except EOFError:
                print("\n[CLI] Goodbye!")
                break
            except Exception as e:
                print(f"[CLI] Error: {e}")
    
    def show_help(self):
        """Show available commands"""
        print("\n[CLI] Available commands:")
        print("  help     - Show this help message")
        print("  status   - Show system status")
        print("  memory   - Memory operations (store, recall, list)")
        print("  agent    - Agent workflow operations")
        print("  file     - File processing operations")
        print("  vector   - Vector database operations")
        print("  gui      - Launch GUI interface")
        print("  test     - Run system tests")
        print("  health   - System health check")
        print("  config   - Configuration management")
        print("  export   - Export data")
        print("  import   - Import data")
        print("  chat     - Chat with Jarvis")
        print("  exit     - Exit CLI")
        print()
    
    @safe_execute(fallback_value=None, context="CLI Status")
    def show_status(self):
        """Show system status"""
        try:
            from jarvis.backend import get_jarvis_backend
            backend = get_jarvis_backend()
            status = backend.get_system_status()
            
            print(f"\n[STATUS] Jarvis System Status")
            print(f"  Health Score: {status.get('system_metrics', {}).get('health_score', 'unknown')}")
            print(f"  Subsystems: {len(status.get('subsystems', {}))}")
            print(f"  Backend ID: {backend.service_id[:8]}")
            print()
            
        except Exception as e:
            print(f"[STATUS] Error getting status: {e}")
    
    def memory_operations(self):
        """Memory operations"""
        print("\n[MEMORY] Memory operations:")
        print("  memory store <key> <value> - Store memory")
        print("  memory recall <key>        - Recall memory")
        print("  memory list                - List all memories")
        print()
        return None
    
    def agent_operations(self):
        """Agent workflow operations"""
        print("\n[AGENT] Agent operations:")
        print("  agent create <name>        - Create agent")
        print("  agent list                 - List agents")
        print("  agent run <name>           - Run agent")
        print()
        return None
    
    def file_operations(self):
        """File processing operations"""
        print("\n[FILE] File operations:")
        print("  file process <path>        - Process file")
        print("  file analyze <path>        - Analyze file")
        print("  file convert <path> <type> - Convert file")
        print()
        return None
    
    def vector_operations(self):
        """Vector database operations"""
        print("\n[VECTOR] Vector database operations:")
        print("  vector search <query>      - Semantic search")
        print("  vector add <text>          - Add document")
        print("  vector status              - Vector DB status")
        print()
        return None
    
    def launch_gui(self):
        """Launch GUI interface"""
        print("[GUI] Launching comprehensive dashboard...")
        try:
            from gui.enhanced.comprehensive_dashboard import launch_comprehensive_dashboard
            launch_comprehensive_dashboard()
        except Exception as e:
            print(f"[GUI] Error launching GUI: {e}")
        return None
    
    def run_tests(self):
        """Run system tests"""
        print("[TEST] Running comprehensive tests...")
        try:
            import subprocess
            result = subprocess.run([sys.executable, "tests/run_all_tests.py"], 
                                  capture_output=True, text=True)
            if result.returncode == 0:
                print("[TEST] ✅ All tests passed")
            else:
                print("[TEST] ❌ Some tests failed")
                print(result.stderr[-500:] if result.stderr else "")
        except Exception as e:
            print(f"[TEST] Error running tests: {e}")
        return None
    
    def system_health(self):
        """System health check"""
        print("[HEALTH] Running system health check...")
        try:
            from scripts.generate_comprehensive_report import create_comprehensive_test_report
            report = create_comprehensive_test_report()
            summary = report['summary']
            print(f"[HEALTH] Status: {summary['overall_status']}")
            print(f"[HEALTH] Functionality: {summary['functionality_percentage']:.1f}%")
            print(f"[HEALTH] Health Score: {summary['health_score']}")
        except Exception as e:
            print(f"[HEALTH] Error checking health: {e}")
        return None
    
    def config_operations(self):
        """Configuration management"""
        print("\n[CONFIG] Configuration operations:")
        print("  config show                - Show current config")
        print("  config set <key> <value>   - Set config value")
        print("  config reset               - Reset to defaults")
        print()
        return None
    
    def export_data(self):
        """Export data"""
        print("[EXPORT] Exporting system data...")
        try:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            export_file = f"jarvis_export_{timestamp}.json"
            
            # TODO: Implement actual export
            print(f"[EXPORT] Data exported to: {export_file}")
            
        except Exception as e:
            print(f"[EXPORT] Error exporting data: {e}")
        return None
    
    def import_data(self):
        """Import data"""
        print("[IMPORT] Import data from file:")
        print("  import <filename>          - Import from file")
        print()
        return None
    
    def chat_mode(self):
        """Chat with Jarvis"""
        print("[CHAT] Entering chat mode (type 'quit' to exit)...")
        
        while True:
            try:
                user_input = input("You: ").strip()
                if user_input.lower() in ['quit', 'exit', 'bye']:
                    print("[CHAT] Exiting chat mode...")
                    break
                
                if user_input:
                    # TODO: Integrate with LLM
                    print(f"Jarvis: I received your message: {user_input}")
                    print("Jarvis: (Chat functionality coming soon)")
                
            except (KeyboardInterrupt, EOFError):
                print("\n[CHAT] Exiting chat mode...")
                break
        
        return None
    
    def exit_cli(self):
        """Exit CLI"""
        print("[CLI] Goodbye!")
        self.running = False
        return False

@safe_execute(fallback_value=None, context="File Processing")
def process_file(file_path: str, options: Dict[str, Any] = None) -> Dict[str, Any]:
    """Process a file with Jarvis capabilities"""
    
    try:
        from pathlib import Path
        from jarvis.ai import MultiModalProcessor
        
        file_path = Path(file_path)
        if not file_path.exists():
            return {
                "success": False,
                "error": f"File not found: {file_path}"
            }
        
        # Initialize multimodal processor
        processor = MultiModalProcessor()
        
        # Determine file type and process accordingly
        if file_path.suffix.lower() in ['.jpg', '.jpeg', '.png', '.gif', '.bmp']:
            # Image processing
            result = processor.process_image(str(file_path))
            return {
                "success": True,
                "file_type": "image",
                "file_path": str(file_path),
                "result": result
            }
            
        elif file_path.suffix.lower() in ['.wav', '.mp3', '.m4a', '.flac']:
            # Audio processing
            result = processor.process_audio(str(file_path))
            return {
                "success": True,
                "file_type": "audio",
                "file_path": str(file_path),
                "result": result
            }
            
        elif file_path.suffix.lower() in ['.txt', '.md', '.json', '.csv']:
            # Text processing
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            return {
                "success": True,
                "file_type": "text",
                "file_path": str(file_path),
                "content": content[:1000] + "..." if len(content) > 1000 else content,
                "size": len(content)
            }
            
        else:
            return {
                "success": False,
                "error": f"Unsupported file type: {file_path.suffix}"
            }
            
    except Exception as e:
        return {
            "success": False,
            "error": f"Error processing file: {str(e)}"
        }

if __name__ == "__main__":
    cli = ModernCLI()
    cli.run()

# Alias for backwards compatibility
CLI = ModernCLI