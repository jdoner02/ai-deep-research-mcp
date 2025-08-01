#!/usr/bin/env python3
"""
AI Deep Research MCP - Retriever Tests

Test suite for the Retriever component that handles semantic search and ranking
of retrieved chunks from the vector store. Follows TDD principles.

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
from src.retriever import Retriever, RetrievalResult, SearchContext
from src.vector_store import VectorStore, SearchResult
from src.embedder import EmbeddedChunk


class TestRetriever:
    """Test the Retriever component for semantic search and ranking"""
    
    def setup_method(self):
        """Set up test fixtures before each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_vectorstore"
    
    def teardown_method(self):
        """Clean up test fixtures after each test"""
        shutil.rmtree(self.temp_dir)
    
    def test_retriever_exists(self):
        """Test that Retriever class can be instantiated"""
        # Create a vector store for retriever
        vector_store = VectorStore(persist_directory=str(self.db_path))
        
        retriever = Retriever(vector_store=vector_store)
        
        assert retriever is not None
        assert hasattr(retriever, 'search')
        assert hasattr(retriever, 'rank_results')
    
    def test_retrieval_result_dataclass(self):
        """Test RetrievalResult dataclass structure"""
        result = RetrievalResult(
            chunk_id="chunk_001",
            text="Sample retrieved text",
            source_url="https://example.com",
            metadata={"title": "Test Document"},
            relevance_score=0.85,
            rank=1,
            reasoning="High semantic similarity to query"
        )
        
        assert result.chunk_id == "chunk_001"
        assert result.text == "Sample retrieved text"
        assert result.source_url == "https://example.com"
        assert result.metadata == {"title": "Test Document"}
        assert result.relevance_score == 0.85
        assert result.rank == 1
        assert result.reasoning == "High semantic similarity to query"
        
        # Test validation
        with pytest.raises(ValueError):
            RetrievalResult(
                chunk_id="", text="", source_url="",
                metadata={}, relevance_score=-0.1, rank=0
            )
    
    def test_search_context_dataclass(self):
        """Test SearchContext dataclass structure"""
        context = SearchContext(
            query="machine learning applications",
            max_results=10,
            relevance_threshold=0.7,
            filters={"domain": "academic"},
            rerank=True,
            include_reasoning=True
        )
        
        assert context.query == "machine learning applications"
        assert context.max_results == 10
        assert context.relevance_threshold == 0.7
        assert context.filters == {"domain": "academic"}
        assert context.rerank is True
        assert context.include_reasoning is True
    
    def test_basic_search_functionality(self):
        """Test basic semantic search using vector store"""
        vector_store = VectorStore(persist_directory=str(self.db_path))
        retriever = Retriever(vector_store=vector_store)
        
        # Add some test data to vector store
        embeddings = [np.random.rand(384) for _ in range(3)]
        chunks = []
        
        for i, embedding in enumerate(embeddings):
            chunk = EmbeddedChunk(
                text=f"Document {i} about machine learning topic {i}",
                source_url=f"https://example.com/doc{i}",
                chunk_id=f"chunk_{i}",
                metadata={"title": f"ML Doc {i}", "domain": "academic"},
                start_char=0,
                end_char=50,
                embedding=embedding,
                embedding_model="test-model"
            )
            chunks.append(chunk)
        
        vector_store.add_chunks(chunks)
        
        # Search for relevant content
        results = retriever.search("machine learning applications", max_results=2)
        
        assert len(results) <= 2
        assert all(isinstance(r, RetrievalResult) for r in results)
        assert all(r.relevance_score >= 0 and r.relevance_score <= 1 for r in results)
        assert all(r.rank >= 1 for r in results)
        
        # Results should be ranked by relevance
        if len(results) > 1:
            assert results[0].relevance_score >= results[1].relevance_score
    
    def test_search_with_filters(self):
        """Test search with metadata filters"""
        vector_store = VectorStore(persist_directory=str(self.db_path))
        retriever = Retriever(vector_store=vector_store)
        
        # Add test data with different domains
        embeddings = [np.random.rand(384) for _ in range(4)]
        chunks = []
        
        domains = ["academic", "academic", "commercial", "blog"]
        for i, (embedding, domain) in enumerate(zip(embeddings, domains)):
            chunk = EmbeddedChunk(
                text=f"Content {i} about AI research",
                source_url=f"https://example.com/doc{i}",
                chunk_id=f"chunk_{i}",
                metadata={"domain": domain, "year": 2023},
                start_char=0,
                end_char=30,
                embedding=embedding,
                embedding_model="test-model"
            )
            chunks.append(chunk)
        
        vector_store.add_chunks(chunks)
        
        # Search with domain filter
        results = retriever.search(
            "AI research",
            max_results=10,
            filters={"domain": "academic"}
        )
        
        assert len(results) <= 2  # Only 2 academic docs
        assert all(r.metadata.get("domain") == "academic" for r in results)
    
    def test_relevance_threshold_filtering(self):
        """Test filtering results by relevance threshold"""
        vector_store = VectorStore(persist_directory=str(self.db_path))
        retriever = Retriever(vector_store=vector_store)
        
        # Add test data
        embeddings = [np.random.rand(384) for _ in range(3)]
        chunks = []
        
        for i, embedding in enumerate(embeddings):
            chunk = EmbeddedChunk(
                text=f"Document {i} content",
                source_url=f"https://example.com/doc{i}",
                chunk_id=f"chunk_{i}",
                metadata={"title": f"Doc {i}"},
                start_char=0,
                end_char=20,
                embedding=embedding,
                embedding_model="test-model"
            )
            chunks.append(chunk)
        
        vector_store.add_chunks(chunks)
        
        # Search with high threshold
        results_high = retriever.search(
            "document content",
            max_results=10,
            relevance_threshold=0.9
        )
        
        # Search with low threshold
        results_low = retriever.search(
            "document content",
            max_results=10,
            relevance_threshold=0.1
        )
        
        # High threshold should return fewer or equal results
        assert len(results_high) <= len(results_low)
        
        # All results should meet threshold
        assert all(r.relevance_score >= 0.9 for r in results_high)
        assert all(r.relevance_score >= 0.1 for r in results_low)
    
    def test_ranking_algorithm(self):
        """Test result ranking and re-ranking functionality"""
        vector_store = VectorStore(persist_directory=str(self.db_path))
        retriever = Retriever(vector_store=vector_store, enable_reranking=True)
        
        # Mock some search results
        mock_results = [
            SearchResult(
                id="chunk_1", text="Machine learning algorithms", 
                source_url="https://example.com/1",
                metadata={"title": "ML Guide"}, score=0.7, rank=1
            ),
            SearchResult(
                id="chunk_2", text="Deep learning neural networks",
                source_url="https://example.com/2", 
                metadata={"title": "DL Paper"}, score=0.8, rank=2
            ),
            SearchResult(
                id="chunk_3", text="Statistical analysis methods",
                source_url="https://example.com/3",
                metadata={"title": "Stats Book"}, score=0.6, rank=3
            )
        ]
        
        # Test ranking
        ranked_results = retriever.rank_results(
            mock_results, 
            query="machine learning applications"
        )
        
        assert len(ranked_results) == 3
        assert all(isinstance(r, RetrievalResult) for r in ranked_results)
        
        # Should be ranked by relevance (descending)
        for i in range(len(ranked_results) - 1):
            assert ranked_results[i].relevance_score >= ranked_results[i + 1].relevance_score
            assert ranked_results[i].rank == i + 1
    
    def test_search_context_integration(self):
        """Test search using SearchContext object"""
        vector_store = VectorStore(persist_directory=str(self.db_path))
        retriever = Retriever(vector_store=vector_store)
        
        # Add test data
        embedding = np.random.rand(384)
        chunk = EmbeddedChunk(
            text="Advanced machine learning techniques for data analysis",
            source_url="https://example.com/ml-guide",
            chunk_id="chunk_ml",
            metadata={"title": "ML Guide", "category": "tutorial"},
            start_char=0,
            end_char=60,
            embedding=embedding,
            embedding_model="test-model"
        )
        
        vector_store.add_chunks([chunk])
        
        # Create search context
        context = SearchContext(
            query="machine learning data analysis",
            max_results=5,
            relevance_threshold=0.5,
            filters={"category": "tutorial"},
            rerank=True,
            include_reasoning=True
        )
        
        results = retriever.search_with_context(context)
        
        assert len(results) <= 5
        assert all(r.relevance_score >= 0.5 for r in results)
        assert all(r.metadata.get("category") == "tutorial" for r in results)
        assert all(r.reasoning is not None for r in results)  # Should include reasoning
    
    def test_hybrid_search_capability(self):
        """Test hybrid search combining semantic and keyword matching"""
        vector_store = VectorStore(persist_directory=str(self.db_path))
        retriever = Retriever(vector_store=vector_store, hybrid_search=True)
        
        # Add diverse test data
        embeddings = [np.random.rand(384) for _ in range(3)]
        texts = [
            "Machine learning algorithms for classification",
            "Deep neural networks and backpropagation",
            "Natural language processing with transformers"
        ]
        
        chunks = []
        for i, (embedding, text) in enumerate(zip(embeddings, texts)):
            chunk = EmbeddedChunk(
                text=text,
                source_url=f"https://example.com/doc{i}",
                chunk_id=f"chunk_{i}",
                metadata={"title": f"AI Doc {i}"},
                start_char=0,
                end_char=len(text),
                embedding=embedding,
                embedding_model="test-model"
            )
            chunks.append(chunk)
        
        vector_store.add_chunks(chunks)
        
        # Search with exact keyword match preference
        results = retriever.search(
            "neural networks",
            max_results=10,
            hybrid_search=True
        )
        
        assert len(results) > 0
        # Result with exact keyword match should rank higher
        top_result = results[0]
        assert "neural networks" in top_result.text.lower()
    
    def test_empty_search_handling(self):
        """Test handling of empty search results"""
        vector_store = VectorStore(persist_directory=str(self.db_path))
        retriever = Retriever(vector_store=vector_store)
        
        # Search empty vector store
        results = retriever.search("machine learning", max_results=5)
        
        assert results == []
        assert isinstance(results, list)
    
    def test_search_performance_metrics(self):
        """Test retrieval performance monitoring"""
        vector_store = VectorStore(persist_directory=str(self.db_path))
        retriever = Retriever(vector_store=vector_store, track_performance=True)
        
        # Add test data
        embedding = np.random.rand(384)
        chunk = EmbeddedChunk(
            text="Performance monitoring for search systems",
            source_url="https://example.com/perf",
            chunk_id="chunk_perf",
            metadata={"title": "Performance Guide"},
            start_char=0,
            end_char=50,
            embedding=embedding,
            embedding_model="test-model"
        )
        
        vector_store.add_chunks([chunk])
        
        # Perform search
        results = retriever.search("search performance", max_results=5)
        
        # Check performance metrics
        metrics = retriever.get_performance_metrics()
        
        assert "search_time" in metrics
        assert "total_searches" in metrics
        assert "avg_results_per_search" in metrics
        assert metrics["total_searches"] >= 1
    
    def test_error_handling_invalid_query(self):
        """Test error handling for invalid queries"""
        vector_store = VectorStore(persist_directory=str(self.db_path))
        retriever = Retriever(vector_store=vector_store)
        
        # Test empty query
        with pytest.raises(ValueError):
            retriever.search("", max_results=5)
        
        # Test None query
        with pytest.raises(ValueError):
            retriever.search(None, max_results=5)
        
        # Test invalid max_results
        with pytest.raises(ValueError):
            retriever.search("valid query", max_results=0)
        
        with pytest.raises(ValueError):
            retriever.search("valid query", max_results=-1)
    
    def test_concurrent_search_operations(self):
        """Test thread-safe concurrent search operations"""
        import threading
        import time
        
        vector_store = VectorStore(persist_directory=str(self.db_path))
        retriever = Retriever(vector_store=vector_store)
        
        # Add test data
        embeddings = [np.random.rand(384) for _ in range(5)]
        chunks = []
        
        for i, embedding in enumerate(embeddings):
            chunk = EmbeddedChunk(
                text=f"Concurrent search test document {i}",
                source_url=f"https://example.com/concurrent{i}",
                chunk_id=f"chunk_concurrent_{i}",
                metadata={"title": f"Concurrent Doc {i}"},
                start_char=0,
                end_char=40,
                embedding=embedding,
                embedding_model="test-model"
            )
            chunks.append(chunk)
        
        vector_store.add_chunks(chunks)
        
        results = []
        errors = []
        
        def search_worker(query_suffix):
            try:
                result = retriever.search(f"concurrent test {query_suffix}", max_results=3)
                results.append(result)
            except Exception as e:
                errors.append(e)
        
        # Launch concurrent searches
        threads = []
        for i in range(3):
            t = threading.Thread(target=search_worker, args=(i,))
            threads.append(t)
            t.start()
        
        # Wait for all threads
        for t in threads:
            t.join()
        
        assert len(errors) == 0  # No errors should occur
        assert len(results) == 3  # All searches should complete
        assert all(isinstance(r, list) for r in results)


