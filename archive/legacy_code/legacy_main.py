#!/usr/bin/env python3
"""
Jarvis AI Assistant v1.0 - Production Entry Point
Unified entry point for production-ready Jarvis AI Assistant.
Supports CLI, GUI, and backend service modes with enterprise features.
"""

import sys
import os
import argparse
import time

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Production system information
VERSION_STRING = "1.0.0"
AVAILABLE_MODELS = ["llama3:8b", "codellama:13b", "llama3:70b", "auto"]

# Production imports - Required for modern system
from jarvis.backend import get_jarvis_backend, shutdown_jarvis_backend
from jarvis.interfaces.production_cli import ProductionCLI
from jarvis.api.api_router import quick_chat, quick_remember, quick_recall

# Modern production functions for backward compatibility
def simple_llm_process(prompt: str) -> dict:
    """Modern LLM processing using production backend"""
    try:
        response = quick_chat(prompt)
        return {
            "prompt": prompt,
            "response": response,
            "timestamp": time.time(),
            "production": True
        }
    except Exception as e:
        return {
            "prompt": prompt,
            "response": f"System error: {e}",
            "timestamp": time.time(),
            "error": True
        }

def simple_log_to_file(log_data, log_file="session_log.json"):
    """Modern logging using production backend"""
    try:
        backend = get_jarvis_backend()
        # Use production memory system for logging
        return backend.memory.store_memory(
            content=str(log_data),
            memory_type="log",
            metadata={"log_file": log_file}
        )
    except Exception:
        return None

def process_interactive_input(user_input: str) -> dict:
    """Modern input processing using production backend"""
    try:
        response = quick_chat(user_input)
        return {
            "input": user_input,
            "response": response,
            "timestamp": time.time(),
            "production": True
        }
    except Exception as e:
        return {
            "input": user_input,
            "response": f"System error: {e}",
            "timestamp": time.time(),
            "error": True
        }

# Expose the variables at module level for backward compatibility
__all__ = [
    'main', 
    'VERSION_STRING', 
    'AVAILABLE_MODELS',
    'simple_llm_process',
    'simple_log_to_file', 
    'process_interactive_input'
]

def run_startup_initialization():
    """Run startup initialization for production system"""
    print("[STARTUP] Initializing Jarvis v1.0 production system...")
    
    try:
        # Initialize production backend
        backend = get_jarvis_backend()
        status = backend.get_system_status()
        
        print(f"[STARTUP] Production backend initialized")
        print(f"[STARTUP] System health: {status.get('system_metrics', {}).get('health_score', 'unknown')}")
        print(f"[STARTUP] Available subsystems: {len(status.get('subsystems', {}))}")
        
        return True
    except Exception as e:
        print(f"[FAIL] Production backend initialization failed: {e}")
        print("[FAIL] Cannot start system without production backend")
        raise

def main_gui():
    """Start the GUI application"""
    print(f"[LAUNCH] Jarvis {VERSION_STRING} - GUI Mode")
    print("=" * 60)
    
    # Run startup initialization
    run_startup_initialization()
    
    try:
        # Check for display availability first
        import os
        if 'DISPLAY' not in os.environ and sys.platform.startswith('linux'):
            print("[INFO] Headless environment detected - GUI cannot be displayed")
            print("[INFO] The professional 9-tab dashboard is available when X11 is present")
            print("[INFO] Dashboard features: Overview, Archive, CRDT, Vector DB, Agents, Monitoring, Security, API, Deployment")
            print("[INFO] Falling back to CLI mode...")
            return main_cli()
        
        # Try comprehensive dashboard first (Primary interface)
        try:
            from gui.enhanced.comprehensive_dashboard import launch_comprehensive_dashboard
            print("[GUI] Launching Comprehensive Professional Dashboard with 9 tabs...")
            result = launch_comprehensive_dashboard()
            if result is not False:  # Success or app closed normally
                return 0
            else:
                print("[WARN] Comprehensive dashboard failed to initialize")
        except ImportError as e:
            print(f"[WARN] Comprehensive dashboard not available: {e}")
        except Exception as e:
            print(f"[WARN] Comprehensive dashboard error: {e}")
        
        # Fallback to production GUI
        try:
            from jarvis.interfaces.production_gui import main as production_gui_main
            print("[GUI] Starting Production GUI interface...")
            return production_gui_main()
        except ImportError as e:
            print(f"[FAIL] Production GUI not available: {e}")
            raise
        
    except ImportError as e:
        print(f"[FAIL] Cannot start GUI: {e}")
        print("[INFO] GUI dependencies missing. Try: pip install PyQt5")
        return 1
    except Exception as e:
        print(f"[FAIL] GUI startup error: {e}")
        return 1

def main_cli():
    """Start the CLI application"""
    print(f"[LAUNCH] Jarvis {VERSION_STRING} - CLI Mode")
    print("=" * 60)
    
    # Run startup initialization
    run_startup_initialization()
    
    try:
        # Use production CLI
        print("[CLI] Starting Production CLI interface...")
        cli = ProductionCLI()
        cli.run()
        return 0
            
    except Exception as e:
        print(f"[FAIL] CLI startup error: {e}")
        return 1

