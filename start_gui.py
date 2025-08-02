#!/usr/bin/env python3
"""
GUI Entry Point for Jarvis AI Assistant (LEGACY)
This file now redirects to the unified entry point with GUI mode.
For new installations, use: python main.py --gui
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

if __name__ == "__main__":
    print("[REDIRECT] Using unified entry point for GUI mode...")
    from main import main_gui
    sys.exit(main_gui())