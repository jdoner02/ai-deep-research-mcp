"""
🎓 STUDENT GUIDE: Scholarly Research Use Cases

=== WHAT ARE USE CASES? ===
Think of use cases like recipes in a cookbook!

Just like a recipe tells you step-by-step how to make cookies:
1. Gather ingredients (get the research query)
2. Mix them together (search multiple academic sources)
3. Bake in the oven (process and analyze the results)
4. Serve delicious cookies (return formatted research results)

Our use cases tell the computer step-by-step how to conduct academic research!

🤔 WHY SCHOLARLY SOURCES?
Regular Google searches find lots of information, but scholarly sources are special:
- Written by experts and scientists
- Peer-reviewed (other experts check the work)
- Include citations so you can verify information
- More reliable for school projects and serious research

🎯 LEARNING TIP: This file shows how our AI system integrates with real academic databases like arXiv (where scientists publish research papers) and Semantic Scholar (an AI-powered academic search engine).

Enhanced application layer use cases that integrate with scholarly sources
infrastructure to provide real academic research capabilities.
"""

import asyncio
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime
import uuid
import logging

from ..domain.entities import (
    ResearchQuery,
    ResearchResult,
    ResearchSource,
    QueryId,
    ResearchQueryType,
    ResearchStatus,
    SourceType,
    ResearchQueryRepository,
    ResearchResultRepository,
    InvalidQueryException,
    DomainException,
    QueryNotFoundError,
)

from ..infrastructure.scholarly_sources import (
    UnifiedScholarlySearcher,
)


# Enhanced DTOs for Scholarly Research


@dataclass
class ScholarlySearchRequest:
    """Request for scholarly research with specific academic parameters."""

    query_text: str
    sources: List[str] = field(default_factory=lambda: ["arxiv", "semantic_scholar"])
    max_results: int = 10
    include_abstracts: bool = True
    min_year: Optional[int] = None
    max_year: Optional[int] = None
    fields_of_study: List[str] = field(default_factory=list)


@dataclass
class ScholarlySearchResponse:
    """Response containing scholarly research results."""

    query_id: str
    papers: List[Dict[str, Any]]
    total_found: int
    sources_used: List[str]
    search_time_ms: int


@dataclass
class ScholarlyPaperResult:
    """Individual scholarly paper result for web display."""

    title: str
    authors: List[str]
    abstract: str
    year: Optional[int]
    citation_count: int
    pdf_url: Optional[str]
    source_url: str
    source_type: str
    relevance_score: float
    venue: Optional[str] = None
    doi: Optional[str] = None


