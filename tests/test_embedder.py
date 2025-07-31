#!/usr/bin/env python3
"""
AI Deep Research MCP - Embedder Tests

Test suite for the Embedder component that handles text chunking and embedding
for semantic search capabilities. Follows TDD principles.

PHASE: RED - Writing failing tests first
"""

import pytest
import numpy as np
from typing import List, Dict, Any
from unittest.mock import Mock, patch, MagicMock

# Import from src directory
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    from embedder import Embedder, TextChunk, EmbeddedChunk
except ImportError as e:
    # Expected during RED phase
    print(f"Import error: {e}")
    pass


class TestEmbedder:
    """Test the Embedder component for text chunking and embedding"""
    
    def test_embedder_exists(self):
        """Test that Embedder class can be instantiated"""
        embedder = Embedder()
        assert embedder is not None
        assert hasattr(embedder, 'chunk_size')
        assert hasattr(embedder, 'chunk_overlap')
        assert hasattr(embedder, 'embedding_model')
    
    def test_text_chunk_dataclass(self):
        """Test TextChunk dataclass structure"""
        chunk = TextChunk(
            text="Sample text chunk",
            source_url="https://example.com",
            chunk_id="chunk_001",
            metadata={"title": "Test Document"},
            start_char=0,
            end_char=17
        )
        
        assert chunk.text == "Sample text chunk"
        assert chunk.source_url == "https://example.com"
        assert chunk.chunk_id == "chunk_001"
        assert chunk.metadata["title"] == "Test Document"
        assert chunk.start_char == 0
        assert chunk.end_char == 17
    
    def test_embedded_chunk_dataclass(self):
        """Test EmbeddedChunk dataclass structure"""
        embedding = np.array([0.1, 0.2, 0.3, 0.4])
        
        chunk = EmbeddedChunk(
            text="Sample text chunk",
            source_url="https://example.com",
            chunk_id="chunk_001",
            metadata={"title": "Test Document"},
            start_char=0,
            end_char=17,
            embedding=embedding,
            embedding_model="test-model"
        )
        
        assert chunk.text == "Sample text chunk"
        assert chunk.source_url == "https://example.com"
        assert chunk.chunk_id == "chunk_001"
        assert np.array_equal(chunk.embedding, embedding)
        assert chunk.embedding_model == "test-model"
    
    def test_chunk_text_basic(self):
        """Test basic text chunking functionality"""
        embedder = Embedder(chunk_size=100, chunk_overlap=20)
        
        text = "This is a long piece of text that should be split into multiple chunks. " * 10
        source_url = "https://example.com/doc"
        
        chunks = embedder.chunk_text(text, source_url=source_url)
        
        assert isinstance(chunks, list)
        assert len(chunks) > 1  # Should create multiple chunks
        assert all(isinstance(chunk, TextChunk) for chunk in chunks)
        assert all(chunk.source_url == source_url for chunk in chunks)
        assert all(len(chunk.text) <= 120 for chunk in chunks)  # Size + some tolerance
    
    def test_chunk_text_with_overlap(self):
        """Test text chunking with overlap"""
        embedder = Embedder(chunk_size=50, chunk_overlap=10)
        
        text = "Word1 Word2 Word3 Word4 Word5 Word6 Word7 Word8 Word9 Word10 Word11 Word12"
        chunks = embedder.chunk_text(text, source_url="https://example.com")
        
        assert len(chunks) >= 2
        
        # Check overlap exists between consecutive chunks
        for i in range(len(chunks) - 1):
            current_chunk = chunks[i]
            next_chunk = chunks[i + 1]
            
            # There should be some overlapping content
            current_words = current_chunk.text.split()
            next_words = next_chunk.text.split()
            
            # At least one word should overlap
            overlap = set(current_words) & set(next_words)
            assert len(overlap) > 0, "Chunks should have overlapping content"
    
    def test_chunk_text_preserves_sentences(self):
        """Test that chunking tries to preserve sentence boundaries"""
        embedder = Embedder(chunk_size=100, chunk_overlap=10)
        
        text = "First sentence is here. Second sentence follows. Third sentence continues. Fourth sentence ends."
        chunks = embedder.chunk_text(text, source_url="https://example.com")
        
        # Should not break sentences in the middle
        for chunk in chunks:
            # Each chunk should end with sentence punctuation or be the last chunk
            if chunk != chunks[-1]:  # Not the last chunk
                assert chunk.text.rstrip().endswith(('.', '!', '?')), f"Chunk should end with sentence: {chunk.text}"
    
    def test_chunk_metadata_inheritance(self):
        """Test that chunks inherit and extend metadata"""
        embedder = Embedder(chunk_size=50)
        
        text = "This is text to be chunked into multiple pieces."
        metadata = {"title": "Test Doc", "author": "Test Author"}
        
        chunks = embedder.chunk_text(text, source_url="https://example.com", metadata=metadata)
        
        for i, chunk in enumerate(chunks):
            assert chunk.metadata["title"] == "Test Doc"
            assert chunk.metadata["author"] == "Test Author"
            assert chunk.metadata["chunk_index"] == i
            assert "chunk_count" in chunk.metadata
            assert chunk.chunk_id.startswith("chunk_")
    
    @patch('embedder.SentenceTransformer')
    def test_generate_embeddings_basic(self, mock_sentence_transformer):
        """Test basic embedding generation"""
        # Mock the sentence transformer
        mock_model = Mock()
        mock_model.encode.return_value = np.array([[0.1, 0.2, 0.3], [0.4, 0.5, 0.6]])
        mock_sentence_transformer.return_value = mock_model
        
        embedder = Embedder()
        
        chunks = [
            TextChunk("First chunk", "https://example.com", "chunk_001", {}, 0, 11),
            TextChunk("Second chunk", "https://example.com", "chunk_002", {}, 12, 24)
        ]
        
        embedded_chunks = embedder.generate_embeddings(chunks)
        
        assert len(embedded_chunks) == 2
        assert all(isinstance(chunk, EmbeddedChunk) for chunk in embedded_chunks)
        assert embedded_chunks[0].text == "First chunk"
        assert embedded_chunks[1].text == "Second chunk"
        
        # Check that embeddings are properly assigned
        np.testing.assert_array_equal(embedded_chunks[0].embedding, np.array([0.1, 0.2, 0.3]))
        np.testing.assert_array_equal(embedded_chunks[1].embedding, np.array([0.4, 0.5, 0.6]))
    
    @patch('embedder.SentenceTransformer')
    def test_generate_embeddings_batch_processing(self, mock_sentence_transformer):
        """Test batch processing of embeddings for efficiency"""
        mock_model = Mock()
        mock_model.encode.return_value = np.random.rand(5, 384)  # 5 chunks, 384-dim embeddings
        mock_sentence_transformer.return_value = mock_model
        
        embedder = Embedder(batch_size=3)
        
        chunks = [
            TextChunk(f"Chunk {i}", "https://example.com", f"chunk_{i:03d}", {}, i*10, (i+1)*10)
            for i in range(5)
        ]
        
        embedded_chunks = embedder.generate_embeddings(chunks)
        
        assert len(embedded_chunks) == 5
        # Model should be called with batch processing
        mock_model.encode.assert_called_once()
        
        # Check that all chunks have embeddings
        for chunk in embedded_chunks:
            assert chunk.embedding is not None
            assert chunk.embedding.shape[0] == 384  # Expected embedding dimension
    
    def test_process_document_end_to_end(self):
        """Test complete document processing pipeline"""
        with patch('embedder.SentenceTransformer') as mock_st:
            mock_model = Mock()
            mock_model.encode.return_value = np.random.rand(3, 384)
            mock_st.return_value = mock_model
            
            embedder = Embedder(chunk_size=100, chunk_overlap=20)
            
            document_text = "This is a longer document that will be split into chunks. " * 5
            source_url = "https://example.com/document"
            metadata = {"title": "Test Document", "author": "Test Author"}
            
            result = embedder.process_document(document_text, source_url, metadata)
            
            assert isinstance(result, list)
            assert len(result) > 0
            assert all(isinstance(chunk, EmbeddedChunk) for chunk in result)
            
            # Check that metadata is preserved
            for chunk in result:
                assert chunk.source_url == source_url
                assert chunk.metadata["title"] == "Test Document"
                assert chunk.metadata["author"] == "Test Author"
                assert chunk.embedding is not None
    
    def test_embedding_model_configuration(self):
        """Test different embedding model configurations"""
        # Test default model
        embedder1 = Embedder()
        assert embedder1.embedding_model == "all-MiniLM-L6-v2"  # Default model
        
        # Test custom model
        embedder2 = Embedder(embedding_model="all-mpnet-base-v2")
        assert embedder2.embedding_model == "all-mpnet-base-v2"
    
    def test_chunk_size_validation(self):
        """Test validation of chunk size parameters"""
        # Valid parameters
        embedder = Embedder(chunk_size=100, chunk_overlap=20)
        assert embedder.chunk_size == 100
        assert embedder.chunk_overlap == 20
        
        # Invalid parameters should raise ValueError
        with pytest.raises(ValueError):
            Embedder(chunk_size=50, chunk_overlap=60)  # Overlap > chunk_size
        
        with pytest.raises(ValueError):
            Embedder(chunk_size=0)  # Zero chunk size
    
    def test_empty_text_handling(self):
        """Test handling of empty or whitespace-only text"""
        embedder = Embedder()
        
        # Empty text
        chunks = embedder.chunk_text("", source_url="https://example.com")
        assert len(chunks) == 0
        
        # Whitespace only
        chunks = embedder.chunk_text("   \n\t  ", source_url="https://example.com")
        assert len(chunks) == 0
    
    def test_very_long_document_processing(self):
        """Test processing of very long documents"""
        with patch('embedder.SentenceTransformer') as mock_st:
            mock_model = Mock()
            # Simulate processing many chunks
            mock_model.encode.return_value = np.random.rand(50, 384)
            mock_st.return_value = mock_model
            
            embedder = Embedder(chunk_size=200, chunk_overlap=50)
            
            # Create a very long document
            long_text = "This is a sentence in a very long document. " * 1000
            
            result = embedder.process_document(long_text, "https://example.com/long-doc")
            
            assert len(result) > 10  # Should create many chunks
            assert all(chunk.embedding is not None for chunk in result)
    
    def test_chunk_character_positions(self):
        """Test that chunk character positions are accurate"""
        embedder = Embedder(chunk_size=30, chunk_overlap=5)
        
        text = "0123456789" * 10  # 100 characters, easy to verify positions
        chunks = embedder.chunk_text(text, source_url="https://example.com")
        
        for chunk in chunks:
            # Verify that the character positions match the actual text
            actual_text = text[chunk.start_char:chunk.end_char]
            assert chunk.text.strip() in actual_text or actual_text in chunk.text.strip()
    
    @patch('embedder.SentenceTransformer')
    def test_error_handling_embedding_failure(self, mock_st):
        """Test error handling when embedding generation fails"""
        mock_model = Mock()
        mock_model.encode.side_effect = Exception("Embedding model error")
        mock_st.return_value = mock_model
        
        embedder = Embedder()
        chunks = [TextChunk("Test", "https://example.com", "chunk_001", {}, 0, 4)]
        
        with pytest.raises(Exception):
            embedder.generate_embeddings(chunks)
    
    def test_batch_size_configuration(self):
        """Test batch size configuration for embedding generation"""
        embedder1 = Embedder()
        assert embedder1.batch_size == 32  # Default
        
        embedder2 = Embedder(batch_size=16)
        assert embedder2.batch_size == 16


