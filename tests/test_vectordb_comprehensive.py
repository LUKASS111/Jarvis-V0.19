"""
Comprehensive tests for Vector Database and RAG functionality
"""

import os
import time
import tempfile
import shutil
from datetime import datetime
from typing import List

# Test framework
import unittest
from unittest.mock import Mock, patch, MagicMock

# System under test
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from jarvis.vectordb import (
        ChromaDBManager, EmbeddingProvider, SentenceTransformerProvider,
        SemanticSearchEngine, EnhancedRAGSystem, Document, SearchResult,
        EmbeddingResult, RAGResponse
    )
    from jarvis.vectordb.semantic_search import SearchStrategy, SearchConfig
    from jarvis.vectordb.rag_system import RAGConfig, DocumentProcessor
    VECTORDB_AVAILABLE = True
except ImportError as e:
    print(f"Vector DB modules not available: {e}")
    VECTORDB_AVAILABLE = False


class TestDocument(unittest.TestCase):
    """Test Document model"""
    
    def test_document_creation(self):
        """Test basic document creation"""
        if not VECTORDB_AVAILABLE:
            self.skipTest("Vector DB not available")
            
        doc = Document(
            id="test_1",
            content="This is a test document",
            metadata={"category": "test"},
            source="test_source"
        )
        
        self.assertEqual(doc.id, "test_1")
        self.assertEqual(doc.content, "This is a test document")
        self.assertEqual(doc.metadata["category"], "test")
        self.assertEqual(doc.source, "test_source")
        self.assertIsInstance(doc.timestamp, datetime)
    
    def test_document_default_values(self):
        """Test document with default values"""
        if not VECTORDB_AVAILABLE:
            self.skipTest("Vector DB not available")
            
        doc = Document(id="test_2", content="Test content")
        
        self.assertEqual(doc.metadata, {})
        self.assertEqual(doc.source, "")
        self.assertIsInstance(doc.timestamp, datetime)


class TestEmbeddingProviders(unittest.TestCase):
    """Test embedding providers"""
    
    @patch('jarvis.vectordb.embedding_providers.SentenceTransformer')
    def test_sentence_transformer_provider(self, mock_st):
        """Test SentenceTransformer provider"""
        if not VECTORDB_AVAILABLE:
            self.skipTest("Vector DB not available")
            
        # Mock the model
        mock_model = Mock()
        mock_model.encode.return_value = [0.1, 0.2, 0.3, 0.4]
        mock_model.get_sentence_embedding_dimension.return_value = 4
        mock_st.return_value = mock_model
        
        provider = SentenceTransformerProvider("test-model")
        result = provider.embed_text("test text")
        
        self.assertIsInstance(result, EmbeddingResult)
        self.assertEqual(result.embedding, [0.1, 0.2, 0.3, 0.4])
        self.assertEqual(result.dimensions, 4)
        self.assertEqual(result.model_name, "test-model")
        self.assertGreater(result.processing_time, 0)
    
    @patch('jarvis.vectordb.embedding_providers.SentenceTransformer')
    def test_batch_embedding(self, mock_st):
        """Test batch embedding generation"""
        if not VECTORDB_AVAILABLE:
            self.skipTest("Vector DB not available")
            
        # Mock the model
        mock_model = Mock()
        mock_model.encode.return_value = [[0.1, 0.2], [0.3, 0.4]]
        mock_model.get_sentence_embedding_dimension.return_value = 2
        mock_st.return_value = mock_model
        
        provider = SentenceTransformerProvider("test-model")
        results = provider.embed_batch(["text1", "text2"])
        
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0].embedding, [0.1, 0.2])
        self.assertEqual(results[1].embedding, [0.3, 0.4])
    
    def test_embedding_result_properties(self):
        """Test EmbeddingResult properties"""
        if not VECTORDB_AVAILABLE:
            self.skipTest("Vector DB not available")
            
        result = EmbeddingResult(
            embedding=[0.3, 0.4],
            model_name="test",
            dimensions=2,
            processing_time=0.1
        )
        
        # Test vector magnitude calculation
        expected_magnitude = (0.3**2 + 0.4**2)**0.5
        self.assertAlmostEqual(result.vector_magnitude, expected_magnitude, places=5)


