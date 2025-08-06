# Enhanced Usage Examples and API Documentation

## Complete API Reference with Usage Examples

This document provides comprehensive usage examples for all key Jarvis V0.19 functionalities with complete parameter documentation, return types, and exception handling.

---

## 1. Core System Initialization

### JarvisAgent - Main Entry Point
```python
from jarvis.core.main import JarvisAgent

# Initialize the main agent
agent = JarvisAgent()
success = agent.initialize()

if success:
    print("✅ Jarvis Agent initialized successfully")
    
    # Get system capabilities overview
    capabilities = agent.get_capabilities()
    print(f"Available capabilities: {list(capabilities.keys())}")
    
    # Process user input through complete pipeline
    result = agent.process_input("Hello, how are you?")
    print(f"Response: {result['response']}")
else:
    print("❌ Failed to initialize Jarvis Agent")
```

**Parameters:**
- `JarvisAgent.__init__()`: No parameters required
- `initialize()`: Returns `bool` - True if successful, False otherwise
- `process_input(user_input: str)`: Returns `Dict[str, Any]` with processing result

**Exceptions:**
- `ImportError`: If core modules cannot be loaded
- `DatabaseError`: If archive system initialization fails
- `CRDTError`: If CRDT system cannot initialize

---

## 2. Backend Service Integration

### Unified Backend Service
```python
from jarvis.backend import get_jarvis_backend, shutdown_jarvis_backend

# Get backend service instance (singleton pattern)
backend = get_jarvis_backend()

# Create a new session
session_id = backend.create_session(
    session_type="api_client",
    metadata={
        "client_type": "custom_application",
        "version": "1.0.0",
        "user_id": "user123"
    }
)
print(f"Session created: {session_id}")

# Process requests through the backend
response = backend.process_request(session_id, "chat", {
    "message": "Explain quantum computing",
    "model": "llama3:8b",
    "temperature": 0.7,
    "max_tokens": 1500
})

if response["success"]:
    chat_response = response["data"]["chat_response"]
    print(f"AI Response: {chat_response['response']}")
    print(f"Model used: {chat_response['model']}")
    print(f"Processing time: {chat_response['processing_time']:.2f}s")
else:
    print(f"Error: {response['error']}")

# Get conversation history
history = backend.get_conversation_history(session_id, limit=10)
for entry in history:
    print(f"[{entry['timestamp']}] {entry['role']}: {entry['content'][:100]}...")

# Clean shutdown
shutdown_jarvis_backend()
```

**Session Management:**
- `create_session(session_type: str, metadata: Dict = None)`: Returns session ID string
- `process_request(session_id: str, request_type: str, data: Dict)`: Returns response dict
- `get_conversation_history(session_id: str, limit: int = 50)`: Returns list of conversation entries
- `get_session_info(session_id: str)`: Returns session metadata and status

**Request Types:**
- `"chat"`: LLM conversation with specified model and parameters
- `"memory"`: Memory storage, search, and recall operations  
- `"file"`: File processing with content extraction
- `"status"`: System health and performance monitoring

---

## 3. Data Archiving and Verification

### Data Archiver with CRDT Integration
```python
from jarvis.core.data_archiver import get_archiver

# Get archiver instance
archiver = get_archiver()

# Archive input data with automatic content hashing
archive_id = archiver.archive_input(
    content="Python is a programming language",
    source="user_input", 
    operation="educational_query",
    metadata={
        "category": "programming",
        "difficulty": "beginner",
        "tags": ["python", "programming", "language"]
    }
)
print(f"Archived with ID: {archive_id}")

# Archive output with verification tracking
output_id = archiver.archive_output(
    content="Python is a high-level programming language known for readability",
    source="llm_response",
    operation="educational_response", 
    confidence_score=0.95,
    metadata={
        "verified": True,
        "model": "llama3:8b",
        "processing_time": 1.23
    }
)

# Get archive statistics
stats = archiver.get_archive_stats()
print(f"Total entries: {stats['total_entries']}")
print(f"Verified entries: {stats['verified_entries']}")
print(f"Database size: {stats['db_size_mb']:.2f} MB")

# Search archived content
search_results = archiver.search_archive(
    query="programming language",
    limit=10,
    include_verified_only=True
)
for result in search_results:
    print(f"[{result['created_at']}] {result['content'][:100]}...")
```

