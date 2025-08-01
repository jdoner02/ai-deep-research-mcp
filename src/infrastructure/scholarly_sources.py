"""
🎓 STUDENT GUIDE: Scholarly Sources Infrastructure for AI Deep Research MCP

=== WHAT IS INFRASTRUCTURE? ===
Think of infrastructure like the plumbing in your house!

Just like how plumbing connects your faucets to the city water supply:
- Your faucet = Our AI research system
- Pipes = Network connections and APIs
- City water supply = Academic databases (arXiv, Google Scholar, etc.)
- Water pressure = How fast we can get data

🤔 WHAT ARE ACADEMIC DATABASES?
These are special websites where scientists and researchers share their discoveries:

📚 arXiv: Where physicists, computer scientists, and mathematicians publish research papers
🔬 Semantic Scholar: AI-powered database that understands connections between research
🎓 Google Scholar: Academic version of Google that focuses on scholarly articles

🎯 LEARNING TIP: This file shows how our system "talks" to these external databases
using APIs (Application Programming Interfaces) - like a universal translator!

External service integrations for academic databases: arXiv, Google Scholar, Semantic Scholar

This module provides infrastructure layer implementations for accessing external
academic databases following Domain-Driven Design principles.
"""

import requests
import time
import logging
from typing import List, Dict, Optional, Any
from dataclasses import dataclass
from datetime import datetime
import xml.etree.ElementTree as ET
from urllib.parse import quote_plus
import feedparser
import json

logger = logging.getLogger(__name__)


@dataclass
class ScholarlyPaper:
    """
    🎓 STUDENT EXPLANATION: Data class for scholarly paper information

    Think of this like a baseball card, but for research papers!

    Just like a baseball card has:
    - Player name, team, stats, picture

    A ScholarlyPaper has:
    - Title, authors, abstract (summary), PDF link

    🤔 WHY DO WE ORGANIZE DATA THIS WAY?
    - Makes it easy to pass paper information around our system
    - Ensures we always have the same fields for every paper
    - Prevents mistakes like forgetting important information

    💡 REAL-WORLD ANALOGY: It's like having a standard form that every
    research paper must fill out so we can organize them properly!
    """

    title: str
    authors: List[str]
    abstract: str
    pdf_url: Optional[str] = None
    source_url: Optional[str] = None
    published: Optional[str] = None
    citation_count: Optional[int] = None
    venue: Optional[str] = None
    year: Optional[int] = None
    source_type: str = "academic"