class TestDocumentProcessor(unittest.TestCase):
    """Test document processing utilities"""
    
    def test_chunk_document(self):
        """Test document chunking"""
        if not VECTORDB_AVAILABLE:
            self.skipTest("Vector DB not available")
            
        # Create a long document
        long_content = "This is sentence one. " * 100  # About 2300 chars
        doc = Document(
            id="long_doc",
            content=long_content,
            metadata={"type": "long"}
        )
        
        chunks = DocumentProcessor.chunk_document(doc, chunk_size=500, overlap=100)
        
        # Should create multiple chunks
        self.assertGreater(len(chunks), 1)
        
        # Check chunk properties
        for i, chunk in enumerate(chunks):
            self.assertTrue(chunk.id.startswith("long_doc_chunk_"))
            self.assertEqual(chunk.metadata["parent_document_id"], "long_doc")
            self.assertEqual(chunk.metadata["chunk_id"], i)
            self.assertLessEqual(len(chunk.content), 600)  # chunk_size + some flexibility
    
    def test_extract_metadata(self):
        """Test metadata extraction"""
        if not VECTORDB_AVAILABLE:
            self.skipTest("Vector DB not available")
            
        doc = Document(
            id="code_doc",
            content="def hello():\n    print('Hello, world!')\n\nThis is Python code."
        )
        
        metadata = DocumentProcessor.extract_metadata(doc)
        
        self.assertIn('word_count', metadata)
        self.assertIn('char_count', metadata)
        self.assertTrue(metadata['has_code'])
        self.assertIn('python', metadata['language_hints'])


class MockChromaDB:
    """Mock ChromaDB for testing"""
    
    def __init__(self):
        self.collections = {}
        self.data = {}
    
    def create_collection(self, name, embedding_function=None, metadata=None):
        collection = MockCollection(name, embedding_function)
        self.collections[name] = collection
        self.data[name] = {'documents': [], 'embeddings': [], 'metadatas': [], 'ids': []}
        return collection
    
    def get_collection(self, name):
        return self.collections.get(name)
    
    def list_collections(self):
        return [Mock(name=name) for name in self.collections.keys()]
    
    def delete_collection(self, name):
        if name in self.collections:
            del self.collections[name]
            del self.data[name]


class MockCollection:
    """Mock ChromaDB collection"""
    
    def __init__(self, name, embedding_function=None):
        self.name = name
        self.embedding_function = embedding_function
        self.data = {'documents': [], 'embeddings': [], 'metadatas': [], 'ids': []}
    
    def add(self, ids, documents, metadatas=None):
        self.data['ids'].extend(ids)
        self.data['documents'].extend(documents)
        self.data['metadatas'].extend(metadatas or [{}] * len(ids))
        
        # Generate mock embeddings
        if self.embedding_function:
            embeddings = self.embedding_function(documents)
            self.data['embeddings'].extend(embeddings)
    
    def query(self, query_embeddings, n_results=10, include=None, where=None):
        # Simple mock: return first n_results
        num_docs = len(self.data['documents'])
        limit = min(n_results, num_docs)
        
        result = {
            'ids': [self.data['ids'][:limit]],
            'documents': [self.data['documents'][:limit]],
            'metadatas': [self.data['metadatas'][:limit]],
            'distances': [[0.1 * i for i in range(limit)]]  # Mock distances
        }
        
        return result
    
    def count(self):
        return len(self.data['documents'])
    
    def update(self, ids, documents=None, metadatas=None):
        # Simple mock update
        for i, doc_id in enumerate(ids):
            if doc_id in self.data['ids']:
                idx = self.data['ids'].index(doc_id)
                if documents:
                    self.data['documents'][idx] = documents[i]
                if metadatas:
                    self.data['metadatas'][idx] = metadatas[i]
    
    def delete(self, ids):
        for doc_id in ids:
            if doc_id in self.data['ids']:
                idx = self.data['ids'].index(doc_id)
                del self.data['ids'][idx]
                del self.data['documents'][idx]
                del self.data['metadatas'][idx]
                if self.data['embeddings']:
                    del self.data['embeddings'][idx]


