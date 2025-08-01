"""
🎓 STUDENT GUIDE: Web Interface Components - Modern web interface for AI Deep Research MCP

=== WHAT IS THE PRESENTATION LAYER? ===
Think of the presentation layer like the front desk at a hotel!

Just like a hotel front desk:
- Greets guests and takes their requests (handles web requests)
- Translates requests to the right hotel departments (calls use cases)
- Makes sure guests get what they need in a nice format (returns formatted responses)
- Handles problems gracefully (error handling)

🌐 WEB INTERFACE CONCEPTS:
- **HTTP Requests**: Like sending letters to our system (GET, POST, etc.)
- **JSON Responses**: Like getting a well-organized letter back with your answer
- **API Endpoints**: Like different windows at the hotel front desk for different services
- **Error Handling**: Like a friendly front desk person helping when something goes wrong

🤔 WHY SEPARATE PRESENTATION FROM BUSINESS LOGIC?
- Web interface can change without affecting the core research logic
- We could add a mobile app, desktop app, or chatbot using the same core system
- Makes testing easier (test web stuff separately from research stuff)
- Different people can work on UI and business logic simultaneously

🎯 LEARNING TIP: This file shows how web applications organize the user-facing part
separate from the "business logic" (the actual AI research functionality).

Provides web-based interface components following modern patterns.
This would integrate with frameworks like FastAPI, Flask, or similar.

Enhanced with scholarly sources integration for academic research capabilities.
"""

import json
import logging
import uuid
from dataclasses import asdict
from datetime import datetime
from typing import Any, Dict, List, Optional

from ..application.scholarly_use_cases import (
    EnhancedResearchOrchestrationService,
    ScholarlyResearchUseCase,
    ScholarlySearchRequest,
)
from ..application.use_cases import (
    CreateResearchQueryRequest,
    CreateResearchQueryUseCase,
    ExecuteResearchRequest,
    ExecuteResearchUseCase,
    ResearchOrchestrationService,
)
from ..infrastructure.repositories import (
    InMemoryResearchQueryRepository,
    InMemoryResearchResultRepository,
)
from ..infrastructure.scholarly_sources import UnifiedScholarlySearcher


