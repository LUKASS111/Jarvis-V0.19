"""
ChromaDB Manager for persistent vector storage
"""

import os
import json
import time
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Union
from pathlib import Path

from .models import Document, SearchResult, CollectionStats, QueryConfig
from .embedding_providers import EmbeddingProvider, SentenceTransformerProvider

logger = logging.getLogger(__name__)


class ChromaDBManager:
    """
    Production-ready ChromaDB integration with comprehensive error handling
    """
    
    def __init__(self, 
                 persist_directory: str = "data/chroma_db",
                 default_embedding_provider: EmbeddingProvider = None):
        """
        Initialize ChromaDB manager
        
        Args:
            persist_directory: Directory for persistent storage
            default_embedding_provider: Default embedding provider
        """
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(parents=True, exist_ok=True)
        
        self._client = None
        self._collections = {}
        
        # Default embedding provider
        if default_embedding_provider is None:
            self.default_embedding_provider = SentenceTransformerProvider()
        else:
            self.default_embedding_provider = default_embedding_provider
            
        logger.info(f"ChromaDB manager initialized with persist_directory: {persist_directory}")
    
    def _get_client(self):
        """Get ChromaDB client with lazy loading"""
        if self._client is None:
            try:
                import chromadb
                from chromadb.config import Settings
                
                self._client = chromadb.PersistentClient(
                    path=str(self.persist_directory),
                    settings=Settings(
                        anonymized_telemetry=False,
                        allow_reset=True
                    )
                )
                logger.info("ChromaDB client initialized successfully")
                
            except ImportError:
                raise ImportError("chromadb not installed. Run: pip install chromadb")
            except Exception as e:
                logger.error(f"Failed to initialize ChromaDB client: {e}")
                raise
                
        return self._client
    
    def create_collection(self, 
                         name: str, 
                         embedding_provider: EmbeddingProvider = None,
                         metadata: Dict[str, Any] = None) -> bool:
        """
        Create a new collection
        
        Args:
            name: Collection name
            embedding_provider: Custom embedding provider for this collection
            metadata: Collection metadata
            
        Returns:
            bool: Success status
        """
        try:
            client = self._get_client()
            
            # Use custom or default embedding provider
            provider = embedding_provider or self.default_embedding_provider
            
            # Create embedding function
            embedding_function = self._create_embedding_function(provider)
            
            # Create collection
            collection = client.create_collection(
                name=name,
                embedding_function=embedding_function,
                metadata=metadata or {}
            )
            
            # Cache collection and provider
            self._collections[name] = {
                'collection': collection,
                'embedding_provider': provider,
                'created_at': time.time()
            }
            
            logger.info(f"Created collection '{name}' with {provider.get_model_name()}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to create collection '{name}': {e}")
            return False
    
    def get_collection(self, name: str):
        """Get existing collection"""
        try:
            client = self._get_client()
            
            if name in self._collections:
                return self._collections[name]['collection']
            
            # Try to get existing collection
            collection = client.get_collection(name)
            
            # Cache it (without embedding provider info)
            self._collections[name] = {
                'collection': collection,
                'embedding_provider': self.default_embedding_provider,
                'created_at': time.time()
            }
            
            return collection
            
        except Exception as e:
            logger.error(f"Failed to get collection '{name}': {e}")
            return None
    
    def list_collections(self) -> List[str]:
        """List all collections"""
        try:
            client = self._get_client()
            collections = client.list_collections()
            return [col.name for col in collections]
        except Exception as e:
            logger.error(f"Failed to list collections: {e}")
            return []
    
    def delete_collection(self, name: str) -> bool:
        """Delete a collection"""
        try:
            client = self._get_client()
            client.delete_collection(name)
            
            # Remove from cache
            if name in self._collections:
                del self._collections[name]
                
            logger.info(f"Deleted collection '{name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete collection '{name}': {e}")
            return False
    
    def add_documents(self, 
                     collection_name: str, 
                     documents: List[Document],
                     batch_size: int = 100) -> Dict[str, Any]:
        """
        Add documents to collection with batch processing
        
        Args:
            collection_name: Target collection
            documents: List of documents to add
            batch_size: Batch size for processing
            
        Returns:
            Dict with processing stats
        """
        collection = self.get_collection(collection_name)
        if collection is None:
            return {'success': False, 'error': f'Collection {collection_name} not found'}
        
        start_time = time.time()
        processed = 0
        errors = 0
        
        try:
            # Process in batches
            for i in range(0, len(documents), batch_size):
                batch = documents[i:i + batch_size]
                
                # Prepare batch data
                ids = [doc.id for doc in batch]
                texts = [doc.content for doc in batch]
                metadatas = [doc.metadata for doc in batch]
                
                try:
                    collection.add(
                        ids=ids,
                        documents=texts,
                        metadatas=metadatas
                    )
                    processed += len(batch)
                    
                except Exception as e:
                    logger.error(f"Batch processing error: {e}")
                    errors += len(batch)
            
            processing_time = time.time() - start_time
            
            result = {
                'success': True,
                'processed': processed,
                'errors': errors,
                'total': len(documents),
                'processing_time': processing_time,
                'documents_per_second': processed / processing_time if processing_time > 0 else 0
            }
            
            logger.info(f"Added {processed}/{len(documents)} documents to '{collection_name}' "
                       f"in {processing_time:.2f}s ({result['documents_per_second']:.1f} docs/s)")
            
            return result
            
        except Exception as e:
            logger.error(f"Failed to add documents to '{collection_name}': {e}")
            return {'success': False, 'error': str(e)}
    
    def semantic_search(self, 
                       query_config: QueryConfig) -> List[SearchResult]:
        """
        Perform semantic search
        
        Args:
            query_config: Search configuration
            
        Returns:
            List of search results
        """
        collection = self.get_collection(query_config.collection_name)
        if collection is None:
            logger.error(f"Collection {query_config.collection_name} not found")
            return []
        
        try:
            # Get embedding provider for this collection
            provider = self._collections.get(query_config.collection_name, {}).get(
                'embedding_provider', self.default_embedding_provider
            )
            
            # Generate query embedding
            query_embedding = provider.embed_text(query_config.query).embedding
            
            # Perform search
            results = collection.query(
                query_embeddings=[query_embedding],
                n_results=query_config.limit,
                include=['documents', 'metadatas', 'distances'],
                where=query_config.where_filters if query_config.where_filters else None
            )
            
            # Convert to SearchResult objects
            search_results = []
            if results['documents'] and results['documents'][0]:
                for i, (doc_content, metadata, distance) in enumerate(zip(
                    results['documents'][0],
                    results['metadatas'][0],
                    results['distances'][0]
                )):
                    # Filter by score threshold
                    if distance > (1 - query_config.score_threshold):
                        continue
                    
                    document = Document(
                        id=results['ids'][0][i] if 'ids' in results else f"doc_{i}",
                        content=doc_content,
                        metadata=metadata or {}
                    )
                    
                    search_result = SearchResult(
                        document=document,
                        score=1 - distance,  # Convert distance to similarity score
                        distance=distance,
                        rank=i + 1
                    )
                    
                    search_results.append(search_result)
            
            logger.info(f"Found {len(search_results)} results for query in '{query_config.collection_name}'")
            return search_results
            
        except Exception as e:
            logger.error(f"Semantic search error in '{query_config.collection_name}': {e}")
            return []
    
    def get_collection_stats(self, name: str) -> Optional[CollectionStats]:
        """Get collection statistics"""
        collection = self.get_collection(name)
        if collection is None:
            return None
        
        try:
            # Get basic stats
            count = collection.count()
            
            # Estimate size (simplified)
            estimated_size = count * 1000  # Rough estimate
            
            # Get collection info
            collection_info = self._collections.get(name, {})
            created_at = collection_info.get('created_at', time.time())
            
            # Get embedding dimensions
            provider = collection_info.get('embedding_provider', self.default_embedding_provider)
            dimensions = provider.get_dimensions()
            
            return CollectionStats(
                name=name,
                document_count=count,
                total_size_bytes=estimated_size,
                embedding_dimensions=dimensions,
                created_at=datetime.fromtimestamp(created_at),
                last_updated=datetime.now()
            )
            
        except Exception as e:
            logger.error(f"Failed to get stats for collection '{name}': {e}")
            return None
    
    def _create_embedding_function(self, provider: EmbeddingProvider):
        """Create ChromaDB embedding function from provider"""
        
        class ProviderEmbeddingFunction:
            def __init__(self, embedding_provider):
                self.provider = embedding_provider
            
            def __call__(self, input_texts):
                """Generate embeddings for input texts"""
                if isinstance(input_texts, str):
                    input_texts = [input_texts]
                
                results = self.provider.embed_batch(input_texts)
                return [result.embedding for result in results]
        
        return ProviderEmbeddingFunction(provider)
    
    def update_document(self, 
                       collection_name: str, 
                       document_id: str, 
                       new_content: str = None,
                       new_metadata: Dict[str, Any] = None) -> bool:
        """Update a document in the collection"""
        collection = self.get_collection(collection_name)
        if collection is None:
            return False
        
        try:
            update_data = {}
            
            if new_content is not None:
                update_data['documents'] = [new_content]
            
            if new_metadata is not None:
                update_data['metadatas'] = [new_metadata]
            
            if update_data:
                collection.update(
                    ids=[document_id],
                    **update_data
                )
                logger.info(f"Updated document '{document_id}' in '{collection_name}'")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Failed to update document '{document_id}' in '{collection_name}': {e}")
            return False
    
    def delete_documents(self, collection_name: str, document_ids: List[str]) -> bool:
        """Delete documents from collection"""
        collection = self.get_collection(collection_name)
        if collection is None:
            return False
        
        try:
            collection.delete(ids=document_ids)
            logger.info(f"Deleted {len(document_ids)} documents from '{collection_name}'")
            return True
            
        except Exception as e:
            logger.error(f"Failed to delete documents from '{collection_name}': {e}")
            return False
    
    def reset_database(self) -> bool:
        """Reset entire database (USE WITH CAUTION)"""
        try:
            client = self._get_client()
            client.reset()
            self._collections.clear()
            logger.warning("Database reset completed")
            return True
            
        except Exception as e:
            logger.error(f"Failed to reset database: {e}")
            return False