class TestChromaDBManager(unittest.TestCase):
    """Test ChromaDBManager"""
    
    def setUp(self):
        """Set up test environment"""
        if not VECTORDB_AVAILABLE:
            self.skipTest("Vector DB not available")
            
        self.temp_dir = tempfile.mkdtemp()
        self.mock_provider = Mock(spec=EmbeddingProvider)
        self.mock_provider.embed_text.return_value = EmbeddingResult(
            embedding=[0.1, 0.2, 0.3],
            model_name="test",
            dimensions=3,
            processing_time=0.01
        )
        self.mock_provider.get_dimensions.return_value = 3
        self.mock_provider.get_model_name.return_value = "test-model"
    
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('jarvis.vectordb.chroma_manager.chromadb')
    def test_create_collection(self, mock_chromadb):
        """Test collection creation"""
        # Set up mock
        mock_client = MockChromaDB()
        mock_chromadb.PersistentClient.return_value = mock_client
        
        manager = ChromaDBManager(
            persist_directory=self.temp_dir,
            default_embedding_provider=self.mock_provider
        )
        
        success = manager.create_collection("test_collection")
        
        self.assertTrue(success)
        self.assertIn("test_collection", manager._collections)
    
    @patch('jarvis.vectordb.chroma_manager.chromadb')
    def test_add_documents(self, mock_chromadb):
        """Test adding documents to collection"""
        # Set up mock
        mock_client = MockChromaDB()
        mock_chromadb.PersistentClient.return_value = mock_client
        
        manager = ChromaDBManager(
            persist_directory=self.temp_dir,
            default_embedding_provider=self.mock_provider
        )
        
        # Create collection first
        manager.create_collection("test_collection")
        
        # Add documents
        documents = [
            Document(id="doc1", content="Test document 1"),
            Document(id="doc2", content="Test document 2")
        ]
        
        result = manager.add_documents("test_collection", documents)
        
        self.assertTrue(result['success'])
        self.assertEqual(result['processed'], 2)
        self.assertEqual(result['total'], 2)
    
    @patch('jarvis.vectordb.chroma_manager.chromadb')
    def test_semantic_search(self, mock_chromadb):
        """Test semantic search"""
        # Set up mock
        mock_client = MockChromaDB()
        mock_chromadb.PersistentClient.return_value = mock_client
        
        manager = ChromaDBManager(
            persist_directory=self.temp_dir,
            default_embedding_provider=self.mock_provider
        )
        
        # Create collection and add documents
        manager.create_collection("test_collection")
        
        from jarvis.vectordb.models import QueryConfig
        query_config = QueryConfig(
            collection_name="test_collection",
            query="test query",
            limit=5
        )
        
        # Add some test data to mock
        collection = mock_client.get_collection("test_collection")
        collection.add(
            ids=["doc1", "doc2"],
            documents=["Test document 1", "Test document 2"],
            metadatas=[{"type": "test"}, {"type": "test"}]
        )
        
        results = manager.semantic_search(query_config)
        
        self.assertIsInstance(results, list)
        # Results depend on mock implementation


class TestSemanticSearchEngine(unittest.TestCase):
    """Test Semantic Search Engine"""
    
    def setUp(self):
        """Set up test environment"""
        if not VECTORDB_AVAILABLE:
            self.skipTest("Vector DB not available")
            
        self.temp_dir = tempfile.mkdtemp()
        self.mock_provider = Mock(spec=EmbeddingProvider)
        self.mock_provider.embed_text.return_value = EmbeddingResult(
            embedding=[0.1, 0.2, 0.3],
            model_name="test",
            dimensions=3,
            processing_time=0.01
        )
    
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('jarvis.vectordb.chroma_manager.chromadb')
    def test_search_strategies(self, mock_chromadb):
        """Test different search strategies"""
        # Set up mock
        mock_client = MockChromaDB()
        mock_chromadb.PersistentClient.return_value = mock_client
        
        chroma_manager = ChromaDBManager(
            persist_directory=self.temp_dir,
            default_embedding_provider=self.mock_provider
        )
        
        search_engine = SemanticSearchEngine(chroma_manager)
        
        # Test each strategy
        strategies = [
            SearchStrategy.SEMANTIC,
            SearchStrategy.HYBRID,
            SearchStrategy.MMR,
            SearchStrategy.CONTEXTUAL,
            SearchStrategy.MULTI_QUERY
        ]
        
        for strategy in strategies:
            config = SearchConfig(strategy=strategy, limit=5)
            
            # This will create a collection if it doesn't exist
            chroma_manager.create_collection("test_collection")
            
            results = search_engine.search(
                query="test query",
                collection_name="test_collection",
                config=config
            )
            
            self.assertIsInstance(results, list)
    
    def test_search_config(self):
        """Test search configuration"""
        if not VECTORDB_AVAILABLE:
            self.skipTest("Vector DB not available")
            
        config = SearchConfig(
            strategy=SearchStrategy.HYBRID,
            limit=15,
            score_threshold=0.8,
            rerank=True,
            diversify=True
        )
        
        self.assertEqual(config.strategy, SearchStrategy.HYBRID)
        self.assertEqual(config.limit, 15)
        self.assertEqual(config.score_threshold, 0.8)
        self.assertTrue(config.rerank)
        self.assertTrue(config.diversify)


