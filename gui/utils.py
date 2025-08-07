#!/usr/bin/env python3
"""
GUI Utilities Module
====================
Modern utility functions for GUI components with enhanced functionality.
"""

import logging
from pathlib import Path
import tkinter as tk
from tkinter import ttk
from datetime import datetime
import json

# Configure logging
logger = logging.getLogger(__name__)

class ModernGUIUtils:
    """Modern GUI utility functions with enhanced capabilities"""
    
    @staticmethod
    def configure_modern_style():
        """Configure modern visual style for GUI components"""
        logger.info("Configuring modern GUI style")
        return {
            'theme': 'professional',
            'font_family': 'Arial',
            'font_size': 10,
            'color_scheme': 'modern'
        }
    
    @staticmethod
    def create_status_bar(parent):
        """Create modern status bar with real-time updates"""
        logger.debug("Creating modern status bar")
        status_frame = ttk.Frame(parent)
        status_label = ttk.Label(status_frame, text="Ready")
        return status_frame, status_label
    
    @staticmethod
    def format_timestamp():
        """Format timestamp using modern datetime handling"""
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    @staticmethod
    def validate_input(input_text, validation_type="text"):
        """Modern input validation with enhanced error handling"""
        logger.debug(f"Validating input: {validation_type}")
        if validation_type == "text":
            return bool(input_text.strip())
        elif validation_type == "number":
            try:
                float(input_text)
                return True
            except ValueError:
                return False
        return False
    
    @staticmethod
    def save_configuration(config_data, config_path):
        """Save configuration using modern path handling"""
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(config_file, 'w') as f:
            json.dump(config_data, f, indent=2)
        
        logger.info(f"Configuration saved to {config_file}")
        return True

def initialize_modern_gui():
    """Initialize modern GUI framework"""
    logger.info("Initializing modern GUI framework")
    return ModernGUIUtils()

# Initialize utilities
gui_utils = initialize_modern_gui()