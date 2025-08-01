"""
AI Deep Research MCP - Main Entry Point

This module provides the main entry point and configuration for the
AI Deep Research MCP system following Clean Architecture principles.
"""

import asyncio
import logging
import sys
from typing import Optional
from pathlib import Path

# Import presentation layer components
from .presentation.mcp_server import create_mcp_server
from .presentation.cli import ResearchCLI
from .presentation.web_interface import create_web_interface

# Set up logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


class AIDeepResearchMCP:
    """
    Main application class for AI Deep Research MCP.

    Coordinates the different presentation interfaces (MCP, CLI, Web)
    and provides a unified entry point for the application.
    """

    def __init__(self):
        """Initialize the main application."""
        self.mcp_server = create_mcp_server()
        self.cli = ResearchCLI()
        self.web_interface = create_web_interface()

        logger.info("AI Deep Research MCP initialized successfully")

    def get_mcp_server(self):
        """Get the MCP server handler."""
        return self.mcp_server

    def get_cli(self):
        """Get the CLI handler."""
        return self.cli

    def get_web_interface(self):
        """Get the web interface handler."""
        return self.web_interface

    async def health_check(self) -> bool:
        """
        Perform a health check on the system.

        Returns:
            True if system is healthy, False otherwise
        """
        try:
            # Test basic functionality
            query_id = await self.cli.create_query("Health check test query")
            logger.info(f"Health check passed - created query {query_id}")
            return True
        except Exception as e:
            logger.error(f"Health check failed: {e}")
            return False


def create_app() -> AIDeepResearchMCP:
    """
    Application factory function.

    Creates and configures the main application instance.
    This is the recommended way to create the application.

    Returns:
        Configured AIDeepResearchMCP instance
    """
    return AIDeepResearchMCP()


async def main():
    """
    Main async entry point for the application.

    This function can be used for testing or running the application directly.
    """
    app = create_app()

    # Perform health check
    is_healthy = await app.health_check()
    if not is_healthy:
        logger.error("Application health check failed")
        sys.exit(1)

    logger.info("AI Deep Research MCP is ready")
    logger.info("Available interfaces:")
    logger.info("- MCP Server: Use create_mcp_server()")
    logger.info("- CLI: Use ResearchCLI() or run cli.py")
    logger.info("- Web Interface: Use create_web_interface()")


if __name__ == "__main__":
    asyncio.run(main())