class TestRAGSystem(unittest.TestCase):
    """Test RAG System"""
    
    def setUp(self):
        """Set up test environment"""
        if not VECTORDB_AVAILABLE:
            self.skipTest("Vector DB not available")
            
        self.temp_dir = tempfile.mkdtemp()
        self.mock_provider = Mock(spec=EmbeddingProvider)
        self.mock_provider.embed_text.return_value = EmbeddingResult(
            embedding=[0.1, 0.2, 0.3],
            model_name="test",
            dimensions=3,
            processing_time=0.01
        )
    
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('jarvis.vectordb.chroma_manager.chromadb')
    def test_rag_query(self, mock_chromadb):
        """Test RAG query functionality"""
        # Set up mock
        mock_client = MockChromaDB()
        mock_chromadb.PersistentClient.return_value = mock_client
        
        chroma_manager = ChromaDBManager(
            persist_directory=self.temp_dir,
            default_embedding_provider=self.mock_provider
        )
        
        search_engine = SemanticSearchEngine(chroma_manager)
        rag_system = EnhancedRAGSystem(chroma_manager, search_engine)
        
        # Create collection
        chroma_manager.create_collection("test_collection")
        
        # Mock some search results
        mock_doc = Document(id="test1", content="Test content for RAG")
        mock_result = SearchResult(
            document=mock_doc,
            score=0.9,
            distance=0.1,
            rank=1
        )
        
        with patch.object(search_engine, 'search', return_value=[mock_result]):
            response = rag_system.query(
                question="What is this about?",
                collection_name="test_collection"
            )
        
        self.assertIsInstance(response, RAGResponse)
        self.assertEqual(response.query, "What is this about?")
        self.assertGreater(len(response.generated_response), 0)
        self.assertEqual(len(response.retrieved_documents), 1)
    
    def test_rag_config(self):
        """Test RAG configuration"""
        if not VECTORDB_AVAILABLE:
            self.skipTest("Vector DB not available")
            
        config = RAGConfig(
            search_strategy=SearchStrategy.HYBRID,
            max_context_length=2000,
            num_documents=8,
            min_relevance_score=0.8,
            temperature=0.5
        )
        
        self.assertEqual(config.search_strategy, SearchStrategy.HYBRID)
        self.assertEqual(config.max_context_length, 2000)
        self.assertEqual(config.num_documents, 8)
        self.assertEqual(config.min_relevance_score, 0.8)
        self.assertEqual(config.temperature, 0.5)
    
    @patch('jarvis.vectordb.chroma_manager.chromadb')
    def test_document_indexing(self, mock_chromadb):
        """Test document indexing for RAG"""
        # Set up mock
        mock_client = MockChromaDB()
        mock_chromadb.PersistentClient.return_value = mock_client
        
        chroma_manager = ChromaDBManager(
            persist_directory=self.temp_dir,
            default_embedding_provider=self.mock_provider
        )
        
        rag_system = EnhancedRAGSystem(chroma_manager)
        
        # Test documents
        documents = [
            Document(id="doc1", content="Short document"),
            Document(id="doc2", content="Very long document content " * 100)  # Will be chunked
        ]
        
        result = rag_system.index_documents(
            documents=documents,
            collection_name="test_collection",
            chunk_large_docs=True,
            chunk_size=500
        )
        
        self.assertTrue(result['success'])
        self.assertEqual(result['original_documents'], 2)
        self.assertGreater(result['processed_documents'], 2)  # Should have chunks


