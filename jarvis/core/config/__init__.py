"""
Configuration Management System for Jarvis 1.0.0
Centralized configuration management with environment support, validation, and hot reloading
"""

import os
import json
import yaml
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Union, Type
from dataclasses import dataclass, field
from enum import Enum
import threading
from pathlib import Path
import time


class ConfigFormat(Enum):
    """Supported configuration formats"""
    JSON = "json"
    YAML = "yaml"
    ENV = "env"


@dataclass
class ConfigSchema:
    """Configuration schema definition"""
    key: str
    value_type: Type
    required: bool = False
    default: Any = None
    description: str = ""
    validation_rules: List[str] = field(default_factory=list)
    env_var: Optional[str] = None


@dataclass
class ValidationResult:
    """Configuration validation result"""
    valid: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)


class ConfigProvider(ABC):
    """Abstract base class for configuration providers"""
    
    @abstractmethod
    def load(self, source: str) -> Dict[str, Any]:
        """Load configuration from source"""
        pass
    
    @abstractmethod
    def save(self, config: Dict[str, Any], destination: str) -> bool:
        """Save configuration to destination"""
        pass


class JSONConfigProvider(ConfigProvider):
    """JSON configuration provider"""
    
    def load(self, source: str) -> Dict[str, Any]:
        """Load configuration from JSON file"""
        try:
            with open(source, 'r') as f:
                return json.load(f)
        except Exception as e:
            raise ValueError(f"Failed to load JSON config from {source}: {e}")
    
    def save(self, config: Dict[str, Any], destination: str) -> bool:
        """Save configuration to JSON file"""
        try:
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            with open(destination, 'w') as f:
                json.dump(config, f, indent=2)
            return True
        except Exception as e:
            logging.error(f"Failed to save JSON config to {destination}: {e}")
            return False


class YAMLConfigProvider(ConfigProvider):
    """YAML configuration provider"""
    
    def load(self, source: str) -> Dict[str, Any]:
        """Load configuration from YAML file"""
        try:
            with open(source, 'r') as f:
                return yaml.safe_load(f) or {}
        except Exception as e:
            raise ValueError(f"Failed to load YAML config from {source}: {e}")
    
    def save(self, config: Dict[str, Any], destination: str) -> bool:
        """Save configuration to YAML file"""
        try:
            os.makedirs(os.path.dirname(destination), exist_ok=True)
            with open(destination, 'w') as f:
                yaml.dump(config, f, default_flow_style=False, indent=2)
            return True
        except Exception as e:
            logging.error(f"Failed to save YAML config to {destination}: {e}")
            return False


class EnvConfigProvider(ConfigProvider):
    """Environment variable configuration provider"""
    
    def __init__(self, prefix: str = "JARVIS_"):
        self.prefix = prefix
    
    def load(self, source: str = None) -> Dict[str, Any]:
        """Load configuration from environment variables"""
        config = {}
        for key, value in os.environ.items():
            if key.startswith(self.prefix):
                config_key = key[len(self.prefix):].lower().replace('_', '.')
                config[config_key] = self._parse_env_value(value)
        return config
    
    def save(self, config: Dict[str, Any], destination: str = None) -> bool:
        """Save configuration to environment (not persistent)"""
        try:
            for key, value in config.items():
                env_key = f"{self.prefix}{key.upper().replace('.', '_')}"
                os.environ[env_key] = str(value)
            return True
        except Exception as e:
            logging.error(f"Failed to save config to environment: {e}")
            return False
    
    def _parse_env_value(self, value: str) -> Any:
        """Parse environment variable value to appropriate type"""
        # Try to parse as JSON first
        try:
            return json.loads(value)
        except:
            pass
        
        # Try boolean
        if value.lower() in ('true', 'false'):
            return value.lower() == 'true'
        
        # Try integer
        try:
            return int(value)
        except:
            pass
        
        # Try float
        try:
            return float(value)
        except:
            pass
        
        # Return as string
        return value


