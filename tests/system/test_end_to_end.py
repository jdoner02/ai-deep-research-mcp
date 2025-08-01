"""
System Tests for Complete Application Workflows

Tests the complete system integration from presentation layer
through to infrastructure, verifying end-to-end functionality.
"""

import pytest
import json
from unittest.mock import patch

from src import create_app
from src.presentation.mcp_server import create_mcp_server
from src.presentation.cli import ResearchCLI
from src.presentation.web_interface import create_web_interface


class TestMCPServerIntegration:
    """Test complete MCP server integration."""

    @pytest.fixture
    def mcp_server(self):
        """Create MCP server for testing."""
        return create_mcp_server()

    @pytest.mark.asyncio
    async def test_create_research_query_tool(self, mcp_server):
        """Test create_research_query tool end-to-end."""
        arguments = {
            "query": "What is artificial intelligence?",
            "sources": ["academic", "web"],
            "max_results": 5,
        }

        response = await mcp_server.handle_tool_call("create_research_query", arguments)

        # Verify response structure
        assert "content" in response
        assert len(response["content"]) > 0
        assert "text" in response["content"][0]
        assert "Query ID:" in response["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_orchestrate_research_tool(self, mcp_server):
        """Test orchestrate_research tool end-to-end."""
        arguments = {
            "query": "Machine learning applications",
            "sources": ["web"],
            "max_results": 3,
        }

        response = await mcp_server.handle_tool_call("orchestrate_research", arguments)

        # Verify response structure
        assert "content" in response
        assert len(response["content"]) > 0
        content_text = response["content"][0]["text"]

        assert "Research Query: Machine learning applications" in content_text
        assert "Query ID:" in content_text
        assert "Results:" in content_text

    @pytest.mark.asyncio
    async def test_execute_research_tool(self, mcp_server):
        """Test execute_research tool with existing query."""
        # First create a query
        create_args = {"query": "Deep learning basics", "sources": ["academic"]}

        create_response = await mcp_server.handle_tool_call(
            "create_research_query", create_args
        )

        # Extract query ID from response
        create_text = create_response["content"][0]["text"]
        query_id = create_text.split("Query ID: ")[1].strip()

        # Now execute research
        execute_args = {"query_id": query_id}
        execute_response = await mcp_server.handle_tool_call(
            "execute_research", execute_args
        )

        # Verify response
        assert "content" in execute_response
        execute_text = execute_response["content"][0]["text"]
        assert "Research executed successfully" in execute_text

    @pytest.mark.asyncio
    async def test_unknown_tool_returns_error(self, mcp_server):
        """Test that unknown tools return proper error response."""
        response = await mcp_server.handle_tool_call("unknown_tool", {})

        assert "error" in response
        assert response["error"]["code"] == "TOOL_ERROR"
        assert "Unknown tool" in response["error"]["message"]

    def test_get_tool_definitions(self, mcp_server):
        """Test that tool definitions are properly formatted."""
        definitions = mcp_server.get_tool_definitions()

        assert len(definitions) == 3

        tool_names = [tool["name"] for tool in definitions]
        expected_names = [
            "create_research_query",
            "execute_research",
            "orchestrate_research",
        ]

        assert set(tool_names) == set(expected_names)

        # Verify each tool has required fields
        for tool in definitions:
            assert "name" in tool
            assert "description" in tool
            assert "inputSchema" in tool
            assert "type" in tool["inputSchema"]
            assert "properties" in tool["inputSchema"]


class TestCLIIntegration:
    """Test complete CLI integration."""

    @pytest.fixture
    def cli(self):
        """Create CLI for testing."""
        return ResearchCLI()

    @pytest.mark.asyncio
    async def test_create_query_workflow(self, cli):
        """Test CLI create query workflow."""
        query_id = await cli.create_query(
            query_text="What is quantum computing?",
            sources=["academic", "web"],
            max_results=7,
        )

        assert query_id is not None
        assert isinstance(query_id, str)
        assert len(query_id) > 0

    @pytest.mark.asyncio
    async def test_orchestrate_research_workflow(self, cli, capsys):
        """Test CLI orchestrate research workflow with output capture."""
        await cli.orchestrate_research(
            query_text="Climate change solutions", sources=["scientific"], max_results=3
        )

        # Capture printed output
        captured = capsys.readouterr()

        assert "Starting research for: Climate change solutions" in captured.out
        assert "Query ID:" in captured.out
        assert "Results Found:" in captured.out


class TestWebInterfaceIntegration:
    """Test complete web interface integration."""

    @pytest.fixture
    def web_interface(self):
        """Create web interface for testing."""
        return create_web_interface()

    @pytest.mark.asyncio
    async def test_handle_research_request(self, web_interface):
        """Test web interface research request handling."""
        request_data = {
            "query": "Renewable energy technologies",
            "sources": ["scientific", "news"],
            "max_results": 5,
        }

        response = await web_interface.handle_research_request(request_data)

        # Verify response structure
        assert response["success"] is True
        assert "data" in response

        data = response["data"]
        assert "query_id" in data
        assert "query_text" in data
        assert "results_count" in data
        assert "results" in data

        assert data["query_text"] == "Renewable energy technologies"
        assert isinstance(data["results"], list)

    @pytest.mark.asyncio
    async def test_handle_create_query_request(self, web_interface):
        """Test web interface create query request."""
        request_data = {
            "query": "Blockchain applications",
            "sources": ["tech"],
            "max_results": 10,
        }

        response = await web_interface.handle_create_query_request(request_data)

        assert response["success"] is True
        assert "data" in response
        assert "query_id" in response["data"]
        assert "message" in response["data"]
        assert response["data"]["message"] == "Query created successfully"

    @pytest.mark.asyncio
    async def test_handle_execute_research_request(self, web_interface):
        """Test web interface execute research request."""
        # First create a query
        create_request = {"query": "AI ethics principles", "sources": ["academic"]}

        create_response = await web_interface.handle_create_query_request(
            create_request
        )
        query_id = create_response["data"]["query_id"]

        # Now execute research
        execute_request = {"query_id": query_id}
        execute_response = await web_interface.handle_execute_research_request(
            execute_request
        )

        assert execute_response["success"] is True
        assert "data" in execute_response
        assert "results" in execute_response["data"]
        assert "results_count" in execute_response["data"]

    @pytest.mark.asyncio
    async def test_invalid_request_returns_error(self, web_interface):
        """Test that invalid requests return proper error responses."""
        # Request with empty query
        invalid_request = {"query": ""}

        response = await web_interface.handle_research_request(invalid_request)

        assert response["success"] is False
        assert "error" in response
        assert "message" in response["error"]

    def test_get_api_documentation(self, web_interface):
        """Test API documentation generation."""
        docs = web_interface.get_api_documentation()

        assert "openapi" in docs
        assert "info" in docs
        assert "paths" in docs

        # Verify expected endpoints
        paths = docs["paths"]
        expected_paths = ["/api/research", "/api/query", "/api/execute"]

        for path in expected_paths:
            assert path in paths


class TestApplicationFactoryIntegration:
    """Test main application factory and integration."""

    @pytest.mark.asyncio
    async def test_create_app_factory(self):
        """Test that create_app factory works correctly."""
        app = create_app()

        # Verify app has all required components
        assert app.get_mcp_server() is not None
        assert app.get_cli() is not None
        assert app.get_web_interface() is not None

    @pytest.mark.asyncio
    async def test_application_health_check(self):
        """Test application health check."""
        app = create_app()

        is_healthy = await app.health_check()

        assert is_healthy is True

    @pytest.mark.asyncio
    async def test_cross_interface_consistency(self):
        """Test that all interfaces work with the same underlying system."""
        app = create_app()

        # Create query through CLI
        cli = app.get_cli()
        query_id = await cli.create_query("Cross-interface test query")

        # Execute through MCP server
        mcp_server = app.get_mcp_server()
        response = await mcp_server.handle_tool_call(
            "execute_research", {"query_id": query_id}
        )

        # Verify response
        assert "content" in response
        assert "Research executed successfully" in response["content"][0]["text"]

    @pytest.mark.asyncio
    async def test_error_handling_consistency(self):
        """Test that error handling is consistent across interfaces."""
        app = create_app()

        # Test invalid query through different interfaces
        cli = app.get_cli()
        mcp_server = app.get_mcp_server()
        web_interface = app.get_web_interface()

        # All should handle empty query appropriately
        with pytest.raises(Exception):  # CLI raises exception
            await cli.create_query("")

        # MCP server returns error response
        mcp_response = await mcp_server.handle_tool_call(
            "create_research_query", {"query": ""}
        )
        assert "error" in mcp_response

        # Web interface returns error response
        web_response = await web_interface.handle_create_query_request({"query": ""})
        assert web_response["success"] is False
