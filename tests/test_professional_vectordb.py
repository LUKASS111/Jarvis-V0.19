"""
Advanced Vector Database Test Suite
Comprehensive testing for professional vector database functionality
"""

import pytest
import tempfile
import shutil
from typing import List, Dict, Any
from pathlib import Path

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

from jarvis.vectordb.models import Document, SearchResult, QueryConfig, RAGResponse
from jarvis.vectordb.semantic_search import SemanticSearchEngine, SearchConfig, SearchStrategy
from jarvis.vectordb.rag_system import EnhancedRAGSystem, RAGConfig


class MockEmbeddingProvider:
    """Professional mock embedding provider for testing"""
    
    def __init__(self, dimensions: int = 384):
        self.dimensions = dimensions
        self.model_name = "mock-professional-embeddings-v1.0"
    
    def embed_text(self, text: str):
        """Generate deterministic mock embeddings"""
        from jarvis.vectordb.models import EmbeddingResult
        import hashlib
        
        # Create deterministic embedding based on text hash
        text_hash = hashlib.md5(text.encode()).hexdigest()
        embedding = []
        
        for i in range(self.dimensions):
            # Use different parts of hash for each dimension
            hash_segment = text_hash[(i % len(text_hash))]
            value = (ord(hash_segment) - 48) / 10.0  # Normalize to 0-1
            embedding.append(value)
        
        return EmbeddingResult(
            embedding=embedding,
            model_name=self.model_name,
            dimensions=self.dimensions,
            processing_time=0.001
        )
    
    def embed_batch(self, texts: List[str]):
        """Batch embedding generation"""
        return [self.embed_text(text) for text in texts]
    
    def get_dimensions(self) -> int:
        return self.dimensions
    
    def get_model_name(self) -> str:
        return self.model_name


