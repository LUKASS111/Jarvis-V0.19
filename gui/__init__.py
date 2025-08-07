"""
GUI Package Initialization
==========================
Modern GUI framework with comprehensive interface components.
"""

import logging
from pathlib import Path

# Configure logging for GUI components
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize GUI component registry
gui_components = {
    'main_window': 'gui.main_window',
    'dashboard': 'gui.dashboard',
    'configuration_interface': 'gui.interfaces.configuration_interface',
    'core_system_interface': 'gui.interfaces.core_system_interface',
    'processing_interface': 'gui.interfaces.processing_interface'
}

logger.info("GUI framework initialized with modern component architecture")