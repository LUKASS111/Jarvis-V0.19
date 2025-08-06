"""
Data models for vector database operations
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Document:
    """Document to be embedded and stored in vector database"""
    id: str
    content: str
    metadata: Dict[str, Any] = None
    source: str = ""
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
        if self.timestamp is None:
            self.timestamp = datetime.now()


@dataclass
class SearchResult:
    """Result from semantic search operation"""
    document: Document
    score: float
    distance: float
    rank: int
    
    @property
    def relevance_percentage(self) -> float:
        """Convert distance to relevance percentage"""
        return max(0, (1 - self.distance) * 100)


@dataclass
class EmbeddingResult:
    """Result from embedding generation"""
    embedding: List[float]
    model_name: str
    dimensions: int
    processing_time: float
    
    @property
    def vector_magnitude(self) -> float:
        """Calculate L2 norm of embedding vector"""
        return sum(x**2 for x in self.embedding) ** 0.5


@dataclass
class RAGResponse:
    """Response from Retrieval-Augmented Generation"""
    query: str
    generated_response: str
    retrieved_documents: List[SearchResult]
    confidence_score: float
    processing_time: float
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}
    
    @property
    def source_count(self) -> int:
        """Number of source documents used"""
        return len(self.retrieved_documents)
    
    @property
    def average_relevance(self) -> float:
        """Average relevance of retrieved documents"""
        if not self.retrieved_documents:
            return 0.0
        return sum(doc.relevance_percentage for doc in self.retrieved_documents) / len(self.retrieved_documents)


@dataclass
class CollectionStats:
    """Statistics for a vector collection"""
    name: str
    document_count: int
    total_size_bytes: int
    embedding_dimensions: int
    created_at: datetime
    last_updated: datetime
    
    @property
    def average_document_size(self) -> float:
        """Average document size in bytes"""
        return self.total_size_bytes / max(1, self.document_count)


@dataclass 
class QueryConfig:
    """Configuration for semantic search queries"""
    collection_name: str
    limit: int = 10
    include_metadata: bool = True
    include_embeddings: bool = False
    where_filters: Dict[str, Any] = None
    score_threshold: float = 0.0
    
    def __post_init__(self):
        if self.where_filters is None:
            self.where_filters = {}