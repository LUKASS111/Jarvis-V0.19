"""
Enhanced Retrieval-Augmented Generation (RAG) System
"""

import time
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass

from .models import Document, SearchResult, RAGResponse
from .semantic_search import SemanticSearchEngine, SearchConfig, SearchStrategy
from .chroma_manager import ChromaDBManager

# Import LLM interface
try:
    from ..llm.llm_interface import get_llm_interface, LLMInterface
    LLM_AVAILABLE = True
except ImportError:
    LLM_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class RAGConfig:
    """Configuration for RAG operations"""
    search_strategy: SearchStrategy = SearchStrategy.HYBRID
    max_context_length: int = 4000
    num_documents: int = 5
    min_relevance_score: float = 0.7
    include_sources: bool = True
    temperature: float = 0.7
    max_tokens: int = 512
    system_prompt: str = ""
    use_conversation_context: bool = False


class DocumentProcessor:
    """Document processing utilities for RAG"""
    
    @staticmethod
    def chunk_document(document: Document, 
                      chunk_size: int = 1000, 
                      overlap: int = 200) -> List[Document]:
        """
        Chunk large document into smaller pieces
        
        Args:
            document: Source document
            chunk_size: Maximum chunk size in characters
            overlap: Overlap between chunks
            
        Returns:
            List of document chunks
        """
        content = document.content
        chunks = []
        
        if len(content) <= chunk_size:
            return [document]
        
        start = 0
        chunk_id = 0
        
        while start < len(content):
            end = min(start + chunk_size, len(content))
            
            # Try to break at sentence boundaries
            if end < len(content):
                # Look for sentence endings in the overlap region
                overlap_start = max(end - overlap, start)
                sentence_break = content.rfind('.', overlap_start, end)
                if sentence_break != -1 and sentence_break > start:
                    end = sentence_break + 1
            
            chunk_content = content[start:end].strip()
            
            if chunk_content:
                chunk_doc = Document(
                    id=f"{document.id}_chunk_{chunk_id}",
                    content=chunk_content,
                    metadata={
                        **document.metadata,
                        'chunk_id': chunk_id,
                        'parent_document_id': document.id,
                        'chunk_start': start,
                        'chunk_end': end
                    },
                    source=document.source,
                    timestamp=document.timestamp
                )
                chunks.append(chunk_doc)
                chunk_id += 1
            
            start = end - overlap if end < len(content) else end
        
        return chunks
    
    @staticmethod
    def extract_metadata(document: Document) -> Dict[str, Any]:
        """Extract additional metadata from document content"""
        content = document.content.lower()
        
        metadata = {
            'word_count': len(document.content.split()),
            'char_count': len(document.content),
            'has_code': any(keyword in content for keyword in ['def ', 'class ', 'import ', 'function']),
            'has_urls': 'http' in content or 'www.' in content,
            'language_hints': []
        }
        
        # Detect potential programming languages
        if 'python' in content or 'def ' in content:
            metadata['language_hints'].append('python')
        if 'javascript' in content or 'function(' in content:
            metadata['language_hints'].append('javascript')
        if 'sql' in content or 'select ' in content:
            metadata['language_hints'].append('sql')
        
        return metadata


