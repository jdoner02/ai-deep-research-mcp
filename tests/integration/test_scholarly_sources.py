"""
🧪 Integration Tests for Scholarly Sources Infrastructure - Educational Edition

=== WHAT ARE INTEGRATION TESTS? ===
Think of integration tests like testing a whole recipe, not just the ingredients!

Unit tests check individual ingredients (one class at a time)
Integration tests check how ingredients work together (multiple classes)

🎯 WHAT WE'RE TESTING HERE:
- ArxivSearcher: Connects to real arXiv database for scientific papers
- SemanticScholarSearcher: Uses AI-powered academic search
- UnifiedScholarlySearcher: Combines multiple academic sources
- PaperProcessor: Formats and cleans research paper data

🌐 REAL-WORLD CONNECTIONS:
These tests actually connect to external APIs (when not mocked):
- http://export.arxiv.org/api/query (arXiv's public API)
- https://api.semanticscholar.org (Semantic Scholar's API)

💡 LEARNING CONCEPTS:
- **Mocking**: Pretending external services work without actually calling them
- **Error Handling**: What happens when internet is down or APIs fail
- **Data Transformation**: Converting XML/JSON from APIs into our Python objects
- **Rate Limiting**: Being respectful to external services (not too many requests)

🔍 WHY INTEGRATION TESTS MATTER:
- Individual components might work but fail when combined
- External APIs might change their format
- Network issues can break functionality
- Performance issues only appear with real data

This module tests the integration of academic database searching capabilities
including arXiv, Semantic Scholar, and unified search functionality.
"""

from unittest.mock import Mock, patch

import pytest

from src.infrastructure.scholarly_sources import (
    ArxivSearcher,
    GoogleScholarSearcher,
    PaperProcessor,
    ScholarlyPaper,
    SemanticScholarSearcher,
    UnifiedScholarlySearcher,
)


class TestScholarlyPaper:
    """Test ScholarlyPaper dataclass"""

    def test_scholarly_paper_creation(self):
        """Test creating a ScholarlyPaper with minimal data"""
        paper = ScholarlyPaper(
            title="Test Paper", authors=["Dr. Test"], abstract="This is a test paper"
        )

        assert paper.title == "Test Paper"
        assert paper.authors == ["Dr. Test"]
        assert paper.abstract == "This is a test paper"
        assert paper.source_type == "academic"

    def test_scholarly_paper_with_all_fields(self):
        """Test creating a ScholarlyPaper with all fields"""
        paper = ScholarlyPaper(
            title="Complete Test Paper",
            authors=["Dr. First", "Dr. Second"],
            abstract="Complete test abstract",
            pdf_url="https://example.com/paper.pdf",
            source_url="https://example.com/paper",
            published="2024-01-01",
            citation_count=42,
            venue="Test Conference",
            year=2024,
            source_type="arxiv",
        )

        assert paper.citation_count == 42
        assert paper.venue == "Test Conference"
        assert paper.year == 2024
        assert paper.source_type == "arxiv"


class TestArxivSearcher:
    """Test arXiv search functionality"""

    def test_arxiv_searcher_initialization(self):
        """Test ArxivSearcher can be initialized"""
        searcher = ArxivSearcher()
        assert searcher.base_url == "http://export.arxiv.org/api/query"
        assert searcher.session is not None

    @pytest.mark.integration
    def test_arxiv_search_returns_results(self):
        """Integration test: ArxivSearcher returns actual results"""
        searcher = ArxivSearcher()
        results = searcher.search("machine learning", max_results=2)

        assert isinstance(results, list)
        assert len(results) <= 2

        if results:  # If we got results, validate structure
            result = results[0]
            assert "title" in result
            assert "authors" in result
            assert "abstract" in result
            assert "source_type" in result
            assert result["source_type"] == "arxiv"

    def test_arxiv_search_handles_empty_query(self):
        """Test ArxivSearcher handles empty queries gracefully"""
        searcher = ArxivSearcher()
        results = searcher.search("", max_results=5)

        # Should return empty list or handle gracefully
        assert isinstance(results, list)

    @patch("requests.Session.get")
    def test_arxiv_search_handles_api_error(self, mock_get):
        """Test ArxivSearcher handles API errors gracefully"""
        mock_get.side_effect = Exception("API Error")

        searcher = ArxivSearcher()
        results = searcher.search("test query", max_results=5)

        assert results == []  # Should return empty list on error


