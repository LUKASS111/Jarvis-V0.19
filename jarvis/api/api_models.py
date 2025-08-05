"""
API Data Models for Jarvis Production API
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Union
from datetime import datetime
from enum import Enum

class RequestType(Enum):
    """Types of API requests"""
    CHAT = "chat"
    MEMORY_STORE = "memory_store"
    MEMORY_RECALL = "memory_recall"
    FILE_PROCESS = "file_process"
    AGENT_TASK = "agent_task"
    SYSTEM_STATUS = "system_status"
    CONFIGURATION = "configuration"

class ResponseStatus(Enum):
    """Response status types"""
    SUCCESS = "success"
    ERROR = "error"
    PARTIAL = "partial"
    PROCESSING = "processing"

@dataclass
class APIRequest:
    """Base API request structure"""
    request_type: RequestType
    request_id: str = field(default_factory=lambda: str(datetime.now().timestamp()))
    data: Dict[str, Any] = field(default_factory=dict)
    metadata: Dict[str, Any] = field(default_factory=dict)
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class APIResponse:
    """Base API response structure"""
    request_id: str
    status: ResponseStatus
    data: Dict[str, Any] = field(default_factory=dict)
    message: str = ""
    error_details: Optional[str] = None
    execution_time: float = 0.0
    timestamp: datetime = field(default_factory=datetime.now)

@dataclass
class ChatRequest:
    """Chat request with model selection and context"""
    message: str
    model: str = "llama3:8b"
    context: List[Dict[str, str]] = field(default_factory=list)
    temperature: float = 0.7
    max_tokens: Optional[int] = None
    stream: bool = False

@dataclass
class ChatResponse:
    """Chat response with conversation context"""
    response: str
    model_used: str
    tokens_used: Optional[int] = None
    conversation_id: Optional[str] = None
    context_updated: bool = False

@dataclass
class MemoryRequest:
    """Memory operations request"""
    operation: str  # "store", "recall", "search", "delete"
    key: Optional[str] = None
    value: Optional[str] = None
    query: Optional[str] = None
    filters: Dict[str, Any] = field(default_factory=dict)

@dataclass
class MemoryResponse:
    """Memory operations response"""
    operation: str
    success: bool
    data: Any = None
    affected_keys: List[str] = field(default_factory=list)

@dataclass
class FileProcessRequest:
    """File processing request"""
    file_path: str
    processor_type: str  # "auto", "txt", "pdf", "excel"
    output_format: str = "agent"  # "agent", "memory", "raw"
    options: Dict[str, Any] = field(default_factory=dict)

@dataclass
class FileProcessResponse:
    """File processing response"""
    file_path: str
    processor_used: str
    content_summary: str
    structured_data: Dict[str, Any] = field(default_factory=dict)
    processing_time: float = 0.0

@dataclass
class AgentTaskRequest:
    """Agent task execution request"""
    task_type: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    priority: int = 1
    timeout: Optional[int] = None
    async_execution: bool = False

@dataclass
class AgentTaskResponse:
    """Agent task execution response"""
    task_id: str
    task_type: str
    status: str  # "completed", "running", "failed", "queued"
    result: Any = None
    progress: float = 0.0
    estimated_completion: Optional[datetime] = None

@dataclass
class SystemStatusRequest:
    """System status request"""
    include_performance: bool = True
    include_health: bool = True
    include_resources: bool = True
    detailed: bool = False

@dataclass
class SystemStatusResponse:
    """System status response"""
    health_score: int
    performance_metrics: Dict[str, Any] = field(default_factory=dict)
    resource_usage: Dict[str, Any] = field(default_factory=dict)
    active_tasks: int = 0
    system_uptime: float = 0.0
    last_update: datetime = field(default_factory=datetime.now)