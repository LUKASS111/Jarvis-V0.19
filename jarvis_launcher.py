#!/usr/bin/env python3
"""
Jarvis V1.0 - Modern Clean Launcher
Single entry point that loads the comprehensive 9-tab professional dashboard only.
All legacy files removed.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import main entry point
from main import main

if __name__ == "__main__":
    """
    Modern entry point with clean implementation:
    1. Comprehensive 9-tab professional dashboard (primary)
    2. Modern CLI interface (--cli flag)
    3. Backend service (--backend flag)
    
    No legacy fallbacks - clean modern codebase only.
    """
    sys.exit(main())