"""
Embedding providers for various embedding models
"""

import time
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Union
from .models import EmbeddingResult

logger = logging.getLogger(__name__)


class EmbeddingProvider(ABC):
    """Abstract base class for embedding providers"""
    
    @abstractmethod
    def embed_text(self, text: str) -> EmbeddingResult:
        """Generate embedding for single text"""
        pass
    
    @abstractmethod
    def embed_batch(self, texts: List[str]) -> List[EmbeddingResult]:
        """Generate embeddings for batch of texts"""
        pass
    
    @abstractmethod
    def get_dimensions(self) -> int:
        """Get embedding dimensions"""
        pass
    
    @abstractmethod
    def get_model_name(self) -> str:
        """Get model name"""
        pass


class SentenceTransformerProvider(EmbeddingProvider):
    """
    Sentence Transformers embedding provider
    High-quality, free, local embeddings
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        """
        Initialize with model name
        
        Popular models:
        - all-MiniLM-L6-v2: Fast, 384 dims, good quality
        - all-mpnet-base-v2: Slower, 768 dims, best quality
        - multi-qa-MiniLM-L6-cos-v1: Optimized for Q&A
        """
        self.model_name = model_name
        self._model = None
        self._dimensions = None
        
    def _load_model(self):
        """Lazy load the model"""
        if self._model is None:
            try:
                from sentence_transformers import SentenceTransformer
                self._model = SentenceTransformer(self.model_name)
                self._dimensions = self._model.get_sentence_embedding_dimension()
                logger.info(f"Loaded SentenceTransformer model: {self.model_name} ({self._dimensions} dims)")
            except ImportError:
                raise ImportError("sentence-transformers not installed. Run: pip install sentence-transformers")
            except Exception as e:
                logger.error(f"Failed to load model {self.model_name}: {e}")
                raise
    
    def embed_text(self, text: str) -> EmbeddingResult:
        """Generate embedding for single text"""
        self._load_model()
        
        start_time = time.time()
        embedding = self._model.encode(text, convert_to_tensor=False)
        processing_time = time.time() - start_time
        
        return EmbeddingResult(
            embedding=embedding.tolist(),
            model_name=self.model_name,
            dimensions=len(embedding),
            processing_time=processing_time
        )
    
    def embed_batch(self, texts: List[str]) -> List[EmbeddingResult]:
        """Generate embeddings for batch of texts"""
        self._load_model()
        
        start_time = time.time()
        embeddings = self._model.encode(texts, convert_to_tensor=False)
        total_time = time.time() - start_time
        time_per_text = total_time / len(texts)
        
        results = []
        for i, embedding in enumerate(embeddings):
            results.append(EmbeddingResult(
                embedding=embedding.tolist(),
                model_name=self.model_name,
                dimensions=len(embedding),
                processing_time=time_per_text
            ))
        
        return results
    
    def get_dimensions(self) -> int:
        """Get embedding dimensions"""
        self._load_model()
        return self._dimensions
    
    def get_model_name(self) -> str:
        """Get model name"""
        return self.model_name


class OpenAIEmbeddingProvider(EmbeddingProvider):
    """
    OpenAI embedding provider
    Requires API key but provides high-quality embeddings
    """
    
    def __init__(self, model_name: str = "text-embedding-3-small", api_key: str = None):
        """
        Initialize with model name and API key
        
        Available models:
        - text-embedding-3-small: 1536 dims, efficient
        - text-embedding-3-large: 3072 dims, highest quality
        - text-embedding-ada-002: 1536 dims, previous version
        """
        self.model_name = model_name
        self.api_key = api_key
        self._client = None
        self._dimensions = self._get_model_dimensions()
        
    def _get_model_dimensions(self) -> int:
        """Get dimensions for model"""
        dimensions_map = {
            "text-embedding-3-small": 1536,
            "text-embedding-3-large": 3072,
            "text-embedding-ada-002": 1536
        }
        return dimensions_map.get(self.model_name, 1536)
    
    def _get_client(self):
        """Get OpenAI client"""
        if self._client is None:
            try:
                import openai
                self._client = openai.OpenAI(api_key=self.api_key)
            except ImportError:
                raise ImportError("openai not installed. Run: pip install openai")
        return self._client
    
    def embed_text(self, text: str) -> EmbeddingResult:
        """Generate embedding for single text"""
        return self.embed_batch([text])[0]
    
    def embed_batch(self, texts: List[str]) -> List[EmbeddingResult]:
        """Generate embeddings for batch of texts"""
        client = self._get_client()
        
        start_time = time.time()
        try:
            response = client.embeddings.create(
                model=self.model_name,
                input=texts
            )
            
            total_time = time.time() - start_time
            time_per_text = total_time / len(texts)
            
            results = []
            for i, embedding_data in enumerate(response.data):
                results.append(EmbeddingResult(
                    embedding=embedding_data.embedding,
                    model_name=self.model_name,
                    dimensions=len(embedding_data.embedding),
                    processing_time=time_per_text
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"OpenAI embedding error: {e}")
            raise
    
    def get_dimensions(self) -> int:
        """Get embedding dimensions"""
        return self._dimensions
    
    def get_model_name(self) -> str:
        """Get model name"""
        return self.model_name


class LocalEmbeddingProvider(EmbeddingProvider):
    """
    Local embedding provider using transformers library
    For custom models or local deployment
    """
    
    def __init__(self, model_path: str, device: str = "auto"):
        """Initialize with local model path"""
        self.model_path = model_path
        self.device = device
        self._model = None
        self._tokenizer = None
        self._dimensions = None
        
    def _load_model(self):
        """Load local model and tokenizer"""
        if self._model is None:
            try:
                from transformers import AutoModel, AutoTokenizer
                import torch
                
                self._tokenizer = AutoTokenizer.from_pretrained(self.model_path)
                self._model = AutoModel.from_pretrained(self.model_path)
                
                if self.device == "auto":
                    self.device = "cuda" if torch.cuda.is_available() else "cpu"
                
                self._model.to(self.device)
                
                # Get dimensions from model config
                self._dimensions = self._model.config.hidden_size
                
                logger.info(f"Loaded local model: {self.model_path} ({self._dimensions} dims)")
                
            except ImportError:
                raise ImportError("transformers not installed. Run: pip install transformers torch")
            except Exception as e:
                logger.error(f"Failed to load local model {self.model_path}: {e}")
                raise
    
    def embed_text(self, text: str) -> EmbeddingResult:
        """Generate embedding for single text"""
        return self.embed_batch([text])[0]
    
    def embed_batch(self, texts: List[str]) -> List[EmbeddingResult]:
        """Generate embeddings for batch of texts"""
        self._load_model()
        
        start_time = time.time()
        
        try:
            import torch
            
            # Tokenize texts
            inputs = self._tokenizer(
                texts, 
                padding=True, 
                truncation=True, 
                return_tensors="pt"
            ).to(self.device)
            
            # Generate embeddings
            with torch.no_grad():
                outputs = self._model(**inputs)
                # Use mean pooling of last hidden states
                embeddings = outputs.last_hidden_state.mean(dim=1)
            
            total_time = time.time() - start_time
            time_per_text = total_time / len(texts)
            
            results = []
            for i, embedding in enumerate(embeddings):
                results.append(EmbeddingResult(
                    embedding=embedding.cpu().numpy().tolist(),
                    model_name=self.model_path,
                    dimensions=len(embedding),
                    processing_time=time_per_text
                ))
            
            return results
            
        except Exception as e:
            logger.error(f"Local embedding error: {e}")
            raise
    
    def get_dimensions(self) -> int:
        """Get embedding dimensions"""
        self._load_model()
        return self._dimensions
    
    def get_model_name(self) -> str:
        """Get model name"""
        return self.model_path


def get_embedding_provider(provider_type: str, **kwargs) -> EmbeddingProvider:
    """
    Factory function to create embedding providers
    
    Args:
        provider_type: "sentence_transformers", "openai", or "local"
        **kwargs: Provider-specific arguments
    """
    providers = {
        "sentence_transformers": SentenceTransformerProvider,
        "openai": OpenAIEmbeddingProvider,
        "local": LocalEmbeddingProvider
    }
    
    if provider_type not in providers:
        raise ValueError(f"Unknown provider type: {provider_type}")
    
    return providers[provider_type](**kwargs)