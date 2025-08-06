"""
Basic Vector Database and Modern AI Integration Tests
"""

import unittest
import tempfile
import shutil
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class TestVectorDBIntegration(unittest.TestCase):
    """Test vector database integration"""
    
    def test_imports(self):
        """Test that all vector DB components can be imported"""
        try:
            from jarvis.vectordb import (
                Document, SearchConfig, SearchStrategy, RAGConfig,
                ChromaDBManager, SemanticSearchEngine, EnhancedRAGSystem
            )
            from jarvis.llm.providers import (
                LLMRequest, TaskType, LLMOrchestrator, OpenAIProvider,
                AnthropicProvider, OllamaProvider
            )
            self.assertTrue(True)  # Import successful
        except ImportError as e:
            self.fail(f"Vector DB imports failed: {e}")
    
    def test_document_creation(self):
        """Test basic document creation"""
        try:
            from jarvis.vectordb import Document
            
            doc = Document(
                id="test_doc",
                content="Test content for vector database",
                metadata={"category": "test"},
                source="test.txt"
            )
            
            self.assertEqual(doc.id, "test_doc")
            self.assertEqual(doc.content, "Test content for vector database")
            self.assertEqual(doc.metadata["category"], "test")
            
        except Exception as e:
            self.fail(f"Document creation failed: {e}")
    
    def test_search_config(self):
        """Test search configuration"""
        try:
            from jarvis.vectordb import SearchConfig, SearchStrategy
            
            config = SearchConfig(
                strategy=SearchStrategy.HYBRID,
                limit=10,
                score_threshold=0.7
            )
            
            self.assertEqual(config.strategy, SearchStrategy.HYBRID)
            self.assertEqual(config.limit, 10)
            self.assertEqual(config.score_threshold, 0.7)
            
        except Exception as e:
            self.fail(f"Search config creation failed: {e}")
    
    def test_llm_request(self):
        """Test LLM request creation"""
        try:
            from jarvis.llm.providers import LLMRequest, TaskType
            
            request = LLMRequest(
                prompt="Test prompt for LLM",
                system_prompt="You are a helpful assistant",
                temperature=0.7,
                max_tokens=512
            )
            
            self.assertEqual(request.prompt, "Test prompt for LLM")
            self.assertEqual(request.temperature, 0.7)
            self.assertIn(request.task_type, list(TaskType))
            
        except Exception as e:
            self.fail(f"LLM request creation failed: {e}")
    
    def test_orchestrator_creation(self):
        """Test LLM orchestrator creation"""
        try:
            from jarvis.llm.providers import LLMOrchestrator, OllamaProvider
            
            orchestrator = LLMOrchestrator()
            provider = OllamaProvider()
            orchestrator.register_provider("test_ollama", provider)
            
            stats = orchestrator.get_orchestrator_stats()
            self.assertEqual(stats['provider_count'], 1)
            self.assertIn("test_ollama", stats['available_providers'])
            
        except Exception as e:
            self.fail(f"Orchestrator creation failed: {e}")


def run_vectordb_integration_tests():
    """Run vector database integration tests"""
    suite = unittest.TestLoader().loadTestsFromTestCase(TestVectorDBIntegration)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_vectordb_integration_tests()
    if success:
        print("\n✅ All vector database integration tests passed!")
    else:
        print("\n❌ Some vector database integration tests failed!")
    sys.exit(0 if success else 1)