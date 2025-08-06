"""
Vector Database Module for Jarvis V0.19
Provides semantic search, embeddings, and RAG capabilities
"""

from .chroma_manager import ChromaDBManager
from .embedding_providers import EmbeddingProvider, SentenceTransformerProvider, OpenAIEmbeddingProvider
from .semantic_search import SemanticSearchEngine, SearchConfig, SearchStrategy
from .rag_system import EnhancedRAGSystem, RAGConfig
from .models import Document, SearchResult, EmbeddingResult, RAGResponse

__all__ = [
    'ChromaDBManager',
    'EmbeddingProvider',
    'SentenceTransformerProvider', 
    'OpenAIEmbeddingProvider',
    'SemanticSearchEngine',
    'SearchConfig',
    'SearchStrategy',
    'EnhancedRAGSystem',
    'RAGConfig',
    'Document',
    'SearchResult',
    'EmbeddingResult',
    'RAGResponse'
]