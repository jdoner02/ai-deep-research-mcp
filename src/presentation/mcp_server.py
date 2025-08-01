"""
MCP Server - Main interface for Model Context Protocol

Provides the external MCP server interface following the protocol specification.
Adapts between MCP protocol and our Clean Architecture application layer.
"""

import json
import logging
from dataclasses import asdict
from typing import Any, Dict, List, Optional, Sequence

from ..application.use_cases import (
    CreateResearchQueryRequest,
    CreateResearchQueryUseCase,
    ExecuteResearchRequest,
    ExecuteResearchUseCase,
    ResearchOrchestrationService,
)
from ..domain.entities import ResearchQuery, ResearchResult
from ..infrastructure.repositories import (
    InMemoryResearchQueryRepository,
    InMemoryResearchResultRepository,
)

logger = logging.getLogger(__name__)


class McpServerHandler:
    """
    MCP Server Handler implementing the Model Context Protocol.

    This is the presentation layer adapter that translates MCP protocol
    messages into our Clean Architecture use cases.
    """

    def __init__(
        self,
        query_repository: Optional["InMemoryResearchQueryRepository"] = None,
        result_repository: Optional["InMemoryResearchResultRepository"] = None,
    ):
        """Initialize the MCP server with dependency injection."""
        # Infrastructure dependencies
        self.query_repository = query_repository or InMemoryResearchQueryRepository()
        self.result_repository = result_repository or InMemoryResearchResultRepository()

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

    async def handle_tool_call(
        self, tool_name: str, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Handle MCP tool calls by routing to appropriate use cases.

        Args:
            tool_name: Name of the tool being called
            arguments: Tool arguments from MCP protocol

        Returns:
            Tool response following MCP protocol format
        """
        try:
            if tool_name == "create_research_query":
                return await self._handle_create_research_query(arguments)
            elif tool_name == "execute_research":
                return await self._handle_execute_research(arguments)
            elif tool_name == "orchestrate_research":
                return await self._handle_orchestrate_research(arguments)
            else:
                raise ValueError(f"Unknown tool: {tool_name}")

        except Exception as e:
            logger.error(f"Error handling tool call {tool_name}: {e}")
            return {"error": {"code": "TOOL_ERROR", "message": str(e)}}

    async def _handle_create_research_query(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle create_research_query tool call."""
        query_text = arguments.get("query", "")
        sources = arguments.get("sources", [])
        max_results = arguments.get("max_results", 10)

        request = CreateResearchQueryRequest(
            query_text=query_text, sources=sources, max_results=max_results
        )

        response = await self.create_query_use_case.execute(request)

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Research query created successfully. Query ID: {response.query_id}",
                }
            ]
        }

    async def _handle_execute_research(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle execute_research tool call."""
        query_id = arguments.get("query_id", "")

        request = ExecuteResearchRequest(query_id=query_id)
        response = await self.execute_research_use_case.execute(request)

        # Format results for MCP response
        results_text = []
        for result in response.results:
            results_text.append(f"Query: {result.query.text}")
            results_text.append(f"Status: {result.status.value}")
            results_text.append(f"Sources found: {len(result.sources)}")
            for i, source in enumerate(result.sources, 1):
                results_text.append(f"  {i}. {source.title}")
                results_text.append(f"     URL: {source.url}")
                results_text.append(f"     Relevance: {source.relevance_score:.2f}")
            if result.synthesis:
                results_text.append(f"Synthesis: {result.synthesis}")
            results_text.append("---")

        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Research executed successfully.\n\nResults:\n"
                    + "\n".join(results_text),
                }
            ]
        }

    async def _handle_orchestrate_research(
        self, arguments: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Handle orchestrate_research tool call - full research workflow."""
        query_text = arguments.get("query", "")
        sources = arguments.get("sources", [])
        max_results = arguments.get("max_results", 10)

        # Execute full research orchestration
        query_response = await self.orchestration_service.create_and_execute_research(
            query_text=query_text, sources=sources, max_results=max_results
        )

        # Format comprehensive response
        response_parts = [
            f"Research Query: {query_text}",
            f"Query ID: {query_response.create_response.query_id}",
            "",
            "Results:",
        ]

        for result in query_response.execute_response.results:
            response_parts.append(f"• Query: {result.query.text}")
            response_parts.append(f"  Status: {result.status.value}")
            response_parts.append(f"  Sources: {len(result.sources)}")
            for i, source in enumerate(result.sources, 1):
                response_parts.append(
                    f"    {i}. {source.title} (Relevance: {source.relevance_score:.2f})"
                )
            if result.synthesis:
                response_parts.append(f"  Synthesis: {result.synthesis}")
            response_parts.append("")

        return {"content": [{"type": "text", "text": "\n".join(response_parts)}]}

    def get_tool_definitions(self) -> List[Dict[str, Any]]:
        """
        Get MCP tool definitions for this server.

        Returns:
            List of tool definitions following MCP protocol
        """
        return [
            {
                "name": "create_research_query",
                "description": "Create a new research query for AI-powered analysis",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The research question or topic to investigate",
                        },
                        "sources": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of sources to search (optional)",
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 10,
                        },
                    },
                    "required": ["query"],
                },
            },
            {
                "name": "execute_research",
                "description": "Execute research for an existing query",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query_id": {
                            "type": "string",
                            "description": "The ID of the research query to execute",
                        }
                    },
                    "required": ["query_id"],
                },
            },
            {
                "name": "orchestrate_research",
                "description": "Create and execute research in one step",
                "inputSchema": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "The research question or topic to investigate",
                        },
                        "sources": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "List of sources to search (optional)",
                        },
                        "max_results": {
                            "type": "integer",
                            "description": "Maximum number of results to return",
                            "default": 10,
                        },
                    },
                    "required": ["query"],
                },
            },
        ]


# MCP Server Factory Function
def create_mcp_server(
    query_repository: Optional["InMemoryResearchQueryRepository"] = None,
    result_repository: Optional["InMemoryResearchResultRepository"] = None,
) -> McpServerHandler:
    """
    Factory function to create and configure the MCP server.

    This function sets up all dependencies and returns a ready-to-use
    MCP server handler.

    Args:
        query_repository: Optional shared query repository instance
        result_repository: Optional shared result repository instance
    """
    return McpServerHandler(
        query_repository=query_repository, result_repository=result_repository
    )