class TestEmbedderIntegration:
    """Integration tests for Embedder with real-world scenarios"""
    
    @patch('embedder.SentenceTransformer')
    def test_embedder_with_document_parser_output(self, mock_st):
        """Test Embedder integration with DocumentParser output"""
        mock_model = Mock()
        mock_model.encode.return_value = np.random.rand(5, 384)
        mock_st.return_value = mock_model
        
        embedder = Embedder(chunk_size=150, chunk_overlap=30)
        
        # Simulate output from DocumentParser
        parsed_content = """
        # Research Paper Title
        
        This is the abstract of a research paper. It contains important information
        about the methodology and findings of the study.
        
        ## Introduction
        
        The introduction provides background context and explains the motivation
        for this research. It references previous work and identifies gaps.
        
        ## Methodology
        
        This section describes the experimental setup and procedures used.
        """
        
        metadata = {
            "title": "Research Paper Title",
            "content_type": "text/markdown",
            "source_url": "https://arxiv.org/abs/1234.5678"
        }
        
        result = embedder.process_document(parsed_content, metadata["source_url"], metadata)
        
        assert len(result) > 2  # Should create multiple chunks
        assert all(chunk.metadata["title"] == "Research Paper Title" for chunk in result)
        assert all(chunk.embedding_model == embedder.embedding_model for chunk in result)
