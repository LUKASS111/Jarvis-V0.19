#!/usr/bin/env python3
"""
Vector Database Manager for Jarvis 1.0.0
Unified interface for vector database operations
"""

import os
import sys
from typing import Dict, List, Any, Optional, Union
from pathlib import Path

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from jarvis.core.error_handler import error_handler, ErrorLevel, safe_execute

class VectorDatabaseManager:
    """
    Unified vector database manager
    Provides high-level interface to vector database operations
    """
    
    def __init__(self):
        self.initialized = False
        self.setup_vector_database()
    
    def setup_vector_database(self):
        """Setup vector database components"""
        try:
            # Import existing vector components
            from jarvis.vectordb.semantic_search import SemanticSearchEngine
            from jarvis.vectordb.chroma_manager import ChromaDBManager
            from jarvis.vectordb.rag_system import EnhancedRAGSystem
            
            # Initialize components
            self.chroma_manager = ChromaDBManager()
            self.search_engine = SemanticSearchEngine(self.chroma_manager)
            self.rag_system = EnhancedRAGSystem()
            
            self.initialized = True
            print("[VECTOR] Vector database manager initialized successfully")
            
        except ImportError as e:
            print(f"[VECTOR] Some vector components not available: {e}")
            self.initialized = False
        except Exception as e:
            error_handler.log_error(
                e, "Vector Database Initialization", ErrorLevel.WARNING,
                "Vector database manager initialization failed"
            )
            self.initialized = False
    
    @safe_execute(fallback_value=None, context="Vector Database")
    def create_embedding(self, text: str, collection_name: str = "default") -> Dict[str, Any]:
        """Create embedding for text"""
        if not self.initialized:
            return {
                "success": False,
                "error": "Vector database not initialized"
            }
        
        try:
            # Use search engine to create embedding
            result = self.search_engine.embed_text(text)
            return {
                "success": True,
                "embedding": result,
                "text": text,
                "collection": collection_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to create embedding: {str(e)}"
            }
    
    @safe_execute(fallback_value=None, context="Vector Database")
    def semantic_search(self, query: str, collection_name: str = "default", limit: int = 5) -> Dict[str, Any]:
        """Perform semantic search"""
        if not self.initialized:
            return {
                "success": False,
                "error": "Vector database not initialized"
            }
        
        try:
            # Use search engine for semantic search
            results = self.search_engine.search(query, limit=limit)
            return {
                "success": True,
                "query": query,
                "results": results,
                "count": len(results)
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Semantic search failed: {str(e)}"
            }
    
    @safe_execute(fallback_value=None, context="Vector Database")
    def add_document(self, text: str, metadata: Dict[str, Any] = None, collection_name: str = "default") -> Dict[str, Any]:
        """Add document to vector database"""
        if not self.initialized:
            return {
                "success": False,
                "error": "Vector database not initialized"
            }
        
        try:
            # Add document through chroma manager
            doc_id = self.chroma_manager.add_document(text, metadata or {}, collection_name)
            return {
                "success": True,
                "document_id": doc_id,
                "text": text[:100] + "..." if len(text) > 100 else text,
                "collection": collection_name
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Failed to add document: {str(e)}"
            }
    
    @safe_execute(fallback_value=None, context="Vector Database")
    def get_rag_response(self, query: str, context_limit: int = 3) -> Dict[str, Any]:
        """Get RAG (Retrieval-Augmented Generation) response"""
        if not self.initialized:
            return {
                "success": False,
                "error": "Vector database not initialized"
            }
        
        try:
            # Use RAG system for enhanced response
            response = self.rag_system.generate_response(query, context_limit=context_limit)
            return {
                "success": True,
                "query": query,
                "response": response,
                "context_used": context_limit
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"RAG response failed: {str(e)}"
            }
    
    def get_status(self) -> Dict[str, Any]:
        """Get vector database status"""
        return {
            "initialized": self.initialized,
            "components": {
                "chroma_manager": hasattr(self, 'chroma_manager'),
                "search_engine": hasattr(self, 'search_engine'),
                "rag_system": hasattr(self, 'rag_system')
            }
        }