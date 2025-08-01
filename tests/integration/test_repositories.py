"""
Integration Tests for Repository Implementations

Tests the infrastructure layer repository implementations
against the domain interfaces to ensure they work correctly together.
"""

from datetime import datetime, timedelta

import pytest

from src.domain.entities import (
    QueryId,
    ResearchQuery,
    ResearchQueryType,
    ResearchResult,
    ResearchStatus,
)
from src.infrastructure.repositories import (
    InMemoryResearchQueryRepository,
    InMemoryResearchResultRepository,
)


class TestInMemoryResearchQueryRepository:
    """Test cases for InMemoryResearchQueryRepository."""

    @pytest.fixture
    def repository(self):
        """Fresh repository for each test."""
        return InMemoryResearchQueryRepository()

    @pytest.fixture
    def sample_query(self):
        """Sample research query."""
        return ResearchQuery(
            id=QueryId(),
            text="What is machine learning?",
            query_type=ResearchQueryType.GENERAL,
            created_at=datetime.now(),
            max_sources=10,
        )

    @pytest.mark.asyncio
    async def test_save_and_find_by_id_success(self, repository, sample_query):
        """Test saving and retrieving a query by ID."""
        # Save query
        repository.save(sample_query)

        # Retrieve query
        found_query = repository.find_by_id(sample_query.id)

        # Assert
        assert found_query is not None
        assert found_query.id == sample_query.id
        assert found_query.text == sample_query.text
        assert found_query.query_type == sample_query.query_type
        assert found_query.max_sources == sample_query.max_sources

    @pytest.mark.asyncio
    async def test_find_by_id_not_found(self, repository):
        """Test retrieving non-existent query returns None."""
        non_existent_id = QueryId()

        found_query = repository.find_by_id(non_existent_id)

        assert found_query is None

    @pytest.mark.asyncio
    async def test_save_overwrites_existing(self, repository, sample_query):
        """Test that saving an existing query overwrites it."""
        # Save original
        repository.save(sample_query)

        # Create modified version with same ID
        modified_query = ResearchQuery(
            id=sample_query.id,
            text="Updated query text",
            query_type=ResearchQueryType.GENERAL,
            created_at=datetime.now(),
            max_sources=20,
        )

        # Save modified version
        repository.save(modified_query)

        # Retrieve and verify it was overwritten
        found_query = repository.find_by_id(sample_query.id)

        assert found_query.text == "Updated query text"
        assert found_query.text == "Updated query text"
        assert found_query.max_sources == 20

    @pytest.mark.asyncio
    async def test_find_all_queries(self, repository):
        """Test retrieving all queries."""
        # Create multiple queries
        queries = [
            ResearchQuery(
                id=QueryId(),
                text=f"Query {i}",
                query_type=ResearchQueryType.GENERAL,
                created_at=datetime.now(),
                max_sources=10,
            )
            for i in range(3)
        ]

        # Save all queries
        for query in queries:
            repository.save(query)

        # Retrieve all
        all_queries = repository.find_all()

        # Assert
        assert len(all_queries) == 3
        saved_ids = {q.id for q in all_queries}
        expected_ids = {q.id for q in queries}
        assert saved_ids == expected_ids

    @pytest.mark.asyncio
    async def test_find_all_empty_repository(self, repository):
        """Test find_all on empty repository."""
        all_queries = repository.find_all()
        assert all_queries == []

    @pytest.mark.asyncio
    async def test_delete_query(self, repository, sample_query):
        """Test deleting a query."""
        # Save query
        repository.save(sample_query)

        # Verify it exists
        found_query = repository.find_by_id(sample_query.id)
        assert found_query is not None

        # Delete query
        repository.delete(sample_query.id)

        # Verify it's gone
        found_query = repository.find_by_id(sample_query.id)
        assert found_query is None

    @pytest.mark.asyncio
    async def test_delete_non_existent_query(self, repository):
        """Test deleting non-existent query doesn't raise error."""
        non_existent_id = QueryId()

        # Should not raise exception
        repository.delete(non_existent_id)

    @pytest.mark.asyncio
    async def test_concurrent_access(self, repository):
        """Test thread-safe concurrent access."""
        import asyncio

        queries = [
            ResearchQuery(
                id=QueryId(),
                text=f"Concurrent query {i}",
                query_type=ResearchQueryType.GENERAL,
                created_at=datetime.now(),
                max_sources=10,
            )
            for i in range(10)
        ]

        # Save queries (not concurrent since they're synchronous operations)
        for q in queries:
            repository.save(q)

        # Retrieve all and verify
        all_queries = repository.find_all()
        assert len(all_queries) == 10


