"""
AI Deep Research MCP - Clean Architecture Implementation

A professional AI-powered research platform following Clean Architecture,
Domain-Driven Design, and modern software engineering best practices.

Architecture:
- Domain Layer: Core business logic and entities
- Application Layer: Use cases and application services
- Infrastructure Layer: External service implementations
- Presentation Layer: MCP server, CLI, and web interfaces

Key Features:
- Multi-source research aggregation
- AI-powered content analysis
- Modular and testable design
- Multiple presentation interfaces
- Professional software architecture
"""

# Core imports - individual modules can be imported as needed
from .domain.entities import ResearchQuery, ResearchResult, ResearchSource, QueryId
from .application.use_cases import (
    CreateResearchQueryUseCase,
    ExecuteResearchUseCase,
    ResearchOrchestrationService,
)
from .presentation.mcp_server import create_mcp_server
from .presentation.cli import ResearchCLI
from .presentation.web_interface import create_web_interface
from .__main__ import create_app, AIDeepResearchMCP

__version__ = "1.0.0"
__author__ = "AI Deep Research MCP Team"
__email__ = "contact@airesearch.dev"

__all__ = [
    # Main application
    "create_app",
    "AIDeepResearchMCP",
    # Presentation interfaces
    "create_mcp_server",
    "ResearchCLI",
    "create_web_interface",
    # Domain entities (for advanced usage)
    "ResearchQuery",
    "ResearchResult",
    "ResearchSource",
    "QueryId",
    # Use cases (for custom integrations)
    "CreateResearchQueryUseCase",
    "ExecuteResearchUseCase",
    "ResearchOrchestrationService",
]
