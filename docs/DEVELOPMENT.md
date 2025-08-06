# Development Guide

## Getting Started

### Development Environment Setup

1. **Clone and Setup**
   ```bash
   git clone https://github.com/LUKASS111/Jarvis-V0.19.git
   cd Jarvis-V0.19
   pip install -r requirements.txt
   ```

2. **Development Dependencies**
   ```bash
   pip install pytest pytest-cov black flake8 mypy
   ```

3. **Pre-commit Hooks** (Optional)
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Code Standards

### Python Style Guide
- Follow PEP 8 standards
- Use type hints where possible
- Maximum line length: 88 characters (Black standard)
- Use descriptive variable names

### Code Quality Tools
```bash
# Format code
black jarvis/

# Check style
flake8 jarvis/

# Type checking
mypy jarvis/

# Security scanning
bandit -r jarvis/
```

## Testing Framework

### Running Tests
```bash
# Run all tests
python run_tests.py

# Run specific test file
python -m pytest tests/test_crdt_implementation.py

# Run with coverage
python -m pytest --cov=jarvis tests/

# Run performance tests
python tests/test_crdt_phase5.py
```

### Test Categories
- **Unit Tests**: Individual component testing
- **Integration Tests**: Multi-component testing
- **Performance Tests**: Benchmarking and optimization
- **Security Tests**: Vulnerability testing

### Writing Tests
```python
import unittest
from jarvis.core import get_crdt_manager

class TestNewFeature(unittest.TestCase):
    def setUp(self):
        """Set up test fixtures"""
        self.crdt_manager = get_crdt_manager()
        
    def test_feature_functionality(self):
        """Test specific functionality"""
        # Test implementation
        result = self.crdt_manager.some_operation()
        self.assertTrue(result.success)
        
    def tearDown(self):
        """Clean up test environment"""
        # Cleanup code
        pass
```

## Development Workflow

### Branch Strategy
```bash
# Create feature branch
git checkout -b feature/new-feature

# Make changes and commit
git add .
git commit -m "feat: add new feature"

# Push and create PR
git push origin feature/new-feature
```

### Commit Message Format
```
feat: add new feature
fix: resolve bug in component
docs: update API documentation
test: add unit tests for feature
refactor: improve code structure
```

## Adding New Features

### 1. Plugin Development
```python
# Create new plugin
from jarvis.plugins.base import FileProcessorPlugin

class CustomProcessor(FileProcessorPlugin):
    def __init__(self):
        super().__init__("custom", [".custom"], "Custom processor")
    
    def process(self, file_path, output_type="memory"):
        # Implementation
        return {"content": "processed"}

# Register plugin
from jarvis.core.plugin_system import get_plugin_manager
plugin_manager = get_plugin_manager()
plugin_manager.register_plugin(CustomProcessor())
```

### 2. LLM Provider Integration
```python
# Create new LLM provider
from jarvis.core.llm.providers.base import LLMProvider

class CustomProvider(LLMProvider):
    def __init__(self, config):
        super().__init__("custom", config)
    
    def chat_completion(self, request):
        # Implementation
        return response

# Register provider
from jarvis.core.llm import get_llm_router
router = get_llm_router()
router.register_provider(CustomProvider(config))
```

### 3. CRDT Extensions
```python
# Create new CRDT type
from jarvis.core.crdt.crdt_base import CRDTBase

class CustomCRDT(CRDTBase):
    def __init__(self, crdt_id, node_id):
        super().__init__(crdt_id, node_id)
    
    def custom_operation(self, value):
        # Implementation with CRDT guarantees
        pass
```

## Configuration Management

### Environment Configuration
```yaml
# config/environments/development.yaml
system:
  debug: true
  log_level: DEBUG

llm:
  default_provider: ollama
  providers:
    ollama:
      host: localhost:11434

database:
  connection_pool_size: 5
```

### Loading Configuration
```python
from jarvis.core.config import get_config_manager

config = get_config_manager()
config.load_environment_config("development")
debug_mode = config.get("system.debug", False)
```

## Error Handling

### Custom Exceptions
```python
from jarvis.core.errors import JarvisException

class CustomFeatureException(JarvisException):
    def __init__(self, message, error_code):
        super().__init__(message)
        self.error_code = error_code
```

### Error Handling Pattern
```python
from jarvis.core.errors import handle_error

try:
    result = risky_operation()
except Exception as e:
    error_report = handle_error(e, 
        context={"operation": "custom_feature"},
        auto_recovery=True
    )
    # Handle error appropriately
```

## Performance Optimization

### Profiling
```python
import cProfile
import pstats

# Profile code
cProfile.run('your_function()', 'profile_stats')
stats = pstats.Stats('profile_stats')
stats.sort_stats('cumulative').print_stats(10)
```

### CRDT Performance
```python
# Optimize CRDT operations
from jarvis.core.crdt.crdt_performance_optimizer import optimize_sync

# Use delta compression
crdt_manager.enable_delta_compression()

# Batch operations
with crdt_manager.batch_operations():
    counter.increment(1)
    counter.increment(2)
    # Operations are batched and sent together
```

## Documentation

### API Documentation
```python
def new_function(param1: str, param2: int = 0) -> dict:
    """
    Brief description of the function.
    
    Args:
        param1: Description of parameter 1
        param2: Description of parameter 2 (default: 0)
    
    Returns:
        dict: Description of return value
    
    Raises:
        CustomException: When specific error occurs
    
    Example:
        >>> result = new_function("test", 42)
        >>> print(result["status"])
        "success"
    """
    # Implementation
    return {"status": "success"}
```

### README Updates
When adding major features, update:
- Main README.md (keep it concise)
- Relevant documentation in docs/
- CHANGELOG.md

## Debugging

### Development Mode
```bash
# Enable debug mode
export JARVIS_DEBUG=true
python main.py --cli
```

### Logging
```python
from jarvis.core.logger import get_logger

logger = get_logger(__name__)
logger.debug("Debug information")
logger.info("General information")
logger.warning("Warning message")
logger.error("Error occurred")
```

### CRDT Debugging
```python
# Check CRDT state
crdt_manager = get_crdt_manager()
status = crdt_manager.get_debug_status()
print(f"Active CRDTs: {status.active_count}")
print(f"Sync status: {status.sync_health}")
```

## Contributing Guidelines

1. **Follow code standards** (PEP 8, type hints)
2. **Write comprehensive tests** (aim for 90%+ coverage)
3. **Update documentation** for new features
4. **Test across environments** (Windows, macOS, Linux)
5. **Keep commits atomic** and well-described
6. **Submit PRs** with clear descriptions

## Release Process

1. **Update version numbers** in relevant files
2. **Update CHANGELOG.md** with new features/fixes
3. **Run full test suite** and ensure 100% pass rate
4. **Update documentation** as needed
5. **Create release tag** and push to repository