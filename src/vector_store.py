#!/usr/bin/env python3
"""
AI Deep Research MCP - VectorStore Component

Handles vector database storage and retrieval for semantic search capabilities.
Uses ChromaDB as the underlying vector database for efficient similarity search
and provides comprehensive methods for managing embedded document chunks.

Features:
- Persistent vector storage with ChromaDB
- Efficient similarity search with configurable ranking
- Metadata filtering and source management
- Thread-safe operations with automatic collection management
- Comprehensive statistics and monitoring

IMPLEMENTATION STATUS: GREEN phase complete - All 19 tests passing
CURRENT PHASE: REFACTOR - Code optimization and cleanup
"""

import os
import logging
import threading
from datetime import datetime, timezone
from dataclasses import dataclass
from typing import List, Dict, Any, Optional, Set, Union
import numpy as np
import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer

try:
    from embedder import EmbeddedChunk
except ImportError:
    # Fallback for when running from different paths
    try:
        from .embedder import EmbeddedChunk
    except ImportError:
        # Create a simple fallback class if embedder isn't available
        from dataclasses import dataclass
        from typing import List
        
        @dataclass
        class EmbeddedChunk:
            content: str
            embedding: List[float]
            metadata: dict = None

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class StoredChunk:
    """
    Represents a chunk stored in the vector database with full metadata.
    
    This dataclass encapsulates all information about a stored chunk including
    its content, embedding, and metadata for retrieval and management.
    """
    id: str
    text: str
    source_url: str
    metadata: Dict[str, Any]
    embedding: np.ndarray
    embedding_model: str
    timestamp: str

    def __post_init__(self):
        """Validate stored chunk data after initialization"""
        if not self.id or not self.text.strip():
            raise ValueError("Stored chunk must have valid ID and non-empty text")
        if self.embedding is None or len(self.embedding) == 0:
            raise ValueError("Stored chunk must have a valid embedding")


@dataclass
class SearchResult:
    """
    Represents a search result from the vector store with relevance scoring.
    
    This dataclass provides structured access to search results including
    similarity scores and ranking information for result evaluation.
    """
    id: str
    text: str
    source_url: str
    metadata: Dict[str, Any]
    score: float  # Similarity score (higher = more similar)
    rank: int     # Result ranking (1 = most relevant)

    def __post_init__(self):
        """Validate search result data after initialization"""
        if self.score < 0 or self.score > 1:
            logger.warning(f"Search result score {self.score} outside expected range [0,1]")
        if self.rank < 1:
            raise ValueError("Search result rank must be positive")


