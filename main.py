#!/usr/bin/env python3
"""
Jarvis AI Assistant v1.0 - Production Entry Point
Professional 9-tab comprehensive dashboard interface with full functionality.
Complete system with all features accessible via modern GUI.
"""

import sys
import os
import argparse

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

VERSION_STRING = "1.0.0"
AVAILABLE_MODELS = ["llama3:8b", "mistral:7b", "gemma:2b", "phi:latest"]

def main():
    """Jarvis entry point - Comprehensive 9-tab dashboard with full functionality"""
    
    parser = argparse.ArgumentParser(
        description="Jarvis AI Assistant v1.0 - Professional Dashboard",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              # Launch comprehensive 9-tab dashboard
  python main.py --cli        # Launch modern CLI interface
  python main.py --backend    # Start backend service
        """
    )
    
    parser.add_argument(
        "--cli", 
        action="store_true", 
        help="Launch CLI interface instead of GUI"
    )
    
    parser.add_argument(
        "--backend", 
        action="store_true", 
        help="Start backend service mode"
    )
    
    parser.add_argument(
        "--version", 
        action="version", 
        version=f"Jarvis AI Assistant v{VERSION_STRING}"
    )

    args = parser.parse_args()

    print(f"[LAUNCH] Jarvis {VERSION_STRING} - Production System with Full Functionality")
    print("=" * 60)

    # Initialize production backend
    try:
        from jarvis.backend import get_jarvis_backend
        backend = get_jarvis_backend()
        status = backend.get_system_status()
        print(f"[STARTUP] Production backend initialized")
        print(f"[STARTUP] System health: {status.get('system_metrics', {}).get('health_score', 'unknown')}")
    except Exception as e:
        print(f"[FAIL] Backend initialization failed: {e}")
        return 1

    if args.backend:
        return start_backend_service()
    elif args.cli:
        return start_cli()
    else:
        return start_comprehensive_dashboard()

def start_comprehensive_dashboard():
    """Launch the comprehensive 9-tab dashboard with full functionality"""
    print("[GUI] Starting Comprehensive Professional Dashboard...")
    print("[GUI] Features: Overview, Archive, CRDT, Vector DB, Agents, Monitoring, Security, API, Deployment")
    
    # Check for display availability
    if 'DISPLAY' not in os.environ and sys.platform.startswith('linux'):
        print("[ERROR] GUI requires X11 display - DISPLAY variable not set")
        print("[INFO] Use --cli flag for command-line interface")
        return 1
    
    try:
        from gui.enhanced.comprehensive_dashboard import launch_comprehensive_dashboard
        result = launch_comprehensive_dashboard()
        return 0 if result is not False else 1
        
    except ImportError as e:
        print(f"[ERROR] Comprehensive dashboard not available: {e}")
        print("[INFO] Install PyQt5: pip install PyQt5")
        return 1
    except Exception as e:
        print(f"[ERROR] Dashboard startup failed: {e}")
        return 1

def start_cli():
    """Launch CLI interface"""
    print("[CLI] Starting CLI Interface...")
    
    try:
        from jarvis.interfaces.cli import CLI
        cli = CLI()
        cli.run()
        return 0
    except ImportError as e:
        print(f"[ERROR] CLI interface not available: {e}")
        return 1
    except Exception as e:
        print(f"[ERROR] CLI startup failed: {e}")
        return 1

def start_backend_service():
    """Start backend service mode"""
    print("[BACKEND] Starting Backend Service...")
    
    try:
        from jarvis.backend import get_jarvis_backend, shutdown_jarvis_backend
        backend = get_jarvis_backend()
        status = backend.get_system_status()
        
        print(f"[BACKEND] Service initialized - ID: {status['service']['id'][:8]}")
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
        
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[BACKEND] Shutting down...")
            shutdown_jarvis_backend()
        
        return 0
        
    except Exception as e:
        print(f"[ERROR] Backend startup failed: {e}")
        return 1

def simple_log_to_file(data, filename="logs/jarvis.log"):
    """Simple file logging function for testing"""
    import json
    import os
    
    # Ensure log directory exists
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    
    try:
        with open(filename, 'a') as f:
            json.dump(data, f)
            f.write('\n')
        return True  # Return success indicator
    except Exception as e:
        print(f"[WARN] Failed to write log: {e}")
        return False

if __name__ == "__main__":
    sys.exit(main())