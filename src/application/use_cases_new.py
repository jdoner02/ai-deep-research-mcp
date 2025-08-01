"""
Application Layer Use Cases

This layer contains the application services (use cases) that orchestrate
the domain logic to fulfill business workflows. Use cases are stateless
and depend only on domain interfaces.
"""

import asyncio
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional

from ..domain.entities import (
    DomainException,
    InvalidQueryException,
    QueryId,
    ResearchQuery,
    ResearchQueryRepository,
    ResearchResult,
    ResearchResultRepository,
)

# Use Case DTOs


@dataclass
class CreateResearchQueryRequest:
    """Request to create a new research query."""

    query_text: str
    sources: List[str] = field(default_factory=list)
    max_results: int = 10


@dataclass
class CreateResearchQueryResponse:
    """Response from creating a research query."""

    query_id: str


@dataclass
class ExecuteResearchRequest:
    """Request to execute research for a query."""

    query_id: str


@dataclass
class ExecuteResearchResponse:
    """Response from executing research."""

    results: List[ResearchResult]


@dataclass
class OrchestrationResponse:
    """Response from full research orchestration."""

    create_response: CreateResearchQueryResponse
    execute_response: ExecuteResearchResponse


# Use Cases


class CreateResearchQueryUseCase:
    """Use case for creating new research queries."""

    def __init__(self, query_repository: ResearchQueryRepository):
        self._query_repository = query_repository

    async def execute(
        self, request: CreateResearchQueryRequest
    ) -> CreateResearchQueryResponse:
        """
        Execute the create research query use case.

        Args:
            request: The create query request

        Returns:
            Response containing the created query ID

        Raises:
            InvalidQueryException: If the query is invalid
        """
        # Validate request
        if not request.query_text or not request.query_text.strip():
            raise InvalidQueryException("Query text cannot be empty")

        if request.max_results <= 0:
            raise InvalidQueryException("Max results must be positive")

        # Create domain entity
        query = ResearchQuery(
            query_id=QueryId.generate(),
            query_text=request.query_text.strip(),
            sources=request.sources,
            max_results=request.max_results,
        )

        # Save to repository
        await self._query_repository.save(query)

        return CreateResearchQueryResponse(query_id=query.query_id.value)


class ExecuteResearchUseCase:
    """Use case for executing research on existing queries."""

    def __init__(
        self,
        query_repository: ResearchQueryRepository,
        result_repository: ResearchResultRepository,
    ):
        self._query_repository = query_repository
        self._result_repository = result_repository

    async def execute(self, request: ExecuteResearchRequest) -> ExecuteResearchResponse:
        """
        Execute research for a given query.

        Args:
            request: The execute research request

        Returns:
            Response containing research results

        Raises:
            DomainException: If the query doesn't exist or execution fails
        """
        # Find the query
        query_id = QueryId(request.query_id)
        query = await self._query_repository.find_by_id(query_id)

        if query is None:
            raise DomainException(f"Query not found: {query_id}")

        # Simulate research execution by creating mock results
        # In a real implementation, this would call external services
        results = await self._simulate_research(query)

        # Save results
        for result in results:
            await self._result_repository.save(result)

        return ExecuteResearchResponse(results=results)

    async def _simulate_research(self, query: ResearchQuery) -> List[ResearchResult]:
        """
        Simulate research execution.

        In a real implementation, this would:
        1. Call source search services
        2. Retrieve and analyze content
        3. Score relevance
        4. Return structured results
        """
        # Create mock results based on query
        results = []

        for i, source in enumerate(query.sources or ["web", "academic"]):
            if len(results) >= query.max_results:
                break

            # Mock result content based on query
            content = (
                f"Research result {i+1} from {source} for query: '{query.query_text}'"
            )
            if "machine learning" in query.query_text.lower():
                content += " - Machine learning is a subset of artificial intelligence."
            elif "climate" in query.query_text.lower():
                content += " - Climate change is a significant global challenge."
            elif "quantum" in query.query_text.lower():
                content += " - Quantum computing leverages quantum mechanics."

            result = ResearchResult(
                query_id=query.query_id,
                source=source,
                content=content,
                relevance_score=0.8 - (i * 0.1),  # Decreasing relevance
            )
            results.append(result)

        # Simulate async processing delay
        await asyncio.sleep(0.1)

        return results


class ResearchOrchestrationService:
    """
    Service that orchestrates complete research workflows.

    This service combines multiple use cases to provide
    higher-level business workflows.
    """

    def __init__(
        self,
        create_query_use_case: CreateResearchQueryUseCase,
        execute_research_use_case: ExecuteResearchUseCase,
    ):
        self._create_query_use_case = create_query_use_case
        self._execute_research_use_case = execute_research_use_case

    async def create_and_execute_research(
        self, query_text: str, sources: List[str], max_results: int
    ) -> OrchestrationResponse:
        """
        Create a query and execute research in one workflow.

        Args:
            query_text: The research question
            sources: Sources to search
            max_results: Maximum results to return

        Returns:
            Combined response with both create and execute results
        """
        # Step 1: Create the query
        create_request = CreateResearchQueryRequest(
            query_text=query_text, sources=sources, max_results=max_results
        )
        create_response = await self._create_query_use_case.execute(create_request)

        # Step 2: Execute research
        execute_request = ExecuteResearchRequest(query_id=create_response.query_id)
        execute_response = await self._execute_research_use_case.execute(
            execute_request
        )

        return OrchestrationResponse(
            create_response=create_response, execute_response=execute_response
        )
