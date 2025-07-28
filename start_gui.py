#!/usr/bin/env python3
"""
GUI Entry Point for Jarvis AI Assistant
This file serves as the entry point for starting the GUI application.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and start the GUI
from gui.modern_gui import SimplifiedJarvisGUI

if __name__ == "__main__":
    gui = SimplifiedJarvisGUI()
    gui.run()