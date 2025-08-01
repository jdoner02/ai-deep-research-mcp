# 🕷️ Web Crawling and HTTP Testing - Educational Module

## Welcome to Web Crawling!

Ever wondered how search engines like Google discover and index billions of web pages? Or how your favorite news app automatically finds new articles? The answer is **web crawling** - the process of systematically browsing the internet to collect information.

In this educational module, we'll learn how to test web crawling components, understand HTTP networking concepts, and explore how modern AI research systems gather information from the web.

## 🌐 What is Web Crawling?

Web crawling is like having a tireless digital librarian that:
1. **Visits web pages** by following links
2. **Downloads content** from each page (HTML, text, images)  
3. **Extracts useful information** from the downloaded content
4. **Follows links** to discover new pages to visit
5. **Respects rules** like rate limits and robots.txt files

### Real-World Example: How AI Research Works
When you ask an AI research system "What are the latest developments in renewable energy?", here's what happens:

1. 🔍 **Query Analysis**: Break down your question into searchable terms
2. 🌐 **Web Search**: Find relevant URLs using search engines
3. 🕷️ **Web Crawling**: Visit those URLs and download their content
4. 📄 **Content Parsing**: Extract the important text from HTML pages
5. 🧠 **AI Processing**: Analyze the text and synthesize an answer
6. 📚 **Citation**: Provide sources for verification

## 🧪 Testing Web Crawlers: The TDD Approach

### Why Test Web Crawlers?
Web crawling involves many things that can go wrong:
- **Network failures**: Websites might be down or slow
- **Malformed HTML**: Web pages might have broken or unusual structure
- **Rate limiting**: Websites might block too many requests
- **Dynamic content**: Pages might require JavaScript to load properly
- **Different file types**: PDFs, images, videos - not just HTML

Testing helps us build robust crawlers that handle these challenges gracefully.

### The RED-GREEN-REFACTOR Cycle for Web Crawling

Let's learn TDD by building a web crawler test-first:

#### 🔴 RED Phase: Write Failing Tests First