class TestSemanticScholarSearcher:
    """Test Semantic Scholar search functionality"""

    def test_semantic_scholar_searcher_initialization(self):
        """Test SemanticScholarSearcher can be initialized"""
        searcher = SemanticScholarSearcher()
        assert searcher.base_url == "https://api.semanticscholar.org/graph/v1"
        assert searcher.session is not None

    def test_semantic_scholar_searcher_with_api_key(self):
        """Test SemanticScholarSearcher initialization with API key"""
        searcher = SemanticScholarSearcher(api_key="test-key")
        assert "x-api-key" in searcher.session.headers
        assert searcher.session.headers["x-api-key"] == "test-key"

    @pytest.mark.integration
    def test_semantic_scholar_search_returns_results(self):
        """Integration test: SemanticScholarSearcher returns actual results"""
        searcher = SemanticScholarSearcher()
        results = searcher.search("deep learning", max_results=2)

        assert isinstance(results, list)
        assert len(results) <= 2

        if results:  # If we got results, validate structure
            result = results[0]
            assert "title" in result
            assert "authors" in result
            assert "source_type" in result
            assert result["source_type"] == "semantic_scholar"

    @patch("requests.Session.get")
    def test_semantic_scholar_handles_api_error(self, mock_get):
        """Test SemanticScholarSearcher handles API errors gracefully"""
        mock_get.side_effect = Exception("API Error")

        searcher = SemanticScholarSearcher()
        results = searcher.search("test query", max_results=5)

        assert results == []  # Should return empty list on error


class TestGoogleScholarSearcher:
    """Test Google Scholar search functionality"""

    def test_google_scholar_searcher_initialization(self):
        """Test GoogleScholarSearcher can be initialized"""
        searcher = GoogleScholarSearcher()
        assert searcher.session is not None
        assert searcher.min_interval > 0  # Should have rate limiting

    def test_google_scholar_search_returns_mock_results(self):
        """Test GoogleScholarSearcher returns mock results (placeholder implementation)"""
        searcher = GoogleScholarSearcher()
        results = searcher.search("test query", max_results=3)

        assert isinstance(results, list)
        assert len(results) <= 3

        if results:  # Should return at least one mock result
            result = results[0]
            assert "title" in result
            assert "authors" in result
            assert "source_type" in result
            assert result["source_type"] == "google_scholar"


class TestUnifiedScholarlySearcher:
    """Test unified search across multiple sources"""

    def test_unified_searcher_initialization(self):
        """Test UnifiedScholarlySearcher can be initialized"""
        searcher = UnifiedScholarlySearcher()
        assert searcher.arxiv_searcher is not None
        assert searcher.semantic_scholar_searcher is not None
        assert searcher.google_scholar_searcher is not None

    def test_unified_searcher_with_api_key(self):
        """Test UnifiedScholarlySearcher with Semantic Scholar API key"""
        searcher = UnifiedScholarlySearcher(semantic_scholar_api_key="test-key")
        assert "x-api-key" in searcher.semantic_scholar_searcher.session.headers

    @pytest.mark.integration
    def test_unified_search_returns_results(self):
        """Integration test: UnifiedScholarlySearcher aggregates results"""
        searcher = UnifiedScholarlySearcher()
        results = searcher.search("neural networks", max_results=5)

        assert isinstance(results, list)
        assert len(results) <= 5

        if results:
            # Should have results from multiple sources
            source_types = {result["source_type"] for result in results}
            assert len(source_types) >= 1  # At least one source type

            # Validate result structure
            result = results[0]
            assert "title" in result
            assert "authors" in result
            assert "source_type" in result

    def test_unified_search_source_filtering(self):
        """Test UnifiedScholarlySearcher with specific sources"""
        searcher = UnifiedScholarlySearcher()
        results = searcher.search("test query", max_results=10, sources=["arxiv"])

        assert isinstance(results, list)

    def test_deduplicate_papers(self):
        """Test paper deduplication functionality"""
        searcher = UnifiedScholarlySearcher()

        # Create test papers with similar titles
        papers = [
            {"title": "Machine Learning Fundamentals", "source_type": "arxiv"},
            {
                "title": "Machine Learning Fundamentals",
                "source_type": "semantic_scholar",
            },
            {"title": "Deep Learning Applications", "source_type": "arxiv"},
        ]

        unique_papers = searcher._deduplicate_papers(papers)

        # Should remove the duplicate
        assert len(unique_papers) == 2
        titles = [paper["title"] for paper in unique_papers]
        assert "Machine Learning Fundamentals" in titles
        assert "Deep Learning Applications" in titles


