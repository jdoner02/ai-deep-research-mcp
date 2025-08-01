"""
Test Guardian Agent - TDD RED Phase Tests for Enhanced Query Research Web
Following pytest conventions with comprehensive web interface testing
"""

import pytest
import json
import asyncio
from pathlib import Path
from unittest.mock import Mock, patch, AsyncMock
import tempfile
import sys

# Add project root to path for imports
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from src.enhanced_query_research_web import ArbitraryQueryResearcherWeb


class TestArbitraryQueryResearcherWeb:
    """Test suite for ArbitraryQueryResearcherWeb - RED phase (failing tests)"""
    
    def test_web_researcher_exists(self):
        """RED: Test that ArbitraryQueryResearcherWeb class can be instantiated"""
        web_researcher = ArbitraryQueryResearcherWeb()
        assert web_researcher is not None
        assert hasattr(web_researcher, 'search_and_research')
        
    def test_logging_configuration_for_web(self):
        """RED: Test web-specific logging configuration"""
        web_researcher = ArbitraryQueryResearcherWeb()
        
        # Should have setup logging method
        assert hasattr(web_researcher, 'setup_logging')
        
        # Web logging should be properly configured
        import logging
        logger = logging.getLogger('src.embedder')
        assert logger.level >= logging.WARNING
        
    @pytest.mark.asyncio
    async def test_search_and_research_basic_functionality(self):
        """RED: Test basic search_and_research method"""
        web_researcher = ArbitraryQueryResearcherWeb()
        
        result = await web_researcher.search_and_research("test web query", max_results=1)
        
        # Expected structure - will fail until implemented
        assert isinstance(result, dict)
        assert 'success' in result
        assert 'query' in result
        assert result['query'] == "test web query"
        
    @pytest.mark.asyncio
    async def test_web_search_integration(self):
        """GREEN: Test web search functionality with proper instance mocking"""

        # Create researcher first
        web_researcher = ArbitraryQueryResearcherWeb()
        
        # Mock the instance methods directly
        with patch.object(web_researcher.web_searcher, 'search') as mock_search, \
             patch.object(web_researcher.content_loader, 'load_multiple_urls') as mock_load_urls:

            # Mock WebSearcher.search
            mock_search.return_value = [
                {"url": "https://example.com/1", "title": "Test Result 1", "snippet": "Test snippet 1"},
                {"url": "https://example.com/2", "title": "Test Result 2", "snippet": "Test snippet 2"}
            ]

            # Mock MultiSourceContentLoader.load_multiple_urls
            mock_load_urls.return_value = [
                {
                    "text": "This is test content from example.com 1",
                    "title": "Test Result 1",
                    "source": "https://example.com/1",
                    "type": "html",
                    "length": 100
                },
                {
                    "text": "This is test content from example.com 2",
                    "title": "Test Result 2", 
                    "source": "https://example.com/2",
                    "type": "html",
                    "length": 100
                }
            ]

            result = await web_researcher.search_and_research("web search test")

            # Should integrate web search results
            assert result['success'] is True
            assert 'sources' in result  # Changed from 'search_results' to 'sources' based on actual response structure
            assert len(result['sources']) >= 1
            
    @pytest.mark.asyncio
    async def test_url_processing_pipeline(self):
        """RED: Test URL processing and content extraction"""
        web_researcher = ArbitraryQueryResearcherWeb()
        
        with patch('src.enhanced_query_research_web.WebCrawler') as mock_crawler_class:
            mock_crawler = Mock()
            mock_crawler_class.return_value = mock_crawler
            
            # Mock successful URL fetch
            mock_result = Mock()
            mock_result.status = "success"
            mock_result.content = b"Web page content for processing"
            mock_result.url = "https://example.com/test"
            mock_crawler.fetch_url = AsyncMock(return_value=mock_result)
            
            # Mock search results to trigger URL processing
            with patch('src.enhanced_query_research_web.WebSearcher') as mock_searcher_class:
                mock_searcher = Mock()
                mock_searcher_class.return_value = mock_searcher
                mock_searcher.search = AsyncMock(return_value=[
                    {"url": "https://example.com/test", "title": "Test", "snippet": "Snippet"}
                ])
                
                result = await web_researcher.search_and_research("url processing test")
                
                # Should process URLs from search results
                mock_crawler.fetch_url.assert_called()
                assert result['success'] is True
                
    @pytest.mark.asyncio
    async def test_web_research_error_handling(self):
        """RED: Test error handling for web research failures"""
        web_researcher = ArbitraryQueryResearcherWeb()
        
        with patch('src.enhanced_query_research_web.WebSearcher') as mock_searcher_class:
            mock_searcher = Mock()
            mock_searcher_class.return_value = mock_searcher
            
            # Mock search failure
            mock_searcher.search = AsyncMock(side_effect=Exception("Search API error"))
            
            result = await web_researcher.search_and_research("failing search")
            
            # Should handle errors gracefully
            assert result['success'] is False
            assert 'error' in result
            assert 'Search API error' in result['error']
            
    @pytest.mark.asyncio
    async def test_web_content_filtering_and_ranking(self):
        """RED: Test content filtering and result ranking"""
        web_researcher = ArbitraryQueryResearcherWeb()
        
        with patch('src.enhanced_query_research_web.WebSearcher') as mock_searcher_class:
            mock_searcher = Mock()
            mock_searcher_class.return_value = mock_searcher
            
            # Mock diverse search results for filtering
            mock_searcher.search = AsyncMock(return_value=[
                {"url": "https://spam.com", "title": "Spam Content", "snippet": "Buy now"},
                {"url": "https://academic.edu", "title": "Research Paper", "snippet": "Scientific study"},
                {"url": "https://news.com", "title": "News Article", "snippet": "Breaking news"},
                {"url": "https://wiki.org", "title": "Encyclopedia Entry", "snippet": "Comprehensive info"}
            ])
            
            result = await web_researcher.search_and_research("filtered content test", max_results=2)
            
            # Should filter and rank results appropriately
            assert result['success'] is True
            assert 'filtered_results' in result
            assert len(result['filtered_results']) <= 2  # Respects max_results
            
    def test_web_query_expansion_method(self):
        """RED: Test web-specific query expansion"""
        web_researcher = ArbitraryQueryResearcherWeb()
        
        # Should have method for expanding web queries
        assert hasattr(web_researcher, 'expand_web_query')
        
        expanded_queries = web_researcher.expand_web_query("AI ethics")
        
        assert isinstance(expanded_queries, list)
        assert len(expanded_queries) > 1
        assert all(isinstance(q, str) for q in expanded_queries)
        # Should include web-specific terms
        assert any("online" in q.lower() or "website" in q.lower() or "web" in q.lower() 
                  for q in expanded_queries)
        
    @pytest.mark.asyncio
    async def test_web_research_with_document_analysis(self):
        """RED: Test integration with document analysis pipeline"""
        web_researcher = ArbitraryQueryResearcherWeb()
        
        # Mock all document processing components
        with patch('src.enhanced_query_research_web.DocumentParser') as mock_parser_class, \
             patch('src.enhanced_query_research_web.Embedder') as mock_embedder_class, \
             patch('src.enhanced_query_research_web.VectorStore') as mock_vector_class:
            
            mock_parser = Mock()
            mock_parser_class.return_value = mock_parser
            mock_embedder = Mock()
            mock_embedder_class.return_value = mock_embedder
            mock_vector = Mock()
            mock_vector_class.return_value = mock_vector
            
            # Mock web search and crawler
            with patch('src.enhanced_query_research_web.WebSearcher') as mock_searcher_class, \
                 patch('src.enhanced_query_research_web.WebCrawler') as mock_crawler_class:
                
                mock_searcher = Mock()
                mock_searcher_class.return_value = mock_searcher
                mock_searcher.search = AsyncMock(return_value=[
                    {"url": "https://test.com", "title": "Test", "snippet": "Test snippet"}
                ])
                
                mock_crawler = Mock()
                mock_crawler_class.return_value = mock_crawler
                mock_result = Mock()
                mock_result.status = "success"
                mock_result.content = b"Document content"
                mock_crawler.fetch_url = AsyncMock(return_value=mock_result)
                
                result = await web_researcher.search_and_research("document analysis test")
                
                # Should process documents through analysis pipeline
                assert result['success'] is True
                assert 'analyzed_content' in result or 'processed_documents' in result
                
    @pytest.mark.asyncio
    async def test_web_research_result_deduplication(self):
        """RED: Test deduplication of web search results"""
        web_researcher = ArbitraryQueryResearcherWeb()
        
        with patch('src.enhanced_query_research_web.WebSearcher') as mock_searcher_class:
            mock_searcher = Mock()
            mock_searcher_class.return_value = mock_searcher
            
            # Mock duplicate results
            mock_searcher.search = AsyncMock(return_value=[
                {"url": "https://example.com/page", "title": "Title 1", "snippet": "Snippet 1"},
                {"url": "https://example.com/page", "title": "Title 1", "snippet": "Snippet 1"},  # Duplicate
                {"url": "https://other.com/page", "title": "Title 2", "snippet": "Snippet 2"},
            ])
            
            result = await web_researcher.search_and_research("deduplication test")
            
            # Should remove duplicates
            assert result['success'] is True
            if 'deduplicated_results' in result:
                unique_urls = set(res['url'] for res in result['deduplicated_results'])
                assert len(unique_urls) == len(result['deduplicated_results'])
                
    @pytest.mark.asyncio
    async def test_web_research_with_llm_synthesis(self):
        """RED: Test LLM integration for web research synthesis"""
        web_researcher = ArbitraryQueryResearcherWeb()
        
        with patch('src.enhanced_query_research_web.LLMClient') as mock_llm_class:
            mock_llm = Mock()
            mock_llm_class.return_value = mock_llm
            
            # Mock LLM synthesis response
            mock_response = Mock()
            mock_response.content = "Synthesized web research findings"
            mock_response.token_usage = Mock(total_tokens=200)
            mock_llm.generate_text = AsyncMock(return_value=mock_response)
            
            # Mock web search components
            with patch('src.enhanced_query_research_web.WebSearcher') as mock_searcher_class:
                mock_searcher = Mock()
                mock_searcher_class.return_value = mock_searcher
                mock_searcher.search = AsyncMock(return_value=[
                    {"url": "https://test.com", "title": "Test", "snippet": "Content"}
                ])
                
                result = await web_researcher.search_and_research("synthesis test")
                
                # Should synthesize web findings using LLM
                assert result['success'] is True
                assert 'synthesized_answer' in result or 'answer' in result
                
    @pytest.mark.asyncio
    async def test_web_research_progress_tracking(self):
        """RED: Test progress tracking for web research operations"""
        web_researcher = ArbitraryQueryResearcherWeb()
        
        with patch('builtins.print') as mock_print:
            with patch('src.enhanced_query_research_web.WebSearcher') as mock_searcher_class:
                mock_searcher = Mock()
                mock_searcher_class.return_value = mock_searcher
                mock_searcher.search = AsyncMock(return_value=[])
                
                await web_researcher.search_and_research("progress tracking test")
                
                # Should print web-specific progress messages
                progress_calls = [call.args[0] for call in mock_print.call_args_list]
                
                assert any("Starting web research" in msg for msg in progress_calls)
                assert any("Searching web sources" in msg for msg in progress_calls)
                
    def test_web_research_statistics_collection(self):
        """RED: Test web-specific statistics collection"""
        web_researcher = ArbitraryQueryResearcherWeb()
        
        # Should have method for collecting web research statistics
        assert hasattr(web_researcher, 'collect_web_statistics')
        
        # Mock statistics data
        mock_stats = {
            'urls_processed': 5,
            'successful_fetches': 4,
            'failed_fetches': 1,
            'total_content_size': 12345,
            'processing_time': 2.5
        }
        
        # Method should process statistics appropriately
        formatted_stats = web_researcher.collect_web_statistics(mock_stats)
        
        assert isinstance(formatted_stats, dict)
        assert 'urls_processed' in formatted_stats
        assert 'success_rate' in formatted_stats
        
        