```python
import pytest
from unittest.mock import Mock, patch
from typing import List, Dict, Any

# These imports will fail initially - that's expected in TDD!
try:
    from src.web_crawler import WebCrawler, CrawlResult
except ImportError:
    WebCrawler = None
    CrawlResult = None

class TestWebCrawler:
    """
    🧪 Test suite for WebCrawler component.
    
    We write these tests BEFORE implementing the crawler,
    so they define what we want our crawler to do.
    
    🎯 Learning Goals:
    - Understand TDD (Test-Driven Development)
    - Learn about testing external dependencies (HTTP requests)
    - Practice using mock objects for network operations
    - See how to test error conditions and edge cases
    """
    
    def test_web_crawler_can_be_created(self):
        """
        🏗️ Test that we can create a WebCrawler instance.
        
        This is the simplest possible test - can we make our object?
        In TDD, we start with the basics and build up complexity.
        
        💡 Why this test matters:
        - Ensures our class can be imported and instantiated
        - Verifies basic object creation works
        - Foundation for all other functionality
        """
        # This will fail until we create the WebCrawler class
        assert WebCrawler is not None, "WebCrawler class should exist"
        
        # Test that we can create an instance
        crawler = WebCrawler()
        assert crawler is not None
        assert isinstance(crawler, WebCrawler)
    
    def test_crawl_result_has_required_fields(self):
        """
        📋 Test that CrawlResult contains all the data we need.
        
        When our crawler visits a webpage, it should return structured
        information about what it found. This test defines that structure.
        
        💡 Real-world analogy:
        Like a field researcher's report card - it should contain:
        - Where they went (URL)
        - What they found (title, content)
        - When they visited (timestamp)
        - Any problems encountered (status)
        """
        assert CrawlResult is not None, "CrawlResult should exist"
        
        # Test creating a CrawlResult with all required fields
        result = CrawlResult(
            url="https://example.com",
            title="Example Domain",
            content="This domain is for use in examples...",
            status_code=200,  # HTTP 200 means "success"
            timestamp="2025-07-31T10:00:00Z",
            error=None
        )
        
        # Verify all fields are accessible
        assert result.url == "https://example.com"
        assert result.title == "Example Domain"
        assert result.content.startswith("This domain is")
        assert result.status_code == 200
        assert result.error is None

    @pytest.mark.asyncio  # This test involves async/await
    async def test_crawl_single_url_success(self):
        """
        🌐 Test successfully crawling a single webpage.
        
        This test simulates what happens when everything goes right:
        - We request a webpage
        - The server responds with HTML
        - We extract the title and content
        - We return a successful CrawlResult
        
        💡 Why use async/await:
        Web requests can take time (network latency), so we use
        asynchronous programming to avoid blocking our program
        while waiting for responses.
        """
        # Create a crawler instance
        crawler = WebCrawler()
        
        # Mock the HTTP request to avoid hitting real websites in tests
        mock_html = '''
        <html>
            <head><title>Test Page</title></head>
            <body><p>This is test content for our crawler.</p></body>
        </html>
        '''
        
        # Use a mock to simulate a successful HTTP response
        with patch('httpx.AsyncClient.get') as mock_get:
            # Configure the mock to return our test HTML
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.text = mock_html
            mock_response.headers = {'content-type': 'text/html'}
            mock_get.return_value = mock_response
            
            # Test the crawl operation
            result = await crawler.crawl_url("https://test-site.com")
            
            # Verify the crawler processed the HTML correctly
            assert result.url == "https://test-site.com"
            assert result.title == "Test Page"
            assert "test content" in result.content.lower()
            assert result.status_code == 200
            assert result.error is None
            
            # Verify the HTTP request was made correctly
            mock_get.assert_called_once_with("https://test-site.com")

    @pytest.mark.asyncio
    async def test_crawl_handles_404_error(self):
        """
        ❌ Test that our crawler handles "page not found" errors gracefully.
        
        Not every URL will exist! Our crawler needs to handle errors
        without crashing the entire research process.
        
        💡 HTTP Status Codes:
        - 200: Success! Page found and loaded
        - 404: Page not found (maybe URL was wrong)
        - 500: Server error (the website is having problems)
        - 403: Forbidden (we're not allowed to access this page)
        """
        crawler = WebCrawler()
        
        # Mock a 404 "Not Found" response
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_response = Mock()
            mock_response.status_code = 404
            mock_response.text = "<html><body>Page not found</body></html>"
            mock_get.return_value = mock_response
            
            # Test crawling a non-existent page
            result = await crawler.crawl_url("https://example.com/nonexistent")
            
            # Verify the crawler handled the error appropriately
            assert result.url == "https://example.com/nonexistent"
            assert result.status_code == 404
            assert result.error is not None
            assert "not found" in result.error.lower()
            # Content might be empty or contain error message
            assert result.content is not None

    @pytest.mark.asyncio
    async def test_crawl_handles_network_timeout(self):
        """
        ⏱️ Test that our crawler handles network timeouts gracefully.
        
        Sometimes websites are slow or unreachable. Our crawler should
        give up after a reasonable time rather than waiting forever.
        
        💡 Why timeouts matter:
        - Prevents our program from getting stuck
        - Allows us to try alternative sources
        - Keeps the user experience responsive
        """
        crawler = WebCrawler(timeout=5.0)  # 5 second timeout
        
        # Mock a timeout exception
        import httpx
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.side_effect = httpx.TimeoutException("Request timed out")
            
            # Test crawling a slow/unreachable site
            result = await crawler.crawl_url("https://very-slow-site.com")
            
            # Verify the crawler handled the timeout
            assert result.url == "https://very-slow-site.com"
            assert result.status_code is None  # No response received
            assert result.error is not None
            assert "timeout" in result.error.lower()
            assert result.content == ""  # No content retrieved

    @pytest.mark.asyncio
    async def test_crawl_multiple_urls_in_parallel(self):
        """
        ⚡ Test crawling multiple URLs simultaneously for efficiency.
        
        When researching a topic, we often want to visit many websites.
        Instead of visiting them one by one (slow), we can visit several
        at the same time using parallel processing.
        
        💡 Parallel vs Sequential:
        - Sequential: Visit site A, wait, visit site B, wait, visit site C
        - Parallel: Start visiting A, B, and C all at once, collect results
        
        Parallel is much faster when dealing with network operations!
        """
        crawler = WebCrawler()
        
        # List of URLs to crawl simultaneously
        urls = [
            "https://site1.com",
            "https://site2.com", 
            "https://site3.com"
        ]
        
        # Mock responses for each URL
        mock_responses = [
            Mock(status_code=200, text="<html><head><title>Site 1</title></head><body>Content 1</body></html>"),
            Mock(status_code=200, text="<html><head><title>Site 2</title></head><body>Content 2</body></html>"),
            Mock(status_code=200, text="<html><head><title>Site 3</title></head><body>Content 3</body></html>")
        ]
        
        with patch('httpx.AsyncClient.get') as mock_get:
            mock_get.side_effect = mock_responses
            
            # Test parallel crawling
            results = await crawler.crawl_urls(urls)
            
            # Verify we got results for all URLs
            assert len(results) == 3
            assert all(result.status_code == 200 for result in results)
            assert results[0].title == "Site 1"
            assert results[1].title == "Site 2"
            assert results[2].title == "Site 3"
            
            # Verify all requests were made
            assert mock_get.call_count == 3

    def test_crawl_respects_robots_txt(self):
        """
        🤖 Test that our crawler respects robots.txt rules.
        
        robots.txt is a file that websites use to tell crawlers:
        "Please don't crawl these pages" or "Please wait X seconds between requests"
        
        💡 Web Etiquette:
        Good crawlers are polite! They:
        - Check robots.txt before crawling a site
        - Respect "disallow" rules
        - Wait between requests (don't overwhelm servers)
        - Identify themselves with a User-Agent string
        
        This is like asking permission before entering someone's house.
        """
        crawler = WebCrawler(respect_robots=True)
        
        # Mock robots.txt that disallows crawling /private/
        robots_content = '''
        User-agent: *
        Disallow: /private/
        Disallow: /admin/
        Crawl-delay: 1
        '''
        
        with patch('httpx.AsyncClient.get') as mock_get:
            # First call gets robots.txt
            mock_robots_response = Mock()
            mock_robots_response.status_code = 200
            mock_robots_response.text = robots_content
            
            mock_get.return_value = mock_robots_response
            
            # Test that disallowed URLs are rejected
            can_crawl_public = crawler.can_crawl("https://example.com/public/page")
            can_crawl_private = crawler.can_crawl("https://example.com/private/secret")
            
            assert can_crawl_public is True
            assert can_crawl_private is False
```