class ArxivSearcher:
    """
    🎓 STUDENT EXPLANATION: Search arXiv database for academic papers

    What is arXiv? It's like YouTube, but for science papers!

    🔬 COOL FACTS ABOUT ARXIV:
    - Started in 1991 (older than Google!)
    - Scientists upload their research before it's officially published
    - Over 2 million papers about physics, math, computer science
    - Completely free to access (unlike many academic journals)

    🤔 HOW DOES THIS CLASS WORK?
    Think of it like a librarian who specializes in science papers:
    1. You give them a topic to research
    2. They search through millions of papers
    3. They bring back the most relevant ones
    4. They organize the information in a useful way

    💡 API CONCEPT: We "talk" to arXiv using their API (like sending a text message
    but for computers). We send a search query, they send back XML data with results.
    """

    def __init__(self, base_url: str = "http://export.arxiv.org/api/query"):
        self.base_url = base_url
        self.session = requests.Session()

    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search arXiv for papers matching the query

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of paper dictionaries with metadata
        """
        try:
            # Clean and format query for arXiv - try multiple search strategies
            search_queries = [
                f'all:"{query}"',  # Exact phrase search
                f'all:{query.replace(" ", " AND ")}',  # AND search
                f'ti:"{query}" OR abs:"{query}"',  # Title or abstract search
                f'all:{query.replace(" ", "+")}',  # Simple plus search
            ]

            papers = []

            for search_query in search_queries:
                if papers:  # If we found results, stop trying other queries
                    break

                # Build arXiv API request
                params = {
                    "search_query": search_query,
                    "start": 0,
                    "max_results": max_results,
                    "sortBy": "relevance",
                    "sortOrder": "descending",
                }

                logger.info(
                    f"Searching arXiv for: '{query}' with query: '{search_query}'"
                )
                response = self.session.get(self.base_url, params=params, timeout=30)
                response.raise_for_status()

                # Parse the arXiv atom feed response
                feed = feedparser.parse(response.content)

                logger.info(
                    f"Found {len(feed.entries)} arXiv entries with query: {search_query}"
                )

                for entry in feed.entries:
                    # Extract authors
                    authors = []
                    if hasattr(entry, "authors"):
                        authors = [author.name for author in entry.authors]
                    elif hasattr(entry, "author"):
                        authors = [entry.author]

                    # Extract PDF URL
                    pdf_url = None
                    for link in entry.links:
                        if link.get("type") == "application/pdf":
                            pdf_url = link.href
                            break

                    # Extract publication date
                    published = None
                    if hasattr(entry, "published"):
                        try:
                            published = entry.published.split("T")[
                                0
                            ]  # Just the date part
                        except (AttributeError, IndexError):
                            published = entry.published

                    paper_data = {
                        "title": entry.title.replace("\n", " ").strip(),
                        "authors": authors,
                        "abstract": (
                            entry.summary.replace("\n", " ").strip()
                            if hasattr(entry, "summary")
                            else ""
                        ),
                        "pdf_url": pdf_url,
                        "source_url": entry.link,
                        "published": published,
                        "venue": "arXiv",
                        "source_type": "arxiv",
                        "citation_count": None,  # arXiv doesn't provide citation counts
                    }

                    papers.append(paper_data)

                if papers:
                    logger.info(
                        f"Successfully retrieved {len(papers)} papers from arXiv"
                    )
                    break
                else:
                    logger.warning(f"No results found with query: {search_query}")
                    time.sleep(1)  # Be polite to the API

            return papers[:max_results]

        except Exception as e:
            logger.error(f"Error searching arXiv: {e}")
            return []


class SemanticScholarSearcher:
    """Search Semantic Scholar API for academic papers"""

    def __init__(self, api_key: Optional[str] = None):
        self.base_url = "https://api.semanticscholar.org/graph/v1"
        self.session = requests.Session()

        # Add API key if provided
        if api_key:
            self.session.headers.update({"x-api-key": api_key})

        # Set reasonable rate limits
        self.last_request_time = 0
        self.min_interval = 1.0  # 1 second between requests for free tier

    def _rate_limit(self):
        """Enforce rate limiting"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()

    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search Semantic Scholar for papers matching the query

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of paper dictionaries with metadata
        """
        try:
            self._rate_limit()

            # Use Semantic Scholar's paper search endpoint
            url = f"{self.base_url}/paper/search"
            params = {
                "query": query,
                "limit": min(max_results, 100),  # API limit
                "fields": "paperId,title,abstract,authors,venue,year,citationCount,url,openAccessPdf",
            }

            logger.info(f"Searching Semantic Scholar for: '{query}'")
            response = self.session.get(url, params=params, timeout=30)
            response.raise_for_status()

            data = response.json()
            papers = []

            if "data" in data:
                logger.info(f"Found {len(data['data'])} Semantic Scholar papers")

                for paper in data["data"]:
                    # Extract authors
                    authors = []
                    if paper.get("authors"):
                        authors = [
                            author.get("name", "Unknown") for author in paper["authors"]
                        ]

                    # Extract PDF URL
                    pdf_url = None
                    if paper.get("openAccessPdf") and paper["openAccessPdf"].get("url"):
                        pdf_url = paper["openAccessPdf"]["url"]

                    paper_data = {
                        "title": paper.get("title", "Untitled"),
                        "authors": authors,
                        "abstract": paper.get("abstract", ""),
                        "pdf_url": pdf_url,
                        "source_url": paper.get("url"),
                        "published": str(paper.get("year", "")),
                        "venue": paper.get("venue", ""),
                        "citation_count": paper.get("citationCount"),
                        "source_type": "semantic_scholar",
                        "year": paper.get("year"),
                    }

                    papers.append(paper_data)

            logger.info(
                f"Successfully retrieved {len(papers)} papers from Semantic Scholar"
            )
            return papers[:max_results]

        except Exception as e:
            logger.error(f"Error searching Semantic Scholar: {e}")
            return []


class GoogleScholarSearcher:
    """Search Google Scholar for academic papers"""

    def __init__(self):
        self.session = requests.Session()
        # Add reasonable delays to be respectful
        self.min_interval = 2.0
        self.last_request_time = 0

    def _rate_limit(self):
        """Enforce rate limiting for web scraping"""
        elapsed = time.time() - self.last_request_time
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        self.last_request_time = time.time()

    def search(self, query: str, max_results: int = 10) -> List[Dict]:
        """
        Search Google Scholar for papers matching the query

        Note: This is a simplified implementation. In production,
        consider using the 'scholarly' library for more robust scraping.

        Args:
            query: Search query string
            max_results: Maximum number of results to return

        Returns:
            List of paper dictionaries with metadata
        """
        try:
            # This is a placeholder implementation
            # In a real system, you would either:
            # 1. Use the 'scholarly' Python library
            # 2. Implement proper web scraping with BeautifulSoup
            # 3. Use a paid Google Scholar API service

            logger.warning(
                "Google Scholar search is placeholder - implement with 'scholarly' library"
            )

            # Return mock data for now to maintain system functionality
            mock_papers = [
                {
                    "title": f'Mock Google Scholar Paper for "{query}"',
                    "authors": ["Mock Author"],
                    "abstract": f"This is a mock paper result for the query: {query}",
                    "pdf_url": None,
                    "source_url": "https://scholar.google.com",
                    "published": "2024",
                    "venue": "Mock Conference",
                    "citation_count": 0,
                    "source_type": "google_scholar",
                    "year": 2024,
                }
            ]

            return mock_papers[:max_results]

        except Exception as e:
            logger.error(f"Error searching Google Scholar: {e}")
            return []


class UnifiedScholarlySearcher:
    """Unified search across all scholarly sources"""

    def __init__(self, semantic_scholar_api_key: Optional[str] = None):
        self.arxiv_searcher = ArxivSearcher()
        self.semantic_scholar_searcher = SemanticScholarSearcher(
            api_key=semantic_scholar_api_key
        )
        self.google_scholar_searcher = GoogleScholarSearcher()

    def search(
        self,
        query: str,
        max_results: int = 20,
        sources: Optional[List[str]] = None,
        results_per_source: Optional[int] = None,
    ) -> List[Dict]:
        """
        Search across multiple scholarly sources

        Args:
            query: Search query string
            max_results: Total maximum number of results to return
            sources: List of sources to search ['arxiv', 'semantic_scholar', 'google_scholar']
            results_per_source: Maximum results per source (auto-calculated if None)

        Returns:
            List of paper dictionaries with metadata from all sources
        """
        if sources is None:
            sources = ["arxiv", "semantic_scholar"]  # Skip Google Scholar for now

        if results_per_source is None:
            results_per_source = max(1, max_results // len(sources))

        all_papers = []

        for source in sources:
            try:
                if source == "arxiv":
                    papers = self.arxiv_searcher.search(query, results_per_source)
                elif source == "semantic_scholar":
                    papers = self.semantic_scholar_searcher.search(
                        query, results_per_source
                    )
                elif source == "google_scholar":
                    papers = self.google_scholar_searcher.search(
                        query, results_per_source
                    )
                else:
                    logger.warning(f"Unknown source: {source}")
                    continue

                all_papers.extend(papers)
                logger.info(f"Retrieved {len(papers)} papers from {source}")

            except Exception as e:
                logger.error(f"Error searching {source}: {e}")
                continue

        # Remove duplicates based on title similarity
        unique_papers = self._deduplicate_papers(all_papers)

        # Sort by citation count (if available) and relevance
        sorted_papers = sorted(
            unique_papers,
            key=lambda p: (p.get("citation_count") or 0, p.get("title", "")),
            reverse=True,
        )

        logger.info(f"Unified search returned {len(sorted_papers)} unique papers")
        return sorted_papers[:max_results]

    def _deduplicate_papers(self, papers: List[Dict]) -> List[Dict]:
        """Remove duplicate papers based on title similarity"""
        unique_papers = []
        seen_titles = set()

        for paper in papers:
            title = paper.get("title", "").lower().strip()
            # Simple deduplication - could be enhanced with fuzzy matching
            title_key = "".join(title.split())[:100]  # First 100 chars, no spaces

            if title_key not in seen_titles:
                seen_titles.add(title_key)
                unique_papers.append(paper)

        return unique_papers


class PaperProcessor:
    """Download and process academic papers"""

    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "AI Deep Research MCP (Educational Use)"}
        )

    def download_pdf(self, pdf_url: str, max_size_mb: int = 50) -> Optional[bytes]:
        """
        Download PDF content from URL

        Args:
            pdf_url: URL of the PDF file
            max_size_mb: Maximum file size to download (in MB)

        Returns:
            PDF content as bytes, or None if download failed
        """
        try:
            logger.info(f"Downloading PDF from: {pdf_url}")

            # Stream download to check size
            response = self.session.get(pdf_url, stream=True, timeout=30)
            response.raise_for_status()

            # Check content length
            content_length = response.headers.get("content-length")
            if content_length:
                size_mb = int(content_length) / (1024 * 1024)
                if size_mb > max_size_mb:
                    logger.warning(f"PDF too large: {size_mb:.1f}MB > {max_size_mb}MB")
                    return None

            # Download content
            content = b""
            downloaded_mb = 0

            for chunk in response.iter_content(chunk_size=8192):
                content += chunk
                downloaded_mb = len(content) / (1024 * 1024)

                if downloaded_mb > max_size_mb:
                    logger.warning(
                        f"PDF too large during download: {downloaded_mb:.1f}MB"
                    )
                    return None

            logger.info(f"Successfully downloaded PDF: {downloaded_mb:.1f}MB")
            return content

        except Exception as e:
            logger.error(f"Error downloading PDF from {pdf_url}: {e}")
            return None

    def extract_text_from_pdf(self, pdf_content: bytes) -> Optional[str]:
        """
        Extract text from PDF content

        Args:
            pdf_content: PDF file content as bytes

        Returns:
            Extracted text, or None if extraction failed
        """
        try:
            # This would require PyPDF2 or similar library
            # Placeholder implementation
            logger.warning("PDF text extraction not implemented - requires PyPDF2")
            return None

        except Exception as e:
            logger.error(f"Error extracting text from PDF: {e}")
            return None
