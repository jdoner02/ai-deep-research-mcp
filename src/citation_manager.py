#!/usr/bin/env python3
"""
AI Deep Research MCP - CitationManager Component

Handles source tracking, citation formatting, and reference management
for research answers. Provides multiple citation styles and bibliography
generation capabilities.

REFACTOR PHASE: Improved code organization with extracted formatters
"""

import json
import uuid
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional, Set, Protocol
from urllib.parse import urlparse
import logging
from abc import ABC, abstractmethod

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CitationStyle(Enum):
    """Enumeration for different citation styles"""
    APA = "apa"
    MLA = "mla"
    CHICAGO = "chicago"
    IEEE = "ieee"
    WEB_SIMPLE = "web_simple"


class CiteError(Exception):
    """Custom exception for citation-related errors"""
    pass


class CitationFormatter(ABC):
    """Abstract base class for citation formatters"""
    
    @abstractmethod
    def format(self, source: 'SourceInfo') -> str:
        """Format a source into a citation string"""
        pass


class APAFormatter(CitationFormatter):
    """APA citation style formatter"""
    
    def format(self, source: 'SourceInfo') -> str:
        """Format citation in APA style"""
        citation = ""
        
        if source.author:
            citation += f"{source.author} "
        
        if source.publication_date:
            year = source.publication_date.split("-")[0]  # Extract year
            citation += f"({year}). "
        
        citation += f"{source.title}. "
        
        if source.publisher:
            citation += f"{source.publisher}. "
        
        citation += f"Retrieved from {source.url}"
        
        return citation


class MLAFormatter(CitationFormatter):
    """MLA citation style formatter"""
    
    def format(self, source: 'SourceInfo') -> str:
        """Format citation in MLA style"""
        citation = ""
        
        if source.author:
            citation += f"{source.author}. "
        
        citation += f'"{source.title}." '
        
        citation += f"{source.domain}, "
        
        if source.publication_date:
            citation += f"{source.publication_date}, "
        
        citation += f"{source.url}."
        
        return citation


class ChicagoFormatter(CitationFormatter):
    """Chicago citation style formatter"""
    
    def format(self, source: 'SourceInfo') -> str:
        """Format citation in Chicago style"""
        citation = ""
        
        if source.author:
            citation += f"{source.author}. "
        
        citation += f'"{source.title}." '
        
        if source.publisher:
            citation += f"{source.publisher}. "
        
        if source.publication_date:
            citation += f"{source.publication_date}. "
        
        citation += f"{source.url}."
        
        return citation


class IEEEFormatter(CitationFormatter):
    """IEEE citation style formatter"""
    
    def format(self, source: 'SourceInfo') -> str:
        """Format citation in IEEE style"""
        citation = ""
        
        if source.author:
            citation += f"{source.author}, "
        
        citation += f'"{source.title}," '
        
        citation += f"{source.domain}, "
        
        if source.publication_date:
            citation += f"{source.publication_date}, "
        
        citation += f"[Online]. Available: {source.url}"
        
        return citation


class WebSimpleFormatter(CitationFormatter):
    """Simple web citation style formatter"""
    
    def format(self, source: 'SourceInfo') -> str:
        """Format citation in simple web style"""
        citation = f"{source.title} - {source.domain}"
        
        if source.author:
            citation += f" (by {source.author})"
        
        citation += f" - {source.url}"
        
        return citation


class URLNormalizer:
    """Helper class for URL normalization and deduplication"""
    
    @staticmethod
    def normalize(url: str) -> str:
        """
        Normalize URL for deduplication by removing query parameters
        and fragments while preserving essential path information.
        """
        try:
            parsed = urlparse(url)
            return f"{parsed.scheme}://{parsed.netloc}{parsed.path}"
        except Exception:
            # Return original URL if parsing fails
            return url
    
    @staticmethod
    def are_similar(url1: str, url2: str, threshold: float = 0.8) -> bool:
        """
        Check if two URLs are similar enough to be considered duplicates.
        Could be enhanced with more sophisticated similarity measures.
        """
        norm1 = URLNormalizer.normalize(url1)
        norm2 = URLNormalizer.normalize(url2)
        return norm1 == norm2


