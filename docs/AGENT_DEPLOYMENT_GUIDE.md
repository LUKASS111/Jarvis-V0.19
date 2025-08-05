# Agent Deployment Guide
## Complete Guide for Deploying AI Agents in Jarvis V0.19

---

## Table of Contents

1. [Agent Architecture Overview](#agent-architecture-overview)
2. [Deployment Prerequisites](#deployment-prerequisites)
3. [Agent Configuration](#agent-configuration)
4. [Deployment Methods](#deployment-methods)
5. [Agent Coordination Setup](#agent-coordination-setup)
6. [Monitoring and Management](#monitoring-and-management)
7. [Troubleshooting](#troubleshooting)
8. [Best Practices](#best-practices)

---

## Agent Architecture Overview

### Agent Types in Jarvis V0.19

#### Core System Agents
Built-in agents that handle essential system operations:

```
System Agent Hierarchy
├── ArchiveAgent - Data archiving and retrieval operations
├── VerificationAgent - Data verification and validation
├── BackupAgent - System backup and recovery management
├── MonitoringAgent - System health and performance monitoring
├── SyncAgent - CRDT synchronization coordination
└── SecurityAgent - Security validation and compliance
```

#### Custom Business Agents
User-defined agents for specific business logic:

```
Custom Agent Types
├── DataAnalysisAgent - Business intelligence and analytics
├── DocumentProcessingAgent - Document workflow automation
├── CustomerServiceAgent - Customer interaction handling
├── ComplianceAgent - Regulatory compliance monitoring
├── IntegrationAgent - External system integration
└── WorkflowAgent - Business process automation
```

#### Specialized CRDT Agents
Agents that work with specialized CRDT types:

```
CRDT Agent Specializations
├── TimeSeriesAgent - Time-series data processing
├── GraphAgent - Relationship and network analysis
├── WorkflowAgent - State machine coordination
└── AnalyticsAgent - Real-time analytics processing
```

---

## Deployment Prerequisites

### System Requirements

#### Minimum Requirements
```yaml
hardware:
  cpu_cores: 2
  memory_gb: 4
  storage_gb: 20
  network: "100 Mbps"

software:
  python: ">=3.8"
  operating_system: ["Linux", "macOS", "Windows"]
  dependencies:
    - "PyQt5>=5.15"
    - "psutil>=5.8"
    - "requests>=2.25"
```

#### Recommended Production Requirements
```yaml
hardware:
  cpu_cores: 8
  memory_gb: 16
  storage_gb: 100
  network: "1 Gbps"
  
infrastructure:
  load_balancer: true
  monitoring: true
  backup_storage: true
  redundancy: "multi-zone"
```

### Environment Setup

#### 1. Install Core Dependencies
```bash
# Clone repository
git clone https://github.com/LUKASS111/Jarvis-V0.19.git
cd Jarvis-V0.19

# Install Python dependencies
pip install -r requirements.txt

# Verify installation
python -c "import jarvis; print('Jarvis installed successfully')"
```

#### 2. Configure System Environment
```bash
# Set environment variables
export JARVIS_ENV=production
export JARVIS_CONFIG_PATH=config/environments/production.yaml
export JARVIS_LOG_LEVEL=INFO

# Create necessary directories
mkdir -p data logs config/environments
```

#### 3. Initialize Database
```bash
# Initialize archive database
python -c "
from jarvis.core.data_archiver import initialize_database
initialize_database('data/jarvis_archive.db')
print('Database initialized')
"
```

---

## Agent Configuration

### Agent Configuration Structure

```yaml
# config/agents/sample_agent.yaml
agent:
  name: "CustomDataAnalysisAgent"
  type: "business_logic"
  version: "1.0.0"
  
deployment:
  node_id: "agent_node_001"
  resources:
    cpu_limit: "1000m"      # 1 CPU core
    memory_limit: "2Gi"     # 2GB RAM
    storage_limit: "10Gi"   # 10GB storage
  
  environment:
    AGENT_DEBUG: "false"
    AGENT_TIMEOUT: "300"
    AGENT_MAX_RETRIES: "3"
  
capabilities:
  - "data_analysis"
  - "report_generation"
  - "statistical_modeling"
  
dependencies:
  llm_providers:
    - "ollama"
    - "openai"
  external_apis:
    - "database_connection"
    - "analytics_api"
  
coordination:
  enable_crdt: true
  sync_interval: 30
  max_peers: 10
  
security:
  enable_sandboxing: true
  allowed_file_access:
    - "/data/analytics"
    - "/tmp/agent_workspace"
  network_access:
    allowed_domains:
      - "api.analytics.com"
      - "data.company.com"
```

### Agent Implementation Template

```python
# agents/custom_analysis_agent.py
from jarvis.core.agent_workflow import BaseAgent, AgentCapability
from jarvis.core.crdt_manager import get_crdt_manager
from jarvis.core.llm import get_llm_router, CompletionRequest, Message

class CustomDataAnalysisAgent(BaseAgent):
    """Custom agent for data analysis tasks"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(
            agent_id=config['agent']['name'],
            capabilities=[
                AgentCapability.DATA_ANALYSIS,
                AgentCapability.REPORT_GENERATION
            ]
        )
        self.config = config
        self.crdt_manager = get_crdt_manager()
        self.llm_router = get_llm_router()
        
        # Initialize agent-specific CRDT state
        self.analysis_counter = self.crdt_manager.get_counter("analysis_tasks")
        self.results_set = self.crdt_manager.get_set("analysis_results")
    
    async def process_task(self, task: AgentTask) -> AgentResponse:
        """Process incoming analysis task"""
        try:
            self.logger.info(f"Processing task: {task.task_id}")
            
            # Validate task requirements
            if not self._validate_task(task):
                return self._create_error_response(task, "Task validation failed")
            
            # Extract data for analysis
            data = await self._extract_data(task.data_source)
            
            # Perform analysis
            analysis_result = await self._perform_analysis(data, task.parameters)
            
            # Generate report using LLM
            report = await self._generate_report(analysis_result)
            
            # Update distributed state
            self.analysis_counter.increment(1)
            result_id = f"result_{task.task_id}_{int(time.time())}"
            self.results_set.add(result_id)
            
            # Return successful response
            return AgentResponse(
                task_id=task.task_id,
                status="completed",
                data={
                    "analysis": analysis_result,
                    "report": report,
                    "result_id": result_id
                },
                metadata={
                    "execution_time": time.time() - task.created_at,
                    "agent_id": self.agent_id,
                    "total_analyses": self.analysis_counter.value()
                }
            )
            
        except Exception as e:
            self.logger.error(f"Task processing failed: {str(e)}")
            return self._create_error_response(task, str(e))
    
    async def _extract_data(self, data_source: str) -> Dict[str, Any]:
        """Extract data from specified source"""
        # Implementation for data extraction
        pass
    
    async def _perform_analysis(self, data: Dict[str, Any], parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Perform statistical analysis on data"""
        # Implementation for analysis logic
        pass
    
    async def _generate_report(self, analysis_result: Dict[str, Any]) -> str:
        """Generate human-readable report using LLM"""
        request = CompletionRequest(
            messages=[
                Message(
                    role="system",
                    content="You are a data analyst. Generate a clear, concise report based on the analysis results."
                ),
                Message(
                    role="user", 
                    content=f"Create a report for this analysis: {json.dumps(analysis_result)}"
                )
            ],
            model="llama3:8b",
            temperature=0.3
        )
        
        response = await self.llm_router.chat_completion(request)
        return response.content if response.success else "Report generation failed"
    
    def get_health_status(self) -> Dict[str, Any]:
        """Return agent health information"""
        return {
            "status": "healthy",
            "tasks_completed": self.analysis_counter.value(),
            "unique_results": len(self.results_set.elements()),
            "memory_usage_mb": self._get_memory_usage(),
            "last_activity": self._get_last_activity_time()
        }
```

---

## Deployment Methods

### Method 1: Single-Node Development Deployment

#### Quick Start Deployment
```bash
# 1. Start core system
python main.py &
JARVIS_PID=$!

# 2. Deploy agent
python agent_launcher.py deploy \
  --config config/agents/analysis_agent.yaml \
  --environment development

# 3. Verify deployment
python agent_launcher.py status
```

#### Development Configuration
```yaml
# config/environments/development.yaml
deployment:
  mode: "development"
  agents:
    max_concurrent: 5
    auto_restart: true
    debug_mode: true
  
  resources:
    cpu_limit_default: "500m"
    memory_limit_default: "1Gi"
  
  monitoring:
    enabled: true
    metrics_interval: 10
    log_level: "DEBUG"
```

### Method 2: Multi-Node Production Deployment

#### Production Deployment Script
```bash
#!/bin/bash
# deploy_production.sh

set -e

echo "Starting Jarvis V0.19 Production Deployment"

# Configuration
ENVIRONMENT="production"
CONFIG_DIR="config/environments"
AGENT_CONFIG_DIR="config/agents"
LOG_DIR="logs"

# Create deployment directories
mkdir -p $LOG_DIR/agents
mkdir -p data/production

# 1. Deploy core system across nodes
echo "Deploying core system..."
for node in node1 node2 node3; do
    echo "Deploying to $node..."
    
    # Copy configuration
    scp -r config/ $node:/opt/jarvis/
    scp -r jarvis/ $node:/opt/jarvis/
    
    # Start core system on node
    ssh $node "cd /opt/jarvis && \
               export JARVIS_NODE_ID=$node && \
               export JARVIS_ENV=$ENVIRONMENT && \
               python main.py --daemon" &
done

# Wait for core system initialization
sleep 30

# 2. Deploy agents
echo "Deploying agents..."

# Deploy data analysis agents (2 instances for redundancy)
python agent_launcher.py deploy \
  --config $AGENT_CONFIG_DIR/data_analysis_agent.yaml \
  --instances 2 \
  --nodes "node1,node2"

# Deploy document processing agents  
python agent_launcher.py deploy \
  --config $AGENT_CONFIG_DIR/document_processing_agent.yaml \
  --instances 3 \
  --nodes "node1,node2,node3"

# Deploy monitoring agent (single instance)
python agent_launcher.py deploy \
  --config $AGENT_CONFIG_DIR/monitoring_agent.yaml \
  --instances 1 \
  --node "node1"

# 3. Verify deployment
echo "Verifying deployment..."
python agent_launcher.py health-check --all-nodes

# 4. Start monitoring
echo "Starting monitoring..."
python system_dashboard.py --production &

echo "Production deployment completed successfully"
```

### Method 3: Container-Based Deployment

#### Dockerfile for Agent Container
```dockerfile
# Dockerfile.agent
FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    git \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy application code
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY jarvis/ jarvis/
COPY config/ config/
COPY agents/ agents/

# Create non-root user for security
RUN useradd -m -u 1000 jarvis && \
    chown -R jarvis:jarvis /app

USER jarvis

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=60s \
  CMD python -c "from jarvis.core.health import check_agent_health; check_agent_health()"

# Default command
CMD ["python", "agent_launcher.py", "run"]
```

#### Docker Compose Configuration
```yaml
# docker-compose.yml
version: '3.8'

services:
  jarvis-core:
    build: .
    image: jarvis:v0.19
    environment:
      - JARVIS_ENV=production
      - JARVIS_NODE_ID=core-001
    ports:
      - "8080:8080"    # API port
      - "8765:8765"    # CRDT sync port
    volumes:
      - ./data:/app/data
      - ./config:/app/config
      - ./logs:/app/logs
    networks:
      - jarvis-network
    
  data-analysis-agent:
    build:
      context: .
      dockerfile: Dockerfile.agent
    image: jarvis-agent:v0.19
    environment:
      - JARVIS_ENV=production
      - AGENT_TYPE=data_analysis
      - AGENT_CONFIG=config/agents/data_analysis_agent.yaml
    depends_on:
      - jarvis-core
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
    networks:
      - jarvis-network
    deploy:
      replicas: 2
      resources:
        limits:
          memory: 2G
          cpus: '1.0'
  
  document-processing-agent:
    build:
      context: .
      dockerfile: Dockerfile.agent
    image: jarvis-agent:v0.19
    environment:
      - JARVIS_ENV=production
      - AGENT_TYPE=document_processing
      - AGENT_CONFIG=config/agents/document_processing_agent.yaml
    depends_on:
      - jarvis-core
    volumes:
      - ./config:/app/config
      - ./logs:/app/logs
      - ./data/documents:/app/data/documents
    networks:
      - jarvis-network
    deploy:
      replicas: 3
      resources:
        limits:
          memory: 4G
          cpus: '2.0'

networks:
  jarvis-network:
    driver: bridge
```

#### Container Deployment Commands
```bash
# Build images
docker-compose build

# Deploy services
docker-compose up -d

# Scale agents
docker-compose up -d --scale data-analysis-agent=3
docker-compose up -d --scale document-processing-agent=5

# Monitor deployment
docker-compose ps
docker-compose logs -f

# Health checks
docker-compose exec jarvis-core python agent_launcher.py status
```

---

## Agent Coordination Setup

### CRDT-Based Coordination

#### Initialize Distributed Coordination
```python
# scripts/setup_coordination.py
from jarvis.core.distributed_coordination import DistributedAgentCoordinator
from jarvis.core.crdt_manager import get_crdt_manager

def setup_agent_coordination():
    """Initialize distributed agent coordination"""
    
    # Initialize CRDT manager
    crdt_manager = get_crdt_manager()
    
    # Initialize distributed coordinator
    coordinator = DistributedAgentCoordinator(
        node_id="coordinator_primary",
        distribution_strategy="capability_based"
    )
    
    # Register coordinator with CRDT manager
    coordinator_state = crdt_manager.get_register("coordinator_state")
    coordinator_state.write({
        "active": True,
        "node_id": "coordinator_primary",
        "started_at": time.time()
    }, "system")
    
    # Initialize task distribution CRDT
    task_queue = crdt_manager.get_set("distributed_task_queue")
    
    # Initialize agent registry CRDT
    agent_registry = crdt_manager.get_register("agent_registry")
    
    print("Distributed coordination initialized successfully")
    return coordinator

if __name__ == "__main__":
    coordinator = setup_agent_coordination()
```

#### Agent Registration
```python
# In agent initialization
def register_agent_with_coordination(agent_instance, coordinator):
    """Register agent with distributed coordination system"""
    
    registration_data = {
        "agent_id": agent_instance.agent_id,
        "capabilities": [cap.value for cap in agent_instance.capabilities],
        "node_id": agent_instance.node_id,
        "status": "active",
        "resources": agent_instance.get_resource_status(),
        "registered_at": time.time()
    }
    
    # Register with coordinator
    coordinator.register_agent_node(agent_instance.to_agent_node())
    
    # Update distributed registry
    agent_registry = coordinator.crdt_manager.get_register(f"agent_{agent_instance.agent_id}")
    agent_registry.write(registration_data, agent_instance.node_id)
    
    print(f"Agent {agent_instance.agent_id} registered successfully")
```

### Task Distribution

#### Automatic Task Distribution
```python
# Task distribution configuration
class TaskDistributionConfig:
    def __init__(self):
        self.strategies = {
            "round_robin": self._round_robin_strategy,
            "capability_based": self._capability_based_strategy,
            "load_balanced": self._load_balanced_strategy,
            "geographic": self._geographic_strategy
        }
    
    def distribute_task(self, task: AgentTask, available_agents: List[AgentNode]) -> AgentNode:
        """Distribute task to optimal agent"""
        strategy = task.distribution_strategy or "capability_based"
        return self.strategies[strategy](task, available_agents)
    
    def _capability_based_strategy(self, task: AgentTask, agents: List[AgentNode]) -> AgentNode:
        """Select agent based on required capabilities"""
        suitable_agents = [
            agent for agent in agents 
            if all(cap in agent.capabilities for cap in task.required_capabilities)
        ]
        
        if not suitable_agents:
            raise NoSuitableAgentException(f"No agents with capabilities: {task.required_capabilities}")
        
        # Select agent with best resource availability
        return max(suitable_agents, key=lambda a: a.available_resources.cpu_percent)
```

---

## Monitoring and Management

### Agent Health Monitoring

#### Health Check Implementation
```python
# jarvis/monitoring/agent_health.py
from jarvis.core.monitoring import HealthChecker
from jarvis.core.errors import handle_error, ErrorSeverity

class AgentHealthMonitor:
    """Comprehensive agent health monitoring"""
    
    def __init__(self, check_interval: int = 30):
        self.check_interval = check_interval
        self.health_checker = HealthChecker()
        self.alert_thresholds = {
            "memory_usage_percent": 85,
            "cpu_usage_percent": 90,
            "task_failure_rate": 0.1,
            "response_time_ms": 5000
        }
    
    async def monitor_agent(self, agent_id: str) -> HealthStatus:
        """Monitor individual agent health"""
        try:
            # Get agent metrics
            metrics = await self._collect_agent_metrics(agent_id)
            
            # Check health criteria
            health_score = self._calculate_health_score(metrics)
            
            # Generate alerts if necessary
            alerts = self._check_alert_conditions(metrics)
            
            # Update health status
            status = HealthStatus(
                agent_id=agent_id,
                health_score=health_score,
                metrics=metrics,
                alerts=alerts,
                timestamp=time.time()
            )
            
            # Store in distributed state
            await self._update_health_status(status)
            
            return status
            
        except Exception as e:
            handle_error(e, context={"agent_id": agent_id}, severity=ErrorSeverity.HIGH)
            return HealthStatus(agent_id=agent_id, health_score=0, status="error")
    
    async def _collect_agent_metrics(self, agent_id: str) -> Dict[str, Any]:
        """Collect comprehensive agent metrics"""
        # Implementation for metrics collection
        pass
```

#### Monitoring Dashboard Setup
```python
# scripts/setup_monitoring.py
from jarvis.monitoring import DashboardManager, AlertManager

def setup_agent_monitoring():
    """Set up comprehensive agent monitoring"""
    
    # Initialize dashboard
    dashboard = DashboardManager()
    
    # Create agent monitoring dashboard
    dashboard.create_dashboard(
        name="Agent Fleet Overview",
        panels=[
            {
                "title": "Agent Health Status",
                "type": "status_grid",
                "query": "agent_health_status",
                "refresh_interval": 10
            },
            {
                "title": "Task Distribution",
                "type": "pie_chart", 
                "query": "tasks_by_agent",
                "time_range": "1h"
            },
            {
                "title": "Performance Metrics",
                "type": "time_series",
                "query": "agent_performance_metrics",
                "metrics": ["response_time", "throughput", "error_rate"]
            },
            {
                "title": "Resource Usage", 
                "type": "gauge",
                "query": "agent_resource_usage",
                "thresholds": {"warning": 70, "critical": 90}
            }
        ]
    )
    
    # Set up alerts
    alert_manager = AlertManager()
    
    # Critical alerts
    alert_manager.add_alert_rule(
        name="agent_down",
        condition="agent_health_score == 0",
        severity="critical",
        notification_channels=["email", "slack", "pagerduty"]
    )
    
    # Warning alerts
    alert_manager.add_alert_rule(
        name="high_resource_usage",
        condition="memory_usage_percent > 85 OR cpu_usage_percent > 90",
        severity="warning",
        notification_channels=["email", "slack"]
    )
    
    print("Agent monitoring dashboard configured successfully")
```

### Performance Analytics

#### Agent Performance Tracking
```python
# jarvis/analytics/agent_performance.py
class AgentPerformanceAnalyzer:
    """Analyze and track agent performance over time"""
    
    def __init__(self):
        self.crdt_manager = get_crdt_manager()
        self.performance_data = self.crdt_manager.get_set("agent_performance_logs")
    
    def record_task_completion(self, agent_id: str, task_data: Dict[str, Any]):
        """Record task completion metrics"""
        performance_entry = {
            "agent_id": agent_id,
            "task_id": task_data["task_id"],
            "execution_time_ms": task_data["execution_time"] * 1000,
            "success": task_data.get("success", True),
            "resource_usage": task_data.get("resource_usage", {}),
            "timestamp": time.time()
        }
        
        entry_id = f"perf_{agent_id}_{task_data['task_id']}_{int(time.time())}"
        self.performance_data.add((entry_id, performance_entry))
    
    def get_agent_performance_report(self, agent_id: str, time_range: Tuple[float, float]) -> Dict[str, Any]:
        """Generate comprehensive performance report for agent"""
        start_time, end_time = time_range
        
        # Collect performance data
        agent_entries = [
            entry for _, entry in self.performance_data.elements()
            if (entry["agent_id"] == agent_id and 
                start_time <= entry["timestamp"] <= end_time)
        ]
        
        if not agent_entries:
            return {"error": "No performance data found for specified time range"}
        
        # Calculate metrics
        total_tasks = len(agent_entries)
        successful_tasks = sum(1 for entry in agent_entries if entry["success"])
        success_rate = successful_tasks / total_tasks if total_tasks > 0 else 0
        
        execution_times = [entry["execution_time_ms"] for entry in agent_entries]
        avg_execution_time = sum(execution_times) / len(execution_times)
        
        return {
            "agent_id": agent_id,
            "time_range": {"start": start_time, "end": end_time},
            "metrics": {
                "total_tasks": total_tasks,
                "successful_tasks": successful_tasks,
                "success_rate": success_rate,
                "average_execution_time_ms": avg_execution_time,
                "min_execution_time_ms": min(execution_times),
                "max_execution_time_ms": max(execution_times),
                "throughput_tasks_per_hour": total_tasks / ((end_time - start_time) / 3600)
            }
        }
```

---

## Troubleshooting

### Common Deployment Issues

#### Issue 1: Agent Registration Failures
**Symptoms**: Agents fail to register with coordinator
```bash
# Diagnosis
python agent_launcher.py diagnose --agent-id "problem_agent"

# Check CRDT synchronization
python -c "
from jarvis.core.crdt_manager import get_crdt_manager
crdt = get_crdt_manager()
registry = crdt.get_register('agent_registry')
print('Registry status:', registry.read())
"

# Solution
python agent_launcher.py repair --registration --agent-id "problem_agent"
```

#### Issue 2: Task Distribution Problems
**Symptoms**: Tasks not being distributed to available agents
```bash
# Check task queue status
python -c "
from jarvis.core.distributed_coordination import get_coordinator
coordinator = get_coordinator()
status = coordinator.get_task_queue_status()
print('Queue status:', status)
"

# Clear stuck tasks
python agent_launcher.py clear-queue --force
```

#### Issue 3: Memory Issues
**Symptoms**: Agents consuming excessive memory
```bash
# Monitor memory usage
python system_dashboard.py --monitor-memory --agent-id "memory_problem_agent"

# Force garbage collection
python agent_launcher.py gc --agent-id "memory_problem_agent"

# Restart with lower memory limits
python agent_launcher.py restart --agent-id "memory_problem_agent" --memory-limit "1Gi"
```

#### Issue 4: Network Connectivity Problems
**Symptoms**: CRDT synchronization failures
```bash
# Test network connectivity
python -c "
from jarvis.core.crdt.crdt_network import test_network_connectivity
result = test_network_connectivity()
print('Network test result:', result)
"

# Reset network configuration
python agent_launcher.py reset-network --all-agents
```

### Diagnostic Tools

#### Agent Diagnostic Script
```python
# scripts/diagnose_agent.py
import sys
from jarvis.core.agent_workflow import get_agent_by_id
from jarvis.core.crdt_manager import get_crdt_manager
from jarvis.monitoring.agent_health import AgentHealthMonitor

def diagnose_agent(agent_id: str):
    """Comprehensive agent diagnosis"""
    print(f"Diagnosing agent: {agent_id}")
    print("=" * 50)
    
    # 1. Check agent registration
    try:
        agent = get_agent_by_id(agent_id)
        print(f"✅ Agent found: {agent.agent_id}")
        print(f"   Status: {agent.status}")
        print(f"   Capabilities: {agent.capabilities}")
    except Exception as e:
        print(f"❌ Agent not found: {e}")
        return
    
    # 2. Check CRDT state
    crdt_manager = get_crdt_manager()
    agent_registry = crdt_manager.get_register(f"agent_{agent_id}")
    registration_data = agent_registry.read()
    
    if registration_data:
        print(f"✅ CRDT registration found")
        print(f"   Node ID: {registration_data.get('node_id')}")
        print(f"   Registered at: {registration_data.get('registered_at')}")
    else:
        print(f"❌ No CRDT registration found")
    
    # 3. Check health status
    health_monitor = AgentHealthMonitor()
    health_status = health_monitor.get_current_status(agent_id)
    
    if health_status:
        print(f"✅ Health status available")
        print(f"   Health score: {health_status.health_score}/100")
        print(f"   Last check: {health_status.timestamp}")
    else:
        print(f"❌ No health status available")
    
    # 4. Check resource usage
    resource_status = agent.get_resource_status()
    print(f"📊 Resource usage:")
    print(f"   CPU: {resource_status.get('cpu_percent', 'N/A')}%")
    print(f"   Memory: {resource_status.get('memory_mb', 'N/A')}MB")
    print(f"   Active tasks: {resource_status.get('active_tasks', 'N/A')}")

if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python diagnose_agent.py <agent_id>")
        sys.exit(1)
    
    diagnose_agent(sys.argv[1])
```

---

## Best Practices

### Security Best Practices

#### 1. Agent Sandboxing
```python
# Secure agent configuration
agent_security_config = {
    "sandboxing": {
        "enabled": True,
        "restrict_file_access": True,
        "allowed_directories": [
            "/data/agent_workspace",
            "/tmp/agent_temp"
        ],
        "deny_network_access": False,
        "allowed_domains": [
            "api.internal.company.com",
            "data.analytics.com"
        ]
    },
    "resource_limits": {
        "max_memory_mb": 2048,
        "max_cpu_percent": 50,
        "max_file_descriptors": 1000,
        "execution_timeout_seconds": 300
    },
    "authentication": {
        "required": True,
        "method": "api_key",
        "rotate_keys": True,
        "key_rotation_interval_hours": 24
    }
}
```

#### 2. Secure Communication
```yaml
# config/security/agent_communication.yaml
communication:
  encryption:
    enabled: true
    method: "TLS_1_3"
    certificate_path: "/etc/ssl/certs/jarvis.crt"
    private_key_path: "/etc/ssl/private/jarvis.key"
  
  authentication:
    method: "mutual_tls"
    verify_certificates: true
    allowed_agents_file: "/etc/jarvis/allowed_agents.json"
  
  message_signing:
    enabled: true
    algorithm: "ECDSA_P256"
    key_rotation_hours: 168  # 1 week
```

### Performance Best Practices

#### 1. Resource Optimization
```python
# Agent resource management
class ResourceOptimizedAgent(BaseAgent):
    """Agent with optimized resource usage"""
    
    def __init__(self, config):
        super().__init__(config)
        self.task_queue_size = 10  # Limit concurrent tasks
        self.memory_threshold = 0.8  # Stop accepting tasks at 80% memory
        self.cleanup_interval = 300  # Cleanup every 5 minutes
    
    async def process_task(self, task: AgentTask) -> AgentResponse:
        """Process task with resource monitoring"""
        # Check resource availability before processing
        if not self._check_resource_availability():
            return self._create_rejection_response(task, "Insufficient resources")
        
        # Process with resource tracking
        start_memory = self._get_memory_usage()
        result = await super().process_task(task)
        end_memory = self._get_memory_usage()
        
        # Log resource usage for optimization
        self._log_resource_usage(task.task_id, end_memory - start_memory)
        
        return result
    
    def _check_resource_availability(self) -> bool:
        """Check if agent has sufficient resources"""
        memory_usage = self._get_memory_usage_percent()
        cpu_usage = self._get_cpu_usage_percent()
        
        return (memory_usage < self.memory_threshold * 100 and 
                cpu_usage < 90 and
                self.get_active_task_count() < self.task_queue_size)
```

#### 2. CRDT Optimization
```python
# Optimized CRDT usage for agents
class CRDTOptimizedAgent(BaseAgent):
    """Agent with optimized CRDT operations"""
    
    def __init__(self, config):
        super().__init__(config)
        self.crdt_batch_size = 100  # Batch CRDT operations
        self.sync_interval = 30     # Sync every 30 seconds
        self.pending_operations = []
    
    def record_task_completion(self, task_id: str, result: Dict[str, Any]):
        """Record task completion with batched CRDT operations"""
        # Add to pending operations instead of immediate CRDT update
        self.pending_operations.append({
            "type": "task_completion",
            "task_id": task_id,
            "result": result,
            "timestamp": time.time()
        })
        
        # Flush if batch size reached
        if len(self.pending_operations) >= self.crdt_batch_size:
            self._flush_crdt_operations()
    
    def _flush_crdt_operations(self):
        """Flush pending CRDT operations in batch"""
        if not self.pending_operations:
            return
        
        # Batch update CRDT state
        task_counter = self.crdt_manager.get_counter(f"agent_{self.agent_id}_tasks")
        results_set = self.crdt_manager.get_set(f"agent_{self.agent_id}_results")
        
        # Process all pending operations
        for operation in self.pending_operations:
            if operation["type"] == "task_completion":
                task_counter.increment(1)
                result_id = f"result_{operation['task_id']}_{int(operation['timestamp'])}"
                results_set.add(result_id)
        
        # Clear pending operations
        self.pending_operations.clear()
        
        self.logger.debug(f"Flushed {len(self.pending_operations)} CRDT operations")
```

### Deployment Best Practices

#### 1. Gradual Rollout Strategy
```bash
#!/bin/bash
# gradual_deployment.sh - Gradual agent deployment

# Phase 1: Deploy to 10% of nodes
echo "Phase 1: Deploying to 10% of nodes..."
python agent_launcher.py deploy \
  --config config/agents/new_agent.yaml \
  --percentage 10 \
  --canary-mode

# Monitor for 10 minutes
sleep 600

# Check health and performance
health_score=$(python agent_launcher.py health-check --percentage 10 --format json | jq '.avg_health_score')

if (( $(echo "$health_score > 80" | bc -l) )); then
    echo "Phase 1 successful, proceeding to Phase 2..."
    
    # Phase 2: Deploy to 50% of nodes
    python agent_launcher.py deploy \
      --config config/agents/new_agent.yaml \
      --percentage 50
    
    sleep 600
    
    # Final deployment to all nodes
    python agent_launcher.py deploy \
      --config config/agents/new_agent.yaml \
      --percentage 100
else
    echo "Phase 1 failed, rolling back..."
    python agent_launcher.py rollback --percentage 10
fi
```

#### 2. Configuration Management
```yaml
# config/deployment/environments.yaml
environments:
  development:
    agent_defaults:
      memory_limit: "1Gi"
      cpu_limit: "500m"
      replicas: 1
      monitoring_enabled: true
      debug_mode: true
    
  staging:
    agent_defaults:
      memory_limit: "2Gi"
      cpu_limit: "1000m"
      replicas: 2
      monitoring_enabled: true
      debug_mode: false
    
  production:
    agent_defaults:
      memory_limit: "4Gi"
      cpu_limit: "2000m"
      replicas: 3
      monitoring_enabled: true
      debug_mode: false
      backup_enabled: true
      metrics_retention_days: 30
```

---

*This agent deployment guide provides comprehensive instructions for deploying, managing, and monitoring AI agents in the Jarvis V0.19 distributed system.*