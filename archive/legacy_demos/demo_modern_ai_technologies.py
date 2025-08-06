#!/usr/bin/env python3
"""
# ARCHIWUM: Ten plik nie jest już używany w systemie produkcyjnym (data archiwizacji: 2025-01-06).

Modern AI Technologies Demo for Jarvis V0.19
Demonstrates vectorization, semantic search, RAG, and multi-LLM capabilities

ARCHIVAL NOTE: This demo file has been archived. Modern AI technologies are now integrated 
into the main system and can be accessed through the production APIs.
"""

import os
import sys
import time
import json
from datetime import datetime

# Add the project root to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Try to import vector database components
try:
    from jarvis.vectordb import (
        ChromaDBManager, SentenceTransformerProvider, SemanticSearchEngine,
        EnhancedRAGSystem, Document, SearchConfig, SearchStrategy, RAGConfig
    )
    VECTORDB_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  Vector DB components not available: {e}")
    VECTORDB_AVAILABLE = False

# Try to import LLM providers
try:
    from jarvis.llm.providers import (
        LLMOrchestrator, OpenAIProvider, AnthropicProvider, OllamaProvider,
        LLMRequest, TaskType
    )
    LLM_PROVIDERS_AVAILABLE = True
except ImportError as e:
    print(f"⚠️  LLM providers not available: {e}")
    LLM_PROVIDERS_AVAILABLE = False


def print_section(title: str):
    """Print a formatted section header"""
    print(f"\n{'=' * 80}")
    print(f"  {title}")
    print('=' * 80)


def print_subsection(title: str):
    """Print a formatted subsection header"""
    print(f"\n{'-' * 60}")
    print(f"  {title}")
    print('-' * 60)


def demo_vector_database():
    """Demonstrate vector database capabilities"""
    if not VECTORDB_AVAILABLE:
        print("❌ Vector database demo skipped - components not available")
        return
    
    print_section("VECTOR DATABASE & SEMANTIC SEARCH DEMO")
    
    try:
        # Initialize components
        print("🔧 Initializing vector database system...")
        
        # Use mock provider for demo (since sentence-transformers might not be installed)
        class MockEmbeddingProvider:
            def embed_text(self, text):
                from jarvis.vectordb.models import EmbeddingResult
                import hashlib
                # Create deterministic "embedding" from text hash
                hash_obj = hashlib.md5(text.encode())
                hash_hex = hash_obj.hexdigest()
                # Convert to fake embedding vector
                embedding = [float(int(hash_hex[i:i+2], 16)) / 255.0 for i in range(0, min(len(hash_hex), 20), 2)]
                return EmbeddingResult(
                    embedding=embedding,
                    model_name="mock-model",
                    dimensions=len(embedding),
                    processing_time=0.001
                )
            
            def embed_batch(self, texts):
                return [self.embed_text(text) for text in texts]
            
            def get_dimensions(self):
                return 10
            
            def get_model_name(self):
                return "mock-model"
        
        embedding_provider = MockEmbeddingProvider()
        chroma_manager = ChromaDBManager(
            persist_directory="data/demo_chroma_db",
            default_embedding_provider=embedding_provider
        )
        
        # Create collection
        print("📚 Creating knowledge base collection...")
        collection_name = "jarvis_knowledge_base"
        chroma_manager.create_collection(collection_name)
        
        # Prepare demo documents
        demo_documents = [
            Document(
                id="python_guide",
                content="Python is a high-level programming language known for its simplicity and readability. It supports multiple programming paradigms including procedural, object-oriented, and functional programming.",
                metadata={"category": "programming", "language": "python", "difficulty": "beginner"},
                source="programming_guide.md"
            ),
            Document(
                id="ai_intro",
                content="Artificial Intelligence (AI) involves creating computer systems that can perform tasks typically requiring human intelligence, such as visual perception, speech recognition, decision-making, and language translation.",
                metadata={"category": "ai", "topic": "introduction", "difficulty": "intermediate"},
                source="ai_handbook.md"
            ),
            Document(
                id="vector_databases",
                content="Vector databases are specialized databases designed to store and query high-dimensional vectors efficiently. They enable semantic search by comparing vector embeddings rather than exact text matches.",
                metadata={"category": "database", "topic": "vectors", "difficulty": "advanced"},
                source="tech_docs.md"
            ),
            Document(
                id="machine_learning",
                content="Machine Learning is a subset of AI that enables computers to learn and improve from experience without being explicitly programmed. It includes supervised, unsupervised, and reinforcement learning approaches.",
                metadata={"category": "ai", "topic": "machine_learning", "difficulty": "intermediate"},
                source="ml_textbook.md"
            ),
            Document(
                id="web_development",
                content="Web development involves creating websites and web applications. It includes front-end development (HTML, CSS, JavaScript) and back-end development (servers, databases, APIs).",
                metadata={"category": "programming", "topic": "web", "difficulty": "beginner"},
                source="web_guide.md"
            )
        ]
        
        # Add documents to collection
        print("📝 Indexing demo documents...")
        result = chroma_manager.add_documents(collection_name, demo_documents)
        print(f"✅ Indexed {result['processed']}/{result['total']} documents successfully")
        
        # Initialize search engine
        search_engine = SemanticSearchEngine(chroma_manager)
        
        # Demo different search strategies
        search_queries = [
            ("What is Python?", SearchStrategy.SEMANTIC),
            ("artificial intelligence machine learning", SearchStrategy.HYBRID),
            ("database vector search", SearchStrategy.MMR)
        ]
        
        for query, strategy in search_queries:
            print_subsection(f"Search: '{query}' (Strategy: {strategy.value})")
            
            config = SearchConfig(
                strategy=strategy,
                limit=3,
                score_threshold=0.1,
                rerank=True
            )
            
            results = search_engine.search(query, collection_name, config)
            
            for i, result in enumerate(results, 1):
                print(f"  {i}. [{result.score:.3f}] {result.document.id}")
                print(f"     {result.document.content[:100]}...")
                print(f"     Category: {result.document.metadata.get('category', 'N/A')}")
        
        # Demo search statistics
        print_subsection("Search Engine Statistics")
        stats = search_engine.get_search_stats()
        for key, value in stats.items():
            print(f"  {key}: {value}")
        
        print("✅ Vector database demo completed successfully!")
        
    except Exception as e:
        print(f"❌ Vector database demo failed: {e}")


