# Plugin System Development Guide

## Overview

The Jarvis v0.2 Plugin System provides a modular architecture for extending functionality through discoverable, loadable plugins with comprehensive sandboxing and security isolation. This guide covers plugin development, API specifications, integration examples, and security best practices.

---

## Plugin Architecture

### System Components

```
Plugin System Architecture
├── PluginManager - Central plugin coordination and lifecycle management
├── PluginDiscovery - Automatic plugin discovery and validation
├── PluginLoader - Secure plugin loading and sandboxing
├── PluginRegistry - Plugin metadata and dependency management
├── PluginSandbox - Security isolation and resource limitation
└── PluginAPI - Standardized plugin interface definitions
```

### Core Classes

#### PluginManager
Central coordination system for all plugin operations.

```python
from jarvis.core.plugin_system import PluginManager

# Initialize plugin manager
plugin_manager = PluginManager()

# Plugin lifecycle operations
plugin_manager.discover_plugins()           # Find available plugins
plugin_manager.load_all_plugins()           # Load discovered plugins
plugin_manager.execute_plugin(name, request) # Execute plugin operation
plugin_manager.unload_plugin(name)          # Unload specific plugin
```

#### Plugin Base Classes

**FileProcessorPlugin** - For file processing extensions:
```python
from jarvis.plugins.base import FileProcessorPlugin

class CustomFileProcessor(FileProcessorPlugin):
    """Custom file processor implementation"""
    
    def get_supported_extensions(self) -> List[str]:
        return ['.custom', '.myformat']
        
    def get_plugin_info(self) -> dict:
        return {
            "name": "Custom Format Processor",
            "version": "1.0.0",
            "description": "Processes custom file formats",
            "author": "Your Name"
        }
        
    def process_file(self, file_path: str, output_format: str) -> dict:
        """Process file and return formatted output"""
        # Implementation here
        pass
```

**LLMProviderPlugin** - For LLM provider extensions:
```python
from jarvis.plugins.base import LLMProviderPlugin

class CustomLLMProvider(LLMProviderPlugin):
    """Custom LLM provider implementation"""
    
    def get_supported_models(self) -> List[str]:
        return ["custom-model-7b", "custom-model-13b"]
        
    def supports_capability(self, capability: str) -> bool:
        return capability in ["chat", "completion", "embedding"]
        
    def chat_completion(self, request: CompletionRequest) -> CompletionResponse:
        """Implement chat completion functionality"""
        # Implementation here
        pass
```

---

## Plugin Development

### Step-by-Step Plugin Creation

#### 1. Plugin Structure Setup

Create plugin directory structure:
```
my_custom_plugin/
├── __init__.py                 # Plugin entry point
├── plugin.py                   # Main plugin implementation  
├── manifest.json               # Plugin metadata and dependencies
├── requirements.txt            # Python dependencies
├── config/                     # Plugin configuration files
│   └── default.yaml
├── tests/                      # Plugin tests
│   └── test_plugin.py
└── docs/                       # Plugin documentation
    └── README.md
```

#### 2. Plugin Manifest Definition

**manifest.json** - Essential plugin metadata:
```json
{
    "name": "my_custom_plugin",
    "version": "1.0.0",
    "description": "Description of plugin functionality",
    "author": "Your Name <email@example.com>",
    "license": "MIT",
    "jarvis_version": ">=0.2.0",
    "plugin_type": "file_processor",
    "entry_point": "plugin:MyCustomPlugin",
    "dependencies": {
        "python_packages": ["numpy", "pandas"],
        "system_packages": ["libxml2-dev"],
        "jarvis_plugins": ["base_processor"]
    },
    "permissions": {
        "file_access": ["read", "write"],
        "network_access": false,
        "system_commands": false
    },
    "configuration": {
        "schema": "config/schema.yaml",
        "defaults": "config/default.yaml"
    },
    "api_version": "1.0"
}
```

#### 3. Plugin Implementation