class EnhancedRAGSystem:
    """
    Production-ready RAG system with advanced retrieval and generation
    """
    
    def __init__(self, 
                 chroma_manager: ChromaDBManager,
                 search_engine: SemanticSearchEngine = None):
        """
        Initialize RAG system
        
        Args:
            chroma_manager: ChromaDB manager instance
            search_engine: Semantic search engine (optional)
        """
        self.chroma_manager = chroma_manager
        self.search_engine = search_engine or SemanticSearchEngine(chroma_manager)
        self.conversation_history = []
        self.rag_stats = {
            'total_queries': 0,
            'successful_generations': 0,
            'average_response_time': 0.0,
            'average_context_length': 0.0
        }
        
        if not LLM_AVAILABLE:
            logger.warning("LLM interface not available. RAG responses will be context-only.")
    
    def query(self, 
              question: str,
              collection_name: str,
              config: RAGConfig = None) -> RAGResponse:
        """
        Perform RAG query with retrieval and generation
        
        Args:
            question: User question
            collection_name: Target collection for retrieval
            config: RAG configuration
            
        Returns:
            RAG response with generated answer and sources
        """
        if config is None:
            config = RAGConfig()
        
        start_time = time.time()
        self.rag_stats['total_queries'] += 1
        
        try:
            # Step 1: Retrieve relevant documents
            search_config = SearchConfig(
                strategy=config.search_strategy,
                limit=config.num_documents,
                score_threshold=config.min_relevance_score,
                rerank=True,
                diversify=True
            )
            
            retrieved_docs = self.search_engine.search(
                query=question,
                collection_name=collection_name,
                config=search_config
            )
            
            if not retrieved_docs:
                return RAGResponse(
                    query=question,
                    generated_response="I couldn't find relevant information to answer your question.",
                    retrieved_documents=[],
                    confidence_score=0.0,
                    processing_time=time.time() - start_time,
                    metadata={'error': 'No relevant documents found'}
                )
            
            # Step 2: Prepare context
            context = self._prepare_context(retrieved_docs, config)
            
            # Step 3: Generate response
            if LLM_AVAILABLE:
                response_text = self._generate_response(question, context, config)
                confidence = self._calculate_confidence(retrieved_docs, response_text)
            else:
                response_text = self._create_context_summary(context, question)
                confidence = 0.5  # Lower confidence for context-only responses
            
            # Step 4: Create response
            processing_time = time.time() - start_time
            
            rag_response = RAGResponse(
                query=question,
                generated_response=response_text,
                retrieved_documents=retrieved_docs,
                confidence_score=confidence,
                processing_time=processing_time,
                metadata={
                    'context_length': len(context),
                    'strategy_used': config.search_strategy.value,
                    'llm_available': LLM_AVAILABLE
                }
            )
            
            # Update conversation history
            if config.use_conversation_context:
                self._update_conversation_history(question, rag_response)
            
            # Update statistics
            self._update_stats(processing_time, len(context))
            self.rag_stats['successful_generations'] += 1
            
            logger.info(f"RAG query completed: {len(retrieved_docs)} docs, "
                       f"{confidence:.2f} confidence, {processing_time:.2f}s")
            
            return rag_response
            
        except Exception as e:
            logger.error(f"RAG query error: {e}")
            return RAGResponse(
                query=question,
                generated_response=f"An error occurred while processing your question: {str(e)}",
                retrieved_documents=[],
                confidence_score=0.0,
                processing_time=time.time() - start_time,
                metadata={'error': str(e)}
            )
    
    def index_documents(self, 
                       documents: List[Document],
                       collection_name: str,
                       chunk_large_docs: bool = True,
                       chunk_size: int = 1000) -> Dict[str, Any]:
        """
        Index documents for RAG with automatic processing
        
        Args:
            documents: Documents to index
            collection_name: Target collection
            chunk_large_docs: Whether to chunk large documents
            chunk_size: Maximum chunk size
            
        Returns:
            Indexing statistics
        """
        start_time = time.time()
        processed_docs = []
        
        try:
            for doc in documents:
                # Extract additional metadata
                extra_metadata = DocumentProcessor.extract_metadata(doc)
                doc.metadata.update(extra_metadata)
                
                # Chunk large documents if needed
                if chunk_large_docs and len(doc.content) > chunk_size:
                    chunks = DocumentProcessor.chunk_document(doc, chunk_size)
                    processed_docs.extend(chunks)
                    logger.debug(f"Chunked document {doc.id} into {len(chunks)} pieces")
                else:
                    processed_docs.append(doc)
            
            # Create collection if it doesn't exist
            existing_collections = self.chroma_manager.list_collections()
            if collection_name not in existing_collections:
                self.chroma_manager.create_collection(collection_name)
            
            # Add documents to collection
            result = self.chroma_manager.add_documents(collection_name, processed_docs)
            
            processing_time = time.time() - start_time
            
            indexing_stats = {
                **result,
                'original_documents': len(documents),
                'processed_documents': len(processed_docs),
                'chunks_created': len(processed_docs) - len(documents),
                'total_processing_time': processing_time
            }
            
            logger.info(f"Indexed {len(documents)} documents ({len(processed_docs)} total) "
                       f"in {processing_time:.2f}s")
            
            return indexing_stats
            
        except Exception as e:
            logger.error(f"Document indexing error: {e}")
            return {
                'success': False,
                'error': str(e),
                'original_documents': len(documents),
                'processed_documents': 0
            }
    
    def _prepare_context(self, 
                        retrieved_docs: List[SearchResult], 
                        config: RAGConfig) -> str:
        """Prepare context from retrieved documents"""
        context_parts = []
        current_length = 0
        
        for i, result in enumerate(retrieved_docs):
            doc = result.document
            
            # Format document with metadata
            doc_text = f"[Source {i+1}] {doc.content}"
            
            if config.include_sources and doc.source:
                doc_text += f" (Source: {doc.source})"
            
            # Check if adding this document would exceed context limit
            if current_length + len(doc_text) > config.max_context_length:
                # Try to include partial content
                remaining_space = config.max_context_length - current_length - 50  # Buffer
                if remaining_space > 100:  # Only include if meaningful content fits
                    truncated_content = doc.content[:remaining_space] + "..."
                    doc_text = f"[Source {i+1}] {truncated_content}"
                    context_parts.append(doc_text)
                break
            
            context_parts.append(doc_text)
            current_length += len(doc_text)
        
        return "\n\n".join(context_parts)
    
    def _generate_response(self, 
                          question: str, 
                          context: str, 
                          config: RAGConfig) -> str:
        """Generate response using LLM"""
        if not LLM_AVAILABLE:
            return self._create_context_summary(context, question)
        
        try:
            # Prepare system prompt
            system_prompt = config.system_prompt or """
You are a helpful AI assistant. Answer the question based on the provided context.
If the context doesn't contain enough information to answer the question, say so clearly.
Always cite your sources when possible.
"""
            
            # Prepare conversation context if enabled
            conversation_context = ""
            if config.use_conversation_context and self.conversation_history:
                recent_history = self.conversation_history[-3:]  # Last 3 exchanges
                history_parts = []
                for entry in recent_history:
                    history_parts.append(f"Q: {entry['question']}")
                    history_parts.append(f"A: {entry['answer']}")
                conversation_context = "\n".join(history_parts) + "\n\n"
            
            # Create prompt
            prompt = f"""
{conversation_context}Context:
{context}

Question: {question}

Please provide a comprehensive answer based on the context above. If you reference information, indicate which source it comes from.
"""
            
            # Get LLM interface and generate response
            llm_interface = get_llm_interface()
            response = llm_interface.generate_response(
                prompt=prompt,
                system_prompt=system_prompt,
                temperature=config.temperature,
                max_tokens=config.max_tokens
            )
            
            # Clean up response
            if response.startswith("[LLM ERROR:"):
                return self._create_context_summary(context, question)
            
            return response.strip()
            
        except Exception as e:
            logger.error(f"LLM generation error: {e}")
            return self._create_context_summary(context, question)
    
    def _create_context_summary(self, context: str, question: str) -> str:
        """Create a context-based summary when LLM is not available"""
        # Simple extractive summary
        sentences = context.split('.')
        
        # Find sentences most relevant to the question
        question_words = set(question.lower().split())
        scored_sentences = []
        
        for sentence in sentences:
            sentence = sentence.strip()
            if len(sentence) < 20:  # Skip very short sentences
                continue
                
            sentence_words = set(sentence.lower().split())
            overlap = len(question_words.intersection(sentence_words))
            
            if overlap > 0:
                scored_sentences.append((sentence, overlap))
        
        # Sort by relevance and take top sentences
        scored_sentences.sort(key=lambda x: x[1], reverse=True)
        top_sentences = [sent for sent, score in scored_sentences[:3]]
        
        if top_sentences:
            summary = "Based on the available information:\n\n" + ". ".join(top_sentences) + "."
        else:
            summary = "I found some relevant information, but it doesn't directly address your specific question. You may want to rephrase your query or check the source documents directly."
        
        return summary
    
    def _calculate_confidence(self, 
                            retrieved_docs: List[SearchResult], 
                            response: str) -> float:
        """Calculate confidence score for the response"""
        if not retrieved_docs:
            return 0.0
        
        # Base confidence on retrieval scores
        avg_retrieval_score = sum(doc.score for doc in retrieved_docs) / len(retrieved_docs)
        
        # Adjust based on response characteristics
        response_quality = 1.0
        
        if len(response) < 50:  # Very short responses are less confident
            response_quality *= 0.8
        
        if "I don't know" in response.lower() or "not enough information" in response.lower():
            response_quality *= 0.6
        
        if "[LLM ERROR:" in response:
            response_quality *= 0.3
        
        return min(1.0, avg_retrieval_score * response_quality)
    
    def _update_conversation_history(self, question: str, response: RAGResponse):
        """Update conversation history"""
        entry = {
            'timestamp': time.time(),
            'question': question,
            'answer': response.generated_response,
            'sources': len(response.retrieved_documents),
            'confidence': response.confidence_score
        }
        
        self.conversation_history.append(entry)
        
        # Keep only recent history
        if len(self.conversation_history) > 20:
            self.conversation_history = self.conversation_history[-10:]
    
    def _update_stats(self, processing_time: float, context_length: int):
        """Update RAG statistics"""
        total_queries = self.rag_stats['total_queries']
        
        # Update average response time
        current_avg_time = self.rag_stats['average_response_time']
        self.rag_stats['average_response_time'] = (
            (current_avg_time * (total_queries - 1) + processing_time) / total_queries
        )
        
        # Update average context length
        current_avg_context = self.rag_stats['average_context_length']
        self.rag_stats['average_context_length'] = (
            (current_avg_context * (total_queries - 1) + context_length) / total_queries
        )
    
    def get_rag_stats(self) -> Dict[str, Any]:
        """Get RAG system statistics"""
        success_rate = (
            self.rag_stats['successful_generations'] / max(1, self.rag_stats['total_queries']) * 100
        )
        
        return {
            **self.rag_stats,
            'success_rate': success_rate,
            'conversation_history_length': len(self.conversation_history),
            'search_stats': self.search_engine.get_search_stats()
        }
    
    def clear_conversation_history(self):
        """Clear conversation history"""
        self.conversation_history.clear()
        logger.info("Conversation history cleared")
    
    def get_conversation_history(self, limit: int = None) -> List[Dict[str, Any]]:
        """Get conversation history"""
        if limit:
            return self.conversation_history[-limit:]
        return self.conversation_history.copy()
    
    def suggest_follow_up_questions(self, 
                                   last_response: RAGResponse, 
                                   limit: int = 3) -> List[str]:
        """Suggest follow-up questions based on the last response"""
        suggestions = []
        
        # Based on retrieved documents
        if last_response.retrieved_documents:
            # Extract topics from metadata
            topics = set()
            for doc_result in last_response.retrieved_documents:
                metadata = doc_result.document.metadata
                if 'language_hints' in metadata:
                    topics.update(metadata['language_hints'])
            
            if topics:
                suggestions.extend([
                    f"Tell me more about {topic}" for topic in list(topics)[:2]
                ])
        
        # Generic follow-ups
        generic_suggestions = [
            "Can you provide more details?",
            "What are the key benefits?",
            "Are there any alternatives?",
            "How does this compare to other approaches?"
        ]
        
        suggestions.extend(generic_suggestions[:limit - len(suggestions)])
        
        return suggestions[:limit]