def main_backend():
    """Start backend service mode"""
    print(f"[LAUNCH] Jarvis {VERSION_STRING} - Backend Service Mode")
    print("=" * 60)
    
    try:
        # Initialize and run backend service
        backend = get_jarvis_backend()
        status = backend.get_system_status()
        
        print("[BACKEND] Service initialized and running")
        print(f"[BACKEND] Service ID: {status['service']['id'][:8]}")
        print(f"[BACKEND] Health: {status.get('system_metrics', {}).get('health_score', 'unknown')}")
        print("[BACKEND] Press Ctrl+C to stop")
        
        # Keep service running
        import signal
        import time
        
        def signal_handler(signum, frame):
            """
            Handle shutdown signals for graceful backend termination.
            
            Args:
                signum (int): Signal number received
                frame: Current stack frame
            """
            print("\n[BACKEND] Shutdown signal received")
            shutdown_jarvis_backend()
            sys.exit(0)
        
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
        
        # Keep running
        while True:
            time.sleep(1)
            
    except KeyboardInterrupt:
        print("\n[BACKEND] Interrupted by user")
        shutdown_jarvis_backend()
        return 0
    except Exception as e:
        print(f"[FAIL] Backend service error: {e}")
        return 1

def detect_environment():
    """Detect if we should run in GUI or CLI mode automatically"""
    # Check for GUI availability
    try:
        import tkinter
        # If we can import tkinter, we likely have a display
        return "gui"
    except ImportError:
        pass
    
    # Check for display environment variables
    if os.environ.get('DISPLAY') or os.environ.get('WAYLAND_DISPLAY'):
        return "gui"
    
    # Check if running in terminal
    if sys.stdin.isatty() and sys.stdout.isatty():
        return "cli"
    
    # Default to CLI for headless/automated environments
    return "cli"

def main():
    """Unified main entry point for Jarvis AI Assistant v1.0"""
    
    parser = argparse.ArgumentParser(
        description='Jarvis AI Assistant v1.0 - Production System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              # Auto-detect mode (CLI/GUI)
  python main.py --cli         # Force CLI mode
  python main.py --gui         # Force GUI mode
  python main.py --backend     # Backend service mode
  python main.py --version     # Show version information
  python main.py --status      # Show system status
        """
    )
    
    parser.add_argument('--cli', action='store_true', 
                       help='Force CLI mode')
    parser.add_argument('--gui', action='store_true', 
                       help='Force GUI mode')
    parser.add_argument('--backend', action='store_true',
                       help='Run backend service mode')
    parser.add_argument('--version', action='store_true',
                       help='Show version information and exit')
    parser.add_argument('--status', action='store_true',
                       help='Show system status and exit')
    
    args = parser.parse_args()
    
    # Handle version request
    if args.version:
        print(f"Jarvis AI Assistant {VERSION_STRING}")
        print(f"Available models: {', '.join(AVAILABLE_MODELS)}")
        print("Production backend: Available")
        return 0
    
    # Handle status request
    if args.status:
        try:
            run_startup_initialization()
            backend = get_jarvis_backend()
            status = backend.get_system_status()
            
            print("JARVIS SYSTEM STATUS")
            print("=" * 40)
            print(f"Version: {VERSION_STRING}")
            print(f"Mode: Production")
            print(f"Service ID: {status['service']['id'][:8]}")
            print(f"Uptime: {status['service']['uptime']:.1f}s")
            print(f"Health Score: {status.get('system_metrics', {}).get('health_score', 'unknown')}")
            
            subsystems = status.get('subsystems', {})
            print(f"Memory entries: {subsystems.get('memory', {}).get('total_memories', 0)}")
            print(f"Active sessions: {status.get('sessions', {}).get('active', 0)}")
            print(f"Total requests: {status.get('requests', {}).get('total', 0)}")
            
            shutdown_jarvis_backend()
            return 0
        except Exception as e:
            print(f"Status check failed: {e}")
            return 1
    
    # Determine mode
    exclusive_modes = [args.gui, args.cli, args.backend]
    if sum(exclusive_modes) > 1:
        print("[ERROR] Cannot specify multiple modes")
        return 1
    elif args.backend:
        mode = "backend"
    elif args.gui:
        mode = "gui"
    elif args.cli:
        mode = "cli"
    else:
        mode = detect_environment()
        print(f"[AUTO] Auto-detected mode: {mode}")
    
    # Show system information
    print(f"[SYSTEM] Jarvis v{VERSION_STRING}")
    print("[SYSTEM] Production system active")
    
    # Run appropriate mode
    try:
        if mode == "backend":
            return main_backend()
        elif mode == "gui":
            return main_gui()
        else:
            return main_cli()
    finally:
        # Ensure cleanup
        try:
            shutdown_jarvis_backend()
        except:
            pass

if __name__ == "__main__":
    sys.exit(main())