**plugin.py** - Main plugin logic:
```python
import os
import json
from typing import Dict, Any, List
from jarvis.plugins.base import FileProcessorPlugin
from jarvis.core.errors import FileProcessingException

class MyCustomPlugin(FileProcessorPlugin):
    """Custom file format processor with advanced features"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.supported_extensions = ['.custom', '.myformat']
        self.version = "1.0.0"
        
    def get_supported_extensions(self) -> List[str]:
        """Return list of supported file extensions"""
        return self.supported_extensions
        
    def get_plugin_info(self) -> Dict[str, Any]:
        """Return comprehensive plugin information"""
        return {
            "name": "Custom Format Processor",
            "version": self.version,
            "description": "Advanced processor for custom file formats",
            "author": "Your Name",
            "capabilities": [
                "text_extraction",
                "metadata_analysis", 
                "format_conversion",
                "batch_processing"
            ],
            "configuration_options": [
                "processing_mode",
                "output_format",
                "validation_level"
            ]
        }
        
    def validate_file(self, file_path: str) -> bool:
        """Validate file format and accessibility"""
        try:
            if not os.path.exists(file_path):
                return False
                
            # Check file extension
            _, ext = os.path.splitext(file_path)
            if ext.lower() not in self.supported_extensions:
                return False
                
            # Validate file format (custom logic)
            return self._validate_custom_format(file_path)
            
        except Exception as e:
            self.logger.error(f"File validation failed: {e}")
            return False
            
    def process_file(self, file_path: str, output_format: str) -> Dict[str, Any]:
        """
        Process file and return formatted output
        
        Args:
            file_path: Path to file to process
            output_format: Desired output format ('memory', 'logs', 'agent')
            
        Returns:
            Dict containing processed data and metadata
        """
        try:
            # Validate input
            if not self.validate_file(file_path):
                raise FileProcessingException(f"Invalid file: {file_path}")
                
            # Extract file content
            content = self._extract_content(file_path)
            
            # Process based on output format
            if output_format == "memory":
                return self._format_for_memory(content, file_path)
            elif output_format == "logs":
                return self._format_for_logs(content, file_path)
            elif output_format == "agent":
                return self._format_for_agent(content, file_path)
            else:
                raise FileProcessingException(f"Unsupported output format: {output_format}")
                
        except Exception as e:
            self.logger.error(f"File processing failed: {e}")
            raise FileProcessingException(f"Processing failed: {str(e)}")
            
    def _extract_content(self, file_path: str) -> Dict[str, Any]:
        """Extract content from custom file format"""
        # Custom extraction logic here
        with open(file_path, 'r', encoding='utf-8') as f:
            raw_content = f.read()
            
        # Parse custom format
        parsed_content = {
            "text": self._extract_text(raw_content),
            "metadata": self._extract_metadata(raw_content),
            "structure": self._analyze_structure(raw_content)
        }
        
        return parsed_content
        
    def _format_for_memory(self, content: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """Format content for memory storage"""
        return {
            "type": "file_content",
            "source": file_path,
            "content": content["text"],
            "metadata": {
                **content["metadata"],
                "processed_by": "my_custom_plugin",
                "processed_at": time.time(),
                "structure_info": content["structure"]
            },
            "tags": ["custom_format", "processed"],
            "searchable": True
        }
        
    def _format_for_agent(self, content: Dict[str, Any], file_path: str) -> Dict[str, Any]:
        """Format content for agent processing"""
        return {
            "summary": f"Processed custom format file: {os.path.basename(file_path)}",
            "content": content["text"],
            "key_points": self._extract_key_points(content),
            "recommendations": self._generate_recommendations(content),
            "metadata": content["metadata"],
            "confidence_score": self._calculate_confidence(content)
        }
```

#### 4. Plugin Configuration

**config/default.yaml** - Default configuration:
```yaml
processing:
  mode: "standard"
  validation_level: "strict"
  batch_size: 100
  
output:
  format: "json"
  include_metadata: true
  compress_output: false
  
performance:
  max_file_size_mb: 50
  timeout_seconds: 30
  parallel_processing: true
  
logging:
  level: "INFO"
  include_debug: false
```

#### 5. Plugin Testing

