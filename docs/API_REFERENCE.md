# API Reference

## Core APIs

### Data Archiving
```python
from jarvis.core import archive_input, archive_output, get_archive_stats

# Archive data
archive_id = archive_input(content="input", source="main", operation="query")
archive_output(content="output", source="llm", operation="response")

# Get statistics
stats = get_archive_stats()
```

### Memory System
```python
from jarvis.memory.production_memory import get_production_memory

memory = get_production_memory()
memory.store_memory("Python", "Programming language", category="technical")
results = memory.search_memories("programming", category="technical")
```

### LLM Integration
```python
from jarvis.llm.production_llm import get_production_llm
from jarvis.core.llm import CompletionRequest, Message

llm = get_production_llm()
request = CompletionRequest(
    messages=[Message(role="user", content="Hello")],
    model="llama3:8b"
)
response = llm.process_request(request)
```

### CRDT Operations
```python
from jarvis.core import get_crdt_manager

crdt_manager = get_crdt_manager()

# Counter operations
counter = crdt_manager.get_counter("metrics")
counter.increment(100)
print(f"Total: {counter.value()}")

# Set operations
audit_set = crdt_manager.get_set("audit_log")
audit_set.add("operation_12345")
```

## Backend Service API

### Unified Backend
```python
from jarvis.backend import get_jarvis_backend

backend = get_jarvis_backend()
session_id = backend.create_session("cli", metadata={"interface": "production_cli"})
response = backend.process_request(session_id, "chat", {"message": "Hello"})
```

### File Processing
```python
from jarvis.utils.file_processors import process_file, is_file_supported

if is_file_supported("document.txt"):
    memory_data = process_file("document.txt", "memory")
    agent_report = process_file("document.txt", "agent")
```

## REST API Endpoints

### Authentication
```http
POST /api/auth/login
Content-Type: application/json

{
  "username": "user",
  "password": "pass"
}
```

### Chat Operations
```http
POST /api/chat/message
Content-Type: application/json
Authorization: Bearer <token>

{
  "message": "Hello, Jarvis",
  "session_id": "session_123"
}
```

### Memory Operations
```http
GET /api/memory/search?query=programming&category=technical
Authorization: Bearer <token>

POST /api/memory/store
Content-Type: application/json
Authorization: Bearer <token>

{
  "content": "Python is a programming language",
  "category": "technical",
  "tags": ["programming", "python"]
}
```

## Error Handling

### Standard Error Response
```python
from jarvis.core.errors import handle_error, JarvisException

try:
    result = risky_operation()
except JarvisException as e:
    error_report = handle_error(e, context={"operation": "example"})
    print(f"Error: {error_report.message}")
```

### Error Types
- `JarvisException` - Base exception
- `CRDTException` - CRDT-related errors
- `PluginException` - Plugin system errors
- `LLMProviderException` - LLM provider errors

## Plugin Development

### Creating a Plugin
```python
from jarvis.plugins.base import FileProcessorPlugin

class CustomProcessor(FileProcessorPlugin):
    def __init__(self):
        super().__init__("custom", [".custom"], "Custom file processor")
    
    def process(self, file_path, output_type="memory"):
        # Implementation
        return {"content": "processed", "metadata": {}}
```

### Plugin Registration
```python
from jarvis.core.plugin_system import get_plugin_manager

plugin_manager = get_plugin_manager()
plugin_manager.register_plugin(CustomProcessor())
```

## Configuration API

### Environment Configuration
```python
from jarvis.core.config import get_config_manager

config = get_config_manager()
config.load_environment_config("production")
debug_mode = config.get("system.debug", False)
```

## Monitoring API

### System Health
```python
from jarvis.core.performance_monitor import get_performance_monitor

monitor = get_performance_monitor()
health_score = monitor.get_health_score()
metrics = monitor.get_system_metrics()
```