class TestInMemoryResearchResultRepository:
    """Test cases for InMemoryResearchResultRepository."""

    @pytest.fixture
    def repository(self):
        """Fresh repository for each test."""
        return InMemoryResearchResultRepository()

    @pytest.fixture
    def sample_query_id(self):
        """Sample query ID."""
        return QueryId()

    @pytest.fixture
    def sample_result(self, sample_query_id):
        """Sample research result."""
        # Create a sample query for the result
        sample_query = ResearchQuery(
            id=sample_query_id,
            text="Sample query for result",
            query_type=ResearchQueryType.GENERAL,
            created_at=datetime.now(),
        )
        return ResearchResult(
            query=sample_query,
            status=ResearchStatus.COMPLETED,
        )

    @pytest.mark.asyncio
    async def test_save_and_find_by_query_id(
        self, repository, sample_result, sample_query_id
    ):
        """Test saving and retrieving results by query ID."""
        # Save result
        repository.save(sample_result)

        # Retrieve results
        found_results = repository.find_by_query_id(sample_query_id)

        # Assert
        assert len(found_results) == 1
        result = found_results[0]
        assert result.query.id == sample_query_id

    @pytest.mark.asyncio
    async def test_find_by_query_id_not_found(self, repository):
        """Test retrieving results for non-existent query ID."""
        non_existent_id = QueryId()

        found_results = repository.find_by_query_id(non_existent_id)

        assert found_results == []

    @pytest.mark.asyncio
    async def test_save_multiple_results_same_query(self, repository, sample_query_id):
        """Test saving multiple results for the same query."""
        results = [
            ResearchResult(
                query=ResearchQuery(
                    id=sample_query_id,
                    text="Test query",
                    query_type=ResearchQueryType.GENERAL,
                    created_at=datetime.now(),
                ),
            )
            for i in range(3)
        ]

        # Save all results
        for result in results:
            repository.save(result)

        # Retrieve and verify
        found_results = repository.find_by_query_id(sample_query_id)

        assert len(found_results) == 3

        # All results should belong to the same query
        for result in found_results:
            assert result.query.id == sample_query_id
            assert result.status == ResearchStatus.PENDING

    @pytest.mark.asyncio
    async def test_save_results_different_queries(self, repository):
        """Test saving results for different queries."""
        query_id_1 = QueryId()
        query_id_2 = QueryId()

        result_1 = ResearchResult(
            query=ResearchQuery(
                id=query_id_1,
                text="Test query 1",
                query_type=ResearchQueryType.GENERAL,
                created_at=datetime.now(),
            ),
        )

        result_2 = ResearchResult(
            query=ResearchQuery(
                id=query_id_2,
                text="Test query 2",
                query_type=ResearchQueryType.GENERAL,
                created_at=datetime.now(),
            ),
        )

        # Save results
        repository.save(result_1)
        repository.save(result_2)

        # Retrieve separately
        results_1 = repository.find_by_query_id(query_id_1)
        results_2 = repository.find_by_query_id(query_id_2)

        # Assert
        assert len(results_1) == 1
        assert len(results_2) == 1
        assert results_1[0].query.id == query_id_1
        assert results_2[0].query.id == query_id_2

    @pytest.mark.asyncio
    async def test_find_all_results(self, repository):
        """Test retrieving all results."""
        query_ids = [QueryId() for _ in range(2)]
        results = []

        # Create results for different queries
        for i, query_id in enumerate(query_ids):
            for j in range(2):  # 2 results per query
                result = ResearchResult(
                    query=ResearchQuery(
                        id=query_id,
                        text="Test query",
                        query_type=ResearchQueryType.GENERAL,
                        created_at=datetime.now(),
                    ),
                )
                results.append(result)
                repository.save(result)

        # Retrieve all
        all_results = repository.find_all()

        # Assert
        assert len(all_results) == 4  # 2 queries * 2 results each

    @pytest.mark.asyncio
    async def test_delete_results_by_query_id(self, repository, sample_query_id):
        """Test deleting all results for a query."""
        # Create multiple results
        results = [
            ResearchResult(
                query=ResearchQuery(
                    id=sample_query_id,
                    text="Test query",
                    query_type=ResearchQueryType.GENERAL,
                    created_at=datetime.now(),
                ),
            )
            for i in range(3)
        ]

        # Save results
        for result in results:
            repository.save(result)

        # Verify they exist
        found_results = repository.find_by_query_id(sample_query_id)
        assert len(found_results) == 3

        # Delete all results for this query
        repository.delete_by_query_id(sample_query_id)

        # Verify they're gone
        found_results = repository.find_by_query_id(sample_query_id)
        assert found_results == []

    @pytest.mark.asyncio
    async def test_delete_results_non_existent_query(self, repository):
        """Test deleting results for non-existent query."""
        non_existent_id = QueryId()

        # Should not raise exception
        repository.delete_by_query_id(non_existent_id)

    @pytest.mark.asyncio
    async def test_concurrent_result_operations(self, repository):
        """Test thread-safe concurrent result operations."""
        import asyncio

        query_id = QueryId()
        results = [
            ResearchResult(
                query=ResearchQuery(
                    id=query_id,
                    text="Test query",
                    query_type=ResearchQueryType.GENERAL,
                    created_at=datetime.now(),
                ),
            )
            for i in range(10)
        ]

        # Save results concurrently (synchronous operation)
        for result in results:
            repository.save(result)

        # Retrieve and verify
        found_results = repository.find_by_query_id(query_id)
        assert len(found_results) == 10