**tests/test_plugin.py** - Comprehensive testing:
```python
import unittest
import tempfile
import os
from jarvis.plugins.my_custom_plugin import MyCustomPlugin

class TestMyCustomPlugin(unittest.TestCase):
    
    def setUp(self):
        self.plugin = MyCustomPlugin()
        
    def test_supported_extensions(self):
        """Test supported file extensions"""
        extensions = self.plugin.get_supported_extensions()
        self.assertIn('.custom', extensions)
        self.assertIn('.myformat', extensions)
        
    def test_file_validation(self):
        """Test file validation functionality"""
        # Create temporary test file
        with tempfile.NamedTemporaryFile(suffix='.custom', delete=False) as tmp:
            tmp.write(b'test content')
            tmp_path = tmp.name
            
        try:
            # Valid file should pass validation
            self.assertTrue(self.plugin.validate_file(tmp_path))
            
            # Non-existent file should fail
            self.assertFalse(self.plugin.validate_file('nonexistent.custom'))
            
        finally:
            os.unlink(tmp_path)
            
    def test_content_processing(self):
        """Test content processing for different output formats"""
        # Create test file
        with tempfile.NamedTemporaryFile(suffix='.custom', mode='w', delete=False) as tmp:
            tmp.write('sample custom format content')
            tmp_path = tmp.name
            
        try:
            # Test memory format
            memory_result = self.plugin.process_file(tmp_path, 'memory')
            self.assertIn('type', memory_result)
            self.assertEqual(memory_result['type'], 'file_content')
            
            # Test agent format  
            agent_result = self.plugin.process_file(tmp_path, 'agent')
            self.assertIn('summary', agent_result)
            self.assertIn('confidence_score', agent_result)
            
        finally:
            os.unlink(tmp_path)
            
    def test_error_handling(self):
        """Test error handling for invalid inputs"""
        from jarvis.core.errors import FileProcessingException
        
        # Invalid file should raise exception
        with self.assertRaises(FileProcessingException):
            self.plugin.process_file('nonexistent.txt', 'memory')
            
        # Invalid output format should raise exception
        with tempfile.NamedTemporaryFile(suffix='.custom') as tmp:
            with self.assertRaises(FileProcessingException):
                self.plugin.process_file(tmp.name, 'invalid_format')

if __name__ == '__main__':
    unittest.main()
```

---

## Plugin Integration Examples

### Plugin Registration and Loading

```python
from jarvis.core.plugin_system import get_plugin_manager

# Get plugin manager instance
plugin_manager = get_plugin_manager()

# Automatic plugin discovery
discovered_plugins = plugin_manager.discover_plugins()
print(f"Discovered {len(discovered_plugins)} plugins")

# Load specific plugin
plugin_manager.load_plugin("my_custom_plugin")

# Load all discovered plugins
plugin_manager.load_all_plugins()

# List loaded plugins
loaded_plugins = plugin_manager.list_loaded_plugins()
for plugin_name, plugin_info in loaded_plugins.items():
    print(f"Loaded: {plugin_name} v{plugin_info['version']}")
```

### Plugin Execution

```python
# Execute file processor plugin
file_path = "documents/sample.custom"
result = plugin_manager.execute_plugin(
    plugin_name="my_custom_plugin",
    operation="process_file",
    parameters={
        "file_path": file_path,
        "output_format": "agent"
    }
)

print(f"Processing result: {result}")

# Execute with custom configuration
custom_config = {
    "processing_mode": "detailed",
    "include_metadata": True
}

result = plugin_manager.execute_plugin(
    plugin_name="my_custom_plugin",
    operation="process_file",
    parameters={
        "file_path": file_path,
        "output_format": "memory"
    },
    config=custom_config
)
```

### Plugin Hooks and Events

```python
from jarvis.core.plugin_system import PluginHooks

# Register plugin hooks for event handling
plugin_hooks = PluginHooks()

# Pre-processing hook
@plugin_hooks.register("before_file_processing")
def before_processing(file_path: str, plugin_name: str):
    print(f"Starting to process {file_path} with {plugin_name}")
    # Custom pre-processing logic

# Post-processing hook
@plugin_hooks.register("after_file_processing") 
def after_processing(result: dict, plugin_name: str):
    print(f"Completed processing with {plugin_name}")
    # Custom post-processing logic
    
# Error handling hook
@plugin_hooks.register("processing_error")
def handle_error(error: Exception, context: dict):
    print(f"Processing error: {error}")
    # Custom error handling logic
```

---

## Plugin Sandboxing and Security

### Security Isolation

#### Resource Limitations
```python
from jarvis.core.plugin_system import PluginSandbox

class SecurePluginExecution:
    """Secure plugin execution with comprehensive sandboxing"""
    
    def __init__(self):
        self.sandbox = PluginSandbox()
        
    def execute_plugin_securely(self, plugin_name: str, operation: str, 
                               parameters: dict) -> dict:
        """Execute plugin with security isolation"""
        
        # Configure sandbox limitations
        sandbox_config = {
            "memory_limit_mb": 512,      # Maximum memory usage
            "cpu_time_limit_sec": 30,    # Maximum CPU time
            "file_access": {
                "read_only": True,       # File system access
                "allowed_paths": ["/tmp", "/data/uploads"]
            },
            "network_access": False,     # Disable network access
            "system_commands": False     # Disable system command execution
        }
        
        # Create sandboxed environment
        with self.sandbox.create_environment(sandbox_config) as env:
            # Execute plugin in isolated environment
            result = env.execute_plugin(plugin_name, operation, parameters)
            
            # Validate output before returning
            validated_result = self._validate_plugin_output(result)
            
        return validated_result
        
    def _validate_plugin_output(self, result: dict) -> dict:
        """Validate plugin output for security compliance"""
        
        # Check for sensitive data exposure
        if self._contains_sensitive_data(result):
            raise SecurityException("Plugin output contains sensitive data")
            
        # Sanitize output
        sanitized_result = self._sanitize_output(result)
        
        return sanitized_result
```

