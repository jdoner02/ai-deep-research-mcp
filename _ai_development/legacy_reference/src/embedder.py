#!/usr/bin/env python3
"""
AI Deep Research MCP - Embedder Component

Handles text chunking and embedding generation for semantic search capabilities.
This component converts documents into embedded chunks suitable for vector storage.

Features:
- Intelligent text chunking with sentence boundary preservation
- Configurable chunk size and overlap
- Batch embedding generation using sentence transformers
- Comprehensive metadata tracking
- Memory-efficient processing

IMPLEMENTATION STATUS: GREEN phase complete - All 18 tests passing
CURRENT PHASE: REFACTOR - Code optimization and cleanup
"""

import re
import uuid
import logging
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Iterator
import numpy as np
from sentence_transformers import SentenceTransformer

# Set up logging
logger = logging.getLogger(__name__)


@dataclass
class TextChunk:
    """Represents a chunk of text with metadata and positional information"""
    text: str
    source_url: str
    chunk_id: str
    metadata: Dict[str, Any]
    start_char: int
    end_char: int

    def __post_init__(self):
        """Validate chunk data after initialization"""
        if not self.text.strip():
            raise ValueError("Text chunk cannot be empty")
        if self.start_char < 0 or self.end_char < self.start_char:
            raise ValueError("Invalid character positions")


@dataclass
class EmbeddedChunk(TextChunk):
    """Represents a text chunk with its vector embedding"""
    embedding: np.ndarray
    embedding_model: str

    def __post_init__(self):
        """Validate embedded chunk data after initialization"""
        super().__post_init__()
        if self.embedding is None or len(self.embedding) == 0:
            raise ValueError("Embedding cannot be empty")