#### 🟢 GREEN Phase: Implement Just Enough to Pass

After writing these tests (which will fail), we'd implement the minimal `WebCrawler` class:

```python
import httpx
import asyncio
from dataclasses import dataclass
from typing import List, Optional
from datetime import datetime
from bs4 import BeautifulSoup
import urllib.robotparser

@dataclass
class CrawlResult:
    """Results from crawling a single webpage."""
    url: str
    title: Optional[str] = None
    content: str = ""
    status_code: Optional[int] = None
    timestamp: str = ""
    error: Optional[str] = None

class WebCrawler:
    """A polite, educational web crawler for AI research."""
    
    def __init__(self, timeout: float = 10.0, respect_robots: bool = True):
        self.timeout = timeout
        self.respect_robots = respect_robots
        self.robots_cache = {}  # Cache robots.txt for different domains
    
    async def crawl_url(self, url: str) -> CrawlResult:
        """Crawl a single URL and return structured results."""
        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)
                
                # Parse HTML content
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.find('title')
                title_text = title.get_text().strip() if title else None
                
                # Extract main content (simplified)
                content = soup.get_text()
                
                return CrawlResult(
                    url=url,
                    title=title_text,
                    content=content,
                    status_code=response.status_code,
                    timestamp=datetime.now().isoformat(),
                    error=None if response.status_code == 200 else f"HTTP {response.status_code}"
                )
                
        except httpx.TimeoutException:
            return CrawlResult(
                url=url,
                error="Request timed out",
                timestamp=datetime.now().isoformat()
            )
        except Exception as e:
            return CrawlResult(
                url=url,
                error=str(e),
                timestamp=datetime.now().isoformat()
            )
    
    async def crawl_urls(self, urls: List[str]) -> List[CrawlResult]:
        """Crawl multiple URLs in parallel."""
        tasks = [self.crawl_url(url) for url in urls]
        return await asyncio.gather(*tasks)
    
    def can_crawl(self, url: str) -> bool:
        """Check if we're allowed to crawl this URL per robots.txt."""
        if not self.respect_robots:
            return True
        
        # Implementation would check robots.txt
        # Simplified for educational purposes
        return "/private/" not in url and "/admin/" not in url
```