#### Permission Management
```python
from jarvis.core.security import PluginPermissionManager

class PluginPermissions:
    """Comprehensive plugin permission management"""
    
    def __init__(self):
        self.permission_manager = PluginPermissionManager()
        
    def configure_plugin_permissions(self, plugin_name: str) -> dict:
        """Configure permissions for specific plugin"""
        
        # Load plugin manifest
        manifest = self.permission_manager.load_plugin_manifest(plugin_name)
        
        # Validate requested permissions
        requested_permissions = manifest.get("permissions", {})
        validated_permissions = self._validate_permissions(requested_permissions)
        
        # Apply permission policy
        effective_permissions = self._apply_permission_policy(
            plugin_name, validated_permissions
        )
        
        # Store permissions in secure registry
        self.permission_manager.store_plugin_permissions(
            plugin_name, effective_permissions
        )
        
        return effective_permissions
        
    def _validate_permissions(self, requested: dict) -> dict:
        """Validate requested permissions against security policy"""
        
        # Check against maximum allowed permissions
        max_permissions = {
            "file_access": ["read"],  # Default: read-only
            "network_access": False,  # Default: no network
            "system_commands": False  # Default: no system access
        }
        
        validated = {}
        for permission, value in requested.items():
            if permission in max_permissions:
                max_value = max_permissions[permission]
                if isinstance(max_value, list):
                    # List-based permissions (e.g., file_access)
                    validated[permission] = [
                        v for v in value if v in max_value
                    ]
                else:
                    # Boolean permissions
                    validated[permission] = value and max_value
            else:
                # Unknown permission - deny by default
                validated[permission] = False
                
        return validated
```

### Plugin Validation

#### Code Analysis
```python
from jarvis.core.security import PluginValidator

class PluginSecurityValidator:
    """Security validation for plugin code and dependencies"""
    
    def __init__(self):
        self.validator = PluginValidator()
        
    def validate_plugin_security(self, plugin_path: str) -> dict:
        """Comprehensive security validation"""
        
        validation_results = {
            "code_analysis": self._analyze_plugin_code(plugin_path),
            "dependency_check": self._check_dependencies(plugin_path),
            "manifest_validation": self._validate_manifest(plugin_path),
            "signature_verification": self._verify_plugin_signature(plugin_path)
        }
        
        # Overall security assessment
        security_score = self._calculate_security_score(validation_results)
        validation_results["security_score"] = security_score
        validation_results["approved"] = security_score >= 80
        
        return validation_results
        
    def _analyze_plugin_code(self, plugin_path: str) -> dict:
        """Static code analysis for security issues"""
        
        # Check for dangerous imports
        dangerous_imports = [
            "os.system", "subprocess", "eval", "exec",
            "pickle", "__import__", "compile"
        ]
        
        code_issues = []
        
        # Scan plugin files
        for root, dirs, files in os.walk(plugin_path):
            for file in files:
                if file.endswith('.py'):
                    file_path = os.path.join(root, file)
                    with open(file_path, 'r') as f:
                        content = f.read()
                        
                    # Check for dangerous patterns
                    for dangerous in dangerous_imports:
                        if dangerous in content:
                            code_issues.append({
                                "file": file_path,
                                "issue": f"Dangerous import/function: {dangerous}",
                                "severity": "high"
                            })
                            
        return {
            "issues_found": len(code_issues),
            "issues": code_issues,
            "status": "safe" if len(code_issues) == 0 else "unsafe"
        }
```

---

## Plugin Performance Optimization

### Caching and Optimization