class WebInterfaceHandler:
    """
    🎓 STUDENT EXPLANATION: Web Interface Handler for AI Deep Research MCP.

    Think of this class like a really smart receptionist at a research library!

    📋 WHAT THIS CLASS DOES:
    1. **Receives requests** from web browsers (like students asking questions)
    2. **Understands the request** (figures out what kind of research they want)
    3. **Delegates to experts** (calls the right use cases to do the research)
    4. **Formats the response** (organizes the answer in a nice, readable way)
    5. **Handles problems** (gives helpful error messages if something goes wrong)

    🌐 WEB CONCEPTS IN ACTION:
    - **HTTP Methods**: GET (retrieve info), POST (submit new research)
    - **Request/Response Cycle**: Browser asks → Server processes → Browser gets answer
    - **JSON**: Standard format for sending data between web apps
    - **Error Codes**: Like postal codes but for web problems (404, 500, etc.)

    💡 DESIGN PATTERN: This follows the "Adapter Pattern" - it adapts our
    research system to work with web browsers, just like a power adapter
    lets you plug a US device into a European outlet!

    Provides HTTP endpoints and web interface logic.
    This is the web presentation layer adapter.
    """

    def __init__(self):
        """Initialize web interface with dependency injection."""
        # Infrastructure dependencies
        self.query_repository = InMemoryResearchQueryRepository()
        self.result_repository = InMemoryResearchResultRepository()

        # Application use cases
        self.create_query_use_case = CreateResearchQueryUseCase(
            query_repository=self.query_repository
        )
        self.execute_research_use_case = ExecuteResearchUseCase(
            query_repository=self.query_repository,
            result_repository=self.result_repository,
        )
        self.orchestration_service = ResearchOrchestrationService(
            create_query_use_case=self.create_query_use_case,
            execute_research_use_case=self.execute_research_use_case,
        )

        # Scholarly research capabilities
        self.scholarly_use_case = ScholarlyResearchUseCase(
            self.query_repository, self.result_repository
        )
        self.enhanced_orchestration = EnhancedResearchOrchestrationService(
            self.query_repository, self.result_repository, self.scholarly_use_case
        )

        self.logger = logging.getLogger(__name__)

    async def handle_research_request(
        self, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle web research request.

        Args:
            request_data: Web request data (JSON format)

        Returns:
            Web response data (JSON format)
        """
        try:
            query_text = request_data.get("query", "")
            sources = request_data.get("sources", [])
            max_results = request_data.get("max_results", 10)

            response = await self.orchestration_service.create_and_execute_research(
                query_text=query_text, sources=sources, max_results=max_results
            )

            # Format for web response
            return {
                "success": True,
                "data": {
                    "query_id": response.create_response.query_id,
                    "query_text": query_text,
                    "results_count": len(response.execute_response.results),
                    "results": [
                        {
                            "query": result.query.text,
                            "status": result.status.value,
                            "sources": [
                                {
                                    "title": source.title,
                                    "url": source.url,
                                    "source_type": source.source_type.value,
                                    "relevance_score": source.relevance_score,
                                }
                                for source in result.sources
                            ],
                            "synthesis": result.synthesis,
                            "created_at": result.created_at.isoformat(),
                        }
                        for result in response.execute_response.results
                    ],
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": {"message": str(e), "type": type(e).__name__},
            }

    async def handle_create_query_request(
        self, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle create query web request."""
        try:
            query_text = request_data.get("query", "")
            sources = request_data.get("sources", [])
            max_results = request_data.get("max_results", 10)

            request = CreateResearchQueryRequest(
                query_text=query_text, sources=sources, max_results=max_results
            )

            response = await self.create_query_use_case.execute(request)

            return {
                "success": True,
                "data": {
                    "query_id": response.query_id,
                    "message": "Query created successfully",
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": {"message": str(e), "type": type(e).__name__},
            }

    async def handle_execute_research_request(
        self, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle execute research web request."""
        try:
            query_id = request_data.get("query_id", "")

            request = ExecuteResearchRequest(query_id=query_id)
            response = await self.execute_research_use_case.execute(request)

            return {
                "success": True,
                "data": {
                    "query_id": query_id,
                    "results_count": len(response.results),
                    "results": [
                        {
                            "query": result.query.text,
                            "status": result.status.value,
                            "sources": [
                                {
                                    "title": source.title,
                                    "url": source.url,
                                    "source_type": source.source_type.value,
                                    "relevance_score": source.relevance_score,
                                }
                                for source in result.sources
                            ],
                            "synthesis": result.synthesis,
                            "created_at": result.created_at.isoformat(),
                        }
                        for result in response.results
                    ],
                },
            }

        except Exception as e:
            return {
                "success": False,
                "error": {"message": str(e), "type": type(e).__name__},
            }

    async def handle_scholarly_search_request(
        self, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle scholarly research search request."""
        try:
            query_text = request_data.get("query", "")
            sources = request_data.get("sources", ["arxiv", "semantic_scholar"])
            max_results = request_data.get("max_results", 10)
            include_abstracts = request_data.get("include_abstracts", True)
            min_year = request_data.get("min_year")
            max_year = request_data.get("max_year")
            fields_of_study = request_data.get("fields_of_study", [])

            request = ScholarlySearchRequest(
                query_text=query_text,
                sources=sources,
                max_results=max_results,
                include_abstracts=include_abstracts,
                min_year=min_year,
                max_year=max_year,
                fields_of_study=fields_of_study,
            )

            response = await self.scholarly_use_case.execute_scholarly_search(request)

            return {
                "success": True,
                "data": {
                    "query_id": response.query_id,
                    "papers": response.papers,
                    "total_found": response.total_found,
                    "sources_used": response.sources_used,
                    "search_time_ms": response.search_time_ms,
                    "message": f"Found {response.total_found} academic papers",
                },
            }

        except Exception as e:
            self.logger.error(f"Scholarly search failed: {str(e)}")
            return {
                "success": False,
                "error": {"message": str(e), "type": type(e).__name__},
            }

    async def handle_enhanced_research_request(
        self, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle enhanced research request with scholarly sources."""
        try:
            query_text = request_data.get("query", "")
            sources = request_data.get("sources", [])
            max_results = request_data.get("max_results", 10)
            include_scholarly = request_data.get("include_scholarly", True)

            # Create query first
            create_request = CreateResearchQueryRequest(
                query_text=query_text, sources=sources, max_results=max_results
            )
            create_response = await self.create_query_use_case.execute(create_request)

            # Execute enhanced research
            result = await self.enhanced_orchestration.execute_enhanced_research(
                create_response.query_id, include_scholarly=include_scholarly
            )

            # Format results for web display
            formatted_sources = []
            for source in result.sources:
                source_data = {
                    "title": source.title,
                    "url": source.url,
                    "source_type": source.source_type.value,
                    "relevance_score": source.relevance_score,
                    "content": (
                        source.content[:500] + "..."
                        if len(source.content) > 500
                        else source.content
                    ),
                    "full_content": source.content,
                }

                # Add scholarly metadata if available
                if source.metadata:
                    source_data.update(
                        {
                            "authors": source.metadata.get("authors", []),
                            "year": source.metadata.get("year"),
                            "citation_count": source.metadata.get("citation_count", 0),
                            "venue": source.metadata.get("venue"),
                            "pdf_url": source.metadata.get("pdf_url"),
                            "doi": source.metadata.get("doi"),
                            "formatted_citation": source.metadata.get(
                                "formatted_citation"
                            ),
                        }
                    )

                formatted_sources.append(source_data)

            return {
                "success": True,
                "data": {
                    "query_id": create_response.query_id,
                    "query": result.query.text,
                    "status": result.status.value,
                    "sources": formatted_sources,
                    "sources_count": len(formatted_sources),
                    "scholarly_sources_included": include_scholarly,
                    "completed_at": (
                        result.completed_at.isoformat() if result.completed_at else None
                    ),
                    "message": f"Research completed with {len(formatted_sources)} sources",
                },
            }

        except Exception as e:
            self.logger.error(f"Enhanced research failed: {str(e)}")
            return {
                "success": False,
                "error": {"message": str(e), "type": type(e).__name__},
            }

    async def handle_citation_export_request(
        self, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        🎯 RESEARCH UTILITY: Export citations in academic formats

        This is a game-changer for researchers! Export search results directly
        to reference managers like Zotero, Mendeley, EndNote.
        """
        try:
            papers = request_data.get("papers", [])
            format_type = request_data.get("format", "bibtex").lower()

            if not papers:
                return {
                    "success": False,
                    "error": {
                        "message": "No papers provided for export",
                        "type": "ValidationError",
                    },
                }

            # Use the scholarly research use case for citation export
            citations = self.scholarly_use_case.export_citations(papers, format_type)

            # Set appropriate content type for download
            content_types = {
                "bibtex": "application/x-bibtex",
                "ris": "application/x-research-info-systems",
                "endnote": "application/x-endnote-refer",
                "apa": "text/plain",
            }

            return {
                "success": True,
                "data": {
                    "citations": citations,
                    "format": format_type,
                    "content_type": content_types.get(format_type, "text/plain"),
                    "filename": f"research_citations.{format_type}",
                    "count": len(papers),
                },
                "message": f"Exported {len(papers)} citations in {format_type.upper()} format",
            }

        except Exception as e:
            self.logger.error(f"Citation export failed: {str(e)}")
            return {
                "success": False,
                "error": {"message": str(e), "type": type(e).__name__},
            }

    async def handle_advanced_search_request(
        self, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        🔍 RESEARCH UTILITY: Advanced search with academic filters

        Researchers need precise control over their searches - year ranges,
        specific venues, author searches, field-of-study filtering.
        """
        try:
            query_text = request_data.get("query", "")
            if not query_text.strip():
                return {
                    "success": False,
                    "error": {
                        "message": "Query text cannot be empty",
                        "type": "ValidationError",
                    },
                }

            # Create advanced scholarly search request
            scholarly_request = ScholarlySearchRequest(
                query_text=query_text,
                sources=request_data.get("sources", ["arxiv", "semantic_scholar"]),
                max_results=min(request_data.get("max_results", 20), 100),
                include_abstracts=request_data.get("include_abstracts", True),
                min_year=request_data.get("min_year"),
                max_year=request_data.get("max_year"),
                fields_of_study=request_data.get("fields_of_study", []),
            )

            # Execute advanced search
            response = await self.scholarly_use_case.execute_scholarly_search(
                scholarly_request
            )

            return {
                "success": True,
                "data": {
                    "query_id": response.query_id,
                    "papers": response.papers,
                    "total_found": response.total_found,
                    "sources_used": response.sources_used,
                    "search_time_ms": response.search_time_ms,
                    "filters_applied": {
                        "min_year": scholarly_request.min_year,
                        "max_year": scholarly_request.max_year,
                        "fields_of_study": scholarly_request.fields_of_study,
                        "sources": scholarly_request.sources,
                    },
                },
                "message": f"Found {response.total_found} papers in {response.search_time_ms}ms",
            }

        except Exception as e:
            self.logger.error(f"Advanced search failed: {str(e)}")
            return {
                "success": False,
                "error": {"message": str(e), "type": type(e).__name__},
            }

    async def handle_research_collection_request(
        self, request_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        📁 RESEARCH UTILITY: Manage research paper collections

        Researchers organize papers into collections for different projects.
        This enables saving, organizing, and managing research libraries.
        """
        try:
            action = request_data.get("action", "create")

            if action == "create":
                collection_name = request_data.get("name", "")
                if not collection_name.strip():
                    return {
                        "success": False,
                        "error": {
                            "message": "Collection name cannot be empty",
                            "type": "ValidationError",
                        },
                    }

                collection_id = str(uuid.uuid4())
                # In a real implementation, this would be stored in a database
                collection = {
                    "id": collection_id,
                    "name": collection_name,
                    "description": request_data.get("description", ""),
                    "papers": [],
                    "created_at": datetime.now().isoformat(),
                    "updated_at": datetime.now().isoformat(),
                }

                return {
                    "success": True,
                    "data": collection,
                    "message": f"Research collection '{collection_name}' created successfully",
                }

            elif action == "add_paper":
                collection_id = request_data.get("collection_id")
                paper = request_data.get("paper")

                if not collection_id or not paper:
                    return {
                        "success": False,
                        "error": {
                            "message": "Collection ID and paper data required",
                            "type": "ValidationError",
                        },
                    }

                # In a real implementation, this would update the database
                return {
                    "success": True,
                    "data": {"collection_id": collection_id, "paper_added": True},
                    "message": "Paper added to collection successfully",
                }

            else:
                return {
                    "success": False,
                    "error": {
                        "message": f"Unknown action: {action}",
                        "type": "ValidationError",
                    },
                }

        except Exception as e:
            self.logger.error(f"Research collection operation failed: {str(e)}")
            return {
                "success": False,
                "error": {"message": str(e), "type": type(e).__name__},
            }

    def get_api_documentation(self) -> Dict[str, Any]:
        """
        Get API documentation for web interface.

        Returns:
            OpenAPI-style documentation
        """
        return {
            "openapi": "3.0.0",
            "info": {
                "title": "AI Deep Research MCP API",
                "version": "1.0.0",
                "description": "AI-powered research platform API",
            },
            "paths": {
                "/api/research": {
                    "post": {
                        "summary": "Create and execute research",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "query": {"type": "string"},
                                            "sources": {
                                                "type": "array",
                                                "items": {"type": "string"},
                                            },
                                            "max_results": {"type": "integer"},
                                        },
                                        "required": ["query"],
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Research results",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "success": {"type": "boolean"},
                                                "data": {
                                                    "type": "object",
                                                    "properties": {
                                                        "query_id": {"type": "string"},
                                                        "results": {"type": "array"},
                                                    },
                                                },
                                            },
                                        }
                                    }
                                },
                            }
                        },
                    }
                },
                "/api/query": {
                    "post": {
                        "summary": "Create research query",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "query": {"type": "string"},
                                            "sources": {
                                                "type": "array",
                                                "items": {"type": "string"},
                                            },
                                            "max_results": {"type": "integer"},
                                        },
                                        "required": ["query"],
                                    }
                                }
                            }
                        },
                    }
                },
                "/api/execute": {
                    "post": {
                        "summary": "Execute research for existing query",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {"query_id": {"type": "string"}},
                                        "required": ["query_id"],
                                    }
                                }
                            }
                        },
                    }
                },
                "/api/scholarly/search": {
                    "post": {
                        "summary": "Search academic databases (arXiv, Semantic Scholar)",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "query": {"type": "string"},
                                            "sources": {
                                                "type": "array",
                                                "items": {"type": "string"},
                                                "default": [
                                                    "arxiv",
                                                    "semantic_scholar",
                                                ],
                                            },
                                            "max_results": {
                                                "type": "integer",
                                                "default": 10,
                                            },
                                            "include_abstracts": {
                                                "type": "boolean",
                                                "default": True,
                                            },
                                            "min_year": {"type": "integer"},
                                            "max_year": {"type": "integer"},
                                            "fields_of_study": {
                                                "type": "array",
                                                "items": {"type": "string"},
                                            },
                                        },
                                        "required": ["query"],
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Academic papers found",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "success": {"type": "boolean"},
                                                "data": {
                                                    "type": "object",
                                                    "properties": {
                                                        "papers": {"type": "array"},
                                                        "total_found": {
                                                            "type": "integer"
                                                        },
                                                        "sources_used": {
                                                            "type": "array"
                                                        },
                                                        "search_time_ms": {
                                                            "type": "integer"
                                                        },
                                                    },
                                                },
                                            },
                                        }
                                    }
                                },
                            }
                        },
                    }
                },
                "/api/research/enhanced": {
                    "post": {
                        "summary": "Enhanced research with scholarly sources integration",
                        "requestBody": {
                            "content": {
                                "application/json": {
                                    "schema": {
                                        "type": "object",
                                        "properties": {
                                            "query": {"type": "string"},
                                            "sources": {
                                                "type": "array",
                                                "items": {"type": "string"},
                                            },
                                            "max_results": {
                                                "type": "integer",
                                                "default": 10,
                                            },
                                            "include_scholarly": {
                                                "type": "boolean",
                                                "default": True,
                                            },
                                        },
                                        "required": ["query"],
                                    }
                                }
                            }
                        },
                        "responses": {
                            "200": {
                                "description": "Enhanced research results with scholarly sources",
                                "content": {
                                    "application/json": {
                                        "schema": {
                                            "type": "object",
                                            "properties": {
                                                "success": {"type": "boolean"},
                                                "data": {
                                                    "type": "object",
                                                    "properties": {
                                                        "sources": {"type": "array"},
                                                        "sources_count": {
                                                            "type": "integer"
                                                        },
                                                        "scholarly_sources_included": {
                                                            "type": "boolean"
                                                        },
                                                    },
                                                },
                                            },
                                        }
                                    }
                                },
                            }
                        },
                    }
                },
            },
        }


