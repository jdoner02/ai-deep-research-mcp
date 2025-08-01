"""
🧪 Unit Tests for Application Layer Use Cases - Educational Edition

This file tests our application layer - the "business logic" that coordinates
between different parts of our system to accomplish user goals.

🎯 What is the Application Layer?
Think of it like the conductor of an orchestra. The conductor doesn't play
any instruments (that's the domain layer), but they coordinate all the
musicians (repositories, services, etc.) to create beautiful music (user features).

🔍 What We're Testing Here:
- CreateResearchQueryUseCase: How we handle new research requests
- ExecuteResearchUseCase: How we actually perform the research
- ResearchOrchestrationService: How we coordinate complex research workflows

💡 Key Testing Concepts You'll Learn:
- How to test business logic that coordinates multiple components
- Using mocks to isolate the code we're testing
- Testing both successful scenarios and error conditions
- Async/await testing patterns for modern Python applications

🏗️ Application Layer Responsibilities:
1. Validate user input
2. Orchestrate domain objects and repository calls
3. Handle errors gracefully
4. Return formatted responses to the presentation layer

This is where the "business rules" live - the step-by-step processes that
define how our AI research system actually works!
"""

import pytest
import uuid
from datetime import datetime
from unittest.mock import Mock, AsyncMock
from typing import List

from unittest.mock import Mock, AsyncMock

from src.application.use_cases import (
    CreateResearchQueryUseCase,
    ExecuteResearchUseCase,
    ResearchOrchestrationService,
    CreateResearchQueryRequest,
    CreateResearchQueryResponse,
    ExecuteResearchRequest,
    ExecuteResearchResponse,
    OrchestrationResponse,
)
from src.domain.entities import (
    ResearchQuery,
    ResearchResult,
    QueryId,
    ResearchQueryType,
    ResearchSource,
    SourceType,
    ResearchStatus,
    QueryNotFoundError,
    InvalidQueryException,
    DomainException,
)


class TestCreateResearchQueryUseCase:
    """
    🎯 Test cases for CreateResearchQueryUseCase.

    This use case handles creating new research requests from users.
    It's like the "intake desk" at a research library - it takes your
    question, assigns it an ID, and gets it ready for processing.

    🧪 What We're Testing:
    - Can we create valid research queries?
    - Do we handle invalid input correctly?
    - Does the use case save queries to the repository?
    - Do we return the right response format?

    💡 Educational Focus:
    - Learn about use case testing patterns
    - Understand mock objects for repositories
    - Practice testing input validation
    - See how to test business logic coordination
    """

    @pytest.fixture
    def mock_query_repository(self):
        """
        🎭 Create a mock query repository for testing.

        A mock is like a "practice partner" - it pretends to be the real
        repository but lets us control exactly what it does. This way,
        we can test our use case without needing a real database.

        Why use mocks?
        - Tests run faster (no database operations)
        - Tests are more reliable (no external dependencies)
        - We can simulate error scenarios easily
        - We can verify our code calls the repository correctly
        """
        return Mock()

    @pytest.fixture
    def use_case(self, mock_query_repository):
        """
        🏗️ Create use case with mock repository.

        This fixture sets up our use case with a mock repository,
        so every test gets a fresh, clean use case to work with.

        It's like getting a new worksheet for each math problem -
        you start fresh each time without leftover work from before.
        """
        return CreateResearchQueryUseCase(query_repository=mock_query_repository)

    @pytest.mark.asyncio
    async def test_create_query_success(self, use_case, mock_query_repository):
        """Test successful query creation."""
        # Arrange
        request = CreateResearchQueryRequest(
            query_text="What is artificial intelligence?",
            sources=["web", "academic"],
            max_results=10,
        )

        # Act
        response = await use_case.execute(request)

        # Assert
        assert isinstance(response, CreateResearchQueryResponse)
        assert response.query_id is not None
        assert len(response.query_id) > 0

        # Verify repository was called
        mock_query_repository.save.assert_called_once()
        saved_query = mock_query_repository.save.call_args[0][0]
        assert isinstance(saved_query, ResearchQuery)
        assert saved_query.text == "What is artificial intelligence?"
        assert saved_query.max_sources == 10

    @pytest.mark.asyncio
    async def test_create_query_with_defaults(self, use_case, mock_query_repository):
        """Test query creation with default values."""
        # Arrange
        request = CreateResearchQueryRequest(query_text="Test query")

        # Act
        response = await use_case.execute(request)

        # Assert
        assert isinstance(response, CreateResearchQueryResponse)
        mock_query_repository.save.assert_called_once()

        saved_query = mock_query_repository.save.call_args[0][0]
        assert saved_query.max_sources == 10  # Default value
        assert saved_query.include_web_search is True  # Default value
        assert saved_query.include_academic_sources is True  # Default value

    @pytest.mark.asyncio
    async def test_create_query_empty_text_raises_error(self, use_case):
        """Test that empty query text raises InvalidQueryException."""
        # Arrange
        request = CreateResearchQueryRequest(query_text="")

        # Act & Assert
        with pytest.raises(InvalidQueryException):
            await use_case.execute(request)

    @pytest.mark.asyncio
    async def test_create_query_invalid_max_results_raises_error(self, use_case):
        """Test that invalid max_results raises InvalidQueryException."""
        # Arrange
        request = CreateResearchQueryRequest(query_text="Valid query", max_results=-1)

        # Act & Assert
        with pytest.raises(InvalidQueryException):
            await use_case.execute(request)


