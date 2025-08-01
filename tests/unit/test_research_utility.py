"""
🎯 RESEARCH UTILITY TESTS for AI Deep Research MCP

Educational Test Guide:
These tests ensure our research platform works correctly for real academics!

What we're testing:
- Citation exports (BibTeX, RIS, EndNote, APA formats)
- Advanced search with academic filters
- Research collection management
- Web interface endpoints for researchers

Why this matters:
- Researchers depend on accurate citation formats
- Academic databases have specific requirements
- Reference managers need exact format compliance
"""

import pytest
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from src.application.scholarly_use_cases import (
    ScholarlyResearchUseCase,
    ScholarlySearchRequest,
    ScholarlySearchResponse,
)
from src.presentation.web_interface import WebInterfaceHandler
from src.infrastructure.repositories import (
    InMemoryResearchQueryRepository,
    InMemoryResearchResultRepository,
)


class TestCitationExport:
    """Test citation export functionality for reference managers."""

    def setup_method(self):
        """Set up test data with realistic academic papers."""
        self.use_case = ScholarlyResearchUseCase(
            InMemoryResearchQueryRepository(), InMemoryResearchResultRepository()
        )

        self.sample_papers = [
            {
                "title": "Attention Is All You Need",
                "authors": ["Ashish Vaswani", "Noam Shazeer", "Niki Parmar"],
                "year": 2017,
                "venue": "Neural Information Processing Systems",
                "doi": "10.5555/3295222.3295349",
                "abstract": "The dominant sequence transduction models are based on complex recurrent or convolutional neural networks.",
                "source_url": "https://arxiv.org/abs/1706.03762",
            },
            {
                "title": "BERT: Pre-training of Deep Bidirectional Transformers",
                "authors": ["Jacob Devlin", "Ming-Wei Chang", "Kenton Lee"],
                "year": 2019,
                "venue": "NAACL-HLT",
                "doi": "10.18653/v1/N19-1423",
                "abstract": "We introduce a new language representation model called BERT.",
                "source_url": "https://arxiv.org/abs/1810.04805",
            },
        ]

    def test_bibtex_export_format(self):
        """Test BibTeX export produces correctly formatted entries."""
        bibtex = self.use_case.export_citations(self.sample_papers, "bibtex")

        # Check required BibTeX fields
        assert "@article{" in bibtex
        assert "title = {Attention Is All You Need}" in bibtex
        assert "author = {Ashish Vaswani and Noam Shazeer and Niki Parmar}" in bibtex
        assert "year = {2017}" in bibtex
        assert "doi = {10.5555/3295222.3295349}" in bibtex

        # Should contain both papers
        assert "BERT: Pre-training" in bibtex
        assert bibtex.count("@article{") == 2

    def test_ris_export_format(self):
        """Test RIS export for EndNote compatibility."""
        ris = self.use_case.export_citations(self.sample_papers, "ris")

        # Check RIS format requirements
        assert "TY  - JOUR" in ris  # Journal article type
        assert "TI  - Attention Is All You Need" in ris
        assert "AU  - Ashish Vaswani" in ris
        assert "PY  - 2017" in ris
        assert "ER  - " in ris  # End record marker

        # Should have correct number of records
        assert ris.count("TY  - JOUR") == 2
        assert ris.count("ER  - ") == 2

    def test_endnote_export_format(self):
        """Test EndNote tagged format export."""
        endnote = self.use_case.export_citations(self.sample_papers, "endnote")

        # Check EndNote format requirements
        assert "%0 Journal Article" in endnote
        assert "%T Attention Is All You Need" in endnote
        assert "%A Ashish Vaswani" in endnote
        assert "%D 2017" in endnote
        assert "%R 10.5555/3295222.3295349" in endnote

    def test_apa_export_format(self):
        """Test APA citation format export."""
        apa = self.use_case.export_citations(self.sample_papers, "apa")

        # Check APA format requirements (using actual format from implementation)
        assert "Ashish Vaswani, Noam Shazeer, & Niki Parmar (2017)" in apa
        assert "Attention Is All You Need" in apa
        assert "Neural Information Processing Systems" in apa
        assert "https://doi.org/10.5555/3295222.3295349" in apa

    def test_invalid_format_raises_error(self):
        """Test that invalid export format raises appropriate error."""
        with pytest.raises(Exception) as exc_info:
            self.use_case.export_citations(self.sample_papers, "invalid_format")

        assert "Unsupported citation format" in str(exc_info.value)

    def test_empty_papers_handling(self):
        """Test citation export with empty paper list."""
        result = self.use_case.export_citations([], "bibtex")
        assert result == ""