class CitationExtractor:
    """Helper class for extracting citations from text"""
    
    CITATION_PATTERNS = [
        r'\[(\d+)\]',  # [1], [2], etc.
        r'\[(\w+)\]',  # [abc], [xyz], etc.
        r'\((\d+)\)',  # (1), (2), etc.
    ]
    
    @classmethod
    def extract_citation_ids(cls, text: str) -> List[str]:
        """
        Extract citation IDs from text containing citation markers.
        
        Args:
            text: Text containing citation markers
            
        Returns:
            List of unique citation IDs found in text
        """
        found_ids = set()
        
        for pattern in cls.CITATION_PATTERNS:
            matches = re.findall(pattern, text)
            found_ids.update(matches)
        
        return list(found_ids)
    
    @classmethod
    def validate_citations(cls, citation_ids: List[str], valid_ids: Set[str]) -> List[str]:
        """Filter citation IDs to only include valid ones"""
        return [cid for cid in citation_ids if cid in valid_ids]


@dataclass
class SourceInfo:
    """Information about a source document"""
    url: str
    title: str
    domain: str
    author: Optional[str] = None
    publication_date: Optional[str] = None
    publisher: Optional[str] = None
    access_date: Optional[str] = None
    page_count: Optional[int] = None
    doi: Optional[str] = None
    
    def __post_init__(self):
        """Validate required fields"""
        if not self.url or not self.url.strip():
            raise CiteError("Source URL cannot be empty")
        if not self.title or not self.title.strip():
            raise CiteError("Source title cannot be empty")
        if not self.domain or not self.domain.strip():
            raise CiteError("Source domain cannot be empty")


@dataclass
class Citation:
    """Represents a citation with source reference and context"""
    source: SourceInfo
    citation_id: str
    text_snippet: Optional[str] = None
    page_number: Optional[int] = None
    quote_start: Optional[int] = None
    quote_end: Optional[int] = None
    context: Optional[str] = None


