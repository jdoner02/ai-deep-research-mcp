"""
Test suite for Web Interface Components with Scholarly Sources Integration

This test suite validates:
1. Basic web interface functionality
2. Scholarly research endpoints
3. Enhanced research with academic sources
4. API documentation accuracy
5. UI component formatting
6. Error handling and edge cases
"""

import asyncio
from datetime import datetime
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest

from src.application.scholarly_use_cases import (
    ScholarlyPaperResult,
    ScholarlySearchRequest,
    ScholarlySearchResponse,
)
from src.domain.entities import ResearchQuery, ResearchResult, ResearchStatus
from src.infrastructure.scholarly_sources import ScholarlyPaper
from src.presentation.web_interface import (
    WebInterfaceHandler,
    WebUIComponents,
    create_web_interface,
)


class TestWebInterfaceHandler:
    """Test suite for WebInterfaceHandler with scholarly integration."""

    @pytest.fixture
    def web_interface(self):
        """Create web interface handler for testing."""
        return WebInterfaceHandler()

    @pytest.fixture
    def sample_scholarly_request(self):
        """Sample scholarly search request."""
        return {
            "query": "machine learning transformers",
            "sources": ["arxiv", "semantic_scholar"],
            "max_results": 5,
            "include_abstracts": True,
            "min_year": 2020,
            "fields_of_study": ["Computer Science"],
        }

    @pytest.fixture
    def sample_scholarly_papers(self):
        """Sample scholarly papers for testing."""
        return [
            {
                "title": "Attention Is All You Need",
                "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
                "abstract": "The dominant sequence transduction models...",
                "year": 2017,
                "citation_count": 75842,
                "pdf_url": "https://arxiv.org/pdf/1706.03762.pdf",
                "source_url": "https://arxiv.org/abs/1706.03762",
                "source_type": "arxiv",
                "relevance_score": 0.95,
                "venue": "NeurIPS",
                "doi": "10.48550/arXiv.1706.03762",
                "formatted_citation": "Vaswani, A. et al. (2017). Attention Is All You Need. NeurIPS.",
                "display_class": "high-relevance",
            },
            {
                "title": "BERT: Pre-training of Deep Bidirectional Transformers",
                "authors": ["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee"],
                "abstract": "We introduce a new language representation model...",
                "year": 2018,
                "citation_count": 65234,
                "pdf_url": None,
                "source_url": "https://arxiv.org/abs/1810.04805",
                "source_type": "arxiv",
                "relevance_score": 0.92,
                "venue": "NAACL",
                "doi": "10.48550/arXiv.1810.04805",
                "formatted_citation": "Devlin, J. et al. (2018). BERT: Pre-training of Deep Bidirectional Transformers. NAACL.",
                "display_class": "high-relevance",
            },
        ]

    @pytest.mark.asyncio
    async def test_handle_scholarly_search_request_success(
        self, web_interface, sample_scholarly_request, sample_scholarly_papers
    ):
        """Test successful scholarly search request."""
        # Mock the scholarly use case
        mock_response = ScholarlySearchResponse(
            query_id="test-query-123",
            papers=sample_scholarly_papers,
            total_found=2,
            sources_used=["arxiv", "semantic_scholar"],
            search_time_ms=1250,
        )

        with patch.object(
            web_interface.scholarly_use_case,
            "execute_scholarly_search",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_search:
            result = await web_interface.handle_scholarly_search_request(
                sample_scholarly_request
            )

            # Verify the call was made correctly
            mock_search.assert_called_once()
            call_args = mock_search.call_args[0][0]
            assert call_args.query_text == "machine learning transformers"
            assert call_args.sources == ["arxiv", "semantic_scholar"]
            assert call_args.max_results == 5

            # Verify response structure
            assert result["success"] is True
            assert result["data"]["query_id"] == "test-query-123"
            assert result["data"]["total_found"] == 2
            assert result["data"]["search_time_ms"] == 1250
            assert len(result["data"]["papers"]) == 2
            assert "Found 2 academic papers" in result["data"]["message"]

    @pytest.mark.asyncio
    async def test_handle_scholarly_search_request_error(
        self, web_interface, sample_scholarly_request
    ):
        """Test scholarly search request with error."""
        with patch.object(
            web_interface.scholarly_use_case,
            "execute_scholarly_search",
            new_callable=AsyncMock,
            side_effect=Exception("Search service unavailable"),
        ):
            result = await web_interface.handle_scholarly_search_request(
                sample_scholarly_request
            )

            assert result["success"] is False
            assert "Search service unavailable" in result["error"]["message"]
            assert result["error"]["type"] == "Exception"

    @pytest.mark.asyncio
    async def test_handle_enhanced_research_request_success(self, web_interface):
        """Test enhanced research request with scholarly sources."""
        request_data = {
            "query": "quantum computing algorithms",
            "sources": ["arxiv"],
            "max_results": 3,
            "include_scholarly": True,
        }

        # Mock the create query response
        mock_create_response = Mock()
        mock_create_response.query_id = "enhanced-query-456"

        # Mock the enhanced research result
        mock_result = Mock()
        mock_result.query = Mock()
        mock_result.query.text = "quantum computing algorithms"
        mock_result.status = ResearchStatus.COMPLETED
        mock_result.completed_at = datetime.now()
        mock_result.sources = [
            Mock(
                title="Quantum Algorithm for Linear Systems",
                url="https://arxiv.org/abs/0811.3171",
                source_type=Mock(value="ARXIV"),
                relevance_score=0.88,
                content="Abstract content here...",
                metadata={
                    "authors": ["Aram W. Harrow", "Avinatan Hassidim"],
                    "year": 2009,
                    "citation_count": 1234,
                    "venue": "Physical Review Letters",
                    "pdf_url": "https://arxiv.org/pdf/0811.3171.pdf",
                    "doi": "10.1103/PhysRevLett.103.150502",
                    "formatted_citation": "Harrow, A. W. et al. (2009). Quantum Algorithm for Linear Systems. Phys. Rev. Lett.",
                },
            )
        ]

        with (
            patch.object(
                web_interface.create_query_use_case,
                "execute",
                new_callable=AsyncMock,
                return_value=mock_create_response,
            ),
            patch.object(
                web_interface.enhanced_orchestration,
                "execute_enhanced_research",
                new_callable=AsyncMock,
                return_value=mock_result,
            ),
        ):
            result = await web_interface.handle_enhanced_research_request(request_data)

            assert result["success"] is True
            assert result["data"]["query_id"] == "enhanced-query-456"
            assert result["data"]["query"] == "quantum computing algorithms"
            assert result["data"]["sources_count"] == 1
            assert result["data"]["scholarly_sources_included"] is True

            # Check scholarly metadata is included
            source = result["data"]["sources"][0]
            assert "authors" in source
            assert "citation_count" in source
            assert "formatted_citation" in source

    @pytest.mark.asyncio
    async def test_handle_enhanced_research_without_scholarly(self, web_interface):
        """Test enhanced research request without scholarly sources."""
        request_data = {
            "query": "general research topic",
            "include_scholarly": False,
        }

        mock_create_response = Mock()
        mock_create_response.query_id = "no-scholarly-789"

        mock_result = Mock()
        mock_result.query = Mock()
        mock_result.query.text = "general research topic"
        mock_result.status = ResearchStatus.COMPLETED
        mock_result.completed_at = datetime.now()
        mock_result.sources = []

        with (
            patch.object(
                web_interface.create_query_use_case,
                "execute",
                new_callable=AsyncMock,
                return_value=mock_create_response,
            ),
            patch.object(
                web_interface.enhanced_orchestration,
                "execute_enhanced_research",
                new_callable=AsyncMock,
                return_value=mock_result,
            ) as mock_enhanced,
        ):
            result = await web_interface.handle_enhanced_research_request(request_data)

            # Verify enhanced research was called with include_scholarly=False
            mock_enhanced.assert_called_once_with(
                "no-scholarly-789", include_scholarly=False
            )

            assert result["success"] is True
            assert result["data"]["scholarly_sources_included"] is False

    def test_get_api_documentation_includes_scholarly_endpoints(self, web_interface):
        """Test that API documentation includes new scholarly endpoints."""
        doc = web_interface.get_api_documentation()

        assert "openapi" in doc
        assert "paths" in doc

        paths = doc["paths"]

        # Check original endpoints still exist
        assert "/api/research" in paths
        assert "/api/query" in paths
        assert "/api/execute" in paths

        # Check new scholarly endpoints
        assert "/api/scholarly/search" in paths
        assert "/api/research/enhanced" in paths

        # Verify scholarly search endpoint structure
        scholarly_endpoint = paths["/api/scholarly/search"]["post"]
        assert (
            scholarly_endpoint["summary"]
            == "Search academic databases (arXiv, Semantic Scholar)"
        )

        # Check request schema
        schema = scholarly_endpoint["requestBody"]["content"]["application/json"][
            "schema"
        ]
        properties = schema["properties"]
        assert "query" in properties
        assert "sources" in properties
        assert "include_abstracts" in properties
        assert "min_year" in properties

    @pytest.mark.asyncio
    async def test_scholarly_search_with_minimal_params(self, web_interface):
        """Test scholarly search with minimal parameters."""
        minimal_request = {"query": "artificial intelligence"}

        mock_response = ScholarlySearchResponse(
            query_id="minimal-test",
            papers=[],
            total_found=0,
            sources_used=["arxiv", "semantic_scholar"],
            search_time_ms=500,
        )

        with patch.object(
            web_interface.scholarly_use_case,
            "execute_scholarly_search",
            new_callable=AsyncMock,
            return_value=mock_response,
        ) as mock_search:
            result = await web_interface.handle_scholarly_search_request(
                minimal_request
            )

            # Verify defaults were applied
            call_args = mock_search.call_args[0][0]
            assert call_args.sources == ["arxiv", "semantic_scholar"]  # Default sources
            assert call_args.max_results == 10  # Default max_results
            assert call_args.include_abstracts is True  # Default include_abstracts

            assert result["success"] is True

    @pytest.mark.asyncio
    async def test_error_handling_missing_query(self, web_interface):
        """Test error handling when query is missing."""
        invalid_request = {"sources": ["arxiv"]}

        with patch.object(
            web_interface.scholarly_use_case,
            "execute_scholarly_search",
            new_callable=AsyncMock,
            side_effect=Exception("Query text cannot be empty"),
        ):
            result = await web_interface.handle_scholarly_search_request(
                invalid_request
            )

            assert result["success"] is False
            assert "Query text cannot be empty" in result["error"]["message"]


class TestWebUIComponents:
    """Test suite for WebUIComponents with scholarly formatting."""

    def test_format_scholarly_papers_for_display(self):
        """Test formatting scholarly papers for web display."""
        sample_papers = [
            {
                "title": "Test Paper Title",
                "authors": ["Author One", "Author Two", "Author Three", "Author Four"],
                "abstract": "This is a test abstract.",
                "year": 2023,
                "citation_count": 150,
                "pdf_url": "https://example.com/paper.pdf",
                "source_url": "https://example.com/paper",
                "source_type": "arxiv",
                "relevance_score": 0.85,
                "venue": "Test Conference",
                "doi": "10.1000/test.doi",
                "formatted_citation": "One, A. et al. (2023). Test Paper Title. Test Conference.",
                "display_class": "high-relevance",
            }
        ]

        formatted = WebUIComponents.format_scholarly_papers_for_display(sample_papers)

        assert len(formatted) == 1
        paper = formatted[0]

        # Check basic formatting
        assert paper["title"] == "Test Paper Title"
        assert paper["year"] == 2023
        assert paper["has_pdf"] is True
        assert paper["is_recent"] is True  # 2023 should be recent
        assert paper["is_highly_cited"] is True  # 150 > 100

        # Check author formatting (should truncate to "Author One, Author Two et al.")
        assert "et al." in paper["authors_display"]

        # Check citation count formatting
        assert "150 citations" in paper["citation_display"]

        # Check source badge
        badge = paper["source_badge"]
        assert badge["label"] == "arXiv"
        assert badge["class"] == "badge-arxiv"

    def test_format_authors_various_lengths(self):
        """Test author formatting for different list lengths."""
        # Single author
        assert WebUIComponents._format_authors(["Single Author"]) == "Single Author"

        # Two authors
        assert WebUIComponents._format_authors(["First", "Second"]) == "First, Second"

        # Three authors
        assert (
            WebUIComponents._format_authors(["First", "Second", "Third"])
            == "First, Second, Third"
        )

        # More than three authors
        result = WebUIComponents._format_authors(
            ["First", "Second", "Third", "Fourth", "Fifth"]
        )
        assert result == "First, Second et al."

        # Empty list
        assert WebUIComponents._format_authors([]) == "Unknown Authors"

    def test_format_citation_count_various_numbers(self):
        """Test citation count formatting for different ranges."""
        assert WebUIComponents._format_citation_count(0) == "No citations"
        assert WebUIComponents._format_citation_count(1) == "1 citation"
        assert WebUIComponents._format_citation_count(42) == "42 citations"
        assert WebUIComponents._format_citation_count(999) == "999 citations"
        assert WebUIComponents._format_citation_count(1500) == "1.5k citations"
        assert WebUIComponents._format_citation_count(12345) == "12.3k citations"

    def test_get_source_badge_various_sources(self):
        """Test source badge generation for different sources."""
        # Known sources
        arxiv_badge = WebUIComponents._get_source_badge("arxiv")
        assert arxiv_badge["label"] == "arXiv"
        assert arxiv_badge["class"] == "badge-arxiv"
        assert arxiv_badge["color"] == "#b31b1b"

        semantic_badge = WebUIComponents._get_source_badge("semantic_scholar")
        assert semantic_badge["label"] == "Semantic Scholar"
        assert semantic_badge["class"] == "badge-semantic"

        # Unknown source
        unknown_badge = WebUIComponents._get_source_badge("unknown_source")
        assert unknown_badge["label"] == "Unknown Source"
        assert unknown_badge["class"] == "badge-default"

    def test_is_recent_paper(self):
        """Test recent paper detection."""
        from datetime import datetime

        current_year = datetime.now().year

        # Recent papers (last 3 years)
        assert WebUIComponents._is_recent_paper(current_year) is True
        assert WebUIComponents._is_recent_paper(current_year - 1) is True
        assert WebUIComponents._is_recent_paper(current_year - 2) is True

        # Older papers
        assert WebUIComponents._is_recent_paper(current_year - 4) is False
        assert WebUIComponents._is_recent_paper(2000) is False

        # Edge cases
        assert WebUIComponents._is_recent_paper(None) is False

    def test_generate_scholarly_search_suggestions(self):
        """Test academic search suggestion generation."""
        # Machine learning suggestions
        ml_suggestions = WebUIComponents.generate_scholarly_search_suggestions(
            "machine learning neural networks"
        )
        assert len(ml_suggestions) <= 5
        assert any("deep learning" in s for s in ml_suggestions)

        # AI suggestions
        ai_suggestions = WebUIComponents.generate_scholarly_search_suggestions(
            "artificial intelligence applications"
        )
        assert any("AI safety" in s for s in ai_suggestions)

        # Quantum computing suggestions
        quantum_suggestions = WebUIComponents.generate_scholarly_search_suggestions(
            "quantum computing algorithms"
        )
        assert any("quantum" in s for s in quantum_suggestions)

        # Climate suggestions
        climate_suggestions = WebUIComponents.generate_scholarly_search_suggestions(
            "climate change solutions"
        )
        assert any("climate" in s or "renewable" in s for s in climate_suggestions)

    def test_format_results_for_display_backwards_compatibility(self):
        """Test that existing format_results_for_display still works."""
        sample_results = [
            {
                "content": "Test content for result",
                "source": "test_source",
                "relevance_score": 0.75,
                "timestamp": "2024-01-01T00:00:00",
            }
        ]

        formatted = WebUIComponents.format_results_for_display(sample_results)

        assert len(formatted) == 1
        result = formatted[0]
        assert result["source"] == "test_source"
        assert result["relevance_percentage"] == 75
        assert result["display_class"] == "medium-relevance"


class TestWebInterfaceFactory:
    """Test the web interface factory function."""

    def test_create_web_interface(self):
        """Test factory creates properly configured web interface."""
        interface = create_web_interface()

        assert isinstance(interface, WebInterfaceHandler)
        assert hasattr(interface, "scholarly_use_case")
        assert hasattr(interface, "enhanced_orchestration")
        assert hasattr(interface, "logger")


class TestIntegrationScenarios:
    """Integration test scenarios combining multiple components."""

    @pytest.fixture
    def web_interface(self):
        return WebInterfaceHandler()

    @pytest.mark.asyncio
    async def test_full_scholarly_research_workflow(self, web_interface):
        """Test complete workflow from search to display formatting."""
        # Step 1: Execute scholarly search
        search_request = {
            "query": "transformer architecture attention mechanism",
            "sources": ["arxiv"],
            "max_results": 2,
        }

        # Mock scholarly search response
        mock_papers = [
            {
                "title": "Attention Is All You Need",
                "authors": ["Ashish Vaswani", "Noam Shazeer"],
                "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks...",
                "year": 2017,
                "citation_count": 75842,
                "pdf_url": "https://arxiv.org/pdf/1706.03762.pdf",
                "source_url": "https://arxiv.org/abs/1706.03762",
                "source_type": "arxiv",
                "relevance_score": 0.95,
                "venue": "NeurIPS",
                "formatted_citation": "Vaswani, A. et al. (2017). Attention Is All You Need. NeurIPS.",
                "display_class": "high-relevance",
            }
        ]

        mock_response = ScholarlySearchResponse(
            query_id="integration-test",
            papers=mock_papers,
            total_found=1,
            sources_used=["arxiv"],
            search_time_ms=800,
        )

        with patch.object(
            web_interface.scholarly_use_case,
            "execute_scholarly_search",
            new_callable=AsyncMock,
            return_value=mock_response,
        ):
            # Execute search
            search_result = await web_interface.handle_scholarly_search_request(
                search_request
            )

            assert search_result["success"] is True
            papers = search_result["data"]["papers"]

            # Step 2: Format papers for display
            formatted_papers = WebUIComponents.format_scholarly_papers_for_display(
                papers
            )

            assert len(formatted_papers) == 1
            paper = formatted_papers[0]

            # Verify comprehensive formatting
            assert paper["title"] == "Attention Is All You Need"
            assert paper["is_highly_cited"] is True
            assert paper["has_pdf"] is True
            assert paper["source_badge"]["label"] == "arXiv"
            assert "Ashish Vaswani" in paper["authors_display"]
            assert "75.8k citations" in paper["citation_display"]

    @pytest.mark.asyncio
    async def test_error_recovery_and_logging(self, web_interface):
        """Test error recovery and logging in scholarly interface."""
        # Test with invalid request that should trigger error handling
        invalid_request = {"query": ""}  # Empty query

        with patch.object(
            web_interface.scholarly_use_case,
            "execute_scholarly_search",
            new_callable=AsyncMock,
            side_effect=Exception("Invalid query parameters"),
        ):
            result = await web_interface.handle_scholarly_search_request(
                invalid_request
            )

            # Should gracefully handle error
            assert result["success"] is False
            assert "Invalid query parameters" in result["error"]["message"]
            assert result["error"]["type"] == "Exception"

    def test_api_documentation_completeness(self, web_interface):
        """Test that API documentation is complete and accurate."""
        doc = web_interface.get_api_documentation()

        # Verify structure
        assert doc["openapi"] == "3.0.0"
        assert "info" in doc
        assert "paths" in doc

        # Verify all expected endpoints
        paths = doc["paths"]
        expected_endpoints = [
            "/api/research",
            "/api/query",
            "/api/execute",
            "/api/scholarly/search",
            "/api/research/enhanced",
        ]

        for endpoint in expected_endpoints:
            assert endpoint in paths, f"Missing endpoint: {endpoint}"

        # Verify scholarly endpoint has proper schema
        scholarly_schema = paths["/api/scholarly/search"]["post"]["requestBody"][
            "content"
        ]["application/json"]["schema"]

        required_properties = ["query", "sources", "max_results", "include_abstracts"]
        for prop in required_properties:
            assert prop in scholarly_schema["properties"], f"Missing property: {prop}"