```python
from jarvis.core.plugin_system import PluginCache

class OptimizedPluginExecution:
    """Performance-optimized plugin execution with caching"""
    
    def __init__(self):
        self.cache = PluginCache()
        self.performance_monitor = PluginPerformanceMonitor()
        
    def execute_with_caching(self, plugin_name: str, operation: str,
                           parameters: dict) -> dict:
        """Execute plugin with intelligent caching"""
        
        # Generate cache key
        cache_key = self._generate_cache_key(plugin_name, operation, parameters)
        
        # Check cache first
        cached_result = self.cache.get(cache_key)
        if cached_result and self._is_cache_valid(cached_result):
            self.performance_monitor.record_cache_hit(plugin_name)
            return cached_result["result"]
            
        # Execute plugin
        start_time = time.time()
        result = self._execute_plugin(plugin_name, operation, parameters)
        execution_time = time.time() - start_time
        
        # Cache result if appropriate
        if self._should_cache_result(result, execution_time):
            self.cache.set(cache_key, {
                "result": result,
                "timestamp": time.time(),
                "execution_time": execution_time
            })
            
        # Record performance metrics
        self.performance_monitor.record_execution(
            plugin_name, operation, execution_time
        )
        
        return result
        
    def _should_cache_result(self, result: dict, execution_time: float) -> bool:
        """Determine if result should be cached"""
        
        # Cache results that took significant time to compute
        if execution_time > 1.0:
            return True
            
        # Cache large results to avoid recomputation
        if len(str(result)) > 10000:
            return True
            
        # Don't cache error results
        if "error" in result:
            return False
            
        return False
```

### Performance Monitoring

```python
from jarvis.core.monitoring import PluginMetricsCollector

class PluginPerformanceAnalyzer:
    """Comprehensive plugin performance analysis"""
    
    def __init__(self):
        self.metrics_collector = PluginMetricsCollector()
        
    def analyze_plugin_performance(self, time_range: dict) -> dict:
        """Generate performance analysis report"""
        
        metrics = self.metrics_collector.get_metrics(time_range)
        
        analysis = {
            "execution_times": self._analyze_execution_times(metrics),
            "memory_usage": self._analyze_memory_usage(metrics),
            "error_rates": self._analyze_error_rates(metrics),
            "cache_efficiency": self._analyze_cache_performance(metrics),
            "recommendations": self._generate_performance_recommendations(metrics)
        }
        
        return analysis
        
    def _generate_performance_recommendations(self, metrics: dict) -> List[str]:
        """Generate performance optimization recommendations"""
        
        recommendations = []
        
        # Check execution times
        avg_execution_time = metrics["avg_execution_time"]
        if avg_execution_time > 5.0:
            recommendations.append(
                "Consider optimizing plugin algorithms - average execution time is high"
            )
            
        # Check memory usage
        max_memory_mb = metrics["max_memory_usage"] / 1024 / 1024
        if max_memory_mb > 100:
            recommendations.append(
                "Plugin memory usage is high - consider implementing streaming processing"
            )
            
        # Check error rates
        error_rate = metrics["error_rate"]
        if error_rate > 0.05:
            recommendations.append(
                "Plugin error rate is above 5% - review error handling and input validation"
            )
            
        # Check cache efficiency
        cache_hit_rate = metrics["cache_hit_rate"]
        if cache_hit_rate < 0.3:
            recommendations.append(
                "Cache hit rate is low - review caching strategy and cache key generation"
            )
            
        return recommendations
```

---

## Plugin Distribution and Deployment

### Plugin Registry

```python
from jarvis.core.plugin_system import PluginRegistry

class PluginDistribution:
    """Plugin distribution and registry management"""
    
    def __init__(self):
        self.registry = PluginRegistry()
        
    def publish_plugin(self, plugin_path: str, registry_url: str = None) -> dict:
        """Publish plugin to registry"""
        
        # Validate plugin before publishing
        validation_result = self._validate_plugin_for_publishing(plugin_path)
        if not validation_result["valid"]:
            raise PluginValidationError(validation_result["errors"])
            
        # Package plugin
        package_info = self._package_plugin(plugin_path)
        
        # Upload to registry
        upload_result = self.registry.upload_plugin(
            package_info["package_path"],
            registry_url or self.registry.default_registry_url
        )
        
        return {
            "plugin_id": upload_result["plugin_id"],
            "version": package_info["version"],
            "registry_url": upload_result["registry_url"],
            "download_url": upload_result["download_url"]
        }
        
    def install_plugin(self, plugin_id: str, version: str = "latest") -> dict:
        """Install plugin from registry"""
        
        # Download plugin package
        download_info = self.registry.download_plugin(plugin_id, version)
        
        # Verify plugin integrity
        if not self._verify_plugin_package(download_info["package_path"]):
            raise PluginIntegrityError("Plugin package integrity verification failed")
            
        # Install plugin
        installation_result = self._install_plugin_package(
            download_info["package_path"]
        )
        
        return installation_result
```

This comprehensive plugin system documentation provides complete guidance for developing, testing, deploying, and securing plugins within the Jarvis v0.2 ecosystem.