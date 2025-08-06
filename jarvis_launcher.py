#!/usr/bin/env python3
"""
Jarvis V0.19 - Unified Clean Launcher
Single entry point that properly loads the comprehensive 9-tab professional dashboard
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import main entry point
from main import main

if __name__ == "__main__":
    """
    Unified entry point that ensures proper loading sequence:
    1. Try comprehensive 9-tab professional dashboard (when display available)
    2. Fallback to production CLI (headless environments)
    3. Emergency fallback to legacy systems (compatibility)
    
    This resolves the entry point confusion between:
    - main.py (this delegates to)
    - start_gui.py (deprecated)
    - production_gui.py (fallback component)
    - comprehensive_dashboard.py (target interface)
    """
    sys.exit(main())