#### 🔧 REFACTOR Phase: Make It Better

Once tests pass, we'd improve the code:
- Add better error handling
- Implement proper robots.txt parsing
- Add rate limiting
- Improve content extraction
- Add logging and monitoring

## 🎯 Key Testing Concepts You Learned

### 1. **Test-Driven Development (TDD)**
- Write tests before implementation
- Tests define the desired behavior
- RED → GREEN → REFACTOR cycle

### 2. **Mocking External Dependencies**
- Use `Mock` objects to simulate HTTP responses
- Avoid hitting real websites during tests
- Control exactly what responses your code receives

### 3. **Async/Await Testing**
- Use `@pytest.mark.asyncio` for async test functions
- Test asynchronous operations like network requests
- Handle concurrent operations properly

### 4. **Error Condition Testing**
- Test what happens when things go wrong
- Network timeouts, 404 errors, malformed HTML
- Ensure graceful degradation, not crashes

### 5. **Edge Case Testing**
- Empty responses, huge files, unusual content
- Rate limiting and politeness rules
- Different content types (HTML, PDF, JSON)

## 🚀 Practice Challenges

Ready to test your understanding? Try these challenges:

### Challenge 1: Test HTML Parsing
Write tests for extracting specific elements from HTML:
- Finding all links (`<a href="...">`)
- Extracting meta descriptions
- Handling malformed HTML

### Challenge 2: Test Rate Limiting
Write tests that verify your crawler waits appropriately between requests to the same domain.

### Challenge 3: Test Content-Type Handling
Write tests for different file types:
- HTML pages
- PDF documents  
- JSON APIs
- Images (should be skipped or handled specially)

### Challenge 4: Test User-Agent Management
Write tests that verify your crawler identifies itself properly and can rotate User-Agent strings.

## 📚 Next Steps

- **Integration Testing**: Test the crawler with real (controlled) websites
- **Performance Testing**: Measure crawling speed and resource usage
- **End-to-End Testing**: Test the complete research workflow from query to results

## 💡 Real-World Applications

The concepts you've learned here apply to:
- **Search engines** (Google, Bing crawling the entire web)
- **Price comparison sites** (checking multiple stores)
- **News aggregators** (collecting articles from many sources)
- **Social media monitoring** (tracking brand mentions)
- **Academic research** (gathering papers and citations)
- **Market research** (analyzing competitor websites)

Remember: **Good web crawlers are like good house guests - polite, respectful, and don't overstay their welcome!** 🕷️✨
