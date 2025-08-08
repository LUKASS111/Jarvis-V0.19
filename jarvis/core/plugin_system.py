"""
Plugin System for Jarvis 1.0.0
Enterprise-grade plugin architecture for modular development

This module provides the foundation for a plugin-based architecture that allows
for modular development, third-party extensions, and improved maintainability.
"""

import os
import sys
import importlib
import inspect
from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional, Type, Callable
from dataclasses import dataclass, field
from enum import Enum
import logging
import json
from pathlib import Path


class PluginStatus(Enum):
    """Plugin status enumeration"""
    UNLOADED = "unloaded"
    LOADED = "loaded" 
    ACTIVE = "active"
    ERROR = "error"
    DISABLED = "disabled"


@dataclass
class PluginContext:
    """Context provided to plugins during initialization"""
    config: Dict[str, Any] = field(default_factory=dict)
    services: Dict[str, Any] = field(default_factory=dict)
    logger: Optional[logging.Logger] = None
    plugin_manager: Optional['PluginManager'] = None
    
    def get_service(self, service_name: str) -> Any:
        """Get a registered service"""
        return self.services.get(service_name)
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """Get configuration value"""
        return self.config.get(key, default)


@dataclass 
class PluginRequest:
    """Request object passed to plugin execution"""
    action: str
    data: Any = None
    context: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)


@dataclass
class PluginResponse:
    """Response object returned from plugin execution"""
    success: bool
    data: Any = None
    error: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    @classmethod
    def success_response(cls, data: Any = None, metadata: Dict[str, Any] = None) -> 'PluginResponse':
        """Create successful response"""
        return cls(success=True, data=data, metadata=metadata or {})
    
    @classmethod
    def error_response(cls, error: str, metadata: Dict[str, Any] = None) -> 'PluginResponse':
        """Create error response"""
        return cls(success=False, error=error, metadata=metadata or {})


