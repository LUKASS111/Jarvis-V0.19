# API Endpoints Reference

## Archive System Endpoints

### POST /archive/data
Archive a new data entry in the system.

**Request Body:**
```json
{
  "data": "Data to archive",
  "source": "data_source",
  "operation": "operation_type"
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "archive_id": "unique_id",
    "timestamp": "2025-01-06T17:00:00Z"
  }
}
```

### GET /archive/stats
Get comprehensive archive system statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_entries": 1000,
    "pending_verification": 5,
    "average_verification_score": 0.95
  }
}
```

## CRDT System Endpoints

### POST /crdt/sync
Synchronize CRDT state across nodes.

**Request Body:**
```json
{
  "node_id": "node_identifier",
  "operations": [],
  "vector_clock": {}
}
```

### GET /crdt/status
Get current CRDT system status.

**Response:**
```json
{
  "success": true,
  "data": {
    "system_status": "healthy",
    "total_crdts": 138,
    "node_id": "node_001"
  }
}
```

## Vector Database Endpoints

### POST /vector/search
Perform semantic search in vector database.

**Request Body:**
```json
{
  "query": "search query",
  "strategy": "mmr",
  "limit": 10
}
```

### POST /vector/embed
Create embeddings for text data.

**Request Body:**
```json
{
  "text": "Text to embed",
  "model": "sentence-transformers"
}
```

## Agent Workflow Endpoints

### POST /agents/workflow
Start a new agent workflow.

**Request Body:**
```json
{
  "agent_id": "agent_identifier",
  "target_cycles": 100,
  "success_threshold": 0.90
}
```

### GET /agents/status
Get current agent system status.

**Response:**
```json
{
  "success": true,
  "data": {
    "registered_agents": 5,
    "active_workflows": 2
  }
}
```

## Monitoring Endpoints

### GET /monitoring/health
Comprehensive system health check.

**Response:**
```json
{
  "success": true,
  "data": {
    "overall_health": true,
    "systems": {
      "archive": true,
      "crdt": true,
      "vector_db": true
    }
  }
}
```

### GET /monitoring/metrics
Get detailed system metrics.

**Response:**
```json
{
  "success": true,
  "data": {
    "performance": {
      "response_time": "1.2s",
      "throughput": "500 ops/sec"
    },
    "resources": {
      "memory_usage": "256MB",
      "cpu_usage": "15%"
    }
  }
}
```