**Key Methods:**
- `archive_input(content, source, operation, metadata=None)`: Returns archive ID
- `archive_output(content, source, operation, confidence_score=None, metadata=None)`: Returns archive ID  
- `search_archive(query, limit=50, include_verified_only=False)`: Returns list of matching entries
- `get_archive_stats()`: Returns statistics dict with counts and sizes

**CRDT Integration:**
- Automatic vector clock tracking for distributed consistency
- Conflict-free synchronization across multiple nodes
- Mathematical convergence guarantees for distributed operations

---

## 4. Dual Verification System

### Data Verification with Confidence Scoring
```python
from jarvis.core.data_verifier import get_verifier

# Get verifier instance
verifier = get_verifier()

# Verify factual data with dual-model approach
verification_result = verifier.verify_data_immediately(
    content="The capital of France is Paris",
    data_type="factual",
    priority="high"
)

print(f"Verified: {verification_result.is_verified}")
print(f"Confidence: {verification_result.confidence_score:.3f}")
print(f"Primary model result: {verification_result.primary_verification}")
print(f"Secondary model result: {verification_result.secondary_verification}")

# Batch verification for multiple items
data_items = [
    {"content": "Water boils at 100°C", "type": "scientific"},
    {"content": "The Earth is flat", "type": "scientific"},
    {"content": "Python was created by Guido van Rossum", "type": "factual"}
]

batch_results = verifier.verify_batch(data_items)
for i, result in enumerate(batch_results):
    status = "✅ VERIFIED" if result.is_verified else "❌ REJECTED"
    print(f"{status} Item {i+1}: Confidence {result.confidence_score:.3f}")

# Get verification statistics
stats = verifier.get_verification_stats()
print(f"Total verifications: {stats['total_count']}")
print(f"Success rate: {stats['success_rate']:.1%}")
print(f"Average confidence: {stats['avg_confidence']:.3f}")
```

**Verification Process:**
1. Primary model verification with main LLM
2. Secondary verification with different model/approach
3. Confidence calculation based on agreement level
4. Automatic decision based on configurable thresholds

**Confidence Levels:**
- `0.95+`: Full agreement - Auto-accept
- `0.70-0.95`: Partial agreement - Accept with monitoring
- `0.30-0.70`: Disagreement - Flag for manual review
- `<0.30`: Strong disagreement - Auto-reject

---

## 5. Memory System Operations

### Production Memory with Full-Text Search
```python
from jarvis.memory.production_memory import get_production_memory

# Get memory system instance
memory = get_production_memory()

# Store memories with categorization and tagging
memory_id = memory.store_memory(
    content="FastAPI is a modern web framework for Python",
    category="programming",
    tags=["python", "web", "framework", "api"],
    metadata={
        "source": "documentation",
        "difficulty": "intermediate",
        "last_updated": "2024-01-15"
    }
)

# Advanced search with filters
search_results = memory.search_memories(
    query="python web framework",
    category="programming",
    tags=["python", "web"],
    limit=20,
    min_relevance=0.7
)

for result in search_results:
    print(f"Score: {result['relevance_score']:.3f}")
    print(f"Content: {result['content']}")
    print(f"Tags: {', '.join(result['tags'])}")
    print("---")

# Recall memories by category
category_memories = memory.recall_by_category(
    category="programming",
    limit=50,
    sort_by="relevance"
)

# Get memory statistics
stats = memory.get_memory_stats()
print(f"Total memories: {stats['total_count']}")
print(f"Categories: {stats['category_count']}")
print(f"Average relevance: {stats['avg_relevance']:.3f}")

# Update existing memory
memory.update_memory(
    memory_id=memory_id,
    content="FastAPI is a modern, fast web framework for building APIs with Python",
    tags=["python", "web", "framework", "api", "fast"],
    metadata={"last_updated": "2024-01-20"}
)
```