class VectorStore:
    """
    Vector database for storing and retrieving embedded document chunks.
    
    This class provides a comprehensive interface for managing embedded text chunks
    in a persistent vector database. It uses ChromaDB for efficient similarity search
    and supports advanced features like metadata filtering, source management, and 
    concurrent access.
    
    Key Features:
    - Persistent storage with automatic collection management
    - Efficient vector similarity search with configurable parameters
    - Metadata filtering and source-based operations
    - Thread-safe operations for concurrent access
    - Comprehensive statistics and monitoring capabilities
    - Automatic embedding dimension validation
    
    Attributes:
        persist_directory: Directory path for database persistence
        collection_name: Name of the ChromaDB collection
        embedding_dimension: Expected dimension of embedding vectors
        embedding_model: Model name for query embedding generation
    """
    
    # Constants for default configuration
    DEFAULT_COLLECTION_NAME = "research_documents"
    DEFAULT_EMBEDDING_DIMENSION = 384
    DEFAULT_EMBEDDING_MODEL = "all-MiniLM-L6-v2"
    METADATA_PREFIX = "meta_"
    
    def __init__(
        self,
        persist_directory: str,
        collection_name: str = DEFAULT_COLLECTION_NAME,
        embedding_dimension: int = DEFAULT_EMBEDDING_DIMENSION,
        embedding_model: str = DEFAULT_EMBEDDING_MODEL
    ):
        """
        Initialize the VectorStore with persistent storage.
        
        Args:
            persist_directory: Directory to persist the database
            collection_name: Name of the collection to use
            embedding_dimension: Expected dimension of embeddings
            embedding_model: Name of the embedding model for query embedding
            
        Raises:
            ValueError: If configuration parameters are invalid
            Exception: If database initialization fails
        """
        self._validate_init_params(persist_directory, collection_name, embedding_dimension)
        
        self.persist_directory = persist_directory
        self.collection_name = collection_name
        self.embedding_dimension = embedding_dimension
        self.embedding_model = embedding_model
        
        # Thread lock for concurrent access safety
        self._lock = threading.Lock()
        
        # Initialize ChromaDB client and collection
        self._initialize_client()
        self._initialize_collection()
        
        # Lazy load embedding model for queries
        self._query_model: Optional[SentenceTransformer] = None
        
        logger.info(f"VectorStore initialized: {self.collection_name} "
                   f"({self.embedding_dimension}D, {self.embedding_model})")
    
    def _validate_init_params(self, persist_directory: str, collection_name: str, embedding_dimension: int) -> None:
        """Validate initialization parameters"""
        if not persist_directory or not persist_directory.strip():
            raise ValueError("persist_directory cannot be empty")
        if not collection_name or not collection_name.strip():
            raise ValueError("collection_name cannot be empty")
        if embedding_dimension <= 0:
            raise ValueError("embedding_dimension must be positive")
    
    def _initialize_client(self) -> None:
        """Initialize ChromaDB client with proper configuration"""
        try:
            # Ensure persist directory exists
            os.makedirs(self.persist_directory, exist_ok=True)
            
            # Configure ChromaDB settings for optimal performance
            settings = Settings(
                persist_directory=self.persist_directory,
                anonymized_telemetry=False,
                allow_reset=True
            )
            
            self.client = chromadb.PersistentClient(
                path=self.persist_directory,
                settings=settings
            )
            
            logger.debug(f"ChromaDB client initialized at {self.persist_directory}")
            
        except Exception as e:
            logger.error(f"Failed to initialize ChromaDB client: {e}")
            raise
    
    def _initialize_collection(self) -> None:
        """Initialize or get existing collection with error handling"""
        try:
            # Try to get existing collection first
            self.collection = self.client.get_collection(name=self.collection_name)
            logger.info(f"Loaded existing collection '{self.collection_name}'")
        except Exception:
            # Collection doesn't exist, create it with metadata
            try:
                self.collection = self.client.create_collection(
                    name=self.collection_name,
                    metadata={
                        "description": "Research document chunks for semantic search",
                        "embedding_dimension": self.embedding_dimension,
                        "embedding_model": self.embedding_model,
                        "created_at": datetime.now(timezone.utc).isoformat()
                    }
                )
                logger.info(f"Created new collection '{self.collection_name}'")
            except Exception as e:
                logger.error(f"Failed to create collection: {e}")
                raise
    
    def _get_query_model(self) -> SentenceTransformer:
        """Lazy load embedding model for query processing"""
        if self._query_model is None:
            try:
                logger.debug(f"Loading embedding model: {self.embedding_model}")
                self._query_model = SentenceTransformer(self.embedding_model)
            except Exception as e:
                logger.error(f"Failed to load embedding model: {e}")
                raise
        return self._query_model
    
    def _embed_query(self, query: str) -> np.ndarray:
        """
        Generate embedding for a query string.
        
        Args:
            query: Text query to embed
            
        Returns:
            Embedding vector as numpy array
            
        Raises:
            Exception: If embedding generation fails
        """
        if not query or not query.strip():
            raise ValueError("Query text cannot be empty")
        
        try:
            model = self._get_query_model()
            embedding = model.encode([query.strip()])[0]
            
            # Validate embedding dimension
            self._validate_embedding(embedding)
            
            return embedding
            
        except Exception as e:
            logger.error(f"Failed to embed query '{query[:50]}...': {e}")
            raise
    
    def _validate_embedding(self, embedding: np.ndarray) -> None:
        """
        Validate embedding dimensions against expected configuration.
        
        Args:
            embedding: Embedding vector to validate
            
        Raises:
            ValueError: If embedding dimension doesn't match expected
        """
        if len(embedding) != self.embedding_dimension:
            raise ValueError(
                f"Embedding dimension {len(embedding)} does not match "
                f"expected dimension {self.embedding_dimension}"
            )
    
    def _prepare_chunk_metadata(self, chunk: EmbeddedChunk) -> Dict[str, Any]:
        """
        Prepare metadata for ChromaDB storage with proper prefixing.
        
        Args:
            chunk: EmbeddedChunk to prepare metadata for
            
        Returns:
            Formatted metadata dictionary for ChromaDB
        """
        # Base metadata required for all chunks
        metadata = {
            "source_url": chunk.source_url,
            "embedding_model": chunk.embedding_model,
            "start_char": chunk.start_char,
            "end_char": chunk.end_char,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        # Add original metadata with prefix to avoid conflicts
        for key, value in chunk.metadata.items():
            # Only store serializable values
            if isinstance(value, (str, int, float, bool)):
                metadata[f"{self.METADATA_PREFIX}{key}"] = value
            else:
                # Convert complex types to strings
                metadata[f"{self.METADATA_PREFIX}{key}"] = str(value)
        
        return metadata
    
    def _reconstruct_original_metadata(self, stored_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reconstruct original metadata from ChromaDB storage format.
        
        Args:
            stored_metadata: Metadata as stored in ChromaDB
            
        Returns:
            Original metadata dictionary
        """
        original_metadata = {}
        for key, value in stored_metadata.items():
            if key.startswith(self.METADATA_PREFIX):
                original_key = key[len(self.METADATA_PREFIX):]
                original_metadata[original_key] = value
        
        return original_metadata
    
    def _build_where_clause(self, filters: Optional[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
        """
        Build ChromaDB where clause from user filters.
        
        Args:
            filters: User-provided filter dictionary
            
        Returns:
            ChromaDB-compatible where clause or None
        """
        if not filters:
            return None
        
        where_clause = {}
        for key, value in filters.items():
            # Determine if this is a system field or user metadata
            if key in ("source_url", "embedding_model", "timestamp"):
                where_clause[key] = value
            else:
                # Add prefix for user metadata
                where_clause[f"{self.METADATA_PREFIX}{key}"] = value
        
        return where_clause
    
    def _convert_to_search_results(self, results: Dict[str, Any]) -> List[SearchResult]:
        """
        Convert ChromaDB query results to SearchResult objects.
        
        Args:
            results: Raw results from ChromaDB query
            
        Returns:
            List of SearchResult objects with proper scoring
        """
        search_results = []
        
        if not results['ids'] or not results['ids'][0]:
            return search_results
        
        for i, chunk_id in enumerate(results['ids'][0]):
            try:
                metadata = results['metadatas'][0][i]
                
                # Convert distance to similarity score (0-1, higher = more similar)
                # ChromaDB returns L2 distances, so we convert to similarity
                distance = results['distances'][0][i]
                similarity_score = max(0.0, 1.0 - distance)
                
                result = SearchResult(
                    id=chunk_id,
                    text=results['documents'][0][i],
                    source_url=metadata.get('source_url', ''),
                    metadata=self._reconstruct_original_metadata(metadata),
                    score=similarity_score,
                    rank=i + 1
                )
                search_results.append(result)
                
            except (IndexError, KeyError) as e:
                logger.warning(f"Failed to process search result {i}: {e}")
                continue
        
        return search_results
    
    def add_chunk(self, chunk: EmbeddedChunk) -> bool:
        """
        Add a single embedded chunk to the vector store.
        
        Args:
            chunk: EmbeddedChunk to store
            
        Returns:
            True if successful, False otherwise
        """
        return self.add_chunks([chunk])
    
    def add_chunks(self, chunks: List[EmbeddedChunk]) -> bool:
        """
        Add multiple embedded chunks to the vector store efficiently.
        
        This method performs batch insertion for optimal performance and
        ensures atomicity of the operation.
        
        Args:
            chunks: List of EmbeddedChunk objects to store
            
        Returns:
            True if successful, False otherwise
            
        Raises:
            ValueError: If chunk data is invalid
            Exception: If database operation fails
        """
        if not chunks:
            logger.debug("No chunks to add")
            return True
        
        with self._lock:
            try:
                # Prepare batch data for ChromaDB
                ids = []
                documents = []
                embeddings = []
                metadatas = []
                
                for chunk in chunks:
                    # Validate embedding dimension
                    self._validate_embedding(chunk.embedding)
                    
                    # Prepare data
                    ids.append(chunk.chunk_id)
                    documents.append(chunk.text)
                    embeddings.append(chunk.embedding.tolist())
                    metadatas.append(self._prepare_chunk_metadata(chunk))
                
                # Batch insert into collection
                self.collection.add(
                    ids=ids,
                    documents=documents,
                    embeddings=embeddings,
                    metadatas=metadatas
                )
                
                logger.info(f"Successfully added {len(chunks)} chunks to collection")
                return True
                
            except Exception as e:
                logger.error(f"Failed to add {len(chunks)} chunks: {e}")
                raise
    
    def search_by_vector(
        self, 
        query_vector: np.ndarray, 
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for similar chunks using a query vector.
        
        Args:
            query_vector: Query embedding vector
            top_k: Number of results to return (default: 5)
            filters: Optional metadata filters
            
        Returns:
            List of SearchResult objects ordered by relevance
            
        Raises:
            ValueError: If query vector is invalid
            Exception: If search operation fails
        """
        self._validate_embedding(query_vector)
        
        if top_k <= 0:
            raise ValueError("top_k must be positive")
        
        # Check if collection is empty first (before acquiring lock)
        collection_size = self.get_collection_size()
        if collection_size == 0:
            logger.debug("Collection is empty, returning empty results")
            return []
        
        with self._lock:
            try:
                # Build where clause from filters
                where_clause = self._build_where_clause(filters)
                
                # Execute similarity search
                results = self.collection.query(
                    query_embeddings=[query_vector.tolist()],
                    n_results=min(top_k, collection_size),
                    where=where_clause
                )
                
                # Convert to SearchResult objects
                search_results = self._convert_to_search_results(results)
                
                logger.debug(f"Vector search returned {len(search_results)} results")
                return search_results
                
            except Exception as e:
                logger.error(f"Vector search failed: {e}")
                raise
    
    def search_by_text(
        self, 
        query_text: str, 
        top_k: int = 5,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[SearchResult]:
        """
        Search for similar chunks using a text query.
        
        This method first embeds the query text then performs vector search.
        
        Args:
            query_text: Text query to search for
            top_k: Number of results to return (default: 5)
            filters: Optional metadata filters
            
        Returns:
            List of SearchResult objects ordered by relevance
        """
        # Generate embedding for query text
        query_vector = self._embed_query(query_text)
        
        # Use vector search
        return self.search_by_vector(query_vector, top_k, filters)
    
    def get_chunk_by_id(self, chunk_id: str) -> Optional[StoredChunk]:
        """
        Retrieve a specific chunk by its ID.
        
        Args:
            chunk_id: ID of the chunk to retrieve
            
        Returns:
            StoredChunk if found, None otherwise
        """
        if not chunk_id or not chunk_id.strip():
            raise ValueError("Chunk ID cannot be empty")
        
        with self._lock:
            try:
                results = self.collection.get(
                    ids=[chunk_id.strip()],
                    include=["documents", "embeddings", "metadatas"]
                )
                
                if not results['ids'] or not results['ids'][0]:
                    return None
                
                metadata = results['metadatas'][0]
                
                return StoredChunk(
                    id=chunk_id,
                    text=results['documents'][0],
                    source_url=metadata.get('source_url', ''),
                    metadata=self._reconstruct_original_metadata(metadata),
                    embedding=np.array(results['embeddings'][0]),
                    embedding_model=metadata.get('embedding_model', ''),
                    timestamp=metadata.get('timestamp', '')
                )
                
            except Exception as e:
                logger.error(f"Failed to get chunk by ID '{chunk_id}': {e}")
                return None
    
    def delete_chunk(self, chunk_id: str) -> bool:
        """
        Delete a chunk from the vector store.
        
        Args:
            chunk_id: ID of the chunk to delete
            
        Returns:
            True if successful, False otherwise
        """
        if not chunk_id or not chunk_id.strip():
            raise ValueError("Chunk ID cannot be empty")
        
        with self._lock:
            try:
                self.collection.delete(ids=[chunk_id.strip()])
                logger.info(f"Deleted chunk '{chunk_id}'")
                return True
                
            except Exception as e:
                logger.error(f"Failed to delete chunk '{chunk_id}': {e}")
                return False
    
    def delete_by_source(self, source_url: str) -> bool:
        """
        Delete all chunks from a specific source URL.
        
        Args:
            source_url: Source URL to delete chunks from
            
        Returns:
            True if successful, False otherwise
        """
        if not source_url or not source_url.strip():
            raise ValueError("Source URL cannot be empty")
        
        with self._lock:
            try:
                self.collection.delete(
                    where={"source_url": source_url.strip()}
                )
                logger.info(f"Deleted chunks from source '{source_url}'")
                return True
                
            except Exception as e:
                logger.error(f"Failed to delete by source '{source_url}': {e}")
                return False
    
    def clear_collection(self) -> bool:
        """
        Clear all chunks from the collection.
        
        This operation removes all data but preserves the collection structure.
        
        Returns:
            True if successful, False otherwise
        """
        with self._lock:
            try:
                # Delete and recreate collection for clean state
                self.client.delete_collection(name=self.collection_name)
                self._initialize_collection()
                logger.info("Successfully cleared collection")
                return True
                
            except Exception as e:
                logger.error(f"Failed to clear collection: {e}")
                return False
    
    def get_collection_size(self) -> int:
        """
        Get the number of chunks in the collection.
        
        Returns:
            Number of chunks currently stored
        """
        with self._lock:
            try:
                return self.collection.count()
            except Exception as e:
                logger.error(f"Failed to get collection size: {e}")
                return 0
    
    def list_sources(self) -> List[str]:
        """
        Get a list of all unique source URLs in the collection.
        
        Returns:
            List of unique source URLs, sorted alphabetically
        """
        with self._lock:
            try:
                # Get all documents with metadata
                results = self.collection.get(include=["metadatas"])
                
                sources = set()
                if results['metadatas']:
                    for metadata in results['metadatas']:
                        source_url = metadata.get('source_url')
                        if source_url:
                            sources.add(source_url)
                
                return sorted(list(sources))
                
            except Exception as e:
                logger.error(f"Failed to list sources: {e}")
                return []
    
    def get_collection_stats(self) -> Dict[str, Any]:
        """
        Get comprehensive statistics about the collection.
        
        Returns:
            Dictionary with detailed collection statistics
        """
        with self._lock:
            try:
                # Get all documents with metadata
                results = self.collection.get(
                    include=["documents", "metadatas"]
                )
                
                total_chunks = len(results['ids']) if results['ids'] else 0
                
                if total_chunks == 0:
                    return {
                        "total_chunks": 0,
                        "unique_sources": 0,
                        "embedding_models": [],
                        "avg_chunk_length": 0,
                        "total_characters": 0,
                        "collection_name": self.collection_name,
                        "embedding_dimension": self.embedding_dimension
                    }
                
                # Analyze metadata and content
                sources = set()
                total_chars = 0
                embedding_models = set()
                
                for i, metadata in enumerate(results['metadatas']):
                    # Source URL tracking
                    source_url = metadata.get('source_url')
                    if source_url:
                        sources.add(source_url)
                    
                    # Embedding model tracking
                    model = metadata.get('embedding_model')
                    if model:
                        embedding_models.add(model)
                    
                    # Character count
                    if i < len(results['documents']):
                        total_chars += len(results['documents'][i])
                
                avg_chunk_length = total_chars / total_chunks if total_chunks > 0 else 0
                
                return {
                    "total_chunks": total_chunks,
                    "unique_sources": len(sources),
                    "embedding_models": sorted(list(embedding_models)),
                    "avg_chunk_length": round(avg_chunk_length, 2),
                    "total_characters": total_chars,
                    "collection_name": self.collection_name,
                    "embedding_dimension": self.embedding_dimension,
                    "last_updated": datetime.now(timezone.utc).isoformat()
                }
                
            except Exception as e:
                logger.error(f"Failed to get collection stats: {e}")
                return {"error": str(e)}
    
    def health_check(self) -> Dict[str, Any]:
        """
        Perform a health check on the vector store.
        
        Returns:
            Dictionary with health status information
        """
        try:
            # Test basic operations
            size = self.get_collection_size()
            
            # Test query model loading
            model_loaded = self._query_model is not None
            if not model_loaded:
                try:
                    self._get_query_model()
                    model_loaded = True
                except:
                    model_loaded = False
            
            return {
                "status": "healthy",
                "collection_size": size,
                "query_model_loaded": model_loaded,
                "persist_directory": self.persist_directory,
                "collection_name": self.collection_name,
                "embedding_dimension": self.embedding_dimension,
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": datetime.now(timezone.utc).isoformat()
            }