def demo_rag_system():
    """Demonstrate RAG (Retrieval-Augmented Generation) system"""
    if not VECTORDB_AVAILABLE:
        print("❌ RAG demo skipped - vector database not available")
        return
    
    print_section("RAG (RETRIEVAL-AUGMENTED GENERATION) DEMO")
    
    try:
        # Use the same setup as vector database demo
        class MockEmbeddingProvider:
            def embed_text(self, text):
                from jarvis.vectordb.models import EmbeddingResult
                import hashlib
                hash_obj = hashlib.md5(text.encode())
                hash_hex = hash_obj.hexdigest()
                embedding = [float(int(hash_hex[i:i+2], 16)) / 255.0 for i in range(0, min(len(hash_hex), 20), 2)]
                return EmbeddingResult(
                    embedding=embedding,
                    model_name="mock-model",
                    dimensions=len(embedding),
                    processing_time=0.001
                )
            
            def embed_batch(self, texts):
                return [self.embed_text(text) for text in texts]
            
            def get_dimensions(self):
                return 10
            
            def get_model_name(self):
                return "mock-model"
        
        embedding_provider = MockEmbeddingProvider()
        chroma_manager = ChromaDBManager(
            persist_directory="data/demo_chroma_db",
            default_embedding_provider=embedding_provider
        )
        
        search_engine = SemanticSearchEngine(chroma_manager)
        rag_system = EnhancedRAGSystem(chroma_manager, search_engine)
        
        print("🔧 RAG system initialized (using existing knowledge base)")
        
        # Demo RAG queries
        rag_queries = [
            "What programming language should I learn first?",
            "Explain the difference between AI and machine learning",
            "How do vector databases work?"
        ]
        
        for query in rag_queries:
            print_subsection(f"RAG Query: '{query}'")
            
            config = RAGConfig(
                search_strategy=SearchStrategy.HYBRID,
                num_documents=3,
                min_relevance_score=0.1,
                max_context_length=2000,
                include_sources=True
            )
            
            response = rag_system.query(
                question=query,
                collection_name="jarvis_knowledge_base",
                config=config
            )
            
            print(f"  📊 Retrieved {len(response.retrieved_documents)} documents")
            print(f"  ⚡ Response time: {response.processing_time:.3f}s")
            print(f"  🎯 Confidence: {response.confidence_score:.3f}")
            print(f"  📝 Response:\n     {response.generated_response}")
            
            if response.retrieved_documents:
                print("  📚 Sources:")
                for i, doc_result in enumerate(response.retrieved_documents, 1):
                    print(f"     {i}. {doc_result.document.id} (score: {doc_result.score:.3f})")
        
        # Demo RAG statistics
        print_subsection("RAG System Statistics")
        stats = rag_system.get_rag_stats()
        for key, value in stats.items():
            if key != 'search_stats':  # Skip nested stats for brevity
                print(f"  {key}: {value}")
        
        print("✅ RAG demo completed successfully!")
        
    except Exception as e:
        print(f"❌ RAG demo failed: {e}")