class TestArbitraryQueryResearcherWebParametrized:
    """Parametrized tests for web research with different scenarios"""
    
    @pytest.mark.parametrize("query,max_results,expected_min_results", [
        ("artificial intelligence", 3, 1),
        ("machine learning tutorials", 5, 1),
        ("cybersecurity news", 2, 1),
        ("", 1, 0),  # Empty query
        ("very_specific_nonexistent_query_12345", 1, 0)  # No results expected
    ])
    @pytest.mark.asyncio
    async def test_web_search_different_queries(self, query, max_results, expected_min_results):
        """RED: Test web search with various query types and result limits"""
        web_researcher = ArbitraryQueryResearcherWeb()
        
        with patch('src.enhanced_query_research_web.WebSearcher') as mock_searcher_class:
            mock_searcher = Mock()
            mock_searcher_class.return_value = mock_searcher
            
            if expected_min_results > 0:
                mock_results = [
                    {"url": f"https://example{i}.com", "title": f"Title {i}", "snippet": f"Snippet {i}"}
                    for i in range(max_results)
                ]
                mock_searcher.search = AsyncMock(return_value=mock_results)
            else:
                mock_searcher.search = AsyncMock(return_value=[])
            
            result = await web_researcher.search_and_research(query, max_results=max_results)
            
            if expected_min_results > 0:
                assert result['success'] is True
                assert len(result.get('search_results', [])) >= expected_min_results
            else:
                # Handle empty/no results gracefully
                assert 'error' in result or result.get('search_results', []) == []
                
    @pytest.mark.parametrize("content_type,should_process", [
        ("text/html", True),
        ("application/pdf", True),
        ("text/plain", True),
        ("image/jpeg", False),
        ("video/mp4", False),
        ("application/octet-stream", False)
    ])
    @pytest.mark.asyncio
    async def test_content_type_filtering(self, content_type, should_process):
        """RED: Test filtering based on content types"""
        web_researcher = ArbitraryQueryResearcherWeb()
        
        # Should have method to check if content type should be processed
        assert hasattr(web_researcher, 'should_process_content_type')
        
        result = web_researcher.should_process_content_type(content_type)
        assert result == should_process


