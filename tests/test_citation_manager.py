#!/usr/bin/env python3
"""
AI Deep Research MCP - CitationManager Component Tests

Tests for the citation management system that handles source tracking,
citation formatting, and reference management for research answers.

RED PHASE: Writing tests first to define expected behavior
"""

import pytest
import tempfile
import json
from unittest.mock import Mock
from dataclasses import dataclass
from typing import List, Dict, Any, Optional

# Test imports - these will fail initially (RED phase)
try:
    from src.citation_manager import (
        CitationManager,
        SourceInfo,
        Citation,
        CitationStyle,
        CiteError
    )
except ImportError:
    # Expected during RED phase
    pass


class TestCitationManager:
    """Test suite for CitationManager component"""
    
    def test_citation_manager_exists(self):
        """Test that CitationManager class exists"""
        from src.citation_manager import CitationManager
        assert CitationManager is not None
    
    def test_source_info_dataclass(self):
        """Test SourceInfo dataclass structure"""
        from src.citation_manager import SourceInfo
        
        source = SourceInfo(
            url="https://example.com/article",
            title="Example Article",
            author="John Doe",
            publication_date="2025-01-15",
            domain="example.com"
        )
        
        assert source.url == "https://example.com/article"
        assert source.title == "Example Article"
        assert source.author == "John Doe"
        assert source.publication_date == "2025-01-15"
        assert source.domain == "example.com"
    
    def test_citation_dataclass(self):
        """Test Citation dataclass structure"""
        from src.citation_manager import Citation, SourceInfo
        
        source = SourceInfo(
            url="https://example.com",
            title="Test",
            domain="example.com"
        )
        
        citation = Citation(
            source=source,
            citation_id="1",
            text_snippet="This is a test quote",
            page_number=42
        )
        
        assert citation.source.url == "https://example.com"
        assert citation.citation_id == "1"
        assert citation.text_snippet == "This is a test quote"
        assert citation.page_number == 42
    
    def test_citation_style_enum(self):
        """Test CitationStyle enumeration"""
        from src.citation_manager import CitationStyle
        
        assert CitationStyle.APA
        assert CitationStyle.MLA
        assert CitationStyle.CHICAGO
        assert CitationStyle.IEEE
        assert CitationStyle.WEB_SIMPLE
    
    def test_add_source_basic(self):
        """Test adding sources to citation manager"""
        from src.citation_manager import CitationManager, SourceInfo
        
        manager = CitationManager()
        source = SourceInfo(
            url="https://example.com/test",
            title="Test Article",
            domain="example.com"
        )
        
        citation_id = manager.add_source(source)
        assert citation_id is not None
        assert isinstance(citation_id, str)
        assert len(citation_id) > 0
    
    def test_add_multiple_sources(self):
        """Test adding multiple sources and getting unique IDs"""
        from src.citation_manager import CitationManager, SourceInfo
        
        manager = CitationManager()
        
        source1 = SourceInfo(url="https://site1.com", title="Article 1", domain="site1.com")
        source2 = SourceInfo(url="https://site2.com", title="Article 2", domain="site2.com")
        
        id1 = manager.add_source(source1)
        id2 = manager.add_source(source2)
        
        assert id1 != id2
        assert manager.get_source(id1).url == "https://site1.com"
        assert manager.get_source(id2).url == "https://site2.com"
    
    def test_duplicate_source_handling(self):
        """Test handling of duplicate sources"""
        from src.citation_manager import CitationManager, SourceInfo
        
        manager = CitationManager()
        source = SourceInfo(url="https://same.com", title="Same Article", domain="same.com")
        
        id1 = manager.add_source(source)
        id2 = manager.add_source(source)  # Same source again
        
        # Should return same ID for duplicate source
        assert id1 == id2
    
    def test_create_citation_with_snippet(self):
        """Test creating citations with text snippets"""
        from src.citation_manager import CitationManager, SourceInfo
        
        manager = CitationManager()
        source = SourceInfo(url="https://test.com", title="Test", domain="test.com")
        source_id = manager.add_source(source)
        
        citation = manager.create_citation(
            source_id=source_id,
            text_snippet="This is an important finding",
            page_number=5
        )
        
        assert citation.citation_id == source_id
        assert citation.text_snippet == "This is an important finding"
        assert citation.page_number == 5
    
    def test_format_citation_apa_style(self):
        """Test APA citation formatting"""
        from src.citation_manager import CitationManager, SourceInfo, CitationStyle
        
        manager = CitationManager()
        source = SourceInfo(
            url="https://journal.com/article",
            title="Research Methods in AI",
            author="Smith, J.",
            publication_date="2025-01-15",
            domain="journal.com"
        )
        
        citation_id = manager.add_source(source)
        formatted = manager.format_citation(citation_id, CitationStyle.APA)
        
        assert "Smith, J." in formatted
        assert "Research Methods in AI" in formatted
        assert "2025" in formatted
    
    def test_format_citation_web_simple_style(self):
        """Test simple web citation formatting"""
        from src.citation_manager import CitationManager, SourceInfo, CitationStyle
        
        manager = CitationManager()
        source = SourceInfo(
            url="https://blog.example.com/post",
            title="Understanding Deep Learning",
            domain="blog.example.com"
        )
        
        citation_id = manager.add_source(source)
        formatted = manager.format_citation(citation_id, CitationStyle.WEB_SIMPLE)
        
        assert "Understanding Deep Learning" in formatted
        assert "blog.example.com" in formatted
    
    def test_generate_bibliography(self):
        """Test generating complete bibliography"""
        from src.citation_manager import CitationManager, SourceInfo, CitationStyle
        
        manager = CitationManager()
        
        sources = [
            SourceInfo(url="https://site1.com", title="Article 1", author="Author A", domain="site1.com"),
            SourceInfo(url="https://site2.com", title="Article 2", author="Author B", domain="site2.com"),
            SourceInfo(url="https://site3.com", title="Article 3", author="Author C", domain="site3.com")
        ]
        
        for source in sources:
            manager.add_source(source)
        
        bibliography = manager.generate_bibliography(CitationStyle.APA)
        
        assert "Article 1" in bibliography
        assert "Article 2" in bibliography  
        assert "Article 3" in bibliography
        assert "Author A" in bibliography
    
    def test_inline_citation_insertion(self):
        """Test inserting inline citations into text"""
        from src.citation_manager import CitationManager, SourceInfo
        
        manager = CitationManager()
        source = SourceInfo(url="https://test.com", title="Test Source", domain="test.com")
        citation_id = manager.add_source(source)
        
        text = "This is a fact that needs citation."
        cited_text = manager.insert_inline_citation(text, citation_id, position="end")
        
        assert citation_id in cited_text or "[1]" in cited_text
        assert "This is a fact that needs citation" in cited_text
    
    def test_citation_tracking_in_text(self):
        """Test tracking citations within generated text"""
        from src.citation_manager import CitationManager, SourceInfo
        
        manager = CitationManager()
        
        # Add sources
        source1 = SourceInfo(url="https://site1.com", title="Source 1", domain="site1.com")
        source2 = SourceInfo(url="https://site2.com", title="Source 2", domain="site2.com")
        
        id1 = manager.add_source(source1)
        id2 = manager.add_source(source2)
        
        # Text with citation markers
        text = f"Fact one [{id1}]. Another fact [{id2}]. More content."
        
        used_citations = manager.extract_citations_from_text(text)
        assert id1 in used_citations
        assert id2 in used_citations
        assert len(used_citations) == 2
    
    def test_citation_validation(self):
        """Test validation of citation data"""
        from src.citation_manager import CitationManager, SourceInfo, CiteError
        
        manager = CitationManager()
        
        # Invalid source (missing required fields)
        with pytest.raises(CiteError):
            invalid_source = SourceInfo(url="", title="", domain="")
            manager.add_source(invalid_source)
    
    def test_export_citations_json(self):
        """Test exporting citations to JSON format"""
        from src.citation_manager import CitationManager, SourceInfo
        
        manager = CitationManager()
        source = SourceInfo(
            url="https://example.com",
            title="Test Article",
            author="Test Author",
            domain="example.com"
        )
        
        manager.add_source(source)
        exported = manager.export_citations("json")
        
        assert isinstance(exported, str)
        data = json.loads(exported)
        assert "sources" in data
        assert len(data["sources"]) == 1
    
    def test_import_citations_json(self):
        """Test importing citations from JSON format"""
        from src.citation_manager import CitationManager
        
        # Create manager with initial data
        manager1 = CitationManager()
        source_data = {
            "sources": [
                {
                    "url": "https://import-test.com",
                    "title": "Imported Article",
                    "author": "Import Author",
                    "domain": "import-test.com"
                }
            ]
        }
        
        # Import into new manager
        manager2 = CitationManager()
        manager2.import_citations(json.dumps(source_data))
        
        # Should be able to retrieve imported source
        sources = manager2.get_all_sources()
        assert len(sources) == 1
        assert sources[0].title == "Imported Article"
    
    def test_citation_deduplication(self):
        """Test automatic deduplication of similar sources"""
        from src.citation_manager import CitationManager, SourceInfo
        
        manager = CitationManager()
        
        # Very similar sources (should be treated as duplicates)
        source1 = SourceInfo(
            url="https://example.com/article?ref=1",
            title="Test Article",
            domain="example.com"
        )
        source2 = SourceInfo(
            url="https://example.com/article?ref=2", 
            title="Test Article",
            domain="example.com"
        )
        
        id1 = manager.add_source(source1)
        id2 = manager.add_source(source2, deduplicate=True)
        
        # Should return same ID if deduplication is enabled
        assert id1 == id2