class PluginInterface(ABC):
    """Base interface that all plugins must implement"""
    
    def __init__(self):
        self.name: str = self.__class__.__name__
        self.version: str = "1.0.0"
        self.description: str = ""
        self.author: str = ""
        self.dependencies: List[str] = []
        self.context: Optional[PluginContext] = None
        self.status: PluginStatus = PluginStatus.UNLOADED
        
    @abstractmethod
    def initialize(self, context: PluginContext) -> bool:
        """Initialize the plugin with the given context
        
        Args:
            context: Plugin context containing config, services, etc.
            
        Returns:
            bool: True if initialization successful, False otherwise
        """
        pass
    
    @abstractmethod
    def execute(self, request: PluginRequest) -> PluginResponse:
        """Execute plugin functionality
        
        Args:
            request: Plugin request containing action and data
            
        Returns:
            PluginResponse: Response from plugin execution
        """
        pass
    
    def cleanup(self) -> None:
        """Cleanup plugin resources - optional to override"""
        pass
    
    def get_supported_actions(self) -> List[str]:
        """Get list of actions this plugin supports"""
        return []
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get plugin metadata"""
        return {
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "author": self.author,
            "dependencies": self.dependencies,
            "status": self.status.value,
            "supported_actions": self.get_supported_actions()
        }


@dataclass
class PluginInfo:
    """Information about a discovered plugin"""
    name: str
    module_path: str
    class_name: str
    file_path: str
    metadata: Dict[str, Any] = field(default_factory=dict)
    instance: Optional[PluginInterface] = None
    status: PluginStatus = PluginStatus.UNLOADED
    error_message: Optional[str] = None


class PluginManager:
    """Main plugin manager responsible for discovering, loading, and managing plugins"""
    
    def __init__(self, plugin_directories: List[str] = None):
        self.logger = logging.getLogger(__name__)
        self.plugin_directories = plugin_directories or []
        self.plugins: Dict[str, PluginInfo] = {}
        self.plugin_chains: Dict[str, List[str]] = {}
        self.hooks: Dict[str, List[Callable]] = {}
        self.context = PluginContext()
        
        # Add default plugin directory
        default_plugin_dir = os.path.join(os.path.dirname(__file__), "..", "..", "plugins")
        if os.path.exists(default_plugin_dir):
            self.plugin_directories.append(default_plugin_dir)
    
    def set_context(self, context: PluginContext) -> None:
        """Set the plugin context"""
        self.context = context
        self.context.plugin_manager = self
    
    def discover_plugins(self) -> int:
        """Discover plugins in configured directories
        
        Returns:
            int: Number of plugins discovered
        """
        discovered_count = 0
        
        for directory in self.plugin_directories:
            if not os.path.exists(directory):
                self.logger.warning(f"Plugin directory does not exist: {directory}")
                continue
                
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        file_path = os.path.join(root, file)
                        plugin_info = self._discover_plugin_in_file(file_path)
                        if plugin_info:
                            self.plugins[plugin_info.name] = plugin_info
                            discovered_count += 1
                            self.logger.info(f"Discovered plugin: {plugin_info.name}")
        
        self.logger.info(f"Discovered {discovered_count} plugins total")
        return discovered_count
    
    def _discover_plugin_in_file(self, file_path: str) -> Optional[PluginInfo]:
        """Discover plugin in a specific file"""
        try:
            # Calculate module path
            relative_path = os.path.relpath(file_path)
            module_path = relative_path.replace(os.sep, '.').replace('.py', '')
            
            # Import module
            spec = importlib.util.spec_from_file_location(module_path, file_path)
            if not spec or not spec.loader:
                return None
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Find plugin classes
            for name, obj in inspect.getmembers(module):
                if (inspect.isclass(obj) and 
                    issubclass(obj, PluginInterface) and 
                    obj != PluginInterface):
                    
                    return PluginInfo(
                        name=name,
                        module_path=module_path,
                        class_name=name,
                        file_path=file_path
                    )
        
        except Exception as e:
            self.logger.error(f"Error discovering plugin in {file_path}: {e}")
            return None
        
        return None
    
    def load_plugin(self, plugin_name: str) -> bool:
        """Load a specific plugin
        
        Args:
            plugin_name: Name of the plugin to load
            
        Returns:
            bool: True if loaded successfully, False otherwise
        """
        if plugin_name not in self.plugins:
            self.logger.error(f"Plugin not found: {plugin_name}")
            return False
        
        plugin_info = self.plugins[plugin_name]
        
        try:
            # Import the module
            spec = importlib.util.spec_from_file_location(
                plugin_info.module_path, 
                plugin_info.file_path
            )
            if not spec or not spec.loader:
                raise ImportError(f"Could not load module spec for {plugin_name}")
                
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Get the plugin class
            plugin_class = getattr(module, plugin_info.class_name)
            
            # Create instance
            plugin_instance = plugin_class()
            
            # Initialize the plugin
            if plugin_instance.initialize(self.context):
                plugin_info.instance = plugin_instance
                plugin_info.status = PluginStatus.ACTIVE
                plugin_instance.status = PluginStatus.ACTIVE
                
                self.logger.info(f"Successfully loaded plugin: {plugin_name}")
                return True
            else:
                plugin_info.status = PluginStatus.ERROR
                plugin_info.error_message = "Plugin initialization failed"
                self.logger.error(f"Plugin initialization failed: {plugin_name}")
                return False
                
        except Exception as e:
            plugin_info.status = PluginStatus.ERROR
            plugin_info.error_message = str(e)
            self.logger.error(f"Error loading plugin {plugin_name}: {e}")
            return False
    
    def load_all_plugins(self) -> int:
        """Load all discovered plugins
        
        Returns:
            int: Number of plugins successfully loaded
        """
        loaded_count = 0
        
        for plugin_name in self.plugins:
            if self.load_plugin(plugin_name):
                loaded_count += 1
        
        self.logger.info(f"Loaded {loaded_count}/{len(self.plugins)} plugins")
        return loaded_count
    
    def execute_plugin(self, plugin_name: str, request: PluginRequest) -> PluginResponse:
        """Execute a specific plugin
        
        Args:
            plugin_name: Name of the plugin to execute
            request: Plugin request
            
        Returns:
            PluginResponse: Response from plugin execution
        """
        if plugin_name not in self.plugins:
            return PluginResponse.error_response(f"Plugin not found: {plugin_name}")
        
        plugin_info = self.plugins[plugin_name]
        
        if plugin_info.status != PluginStatus.ACTIVE or not plugin_info.instance:
            return PluginResponse.error_response(f"Plugin not active: {plugin_name}")
        
        try:
            return plugin_info.instance.execute(request)
        except Exception as e:
            self.logger.error(f"Error executing plugin {plugin_name}: {e}")
            return PluginResponse.error_response(f"Plugin execution error: {e}")
    
    def execute_plugin_chain(self, chain_name: str, initial_data: Any) -> List[PluginResponse]:
        """Execute a chain of plugins
        
        Args:
            chain_name: Name of the plugin chain
            initial_data: Initial data to pass to the chain
            
        Returns:
            List[PluginResponse]: Responses from each plugin in the chain
        """
        if chain_name not in self.plugin_chains:
            return [PluginResponse.error_response(f"Plugin chain not found: {chain_name}")]
        
        responses = []
        current_data = initial_data
        
        for plugin_name in self.plugin_chains[chain_name]:
            request = PluginRequest(action="execute", data=current_data)
            response = self.execute_plugin(plugin_name, request)
            responses.append(response)
            
            if not response.success:
                self.logger.warning(f"Plugin chain {chain_name} stopped at {plugin_name} due to error")
                break
                
            current_data = response.data
        
        return responses
    
    def register_plugin_chain(self, chain_name: str, plugin_names: List[str]) -> bool:
        """Register a plugin execution chain
        
        Args:
            chain_name: Name for the chain
            plugin_names: List of plugin names in execution order
            
        Returns:
            bool: True if registered successfully
        """
        # Validate all plugins exist and are loaded
        for plugin_name in plugin_names:
            if (plugin_name not in self.plugins or 
                self.plugins[plugin_name].status != PluginStatus.ACTIVE):
                self.logger.error(f"Cannot create chain {chain_name}: plugin {plugin_name} not available")
                return False
        
        self.plugin_chains[chain_name] = plugin_names
        self.logger.info(f"Registered plugin chain: {chain_name} -> {plugin_names}")
        return True
    
    def get_plugin_info(self, plugin_name: str) -> Optional[PluginInfo]:
        """Get information about a specific plugin"""
        return self.plugins.get(plugin_name)
    
    def get_all_plugins(self) -> Dict[str, PluginInfo]:
        """Get information about all plugins"""
        return self.plugins.copy()
    
    def get_active_plugins(self) -> Dict[str, PluginInfo]:
        """Get all active plugins"""
        return {
            name: info for name, info in self.plugins.items() 
            if info.status == PluginStatus.ACTIVE
        }
    
    def unload_plugin(self, plugin_name: str) -> bool:
        """Unload a specific plugin
        
        Args:
            plugin_name: Name of the plugin to unload
            
        Returns:
            bool: True if unloaded successfully
        """
        if plugin_name not in self.plugins:
            return False
        
        plugin_info = self.plugins[plugin_name]
        
        try:
            if plugin_info.instance:
                plugin_info.instance.cleanup()
                plugin_info.instance = None
            
            plugin_info.status = PluginStatus.UNLOADED
            self.logger.info(f"Unloaded plugin: {plugin_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Error unloading plugin {plugin_name}: {e}")
            return False
    
    def unload_all_plugins(self) -> int:
        """Unload all plugins
        
        Returns:
            int: Number of plugins unloaded
        """
        unloaded_count = 0
        
        for plugin_name in list(self.plugins.keys()):
            if self.unload_plugin(plugin_name):
                unloaded_count += 1
        
        return unloaded_count
    
    def register_hook(self, hook_name: str, callback: Callable) -> None:
        """Register a hook callback
        
        Args:
            hook_name: Name of the hook
            callback: Callback function to register
        """
        if hook_name not in self.hooks:
            self.hooks[hook_name] = []
        self.hooks[hook_name].append(callback)
    
    def trigger_hook(self, hook_name: str, *args, **kwargs) -> List[Any]:
        """Trigger all callbacks for a hook
        
        Args:
            hook_name: Name of the hook to trigger
            *args, **kwargs: Arguments to pass to callbacks
            
        Returns:
            List[Any]: Results from all callbacks
        """
        results = []
        
        if hook_name in self.hooks:
            for callback in self.hooks[hook_name]:
                try:
                    result = callback(*args, **kwargs)
                    results.append(result)
                except Exception as e:
                    self.logger.error(f"Error in hook {hook_name} callback: {e}")
                    results.append(None)
        
        return results
    
    def get_plugin_status_report(self) -> Dict[str, Any]:
        """Generate a comprehensive status report of all plugins"""
        total_plugins = len(self.plugins)
        active_plugins = len(self.get_active_plugins())
        error_plugins = len([p for p in self.plugins.values() if p.status == PluginStatus.ERROR])
        
        return {
            "total_plugins": total_plugins,
            "active_plugins": active_plugins,
            "error_plugins": error_plugins,
            "plugin_chains": len(self.plugin_chains),
            "hooks": len(self.hooks),
            "plugins": {
                name: {
                    "status": info.status.value,
                    "file_path": info.file_path,
                    "error_message": info.error_message,
                    "metadata": info.instance.get_metadata() if info.instance else {}
                }
                for name, info in self.plugins.items()
            }
        }


# Global plugin manager instance
_plugin_manager: Optional[PluginManager] = None


def get_plugin_manager() -> PluginManager:
    """Get the global plugin manager instance"""
    global _plugin_manager
    if _plugin_manager is None:
        _plugin_manager = PluginManager()
    return _plugin_manager


def initialize_plugin_system(plugin_directories: List[str] = None, 
                           context: PluginContext = None) -> PluginManager:
    """Initialize the plugin system
    
    Args:
        plugin_directories: List of directories to search for plugins
        context: Plugin context to use
        
    Returns:
        PluginManager: Initialized plugin manager
    """
    global _plugin_manager
    _plugin_manager = PluginManager(plugin_directories)
    
    if context:
        _plugin_manager.set_context(context)
    
    # Discover and load plugins
    _plugin_manager.discover_plugins()
    _plugin_manager.load_all_plugins()
    
    return _plugin_manager