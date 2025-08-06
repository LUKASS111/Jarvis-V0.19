# 🚀 Enhanced Startup and Deployment Guide

## Quick Start Commands

### 1. Immediate Development Setup
```bash
# Clone and setup environment
git clone https://github.com/LUKASS111/Jarvis-V0.19.git
cd Jarvis-V0.19

# Install dependencies
pip install -r requirements.txt

# Quick validation (30 seconds)
python -c "from jarvis.core.main import JarvisAgent; agent = JarvisAgent(); print('✅ Ready' if agent.initialize() else '❌ Issues')"

# Start interactive CLI
python main.py
```

### 2. Production Deployment
```bash
# Start unified backend service
python main.py --backend --port 8080

# Start GUI interface
python start_gui.py

# Run system health check
python system_dashboard.py --monitor
```

### 3. Container Deployment
```bash
# Build Docker image
docker build -t jarvis-v019 .

# Run with persistent data
docker run -d \
  --name jarvis-production \
  -p 8080:8080 \
  -v jarvis-data:/app/data \
  jarvis-v019 --backend
```

## Environment Configuration

### Development Environment
```python
# config/environments/development.yaml
system:
  debug: true
  log_level: DEBUG
  
llm:
  default_provider: ollama
  models:
    - llama3:8b
    - codellama:13b
    
security:
  require_mfa: false
  session_timeout: 3600
```

### Production Environment
```python
# config/environments/production.yaml
system:
  debug: false
  log_level: INFO
  
llm:
  default_provider: openai
  fallback_chain:
    - openai
    - ollama
    
security:
  require_mfa: true
  session_timeout: 1800
  encryption_enabled: true
```

## API Integration Examples

### REST API Usage
```python
import requests

# Start backend service first
# python main.py --backend --port 8080

# Chat with Jarvis
response = requests.post('http://localhost:8080/api/chat', json={
    'message': 'Explain quantum computing',
    'session_id': 'my-session-123'
})

print(response.json())
# Output: {'response': 'Quantum computing explanation...', 'session_id': 'my-session-123'}

# Store memory
requests.post('http://localhost:8080/api/memory/store', json={
    'content': 'Important meeting notes',
    'category': 'work',
    'tags': ['meeting', 'Q4-planning']
})

# Search memories
memories = requests.get('http://localhost:8080/api/memory/search', params={
    'query': 'meeting',
    'category': 'work'
})
print(memories.json())
```

### WebSocket Real-time Integration
```python
import websocket
import json

def on_message(ws, message):
    data = json.loads(message)
    print(f"Real-time update: {data}")

def on_open(ws):
    # Subscribe to system health updates
    ws.send(json.dumps({
        'type': 'subscribe',
        'channel': 'system_health'
    }))

# Connect to real-time updates
ws = websocket.WebSocketApp(
    "ws://localhost:8768/ws",
    on_message=on_message,
    on_open=on_open
)
ws.run_forever()
```

## Advanced Configuration

### LLM Provider Setup
```python
# Custom LLM provider configuration
from jarvis.core.llm import get_llm_router, register_provider

router = get_llm_router()

# Register OpenAI provider
router.register_provider('openai', {
    'api_key': 'your-api-key',
    'base_url': 'https://api.openai.com/v1',
    'models': ['gpt-4', 'gpt-3.5-turbo']
})

# Register local Ollama
router.register_provider('ollama', {
    'base_url': 'http://localhost:11434',
    'models': ['llama3:8b', 'codellama:13b']
})

# Set intelligent fallback chain
router.set_fallback_chain('auto', ['openai', 'ollama'])
```

### Security Configuration
```python
from jarvis.security import SecurityManager, AuthenticationManager

# Initialize security framework
security = SecurityManager()
auth = AuthenticationManager()

# Enable enterprise security
security.enable_enterprise_mode()

# Configure MFA
auth.enable_mfa_for_all_users()

# Set up compliance monitoring
compliance_result = await security.validate_compliance()
print(f"Compliance score: {compliance_result['score']}/100")
```

## System Monitoring and Health

### Health Check Dashboard
```python
from jarvis.core.system_health import SystemHealthMonitor
from jarvis.core.realtime_metrics import MetricsCollector

# Start comprehensive monitoring
health_monitor = SystemHealthMonitor()
metrics = MetricsCollector()

# Get real-time system status
status = health_monitor.get_system_status()
print(f"System Health: {status['overall_health_score']}/100")

# Monitor specific metrics
cpu_metric = metrics.get_metric('system.cpu_usage')
memory_metric = metrics.get_metric('system.memory_usage')

print(f"CPU Usage: {cpu_metric.current_value}%")
print(f"Memory Usage: {memory_metric.current_value}%")
```