class TestCitationManagerIntegration:
    """Integration tests for CitationManager with other components"""
    
    def setup_method(self):
        """Set up test fixtures before each test"""
        self.temp_dir = tempfile.mkdtemp()
    
    def teardown_method(self):
        """Clean up test fixtures after each test"""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_integration_with_retriever_results(self):
        """Test integration with retrieval results from vector store"""
        from src.citation_manager import CitationManager, SourceInfo
        
        # Mock retrieval results
        mock_retrieval_results = [
            Mock(
                text="Important research finding",
                source_url="https://research.com/paper1",
                metadata={"title": "Research Paper 1", "author": "Dr. Smith"}
            ),
            Mock(
                text="Another significant discovery", 
                source_url="https://research.com/paper2",
                metadata={"title": "Research Paper 2", "author": "Dr. Jones"}
            )
        ]
        
        manager = CitationManager()
        
        # Process retrieval results into citations
        citation_ids = []
        for result in mock_retrieval_results:
            source = SourceInfo(
                url=result.source_url,
                title=result.metadata.get("title", ""),
                author=result.metadata.get("author", ""),
                domain=result.source_url.split("//")[1].split("/")[0]
            )
            citation_id = manager.add_source(source)
            citation_ids.append(citation_id)
        
        # Should have created citations for all sources
        assert len(citation_ids) == 2
        assert all(cid for cid in citation_ids)
        
        # Should be able to generate bibliography
        bibliography = manager.generate_bibliography()
        assert "Research Paper 1" in bibliography
        assert "Research Paper 2" in bibliography