class TestExecuteResearchUseCase:
    """Test cases for ExecuteResearchUseCase."""

    @pytest.fixture
    def mock_query_repository(self):
        """Mock query repository."""
        return Mock()

    @pytest.fixture
    def mock_result_repository(self):
        """Mock result repository."""
        return Mock()

    @pytest.fixture
    def use_case(self, mock_query_repository, mock_result_repository):
        """Create use case with mock repositories."""
        return ExecuteResearchUseCase(
            query_repository=mock_query_repository,
            result_repository=mock_result_repository,
        )

    @pytest.fixture
    def sample_query(self):
        """Sample query for testing."""
        return ResearchQuery(
            id=QueryId(),
            text="What is AI?",
            query_type=ResearchQueryType.GENERAL,
            created_at=datetime.now(),
            max_sources=5,
        )

    @pytest.mark.asyncio
    async def test_execute_research_success(
        self, use_case, mock_query_repository, mock_result_repository, sample_query
    ):
        """Test successful research execution."""
        # Arrange
        request = ExecuteResearchRequest(query_id=str(sample_query.id.value))

        # Mock repository responses
        mock_query_repository.find_by_id.return_value = sample_query

        sample_results = [
            ResearchResult(
                query=sample_query,
                status=ResearchStatus.COMPLETED,
            )
        ]
        mock_result_repository.find_by_query_id.return_value = sample_results

        # Act
        response = await use_case.execute(request)

        # Assert
        assert isinstance(response, ExecuteResearchResponse)
        assert len(response.results) > 0
        assert response.results[0].query == sample_query
        assert response.results[0].status == ResearchStatus.COMPLETED

        # Verify repositories were called
        mock_query_repository.find_by_id.assert_called_once()
        mock_result_repository.save.assert_called()

    @pytest.mark.asyncio
    async def test_execute_research_query_not_found(
        self, use_case, mock_query_repository, mock_result_repository
    ):
        """Test research execution with non-existent query."""
        # Arrange
        request = ExecuteResearchRequest(query_id=str(uuid.uuid4()))
        mock_query_repository.find_by_id.return_value = None

        # Act & Assert
        with pytest.raises(QueryNotFoundError):
            await use_case.execute(request)

        # Verify repository was called
        mock_query_repository.find_by_id.assert_called_once()
        mock_result_repository.save.assert_not_called()

    @pytest.mark.asyncio
    async def test_execute_research_no_results(
        self, use_case, mock_query_repository, mock_result_repository, sample_query
    ):
        """Test research execution that yields no results."""
        # Arrange
        request = ExecuteResearchRequest(query_id=str(sample_query.id.value))
        mock_query_repository.find_by_id.return_value = sample_query

        # Act
        response = await use_case.execute(request)

        # Assert
        assert isinstance(response, ExecuteResearchResponse)
        assert len(response.results) > 0  # Should have at least one mock result

        # Verify repositories were called
        mock_query_repository.find_by_id.assert_called_once()


class TestResearchOrchestrationService:
    """Test cases for ResearchOrchestrationService."""

    @pytest.fixture
    def mock_create_use_case(self):
        """Mock create query use case."""
        return AsyncMock()

    @pytest.fixture
    def mock_execute_use_case(self):
        """Mock execute research use case."""
        return AsyncMock()

    @pytest.fixture
    def orchestration_service(self, mock_create_use_case, mock_execute_use_case):
        """Create orchestration service with mock use cases."""
        return ResearchOrchestrationService(
            create_query_use_case=mock_create_use_case,
            execute_research_use_case=mock_execute_use_case,
        )

    @pytest.mark.asyncio
    async def test_create_and_execute_research_success(
        self,
        orchestration_service,
        mock_create_use_case,
        mock_execute_use_case,
    ):
        """Test successful end-to-end research orchestration."""
        # Arrange
        query_text = "Test research query"
        sources = ["web", "academic"]
        max_results = 5

        # Mock responses
        create_response = CreateResearchQueryResponse(
            query_id="test-query-id",
        )
        mock_create_use_case.execute.return_value = create_response

        execute_response = ExecuteResearchResponse(
            results=[
                ResearchResult(
                    query=ResearchQuery(
                        id=QueryId(),
                        text=query_text,
                        query_type=ResearchQueryType.GENERAL,
                        created_at=datetime.now(),
                    ),
                    status=ResearchStatus.COMPLETED,
                )
            ]
        )
        mock_execute_use_case.execute.return_value = execute_response

        # Act
        response = await orchestration_service.create_and_execute_research(
            query_text=query_text, sources=sources, max_results=max_results
        )

        # Assert
        assert isinstance(response, OrchestrationResponse)
        assert response.create_response == create_response
        assert response.execute_response == execute_response

        # Verify use cases were called
        mock_create_use_case.execute.assert_called_once()
        mock_execute_use_case.execute.assert_called_once()

        # Verify correct arguments were passed
        create_args = mock_create_use_case.execute.call_args[0][0]
        assert create_args.query_text == query_text
        assert create_args.sources == sources
        assert create_args.max_results == max_results

        execute_args = mock_execute_use_case.execute.call_args[0][0]
        assert execute_args.query_id == "test-query-id"