**Memory Operations:**
- `store_memory(content, category=None, tags=None, metadata=None)`: Returns memory ID
- `search_memories(query, category=None, tags=None, limit=50)`: Returns ranked results
- `recall_by_category(category, limit=50, sort_by="created_at")`: Returns category memories
- `update_memory(memory_id, content=None, tags=None, metadata=None)`: Updates existing memory
- `delete_memory(memory_id)`: Removes memory (soft delete with audit trail)

---

## 6. LLM Provider Integration

### Multi-Provider LLM with Intelligent Routing
```python
from jarvis.llm.production_llm import get_production_llm
from jarvis.api.api_models import LLMRequest, Message

# Get LLM interface
llm = get_production_llm()

# Simple chat completion
response = llm.chat_completion(
    messages=[
        Message(role="system", content="You are a helpful programming assistant"),
        Message(role="user", content="Explain list comprehensions in Python")
    ],
    model="llama3:8b",
    temperature=0.7,
    max_tokens=1000
)

print(f"Response: {response.content}")
print(f"Model used: {response.model}")
print(f"Provider: {response.provider}")
print(f"Tokens used: {response.usage['total_tokens']}")

# Batch processing with fallback
requests = [
    LLMRequest(
        messages=[Message(role="user", content="What is machine learning?")],
        model="llama3:8b"
    ),
    LLMRequest(
        messages=[Message(role="user", content="Explain neural networks")],
        model="codellama:13b"  # Different model for code-related query
    )
]

batch_responses = llm.batch_completion(requests)
for i, response in enumerate(batch_responses):
    print(f"Request {i+1}: {response.content[:100]}...")

# Provider status and health
provider_status = llm.get_provider_status()
for provider, status in provider_status.items():
    print(f"{provider}: {'🟢 Online' if status['available'] else '🔴 Offline'}")
    print(f"  Response time: {status['avg_response_time']:.2f}s")
    print(f"  Success rate: {status['success_rate']:.1%}")
```

**LLM Configuration:**
- Primary: Ollama (local, private, no API costs)
- Fallback: OpenAI (cloud, reliable, API costs)  
- Emergency: Mock provider (testing, degraded mode)

**Automatic Features:**
- Intelligent model selection based on query type
- Automatic fallback on provider failure
- Response caching for identical requests
- Connection pooling for efficiency

---

## 7. File Processing System

### Universal File Processor with Plugin Architecture
```python
from jarvis.utils.file_processors import process_file, get_file_info, is_file_supported

# Check if file format is supported
if is_file_supported("document.pdf"):
    print("✅ PDF processing supported")

# Get file information without processing
file_info = get_file_info("example.txt")
print(f"File size: {file_info['size_bytes']} bytes")
print(f"MIME type: {file_info['mime_type']}")
print(f"Last modified: {file_info['last_modified']}")

# Process for memory storage
memory_data = process_file(
    file_path="document.pdf",
    output_format="memory",
    options={
        "extract_text": True,
        "extract_metadata": True,
        "chunk_size": 1000,
        "overlap": 100
    }
)

print(f"Extracted {len(memory_data['chunks'])} text chunks")
print(f"Document title: {memory_data['metadata']['title']}")
print(f"Page count: {memory_data['metadata']['page_count']}")

# Process for structured logging
log_data = process_file(
    file_path="spreadsheet.xlsx",
    output_format="logs",
    options={
        "extract_worksheets": True,
        "include_formulas": True,
        "summary_stats": True
    }
)

# Process for AI agent consumption
agent_report = process_file(
    file_path="image.png", 
    output_format="agent",
    options={
        "extract_text": True,  # OCR if available
        "analyze_content": True,
        "generate_description": True
    }
)

print(f"Agent report: {agent_report['summary']}")
```

**Supported Formats:**
- **Text**: .txt, .md, .rtf (full text extraction)
- **Documents**: .pdf, .docx (text, metadata, structure)
- **Spreadsheets**: .xlsx, .xls (data, formulas, charts)
- **Data**: .json, .csv, .xml (structured data parsing)
- **Images**: .jpg, .png, .gif, .bmp (metadata, OCR if available)

**Output Formats:**
- `"memory"`: Optimized for memory system storage with chunking
- `"logs"`: Structured logging format with full audit trail
- `"agent"`: Human-readable analysis for LLM consumption

---

## 8. CRDT Distributed Operations