class CitationManager:
    """
    Manages citations and source references for research documents.
    
    This class provides comprehensive citation management including:
    - Source tracking and deduplication
    - Multiple citation style formatting (APA, MLA, Chicago, IEEE, Web)
    - Bibliography generation
    - Inline citation insertion
    - Citation extraction from text
    - Import/export functionality
    
    REFACTOR: Improved with extracted helper classes and formatters
    """
    
    def __init__(self):
        """Initialize the citation manager with formatter registry"""
        self._sources: Dict[str, SourceInfo] = {}
        self._citations: List[Citation] = []
        self._url_to_id: Dict[str, str] = {}  # For deduplication
        
        # Initialize formatters
        self._formatters = {
            CitationStyle.APA: APAFormatter(),
            CitationStyle.MLA: MLAFormatter(),
            CitationStyle.CHICAGO: ChicagoFormatter(),
            CitationStyle.IEEE: IEEEFormatter(),
            CitationStyle.WEB_SIMPLE: WebSimpleFormatter()
        }
        
        # Initialize helper components
        self._url_normalizer = URLNormalizer()
        self._citation_extractor = CitationExtractor()
    
    def add_source(self, source: SourceInfo, deduplicate: bool = True) -> str:
        """
        Add a source and return its citation ID.
        
        Args:
            source: SourceInfo object containing source details
            deduplicate: Whether to check for existing similar sources
            
        Returns:
            Citation ID string
            
        Raises:
            CiteError: If source validation fails
        """
        # Validate source
        if not isinstance(source, SourceInfo):
            raise CiteError("Source must be a SourceInfo object")
        
        # Check for duplicates if requested
        if deduplicate:
            normalized_url = self._url_normalizer.normalize(source.url)
            if normalized_url in self._url_to_id:
                return self._url_to_id[normalized_url]
        
        # Generate unique citation ID
        citation_id = str(len(self._sources) + 1)
        
        # Store source
        self._sources[citation_id] = source
        if deduplicate:
            self._url_to_id[self._url_normalizer.normalize(source.url)] = citation_id
        
        logger.info(f"Added source: {source.title} (ID: {citation_id})")
        return citation_id
    
    def get_source(self, citation_id: str) -> Optional[SourceInfo]:
        """Get source by citation ID"""
        return self._sources.get(citation_id)
    
    def get_all_sources(self) -> List[SourceInfo]:
        """Get all sources"""
        return list(self._sources.values())
    
    def create_citation(
        self,
        source_id: str,
        text_snippet: Optional[str] = None,
        page_number: Optional[int] = None,
        context: Optional[str] = None
    ) -> Citation:
        """
        Create a citation object for a source.
        
        Args:
            source_id: ID of the source
            text_snippet: Optional quoted text
            page_number: Optional page number
            context: Optional surrounding context
            
        Returns:
            Citation object
            
        Raises:
            CiteError: If source ID not found
        """
        source = self.get_source(source_id)
        if not source:
            raise CiteError(f"Source not found: {source_id}")
        
        citation = Citation(
            source=source,
            citation_id=source_id,
            text_snippet=text_snippet,
            page_number=page_number,
            context=context
        )
        
        self._citations.append(citation)
        return citation
    
    def format_citation(self, citation_id: str, style: CitationStyle = CitationStyle.APA) -> str:
        """
        Format a citation in the specified style using formatter pattern.
        
        Args:
            citation_id: ID of the citation to format
            style: Citation style to use
            
        Returns:
            Formatted citation string
        """
        source = self.get_source(citation_id)
        if not source:
            raise CiteError(f"Source not found: {citation_id}")
        
        formatter = self._formatters.get(style)
        if not formatter:
            raise CiteError(f"Unsupported citation style: {style}")
        
        return formatter.format(source)
    
    def generate_bibliography(self, style: CitationStyle = CitationStyle.APA) -> str:
        """
        Generate a complete bibliography for all sources.
        
        Args:
            style: Citation style to use
            
        Returns:
            Formatted bibliography string
        """
        if not self._sources:
            return "## References\n\nNo sources cited."
        
        bibliography = "## References\n\n"
        
        # Sort sources by ID for consistent ordering
        sorted_ids = sorted(self._sources.keys(), key=lambda x: int(x))
        
        for citation_id in sorted_ids:
            citation = self.format_citation(citation_id, style)
            bibliography += f"{citation}\n\n"
        
        return bibliography.strip()
    
    def insert_inline_citation(
        self,
        text: str,
        citation_id: str,
        position: str = "end"
    ) -> str:
        """
        Insert an inline citation into text.
        
        Args:
            text: Text to insert citation into
            citation_id: ID of citation to insert
            position: Where to insert ("end", "start", or specific position)
            
        Returns:
            Text with citation inserted
        """
        if citation_id not in self._sources:
            raise CiteError(f"Citation ID not found: {citation_id}")
        
        inline_ref = f"[{citation_id}]"
        
        if position == "end":
            return f"{text} {inline_ref}"
        elif position == "start":
            return f"{inline_ref} {text}"
        else:
            # Could implement more sophisticated insertion logic
            return f"{text} {inline_ref}"
    
    def extract_citations_from_text(self, text: str) -> List[str]:
        """
        Extract citation IDs from text containing citation markers.
        
        Args:
            text: Text containing citation markers like [1], [2], etc.
            
        Returns:
            List of citation IDs found in text
        """
        # Use the citation extractor helper
        found_ids = self._citation_extractor.extract_citation_ids(text)
        
        # Filter to only return valid citation IDs
        valid_ids = set(self._sources.keys())
        return self._citation_extractor.validate_citations(found_ids, valid_ids)
    
    def export_citations(self, format_type: str = "json") -> str:
        """
        Export citations to specified format.
        
        Args:
            format_type: Export format ("json", "bibtex", etc.)
            
        Returns:
            Serialized citation data
        """
        if format_type == "json":
            export_data = {
                "sources": []
            }
            
            for citation_id, source in self._sources.items():
                source_dict = {
                    "id": citation_id,
                    "url": source.url,
                    "title": source.title,
                    "domain": source.domain,
                    "author": source.author,
                    "publication_date": source.publication_date,
                    "publisher": source.publisher,
                    "access_date": source.access_date,
                    "page_count": source.page_count,
                    "doi": source.doi
                }
                export_data["sources"].append(source_dict)
            
            return json.dumps(export_data, indent=2)
        else:
            raise CiteError(f"Unsupported export format: {format_type}")
    
    def import_citations(self, data: str, format_type: str = "json"):
        """
        Import citations from serialized data.
        
        Args:
            data: Serialized citation data
            format_type: Data format ("json", "bibtex", etc.)
        """
        if format_type == "json":
            try:
                import_data = json.loads(data)
                
                for source_dict in import_data.get("sources", []):
                    source = SourceInfo(
                        url=source_dict["url"],
                        title=source_dict["title"],
                        domain=source_dict["domain"],
                        author=source_dict.get("author"),
                        publication_date=source_dict.get("publication_date"),
                        publisher=source_dict.get("publisher"),
                        access_date=source_dict.get("access_date"),
                        page_count=source_dict.get("page_count"),
                        doi=source_dict.get("doi")
                    )
                    
                    self.add_source(source, deduplicate=False)
                    
            except json.JSONDecodeError as e:
                raise CiteError(f"Invalid JSON data: {e}")
        else:
            raise CiteError(f"Unsupported import format: {format_type}")
    
    def format_academic_citation(self, paper_data: Dict, style: CitationStyle) -> str:
        """
        Format academic paper citation in specified style
        
        Args:
            paper_data: Dictionary containing paper metadata (from scholarly sources)
            style: Citation style to use
            
        Returns:
            Formatted citation string
        """
        try:
            if style == CitationStyle.APA:
                # APA format for academic papers
                citation = ""
                
                # Authors
                authors = paper_data.get('authors', [])
                if authors:
                    if len(authors) == 1:
                        citation += f"{authors[0]}. "
                    elif len(authors) <= 6:
                        if len(authors) == 2:
                            citation += f"{authors[0]} & {authors[1]}. "
                        else:
                            citation += ", ".join(authors[:-1]) + f", & {authors[-1]}. "
                    else:
                        citation += f"{authors[0]} et al. "
                
                # Year
                year = paper_data.get('year') or paper_data.get('published', '')[:4] if paper_data.get('published') else None
                if year:
                    citation += f"({year}). "
                
                # Title
                title = paper_data.get('title', 'Untitled')
                citation += f"{title}. "
                
                # Venue/Journal
                venue = paper_data.get('venue') or paper_data.get('source', '')
                if venue:
                    citation += f"*{venue}*. "
                
                # arXiv identifier or DOI
                if paper_data.get('source_type') == 'arxiv':
                    arxiv_id = paper_data.get('source_url', '').split('/')[-1] if paper_data.get('source_url') else 'unknown'
                    citation += f"arXiv preprint arXiv:{arxiv_id}."
                
                return citation.strip()
                
            elif style == CitationStyle.MLA:
                # MLA format for academic papers
                citation = ""
                
                # Authors
                authors = paper_data.get('authors', [])
                if authors:
                    citation += f"{authors[0]}. "
                    if len(authors) > 1:
                        citation = citation.replace(f"{authors[0]}.", f"{authors[0]}, et al.")
                
                # Title
                title = paper_data.get('title', 'Untitled')
                citation += f'"{title}." '
                
                # Venue
                venue = paper_data.get('venue') or paper_data.get('source', '')
                if venue:
                    citation += f"{venue}, "
                
                # Year
                year = paper_data.get('year') or paper_data.get('published', '')[:4] if paper_data.get('published') else None
                if year:
                    citation += f"{year}, "
                
                # URL
                source_url = paper_data.get('source_url') or paper_data.get('pdf_url')
                if source_url:
                    citation += f"{source_url}."
                
                return citation.strip()
                
            elif style == CitationStyle.CHICAGO:
                # Chicago format for academic papers
                citation = ""
                
                # Authors
                authors = paper_data.get('authors', [])
                if authors:
                    citation += f"{authors[0]}. "
                    if len(authors) > 1:
                        citation = citation.replace(f"{authors[0]}.", f"{authors[0]} et al.")
                
                # Title
                title = paper_data.get('title', 'Untitled')
                citation += f'"{title}." '
                
                # Venue
                venue = paper_data.get('venue') or paper_data.get('source', '')
                if venue:
                    citation += f"{venue} "
                
                # Year
                year = paper_data.get('year') or paper_data.get('published', '')[:4] if paper_data.get('published') else None
                if year:
                    citation += f"({year}). "
                
                # URL
                source_url = paper_data.get('source_url') or paper_data.get('pdf_url')
                if source_url:
                    citation += f"Accessed from {source_url}."
                
                return citation.strip()
            
            else:
                # Fallback to web simple format
                title = paper_data.get('title', 'Untitled')
                authors = paper_data.get('authors', [])
                author_str = f" by {authors[0]}" if authors else ""
                venue = paper_data.get('venue') or paper_data.get('source', 'Academic Source')
                return f"{title} - {venue}{author_str}"
                
        except Exception as e:
            logger.error(f"Academic citation formatting failed: {e}")
            return f"Error formatting citation: {paper_data.get('title', 'Unknown')}"