class TestProfessionalVectorDatabase:
    """
    Professional test suite for vector database functionality
    Testing all critical paths and edge cases
    """
    
    @pytest.fixture
    def temp_db_path(self):
        """Create temporary database path"""
        temp_dir = tempfile.mkdtemp()
        yield temp_dir
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_embedding_provider(self):
        """Create mock embedding provider"""
        return MockEmbeddingProvider(dimensions=128)
    
    @pytest.fixture
    def sample_documents(self) -> List[Document]:
        """Create sample documents for testing"""
        return [
            Document(
                id="doc_001",
                content="Python is a high-level programming language with dynamic typing and garbage collection.",
                metadata={"category": "programming", "language": "python"},
                source="programming_guide.txt"
            ),
            Document(
                id="doc_002", 
                content="Machine learning algorithms can automatically learn patterns from data without explicit programming.",
                metadata={"category": "ai", "topic": "machine_learning"},
                source="ai_handbook.pdf"
            ),
            Document(
                id="doc_003",
                content="Vector databases store and query high-dimensional embeddings for semantic search applications.",
                metadata={"category": "database", "topic": "vector_search"},
                source="database_concepts.md"
            ),
            Document(
                id="doc_004",
                content="Retrieval-Augmented Generation combines information retrieval with language model generation.",
                metadata={"category": "ai", "topic": "rag"},
                source="rag_paper.pdf"
            )
        ]
    
    @pytest.mark.skipif(not CHROMADB_AVAILABLE, reason="ChromaDB not installed")
    def test_vector_database_creation_and_operations(self, temp_db_path, mock_embedding_provider, sample_documents):
        """Test complete vector database workflow"""
        from jarvis.vectordb.chroma_manager import ChromaDBManager
        
        # Initialize ChromaDB manager
        manager = ChromaDBManager(
            persist_directory=temp_db_path,
            default_embedding_provider=mock_embedding_provider
        )
        
        collection_name = "test_professional_collection"
        
        # Test collection creation
        assert manager.create_collection(collection_name) == True
        
        # Test collection listing
        collections = manager.list_collections()
        assert collection_name in collections
        
        # Test document addition
        result = manager.add_documents(collection_name, sample_documents)
        assert result['success'] == True
        assert result['documents_added'] == len(sample_documents)
        
        # Test semantic search
        query_config = QueryConfig(
            collection_name=collection_name,
            query="machine learning algorithms",
            limit=2,
            score_threshold=0.0
        )
        
        search_results = manager.semantic_search(query_config)
        assert len(search_results) <= 2
        assert all(isinstance(result, SearchResult) for result in search_results)
        
        # Verify search relevance
        if search_results:
            assert search_results[0].document.id in ["doc_002", "doc_004"]  # ML or RAG docs
    
    def test_semantic_search_engine_strategies(self, temp_db_path, mock_embedding_provider, sample_documents):
        """Test all semantic search strategies"""
        if not CHROMADB_AVAILABLE:
            pytest.skip("ChromaDB not installed")
        
        from jarvis.vectordb.chroma_manager import ChromaDBManager
        
        manager = ChromaDBManager(
            persist_directory=temp_db_path,
            default_embedding_provider=mock_embedding_provider
        )
        
        collection_name = "test_search_strategies"
        manager.create_collection(collection_name)
        manager.add_documents(collection_name, sample_documents)
        
        search_engine = SemanticSearchEngine(manager)
        
        # Test all search strategies
        strategies = [
            SearchStrategy.SEMANTIC,
            SearchStrategy.HYBRID,
            SearchStrategy.MMR,
            SearchStrategy.CONTEXTUAL
        ]
        
        for strategy in strategies:
            config = SearchConfig(
                strategy=strategy,
                limit=3,
                score_threshold=0.0
            )
            
            results = search_engine.search(
                query="programming language concepts",
                collection_name=collection_name,
                config=config
            )
            
            # Verify results structure
            assert isinstance(results, list)
            assert len(results) <= 3
            assert all(isinstance(result, SearchResult) for result in results)
    
    def test_rag_system_comprehensive(self, temp_db_path, mock_embedding_provider, sample_documents):
        """Test complete RAG system functionality"""
        if not CHROMADB_AVAILABLE:
            pytest.skip("ChromaDB not installed")
        
        from jarvis.vectordb.chroma_manager import ChromaDBManager
        
        manager = ChromaDBManager(
            persist_directory=temp_db_path,
            default_embedding_provider=mock_embedding_provider
        )
        
        collection_name = "test_rag_system"
        manager.create_collection(collection_name)
        
        search_engine = SemanticSearchEngine(manager)
        rag_system = EnhancedRAGSystem(manager, search_engine)
        
        # Test document indexing
        indexing_stats = rag_system.index_documents(
            documents=sample_documents,
            collection_name=collection_name,
            chunk_large_docs=False
        )
        
        assert indexing_stats['success'] == True
        assert indexing_stats['original_documents'] == len(sample_documents)
        
        # Test RAG query
        rag_config = RAGConfig(
            search_strategy=SearchStrategy.HYBRID,
            num_documents=2,
            min_relevance_score=0.0,
            max_context_length=1000
        )
        
        response = rag_system.query(
            question="What is machine learning?",
            collection_name=collection_name,
            config=rag_config
        )
        
        # Verify RAG response structure
        assert isinstance(response, RAGResponse)
        assert response.query == "What is machine learning?"
        assert isinstance(response.generated_response, str)
        assert len(response.generated_response) > 0
        assert response.confidence_score >= 0.0
        assert response.processing_time > 0.0
        
        # Test RAG statistics
        stats = rag_system.get_rag_stats()
        assert stats['total_queries'] == 1
        assert 'success_rate' in stats
        assert 'conversation_history_length' in stats
    
    def test_document_processing_edge_cases(self, sample_documents):
        """Test document processing edge cases"""
        from jarvis.vectordb.rag_system import DocumentProcessor
        
        # Test large document chunking
        large_doc = Document(
            id="large_doc",
            content="This is a very long document. " * 200,  # ~5000 chars
            metadata={"type": "large"},
            source="large_file.txt"
        )
        
        chunks = DocumentProcessor.chunk_document(large_doc, chunk_size=500, overlap=50)
        
        assert len(chunks) > 1
        assert all(len(chunk.content) <= 500 for chunk in chunks)
        assert all(chunk.id.startswith("large_doc_chunk_") for chunk in chunks)
        
        # Test metadata extraction
        code_doc = Document(
            id="code_doc",
            content="def hello_world():\n    print('Hello, World!')\n    return True",
            metadata={},
            source="example.py"
        )
        
        metadata = DocumentProcessor.extract_metadata(code_doc)
        assert metadata['has_code'] == True
        assert 'python' in metadata['language_hints']
        assert metadata['word_count'] > 0
    
    def test_error_handling_and_resilience(self, temp_db_path, mock_embedding_provider):
        """Test error handling and system resilience"""
        if not CHROMADB_AVAILABLE:
            pytest.skip("ChromaDB not installed")
        
        from jarvis.vectordb.chroma_manager import ChromaDBManager
        
        manager = ChromaDBManager(
            persist_directory=temp_db_path,
            default_embedding_provider=mock_embedding_provider
        )
        
        # Test search on non-existent collection
        query_config = QueryConfig(
            collection_name="nonexistent_collection",
            query="test query",
            limit=5
        )
        
        results = manager.semantic_search(query_config)
        assert results == []  # Should return empty list, not crash
        
        # Test RAG query on non-existent collection
        search_engine = SemanticSearchEngine(manager)
        rag_system = EnhancedRAGSystem(manager, search_engine)
        
        response = rag_system.query(
            question="test question",
            collection_name="nonexistent_collection"
        )
        
        assert isinstance(response, RAGResponse)
        assert "couldn't find" in response.generated_response.lower()
        assert response.confidence_score == 0.0
    
    def test_performance_benchmarks(self, temp_db_path, mock_embedding_provider):
        """Test performance benchmarks for professional standards"""
        if not CHROMADB_AVAILABLE:
            pytest.skip("ChromaDB not installed")
        
        import time
        from jarvis.vectordb.chroma_manager import ChromaDBManager
        
        manager = ChromaDBManager(
            persist_directory=temp_db_path,
            default_embedding_provider=mock_embedding_provider
        )
        
        collection_name = "performance_test"
        manager.create_collection(collection_name)
        
        # Generate larger dataset for performance testing
        performance_docs = []
        for i in range(50):  # 50 documents for performance test
            doc = Document(
                id=f"perf_doc_{i:03d}",
                content=f"Performance test document {i} with varied content about topic {i % 5}. " * 10,
                metadata={"index": i, "category": f"cat_{i % 5}"},
                source=f"perf_file_{i}.txt"
            )
            performance_docs.append(doc)
        
        # Test document addition performance
        start_time = time.time()
        result = manager.add_documents(collection_name, performance_docs)
        add_time = time.time() - start_time
        
        assert result['success'] == True
        assert add_time < 5.0  # Should complete within 5 seconds
        
        # Test search performance
        query_config = QueryConfig(
            collection_name=collection_name,
            query="performance test content",
            limit=10
        )
        
        start_time = time.time()
        search_results = manager.semantic_search(query_config)
        search_time = time.time() - start_time
        
        assert len(search_results) <= 10
        assert search_time < 1.0  # Should complete within 1 second
        
        # Log performance metrics for monitoring
        print(f"\n📊 Performance Metrics:")
        print(f"  Document Addition: {add_time:.3f}s for {len(performance_docs)} docs")
        print(f"  Search Performance: {search_time:.3f}s for 10 results")
        print(f"  Throughput: {len(performance_docs)/add_time:.1f} docs/sec")


def run_professional_vectordb_tests():
    """
    Run comprehensive professional vector database tests
    """
    print("="*80)
    print("  PROFESSIONAL VECTOR DATABASE TEST SUITE")
    print("="*80)
    
    if not CHROMADB_AVAILABLE:
        print("⚠️  ChromaDB not installed - running mock tests only")
        print("📦 Install with: pip install chromadb")
        return False
    
    print("🧪 Running comprehensive vector database tests...")
    
    # Run pytest with verbose output
    import subprocess
    result = subprocess.run([
        "python", "-m", "pytest", __file__, "-v", "--tb=short"
    ], capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ All vector database tests passed!")
        print("🎯 System ready for production vector database operations")
        return True
    else:
        print("❌ Some tests failed:")
        print(result.stdout)
        print(result.stderr)
        return False


if __name__ == "__main__":
    success = run_professional_vectordb_tests()
    exit(0 if success else 1)