class WebUIComponents:
    """
    Web UI Component helpers for frontend integration.

    Provides reusable components and utilities for web frontend.
    """

    @staticmethod
    def format_results_for_display(
        results: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Format research results for web display."""
        formatted_results = []

        for result in results:
            formatted_results.append(
                {
                    "id": hash(result["content"]),  # Simple ID generation
                    "source": result["source"],
                    "content": (
                        result["content"][:500] + "..."
                        if len(result["content"]) > 500
                        else result["content"]
                    ),
                    "full_content": result["content"],
                    "relevance_score": result["relevance_score"],
                    "relevance_percentage": int(result["relevance_score"] * 100),
                    "timestamp": result["timestamp"],
                    "display_class": WebUIComponents._get_relevance_class(
                        result["relevance_score"]
                    ),
                }
            )

        return formatted_results

    @staticmethod
    def _get_relevance_class(score: float) -> str:
        """Get CSS class based on relevance score."""
        if score >= 0.8:
            return "high-relevance"
        elif score >= 0.6:
            return "medium-relevance"
        else:
            return "low-relevance"

    @staticmethod
    def generate_search_suggestions(query: str) -> List[str]:
        """Generate search suggestions based on query."""
        # Simple suggestion logic - in real implementation this could use ML
        suggestions = []

        query_lower = query.lower()

        if "machine learning" in query_lower:
            suggestions.extend(
                [
                    "machine learning algorithms",
                    "deep learning applications",
                    "ML model training",
                ]
            )
        elif "ai" in query_lower or "artificial intelligence" in query_lower:
            suggestions.extend(
                [
                    "artificial intelligence ethics",
                    "AI applications in healthcare",
                    "AI safety research",
                ]
            )
        elif "climate" in query_lower:
            suggestions.extend(
                [
                    "climate change impacts",
                    "renewable energy solutions",
                    "carbon footprint reduction",
                ]
            )

        return suggestions[:5]  # Limit to 5 suggestions

    @staticmethod
    def format_scholarly_papers_for_display(
        papers: List[Dict[str, Any]],
    ) -> List[Dict[str, Any]]:
        """Format scholarly papers for web display with academic-specific information."""
        formatted_papers = []

        for paper in papers:
            formatted_papers.append(
                {
                    "id": hash(paper.get("title", "")),
                    "title": paper.get("title", ""),
                    "authors": paper.get("authors", []),
                    "authors_display": WebUIComponents._format_authors(
                        paper.get("authors", [])
                    ),
                    "abstract": paper.get("abstract", ""),
                    "year": paper.get("year"),
                    "citation_count": paper.get("citation_count", 0),
                    "citation_display": WebUIComponents._format_citation_count(
                        paper.get("citation_count", 0)
                    ),
                    "venue": paper.get("venue", ""),
                    "pdf_url": paper.get("pdf_url"),
                    "source_url": paper.get("source_url", ""),
                    "source_type": paper.get("source_type", ""),
                    "source_badge": WebUIComponents._get_source_badge(
                        paper.get("source_type", "")
                    ),
                    "relevance_score": paper.get("relevance_score", 0.0),
                    "display_class": paper.get("display_class", ""),
                    "formatted_citation": paper.get("formatted_citation", ""),
                    "doi": paper.get("doi"),
                    "has_pdf": bool(paper.get("pdf_url")),
                    "is_recent": WebUIComponents._is_recent_paper(paper.get("year")),
                    "is_highly_cited": (paper.get("citation_count") or 0) > 100,
                }
            )

        return formatted_papers

    @staticmethod
    def _format_authors(authors: List[str]) -> str:
        """Format author list for display."""
        if not authors:
            return "Unknown Authors"

        if len(authors) == 1:
            return authors[0]
        elif len(authors) <= 3:
            return ", ".join(authors)
        else:
            return f"{', '.join(authors[:2])} et al."

    @staticmethod
    def _format_citation_count(count: int) -> str:
        """Format citation count for display."""
        if count is None or count == 0:
            return "No citations"
        elif count == 1:
            return "1 citation"
        elif count < 1000:
            return f"{count} citations"
        else:
            return f"{count/1000:.1f}k citations"

    @staticmethod
    def _get_source_badge(source_type: str) -> Dict[str, str]:
        """Get badge information for source type."""
        source_badges = {
            "arxiv": {"label": "arXiv", "class": "badge-arxiv", "color": "#b31b1b"},
            "semantic_scholar": {
                "label": "Semantic Scholar",
                "class": "badge-semantic",
                "color": "#1e88e5",
            },
            "google_scholar": {
                "label": "Google Scholar",
                "class": "badge-google",
                "color": "#4285f4",
            },
        }

        return source_badges.get(
            source_type.lower(),
            {
                "label": source_type.replace("_", " ").title(),
                "class": "badge-default",
                "color": "#666666",
            },
        )

    @staticmethod
    def _is_recent_paper(year: Optional[int]) -> bool:
        """Check if paper is from recent years."""
        if not year:
            return False

        from datetime import datetime

        current_year = datetime.now().year
        return year >= (current_year - 3)  # Last 3 years

    @staticmethod
    def generate_scholarly_search_suggestions(query: str) -> List[str]:
        """Generate academic search suggestions based on query."""
        suggestions = []
        query_lower = query.lower()

        # Academic field suggestions
        if any(
            term in query_lower for term in ["machine learning", "ml", "neural network"]
        ):
            suggestions.extend(
                [
                    "deep learning applications",
                    "neural network architectures",
                    "machine learning algorithms",
                    "transformer models",
                    "reinforcement learning",
                ]
            )
        elif any(term in query_lower for term in ["ai", "artificial intelligence"]):
            suggestions.extend(
                [
                    "artificial intelligence ethics",
                    "AI safety research",
                    "natural language processing",
                    "computer vision applications",
                    "AI in healthcare",
                ]
            )
        elif any(term in query_lower for term in ["quantum", "computing"]):
            suggestions.extend(
                [
                    "quantum computing algorithms",
                    "quantum machine learning",
                    "quantum information theory",
                    "quantum cryptography",
                    "quantum error correction",
                ]
            )
        elif any(term in query_lower for term in ["climate", "environment"]):
            suggestions.extend(
                [
                    "climate change mitigation",
                    "renewable energy systems",
                    "carbon capture technology",
                    "environmental sustainability",
                    "green energy solutions",
                ]
            )

        return suggestions[:5]


# Web Interface Factory
def create_web_interface() -> WebInterfaceHandler:
    """
    Factory function to create and configure web interface handler.

    Returns:
        Configured web interface handler
    """
    return WebInterfaceHandler()