class ConfigManager:
    """Main configuration manager"""
    
    def __init__(self, config_dir: str = None):
        self.config_dir = config_dir or os.path.join(os.path.dirname(__file__), "..", "..", "..", "config")
        self.config: Dict[str, Any] = {}
        self.schema: Dict[str, ConfigSchema] = {}
        self.providers: Dict[ConfigFormat, ConfigProvider] = {
            ConfigFormat.JSON: JSONConfigProvider(),
            ConfigFormat.YAML: YAMLConfigProvider(),
            ConfigFormat.ENV: EnvConfigProvider()
        }
        self.watchers: List[callable] = []
        self.lock = threading.RLock()
        self.logger = logging.getLogger(__name__)
        self.environment = "development"
        self.hot_reload_enabled = False
        self.file_watchers = {}
        
        # Initialize with default configuration
        self._load_default_config()
    
    def _load_default_config(self) -> None:
        """Load default configuration"""
        default_config = {
            "system": {
                "name": "Jarvis",
                "version": "1.0.0",
                "debug": False,
                "log_level": "INFO"
            },
            "plugins": {
                "enabled": True,
                "directories": ["jarvis/plugins"],
                "auto_load": True
            },
            "llm": {
                "default_provider": "ollama",
                "timeout": 30,
                "max_retries": 3,
                "fallback_enabled": True
            },
            "database": {
                "path": "data/jarvis_archive.db",
                "backup_enabled": True,
                "backup_interval": 3600
            },
            "logging": {
                "level": "INFO",
                "format": "%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                "file": "logs/jarvis.log",
                "max_size": 10485760,  # 10MB
                "backup_count": 5
            },
            "security": {
                "encryption_enabled": False,
                "api_key_required": False,
                "rate_limiting": {
                    "enabled": False,
                    "requests_per_minute": 60
                }
            }
        }
        
        with self.lock:
            self.config = default_config
    
    def define_schema(self, schemas: List[ConfigSchema]) -> None:
        """Define configuration schema"""
        with self.lock:
            for schema in schemas:
                self.schema[schema.key] = schema
    
    def load_from_file(self, filepath: str, merge: bool = True) -> bool:
        """Load configuration from file
        
        Args:
            filepath: Path to configuration file
            merge: Whether to merge with existing config or replace
            
        Returns:
            bool: True if loaded successfully
        """
        try:
            if not os.path.exists(filepath):
                self.logger.warning(f"Configuration file does not exist: {filepath}")
                return False
            
            # Determine format from file extension
            ext = Path(filepath).suffix.lower()
            if ext == '.json':
                provider = self.providers[ConfigFormat.JSON]
            elif ext in ['.yaml', '.yml']:
                provider = self.providers[ConfigFormat.YAML]
            else:
                self.logger.error(f"Unsupported configuration file format: {ext}")
                return False
            
            loaded_config = provider.load(filepath)
            
            with self.lock:
                if merge:
                    self._deep_merge(self.config, loaded_config)
                else:
                    self.config = loaded_config
            
            self.logger.info(f"Loaded configuration from {filepath}")
            self._notify_watchers("config_loaded", filepath)
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration from {filepath}: {e}")
            return False
    
    def load_environment_config(self, environment: str = None) -> bool:
        """Load environment-specific configuration
        
        Args:
            environment: Environment name (development, staging, production)
            
        Returns:
            bool: True if loaded successfully
        """
        env = environment or self.environment
        env_config_path = os.path.join(self.config_dir, "environments", f"{env}.yaml")
        
        if os.path.exists(env_config_path):
            return self.load_from_file(env_config_path, merge=True)
        else:
            self.logger.info(f"No environment configuration found for {env}")
            return True
    
    def load_from_env(self) -> bool:
        """Load configuration from environment variables"""
        try:
            env_provider = self.providers[ConfigFormat.ENV]
            env_config = env_provider.load()
            
            with self.lock:
                self._deep_merge(self.config, env_config)
            
            self.logger.info(f"Loaded {len(env_config)} configuration values from environment")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to load configuration from environment: {e}")
            return False
    
    def save_to_file(self, filepath: str, format: ConfigFormat = ConfigFormat.YAML) -> bool:
        """Save configuration to file"""
        try:
            provider = self.providers[format]
            
            with self.lock:
                config_copy = self.config.copy()
            
            return provider.save(config_copy, filepath)
            
        except Exception as e:
            self.logger.error(f"Failed to save configuration to {filepath}: {e}")
            return False
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value
        
        Args:
            key: Configuration key (supports dot notation)
            default: Default value if key not found
            
        Returns:
            Configuration value or default
        """
        with self.lock:
            return self._get_nested_value(self.config, key, default)
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value
        
        Args:
            key: Configuration key (supports dot notation)
            value: Value to set
        """
        with self.lock:
            self._set_nested_value(self.config, key, value)
            self._notify_watchers("config_changed", key, value)
    
    def delete(self, key: str) -> bool:
        """Delete configuration key
        
        Args:
            key: Configuration key to delete
            
        Returns:
            bool: True if key was deleted
        """
        with self.lock:
            return self._delete_nested_value(self.config, key)
    
    def validate(self) -> ValidationResult:
        """Validate current configuration against schema"""
        errors = []
        warnings = []
        
        with self.lock:
            # Check required keys
            for key, schema in self.schema.items():
                if schema.required:
                    value = self._get_nested_value(self.config, key)
                    if value is None:
                        errors.append(f"Required configuration key missing: {key}")
                    else:
                        # Type validation
                        if not isinstance(value, schema.value_type):
                            errors.append(f"Invalid type for {key}: expected {schema.value_type.__name__}, got {type(value).__name__}")
            
            # Check for unknown keys if schema is restrictive
            # (This could be implemented based on requirements)
        
        return ValidationResult(valid=len(errors) == 0, errors=errors, warnings=warnings)
    
    def get_section(self, section: str) -> Dict[str, Any]:
        """Get entire configuration section"""
        with self.lock:
            return self._get_nested_value(self.config, section, {})
    
    def add_watcher(self, callback: callable) -> None:
        """Add configuration change watcher"""
        self.watchers.append(callback)
    
    def remove_watcher(self, callback: callable) -> None:
        """Remove configuration change watcher"""
        if callback in self.watchers:
            self.watchers.remove(callback)
    
    def enable_hot_reload(self, enabled: bool = True) -> None:
        """Enable/disable hot reloading of configuration files"""
        self.hot_reload_enabled = enabled
        if enabled:
            self.logger.info("Hot reload enabled for configuration files")
        else:
            self.logger.info("Hot reload disabled")
    
    def get_config_summary(self) -> Dict[str, Any]:
        """Get configuration summary"""
        with self.lock:
            total_keys = self._count_keys(self.config)
            
            return {
                "environment": self.environment,
                "total_keys": total_keys,
                "schema_defined": len(self.schema),
                "hot_reload_enabled": self.hot_reload_enabled,
                "watchers": len(self.watchers),
                "validation": self.validate().valid,
                "sections": list(self.config.keys()) if isinstance(self.config, dict) else []
            }
    
    def _deep_merge(self, target: Dict[str, Any], source: Dict[str, Any]) -> None:
        """Deep merge source into target"""
        for key, value in source.items():
            if key in target and isinstance(target[key], dict) and isinstance(value, dict):
                self._deep_merge(target[key], value)
            else:
                target[key] = value
    
    def _get_nested_value(self, config: Dict[str, Any], key: str, default: Any = None) -> Any:
        """Get nested configuration value using dot notation"""
        keys = key.split('.')
        current = config
        
        for k in keys:
            if isinstance(current, dict) and k in current:
                current = current[k]
            else:
                return default
        
        return current
    
    def _set_nested_value(self, config: Dict[str, Any], key: str, value: Any) -> None:
        """Set nested configuration value using dot notation"""
        keys = key.split('.')
        current = config
        
        for k in keys[:-1]:
            if k not in current:
                current[k] = {}
            elif not isinstance(current[k], dict):
                current[k] = {}
            current = current[k]
        
        current[keys[-1]] = value
    
    def _delete_nested_value(self, config: Dict[str, Any], key: str) -> bool:
        """Delete nested configuration value using dot notation"""
        keys = key.split('.')
        current = config
        
        for k in keys[:-1]:
            if k not in current or not isinstance(current[k], dict):
                return False
            current = current[k]
        
        if keys[-1] in current:
            del current[keys[-1]]
            return True
        
        return False
    
    def _count_keys(self, config: Any) -> int:
        """Count total number of configuration keys"""
        if isinstance(config, dict):
            return sum(1 + self._count_keys(v) for v in config.values())
        else:
            return 0
    
    def _notify_watchers(self, event_type: str, *args) -> None:
        """Notify configuration watchers of changes"""
        for watcher in self.watchers:
            try:
                watcher(event_type, *args)
            except Exception as e:
                self.logger.error(f"Error in configuration watcher: {e}")


# Global configuration manager instance
_config_manager: Optional[ConfigManager] = None


def get_config_manager() -> ConfigManager:
    """Get the global configuration manager instance"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager


def initialize_config_system(config_dir: str = None, environment: str = "development") -> ConfigManager:
    """Initialize the configuration system
    
    Args:
        config_dir: Directory containing configuration files
        environment: Environment name
        
    Returns:
        ConfigManager: Initialized configuration manager
    """
    global _config_manager
    _config_manager = ConfigManager(config_dir)
    _config_manager.environment = environment
    
    # Load environment-specific configuration
    _config_manager.load_environment_config()
    
    # Load from environment variables (highest priority)
    _config_manager.load_from_env()
    
    return _config_manager


# Convenience functions
def get_config(key: str, default: Any = None) -> Any:
    """Get configuration value (convenience function)"""
    return get_config_manager().get(key, default)


def set_config(key: str, value: Any) -> None:
    """Set configuration value (convenience function)"""
    get_config_manager().set(key, value)