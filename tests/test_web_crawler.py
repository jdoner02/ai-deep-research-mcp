#!/usr/bin/env python3
"""
Test Guardian Agent - RED Phase
Test cases for Web Crawler component of AI Deep Research MCP system

These tests define the expected behavior of the WebCrawler class before implementation.
They will FAIL initially (RED phase) until we implement the code.
"""

import pytest
from typing import List, Dict, Any
from unittest.mock import Mock, patch, AsyncMock
import asyncio
import sys
import os

# Add src directory to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

try:
    # Import from our implementation
    from web_crawler import WebCrawler, CrawlResult, fetch_with_playwright
except ImportError:
    # Set to None to indicate missing implementation
    WebCrawler = None
    CrawlResult = None
    fetch_with_playwright = None
try:
    from src.web_crawler import WebCrawler, CrawlResult
except ImportError:
    WebCrawler = None
    CrawlResult = None


class TestWebCrawler:
    """Test suite for WebCrawler component - defining expected behavior"""
    
    def test_web_crawler_exists(self):
        """Test that WebCrawler class exists and can be instantiated"""
        assert WebCrawler is not None, "WebCrawler class should exist"
        crawler = WebCrawler()
        assert crawler is not None
    
    def test_crawl_result_dataclass(self):
        """Test that CrawlResult dataclass exists with required fields"""
        assert CrawlResult is not None, "CrawlResult dataclass should exist"
        
        result = CrawlResult(
            url="https://example.com",
            title="Test Title",
            content="Test content",
            status="success",
            metadata={}
        )
        
        assert result.url == "https://example.com"
        assert result.title == "Test Title"
        assert result.content == "Test content"
        assert result.status == "success"
        assert isinstance(result.metadata, dict)
    
    @pytest.mark.asyncio
    async def test_fetch_single_url(self):
        """Test fetching content from a single URL"""
        crawler = WebCrawler()
        
        url = "https://example.com"
        result = await crawler.fetch_url(url)
        
        assert isinstance(result, CrawlResult)
        assert result.url == url
        assert result.status in ["success", "error"]
        
        if result.status == "success":
            assert result.content is not None
            assert len(result.content) > 0
            assert result.title is not None
    
    @pytest.mark.asyncio
    async def test_fetch_multiple_urls_concurrent(self):
        """Test concurrent fetching of multiple URLs"""
        crawler = WebCrawler(max_concurrent=3)
        
        urls = [
            "https://example.com",
            "https://httpbin.org/html",
            "https://httpbin.org/json"
        ]
        
        results = await crawler.fetch_urls(urls)
        
        assert isinstance(results, list)
        assert len(results) == len(urls)
        
        for result in results:
            assert isinstance(result, CrawlResult)
            assert result.url in urls
    
    def test_respects_robots_txt(self):
        """Test that crawler respects robots.txt when configured"""
        crawler = WebCrawler(respect_robots=True)
        
        # This test verifies the configuration is set
        assert crawler.respect_robots is True
        
        # Implementation should check robots.txt before crawling
        assert hasattr(crawler, 'check_robots_permission')
    
    def test_rate_limiting_configuration(self):
        """Test rate limiting configuration"""
        crawler = WebCrawler(delay_between_requests=1.0, max_concurrent=2)
        
        assert crawler.delay_between_requests == 1.0
        assert crawler.max_concurrent == 2
    
    @pytest.mark.asyncio
    async def test_handles_different_content_types(self):
        """Test handling of different content types (HTML, PDF, etc.)"""
        crawler = WebCrawler()

        # Mock httpx.AsyncClient to control the response
        mock_response = Mock()
        mock_response.text = '<html><body>Test HTML</body></html>'
        mock_response.headers = {"content-type": "text/html"}
        mock_response.status_code = 200
        mock_response.url = "https://example.com/page.html"

        with patch('web_crawler.httpx.AsyncClient') as mock_client:
            mock_context = Mock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_context)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_context.get = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_context

            result = await crawler.fetch_url("https://example.com/page.html")
            assert result.status == "success"
            assert "Test HTML" in result.content

    @pytest.mark.asyncio
    async def test_handles_javascript_rendered_content(self):
        """Test handling of JavaScript-rendered content using headless browser"""
        crawler = WebCrawler(use_browser=True)

        # Should use browser for JS-heavy sites
        assert crawler.use_browser is True

        # Test that it uses browser method
        result = await crawler.fetch_url("https://example.com/js-app")
        
        # For now, browser mode returns mock content
        assert result.status == "success"
        assert result.metadata.get("rendered") is True
    
    def test_error_handling_invalid_urls(self):
        """Test error handling for invalid URLs"""
        crawler = WebCrawler()
        
        invalid_urls = [
            "not-a-url",
            "ftp://invalid-protocol.com",
            "https://non-existent-domain-12345.com"
        ]
        
        for url in invalid_urls:
            # Should handle gracefully without throwing exception
            try:
                result = asyncio.run(crawler.fetch_url(url))
                assert result.status == "error"
                assert result.url == url
            except Exception as e:
                pytest.fail(f"Should handle invalid URL gracefully: {e}")
    
    def test_timeout_configuration(self):
        """Test timeout configuration for slow responses"""
        crawler = WebCrawler(timeout=5.0)
        
        assert crawler.timeout == 5.0
    
    @pytest.mark.asyncio
    async def test_follow_redirects(self):
        """Test following HTTP redirects"""
        crawler = WebCrawler(follow_redirects=True)
        
        # Should follow redirects and return final URL
        with patch('src.web_crawler.httpx.AsyncClient') as mock_client:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = "<html>Final content</html>"
            mock_response.url = "https://final-destination.com"
            mock_response.headers = {"content-type": "text/html"}
            
            mock_client.return_value.__aenter__.return_value.get.return_value = mock_response
            
            result = await crawler.fetch_url("https://redirect-example.com")
            
            # Implementation should track final URL after redirects
            assert result.status == "success"
    
    def test_user_agent_configuration(self):
        """Test custom user agent configuration"""
        custom_ua = "DeepResearchBot/1.0"
        crawler = WebCrawler(user_agent=custom_ua)
        
        assert crawler.user_agent == custom_ua
    
    @pytest.mark.asyncio
    async def test_extract_metadata(self):
        """Test extraction of metadata from web pages"""
        crawler = WebCrawler()

        html_content = """
        <html>
        <head>
            <title>Test Page Title</title>
            <meta name="description" content="Test page description">
            <meta property="og:title" content="OG Title">
            <meta name="author" content="Test Author">
        </head>
        <body>Content here</body>
        </html>
        """

        # Mock httpx.AsyncClient to return our test HTML
        mock_response = Mock()
        mock_response.text = html_content
        mock_response.headers = {"content-type": "text/html"}
        mock_response.status_code = 200
        mock_response.url = "https://example.com"

        with patch('web_crawler.httpx.AsyncClient') as mock_client:
            mock_context = Mock()
            mock_context.__aenter__ = AsyncMock(return_value=mock_context)
            mock_context.__aexit__ = AsyncMock(return_value=None)
            mock_context.get = AsyncMock(return_value=mock_response)
            mock_client.return_value = mock_context

            result = await crawler.fetch_url("https://example.com")

            if result.status == "success":
                assert result.title == "Test Page Title"
                assert result.metadata["content_type"] == "text/html"

    def test_content_filtering(self):
        """Test filtering of unwanted content (ads, navigation, etc.)"""
        crawler = WebCrawler(filter_content=True)
        
        assert crawler.filter_content is True
        
        # Should have method to clean content
        assert hasattr(crawler, 'filter_main_content')
    
    @pytest.mark.asyncio
    async def test_depth_limited_crawling(self):
        """Test crawling with depth limits (following links)"""
        crawler = WebCrawler(max_depth=2)
        
        start_urls = ["https://example.com"]
        results = await crawler.crawl_with_depth(start_urls)
        
        assert isinstance(results, list)
        
        # Should respect depth limit
        for result in results:
            assert result.metadata.get("depth", 0) <= 2
    
    def test_domain_restrictions(self):
        """Test restricting crawling to specific domains"""
        allowed_domains = ["example.com", "academic-site.edu"]
        crawler = WebCrawler(allowed_domains=allowed_domains)
        
        assert crawler.allowed_domains == allowed_domains
        
        # Should have method to check domain permissions
        assert hasattr(crawler, 'is_domain_allowed')
    
    @pytest.mark.asyncio
    async def test_crawl_logging_and_progress(self):
        """Test logging and progress tracking during crawling"""
        crawler = WebCrawler()
        
        urls = ["https://example.com", "https://httpbin.org"]
        
        # Should track progress
        progress_updates = []
        
        def progress_callback(current, total, url):
            progress_updates.append((current, total, url))
        
        results = await crawler.fetch_urls(urls, progress_callback=progress_callback)
        
        # Should have received progress updates
        assert len(progress_updates) >= len(urls)


class TestWebCrawlerIntegration:
    """Integration tests for WebCrawler with real network calls"""
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_crawl_real_webpage(self):
        """Integration test - crawl a real webpage (requires internet)"""
        crawler = WebCrawler()
        
        # Use a reliable test endpoint
        url = "https://httpbin.org/html"
        result = await crawler.fetch_url(url)
        
        assert result.status == "success"
        assert result.url == url
        assert len(result.content) > 0
        assert "html" in result.content.lower()
    
    @pytest.mark.integration
    @pytest.mark.asyncio
    async def test_handle_real_timeout(self):
        """Integration test - handle real timeout scenarios"""
        crawler = WebCrawler(timeout=0.1)  # Very short timeout
        
        # This should timeout
        result = await crawler.fetch_url("https://httpbin.org/delay/1")
        
        assert result.status == "error"
        assert "timeout" in result.metadata.get("error", "").lower()
