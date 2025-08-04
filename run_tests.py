#!/usr/bin/env python3
"""
Comprehensive Test Runner Entry Point for Jarvis AI Assistant
This file serves as the entry point for running ALL program tests.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and run the comprehensive test suite
from tests.run_all_tests import main

if __name__ == "__main__":
    main()