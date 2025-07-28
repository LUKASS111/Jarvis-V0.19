#!/usr/bin/env python3
"""
Test Runner Entry Point for Jarvis AI Assistant
This file serves as the entry point for running all tests.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the test suite
from scripts.run_tests import main

if __name__ == "__main__":
    main()