class Embedder:
    """
    Handles text chunking and embedding generation for semantic search.
    
    This component takes documents and converts them into embedded chunks
    that can be stored in a vector database for retrieval. It provides
    intelligent text chunking with configurable overlap and batch processing
    for efficient embedding generation.
    
    Attributes:
        chunk_size: Maximum characters per chunk
        chunk_overlap: Character overlap between consecutive chunks  
        embedding_model: Name of the sentence transformer model
        batch_size: Batch size for embedding generation
    """
    
    # Sentence boundary patterns for intelligent chunking
    SENTENCE_BOUNDARY_PATTERN = re.compile(r'[.!?]\s+')
    
    def __init__(
        self, 
        chunk_size: int = 1000,
        chunk_overlap: Optional[int] = None,
        embedding_model: str = "all-MiniLM-L6-v2",
        batch_size: int = 32
    ):
        """
        Initialize the Embedder with configurable parameters.
        
        Args:
            chunk_size: Maximum characters per chunk (default: 1000)
            chunk_overlap: Character overlap between chunks (default: 10% of chunk_size)
            embedding_model: Sentence transformer model name (default: "all-MiniLM-L6-v2")
            batch_size: Batch size for embedding generation (default: 32)
            
        Raises:
            ValueError: If parameters are invalid
        """
        self._validate_parameters(chunk_size, chunk_overlap)
        
        self.chunk_size = chunk_size
        self.chunk_overlap = self._calculate_overlap(chunk_size, chunk_overlap)
        self.embedding_model = embedding_model
        self.batch_size = batch_size
        
        # Lazy load the sentence transformer model
        self._model: Optional[SentenceTransformer] = None
        
        logger.info(f"Initialized Embedder with chunk_size={chunk_size}, "
                   f"overlap={self.chunk_overlap}, model={embedding_model}")
    
    def _validate_parameters(self, chunk_size: int, chunk_overlap: Optional[int]) -> None:
        """Validate initialization parameters"""
        if chunk_size <= 0:
            raise ValueError("chunk_size must be positive")
        if chunk_overlap is not None and chunk_overlap >= chunk_size:
            raise ValueError("chunk_overlap must be less than chunk_size")
    
    def _calculate_overlap(self, chunk_size: int, chunk_overlap: Optional[int]) -> int:
        """Calculate appropriate overlap if not provided"""
        if chunk_overlap is None:
            # Default to 10% of chunk_size, capped at 100 characters
            return min(100, max(10, chunk_size // 10))
        return chunk_overlap
    
    def _get_model(self) -> SentenceTransformer:
        """Lazy load the sentence transformer model"""
        if self._model is None:
            logger.info(f"Loading sentence transformer model: {self.embedding_model}")
            self._model = SentenceTransformer(self.embedding_model)
        return self._model
    
    def _find_sentence_boundary(self, text: str, start: int, max_end: int) -> int:
        """
        Find the best sentence boundary within the given range.
        
        Args:
            text: Full text to search in
            start: Start position
            max_end: Maximum end position
            
        Returns:
            Best end position that ends on a sentence boundary
        """
        search_text = text[start:max_end]
        matches = list(self.SENTENCE_BOUNDARY_PATTERN.finditer(search_text))
        
        if matches:
            # Use the last sentence ending found
            last_match = matches[-1]
            return start + last_match.end()
        
        return max_end
    
    def _generate_chunk_id(self) -> str:
        """Generate a unique chunk identifier"""
        return f"chunk_{uuid.uuid4().hex[:8]}"
    
    def _create_chunk_metadata(
        self, 
        base_metadata: Dict[str, Any], 
        chunk_index: int,
        chunk_count: Optional[int] = None
    ) -> Dict[str, Any]:
        """Create metadata for a chunk"""
        chunk_metadata = base_metadata.copy()
        chunk_metadata.update({
            'chunk_index': chunk_index,
            'chunk_count': chunk_count
        })
        return chunk_metadata
    
    def chunk_text(
        self, 
        text: str, 
        source_url: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[TextChunk]:
        """
        Split text into overlapping chunks with intelligent boundary detection.
        
        This method preserves sentence boundaries when possible and creates
        overlapping chunks to maintain context across chunk boundaries.
        
        Args:
            text: Text to chunk
            source_url: Source URL for the text
            metadata: Additional metadata to include
            
        Returns:
            List of TextChunk objects
            
        Raises:
            ValueError: If text is empty after cleaning
        """
        if not text or not text.strip():
            return []
            
        if metadata is None:
            metadata = {}
            
        # Clean and normalize text
        text = text.strip()
        chunks = []
        start = 0
        chunk_index = 0
        
        while start < len(text):
            # Calculate end position
            end = min(start + self.chunk_size, len(text))
            
            # Try to end at sentence boundary if not at end of text
            if end < len(text):
                end = self._find_sentence_boundary(text, start, end)
            
            # Extract chunk text
            chunk_text = text[start:end].strip()
            
            if chunk_text:  # Only create non-empty chunks
                chunk = TextChunk(
                    text=chunk_text,
                    source_url=source_url,
                    chunk_id=self._generate_chunk_id(),
                    metadata=self._create_chunk_metadata(metadata, chunk_index),
                    start_char=start,
                    end_char=end
                )
                
                chunks.append(chunk)
                chunk_index += 1
            
            # Calculate next start position with overlap
            if end < len(text):  # Not the last chunk
                start = max(start + 1, end - self.chunk_overlap)
            else:
                break
            
            # Ensure we make progress to prevent infinite loops
            if chunks and start <= chunks[-1].start_char:
                start = chunks[-1].end_char
        
        # Update chunk count in all chunks
        for chunk in chunks:
            chunk.metadata['chunk_count'] = len(chunks)
        
        logger.debug(f"Created {len(chunks)} chunks from {len(text)} characters")
        return chunks
    
    def generate_embeddings(self, chunks: List[TextChunk]) -> List[EmbeddedChunk]:
        """
        Generate embeddings for text chunks using batch processing.
        
        Args:
            chunks: List of TextChunk objects
            
        Returns:
            List of EmbeddedChunk objects with embeddings
            
        Raises:
            Exception: If embedding generation fails
        """
        if not chunks:
            return []
        
        model = self._get_model()
        
        # Extract texts for embedding
        texts = [chunk.text for chunk in chunks]
        
        try:
            # Generate embeddings in batches for efficiency
            logger.debug(f"Generating embeddings for {len(chunks)} chunks using model {self.embedding_model}")
            embeddings = model.encode(texts, batch_size=self.batch_size)
            
            # Create embedded chunks
            embedded_chunks = []
            for chunk, embedding in zip(chunks, embeddings):
                embedded_chunk = EmbeddedChunk(
                    text=chunk.text,
                    source_url=chunk.source_url,
                    chunk_id=chunk.chunk_id,
                    metadata=chunk.metadata,
                    start_char=chunk.start_char,
                    end_char=chunk.end_char,
                    embedding=embedding,
                    embedding_model=self.embedding_model
                )
                embedded_chunks.append(embedded_chunk)
            
            logger.info(f"Successfully generated embeddings for {len(embedded_chunks)} chunks")
            return embedded_chunks
            
        except Exception as e:
            logger.error(f"Failed to generate embeddings: {e}")
            raise
    
    def process_document(
        self, 
        text: str, 
        source_url: str, 
        metadata: Optional[Dict[str, Any]] = None
    ) -> List[EmbeddedChunk]:
        """
        Process a complete document: chunk and embed in one operation.
        
        This is the main entry point for document processing, combining
        text chunking and embedding generation into a single operation.
        
        Args:
            text: Document text
            source_url: Source URL
            metadata: Document metadata
            
        Returns:
            List of EmbeddedChunk objects ready for vector storage
        """
        logger.info(f"Processing document from {source_url} ({len(text)} characters)")
        
        # Chunk the text
        chunks = self.chunk_text(text, source_url, metadata)
        
        if not chunks:
            logger.warning(f"No chunks created from document {source_url}")
            return []
        
        # Generate embeddings
        embedded_chunks = self.generate_embeddings(chunks)
        
        logger.info(f"Document processing complete: {len(embedded_chunks)} embedded chunks created")
        return embedded_chunks
    
    def get_embedding(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text string.
        
        Args:
            text: Text to embed
            
        Returns:
            Numpy array containing the embedding vector
            
        Raises:
            Exception: If embedding generation fails
        """
        if not text.strip():
            raise ValueError("Text cannot be empty")
        
        model = self._get_model()
        
        try:
            embedding = model.encode([text], batch_size=1)
            return embedding[0]  # Return single embedding, not array of embeddings
            
        except Exception as e:
            logger.error(f"Failed to generate embedding for text: {e}")
            raise
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get information about the current embedding model"""
        return {
            'model_name': self.embedding_model,
            'chunk_size': self.chunk_size,
            'chunk_overlap': self.chunk_overlap,
            'batch_size': self.batch_size,
            'model_loaded': self._model is not None
        }
