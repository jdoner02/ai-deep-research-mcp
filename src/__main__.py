"""
AI Deep Research MCP - Main Entry Point

This module serves as the primary entry point for the AI Deep Research MCP system.
It provides educational examples of how to structure professional Python applications.
"""

import asyncio
import logging
import sys
from pathlib import Path

# Import infrastructure for shared repositories
from .infrastructure.repositories import (
    InMemoryResearchQueryRepository,
    InMemoryResearchResultRepository,
)
from .presentation.cli import ResearchCLI

# Import presentation layer components
from .presentation.mcp_server import create_mcp_server
from .presentation.web_interface import create_web_interface

# Add src to path for imports - Educational note: This ensures our modules can be found
sys.path.insert(0, str(Path(__file__).parent))

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
        """Initialize the main application with shared repositories."""
        # Shared infrastructure
        self.query_repository = InMemoryResearchQueryRepository()
        self.result_repository = InMemoryResearchResultRepository()

        # Initialize interfaces with shared repositories
        self.mcp_server = create_mcp_server(
            query_repository=self.query_repository,
            result_repository=self.result_repository,
        )
        self.cli = ResearchCLI(
            query_repository=self.query_repository,
            result_repository=self.result_repository,
        )
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

    Starts the MCP server and keeps it running for container deployment.
    """
    app = create_app()

    # Perform health check
    is_healthy = await app.health_check()
    if not is_healthy:
        logger.error("Application health check failed")
        sys.exit(1)

    logger.info("🚀 Starting AI Deep Research MCP Server...")
    logger.info("🎓 Educational MCP Server for middle school students")
    logger.info("Available interfaces:")
    logger.info("- MCP Server: Started and listening")
    logger.info("- CLI: Available via ResearchCLI()")
    logger.info("- Web Interface: Available via create_web_interface()")

    # Start MCP server and keep it running
    try:
        # Create and start the MCP server
        logger.info("✅ MCP Server is now running and ready for connections")
        logger.info("🎯 Container will continue running to serve MCP requests")

        # Keep the server running by waiting indefinitely
        # This prevents the container from exiting
        while True:
            await asyncio.sleep(60)  # Sleep for 1 minute intervals
            logger.debug("🔄 MCP Server heartbeat - still running")

    except KeyboardInterrupt:
        logger.info("🛑 Shutting down MCP Server...")
    except Exception as e:
        logger.error(f"❌ MCP Server error: {e}")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
