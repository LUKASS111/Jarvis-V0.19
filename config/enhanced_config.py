#!/usr/bin/env python3
"""
Enhanced Configuration Manager
=============================
Enhanced configuration management with improved Python patterns.
"""

import logging
from pathlib import Path
import json
from datetime import datetime
from typing import Dict, Any, Optional

# Configure logging
logger = logging.getLogger(__name__)

class EnhancedConfigurationManager:
    """Enhanced configuration management with improved features"""
    
    def __init__(self, config_dir: Path = None):
        self.config_dir = config_dir or Path("config")
        self.config_dir.mkdir(parents=True, exist_ok=True)
        self.config_file = self.config_dir / "settings.json"
        self._config_cache = {}
        
        logger.info(f"Configuration manager initialized: {self.config_dir}")
    
    def load_configuration(self) -> Dict[str, Any]:
        """Load configuration using improved file handling"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    self._config_cache = config
                    logger.info("Configuration loaded successfully")
                    return config
            else:
                config = self._get_default_configuration()
                self.save_configuration(config)
                return config
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            return self._get_default_configuration()
    
    def save_configuration(self, config: Dict[str, Any]) -> bool:
        """Save configuration with improved error handling"""
        try:
            # Add metadata
            config['_metadata'] = {
                'last_modified': datetime.now().isoformat(),
                'version': '1.0.0'
            }
            
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self._config_cache = config
            logger.info("Configuration saved successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to save configuration: {e}")
            return False
    
    def get_setting(self, key: str, default: Any = None) -> Any:
        """Get configuration setting with improved default handling"""
        if not self._config_cache:
            self.load_configuration()
        
        keys = key.split('.')
        value = self._config_cache
        
        try:
            for k in keys:
                value = value[k]
            return value
        except (KeyError, TypeError):
            logger.debug(f"Setting not found: {key}, using default: {default}")
            return default
    
    def set_setting(self, key: str, value: Any) -> bool:
        """Set configuration setting with improved path handling"""
        if not self._config_cache:
            self.load_configuration()
        
        keys = key.split('.')
        config = self._config_cache
        
        # Navigate to parent
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        
        # Set value
        config[keys[-1]] = value
        
        return self.save_configuration(self._config_cache)
    
    def _get_default_configuration(self) -> Dict[str, Any]:
        """Get default configuration with enhanced structure"""
        return {
            "application": {
                "name": "Jarvis 1.0.0",
                "version": "1.0.0",
                "theme": "professional"
            },
            "gui": {
                "window_size": [1200, 800],
                "font_family": "Arial",
                "font_size": 10,
                "show_tooltips": True
            },
            "performance": {
                "memory_limit_mb": 512,
                "cache_size_mb": 128,
                "thread_pool_size": 4,
                "enable_monitoring": True
            },
            "logging": {
                "level": "INFO",
                "enable_file_logging": True,
                "log_rotation": True
            }
        }

# Initialize global configuration manager
config_manager = EnhancedConfigurationManager()

def get_config() -> EnhancedConfigurationManager:
    """Get global configuration manager instance"""
    return config_manager