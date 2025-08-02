#!/usr/bin/env python3
"""
Jarvis AI Assistant - Unified Entry Point
This file serves as the main unified entry point for the Jarvis AI Assistant application.
Supports both CLI and GUI modes with unified initialization.
"""

import sys
import os
import argparse

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main function and expose important variables from the core module
from jarvis.core.main import (
    main as main_cli, 
    VERSION_STRING,
    AVAILABLE_MODELS,
    simple_llm_process,
    simple_log_to_file,
    process_interactive_input
)

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
    """Run all startup initialization tasks that should happen regardless of mode"""
    print("[STARTUP] Initializing automatic version-based archive cleanup...")
    try:
        from jarvis.core.archive_purge_manager import auto_purge_startup, get_archive_health
        from jarvis.core.error_handler import error_handler, ErrorLevel
        
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
        
        return True
        
    except Exception as e:
        print(f"[WARN] Archive purge system initialization failed: {e}")
        return False

def main_gui():
    """Start the GUI application with unified initialization"""
    print(f"[LAUNCH] Jarvis {VERSION_STRING} - GUI Mode")
    print("=" * 60)
    
    # Run unified startup initialization
    run_startup_initialization()
    
    try:
        from gui.modern_gui import SimplifiedJarvisGUI
        print("[GUI] Starting Jarvis GUI interface...")
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
    """Start the CLI application (existing functionality)"""
    print(f"[LAUNCH] Jarvis {VERSION_STRING} - CLI Mode")
    print("=" * 60)
    
    # Run unified startup initialization
    run_startup_initialization()
    
    try:
        from jarvis.core.main import main as core_main
        # Skip startup init since we already did it
        return core_main(skip_startup_init=True)
    except Exception as e:
        print(f"[FAIL] CLI startup error: {e}")
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
    """Unified main entry point for Jarvis AI Assistant"""
    parser = argparse.ArgumentParser(
        description='Jarvis AI Assistant - Unified Entry Point',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python main.py              # Auto-detect mode (CLI/GUI)
  python main.py --cli         # Force CLI mode
  python main.py --gui         # Force GUI mode
  python main.py --version     # Show version information
        """
    )
    
    parser.add_argument('--cli', action='store_true', 
                       help='Force CLI mode')
    parser.add_argument('--gui', action='store_true', 
                       help='Force GUI mode')
    parser.add_argument('--version', action='store_true',
                       help='Show version information and exit')
    
    args = parser.parse_args()
    
    # Handle version request
    if args.version:
        print(f"Jarvis AI Assistant {VERSION_STRING}")
        print(f"Available models: {', '.join(AVAILABLE_MODELS)}")
        return 0
    
    # Determine mode
    if args.gui and args.cli:
        print("[ERROR] Cannot specify both --gui and --cli modes")
        return 1
    elif args.gui:
        mode = "gui"
    elif args.cli:
        mode = "cli"
    else:
        mode = detect_environment()
        print(f"[AUTO] Auto-detected mode: {mode}")
    
    # Run appropriate mode
    if mode == "gui":
        return main_gui()
    else:
        return main_cli()

if __name__ == "__main__":
    sys.exit(main())