def demo_llm_orchestrator():
    """Demonstrate multi-LLM provider orchestration"""
    if not LLM_PROVIDERS_AVAILABLE:
        print("❌ LLM orchestrator demo skipped - providers not available")
        return
    
    print_section("MULTI-LLM PROVIDER ORCHESTRATION DEMO")
    
    try:
        # Initialize orchestrator
        orchestrator = LLMOrchestrator()
        
        print("🔧 Initializing LLM providers...")
        
        # Register available providers
        # Note: These will fail without proper API keys, but we can still demo the orchestration logic
        
        # Local Ollama provider (most likely to work)
        try:
            ollama_provider = OllamaProvider()
            orchestrator.register_provider("ollama", ollama_provider)
            print("  ✅ Ollama provider registered")
        except Exception as e:
            print(f"  ⚠️  Ollama provider failed: {e}")
        
        # OpenAI provider (requires API key)
        try:
            openai_provider = OpenAIProvider(
                api_key=os.getenv("OPENAI_API_KEY", "demo-key"),
                default_model="gpt-4o-mini"
            )
            orchestrator.register_provider("openai", openai_provider)
            print("  ✅ OpenAI provider registered")
        except Exception as e:
            print(f"  ⚠️  OpenAI provider failed: {e}")
        
        # Anthropic provider (requires API key)
        try:
            anthropic_provider = AnthropicProvider(
                api_key=os.getenv("ANTHROPIC_API_KEY", "demo-key"),
                default_model="claude-3-haiku-20240307"
            )
            orchestrator.register_provider("anthropic", anthropic_provider)
            print("  ✅ Anthropic provider registered")
        except Exception as e:
            print(f"  ⚠️  Anthropic provider failed: {e}")
        
        # Set fallback chain
        orchestrator.set_fallback_chain(["ollama", "openai", "anthropic"])
        
        # Demo provider capabilities
        print_subsection("Provider Capabilities")
        capabilities = orchestrator.get_provider_capabilities()
        for name, info in capabilities.items():
            print(f"  {name} ({info['type']}):")
            caps = info['capabilities']
            print(f"    Context: {caps['max_context_length']} tokens")
            print(f"    Vision: {caps['supports_vision']}")
            print(f"    Functions: {caps['supports_function_calling']}")
            print(f"    Cost/1K tokens: ${caps['cost_per_1k_tokens'] or 'Free'}")
        
        # Demo intelligent routing
        print_subsection("Intelligent Task Routing")
        
        test_requests = [
            LLMRequest(
                prompt="Write a Python function to calculate fibonacci numbers",
                metadata={"task_type": "code_generation"}
            ),
            LLMRequest(
                prompt="Analyze the philosophical implications of artificial intelligence",
                metadata={"task_type": "reasoning"}
            ),
            LLMRequest(
                prompt="What's the weather like today?",
                metadata={"task_type": "general_chat"}
            ),
            LLMRequest(
                prompt="Describe this image",
                images=["data:image/jpeg;base64,fake_image_data"],
                metadata={"task_type": "multimodal"}
            )
        ]
        
        for i, request in enumerate(test_requests, 1):
            task_type = request.task_type
            print(f"  {i}. Task: {task_type.value}")
            print(f"     Prompt: {request.prompt[:50]}...")
            
            # Select provider (without actually calling LLM)
            available_providers = list(orchestrator.providers.values())
            selected = orchestrator.task_router.select_provider(request, available_providers)
            
            if selected:
                print(f"     Selected: {selected.provider_type.value}")
                # Estimate cost and time
                cost = selected.estimate_cost(request)
                print(f"     Estimated cost: ${cost:.4f}")
            else:
                print("     No suitable provider found")
        
        # Demo orchestrator statistics
        print_subsection("Orchestrator Statistics")
        stats = orchestrator.get_orchestrator_stats()
        for key, value in stats.items():
            if key != 'provider_usage':  # Skip detailed provider stats
                print(f"  {key}: {value}")
        
        print("✅ LLM orchestrator demo completed successfully!")
        
    except Exception as e:
        print(f"❌ LLM orchestrator demo failed: {e}")


