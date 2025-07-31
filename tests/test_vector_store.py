#!/usr/bin/env python3
"""
AI Deep Research MCP - VectorStore Tests

Test suite for the VectorStore component that handles vector database storage
and retrieval for semantic search capabilities. Follows TDD principles.

PHASE: RED - Writing failing tests first
"""

import pytest
import numpy as np
import tempfile
import shutil
from pathlib import Path
from typing import List, Dict, Any, Optional
from unittest.mock import Mock, patch, MagicMock

# Import from src package using the fixed import system
from src.vector_store import VectorStore, StoredChunk, SearchResult
from src.embedder import EmbeddedChunk


class TestVectorStore:
    """Test the VectorStore component for vector database operations"""
    
    def setup_method(self):
        """Set up test fixtures before each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_vectorstore"
    
    def teardown_method(self):
        """Clean up after each test"""
        if hasattr(self, 'temp_dir') and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_vector_store_exists(self):
        """Test that VectorStore class can be instantiated"""
        store = VectorStore(persist_directory=str(self.db_path))
        assert store is not None
        assert hasattr(store, 'collection_name')
        assert hasattr(store, 'persist_directory')
    
    def test_stored_chunk_dataclass(self):
        """Test StoredChunk dataclass structure"""
        embedding = np.array([0.1, 0.2, 0.3, 0.4])
        
        chunk = StoredChunk(
            id="chunk_001",
            text="Sample text chunk",
            source_url="https://example.com",
            metadata={"title": "Test Document"},
            embedding=embedding,
            embedding_model="test-model",
            timestamp="2025-07-30T12:00:00Z"
        )
        
        assert chunk.id == "chunk_001"
        assert chunk.text == "Sample text chunk"
        assert chunk.source_url == "https://example.com"
        assert chunk.metadata["title"] == "Test Document"
        assert np.array_equal(chunk.embedding, embedding)
        assert chunk.embedding_model == "test-model"
        assert chunk.timestamp == "2025-07-30T12:00:00Z"
    
    def test_search_result_dataclass(self):
        """Test SearchResult dataclass structure"""
        result = SearchResult(
            id="chunk_001",
            text="Sample text chunk",
            source_url="https://example.com",
            metadata={"title": "Test Document"},
            score=0.85,
            rank=1
        )
        
        assert result.id == "chunk_001"
        assert result.text == "Sample text chunk"
        assert result.source_url == "https://example.com"
        assert result.score == 0.85
        assert result.rank == 1
    
    def test_initialize_collection(self):
        """Test vector store collection initialization"""
        store = VectorStore(persist_directory=str(self.db_path))
        
        # Should create collection
        assert store.collection is not None
        assert store.collection_name == "research_documents"
        
        # Should be able to reinitialize with same path
        store2 = VectorStore(persist_directory=str(self.db_path))
        assert store2.collection is not None
    
    def test_add_single_chunk(self):
        """Test adding a single embedded chunk to the vector store"""
        store = VectorStore(persist_directory=str(self.db_path))
        
        # Create test chunk
        embedding = np.random.rand(384)  # Standard sentence transformer size
        chunk = EmbeddedChunk(
            text="This is a test document about machine learning.",
            source_url="https://example.com/ml-guide",
            chunk_id="chunk_001",
            metadata={"title": "ML Guide", "author": "Test Author"},
            start_char=0,
            end_char=45,
            embedding=embedding,
            embedding_model="all-MiniLM-L6-v2"
        )
        
        # Add chunk
        result = store.add_chunk(chunk)
        
        assert result is True
        assert store.get_collection_size() == 1
    
    def test_add_multiple_chunks(self):
        """Test adding multiple chunks at once"""
        store = VectorStore(persist_directory=str(self.db_path))
        
        # Create test chunks
        chunks = []
        for i in range(5):
            embedding = np.random.rand(384)
            chunk = EmbeddedChunk(
                text=f"This is test document {i} about various topics.",
                source_url=f"https://example.com/doc{i}",
                chunk_id=f"chunk_{i:03d}",
                metadata={"title": f"Document {i}", "topic": f"topic_{i}"},
                start_char=0,
                end_char=40,
                embedding=embedding,
                embedding_model="all-MiniLM-L6-v2"
            )
            chunks.append(chunk)
        
        # Add chunks
        result = store.add_chunks(chunks)
        
        assert result is True
        assert store.get_collection_size() == 5
    
    def test_search_by_vector(self):
        """Test vector similarity search"""
        store = VectorStore(persist_directory=str(self.db_path))
        
        # Add some test data
        embeddings = [np.random.rand(384) for _ in range(3)]
        chunks = []
        
        for i, embedding in enumerate(embeddings):
            chunk = EmbeddedChunk(
                text=f"Document {i} about topic {i}",
                source_url=f"https://example.com/doc{i}",
                chunk_id=f"chunk_{i}",
                metadata={"title": f"Doc {i}"},
                start_char=0,
                end_char=20,
                embedding=embedding,
                embedding_model="test-model"
            )
            chunks.append(chunk)
        
        store.add_chunks(chunks)
        
        # Search with the first embedding (should be most similar to itself)
        results = store.search_by_vector(embeddings[0], top_k=2)
        
        assert len(results) <= 2
        assert all(isinstance(r, SearchResult) for r in results)
        assert results[0].score >= results[1].score  # Results should be ranked
        assert "chunk_0" in results[0].id  # First result should be the exact match
    
    def test_search_by_text(self):
        """Test text-based similarity search"""
        store = VectorStore(persist_directory=str(self.db_path))
        
        # Add test data with known content
        test_docs = [
            "Machine learning is a subset of artificial intelligence",
            "Deep learning uses neural networks with many layers",
            "Natural language processing handles text and speech",
            "Computer vision analyzes and interprets visual data"
        ]
        
        chunks = []
        for i, text in enumerate(test_docs):
            # Create deterministic embedding based on text
            embedding = np.array([hash(text) % 1000 / 1000.0] * 384)
            
            chunk = EmbeddedChunk(
                text=text,
                source_url=f"https://example.com/ai-doc{i}",
                chunk_id=f"ai_chunk_{i}",
                metadata={"title": f"AI Document {i}"},
                start_char=0,
                end_char=len(text),
                embedding=embedding,
                embedding_model="test-model"
            )
            chunks.append(chunk)
        
        store.add_chunks(chunks)
        
        # Search for machine learning content
        with patch.object(store, '_embed_query') as mock_embed:
            mock_embed.return_value = np.array([hash("machine learning") % 1000 / 1000.0] * 384)
            
            results = store.search_by_text("machine learning algorithms", top_k=2)
            
            assert len(results) <= 2
            assert all(isinstance(r, SearchResult) for r in results)
            mock_embed.assert_called_once_with("machine learning algorithms")
    
    def test_search_with_filters(self):
        """Test search with metadata filters"""
        store = VectorStore(persist_directory=str(self.db_path))
        
        # Add chunks with different metadata
        chunks = []
        topics = ["AI", "ML", "NLP", "CV"]
        
        for i, topic in enumerate(topics):
            embedding = np.random.rand(384)
            chunk = EmbeddedChunk(
                text=f"Content about {topic}",
                source_url=f"https://example.com/{topic.lower()}",
                chunk_id=f"{topic.lower()}_chunk",
                metadata={"topic": topic, "year": 2024 + i % 2},
                start_char=0,
                end_char=15,
                embedding=embedding,
                embedding_model="test-model"
            )
            chunks.append(chunk)
        
        store.add_chunks(chunks)
        
        # Search with topic filter
        query_vector = np.random.rand(384)
        results = store.search_by_vector(
            query_vector, 
            top_k=10, 
            filters={"topic": "AI"}
        )
        
        assert len(results) == 1
        assert results[0].metadata["topic"] == "AI"
    
    def test_delete_chunk(self):
        """Test deleting a chunk from the vector store"""
        store = VectorStore(persist_directory=str(self.db_path))
        
        # Add a chunk
        embedding = np.random.rand(384)
        chunk = EmbeddedChunk(
            text="Test content to delete",
            source_url="https://example.com/delete-test",
            chunk_id="delete_me",
            metadata={"title": "Delete Test"},
            start_char=0,
            end_char=21,
            embedding=embedding,
            embedding_model="test-model"
        )
        
        store.add_chunk(chunk)
        assert store.get_collection_size() == 1
        
        # Delete the chunk
        result = store.delete_chunk("delete_me")
        
        assert result is True
        assert store.get_collection_size() == 0
    
    def test_delete_by_source(self):
        """Test deleting all chunks from a specific source"""
        store = VectorStore(persist_directory=str(self.db_path))
        
        # Add chunks from different sources
        sources = ["https://example.com/doc1", "https://example.com/doc2", "https://other.com/doc3"]
        
        for i, source in enumerate(sources):
            embedding = np.random.rand(384)
            chunk = EmbeddedChunk(
                text=f"Content from source {i}",
                source_url=source,
                chunk_id=f"chunk_{i}",
                metadata={"source_index": i},
                start_char=0,
                end_char=20,
                embedding=embedding,
                embedding_model="test-model"
            )
            store.add_chunk(chunk)
        
        assert store.get_collection_size() == 3
        
        # Delete chunks from first source
        result = store.delete_by_source("https://example.com/doc1")
        
        assert result is True
        assert store.get_collection_size() == 2
        
        # Verify remaining chunks are from other sources
        remaining = store.search_by_vector(np.random.rand(384), top_k=10)
        source_urls = {r.source_url for r in remaining}
        assert "https://example.com/doc1" not in source_urls
    
    def test_clear_collection(self):
        """Test clearing entire collection"""
        store = VectorStore(persist_directory=str(self.db_path))
        
        # Add some chunks
        chunks = []
        for i in range(3):
            embedding = np.random.rand(384)
            chunk = EmbeddedChunk(
                text=f"Content {i}",
                source_url=f"https://example.com/doc{i}",
                chunk_id=f"chunk_{i}",
                metadata={},
                start_char=0,
                end_char=10,
                embedding=embedding,
                embedding_model="test-model"
            )
            chunks.append(chunk)
        
        store.add_chunks(chunks)
        assert store.get_collection_size() == 3
        
        # Clear collection
        result = store.clear_collection()
        
        assert result is True
        assert store.get_collection_size() == 0
    
    def test_get_chunk_by_id(self):
        """Test retrieving a specific chunk by ID"""
        store = VectorStore(persist_directory=str(self.db_path))
        
        # Add a chunk
        embedding = np.random.rand(384)
        original_chunk = EmbeddedChunk(
            text="Specific content to retrieve",
            source_url="https://example.com/specific",
            chunk_id="specific_chunk",
            metadata={"title": "Specific Document"},
            start_char=0,
            end_char=27,
            embedding=embedding,
            embedding_model="test-model"
        )
        
        store.add_chunk(original_chunk)
        
        # Retrieve the chunk
        retrieved = store.get_chunk_by_id("specific_chunk")
        
        assert retrieved is not None
        assert isinstance(retrieved, StoredChunk)
        assert retrieved.id == "specific_chunk"
        assert retrieved.text == "Specific content to retrieve"
        assert retrieved.source_url == "https://example.com/specific"
    
    def test_list_sources(self):
        """Test listing all unique sources in the collection"""
        store = VectorStore(persist_directory=str(self.db_path))
        
        # Add chunks from different sources
        sources = [
            "https://example.com/doc1",
            "https://example.com/doc2", 
            "https://other.com/doc1",
            "https://example.com/doc1"  # Duplicate
        ]
        
        for i, source in enumerate(sources):
            embedding = np.random.rand(384)
            chunk = EmbeddedChunk(
                text=f"Content {i}",
                source_url=source,
                chunk_id=f"chunk_{i}",
                metadata={},
                start_char=0,
                end_char=10,
                embedding=embedding,
                embedding_model="test-model"
            )
            store.add_chunk(chunk)
        
        # Get unique sources
        unique_sources = store.list_sources()
        
        assert len(unique_sources) == 3  # Should deduplicate
        assert "https://example.com/doc1" in unique_sources
        assert "https://example.com/doc2" in unique_sources
        assert "https://other.com/doc1" in unique_sources
    
    def test_get_collection_stats(self):
        """Test getting collection statistics"""
        store = VectorStore(persist_directory=str(self.db_path))
        
        # Add some test data
        chunks = []
        for i in range(5):
            embedding = np.random.rand(384)
            chunk = EmbeddedChunk(
                text=f"Content {i}" * 10,  # Variable length
                source_url=f"https://example.com/doc{i % 2}",  # 2 unique sources
                chunk_id=f"chunk_{i}",
                metadata={"category": "test"},
                start_char=0,
                end_char=len(f"Content {i}" * 10),
                embedding=embedding,
                embedding_model="test-model"
            )
            chunks.append(chunk)
        
        store.add_chunks(chunks)
        
        # Get stats
        stats = store.get_collection_stats()
        
        assert isinstance(stats, dict)
        assert stats["total_chunks"] == 5
        assert stats["unique_sources"] == 2
        assert "embedding_models" in stats  # Changed from singular to plural
        assert isinstance(stats["embedding_models"], list)
        assert "avg_chunk_length" in stats
    
    def test_persistence(self):
        """Test that data persists across VectorStore instances"""
        # Create store and add data
        store1 = VectorStore(persist_directory=str(self.db_path))
        
        embedding = np.random.rand(384)
        chunk = EmbeddedChunk(
            text="Persistent content",
            source_url="https://example.com/persistent",
            chunk_id="persistent_chunk",
            metadata={"persistent": True},
            start_char=0,
            end_char=18,
            embedding=embedding,
            embedding_model="test-model"
        )
        
        store1.add_chunk(chunk)
        assert store1.get_collection_size() == 1
        
        # Create new store instance with same path
        store2 = VectorStore(persist_directory=str(self.db_path))
        
        # Should load existing data
        assert store2.get_collection_size() == 1
        
        # Should be able to retrieve the chunk
        retrieved = store2.get_chunk_by_id("persistent_chunk")
        assert retrieved is not None
        assert retrieved.text == "Persistent content"
    
    def test_embedding_dimension_validation(self):
        """Test validation of embedding dimensions"""
        store = VectorStore(persist_directory=str(self.db_path), embedding_dimension=256)
        
        # Wrong dimension should raise error
        wrong_embedding = np.random.rand(384)  # Should be 256
        chunk = EmbeddedChunk(
            text="Test content",
            source_url="https://example.com/test",
            chunk_id="test_chunk",
            metadata={},
            start_char=0,
            end_char=12,
            embedding=wrong_embedding,
            embedding_model="test-model"
        )
        
        with pytest.raises(ValueError, match="dimension"):
            store.add_chunk(chunk)
    
    def test_concurrent_access(self):
        """Test thread-safe access to vector store"""
        import threading
        
        store = VectorStore(persist_directory=str(self.db_path))
        
        def add_chunks_worker(worker_id):
            chunks = []
            for i in range(5):
                embedding = np.random.rand(384)
                chunk = EmbeddedChunk(
                    text=f"Worker {worker_id} content {i}",
                    source_url=f"https://example.com/worker{worker_id}",
                    chunk_id=f"worker{worker_id}_chunk{i}",
                    metadata={"worker": worker_id},
                    start_char=0,
                    end_char=20,
                    embedding=embedding,
                    embedding_model="test-model"
                )
                chunks.append(chunk)
            
            store.add_chunks(chunks)
        
        # Run multiple workers concurrently
        threads = []
        for worker_id in range(3):
            thread = threading.Thread(target=add_chunks_worker, args=(worker_id,))
            threads.append(thread)
            thread.start()
        
        # Wait for all threads to complete
        for thread in threads:
            thread.join()
        
        # Should have all chunks from all workers
        assert store.get_collection_size() == 15  # 3 workers * 5 chunks each


class TestVectorStoreIntegration:
    """Integration tests for VectorStore with other components"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "integration_test"
    
    def teardown_method(self):
        """Clean up after tests"""
        if hasattr(self, 'temp_dir') and Path(self.temp_dir).exists():
            shutil.rmtree(self.temp_dir)
    
    def test_integration_with_embedder_output(self):
        """Test VectorStore with real Embedder output"""
        # This test would use the actual Embedder component
        # For now, we simulate its output structure
        
        store = VectorStore(persist_directory=str(self.db_path))
        
        # Simulate embedded chunks from document processing
        embedded_chunks = []
        documents = [
            "Artificial intelligence is transforming healthcare through diagnostic tools.",
            "Machine learning algorithms can analyze medical images with high accuracy.",
            "Natural language processing helps extract insights from clinical notes."
        ]
        
        for i, text in enumerate(documents):
            # Simulate realistic embedding
            embedding = np.random.rand(384)
            
            chunk = EmbeddedChunk(
                text=text,
                source_url=f"https://medical-ai.com/article{i}",
                chunk_id=f"medical_chunk_{i}",
                metadata={
                    "title": f"AI in Healthcare - Part {i+1}",
                    "domain": "healthcare",
                    "chunk_index": i,
                    "chunk_count": len(documents)
                },
                start_char=i * 100,
                end_char=(i * 100) + len(text),
                embedding=embedding,
                embedding_model="all-MiniLM-L6-v2"
            )
            embedded_chunks.append(chunk)
        
        # Add to vector store
        result = store.add_chunks(embedded_chunks)
        assert result is True
        
        # Test search functionality
        query_embedding = np.random.rand(384)
        results = store.search_by_vector(query_embedding, top_k=2)
        
        assert len(results) == 2
        assert all(r.metadata["domain"] == "healthcare" for r in results)
        # Verify results contain expected content (at least some medical terms)
        all_text = " ".join(r.text for r in results)
        medical_terms = ["artificial", "intelligence", "machine", "learning", "language", "processing", "healthcare", "medical", "diagnostic", "clinical"]
        assert any(term.lower() in all_text.lower() for term in medical_terms)
