"""
🎓 STUDENT GUIDE: Core Domain Entities for AI Deep Research MCP

=== WHAT ARE DOMAIN ENTITIES? ===
Think of domain entities like the main characters in a story about research!

Just like how a story about school would have Students, Teachers, and Classes as main characters,
our AI research system has ResearchQuery, ResearchResult, and ResearchSource as main characters.

These entities represent the fundamental concepts in our research domain.
They contain business logic (the rules about how things work) and maintain
consistency rules (making sure everything makes sense together).

🤔 WHY DO WE ORGANIZE CODE THIS WAY?
- It makes the code easier to understand (like organizing your school binder by subject)
- It prevents bugs by having clear rules about what each entity can and can't do
- It makes the system easier to change and improve over time
- It matches how we naturally think about the problem we're solving

🎯 LEARNING TIP: As you read this file, ask yourself:
"What real-world concept does this represent?" and "What rules would this need in real life?"
"""

from __future__ import annotations
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import List, Dict, Optional, Any, Protocol
from uuid import UUID, uuid4


class ResearchQueryType(Enum):
    """
    🎯 STUDENT EXPLANATION: Types of research queries the system can handle.

    Think of this like different "modes" for your research assistant:

    📚 ACADEMIC: For school projects, science reports, serious research
        Example: "Explain photosynthesis" or "History of World War II"

    🔧 TECHNICAL: For understanding how things work, programming, engineering
        Example: "How do computers process data?" or "How does a car engine work?"

    🌍 GENERAL: For everyday curiosity, broad topics, general knowledge
        Example: "What's the weather like?" or "Best pizza recipes"

    ⚖️ COMPARATIVE: For comparing different options or analyzing pros/cons
        Example: "iPhone vs Android" or "Solar energy vs wind energy"

    📈 TREND_ANALYSIS: For understanding how things change over time
        Example: "How has social media usage changed?" or "Climate change trends"

    💡 WHY DOES THIS MATTER?
    Different types of questions need different research strategies!
    Academic questions need scholarly sources, while general questions might use Wikipedia.
    """

    ACADEMIC = "academic"
    TECHNICAL = "technical"
    GENERAL = "general"
    COMPARATIVE = "comparative"
    TREND_ANALYSIS = "trend_analysis"


class SourceType(Enum):
    """
    📖 STUDENT EXPLANATION: Types of research sources our system can use.

    Think of these like different libraries or information sources:

    🔬 ARXIV: Where scientists share their latest research papers
        Example: New discoveries in physics, computer science, biology

    🎓 GOOGLE_SCHOLAR: Academic search engine for scholarly articles
        Example: University research, peer-reviewed studies

    🧠 SEMANTIC_SCHOLAR: AI-powered academic search with smart connections
        Example: Research papers with citation analysis and related work

    🌐 WEB: Regular internet websites and online content
        Example: News articles, blogs, company websites

    📚 WIKIPEDIA: The online encyclopedia everyone knows
        Example: General knowledge articles with good overviews

    📄 CUSTOM: Special sources we add for specific needs
        Example: Internal documents, specialized databases

    🤔 WHY SO MANY TYPES?
    Different sources are good for different things! Scientific papers are great for
    accuracy but hard to read. Wikipedia is easy to understand but not always complete.
    Our AI system knows which source to use for each type of question!
    """

    ARXIV = "arxiv"
    GOOGLE_SCHOLAR = "google_scholar"
    SEMANTIC_SCHOLAR = "semantic_scholar"
    WEB = "web"
    WIKIPEDIA = "wikipedia"
    CUSTOM = "custom"


class ResearchStatus(Enum):
    """Status of a research request."""

    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass(frozen=True)
class QueryId:
    """Value object representing a unique query identifier."""

    value: UUID = field(default_factory=uuid4)

    def __str__(self) -> str:
        return str(self.value)