### Performance Optimization
```python
from jarvis.core.performance_monitor import PerformanceMonitor

monitor = PerformanceMonitor()

# Start performance profiling
with monitor.profile_context('api_request'):
    # Your code here
    result = process_complex_request()

# Get performance insights
metrics = monitor.get_performance_summary()
print(f"Average response time: {metrics['avg_response_time']}ms")
```

## Troubleshooting Guide

### Common Issues and Solutions

**1. Import Errors**
```bash
# Fix Python path issues
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
python main.py

# Or use absolute imports
python -m jarvis.main
```

**2. Database Connection Issues**
```python
# Reset database
from jarvis.core.data_archiver import get_archiver
archiver = get_archiver()
archiver.reset_database()  # WARNING: This deletes all data
```

**3. CRDT Synchronization Problems**
```python
# Reset CRDT network state
from jarvis.core.crdt_manager import get_crdt_manager
crdt_manager = get_crdt_manager()
crdt_manager.reset_network_state()
```

**4. Performance Issues**
```bash
# Run performance diagnostics
python tests/performance/test_performance_comprehensive.py

# Optimize system
python system_efficiency_optimizer.py --auto-optimize
```

## Integration Patterns

### Microservices Integration
```python
# Use Jarvis as a microservice
from jarvis.api.api_router import create_api_app
from fastapi import FastAPI

app = FastAPI()

# Mount Jarvis API
jarvis_api = create_api_app()
app.mount("/jarvis", jarvis_api)

# Add custom endpoints
@app.get("/custom/health")
async def custom_health():
    return {"status": "healthy", "service": "custom-service"}
```

### Event-Driven Architecture
```python
from jarvis.core.event_system import EventBus, EventHandler

bus = EventBus()

@bus.subscribe('user.message.received')
class MessageHandler(EventHandler):
    async def handle(self, event):
        # Process user message
        response = await self.process_message(event.data['message'])
        
        # Emit response event
        await bus.emit('ai.response.generated', {
            'response': response,
            'original_message': event.data['message']
        })

# Start event processing
await bus.start()
```

## Best Practices

### 1. Error Handling
```python
from jarvis.core.error_handler import safe_execute, ErrorLevel

@safe_execute(
    fallback_value={"error": "Service unavailable"},
    context="API endpoint",
    level=ErrorLevel.ERROR
)
def process_request(data):
    # Your processing logic
    return {"result": "success"}
```

### 2. Resource Management
```python
from jarvis.core.resource_manager import ResourceManager

with ResourceManager() as rm:
    # Resources are automatically managed
    llm = rm.get_llm_instance()
    memory = rm.get_memory_instance()
    
    result = llm.process(user_input)
    memory.store(result)
    
# Resources automatically cleaned up
```

### 3. Testing Integration
```python
import pytest
from jarvis.testing import JarvisTestClient

@pytest.fixture
def jarvis_client():
    return JarvisTestClient()

def test_api_integration(jarvis_client):
    response = jarvis_client.chat("Hello")
    assert response['success'] is True
    assert 'response' in response
```

## Deployment Checklist

- [ ] **Environment Setup**
  - [ ] Python 3.8+ installed
  - [ ] Dependencies installed (`pip install -r requirements.txt`)
  - [ ] Environment variables configured

- [ ] **System Validation**
  - [ ] Core tests passing (`python run_tests.py`)
  - [ ] Health check successful (`python system_dashboard.py`)
  - [ ] Database accessible

- [ ] **Security Configuration**
  - [ ] MFA enabled for production
  - [ ] SSL/TLS certificates installed
  - [ ] Compliance checks passing

- [ ] **Performance Optimization**
  - [ ] Resource limits configured
  - [ ] Monitoring dashboards setup
  - [ ] Backup procedures tested

- [ ] **Production Readiness**
  - [ ] Load balancer configured
  - [ ] Auto-scaling policies setup
  - [ ] Incident response procedures documented

## Support and Maintenance

### Log Analysis
```bash
# Analyze error patterns
python scripts/log_analyzer.py --errors --last-24h

# Generate system report
python scripts/system_report.py --comprehensive
```

### Backup and Recovery
```bash
# Create system backup
python scripts/backup_system.py --full

# Restore from backup
python scripts/restore_system.py --backup-id latest
```

### Updates and Maintenance
```bash
# Check for updates
python scripts/check_updates.py

# Apply updates
python scripts/apply_updates.py --auto-restart

# Validate system after update
python run_tests.py --comprehensive
```