class TestPaperProcessor:
    """Test paper download and processing functionality"""

    def test_paper_processor_initialization(self):
        """Test PaperProcessor can be initialized"""
        processor = PaperProcessor()
        assert processor.session is not None
        assert "User-Agent" in processor.session.headers

    @patch("requests.Session.get")
    def test_download_pdf_success(self, mock_get):
        """Test successful PDF download"""
        # Mock successful response
        mock_response = Mock()
        mock_response.headers = {"content-length": "1000000"}  # 1MB
        mock_response.iter_content.return_value = [b"test pdf content"]
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response

        processor = PaperProcessor()
        content = processor.download_pdf("https://example.com/paper.pdf")

        assert content == b"test pdf content"

    @patch("requests.Session.get")
    def test_download_pdf_too_large(self, mock_get):
        """Test PDF download size limit"""
        # Mock response with large file
        mock_response = Mock()
        mock_response.headers = {"content-length": "100000000"}  # 100MB
        mock_get.return_value = mock_response

        processor = PaperProcessor()
        content = processor.download_pdf(
            "https://example.com/large.pdf", max_size_mb=50
        )

        assert content is None  # Should reject large files

    @patch("requests.Session.get")
    def test_download_pdf_handles_error(self, mock_get):
        """Test PDF download error handling"""
        mock_get.side_effect = Exception("Download error")

        processor = PaperProcessor()
        content = processor.download_pdf("https://example.com/error.pdf")

        assert content is None  # Should return None on error

    def test_extract_text_from_pdf_placeholder(self):
        """Test PDF text extraction (placeholder implementation)"""
        processor = PaperProcessor()
        text = processor.extract_text_from_pdf(b"fake pdf content")

        # Current implementation is placeholder
        assert text is None


class TestScholarlySourcesIntegration:
    """Integration tests for scholarly sources with existing system"""

    @pytest.mark.integration
    def test_scholarly_sources_import_from_infrastructure(self):
        """Test that scholarly sources can be imported from infrastructure package"""
        from src.infrastructure import (
            ArxivSearcher,
            SemanticScholarSearcher,
            UnifiedScholarlySearcher,
        )

        # Should be able to create instances
        arxiv = ArxivSearcher()
        semantic = SemanticScholarSearcher()
        unified = UnifiedScholarlySearcher()

        assert arxiv is not None
        assert semantic is not None
        assert unified is not None

    @pytest.mark.integration
    def test_end_to_end_scholarly_search(self):
        """End-to-end test of scholarly search functionality"""
        from src.infrastructure import UnifiedScholarlySearcher

        searcher = UnifiedScholarlySearcher()
        results = searcher.search("machine learning", max_results=3)

        assert isinstance(results, list)
        assert len(results) <= 3

        # Validate that we get results from real sources
        if results:
            for result in results:
                assert "title" in result
                assert "authors" in result
                assert isinstance(result["authors"], list)
                assert "abstract" in result
                assert "source_type" in result
                assert result["source_type"] in [
                    "arxiv",
                    "semantic_scholar",
                    "google_scholar",
                ]

    def test_scholarly_paper_dataclass_in_infrastructure(self):
        """Test ScholarlyPaper dataclass is available from infrastructure"""
        from src.infrastructure import ScholarlyPaper

        paper = ScholarlyPaper(
            title="Test Infrastructure Paper",
            authors=["Test Author"],
            abstract="Test abstract",
        )

        assert paper.title == "Test Infrastructure Paper"
        assert paper.source_type == "academic"