### Conflict-Free Distributed Data Types
```python
from jarvis.core.crdt_manager import get_crdt_manager

# Get CRDT manager
crdt_manager = get_crdt_manager()

# Distributed counter operations
health_counter = crdt_manager.get_counter("system_health")
health_counter.increment(95)  # Add to health score
print(f"Current health: {health_counter.value()}")

# Distributed set operations (permanent records)
audit_set = crdt_manager.get_set("security_audit")
audit_set.add("login_attempt_user123_2024-01-20")
audit_set.add("permission_change_admin_2024-01-20")
print(f"Audit entries: {len(audit_set.elements())}")

# Last-write-wins register (configuration)
config_register = crdt_manager.get_register("system_config")
config_register.write({
    "debug_mode": False,
    "max_sessions": 1000,
    "log_level": "INFO"
}, node_id="admin_node")

current_config = config_register.read()
print(f"Current config: {current_config}")

# Distributed synchronization with peers
sync_result = crdt_manager.sync_with_peers([
    "192.168.1.100:8768",
    "192.168.1.101:8768"
])

print(f"Sync successful: {sync_result.success}")
print(f"Peers synchronized: {sync_result.peer_count}")
print(f"Operations synchronized: {sync_result.operation_count}")

# Get CRDT network status
network_status = crdt_manager.get_network_status()
for peer, status in network_status.items():
    print(f"Peer {peer}: {'🟢 Connected' if status['connected'] else '🔴 Disconnected'}")
    print(f"  Last sync: {status['last_sync']}")
    print(f"  Pending operations: {status['pending_ops']}")
```

**CRDT Types Available:**
- **G-Counter**: Grow-only counter (metrics, scores)
- **PN-Counter**: Increment/decrement counter (resource tracking) 
- **G-Set**: Grow-only set (permanent audit records)
- **OR-Set**: Observed-remove set (dynamic collections)
- **LWW-Register**: Last-write-wins (configuration values)
- **Specialized**: Time-series, graphs, workflows

**Mathematical Guarantees:**
- **Convergence**: All nodes eventually reach same state
- **Commutativity**: Operation order doesn't matter
- **Associativity**: Grouping of operations doesn't matter
- **Idempotence**: Duplicate operations have no effect

---

## 9. System Monitoring and Health

### Real-Time Performance Monitoring
```python
from jarvis.monitoring.system_health import get_system_health_monitor
from jarvis.monitoring.realtime_metrics import get_metrics_collector

# System health monitoring
health_monitor = get_system_health_monitor()

# Get current system health
health_report = health_monitor.get_current_health()
print(f"Overall health: {health_report['overall_score']}/100")
print(f"System status: {health_report['status']}")

for component, health in health_report['components'].items():
    status = "🟢" if health['healthy'] else "🔴"
    print(f"{status} {component}: {health['score']}/100")

# Set up health alerts
health_monitor.configure_alerts({
    "email": {
        "enabled": True,
        "recipients": ["admin@company.com"],
        "threshold": 80  # Alert if health drops below 80%
    },
    "webhook": {
        "enabled": True, 
        "url": "https://alerts.company.com/webhook",
        "critical_threshold": 60
    }
})

# Real-time metrics collection
metrics = get_metrics_collector()

# Record custom metrics
metrics.record_metric("api_request_count", 1, {
    "endpoint": "/chat",
    "method": "POST",
    "status": 200
})

metrics.record_timing("database_query_time", 0.045, {
    "table": "archive_entries",
    "operation": "SELECT"
})

# Get metrics summary
summary = metrics.get_metrics_summary(timeframe="1h")
print(f"API requests (1h): {summary['api_request_count']['total']}")
print(f"Avg response time: {summary['api_response_time']['avg']:.3f}s")
print(f"Error rate: {summary['error_rate']['current']:.2%}")

# Real-time metrics streaming (WebSocket)
def metrics_callback(metric_data):
    print(f"Live metric: {metric_data['name']} = {metric_data['value']}")

metrics.start_real_time_stream(
    port=8769,
    callback=metrics_callback,
    filters=["system_health", "api_requests", "memory_usage"]
)
```