class TestRetrieverIntegration:
    """Integration tests for Retriever with other components"""
    
    def setup_method(self):
        """Set up test fixtures before each test"""
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = Path(self.temp_dir) / "test_vectorstore"
    
    def teardown_method(self):
        """Clean up test fixtures after each test"""
        shutil.rmtree(self.temp_dir)
    
    def test_end_to_end_retrieval_pipeline(self):
        """Test complete retrieval pipeline from embedding to results"""
        # This test simulates the full pipeline:
        # Query -> Embedding -> Vector Search -> Ranking -> Results
        
        vector_store = VectorStore(persist_directory=str(self.db_path))
        retriever = Retriever(
            vector_store=vector_store,
            enable_reranking=True,
            hybrid_search=True
        )
        
        # Simulate realistic academic content
        realistic_content = [
            {
                "text": "Machine learning algorithms have revolutionized data analysis by enabling computers to learn patterns from large datasets without explicit programming.",
                "title": "Introduction to Machine Learning",
                "domain": "academic"
            },
            {
                "text": "Deep neural networks utilize multiple layers of interconnected nodes to process information, mimicking the structure of biological neural networks.",
                "title": "Deep Learning Fundamentals", 
                "domain": "academic"
            },
            {
                "text": "Natural language processing techniques enable computers to understand, interpret, and generate human language through statistical and machine learning methods.",
                "title": "NLP Overview",
                "domain": "academic"  
            },
            {
                "text": "Computer vision applications use convolutional neural networks to automatically identify and classify objects in digital images and videos.",
                "title": "Computer Vision with CNNs",
                "domain": "academic"
            }
        ]
        
        # Add realistic content to vector store
        chunks = []
        for i, content in enumerate(realistic_content):
            embedding = np.random.rand(384)
            chunk = EmbeddedChunk(
                text=content["text"],
                source_url=f"https://academic.example.com/paper{i}",
                chunk_id=f"academic_chunk_{i}",
                metadata={"title": content["title"], "domain": content["domain"]},
                start_char=0,
                end_char=len(content["text"]),
                embedding=embedding,
                embedding_model="test-model"
            )
            chunks.append(chunk)
        
        vector_store.add_chunks(chunks)
        
        # Mock the search_by_text method to avoid embedding model issues
        mock_search_results = [
            SearchResult(
                id="academic_chunk_1",
                text="Deep neural networks utilize multiple layers of interconnected nodes to process information, mimicking the structure of biological neural networks.",
                source_url="https://academic.example.com/paper1",
                metadata={"title": "Deep Learning Fundamentals", "domain": "academic"},
                score=0.85,
                rank=1
            ),
            SearchResult(
                id="academic_chunk_0", 
                text="Machine learning algorithms have revolutionized data analysis by enabling computers to learn patterns from large datasets without explicit programming.",
                source_url="https://academic.example.com/paper0",
                metadata={"title": "Introduction to Machine Learning", "domain": "academic"},
                score=0.75,
                rank=2
            )
        ]
        
        # Mock vector store search to return our test results
        from unittest.mock import patch
        with patch.object(vector_store, 'search_by_text', return_value=mock_search_results):
            # Perform comprehensive search
            results = retriever.search(
                "neural networks deep learning applications",
                max_results=10,
                relevance_threshold=0.3,
                filters={"domain": "academic"}
            )
        
        # Validate results
        assert len(results) > 0
        assert len(results) <= 10
        assert all(isinstance(r, RetrievalResult) for r in results)
        assert all(r.metadata.get("domain") == "academic" for r in results)
        assert all(r.relevance_score >= 0.3 for r in results)
        
        # Check ranking quality
        if len(results) > 1:
            for i in range(len(results) - 1):
                assert results[i].relevance_score >= results[i + 1].relevance_score
                assert results[i].rank <= results[i + 1].rank
        
        # Verify result contains expected content
        result_texts = [r.text.lower() for r in results]
        neural_network_found = any("neural network" in text for text in result_texts)
        assert neural_network_found, "Should find content about neural networks"
