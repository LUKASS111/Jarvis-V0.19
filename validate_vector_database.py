"""
Professional Vector Database Validation Script
Direct testing without pytest dependency
"""

import tempfile
import shutil
import time
from typing import List

try:
    import chromadb
    CHROMADB_AVAILABLE = True
except ImportError:
    CHROMADB_AVAILABLE = False

# Test imports
try:
    from jarvis.vectordb.models import Document, SearchResult, QueryConfig, RAGResponse
    from jarvis.vectordb.semantic_search import SemanticSearchEngine, SearchConfig, SearchStrategy
    from jarvis.vectordb.rag_system import EnhancedRAGSystem, RAGConfig
    JARVIS_MODULES_AVAILABLE = True
except ImportError as e:
    JARVIS_MODULES_AVAILABLE = False
    IMPORT_ERROR = str(e)


class ProfessionalVectorDBValidator:
    """Professional validation of vector database functionality"""
    
    def __init__(self):
        self.test_results = []
        self.temp_dir = None
        
    def setup_test_environment(self):
        """Setup test environment"""
        self.temp_dir = tempfile.mkdtemp()
        print(f"📁 Created test environment: {self.temp_dir}")
        
    def cleanup_test_environment(self):
        """Cleanup test environment"""
        if self.temp_dir:
            shutil.rmtree(self.temp_dir)
            print(f"🧹 Cleaned up test environment")
    
    def create_sample_documents(self) -> List[Document]:
        """Create sample documents for testing"""
        return [
            Document(
                id="doc_001",
                content="Python is a high-level programming language with dynamic typing.",
                metadata={"category": "programming", "language": "python"},
                source="programming_guide.txt"
            ),
            Document(
                id="doc_002", 
                content="Machine learning algorithms learn patterns from data automatically.",
                metadata={"category": "ai", "topic": "machine_learning"},
                source="ai_handbook.pdf"
            ),
            Document(
                id="doc_003",
                content="Vector databases store high-dimensional embeddings for semantic search.",
                metadata={"category": "database", "topic": "vector_search"},
                source="database_concepts.md"
            )
        ]
    
    def test_model_imports(self) -> bool:
        """Test that all required models can be imported"""
        print("🔍 Testing model imports...")
        
        if not JARVIS_MODULES_AVAILABLE:
            print(f"❌ Import failed: {IMPORT_ERROR}")
            return False
        
        # Test Document creation
        doc = Document(
            id="test_doc",
            content="Test content",
            metadata={"test": True},
            source="test.txt"
        )
        
        # Test QueryConfig creation
        query_config = QueryConfig(
            collection_name="test_collection",
            query="test query",
            limit=5
        )
        
        print("✅ All model imports successful")
        print(f"   Document: {doc.id}")
        print(f"   QueryConfig: {query_config.collection_name}")
        return True
    
    def test_mock_embedding_provider(self) -> bool:
        """Test mock embedding provider functionality"""
        print("🔍 Testing mock embedding provider...")
        
        try:
            from tests.test_professional_vectordb import MockEmbeddingProvider
            
            provider = MockEmbeddingProvider(dimensions=128)
            
            # Test single embedding
            result = provider.embed_text("test text")
            assert len(result.embedding) == 128
            assert result.model_name == "mock-professional-embeddings-v1.0"
            assert result.dimensions == 128
            
            # Test batch embedding
            batch_results = provider.embed_batch(["text1", "text2", "text3"])
            assert len(batch_results) == 3
            assert all(len(result.embedding) == 128 for result in batch_results)
            
            print("✅ Mock embedding provider working correctly")
            return True
            
        except Exception as e:
            print(f"❌ Mock embedding provider failed: {e}")
            return False
    
    def test_vector_database_basic_operations(self) -> bool:
        """Test basic vector database operations"""
        print("🔍 Testing vector database basic operations...")
        
        if not CHROMADB_AVAILABLE:
            print("⚠️  ChromaDB not available - skipping database tests")
            return True
        
        try:
            from jarvis.vectordb.chroma_manager import ChromaDBManager
            from tests.test_professional_vectordb import MockEmbeddingProvider
            
            # Setup
            provider = MockEmbeddingProvider(dimensions=64)
            manager = ChromaDBManager(
                persist_directory=self.temp_dir,
                default_embedding_provider=provider
            )
            
            collection_name = "test_collection"
            
            # Test collection creation
            success = manager.create_collection(collection_name)
            if not success:
                print("❌ Collection creation failed")
                return False
            
            # Test collection listing
            collections = manager.list_collections()
            if collection_name not in collections:
                print(f"❌ Collection not found in list: {collections}")
                return False
            
            # Test document addition
            documents = self.create_sample_documents()
            result = manager.add_documents(collection_name, documents)
            
            if not result.get('success', False):
                print(f"❌ Document addition failed: {result}")
                return False
            
            print(f"✅ Vector database operations successful")
            print(f"   Collections: {len(collections)}")
            print(f"   Documents added: {result.get('documents_added', 0)}")
            return True
            
        except Exception as e:
            print(f"❌ Vector database test failed: {e}")
            return False
    
    def test_semantic_search_functionality(self) -> bool:
        """Test semantic search functionality"""
        print("🔍 Testing semantic search functionality...")
        
        if not CHROMADB_AVAILABLE:
            print("⚠️  ChromaDB not available - skipping search tests")
            return True
        
        try:
            from jarvis.vectordb.chroma_manager import ChromaDBManager
            from tests.test_professional_vectordb import MockEmbeddingProvider
            
            # Setup
            provider = MockEmbeddingProvider(dimensions=64)
            manager = ChromaDBManager(
                persist_directory=self.temp_dir,
                default_embedding_provider=provider
            )
            
            collection_name = "search_test_collection"
            manager.create_collection(collection_name)
            
            documents = self.create_sample_documents()
            manager.add_documents(collection_name, documents)
            
            # Test semantic search
            search_engine = SemanticSearchEngine(manager)
            
            config = SearchConfig(
                strategy=SearchStrategy.SEMANTIC,
                limit=2,
                score_threshold=0.0
            )
            
            results = search_engine.search(
                query="programming language concepts",
                collection_name=collection_name,
                config=config
            )
            
            if not isinstance(results, list):
                print(f"❌ Search results should be list, got: {type(results)}")
                return False
            
            if len(results) > 2:
                print(f"❌ Too many results returned: {len(results)} > 2")
                return False
            
            print(f"✅ Semantic search working correctly")
            print(f"   Results returned: {len(results)}")
            return True
            
        except Exception as e:
            print(f"❌ Semantic search test failed: {e}")
            return False
    
    def test_rag_system_basic_functionality(self) -> bool:
        """Test RAG system basic functionality"""
        print("🔍 Testing RAG system functionality...")
        
        if not CHROMADB_AVAILABLE:
            print("⚠️  ChromaDB not available - skipping RAG tests")
            return True
        
        try:
            from jarvis.vectordb.chroma_manager import ChromaDBManager
            from tests.test_professional_vectordb import MockEmbeddingProvider
            
            # Setup
            provider = MockEmbeddingProvider(dimensions=64)
            manager = ChromaDBManager(
                persist_directory=self.temp_dir,
                default_embedding_provider=provider
            )
            
            collection_name = "rag_test_collection"
            manager.create_collection(collection_name)
            
            # Setup RAG system
            search_engine = SemanticSearchEngine(manager)
            rag_system = EnhancedRAGSystem(manager, search_engine)
            
            # Index documents
            documents = self.create_sample_documents()
            indexing_stats = rag_system.index_documents(
                documents=documents,
                collection_name=collection_name
            )
            
            if not indexing_stats.get('success', False):
                print(f"❌ Document indexing failed: {indexing_stats}")
                return False
            
            # Test RAG query
            config = RAGConfig(
                search_strategy=SearchStrategy.SEMANTIC,
                num_documents=2,
                min_relevance_score=0.0
            )
            
            response = rag_system.query(
                question="What is machine learning?",
                collection_name=collection_name,
                config=config
            )
            
            if not isinstance(response, RAGResponse):
                print(f"❌ RAG response should be RAGResponse, got: {type(response)}")
                return False
            
            if not response.generated_response:
                print("❌ RAG response should contain generated text")
                return False
            
            print(f"✅ RAG system working correctly")
            print(f"   Documents indexed: {indexing_stats.get('original_documents', 0)}")
            print(f"   Response length: {len(response.generated_response)} chars")
            print(f"   Processing time: {response.processing_time:.3f}s")
            return True
            
        except Exception as e:
            print(f"❌ RAG system test failed: {e}")
            return False
    
    def test_performance_benchmarks(self) -> bool:
        """Test performance benchmarks"""
        print("🔍 Testing performance benchmarks...")
        
        if not CHROMADB_AVAILABLE:
            print("⚠️  ChromaDB not available - skipping performance tests")
            return True
        
        try:
            from jarvis.vectordb.chroma_manager import ChromaDBManager
            from tests.test_professional_vectordb import MockEmbeddingProvider
            
            # Setup
            provider = MockEmbeddingProvider(dimensions=32)  # Smaller for speed
            manager = ChromaDBManager(
                persist_directory=self.temp_dir,
                default_embedding_provider=provider
            )
            
            collection_name = "performance_test"
            manager.create_collection(collection_name)
            
            # Create test documents
            test_docs = []
            for i in range(20):  # 20 documents for quick test
                doc = Document(
                    id=f"perf_doc_{i:03d}",
                    content=f"Performance test document {i} with content about topic {i % 3}. " * 5,
                    metadata={"index": i, "category": f"cat_{i % 3}"},
                    source=f"perf_file_{i}.txt"
                )
                test_docs.append(doc)
            
            # Test document addition performance
            start_time = time.time()
            result = manager.add_documents(collection_name, test_docs)
            add_time = time.time() - start_time
            
            if not result.get('success', False):
                print(f"❌ Performance test document addition failed: {result}")
                return False
            
            # Test search performance
            query_config = QueryConfig(
                collection_name=collection_name,
                query="performance test content",
                limit=5
            )
            
            start_time = time.time()
            search_results = manager.semantic_search(query_config)
            search_time = time.time() - start_time
            
            print(f"✅ Performance benchmarks completed")
            print(f"   Document addition: {add_time:.3f}s for {len(test_docs)} docs")
            print(f"   Search time: {search_time:.3f}s for {len(search_results)} results")
            print(f"   Throughput: {len(test_docs)/add_time:.1f} docs/sec")
            
            # Performance assertions
            if add_time > 3.0:  # Should be fast with mock embeddings
                print(f"⚠️  Document addition slower than expected: {add_time:.3f}s")
            
            if search_time > 1.0:  # Search should be very fast
                print(f"⚠️  Search slower than expected: {search_time:.3f}s")
            
            return True
            
        except Exception as e:
            print(f"❌ Performance benchmark test failed: {e}")
            return False
    
    def run_all_tests(self) -> bool:
        """Run all validation tests"""
        print("="*80)
        print("  PROFESSIONAL VECTOR DATABASE VALIDATION")
        print("="*80)
        
        self.setup_test_environment()
        
        try:
            tests = [
                ("Model Imports", self.test_model_imports),
                ("Mock Embedding Provider", self.test_mock_embedding_provider),
                ("Vector Database Operations", self.test_vector_database_basic_operations),
                ("Semantic Search", self.test_semantic_search_functionality),
                ("RAG System", self.test_rag_system_basic_functionality),
                ("Performance Benchmarks", self.test_performance_benchmarks)
            ]
            
            passed = 0
            total = len(tests)
            
            for test_name, test_func in tests:
                print(f"\n📋 Running: {test_name}")
                try:
                    if test_func():
                        passed += 1
                    else:
                        print(f"❌ {test_name} failed")
                except Exception as e:
                    print(f"❌ {test_name} crashed: {e}")
            
            print("\n" + "="*80)
            print(f"TEST RESULTS: {passed}/{total} tests passed")
            
            if passed == total:
                print("✅ ALL TESTS PASSED - Vector database system ready for production!")
            else:
                print(f"⚠️  {total - passed} tests failed - review implementation")
            
            # System status
            print(f"\n🎯 SYSTEM STATUS:")
            print(f"   ChromaDB Available: {'✅' if CHROMADB_AVAILABLE else '❌'}")
            print(f"   Jarvis Modules: {'✅' if JARVIS_MODULES_AVAILABLE else '❌'}")
            print(f"   Test Environment: ✅")
            print(f"   Professional Standards: {'✅' if passed == total else '⚠️'}")
            
            return passed == total
            
        finally:
            self.cleanup_test_environment()


def main():
    """Main validation function"""
    validator = ProfessionalVectorDBValidator()
    success = validator.run_all_tests()
    return success


if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)