**Health Components Monitored:**
- **System**: CPU, memory, disk usage
- **Database**: Connection pool, query performance
- **Network**: Connectivity, latency, throughput
- **CRDT**: Synchronization status, conflict rates
- **LLM**: Provider availability, response times
- **Memory**: Storage usage, search performance

---

## 10. Error Handling and Recovery

### Comprehensive Error Management
```python
from jarvis.core.error_handler import error_handler, ErrorLevel
from jarvis.core.errors import JarvisException, CRDTException

# Configure error handling
error_handler.configure({
    "log_level": "INFO",
    "enable_auto_recovery": True,
    "notification_channels": ["console", "file", "webhook"],
    "recovery_strategies": {
        "database_errors": "retry_with_backoff",
        "network_errors": "circuit_breaker",
        "crdt_conflicts": "auto_resolve"
    }
})

# Manual error handling with context
try:
    result = risky_database_operation()
except Exception as e:
    error_response = error_handler.handle_error(
        error=e,
        context={
            "operation": "database_query",
            "user_id": "user123",
            "session_id": session_id,
            "retry_count": 0
        },
        severity=ErrorLevel.HIGH,
        auto_recovery=True
    )
    
    if error_response.recovered:
        print(f"✅ Automatically recovered: {error_response.recovery_method}")
        result = error_response.recovery_result
    else:
        print(f"❌ Recovery failed: {error_response.error_message}")
        # Implement fallback logic

# Custom exception handling
class CustomBusinessException(JarvisException):
    def __init__(self, message, error_code, context=None):
        super().__init__(message)
        self.error_code = error_code
        self.context = context or {}

# Register custom recovery strategy
@error_handler.register_recovery_strategy(CustomBusinessException)
def recover_business_error(error, context):
    """Custom recovery for business logic errors"""
    if error.error_code == "QUOTA_EXCEEDED":
        # Implement quota reset logic
        return reset_user_quota(context.get("user_id"))
    elif error.error_code == "INVALID_STATE":
        # Implement state repair logic  
        return repair_system_state()
    return False

# Get error statistics
error_stats = error_handler.get_error_statistics(timeframe="24h")
print(f"Total errors (24h): {error_stats['total_count']}")
print(f"Recovery rate: {error_stats['recovery_rate']:.1%}")
print(f"Most common error: {error_stats['most_common']['type']}")
```

**Error Recovery Strategies:**
- **Retry with Exponential Backoff**: Database connection errors
- **Circuit Breaker Pattern**: External API failures
- **Automatic Failover**: LLM provider switching
- **State Repair**: CRDT consistency recovery
- **Graceful Degradation**: Feature disabling on critical errors

---

## Complete Error Reference

### Common Exceptions and Solutions

```python
# Import all error types
from jarvis.core.errors import (
    JarvisException,           # Base exception
    DatabaseError,             # Database operation failures
    CRDTException,            # CRDT operation errors
    LLMProviderException,     # LLM provider issues
    PluginException,          # Plugin loading/execution errors
    ValidationError,          # Data validation failures
    SecurityException,        # Security and authentication errors
    NetworkError,             # Network and connectivity issues
    ConfigurationError        # Configuration and setup errors
)

# Exception handling patterns
try:
    # Risky operation
    pass
except DatabaseError as e:
    # Database-specific recovery
    if "connection" in str(e).lower():
        # Reconnect and retry
        pass
    elif "timeout" in str(e).lower():
        # Increase timeout and retry
        pass
        
except CRDTException as e:
    # CRDT-specific recovery
    if e.error_type == "conflict":
        # Manual conflict resolution
        pass
    elif e.error_type == "sync_failure":
        # Retry synchronization
        pass
        
except LLMProviderException as e:
    # LLM provider fallback
    if e.provider == "ollama":
        # Try OpenAI fallback
        pass
    elif e.error_type == "quota_exceeded":
        # Wait and retry
        pass
        
except JarvisException as e:
    # Generic Jarvis error handling
    error_handler.log_error(e, "operation_context")
    
except Exception as e:
    # Unexpected error handling
    error_handler.handle_unexpected_error(e)
```

This comprehensive API reference provides complete usage examples for all major Jarvis V0.19 systems with proper parameter documentation, return types, and exception handling patterns.