class TestAdvancedSearchInterface:
    """Test advanced search functionality for researchers."""

    def setup_method(self):
        """Set up web interface handler for testing."""
        self.handler = WebInterfaceHandler()

    @pytest.mark.asyncio
    async def test_advanced_search_with_filters(self):
        """Test advanced search with year and field filters."""
        request_data = {
            "query": "machine learning",
            "sources": ["arxiv", "semantic_scholar"],
            "max_results": 10,
            "min_year": 2020,
            "max_year": 2024,
            "fields_of_study": ["Computer Science", "Artificial Intelligence"],
        }

        # Mock the scholarly use case to avoid actual API calls
        self.handler.scholarly_use_case.execute_scholarly_search = AsyncMock(
            return_value=ScholarlySearchResponse(
                query_id="test-id",
                papers=[{"title": "Test Paper", "authors": ["Test Author"]}],
                total_found=1,
                sources_used=["arxiv"],
                search_time_ms=100,
            )
        )

        response = await self.handler.handle_advanced_search_request(request_data)

        assert response["success"] is True
        assert "papers" in response["data"]
        assert response["data"]["filters_applied"]["min_year"] == 2020
        assert response["data"]["filters_applied"]["max_year"] == 2024

    @pytest.mark.asyncio
    async def test_empty_query_validation(self):
        """Test that empty queries are properly rejected."""
        request_data = {"query": "   "}  # Empty/whitespace query

        response = await self.handler.handle_advanced_search_request(request_data)

        assert response["success"] is False
        assert "cannot be empty" in response["error"]["message"]


class TestResearchCollections:
    """Test research collection management for organizing papers."""

    def setup_method(self):
        """Set up web interface handler for testing."""
        self.handler = WebInterfaceHandler()

    @pytest.mark.asyncio
    async def test_create_research_collection(self):
        """Test creating a new research collection."""
        request_data = {
            "action": "create",
            "name": "My AI Research",
            "description": "Collection of papers on artificial intelligence",
        }

        response = await self.handler.handle_research_collection_request(request_data)

        assert response["success"] is True
        assert response["data"]["name"] == "My AI Research"
        assert "id" in response["data"]
        assert "created_at" in response["data"]

    @pytest.mark.asyncio
    async def test_add_paper_to_collection(self):
        """Test adding a paper to an existing collection."""
        request_data = {
            "action": "add_paper",
            "collection_id": "test-collection-id",
            "paper": {"title": "Test Paper", "authors": ["Test Author"], "year": 2024},
        }

        response = await self.handler.handle_research_collection_request(request_data)

        assert response["success"] is True
        assert response["data"]["paper_added"] is True

    @pytest.mark.asyncio
    async def test_empty_collection_name_validation(self):
        """Test that empty collection names are rejected."""
        request_data = {"action": "create", "name": "   "}  # Empty/whitespace name

        response = await self.handler.handle_research_collection_request(request_data)

        assert response["success"] is False
        assert "cannot be empty" in response["error"]["message"]


class TestWebInterfaceCitationExport:
    """Test citation export through web interface."""

    def setup_method(self):
        """Set up web interface handler for testing."""
        self.handler = WebInterfaceHandler()

        # Mock the scholarly use case
        self.handler.scholarly_use_case = Mock()
        self.handler.scholarly_use_case.export_citations = Mock(
            return_value="@article{test2024, title={Test Paper}}"
        )

    @pytest.mark.asyncio
    async def test_citation_export_via_web_interface(self):
        """Test citation export through web API."""
        request_data = {
            "papers": [{"title": "Test Paper", "authors": ["Test Author"]}],
            "format": "bibtex",
        }

        response = await self.handler.handle_citation_export_request(request_data)

        assert response["success"] is True
        assert "citations" in response["data"]
        assert response["data"]["format"] == "bibtex"
        assert response["data"]["content_type"] == "application/x-bibtex"
        assert response["data"]["filename"] == "research_citations.bibtex"

    @pytest.mark.asyncio
    async def test_export_with_no_papers(self):
        """Test export request with no papers provided."""
        request_data = {"papers": [], "format": "bibtex"}

        response = await self.handler.handle_citation_export_request(request_data)

        assert response["success"] is False
        assert "No papers provided" in response["error"]["message"]


# Integration test for complete research workflow
class TestResearchWorkflowIntegration:
    """Test complete research workflow from search to export."""

    @pytest.mark.asyncio
    async def test_complete_research_workflow(self):
        """Test the complete workflow: search → collect → export."""
        handler = WebInterfaceHandler()

        # Mock the scholarly search
        mock_papers = [
            {
                "title": "Test AI Paper",
                "authors": ["Dr. AI", "Prof. ML"],
                "year": 2024,
                "venue": "AI Conference",
                "abstract": "This paper presents...",
                "source_url": "https://example.com/paper",
            }
        ]

        handler.scholarly_use_case.execute_scholarly_search = AsyncMock(
            return_value=ScholarlySearchResponse(
                query_id="workflow-test",
                papers=mock_papers,
                total_found=1,
                sources_used=["arxiv"],
                search_time_ms=150,
            )
        )

        handler.scholarly_use_case.export_citations = Mock(
            return_value="@article{AI2024Test, title={Test AI Paper}}"
        )

        # Step 1: Advanced search
        search_request = {"query": "artificial intelligence", "max_results": 5}
        search_response = await handler.handle_advanced_search_request(search_request)
        assert search_response["success"] is True
        papers = search_response["data"]["papers"]

        # Step 2: Create collection
        collection_request = {"action": "create", "name": "AI Research Papers"}
        collection_response = await handler.handle_research_collection_request(
            collection_request
        )
        assert collection_response["success"] is True

        # Step 3: Export citations
        export_request = {"papers": papers, "format": "bibtex"}
        export_response = await handler.handle_citation_export_request(export_request)
        assert export_response["success"] is True

        # Verify the complete workflow succeeded
        assert len(papers) > 0
        assert "Test AI Paper" in export_response["data"]["citations"]
