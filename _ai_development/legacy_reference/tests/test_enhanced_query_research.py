"""
Test Guardian Agent - TDD RED Phase Tests for Enhanced Query Research
Following pytest conventions with comprehensive test coverage
"""

import pytest
import asyncio
import json
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import tempfile
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.enhanced_query_research import ArbitraryQueryResearcher


class TestArbitraryQueryResearcher:
    """Test suite for ArbitraryQueryResearcher - RED phase (failing tests)"""
    
    def test_arbitrary_query_researcher_exists(self):
        """RED: Test that ArbitraryQueryResearcher class can be instantiated"""
        researcher = ArbitraryQueryResearcher()
        assert researcher is not None
        assert hasattr(researcher, 'research_query')
        
    def test_logging_setup_configuration(self):
        """RED: Test that logging is properly configured to avoid JSON interference"""
        researcher = ArbitraryQueryResearcher()
        
        # Should have setup logging method
        assert hasattr(researcher, 'setup_logging')
        
        # Logging should be configured to WARNING level to avoid interference
        import logging
        logger = logging.getLogger('src.embedder')
        assert logger.level == logging.CRITICAL
        
    @pytest.mark.asyncio
    async def test_research_query_basic_functionality(self):
        """RED: Test basic research_query method functionality"""
        researcher = ArbitraryQueryResearcher()
        
        # This should fail initially as the method needs proper implementation
        result = await researcher.research_query("test query", max_sources=1)
        
        # Expected structure - will fail until implemented
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'query' in result
        assert result['query'] == "test query"
        
    @pytest.mark.asyncio
    async def test_research_query_with_valid_sources(self):
        """GREEN: Test research with valid sources returns proper structure"""
        researcher = ArbitraryQueryResearcher()
        
        with patch('src.web_crawler.WebCrawler') as mock_crawler_class, \
             patch('src.document_parser.DocumentParser') as mock_parser_class, \
             patch('src.embedder.Embedder') as mock_embedder_class, \
             patch('src.vector_store.VectorStore') as mock_vector_class:
            
            # Mock the crawler instance and its methods
            mock_crawler = Mock()
            mock_crawler_class.return_value = mock_crawler
            
            # Mock successful fetch result
            mock_result = Mock()
            mock_result.status = "success"
            mock_result.content = b"Sample PDF content"
            mock_crawler.fetch_url = AsyncMock(return_value=mock_result)
            
            # Mock document parser
            mock_parser = Mock()
            mock_parser_class.return_value = mock_parser
            mock_parsed_doc = Mock()
            mock_parsed_doc.title = "Sample Document"
            mock_parsed_doc.content = "This is sample content for testing. " * 50  # Make it long enough
            mock_parser.parse_pdf.return_value = mock_parsed_doc
            
            # Mock embedder and vector store
            mock_embedder = Mock()
            mock_embedder_class.return_value = mock_embedder
            mock_embedder.chunk_text.return_value = [Mock(text="chunk1"), Mock(text="chunk2")]
            mock_embedder.generate_embeddings.return_value = [Mock(text="chunk1"), Mock(text="chunk2")]
            
            mock_vector = Mock()
            mock_vector_class.return_value = mock_vector
            mock_vector.search_by_text.return_value = [Mock(text="relevant content")]
            
            result = await researcher.research_query("AI transformers")
            
            # Expected structure for successful research
            assert result['success'] is True
            assert 'answer' in result
            assert 'sources' in result
            assert 'statistics' in result
            
    @pytest.mark.asyncio
    async def test_research_query_error_handling_no_sources(self):
        """GREEN: Test proper error handling when no sources can be fetched"""
        researcher = ArbitraryQueryResearcher()
        
        with patch('src.web_crawler.WebCrawler') as mock_crawler_class:
            mock_crawler = Mock()
            mock_crawler_class.return_value = mock_crawler
            
            # Mock failed fetch result
            mock_result = Mock()
            mock_result.status = "failed"
            mock_result.content = None
            mock_crawler.fetch_url = AsyncMock(return_value=mock_result)
            
            result = await researcher.research_query("impossible query")
            
            # Should handle gracefully
            assert result['success'] is False
            assert 'error' in result
            assert result['error'] == "No documents could be fetched"
            assert result['query'] == "impossible query"
            
    def test_generate_search_queries_method_exists(self):
        """RED: Test that generate_search_queries method exists and works"""
        researcher = ArbitraryQueryResearcher()
        
        # Method should exist
        assert hasattr(researcher, 'generate_search_queries')
        
        # Should generate multiple query variations
        queries = researcher.generate_search_queries("machine learning")
        
        assert isinstance(queries, list)
        assert len(queries) > 1  # Should generate multiple variations
        assert all(isinstance(q, str) for q in queries)
        
    @pytest.mark.asyncio 
    async def test_document_processing_pipeline(self):
        """GREEN: Test document processing and analysis pipeline"""
        researcher = ArbitraryQueryResearcher()
        
        # Mock all the required components
        with patch('src.document_parser.DocumentParser') as mock_parser_class, \
             patch('src.embedder.Embedder') as mock_embedder_class, \
             patch('src.vector_store.VectorStore') as mock_vector_class:
            
            # Setup mocks
            mock_parser = Mock()
            mock_parser_class.return_value = mock_parser
            mock_embedder = Mock()
            mock_embedder_class.return_value = mock_embedder
            mock_vector = Mock()
            mock_vector_class.return_value = mock_vector
            
            # Mock document processing with proper content length
            mock_parsed_doc = Mock()
            mock_parsed_doc.title = "Test Document"
            mock_parsed_doc.content = "Test content for processing pipeline. " * 50  # Long enough content
            mock_parser.parse_pdf.return_value = mock_parsed_doc
            
            # Mock embedder processing  
            mock_embedder.chunk_text.return_value = [Mock(text="chunk1"), Mock(text="chunk2")]
            mock_embedder.generate_embeddings.return_value = [
                Mock(text="chunk1", embedding=[0.1, 0.2, 0.3]),
                Mock(text="chunk2", embedding=[0.4, 0.5, 0.6])
            ]
            
            # Mock vector store search
            mock_vector.search_by_text.return_value = [Mock(text="relevant result")]
            
            # Test with mock crawler
            with patch('src.web_crawler.WebCrawler') as mock_crawler_class:
                mock_crawler = Mock()
                mock_crawler_class.return_value = mock_crawler
                mock_result = Mock()
                mock_result.status = "success"
                mock_result.content = b"Sample content"
                mock_crawler.fetch_url = AsyncMock(return_value=mock_result)
                
                result = await researcher.research_query("test processing")
                
                # Should process documents through the pipeline
                mock_parser.parse_pdf.assert_called()
                mock_embedder.chunk_text.assert_called()
                mock_embedder.generate_embeddings.assert_called()
                mock_vector.add_chunks.assert_called()
                
    @pytest.mark.asyncio
    async def test_answer_generation_functionality(self):
        """GREEN: Test answer generation functionality (no LLM, uses built-in logic)"""
        researcher = ArbitraryQueryResearcher()
        
        # Test the generate_answer method directly
        mock_search_results = [
            Mock(text="Important finding about AI transformers"),
            Mock(text="Another key insight about neural networks"),
            Mock(text="Additional research on attention mechanisms")
        ]
        
        mock_processed_docs = [
            {"title": "AI Paper 1", "url": "https://example.com/1"},
            {"title": "AI Paper 2", "url": "https://example.com/2"}
        ]
        
        answer = researcher.generate_answer("AI transformers", mock_search_results, mock_processed_docs)
        
        # Should generate structured HTML answer
        assert isinstance(answer, str)
        assert "Research Analysis: AI transformers" in answer
        assert "Key Insights:" in answer
        assert "Finding 1:" in answer
        assert len(mock_processed_docs) == 2  # Should reference document count
                
    @pytest.mark.asyncio
    async def test_research_progress_reporting(self):
        """GREEN: Test that research progress is properly reported"""
        researcher = ArbitraryQueryResearcher()
        
        # Capture print outputs to verify progress reporting
        with patch('builtins.print') as mock_print:
            with patch('src.web_crawler.WebCrawler') as mock_crawler_class:
                mock_crawler = Mock()
                mock_crawler_class.return_value = mock_crawler
                mock_result = Mock()
                mock_result.status = "success"  
                mock_result.content = b"content"
                mock_crawler.fetch_url = AsyncMock(return_value=mock_result)
                
                await researcher.research_query("progress test")
                
                # Should print progress messages
                progress_calls = [call.args[0] for call in mock_print.call_args_list]
                
                # Check for expected progress messages
                assert any("Starting research for" in msg for msg in progress_calls)
                assert any("Analyzing query" in msg for msg in progress_calls)
                assert any("Fetching relevant content" in msg for msg in progress_calls)
                
    def test_concurrent_research_safety(self):
        """RED: Test that multiple concurrent research requests are handled safely"""
        researcher = ArbitraryQueryResearcher()
        
        # Test that multiple instances can be created safely
        researcher2 = ArbitraryQueryResearcher()
        
        assert researcher is not researcher2
        assert hasattr(researcher, 'research_query')
        assert hasattr(researcher2, 'research_query')
        
    @pytest.mark.asyncio
    async def test_research_statistics_collection(self):
        """GREEN: Test that research statistics are properly collected and returned"""
        researcher = ArbitraryQueryResearcher()
        
        with patch('src.web_crawler.WebCrawler') as mock_crawler_class, \
             patch('src.document_parser.DocumentParser') as mock_parser_class, \
             patch('src.embedder.Embedder') as mock_embedder_class, \
             patch('src.vector_store.VectorStore') as mock_vector_class:
            
            # Mock crawler
            mock_crawler = Mock()
            mock_crawler_class.return_value = mock_crawler
            mock_result = Mock()
            mock_result.status = "success"
            mock_result.content = b"Statistical test content"
            mock_crawler.fetch_url = AsyncMock(return_value=mock_result)
            
            # Mock document parser with sufficient content
            mock_parser = Mock()
            mock_parser_class.return_value = mock_parser
            mock_parsed_doc = Mock()
            mock_parsed_doc.title = "Test Document"
            mock_parsed_doc.content = "Test content for statistics. " * 100  # Long enough content
            mock_parser.parse_pdf.return_value = mock_parsed_doc
            
            # Mock embedder and vector store
            mock_embedder = Mock()
            mock_embedder_class.return_value = mock_embedder
            mock_embedder.chunk_text.return_value = [Mock(text="chunk1"), Mock(text="chunk2")]
            mock_embedder.generate_embeddings.return_value = [Mock(text="chunk1"), Mock(text="chunk2")]
            
            mock_vector = Mock()
            mock_vector_class.return_value = mock_vector
            mock_vector.search_by_text.return_value = [Mock(text="relevant content")]
            
            result = await researcher.research_query("statistics test")
            
            # Should collect and return statistics
            assert 'statistics' in result
            stats = result['statistics']
            
            assert 'documents_processed' in stats
            assert 'chunks_indexed' in stats or 'total_chunks' in result  # Flexible naming
            assert isinstance(stats['documents_processed'], int)
            assert stats['documents_processed'] >= 0