class ScholarlyResearchUseCase:
    """
    Use case for executing scholarly research queries using academic databases.

    This use case orchestrates scholarly research by:
    1. Validating research parameters
    2. Coordinating searches across academic databases
    3. Processing and ranking results
    4. Formatting results for presentation
    """

    def __init__(
        self,
        query_repository: ResearchQueryRepository,
        result_repository: ResearchResultRepository,
        scholarly_searcher: Optional[UnifiedScholarlySearcher] = None,
    ):
        self.query_repository = query_repository
        self.result_repository = result_repository
        self.scholarly_searcher = scholarly_searcher or UnifiedScholarlySearcher()
        self.logger = logging.getLogger(__name__)

    async def execute_scholarly_search(
        self, request: ScholarlySearchRequest
    ) -> ScholarlySearchResponse:
        """
        Execute a scholarly research search across academic databases.

        Args:
            request: Scholarly search parameters

        Returns:
            ScholarlySearchResponse with formatted results
        """
        start_time = datetime.now()

        try:
            # Validate request
            if not request.query_text.strip():
                raise InvalidQueryException("Query text cannot be empty")

            if request.max_results < 1 or request.max_results > 100:
                raise InvalidQueryException("Max results must be between 1 and 100")

            # Execute search using the actual UnifiedScholarlySearcher API
            self.logger.info(f"Executing scholarly search: '{request.query_text}'")

            papers_data = self.scholarly_searcher.search(
                query=request.query_text,
                max_results=request.max_results,
                sources=request.sources,
                results_per_source=max(request.max_results // len(request.sources), 1),
            )

            # Process and format results
            formatted_papers = [
                self._format_paper_for_response(paper_data)
                for paper_data in papers_data
            ]

            # Calculate search time
            search_time = int((datetime.now() - start_time).total_seconds() * 1000)

            # Generate response
            query_id = str(uuid.uuid4())
            response = ScholarlySearchResponse(
                query_id=query_id,
                papers=formatted_papers,
                total_found=len(papers_data),
                sources_used=request.sources,
                search_time_ms=search_time,
            )

            self.logger.info(
                f"Scholarly search completed: {len(formatted_papers)} results in {search_time}ms"
            )

            return response

        except Exception as e:
            self.logger.error(f"Scholarly search failed: {str(e)}")
            raise DomainException(f"Scholarly search failed: {str(e)}")

    def export_citations(
        self, papers: List[Dict[str, Any]], format_type: str = "bibtex"
    ) -> str:
        """
        🎓 RESEARCH UTILITY: Export citations in various academic formats

        This is what researchers need most! Every paper needs to be exported
        to reference managers like Zotero, Mendeley, or EndNote.

        Args:
            papers: List of paper dictionaries from search results
            format_type: 'bibtex', 'ris', 'endnote', or 'apa'

        Returns:
            Formatted citation string ready for import into reference managers
        """
        if format_type.lower() == "bibtex":
            return self._export_bibtex(papers)
        elif format_type.lower() == "ris":
            return self._export_ris(papers)
        elif format_type.lower() == "endnote":
            return self._export_endnote(papers)
        elif format_type.lower() == "apa":
            return self._export_apa(papers)
        else:
            raise InvalidQueryException(f"Unsupported citation format: {format_type}")

    def _export_bibtex(self, papers: List[Dict[str, Any]]) -> str:
        """Export papers in BibTeX format - most widely used academic format."""
        bibtex_entries = []

        for i, paper in enumerate(papers):
            # Generate unique citation key
            first_author = (
                paper.get("authors", ["Unknown"])[0].split()[-1]
                if paper.get("authors")
                else "Unknown"
            )
            year = paper.get("year", datetime.now().year)
            title_words = paper.get("title", "").split()[:2]
            key = f"{first_author}{year}{''.join(title_words)}"

            # Clean key of special characters
            key = "".join(c for c in key if c.isalnum())

            entry = f"@article{{{key},\n"
            entry += f"  title = {{{paper.get('title', 'Unknown Title')}}},\n"

            if paper.get("authors"):
                authors_str = " and ".join(paper["authors"])
                entry += f"  author = {{{authors_str}}},\n"

            if paper.get("year"):
                entry += f"  year = {{{paper['year']}}},\n"

            if paper.get("venue"):
                entry += f"  journal = {{{paper['venue']}}},\n"

            if paper.get("doi"):
                entry += f"  doi = {{{paper['doi']}}},\n"

            if paper.get("source_url"):
                entry += f"  url = {{{paper['source_url']}}},\n"

            entry += f"  abstract = {{{paper.get('abstract', '')}}}\n"
            entry += "}\n\n"

            bibtex_entries.append(entry)

        return "".join(bibtex_entries)

    def _export_ris(self, papers: List[Dict[str, Any]]) -> str:
        """Export papers in RIS format - used by EndNote and other reference managers."""
        ris_entries = []

        for paper in papers:
            entry = "TY  - JOUR\n"  # Journal article type
            entry += f"TI  - {paper.get('title', 'Unknown Title')}\n"

            for author in paper.get("authors", []):
                entry += f"AU  - {author}\n"

            if paper.get("year"):
                entry += f"PY  - {paper['year']}\n"

            if paper.get("venue"):
                entry += f"JO  - {paper['venue']}\n"

            if paper.get("doi"):
                entry += f"DO  - {paper['doi']}\n"

            if paper.get("source_url"):
                entry += f"UR  - {paper['source_url']}\n"

            if paper.get("abstract"):
                entry += f"AB  - {paper['abstract']}\n"

            entry += "ER  - \n\n"
            ris_entries.append(entry)

        return "".join(ris_entries)

    def _export_endnote(self, papers: List[Dict[str, Any]]) -> str:
        """Export papers in EndNote tagged format."""
        endnote_entries = []

        for paper in papers:
            entry = "%0 Journal Article\n"
            entry += f"%T {paper.get('title', 'Unknown Title')}\n"

            for author in paper.get("authors", []):
                entry += f"%A {author}\n"

            if paper.get("year"):
                entry += f"%D {paper['year']}\n"

            if paper.get("venue"):
                entry += f"%J {paper['venue']}\n"

            if paper.get("doi"):
                entry += f"%R {paper['doi']}\n"

            if paper.get("source_url"):
                entry += f"%U {paper['source_url']}\n"

            if paper.get("abstract"):
                entry += f"%X {paper['abstract']}\n"

            entry += "\n"
            endnote_entries.append(entry)

        return "".join(endnote_entries)

    def _export_apa(self, papers: List[Dict[str, Any]]) -> str:
        """Export papers in APA citation format."""
        apa_citations = []

        for paper in papers:
            authors = paper.get("authors", ["Unknown Author"])

            # Format authors for APA
            if len(authors) == 1:
                author_str = authors[0]
            elif len(authors) == 2:
                author_str = f"{authors[0]} & {authors[1]}"
            else:
                author_str = f"{', '.join(authors[:-1])}, & {authors[-1]}"

            year = paper.get("year", "n.d.")
            title = paper.get("title", "Unknown title")
            venue = paper.get("venue", "Unknown venue")

            citation = f"{author_str} ({year}). {title}. {venue}."

            if paper.get("doi"):
                citation += f" https://doi.org/{paper['doi']}"
            elif paper.get("source_url"):
                citation += f" Retrieved from {paper['source_url']}"

            apa_citations.append(citation)

        return "\n\n".join(apa_citations)

    def _format_paper_for_response(self, paper_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format a paper dictionary for API response."""
        abstract = paper_data.get("abstract", "")
        return {
            "title": paper_data.get("title", ""),
            "authors": paper_data.get("authors", []),
            "abstract": abstract[:500] + "..." if len(abstract) > 500 else abstract,
            "full_abstract": abstract,
            "year": paper_data.get("year"),
            "citation_count": paper_data.get("citation_count", 0),
            "pdf_url": paper_data.get("pdf_url"),
            "source_url": paper_data.get("url", ""),
            "source_type": paper_data.get("source", ""),
            "relevance_score": paper_data.get("relevance_score", 0.5),
            "venue": paper_data.get("venue"),
            "doi": paper_data.get("doi"),
            "formatted_citation": self._format_citation(paper_data),
            "display_class": self._get_relevance_class(
                paper_data.get("relevance_score", 0.5)
            ),
        }

    def _format_citation(self, paper_data: Dict[str, Any]) -> str:
        """Format paper as academic citation."""
        authors = paper_data.get("authors", [])
        if not authors:
            authors_str = "Unknown Authors"
        else:
            authors_str = ", ".join(authors[:3])  # First 3 authors
            if len(authors) > 3:
                authors_str += " et al."

        year = paper_data.get("year")
        year_str = f" ({year})" if year else ""
        venue = paper_data.get("venue")
        venue_str = f" {venue}." if venue else ""
        title = paper_data.get("title", "Untitled")

        return f"{authors_str}{year_str}. {title}.{venue_str}"

    def _get_relevance_class(self, score: float) -> str:
        """Get CSS class based on relevance score."""
        if score >= 0.8:
            return "high-relevance"
        elif score >= 0.6:
            return "medium-relevance"
        else:
            return "low-relevance"


class EnhancedResearchOrchestrationService:
    """
    Enhanced orchestration service that integrates scholarly sources
    with the existing research workflow.
    """

    def __init__(
        self,
        query_repository: ResearchQueryRepository,
        result_repository: ResearchResultRepository,
        scholarly_use_case: Optional[ScholarlyResearchUseCase] = None,
    ):
        self.query_repository = query_repository
        self.result_repository = result_repository
        self.scholarly_use_case = scholarly_use_case or ScholarlyResearchUseCase(
            query_repository, result_repository
        )
        self.logger = logging.getLogger(__name__)

    async def execute_enhanced_research(
        self, query_id: str, include_scholarly: bool = True
    ) -> ResearchResult:
        """
        Execute research with optional scholarly source integration.

        Args:
            query_id: ID of the research query
            include_scholarly: Whether to include scholarly sources

        Returns:
            ResearchResult with enhanced data
        """
        try:
            # Get the query
            query = self.query_repository.find_by_id(QueryId(query_id))
            if not query:
                raise QueryNotFoundError(f"Query {query_id} not found")

            # Create result structure
            result = ResearchResult(
                query=query,
                status=ResearchStatus.IN_PROGRESS,
                created_at=datetime.now(),
            )

            # If scholarly sources requested and query includes academic sources
            if include_scholarly and query.include_academic_sources:
                self.logger.info(f"Including scholarly sources for query: {query.text}")

                # Execute scholarly search
                scholarly_request = ScholarlySearchRequest(
                    query_text=query.text,
                    max_results=query.max_sources,
                    include_abstracts=True,
                )

                scholarly_response = (
                    await self.scholarly_use_case.execute_scholarly_search(
                        scholarly_request
                    )
                )

                # Add scholarly results to research result
                for paper_data in scholarly_response.papers:
                    # Map source types correctly - use existing SourceType enum values
                    source_type_map = {
                        "arxiv": SourceType.ARXIV,
                        "semantic_scholar": SourceType.SEMANTIC_SCHOLAR,
                        "google_scholar": SourceType.GOOGLE_SCHOLAR,
                    }

                    source_type = source_type_map.get(
                        paper_data.get("source_type", "").lower(),
                        SourceType.CUSTOM,  # Default for academic sources not specifically mapped
                    )

                    source = ResearchSource(
                        title=paper_data["title"],
                        url=paper_data["source_url"],
                        source_type=source_type,
                        content=paper_data["full_abstract"],
                        relevance_score=paper_data["relevance_score"],
                        metadata={
                            "authors": paper_data["authors"],
                            "year": paper_data["year"],
                            "citation_count": paper_data["citation_count"],
                            "venue": paper_data["venue"],
                            "pdf_url": paper_data["pdf_url"],
                            "doi": paper_data["doi"],
                            "formatted_citation": paper_data["formatted_citation"],
                        },
                    )
                    result.add_source(source)

            # Mark as completed
            result.status = ResearchStatus.COMPLETED
            result.completed_at = datetime.now()

            # Save result
            self.result_repository.save(result)

            self.logger.info(
                f"Enhanced research completed for query {query_id}: {len(result.sources)} sources"
            )

            return result

        except Exception as e:
            self.logger.error(
                f"Enhanced research failed for query {query_id}: {str(e)}"
            )
            raise DomainException(f"Research execution failed: {str(e)}")


# Factory functions


def create_scholarly_research_use_case(
    query_repository: ResearchQueryRepository,
    result_repository: ResearchResultRepository,
) -> ScholarlyResearchUseCase:
    """Factory to create scholarly research use case."""
    return ScholarlyResearchUseCase(query_repository, result_repository)


def create_enhanced_orchestration_service(
    query_repository: ResearchQueryRepository,
    result_repository: ResearchResultRepository,
) -> EnhancedResearchOrchestrationService:
    """Factory to create enhanced orchestration service."""
    return EnhancedResearchOrchestrationService(query_repository, result_repository)