@dataclass(frozen=True)
class ResearchQuery:
    """
    Domain entity representing a research query.

    This is the central entity that drives the research process.
    It contains all the information needed to conduct research
    and maintains business rules about valid queries.
    """

    id: QueryId
    text: str
    query_type: ResearchQueryType
    created_at: datetime
    requester_id: Optional[str] = None
    max_sources: int = 10
    include_web_search: bool = True
    include_academic_sources: bool = True
    language_preference: str = "en"

    def __post_init__(self):
        """Validate business rules."""
        if not self.text.strip():
            raise ValueError("Query text cannot be empty")

        if self.max_sources < 1 or self.max_sources > 100:
            raise ValueError("Max sources must be between 1 and 100")

        if len(self.text) > 1000:
            raise ValueError("Query text cannot exceed 1000 characters")

    def is_academic_focused(self) -> bool:
        """Check if this query should prioritize academic sources."""
        return self.query_type in [
            ResearchQueryType.ACADEMIC,
            ResearchQueryType.TECHNICAL,
        ]

    def requires_trend_analysis(self) -> bool:
        """Check if this query requires temporal analysis."""
        return self.query_type == ResearchQueryType.TREND_ANALYSIS


@dataclass
class ResearchSource:
    """
    Domain entity representing a source of research information.

    Sources can be papers, websites, or other information repositories.
    """

    id: UUID = field(default_factory=uuid4)
    url: str = ""
    title: str = ""
    authors: List[str] = field(default_factory=list)
    publication_date: Optional[datetime] = None
    source_type: SourceType = SourceType.WEB
    abstract: str = ""
    content: str = ""
    relevance_score: float = 0.0
    citation_count: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def __post_init__(self):
        """Validate business rules."""
        if self.relevance_score < 0.0 or self.relevance_score > 1.0:
            raise ValueError("Relevance score must be between 0.0 and 1.0")

        if self.citation_count < 0:
            raise ValueError("Citation count cannot be negative")

    def is_academic_source(self) -> bool:
        """Check if this is an academic source."""
        return self.source_type in [
            SourceType.ARXIV,
            SourceType.GOOGLE_SCHOLAR,
            SourceType.SEMANTIC_SCHOLAR,
        ]

    def has_sufficient_content(self) -> bool:
        """Check if source has enough content to be useful."""
        return len(self.content.strip()) >= 100 or len(self.abstract.strip()) >= 50

    def get_display_title(self) -> str:
        """Get a title suitable for display."""
        return self.title.strip() if self.title.strip() else f"Source from {self.url}"