class TestIntegration(unittest.TestCase):
    """Integration tests for the complete vector DB system"""
    
    def setUp(self):
        """Set up test environment"""
        if not VECTORDB_AVAILABLE:
            self.skipTest("Vector DB not available")
            
        self.temp_dir = tempfile.mkdtemp()
    
    def tearDown(self):
        """Clean up test environment"""
        if hasattr(self, 'temp_dir'):
            shutil.rmtree(self.temp_dir, ignore_errors=True)
    
    @patch('jarvis.vectordb.embedding_providers.SentenceTransformer')
    @patch('jarvis.vectordb.chroma_manager.chromadb')
    def test_end_to_end_workflow(self, mock_chromadb, mock_st):
        """Test complete end-to-end workflow"""
        # Set up mocks
        mock_client = MockChromaDB()
        mock_chromadb.PersistentClient.return_value = mock_client
        
        mock_model = Mock()
        mock_model.encode.return_value = [[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]]
        mock_model.get_sentence_embedding_dimension.return_value = 3
        mock_st.return_value = mock_model
        
        # Create system components
        embedding_provider = SentenceTransformerProvider("test-model")
        chroma_manager = ChromaDBManager(
            persist_directory=self.temp_dir,
            default_embedding_provider=embedding_provider
        )
        search_engine = SemanticSearchEngine(chroma_manager)
        rag_system = EnhancedRAGSystem(chroma_manager, search_engine)
        
        # Step 1: Create collection
        success = chroma_manager.create_collection("knowledge_base")
        self.assertTrue(success)
        
        # Step 2: Index documents
        documents = [
            Document(
                id="python_basics",
                content="Python is a high-level programming language known for its simplicity.",
                metadata={"category": "programming", "language": "python"}
            ),
            Document(
                id="ai_intro",
                content="Artificial Intelligence involves creating systems that can perform tasks requiring human intelligence.",
                metadata={"category": "ai", "topic": "introduction"}
            )
        ]
        
        index_result = rag_system.index_documents(documents, "knowledge_base")
        self.assertTrue(index_result['success'])
        
        # Step 3: Perform semantic search
        search_config = SearchConfig(
            strategy=SearchStrategy.SEMANTIC,
            limit=5,
            score_threshold=0.5
        )
        
        search_results = search_engine.search(
            query="programming language",
            collection_name="knowledge_base",
            config=search_config
        )
        
        self.assertIsInstance(search_results, list)
        
        # Step 4: RAG query
        rag_config = RAGConfig(
            search_strategy=SearchStrategy.HYBRID,
            num_documents=3,
            min_relevance_score=0.5
        )
        
        with patch.object(search_engine, 'search') as mock_search:
            # Mock search results for RAG
            mock_search.return_value = [
                SearchResult(
                    document=documents[0],
                    score=0.9,
                    distance=0.1,
                    rank=1
                )
            ]
            
            rag_response = rag_system.query(
                question="What is Python?",
                collection_name="knowledge_base",
                config=rag_config
            )
        
        self.assertIsInstance(rag_response, RAGResponse)
        self.assertEqual(rag_response.query, "What is Python?")
        self.assertGreater(len(rag_response.generated_response), 0)


# Test runner function
def run_vector_db_tests():
    """Run all vector database tests"""
    if not VECTORDB_AVAILABLE:
        print("⚠️  Vector DB modules not available - skipping tests")
        return True
    
    # Create test suite
    test_classes = [
        TestDocument,
        TestEmbeddingProviders,
        TestDocumentProcessor,
        TestChromaDBManager,
        TestSemanticSearchEngine,
        TestRAGSystem,
        TestIntegration
    ]
    
    suite = unittest.TestSuite()
    
    for test_class in test_classes:
        tests = unittest.TestLoader().loadTestsFromTestCase(test_class)
        suite.addTests(tests)
    
    # Run tests
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    
    # Return success status
    return result.wasSuccessful()


if __name__ == "__main__":
    run_vector_db_tests()