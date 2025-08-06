# Jarvis V0.19 Complete REST API Documentation

## 🌐 Overview

Welcome to the comprehensive REST API documentation for Jarvis V0.19 Professional AI Assistant. This API provides access to all system capabilities including distributed CRDT operations, vector database search, agent workflows, monitoring, and more.

### 🚀 Quick Start

```bash
# Health check
curl -X GET "http://localhost:8000/api/v1/health" \
  -H "Authorization: Bearer YOUR_API_KEY"

# Archive data
curl -X POST "http://localhost:8000/api/v1/archive/data" \
  -H "Authorization: Bearer YOUR_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"data": "Sample data", "source": "api", "operation": "test"}'
```

### 📊 Base Information

- **Base URL**: `http://localhost:8000/api/v1`
- **API Version**: v1.0
- **Authentication**: Bearer Token (API Key)
- **Content Type**: `application/json`
- **Rate Limit**: 1000 requests/hour per API key

---

## 🔐 Authentication

All API endpoints require authentication using an API key in the `Authorization` header:

```http
Authorization: Bearer YOUR_API_KEY
```

### Getting an API Key

Contact your system administrator or use the CLI:
```bash
jarvis-cli auth --generate-key
```

---

## 📊 System Health & Status

### GET /health
Get comprehensive system health status.

**Response:**
```json
{
  "success": true,
  "data": {
    "status": "healthy",
    "version": "0.19.0",
    "uptime": "5d 12h 30m",
    "systems": {
      "archive": true,
      "crdt": true,
      "vector_db": true,
      "agents": true,
      "monitoring": true
    },
    "performance": {
      "response_time": "1.2s",
      "throughput": "500 ops/sec",
      "memory_usage": "45%",
      "cpu_usage": "25%"
    }
  },
  "timestamp": "2025-01-06T17:00:00Z"
}
```

### GET /status
Get detailed system status and metrics.

**Response:**
```json
{
  "success": true,
  "data": {
    "architecture_health": 98,
    "test_coverage": 100,
    "active_sessions": 15,
    "total_operations": 150000,
    "error_rate": 0.001
  }
}
```

---

## 📚 Archive System API

### POST /archive/data
Archive new data entry in the system.

**Request Body:**
```json
{
  "data": "Data content to archive",
  "data_type": "user_input",
  "source": "web_app",
  "operation": "create_entry",
  "metadata": {
    "user_id": "user123",
    "category": "important"
  }
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "archive_id": "arch_2025010617001234",
    "timestamp": "2025-01-06T17:00:12Z",
    "verification_status": "pending",
    "estimated_verification_time": "30s"
  },
  "message": "Data archived successfully"
}
```

### GET /archive/stats
Get comprehensive archive system statistics.

**Response:**
```json
{
  "success": true,
  "data": {
    "total_entries": 37606,
    "pending_verification": 5,
    "average_verification_score": 0.95,
    "verification_stats": {
      "verified": 37580,
      "pending": 5,
      "failed": 21
    },
    "data_type_stats": {
      "user_input": 15000,
      "system_log": 12000,
      "api_call": 8000,
      "other": 2606
    }
  }
}
```

---

## 🔄 CRDT Operations API

### GET /crdt/status
Get CRDT system status and health metrics.

**Response:**
```json
{
  "success": true,
  "data": {
    "system_status": "healthy",
    "node_id": "node_001",
    "total_crdts": 138,
    "sync_status": "synchronized",
    "crdt_types": {
      "interaction_counter": "GCounter",
      "active_sessions": "GSet",
      "system_state": "LWWRegister"
    }
  }
}
```

### POST /crdt/sync
Synchronize CRDT state with other nodes.

**Request Body:**
```json
{
  "node_id": "node_002",
  "operations": [
    {
      "type": "increment",
      "crdt_name": "interaction_counter",
      "value": 1
    }
  ]
}
```

---

## 🧠 Vector Database API

### POST /vector/search
Perform semantic search in the vector database.

**Request Body:**
```json
{
  "query": "machine learning algorithms",
  "strategy": "mmr",
  "limit": 10,
  "include_metadata": true
}
```

**Response:**
```json
{
  "success": true,
  "data": {
    "results": [
      {
        "content": "Machine learning content...",
        "similarity_score": 0.95,
        "metadata": {
          "source": "docs",
          "category": "technical"
        }
      }
    ],
    "search_time_ms": 45
  }
}
```

### POST /vector/embed
Create embeddings for text data.

**Request Body:**
```json
{
  "texts": ["Text to embed"],
  "model": "sentence-transformers"
}
```

### GET /vector/collections
List all available vector collections.

**Response:**
```json
{
  "success": true,
  "data": {
    "collections": [
      {
        "name": "knowledge_base",
        "document_count": 5000,
        "embedding_dimension": 384
      }
    ]
  }
}
```

---

## 🤖 Agent Workflow API

### POST /agents/workflow
Start a new agent workflow.

**Request Body:**
```json
{
  "agent_id": "support_agent",
  "workflow_type": "customer_inquiry",
  "target_cycles": 100,
  "parameters": {
    "customer_id": "CUST_001",
    "priority": "high"
  }
}
```

### GET /agents/status
Get status of all agents and workflows.

**Response:**
```json
{
  "success": true,
  "data": {
    "registered_agents": 8,
    "active_workflows": 3,
    "agents": [
      {
        "agent_id": "support_agent",
        "status": "active",
        "current_workflows": 2
      }
    ]
  }
}
```

---

## 📊 Monitoring API

### GET /monitoring/metrics
Get comprehensive system metrics.

**Response:**
```json
{
  "success": true,
  "data": {
    "cpu_usage_percent": 25.5,
    "memory_usage_percent": 45.2,
    "requests_per_second": 85.2,
    "error_rate_percent": 0.1
  }
}
```

### GET /monitoring/health
Get detailed health information.

**Response:**
```json
{
  "success": true,
  "data": {
    "overall_health": "healthy",
    "components": {
      "archive_system": "healthy",
      "vector_database": "healthy",
      "crdt_system": "healthy"
    }
  }
}
```

---

## 📈 Error Handling

### Error Response Format
```json
{
  "success": false,
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Invalid request parameters"
  },
  "timestamp": "2025-01-06T17:00:00Z"
}
```

### HTTP Status Codes
- `200 OK` - Request successful
- `400 Bad Request` - Invalid parameters
- `401 Unauthorized` - Authentication required
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

---

## 🔄 Rate Limiting

API requests are rate limited:
- **Standard**: 1000 requests/hour
- **Premium**: 10000 requests/hour

---

*API Version: v1.0 | Last Updated: 2025-01-06*