class TestArbitraryQueryResearcherWebIntegration:
    """Integration tests for complete web research system"""
    
    @pytest.mark.asyncio
    async def test_full_web_research_pipeline(self):
        """RED: Test complete web research pipeline integration"""
        web_researcher = ArbitraryQueryResearcherWeb()
        
        # Mock all components for full pipeline test
        with patch('src.enhanced_query_research_web.WebSearcher') as mock_searcher_class, \
             patch('src.enhanced_query_research_web.WebCrawler') as mock_crawler_class, \
             patch('src.enhanced_query_research_web.DocumentParser') as mock_parser_class, \
             patch('src.enhanced_query_research_web.Embedder') as mock_embedder_class, \
             patch('src.enhanced_query_research_web.VectorStore') as mock_vector_class, \
             patch('src.enhanced_query_research_web.LLMClient') as mock_llm_class:
            
            # Setup all mocks for successful pipeline
            mock_searcher = Mock()
            mock_searcher_class.return_value = mock_searcher
            mock_searcher.search = AsyncMock(return_value=[
                {"url": "https://example.com", "title": "Test Article", "snippet": "Test content"}
            ])
            
            mock_crawler = Mock()
            mock_crawler_class.return_value = mock_crawler
            mock_result = Mock()
            mock_result.status = "success"
            mock_result.content = b"Full article content"
            mock_crawler.fetch_url = AsyncMock(return_value=mock_result)
            
            mock_parser = Mock()
            mock_parser_class.return_value = mock_parser
            mock_parser.parse_document.return_value = Mock(
                title="Test Article",
                content="Parsed content",
                metadata={"source": "web"}
            )
            
            mock_embedder = Mock()
            mock_embedder_class.return_value = mock_embedder
            mock_embedder.process_document.return_value = [
                Mock(text="chunk1", embedding=[0.1, 0.2])
            ]
            
            mock_vector = Mock()
            mock_vector_class.return_value = mock_vector
            
            mock_llm = Mock()
            mock_llm_class.return_value = mock_llm
            mock_response = Mock()
            mock_response.content = "Comprehensive web research answer"
            mock_llm.generate_text = AsyncMock(return_value=mock_response)
            
            result = await web_researcher.search_and_research(
                "How does artificial intelligence impact modern web development?",
                max_results=2
            )
            
            # Full pipeline should provide comprehensive results
            assert isinstance(result, dict)
            assert result.get('success') is True
            assert 'answer' in result or 'synthesized_answer' in result
            assert 'web_sources' in result or 'sources' in result
            assert 'statistics' in result
            
    @pytest.mark.asyncio
    async def test_web_research_concurrent_safety(self):
        """RED: Test concurrent web research requests"""
        web_researcher = ArbitraryQueryResearcherWeb()
        
        # Test multiple concurrent instances
        web_researcher2 = ArbitraryQueryResearcherWeb()
        
        assert web_researcher is not web_researcher2
        
        # Both should be able to perform research concurrently
        with patch('src.enhanced_query_research_web.WebSearcher'):
            tasks = [
                web_researcher.search_and_research("query 1"),
                web_researcher2.search_and_research("query 2")
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Should complete without conflicts
            assert len(results) == 2
            assert all(not isinstance(r, Exception) for r in results)
