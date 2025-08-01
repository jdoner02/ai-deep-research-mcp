"""
Command Line Interface - CLI for AI Deep Research MCP

Provides a command-line interface for interacting with the AI Deep Research system.
Useful for testing, automation, and direct interaction outside of MCP protocol.
"""

import asyncio
import json
import sys
from typing import List, Optional
import argparse
from dataclasses import asdict

from ..application.use_cases import (
    CreateResearchQueryUseCase,
    ExecuteResearchUseCase,
    ResearchOrchestrationService,
    CreateResearchQueryRequest,
    ExecuteResearchRequest,
)
from ..infrastructure.repositories import (
    InMemoryResearchQueryRepository,
    InMemoryResearchResultRepository,
)


class ResearchCLI:
    """
    Command Line Interface for AI Deep Research MCP.

    Provides direct access to research functionality through command line,
    useful for testing and automation.
    """

    def __init__(self):
        """Initialize CLI with dependency injection."""
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

    async def create_query(
        self,
        query_text: str,
        sources: Optional[List[str]] = None,
        max_results: int = 10,
    ) -> str:
        """
        Create a new research query.

        Args:
            query_text: The research question
            sources: Optional list of sources to search
            max_results: Maximum number of results

        Returns:
            Query ID for the created query
        """
        request = CreateResearchQueryRequest(
            query_text=query_text, sources=sources or [], max_results=max_results
        )

        response = await self.create_query_use_case.execute(request)
        return response.query_id

    async def execute_research(self, query_id: str) -> None:
        """
        Execute research for a given query ID.

        Args:
            query_id: The ID of the query to execute
        """
        request = ExecuteResearchRequest(query_id=query_id)
        response = await self.execute_research_use_case.execute(request)

        print(f"Research Results for Query {query_id}:")
        print("=" * 50)

        for i, result in enumerate(response.results, 1):
            print(f"\nResult {i}:")
            print(f"Query: {result.query.text}")
            print(f"Status: {result.status.value}")
            print(f"Sources: {len(result.sources)}")
            for j, source in enumerate(result.sources, 1):
                print(f"  {j}. {source.title}")
                print(f"     URL: {source.url}")
                print(f"     Relevance: {source.relevance_score:.2f}")
            if result.synthesis:
                print(f"Synthesis: {result.synthesis}")
            print("-" * 30)

    async def orchestrate_research(
        self,
        query_text: str,
        sources: Optional[List[str]] = None,
        max_results: int = 10,
    ) -> None:
        """
        Create and execute research in one step.

        Args:
            query_text: The research question
            sources: Optional list of sources to search
            max_results: Maximum number of results
        """
        print(f"Starting research for: {query_text}")
        print("=" * 50)

        response = await self.orchestration_service.create_and_execute_research(
            query_text=query_text, sources=sources or [], max_results=max_results
        )

        print(f"Query ID: {response.create_response.query_id}")
        print(f"Results Found: {len(response.execute_response.results)}")
        print("\nResults:")
        print("-" * 30)

        for i, result in enumerate(response.execute_response.results, 1):
            print(f"\n{i}. Query: {result.query.text}")
            print(f"   Status: {result.status.value}")
            print(f"   Sources: {len(result.sources)}")
            for j, source in enumerate(result.sources, 1):
                print(
                    f"     {j}. {source.title} (Relevance: {source.relevance_score:.2f})"
                )
            if result.synthesis:
                print(f"   Synthesis: {result.synthesis}")


def create_cli_parser() -> argparse.ArgumentParser:
    """Create and configure the CLI argument parser."""
    parser = argparse.ArgumentParser(
        description="AI Deep Research MCP Command Line Interface",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s research "What is machine learning?"
  %(prog)s research "Climate change impacts" --sources "academic" "news"
  %(prog)s create-query "AI ethics" --max-results 5
  %(prog)s execute-research <query-id>
        """,
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Research command
    research_parser = subparsers.add_parser(
        "research", help="Create and execute research in one step"
    )
    research_parser.add_argument("query", help="Research question or topic")
    research_parser.add_argument(
        "--sources", nargs="*", help="Sources to search (optional)"
    )
    research_parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="Maximum number of results (default: 10)",
    )

    # Create query command
    create_parser = subparsers.add_parser(
        "create-query", help="Create a research query without executing"
    )
    create_parser.add_argument("query", help="Research question or topic")
    create_parser.add_argument(
        "--sources", nargs="*", help="Sources to search (optional)"
    )
    create_parser.add_argument(
        "--max-results",
        type=int,
        default=10,
        help="Maximum number of results (default: 10)",
    )

    # Execute research command
    execute_parser = subparsers.add_parser(
        "execute-research", help="Execute research for an existing query"
    )
    execute_parser.add_argument("query_id", help="ID of the query to execute")

    return parser


async def main():
    """Main CLI entry point."""
    parser = create_cli_parser()
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return

    cli = ResearchCLI()

    try:
        if args.command == "research":
            await cli.orchestrate_research(
                query_text=args.query,
                sources=args.sources,
                max_results=args.max_results,
            )

        elif args.command == "create-query":
            query_id = await cli.create_query(
                query_text=args.query,
                sources=args.sources,
                max_results=args.max_results,
            )
            print(f"Query created successfully. ID: {query_id}")

        elif args.command == "execute-research":
            await cli.execute_research(args.query_id)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