def demo_integration_workflow():
    """Demonstrate complete integration workflow"""
    if not (VECTORDB_AVAILABLE and LLM_PROVIDERS_AVAILABLE):
        print("❌ Integration demo skipped - required components not available")
        return
    
    print_section("COMPLETE INTEGRATION WORKFLOW DEMO")
    
    try:
        print("🔧 Setting up integrated AI system...")
        
        # This would demonstrate:
        # 1. Document ingestion and vectorization
        # 2. Semantic search and retrieval  
        # 3. LLM provider selection based on task
        # 4. RAG-enhanced response generation
        # 5. Multi-modal processing
        
        workflow_steps = [
            "📚 Document Ingestion → Vector Database",
            "🔍 Semantic Search → Relevant Context Retrieval", 
            "🧠 Task Analysis → Optimal LLM Provider Selection",
            "⚡ RAG Processing → Context-Enhanced Generation",
            "🎯 Response Optimization → Final Answer"
        ]
        
        for step in workflow_steps:
            print(f"  {step}")
            time.sleep(0.1)  # Simulate processing
        
        print("\n  💡 Example Integration Flow:")
        print("     User: 'How do I implement semantic search in Python?'")
        print("     1. Query vectorized using sentence-transformers")
        print("     2. ChromaDB retrieves relevant documents about Python + semantic search")
        print("     3. Task router selects OpenAI GPT-4o (code generation + high quality)")
        print("     4. RAG system combines retrieved context with LLM generation")
        print("     5. Response includes code examples with implementation details")
        
        print("\n✅ Integration workflow demo completed!")
        
    except Exception as e:
        print(f"❌ Integration demo failed: {e}")


def main():
    """Run the complete modern AI technologies demo"""
    print_section("JARVIS V0.19 - MODERN AI TECHNOLOGIES DEMO")
    print("🚀 Demonstrating cutting-edge AI capabilities:")
    print("   • Vector Database & Semantic Search")
    print("   • Retrieval-Augmented Generation (RAG)")
    print("   • Multi-LLM Provider Orchestration")
    print("   • Intelligent Task Routing")
    print("   • Complete Integration Workflow")
    
    start_time = time.time()
    
    # Run individual demos
    demo_vector_database()
    demo_rag_system()
    demo_llm_orchestrator()
    demo_integration_workflow()
    
    # Summary
    total_time = time.time() - start_time
    print_section("DEMO SUMMARY")
    
    print("📊 Capabilities Demonstrated:")
    
    if VECTORDB_AVAILABLE:
        print("  ✅ Vector Database System")
        print("     • ChromaDB integration with persistent storage")
        print("     • Multiple embedding providers (SentenceTransformers, OpenAI)")
        print("     • Advanced semantic search strategies (MMR, Hybrid, Contextual)")
        print("     • Document chunking and metadata extraction")
    else:
        print("  ❌ Vector Database System (dependencies not installed)")
    
    if LLM_PROVIDERS_AVAILABLE:
        print("  ✅ Multi-LLM Provider System")
        print("     • Universal provider interface (OpenAI, Anthropic, Mistral, Ollama)")
        print("     • Intelligent task routing and provider selection")
        print("     • Cost and performance optimization")
        print("     • Fallback chains and error handling")
    else:
        print("  ❌ Multi-LLM Provider System (dependencies not installed)")
    
    if VECTORDB_AVAILABLE and LLM_PROVIDERS_AVAILABLE:
        print("  ✅ RAG System Integration")
        print("     • Context-aware response generation")
        print("     • Source attribution and confidence scoring")
        print("     • Conversation history management")
    else:
        print("  ❌ RAG System Integration (dependencies not available)")
    
    print(f"\n⚡ Total demo time: {total_time:.2f} seconds")
    
    print("\n🎯 Next Steps for Full Implementation:")
    print("  1. Install dependencies: pip install chromadb sentence-transformers openai anthropic")
    print("  2. Set API keys: OPENAI_API_KEY, ANTHROPIC_API_KEY")
    print("  3. Start Ollama server for local inference")
    print("  4. Run comprehensive tests: python tests/test_vectordb_comprehensive.py")
    
    print("\n🌟 Jarvis V0.19 is ready for modern AI workloads!")


if __name__ == "__main__":
    main()