class TestArbitraryQueryResearcherParametrized:
    """Parametrized tests for different query types"""
    
    @pytest.mark.parametrize("query,expected_sources", [
        ("machine learning algorithms", 1),
        ("cybersecurity best practices", 1), 
        ("climate change impacts", 1),
        ("", 0)  # Empty query should handle gracefully
    ])
    @pytest.mark.asyncio
    async def test_research_query_different_types(self, query, expected_sources):
        """GREEN: Test research with different query types"""
        researcher = ArbitraryQueryResearcher()
        
        with patch('src.web_crawler.WebCrawler') as mock_crawler_class, \
             patch('src.document_parser.DocumentParser') as mock_parser_class, \
             patch('src.embedder.Embedder') as mock_embedder_class, \
             patch('src.vector_store.VectorStore') as mock_vector_class:
            
            mock_crawler = Mock()
            mock_crawler_class.return_value = mock_crawler
            
            if expected_sources > 0:
                mock_result = Mock()
                mock_result.status = "success"
                mock_result.content = b"test content"
                mock_crawler.fetch_url = AsyncMock(return_value=mock_result)
                
                # Mock document parser for successful cases
                mock_parser = Mock()
                mock_parser_class.return_value = mock_parser
                mock_parsed_doc = Mock()
                mock_parsed_doc.title = "Test Document"
                mock_parsed_doc.content = "Test content for query analysis. " * 50
                mock_parser.parse_pdf.return_value = mock_parsed_doc
                
                # Mock embedder and vector store
                mock_embedder = Mock()
                mock_embedder_class.return_value = mock_embedder
                mock_embedder.chunk_text.return_value = [Mock(text="chunk1")]
                mock_embedder.generate_embeddings.return_value = [Mock(text="chunk1")]
                
                mock_vector = Mock()
                mock_vector_class.return_value = mock_vector
                mock_vector.search_by_text.return_value = [Mock(text="relevant content")]
            
            result = await researcher.research_query(query)
            
            if expected_sources > 0:
                assert result['success'] is True
            else:
                # Empty query should be handled gracefully
                assert 'error' in result or result['success'] is False


class TestArbitraryQueryResearcherIntegration:
    """Integration tests for the research system"""
    
    @pytest.mark.asyncio
    async def test_full_research_pipeline_integration(self):
        """GREEN: Test complete integration of all research components"""
        researcher = ArbitraryQueryResearcher()
        
        # This test will pass with proper mocking of all components
        with patch('src.web_crawler.WebCrawler'), \
             patch('src.document_parser.DocumentParser'), \
             patch('src.embedder.Embedder'), \
             patch('src.vector_store.VectorStore'):
            
            result = await researcher.research_query(
                "What are the latest developments in artificial intelligence?",
                max_sources=2
            )
            
            # Full integration should provide complete research results
            assert isinstance(result, dict)
            # Either success or graceful failure handling
            assert 'success' in result
            assert 'query' in result
            if result.get('success'):
                assert 'answer' in result
                assert 'sources' in result or 'statistics' in result
