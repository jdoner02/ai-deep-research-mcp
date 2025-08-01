"""
AI Deep Research MCP - Infrastructure Layer

This layer contains implementations of external services, repositories,
and other infrastructure concerns. It adapts external systems to work
with our domain interfaces.
"""

from .repositories import (
    InMemoryResearchQueryRepository,
    InMemoryResearchResultRepository,
)
from .scholarly_sources import (
    ArxivSearcher,
    GoogleScholarSearcher,
    PaperProcessor,
    ScholarlyPaper,
    SemanticScholarSearcher,
    UnifiedScholarlySearcher,
)

__all__ = [
    # Repositories
    "InMemoryResearchQueryRepository",
    "InMemoryResearchResultRepository",
    # Scholarly Sources
    "ArxivSearcher",
    "SemanticScholarSearcher",
    "GoogleScholarSearcher",
    "UnifiedScholarlySearcher",
    "PaperProcessor",
    "ScholarlyPaper",
]
