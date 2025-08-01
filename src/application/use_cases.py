"""
Application Layer Use Cases

This layer contains the application services (use cases) that orchestrate
the domain logic to fulfill business workflows. Use cases are stateless
and depend only on domain interfaces.
"""

import asyncio
from dataclasses import dataclass, field
from typing import List, Optional
from datetime import datetime
import uuid

from ..domain.entities import (
    ResearchQuery,
    ResearchResult,
    ResearchSource,
    QueryId,
    ResearchQueryType,
    ResearchStatus,
    SourceType,
    ResearchQueryRepository,
    ResearchResultRepository,
    InvalidQueryException,
    DomainException,
    QueryNotFoundError,
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
            id=QueryId(),
            text=request.query_text.strip(),
            query_type=ResearchQueryType.GENERAL,  # Default type
            created_at=datetime.now(),
            max_sources=request.max_results,  # Using our actual field name
        )

        # Save to repository
        self._query_repository.save(query)

        return CreateResearchQueryResponse(query_id=str(query.id.value))


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
        if isinstance(request.query_id, str):
            query_id = QueryId(uuid.UUID(request.query_id))
        else:
            query_id = QueryId(request.query_id)
        query = self._query_repository.find_by_id(query_id)

        if query is None:
            raise QueryNotFoundError(f"Query not found: {query_id}")

        # Simulate research execution by creating mock results
        # In a real implementation, this would call external services
        results = await self._simulate_research(query)

        # Save results
        for result in results:
            self._result_repository.save(result)

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
        # Create a research result for this query
        result = ResearchResult(
            query=query,
            status=ResearchStatus.COMPLETED,
            completed_at=datetime.now(),
        )

        # Add mock sources based on query preferences
        source_types = []
        if query.include_web_search:
            source_types.append(SourceType.WEB)
        if query.include_academic_sources:
            source_types.append(SourceType.ARXIV)

        if not source_types:
            source_types = [SourceType.WEB]  # Default fallback

        for i, source_type in enumerate(source_types):
            if len(result.sources) >= query.max_sources:
                break

            # Mock result content based on query
            content = f"Research result {i+1} from {source_type.value} for query: '{query.text}'"
            if "machine learning" in query.text.lower():
                content += " - Machine learning is a subset of artificial intelligence."
            elif "climate" in query.text.lower():
                content += " - Climate change is a significant global challenge."
            elif "quantum" in query.text.lower():
                content += " - Quantum computing leverages quantum mechanics."

            # Create a research source
            source = ResearchSource(
                url=f"https://example.com/source_{i}",
                title=f"Research Source {i+1}",
                source_type=source_type,
                content=content,
                relevance_score=0.8 - (i * 0.1),  # Decreasing relevance
            )
            result.add_source(source)

        # Simulate async processing delay
        await asyncio.sleep(0.1)

        return [result]


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
