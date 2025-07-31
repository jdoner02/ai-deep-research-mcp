#!/usr/bin/env python3
"""
Test Guardian Agent - RED Phase
Test cases for Document Parser component of AI Deep Research MCP system

These tests define the expected behavior of the DocumentParser class before implementation.
They will FAIL initially (RED phase) until we implement the code.
"""

import pytest
from typing import List, Dict, Any
from unittest.mock import Mock, patch, mock_open
from pathlib import Path

# Import will fail initially - this is expected in RED phase
try:
    from src.document_parser import DocumentParser, ParsedDocument
except ImportError:
    DocumentParser = None
    ParsedDocument = None


class TestDocumentParser:
    """Test suite for DocumentParser component - defining expected behavior"""
    
    def test_document_parser_exists(self):
        """Test that DocumentParser class exists and can be instantiated"""
        assert DocumentParser is not None, "DocumentParser class should exist"
        parser = DocumentParser()
        assert parser is not None
    
    def test_parsed_document_dataclass(self):
        """Test that ParsedDocument dataclass exists with required fields"""
        assert ParsedDocument is not None, "ParsedDocument dataclass should exist"
        
        doc = ParsedDocument(
            title="Test Document",
            content="Test content here",
            source_url="https://example.com",
            metadata={"author": "Test Author"},
            content_type="text/html"
        )
        
        assert doc.title == "Test Document"
        assert doc.content == "Test content here"
        assert doc.source_url == "https://example.com"
        assert doc.metadata["author"] == "Test Author"
        assert doc.content_type == "text/html"
    
    def test_parse_html_content(self):
        """Test parsing HTML content to extract main text"""
        parser = DocumentParser()
        
        html_content = """
        <html>
        <head>
            <title>Test Article</title>
            <meta name="description" content="A test article">
        </head>
        <body>
            <nav>Navigation menu</nav>
            <article>
                <h1>Main Article Title</h1>
                <p>This is the main content of the article.</p>
                <p>Another paragraph with important information.</p>
            </article>
            <aside>Sidebar content</aside>
            <footer>Footer information</footer>
        </body>
        </html>
        """
        
        result = parser.parse_html(html_content, source_url="https://example.com")
        
        assert isinstance(result, ParsedDocument)
        assert result.title == "Test Article" or result.title == "Main Article Title"
        assert "main content of the article" in result.content
        assert "important information" in result.content
        
        # Should filter out navigation and footer
        assert "Navigation menu" not in result.content
        assert "Footer information" not in result.content
        
        assert result.source_url == "https://example.com"
        assert result.content_type == "text/html"
    
    def test_parse_pdf_content(self):
        """Test parsing PDF content to extract text"""
        parser = DocumentParser()
        
        # Mock PDF parsing
        with patch('src.document_parser.fitz') as mock_fitz:
            mock_page = Mock()
            mock_page.get_text.return_value = "This is text extracted from PDF."
            
            mock_doc = Mock()
            mock_doc.__iter__ = Mock(return_value=iter([mock_page]))
            mock_doc.close.return_value = None
            
            mock_fitz.open.return_value = mock_doc
            
            pdf_bytes = b"Mock PDF content"
            result = parser.parse_pdf(pdf_bytes, source_url="https://example.com/doc.pdf")
            
            assert isinstance(result, ParsedDocument)
            assert result.content == "This is text extracted from PDF."
            assert result.content_type == "application/pdf"
            assert result.source_url == "https://example.com/doc.pdf"
    
    def test_parse_markdown_content(self):
        """Test parsing Markdown content"""
        parser = DocumentParser()
        
        markdown_content = """
        # Main Title
        
        This is a **bold** statement and this is *italic*.
        
        ## Subsection
        
        - List item 1
        - List item 2
        
        Here's a [link](https://example.com).
        """
        
        result = parser.parse_markdown(markdown_content, source_url="https://example.com")
        
        assert isinstance(result, ParsedDocument)
        assert "Main Title" in result.content
        assert "bold statement" in result.content
        assert "List item 1" in result.content
        assert result.content_type == "text/markdown"
    
    def test_auto_detect_content_type(self):
        """Test automatic detection of content type"""
        parser = DocumentParser()
        
        html_content = "<html><body>HTML content</body></html>"
        pdf_content = b"%PDF-1.4 binary content"
        json_content = '{"key": "value", "data": "JSON content"}'
        
        assert parser.detect_content_type(html_content) == "text/html"
        assert parser.detect_content_type(pdf_content) == "application/pdf"
        assert parser.detect_content_type(json_content) == "application/json"
    
    def test_extract_metadata_from_html(self):
        """Test extraction of metadata from HTML headers"""
        parser = DocumentParser()
        
        html_with_metadata = """
        <html>
        <head>
            <title>Research Paper Title</title>
            <meta name="author" content="Dr. Jane Smith">
            <meta name="description" content="A comprehensive study">
            <meta name="keywords" content="AI, machine learning, research">
            <meta property="og:title" content="OG Title">
            <meta name="publication-date" content="2024-01-15">
        </head>
        <body>Content here</body>
        </html>
        """
        
        result = parser.parse_html(html_with_metadata, source_url="https://example.com")
        
        assert result.metadata["author"] == "Dr. Jane Smith"
        assert result.metadata["description"] == "A comprehensive study"
        assert result.metadata["keywords"] == "AI, machine learning, research"
        assert result.metadata["publication-date"] == "2024-01-15"
    
    def test_clean_and_normalize_text(self):
        """Test text cleaning and normalization"""
        parser = DocumentParser()
        
        messy_text = """
        
        
        This    has     extra    spaces.
        
        
        And extra line breaks.
        
        
        Also some\ttabs\there.
        """
        
        cleaned = parser.clean_text(messy_text)
        
        assert cleaned == "This has extra spaces.\n\nAnd extra line breaks.\n\nAlso some tabs here."
        
        # Should remove excessive whitespace but preserve paragraph breaks
        assert "    " not in cleaned
        assert "\n\n\n" not in cleaned
    
    def test_handle_different_encodings(self):
        """Test handling of different text encodings"""
        parser = DocumentParser()
        
        # Test UTF-8 with special characters
        utf8_content = "Café résumé naïve façade"
        result = parser.parse_text(utf8_content, source_url="https://example.com")
        
        assert isinstance(result, ParsedDocument)
        assert "Café" in result.content
        assert "résumé" in result.content
    
    def test_parse_json_structured_data(self):
        """Test parsing JSON structured data"""
        parser = DocumentParser()
        
        json_content = """
        {
            "title": "API Response Data",
            "articles": [
                {"headline": "News Item 1", "content": "First news content"},
                {"headline": "News Item 2", "content": "Second news content"}
            ],
            "metadata": {
                "source": "News API",
                "timestamp": "2024-01-15T10:00:00Z"
            }
        }
        """
        
        result = parser.parse_json(json_content, source_url="https://api.example.com")
        
        assert isinstance(result, ParsedDocument)
        assert "News Item 1" in result.content
        assert "First news content" in result.content
        assert result.content_type == "application/json"
    
    def test_error_handling_malformed_content(self):
        """Test graceful handling of malformed content"""
        parser = DocumentParser()
        
        # Malformed HTML
        malformed_html = "<html><body><p>Unclosed paragraph<div>Nested incorrectly</p></div>"
        
        result = parser.parse_html(malformed_html, source_url="https://example.com")
        
        # Should still extract some content despite malformation
        assert isinstance(result, ParsedDocument)
        assert "Unclosed paragraph" in result.content
    
    def test_content_length_limits(self):
        """Test handling of extremely long content"""
        parser = DocumentParser(max_content_length=1000)
        
        very_long_content = "A" * 2000  # 2000 characters
        
        result = parser.parse_text(very_long_content, source_url="https://example.com")
        
        # Should truncate or handle gracefully
        assert len(result.content) <= 1000
    
    def test_preserve_structure_for_academic_papers(self):
        """Test preservation of document structure for academic content"""
        parser = DocumentParser(preserve_structure=True)
        
        academic_html = """
        <html>
        <body>
        <h1>Abstract</h1>
        <p>This paper presents...</p>
        
        <h1>Introduction</h1>
        <p>Recent advances in...</p>
        
        <h2>1.1 Background</h2>
        <p>Previous work has shown...</p>
        
        <h1>Methodology</h1>
        <p>We employed the following approach...</p>
        </body>
        </html>
        """
        
        result = parser.parse_html(academic_html, source_url="https://arxiv.org/abs/1234")
        
        # Should preserve section headers
        assert "# Abstract" in result.content or "Abstract" in result.content
        assert "# Introduction" in result.content or "Introduction" in result.content
        assert "# Methodology" in result.content or "Methodology" in result.content
    
    def test_filter_unwanted_elements(self):
        """Test filtering of unwanted HTML elements"""
        parser = DocumentParser()
        
        html_with_noise = """
        <html>
        <body>
        <article>
            <h1>Main Content</h1>
            <p>This is important content.</p>
            
            <script>alert('malicious code')</script>
            <style>body { color: red; }</style>
            
            <div class="advertisement">Buy our product!</div>
            <nav>Home | About | Contact</nav>
            
            <p>More important content here.</p>
        </article>
        </body>
        </html>
        """
        
        result = parser.parse_html(html_with_noise, source_url="https://example.com")
        
        # Should include main content
        assert "important content" in result.content
        assert "More important content" in result.content
        
        # Should filter out scripts, styles, ads, navigation
        assert "alert('malicious code')" not in result.content
        assert "color: red" not in result.content
        assert "Buy our product!" not in result.content
        assert "Home | About | Contact" not in result.content
    
    def test_parse_multiple_documents_batch(self):
        """Test batch parsing of multiple documents"""
        parser = DocumentParser()
        
        documents = [
            {"content": "<html><body>Doc 1</body></html>", "url": "https://example.com/1", "type": "html"},
            {"content": "<html><body>Doc 2</body></html>", "url": "https://example.com/2", "type": "html"},
            {"content": "Plain text document", "url": "https://example.com/3", "type": "text"}
        ]
        
        results = parser.parse_batch(documents)
        
        assert isinstance(results, list)
        assert len(results) == 3
        
        for result in results:
            assert isinstance(result, ParsedDocument)
            assert result.content is not None
            assert result.source_url is not None


