#!/usr/bin/env python3
"""
GUI Entry Point for Jarvis AI Assistant
Launches the production GUI interface with full backend capabilities.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("[LAUNCH] Starting Jarvis Production GUI...")
    from main import main_gui
    sys.exit(main_gui())