@dataclass
class ResearchResult:
    """
    Domain entity representing the result of a research operation.

    This aggregates all sources found for a query along with
    synthesized insights and metadata about the research process.
    """

    query: ResearchQuery
    sources: List[ResearchSource] = field(default_factory=list)
    status: ResearchStatus = ResearchStatus.PENDING
    created_at: datetime = field(default_factory=datetime.now)
    completed_at: Optional[datetime] = None
    synthesis: str = ""
    key_findings: List[str] = field(default_factory=list)
    search_strategies_used: List[str] = field(default_factory=list)
    total_processing_time: float = 0.0
    error_message: Optional[str] = None

    def add_source(self, source: ResearchSource) -> None:
        """Add a source to the research results."""
        if len(self.sources) >= self.query.max_sources:
            raise ValueError(f"Cannot add more than {self.query.max_sources} sources")

        # Prevent duplicate sources
        if any(existing.url == source.url for existing in self.sources if source.url):
            return

        self.sources.append(source)

    def mark_completed(
        self, synthesis: str = "", key_findings: List[str] = None
    ) -> None:
        """Mark the research as completed."""
        self.status = ResearchStatus.COMPLETED
        self.completed_at = datetime.now()
        self.synthesis = synthesis
        self.key_findings = key_findings or []

    def mark_failed(self, error_message: str) -> None:
        """Mark the research as failed."""
        self.status = ResearchStatus.FAILED
        self.completed_at = datetime.now()
        self.error_message = error_message

    def get_academic_sources(self) -> List[ResearchSource]:
        """Get only academic sources from the results."""
        return [source for source in self.sources if source.is_academic_source()]

    def get_web_sources(self) -> List[ResearchSource]:
        """Get only web sources from the results."""
        return [
            source for source in self.sources if source.source_type == SourceType.WEB
        ]

    def get_average_relevance_score(self) -> float:
        """Calculate average relevance score across all sources."""
        if not self.sources:
            return 0.0
        return sum(source.relevance_score for source in self.sources) / len(
            self.sources
        )

    def is_complete(self) -> bool:
        """Check if research is complete."""
        return self.status == ResearchStatus.COMPLETED

    def has_sufficient_sources(self) -> bool:
        """Check if we have enough quality sources."""
        quality_sources = [s for s in self.sources if s.has_sufficient_content()]
        return len(quality_sources) >= min(3, self.query.max_sources // 2)


# Domain Services and Repositories (Interfaces)


class ResearchQueryRepository(Protocol):
    """Repository interface for research queries."""

    def save(self, query: ResearchQuery) -> None:
        """Save a research query."""
        ...

    def find_by_id(self, query_id: QueryId) -> Optional[ResearchQuery]:
        """Find a query by its ID."""
        ...

    def find_by_requester(self, requester_id: str) -> List[ResearchQuery]:
        """Find queries by requester."""
        ...


class ResearchResultRepository(Protocol):
    """Repository interface for research results."""

    def save(self, result: ResearchResult) -> None:
        """Save research results."""
        ...

    def find_by_query_id(self, query_id: QueryId) -> Optional[ResearchResult]:
        """Find results by query ID."""
        ...

    def find_completed_results(
        self, limit: int = 10, offset: int = 0
    ) -> List[ResearchResult]:
        """Find completed research results."""
        ...


class SourceAnalyzer(Protocol):
    """Service for analyzing source quality and relevance."""

    def calculate_relevance(
        self, source: ResearchSource, query: ResearchQuery
    ) -> float:
        """Calculate how relevant a source is to a query."""
        ...

    def extract_key_information(self, source: ResearchSource) -> Dict[str, Any]:
        """Extract key information from a source."""
        ...


class QueryClassifier(Protocol):
    """Service for classifying research queries."""

    def classify_query(self, query_text: str) -> ResearchQueryType:
        """Classify a query into its appropriate type."""
        ...

    def suggest_search_strategies(self, query: ResearchQuery) -> List[str]:
        """Suggest search strategies based on query type."""
        ...


# Domain Events


class DomainEvent:
    """Base class for all domain events."""

    def __init__(self):
        self.occurred_at = datetime.now()
        self.event_id = uuid4()


@dataclass(frozen=True)
class ResearchQueryCreated(DomainEvent):
    """Event fired when a new research query is created."""

    query: ResearchQuery

    def __post_init__(self):
        super().__init__()


@dataclass(frozen=True)
class ResearchCompleted(DomainEvent):
    """Event fired when research is completed."""

    result: ResearchResult

    def __post_init__(self):
        super().__init__()


@dataclass(frozen=True)
class SourceDiscovered(DomainEvent):
    """Event fired when a new source is discovered."""

    source: ResearchSource
    query_id: QueryId

    def __post_init__(self):
        super().__init__()


# Domain Exceptions


class DomainException(Exception):
    """Base exception for domain-related errors."""

    pass


class InvalidQueryException(DomainException):
    """Raised when a query violates business rules."""

    pass


class ResearchFailedException(DomainException):
    """Raised when research operation fails."""

    pass


class SourceValidationException(DomainException):
    """Raised when source data is invalid."""

    pass


class QueryNotFoundError(DomainException):
    """Raised when a query cannot be found."""

    pass