class TestDocumentParserIntegration:
    """Integration tests for DocumentParser with real content"""
    
    def test_parse_real_webpage_content(self, temp_dir):
        """Test parsing content from a real webpage structure"""
        parser = DocumentParser()
        
        # Simulate real webpage HTML
        real_html = """
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <title>Real Article Title</title>
            <meta name="description" content="This is a real article description">
            <meta name="author" content="John Doe">
        </head>
        <body>
            <header>
                <nav>Navigation links</nav>
            </header>
            <main>
                <article>
                    <h1>Real Article Title</h1>
                    <p>This is the first paragraph of real content with actual information.</p>
                    <h2>Section 1</h2>
                    <p>This section contains detailed information about the topic.</p>
                    <h2>Section 2</h2>
                    <p>Another section with more detailed content and analysis.</p>
                </article>
            </main>
            <aside>
                <div class="sidebar">Related articles</div>
            </aside>
            <footer>
                <p>Copyright information</p>
            </footer>
        </body>
        </html>
        """
        
        result = parser.parse_html(real_html, source_url="https://realarticle.com")
        
        assert result.title == "Real Article Title"
        assert "first paragraph of real content" in result.content
        assert "detailed information about the topic" in result.content
        
        # Should exclude navigation and footer
        assert "Navigation links" not in result.content
        assert "Copyright information" not in result.content
        
        # Should include metadata
        assert result.metadata["author"] == "John Doe"
        assert result.metadata["description"] == "This is a real article description"
