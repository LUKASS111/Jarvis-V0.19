#!/usr/bin/env python3
"""
Jarvis AI Assistant v1.0 - Production Entry Point
Unified entry point for production-ready Jarvis AI Assistant.
Supports CLI, GUI, and backend service modes with enterprise features.
"""

import sys
import os
import argparse

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Production system information
VERSION_STRING = "1.0.0"
AVAILABLE_MODELS = ["llama3:8b", "codellama:13b", "llama3:70b", "auto"]

# Production imports
try:
    from jarvis.backend import get_jarvis_backend, shutdown_jarvis_backend
    from jarvis.interfaces.production_cli import ProductionCLI
    from jarvis.api.api_router import quick_chat, quick_remember, quick_recall
    PRODUCTION_BACKEND_AVAILABLE = True
except ImportError as e:
    print(f"[WARN] Production backend not available: {e}")
    PRODUCTION_BACKEND_AVAILABLE = False
    # Fallback to legacy system
    from jarvis.core.main import (
        main as legacy_main_cli, 
        simple_llm_process,
        simple_log_to_file,
        process_interactive_input
    )

# Expose functions for backward compatibility
def simple_llm_process(prompt: str) -> dict:
    """Backward compatible LLM processing"""
    if PRODUCTION_BACKEND_AVAILABLE:
        try:
            response = quick_chat(prompt)
            return {
                "prompt": prompt,
                "response": response,
                "timestamp": time.time(),
                "production": True
            }
        except:
            pass
    
    # Fallback to legacy
    try:
        from jarvis.core.main import simple_llm_process as legacy_llm
        return legacy_llm(prompt)
    except:
        return {
            "prompt": prompt,
            "response": "System not available",
            "timestamp": time.time(),
            "error": True
        }

def simple_log_to_file(log_data, log_file="session_log.json"):
    """Backward compatible logging"""
    try:
        from jarvis.core.main import simple_log_to_file as legacy_log
        return legacy_log(log_data, log_file)
    except:
        return None

def process_interactive_input(user_input: str) -> dict:
    """Backward compatible input processing"""
    if PRODUCTION_BACKEND_AVAILABLE:
        try:
            response = quick_chat(user_input)
            return {
                "input": user_input,
                "response": response,
                "timestamp": time.time(),
                "production": True
            }
        except:
            pass
    
    # Fallback to legacy
    try:
        from jarvis.core.main import process_interactive_input as legacy_input
        return legacy_input(user_input)
    except:
        return {
            "input": user_input,
            "response": "System not available",
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
    
    if PRODUCTION_BACKEND_AVAILABLE:
        try:
            # Initialize production backend
            backend = get_jarvis_backend()
            status = backend.get_system_status()
            
            print(f"[STARTUP] Production backend initialized")
            print(f"[STARTUP] System health: {status.get('system_metrics', {}).get('health_score', 'unknown')}")
            print(f"[STARTUP] Available subsystems: {len(status.get('subsystems', {}))}")
            
            return True
        except Exception as e:
            print(f"[WARN] Production backend initialization failed: {e}")
            print("[WARN] Falling back to legacy system")
    
    # Fallback to legacy initialization
    try:
        from jarvis.core.archive_purge_manager import auto_purge_startup, get_archive_health
        
        purge_result = auto_purge_startup()
        
        if purge_result:
            summary = purge_result.get('summary', {})
            entries_removed = summary.get('entries_removed', 0)
            
            if entries_removed > 0:
                print(f"[PURGE] Legacy cleanup: {entries_removed} old entries removed")
            else:
                print("[PURGE] Archive is clean")
        
        # Show archive health
        health = get_archive_health()
        print(f"[ARCHIVE] Health: {health['health_score']}/100, Size: {health['archive_size_mb']}MB")
        
        return True
        
    except Exception as e:
        print(f"[WARN] Legacy system initialization failed: {e}")
        return False

def main_gui():
    """Start the GUI application"""
    print(f"[LAUNCH] Jarvis {VERSION_STRING} - GUI Mode")
    print("=" * 60)
    
    # Run startup initialization
    run_startup_initialization()
    
    try:
        if PRODUCTION_BACKEND_AVAILABLE:
            # Use production GUI when available
            try:
                from jarvis.interfaces.production_gui import ProductionGUI
                print("[GUI] Starting Production GUI interface...")
                gui = ProductionGUI()
                return gui.run()
            except ImportError:
                print("[GUI] Production GUI not available, using legacy GUI")
        
        # Fallback to legacy GUI
        from gui.modern_gui import SimplifiedJarvisGUI
        print("[GUI] Starting Legacy GUI interface...")
        gui = SimplifiedJarvisGUI()
        return gui.run()
        
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
        if PRODUCTION_BACKEND_AVAILABLE:
            # Use production CLI
            print("[CLI] Starting Production CLI interface...")
            cli = ProductionCLI()
            cli.run()
            return 0
        else:
            # Fallback to legacy CLI
            print("[CLI] Starting Legacy CLI interface...")
            from jarvis.core.main import main as legacy_main
            return legacy_main(skip_startup_init=True)
            
    except Exception as e:
        print(f"[FAIL] CLI startup error: {e}")
        return 1

def main_backend():
    """Start backend service mode"""
    print(f"[LAUNCH] Jarvis {VERSION_STRING} - Backend Service Mode")
    print("=" * 60)
    
    if not PRODUCTION_BACKEND_AVAILABLE:
        print("[FAIL] Production backend not available")
        return 1
    
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
    # Handle global variable properly
    global PRODUCTION_BACKEND_AVAILABLE
    
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
    parser.add_argument('--production', action='store_true',
                       help='Force production mode (default)')
    parser.add_argument('--legacy', action='store_true',
                       help='Force legacy mode')
    
    args = parser.parse_args()
    
    # Handle version request
    if args.version:
        print(f"Jarvis AI Assistant {VERSION_STRING}")
        print(f"Available models: {', '.join(AVAILABLE_MODELS)}")
        if PRODUCTION_BACKEND_AVAILABLE:
            print("Production backend: Available")
        else:
            print("Production backend: Not available (using legacy)")
        return 0
    
    # Handle status request
    if args.status:
        if PRODUCTION_BACKEND_AVAILABLE and not args.legacy:
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
        else:
            print("JARVIS SYSTEM STATUS")
            print("=" * 40)
            print(f"Version: {VERSION_STRING}")
            print(f"Mode: Legacy")
            print("Production backend: Not available")
            return 0
    
    # Force legacy mode if requested
    if args.legacy:
        PRODUCTION_BACKEND_AVAILABLE = False
    
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
    if PRODUCTION_BACKEND_AVAILABLE and not args.legacy:
        print("[SYSTEM] Production system active")
    else:
        print("[SYSTEM] Legacy system active")
    
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
        if PRODUCTION_BACKEND_AVAILABLE:
            try:
                shutdown_jarvis_backend()
            except:
                pass

if __name__ == "__main__":
    import time
    sys.exit(main())