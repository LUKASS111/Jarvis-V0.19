"""
Semantic Search Engine with advanced search strategies
"""

import time
import logging
from typing import List, Dict, Any, Optional, Union
from dataclasses import dataclass
from enum import Enum

from .models import Document, SearchResult, QueryConfig
from .chroma_manager import ChromaDBManager
from .embedding_providers import EmbeddingProvider

logger = logging.getLogger(__name__)


class SearchStrategy(Enum):
    """Available search strategies"""
    SEMANTIC = "semantic"           # Pure vector similarity
    HYBRID = "hybrid"              # Vector + keyword search
    MMR = "mmr"                   # Maximal Marginal Relevance
    CONTEXTUAL = "contextual"      # Context-aware search
    MULTI_QUERY = "multi_query"    # Multiple query variations


@dataclass
class SearchConfig:
    """Configuration for semantic search"""
    strategy: SearchStrategy = SearchStrategy.SEMANTIC
    limit: int = 10
    score_threshold: float = 0.7
    include_metadata: bool = True
    rerank: bool = False
    diversify: bool = False
    expand_query: bool = False


class SemanticSearchEngine:
    """
    Advanced semantic search engine with multiple strategies
    """
    
    def __init__(self, 
                 chroma_manager: ChromaDBManager,
                 default_strategy: SearchStrategy = SearchStrategy.SEMANTIC):
        """
        Initialize semantic search engine
        
        Args:
            chroma_manager: ChromaDB manager instance
            default_strategy: Default search strategy
        """
        self.chroma_manager = chroma_manager
        self.default_strategy = default_strategy
        self.query_cache = {}
        self.search_stats = {
            'total_searches': 0,
            'cache_hits': 0,
            'average_response_time': 0.0
        }
        
    def search(self, 
               query: str,
               collection_name: str,
               config: SearchConfig = None) -> List[SearchResult]:
        """
        Perform semantic search with specified strategy
        
        Args:
            query: Search query
            collection_name: Target collection
            config: Search configuration
            
        Returns:
            List of search results
        """
        if config is None:
            config = SearchConfig()
        
        start_time = time.time()
        self.search_stats['total_searches'] += 1
        
        try:
            # Check cache first
            cache_key = self._get_cache_key(query, collection_name, config)
            if cache_key in self.query_cache:
                self.search_stats['cache_hits'] += 1
                logger.debug(f"Cache hit for query: {query[:50]}...")
                return self.query_cache[cache_key]
            
            # Route to appropriate search strategy
            if config.strategy == SearchStrategy.SEMANTIC:
                results = self._semantic_search(query, collection_name, config)
            elif config.strategy == SearchStrategy.HYBRID:
                results = self._hybrid_search(query, collection_name, config)
            elif config.strategy == SearchStrategy.MMR:
                results = self._mmr_search(query, collection_name, config)
            elif config.strategy == SearchStrategy.CONTEXTUAL:
                results = self._contextual_search(query, collection_name, config)
            elif config.strategy == SearchStrategy.MULTI_QUERY:
                results = self._multi_query_search(query, collection_name, config)
            else:
                results = self._semantic_search(query, collection_name, config)
            
            # Post-process results
            if config.rerank:
                results = self._rerank_results(query, results)
            
            if config.diversify:
                results = self._diversify_results(results)
            
            # Cache results
            self.query_cache[cache_key] = results
            
            # Update stats
            processing_time = time.time() - start_time
            self._update_stats(processing_time)
            
            logger.info(f"Search completed: {len(results)} results in {processing_time:.3f}s")
            return results
            
        except Exception as e:
            logger.error(f"Search error: {e}")
            return []
    
    def _semantic_search(self, 
                        query: str, 
                        collection_name: str, 
                        config: SearchConfig) -> List[SearchResult]:
        """Pure semantic vector search"""
        query_config = QueryConfig(
            collection_name=collection_name,
            limit=config.limit,
            include_metadata=config.include_metadata,
            score_threshold=config.score_threshold,
            query=query
        )
        
        return self.chroma_manager.semantic_search(query_config)
    
    def _hybrid_search(self, 
                      query: str, 
                      collection_name: str, 
                      config: SearchConfig) -> List[SearchResult]:
        """Hybrid vector + keyword search"""
        # Get semantic results
        semantic_results = self._semantic_search(query, collection_name, config)
        
        # Extract keywords for additional filtering
        keywords = self._extract_keywords(query)
        
        # Re-rank based on keyword presence
        for result in semantic_results:
            keyword_boost = self._calculate_keyword_boost(result.document.content, keywords)
            result.score = result.score * (1 + keyword_boost * 0.2)  # 20% keyword boost
        
        # Sort by updated scores
        semantic_results.sort(key=lambda x: x.score, reverse=True)
        
        return semantic_results[:config.limit]
    
    def _mmr_search(self, 
                   query: str, 
                   collection_name: str, 
                   config: SearchConfig) -> List[SearchResult]:
        """Maximal Marginal Relevance search for diversity"""
        # Get more results than needed for MMR selection
        extended_config = SearchConfig(
            strategy=SearchStrategy.SEMANTIC,
            limit=config.limit * 3,  # Get 3x more for diversity selection
            score_threshold=config.score_threshold * 0.8  # Lower threshold
        )
        
        candidates = self._semantic_search(query, collection_name, extended_config)
        
        if len(candidates) <= config.limit:
            return candidates
        
        # MMR algorithm
        selected = []
        lambda_param = 0.7  # Balance relevance vs diversity
        
        # Select first (highest relevance)
        if candidates:
            selected.append(candidates[0])
            candidates = candidates[1:]
        
        # Select remaining using MMR
        while len(selected) < config.limit and candidates:
            best_candidate = None
            best_score = -1
            best_idx = -1
            
            for i, candidate in enumerate(candidates):
                # Calculate MMR score
                relevance = candidate.score
                max_similarity = max([
                    self._calculate_similarity(candidate, selected_doc) 
                    for selected_doc in selected
                ])
                
                mmr_score = lambda_param * relevance - (1 - lambda_param) * max_similarity
                
                if mmr_score > best_score:
                    best_score = mmr_score
                    best_candidate = candidate
                    best_idx = i
            
            if best_candidate:
                selected.append(best_candidate)
                candidates.pop(best_idx)
        
        return selected
    
    def _contextual_search(self, 
                          query: str, 
                          collection_name: str, 
                          config: SearchConfig) -> List[SearchResult]:
        """Context-aware search using query expansion"""
        # Expand query with context
        expanded_query = self._expand_query(query) if config.expand_query else query
        
        # Perform search with expanded query
        expanded_config = SearchConfig(
            strategy=SearchStrategy.SEMANTIC,
            limit=config.limit,
            score_threshold=config.score_threshold
        )
        
        return self._semantic_search(expanded_query, collection_name, expanded_config)
    
    def _multi_query_search(self, 
                           query: str, 
                           collection_name: str, 
                           config: SearchConfig) -> List[SearchResult]:
        """Search using multiple query variations"""
        # Generate query variations
        query_variations = self._generate_query_variations(query)
        
        all_results = {}  # document_id -> SearchResult
        
        # Search with each variation
        for variation in query_variations:
            variation_config = SearchConfig(
                strategy=SearchStrategy.SEMANTIC,
                limit=config.limit,
                score_threshold=config.score_threshold * 0.8
            )
            
            results = self._semantic_search(variation, collection_name, variation_config)
            
            # Merge results (keep highest score for each document)
            for result in results:
                doc_id = result.document.id
                if doc_id not in all_results or result.score > all_results[doc_id].score:
                    all_results[doc_id] = result
        
        # Sort by score and return top results
        final_results = sorted(all_results.values(), key=lambda x: x.score, reverse=True)
        return final_results[:config.limit]
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract keywords from query"""
        # Simple keyword extraction (can be enhanced with NLP)
        import re
        
        # Remove common stop words
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by'}
        
        # Extract words
        words = re.findall(r'\b\w+\b', query.lower())
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        
        return keywords
    
    def _calculate_keyword_boost(self, content: str, keywords: List[str]) -> float:
        """Calculate keyword presence boost"""
        if not keywords:
            return 0.0
        
        content_lower = content.lower()
        matches = sum(1 for keyword in keywords if keyword in content_lower)
        
        return matches / len(keywords)
    
    def _calculate_similarity(self, result1: SearchResult, result2: SearchResult) -> float:
        """Calculate similarity between two search results"""
        # Simple similarity based on content overlap
        content1 = set(result1.document.content.lower().split())
        content2 = set(result2.document.content.lower().split())
        
        if not content1 or not content2:
            return 0.0
        
        intersection = len(content1.intersection(content2))
        union = len(content1.union(content2))
        
        return intersection / union if union > 0 else 0.0
    
    def _expand_query(self, query: str) -> str:
        """Expand query with related terms"""
        # Simple query expansion (can be enhanced with thesaurus/word embeddings)
        expansion_map = {
            'python': 'python programming code script',
            'database': 'database sql data storage',
            'ai': 'artificial intelligence machine learning ml',
            'web': 'web website http api endpoint'
        }
        
        expanded_terms = []
        query_lower = query.lower()
        
        for term, expansion in expansion_map.items():
            if term in query_lower:
                expanded_terms.extend(expansion.split())
        
        if expanded_terms:
            return f"{query} {' '.join(set(expanded_terms))}"
        
        return query
    
    def _generate_query_variations(self, query: str) -> List[str]:
        """Generate variations of the query"""
        variations = [query]
        
        # Add synonyms/variations
        synonym_map = {
            'find': ['search', 'locate', 'discover'],
            'create': ['make', 'build', 'generate'],
            'delete': ['remove', 'eliminate', 'drop'],
            'update': ['modify', 'change', 'edit']
        }
        
        query_lower = query.lower()
        for original, synonyms in synonym_map.items():
            if original in query_lower:
                for synonym in synonyms:
                    variation = query_lower.replace(original, synonym)
                    variations.append(variation)
        
        return list(set(variations))  # Remove duplicates
    
    def _rerank_results(self, query: str, results: List[SearchResult]) -> List[SearchResult]:
        """Re-rank results using advanced scoring"""
        # Simple re-ranking based on query term frequency
        query_terms = set(query.lower().split())
        
        for result in results:
            content_terms = set(result.document.content.lower().split())
            term_overlap = len(query_terms.intersection(content_terms))
            
            # Boost score based on term overlap
            boost = term_overlap / len(query_terms) if query_terms else 0
            result.score = result.score * (1 + boost * 0.1)
        
        results.sort(key=lambda x: x.score, reverse=True)
        return results
    
    def _diversify_results(self, results: List[SearchResult]) -> List[SearchResult]:
        """Diversify results to avoid redundancy"""
        if len(results) <= 1:
            return results
        
        diversified = [results[0]]  # Keep top result
        
        for candidate in results[1:]:
            # Check similarity with already selected results
            max_similarity = max([
                self._calculate_similarity(candidate, selected) 
                for selected in diversified
            ])
            
            # Only add if not too similar to existing results
            if max_similarity < 0.8:  # Similarity threshold
                diversified.append(candidate)
        
        return diversified
    
    def _get_cache_key(self, query: str, collection_name: str, config: SearchConfig) -> str:
        """Generate cache key for query"""
        return f"{collection_name}:{config.strategy.value}:{hash(query)}:{config.limit}:{config.score_threshold}"
    
    def _update_stats(self, processing_time: float):
        """Update search statistics"""
        current_avg = self.search_stats['average_response_time']
        total_searches = self.search_stats['total_searches']
        
        # Update average response time
        self.search_stats['average_response_time'] = (
            (current_avg * (total_searches - 1) + processing_time) / total_searches
        )
    
    def get_search_stats(self) -> Dict[str, Any]:
        """Get search engine statistics"""
        cache_hit_rate = (
            self.search_stats['cache_hits'] / max(1, self.search_stats['total_searches']) * 100
        )
        
        return {
            **self.search_stats,
            'cache_hit_rate': cache_hit_rate,
            'cache_size': len(self.query_cache)
        }
    
    def clear_cache(self):
        """Clear query cache"""
        self.query_cache.clear()
        logger.info("Search cache cleared")
    
    def suggest_queries(self, partial_query: str, collection_name: str, limit: int = 5) -> List[str]:
        """Suggest query completions based on collection content"""
        # Simple query suggestion (can be enhanced with more sophisticated methods)
        if len(partial_query) < 2:
            return []
        
        # Get some sample documents to analyze common terms
        sample_config = SearchConfig(limit=50, score_threshold=0.1)
        sample_results = self._semantic_search(partial_query, collection_name, sample_config)
        
        # Extract common terms from results
        term_frequency = {}
        for result in sample_results:
            words = result.document.content.lower().split()
            for word in words:
                if len(word) > 3 and partial_query.lower() in word:
                    term_frequency[word] = term_frequency.get(word, 0) + 1
        
        # Return most frequent matching terms
        suggestions = sorted(term_frequency.items(), key=lambda x: x[1], reverse=True)
        return [term for term, freq in suggestions[:limit]]