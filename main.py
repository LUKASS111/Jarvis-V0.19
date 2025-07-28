#!/usr/bin/env python3
"""
Jarvis AI Assistant - Main Entry Point
This file serves as the main entry point for the Jarvis AI Assistant application.
"""

import sys
import os

# Add the current directory to the Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import the main function and expose important variables from the core module
from jarvis.core.main import (
    main, 
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

if __name__ == "__main__":
    main()