"""
🧪 Unit Tests for Domain Layer - Educational Edition

This file contains unit tests for our core domain entities. These are the
fundamental building blocks of our AI Deep Research system.

🎯 What are Unit Tests?
Unit tests check individual pieces (units) of code in isolation - like testing
each ingredient before baking a cake. We test each class and function by itself
to make sure it works correctly before combining it with other parts.

🏗️ What is the Domain Layer?
In Clean Architecture, the domain layer contains our core business logic -
the essential rules and concepts that define what our application does.
Think of it as the "heart" of our application that doesn't depend on
databases, web interfaces, or external services.

🔍 What We're Testing Here:
- QueryId: Unique identifiers for research queries (like ID cards)
- ResearchQuery: Questions users ask our AI system
- ResearchResult: Answers and data our system finds
- ResearchSource: Where we found information (citations)
- Various enums and exceptions that help our system work correctly

💡 Learning Goals:
- Understand how to test value objects and entities
- Learn about testing equality and validation
- See how to test enums and error handling
- Practice the Arrange-Act-Assert pattern
"""

from datetime import datetime
from uuid import UUID

import pytest

from src.domain.entities import (
    DomainException,
    InvalidQueryException,
    QueryId,
    QueryNotFoundError,
    ResearchQuery,
    ResearchQueryType,
    ResearchResult,
    ResearchSource,
    ResearchStatus,
    SourceType,
)


class TestQueryId:
    """
    🆔 Test cases for QueryId value object.

    QueryId is like a unique ID card for each research question.
    Just like every student has a unique student ID, every research
    query gets a unique QueryId so we can track and manage it.

    🎓 Educational Focus:
    - Learn about UUIDs (Universally Unique Identifiers)
    - Understand value object testing patterns
    - Practice testing equality and immutability
    """

    def test_query_id_generation(self):
        """
        🧪 Test that QueryId generates valid UUIDs.

        This test ensures our QueryId can create unique identifiers.

        🎯 What we're testing:
        - Can we create a new QueryId? (instantiation)
        - Is the ID actually a UUID? (type checking)
        - Can we convert it to a string? (string representation)

        💡 Why this matters:
        Every research query needs a unique ID so we can tell them apart,
        just like how every book in a library has a unique call number.
        """
        # ARRANGE: Set up what we need (nothing needed here)

        # ACT: Create a new QueryId
        query_id = QueryId()

        # ASSERT: Check that it worked correctly
        assert isinstance(query_id.value, UUID)  # Should be a UUID type
        assert str(query_id.value)  # Should be convertible to string
        # UUIDs look like: "12345678-1234-5678-9012-123456789abc"

    def test_query_id_equality(self):
        """
        ✅ Test QueryId equality comparison.

        This test checks if two QueryIds with the same value are considered equal.

        🎯 What we're testing:
        - Two QueryIds with same UUID should be equal (==)
        - Two QueryIds with different UUIDs should not be equal (!=)

        💡 Real-world analogy:
        If two students have the same student ID number, they should be
        considered the "same student" by the system. But if they have
        different IDs, they're different students.
        """
        # ARRANGE: Create test data with known UUIDs
        uuid_val = UUID("12345678-1234-5678-9012-123456789abc")
        query_id1 = QueryId(uuid_val)  # First ID with specific UUID
        query_id2 = QueryId(uuid_val)  # Second ID with same UUID
        query_id3 = QueryId()  # Third ID with random UUID

        # ACT & ASSERT: Test equality relationships
        assert query_id1 == query_id2  # Same UUID = equal
        assert query_id1 != query_id3  # Different UUID = not equal

    def test_query_id_from_string(self):
        """
        🔄 Test creating QueryId from UUID.

        This test verifies we can create a QueryId from an existing UUID value.

        🎯 What we're testing:
        - Can we create a QueryId with a specific UUID?
        - Does it store the UUID correctly?

        💡 Why this is useful:
        Sometimes we need to recreate a QueryId from a stored value,
        like when loading a saved research query from a database.
        """
        # ARRANGE: Create a specific UUID to use
        uuid_val = UUID("12345678-1234-5678-9012-123456789abc")

        # ACT: Create QueryId with that specific UUID
        query_id = QueryId(uuid_val)

        assert query_id.value == uuid_val

    def test_query_id_repr(self):
        """Test QueryId string representation."""
        uuid_val = UUID("12345678-1234-5678-9012-123456789abc")
        query_id = QueryId(uuid_val)

        assert str(query_id) == str(uuid_val)
        assert "QueryId" in repr(query_id)


class TestResearchQuery:
    """Test cases for ResearchQuery entity."""

    def test_research_query_creation(self):
        """Test creating a valid research query."""
        query_id = QueryId()
        query = ResearchQuery(
            id=query_id,
            text="What is artificial intelligence?",
            query_type=ResearchQueryType.GENERAL,
            created_at=datetime.now(),
            max_sources=10,
        )

        assert query.id == query_id
        assert query.text == "What is artificial intelligence?"
        assert query.query_type == ResearchQueryType.GENERAL
        assert query.max_sources == 10
        assert isinstance(query.created_at, datetime)

    def test_research_query_validation_empty_text(self):
        """Test that empty query text raises validation error."""
        with pytest.raises(ValueError):
            ResearchQuery(
                id=QueryId(),
                text="",
                query_type=ResearchQueryType.GENERAL,
                created_at=datetime.now(),
            )

    def test_research_query_validation_negative_max_results(self):
        """Test that negative max_sources raises validation error."""
        with pytest.raises(ValueError):
            ResearchQuery(
                id=QueryId(),
                text="Valid query",
                query_type=ResearchQueryType.GENERAL,
                created_at=datetime.now(),
                max_sources=-1,
            )

    def test_research_query_validation_zero_max_results(self):
        """Test that zero max_sources raises validation error."""
        with pytest.raises(ValueError):
            ResearchQuery(
                id=QueryId(),
                text="Valid query",
                query_type=ResearchQueryType.GENERAL,
                created_at=datetime.now(),
                max_sources=0,
            )

    def test_research_query_default_values(self):
        """Test research query with default values."""
        query_id = QueryId()
        query = ResearchQuery(
            id=query_id,
            text="Simple query",
            query_type=ResearchQueryType.GENERAL,
            created_at=datetime.now(),
        )

        assert query.max_sources == 10
        assert query.include_web_search is True
        assert query.include_academic_sources is True

    def test_research_query_equality(self):
        """Test research query equality based on all fields."""
        query_id = QueryId()
        created_time = datetime.now()

        query1 = ResearchQuery(
            id=query_id,
            text="Query 1",
            query_type=ResearchQueryType.GENERAL,
            created_at=created_time,
        )

        query2 = ResearchQuery(
            id=query_id,
            text="Query 1",  # Same text
            query_type=ResearchQueryType.GENERAL,  # Same type
            created_at=created_time,  # Same time
        )

        query3 = ResearchQuery(
            id=QueryId(),
            text="Query 1",
            query_type=ResearchQueryType.GENERAL,
            created_at=created_time,
        )

        # Same values means equal (dataclass equality)
        assert query1 == query2
        # Different id means not equal
        assert query1 != query3


class TestResearchResult:
    """Test cases for ResearchResult entity."""

    def test_research_result_creation(self):
        """Test creating a valid research result."""
        query = ResearchQuery(
            id=QueryId(),
            text="What is machine learning?",
            query_type=ResearchQueryType.TECHNICAL,
            created_at=datetime.now(),
        )
        result = ResearchResult(query=query)

        assert result.query == query
        assert result.status == ResearchStatus.PENDING
        assert isinstance(result.created_at, datetime)
        assert result.sources == []
        assert result.synthesis == ""

    def test_research_result_add_source(self):
        """Test adding sources to result."""
        query = ResearchQuery(
            id=QueryId(),
            text="AI research",
            query_type=ResearchQueryType.ACADEMIC,
            created_at=datetime.now(),
            max_sources=2,
        )
        result = ResearchResult(query=query)

        source = ResearchSource(
            url="https://example.com", title="AI Paper", source_type=SourceType.ARXIV
        )

        result.add_source(source)
        assert len(result.sources) == 1
        assert result.sources[0] == source

    def test_research_result_max_sources_validation(self):
        """Test that adding sources beyond max_sources raises error."""
        query = ResearchQuery(
            id=QueryId(),
            text="AI research",
            query_type=ResearchQueryType.ACADEMIC,
            created_at=datetime.now(),
            max_sources=1,
        )
        result = ResearchResult(query=query)

        source1 = ResearchSource(url="https://example1.com", title="Paper 1")
        source2 = ResearchSource(url="https://example2.com", title="Paper 2")

        result.add_source(source1)

        with pytest.raises(ValueError):
            result.add_source(source2)

    def test_research_result_mark_completed(self):
        """Test marking result as completed."""
        query = ResearchQuery(
            id=QueryId(),
            text="Test query",
            query_type=ResearchQueryType.GENERAL,
            created_at=datetime.now(),
        )
        result = ResearchResult(query=query)

        synthesis = "Key insights from research"
        findings = ["Finding 1", "Finding 2"]

        result.mark_completed(synthesis, findings)

        assert result.status == ResearchStatus.COMPLETED
        assert result.synthesis == synthesis
        assert result.key_findings == findings
        assert result.completed_at is not None

    def test_research_result_mark_failed(self):
        """Test marking result as failed."""
        query = ResearchQuery(
            id=QueryId(),
            text="Test query",
            query_type=ResearchQueryType.GENERAL,
            created_at=datetime.now(),
        )
        result = ResearchResult(query=query)

        error_msg = "Network timeout"
        result.mark_failed(error_msg)

        assert result.status == ResearchStatus.FAILED
        assert result.error_message == error_msg
        assert result.completed_at is not None


class TestResearchSource:
    """Test cases for ResearchSource entity."""

    def test_research_source_creation(self):
        """Test creating a valid research source."""
        source = ResearchSource(
            url="https://academic.example.com",
            title="Machine Learning Research Paper",
            source_type=SourceType.ARXIV,
            relevance_score=0.95,
        )

        assert source.url == "https://academic.example.com"
        assert source.title == "Machine Learning Research Paper"
        assert source.source_type == SourceType.ARXIV
        assert source.relevance_score == 0.95
        assert isinstance(source.id, UUID)

    def test_research_source_default_values(self):
        """Test research source with default values."""
        source = ResearchSource()

        assert source.url == ""
        assert source.title == ""
        assert source.source_type == SourceType.WEB
        assert source.relevance_score == 0.0
        assert source.citation_count == 0

    def test_research_source_validation_invalid_relevance_score(self):
        """Test that invalid relevance scores raise validation errors."""
        # Test score below 0
        with pytest.raises(ValueError):
            ResearchSource(relevance_score=-0.1)

        # Test score above 1
        with pytest.raises(ValueError):
            ResearchSource(relevance_score=1.1)

    def test_research_source_validation_negative_citation_count(self):
        """Test that negative citation count raises validation error."""
        with pytest.raises(ValueError):
            ResearchSource(citation_count=-1)

    def test_research_source_is_academic_source(self):
        """Test identifying academic sources."""
        arxiv_source = ResearchSource(source_type=SourceType.ARXIV)
        scholar_source = ResearchSource(source_type=SourceType.GOOGLE_SCHOLAR)
        web_source = ResearchSource(source_type=SourceType.WEB)

        assert arxiv_source.is_academic_source() is True
        assert scholar_source.is_academic_source() is True
        assert web_source.is_academic_source() is False

    def test_research_source_has_sufficient_content(self):
        """Test content sufficiency checks."""
        # Source with sufficient content
        source_with_content = ResearchSource(content="a" * 100)
        assert source_with_content.has_sufficient_content() is True

        # Source with sufficient abstract
        source_with_abstract = ResearchSource(abstract="a" * 50)
        assert source_with_abstract.has_sufficient_content() is True

        # Source with insufficient content
        source_insufficient = ResearchSource(content="short", abstract="short")
        assert source_insufficient.has_sufficient_content() is False

    def test_research_source_get_display_title(self):
        """Test display title generation."""
        # Source with title
        source_with_title = ResearchSource(
            title="Great Paper", url="https://example.com"
        )
        assert source_with_title.get_display_title() == "Great Paper"

        # Source without title
        source_no_title = ResearchSource(url="https://example.com")
        assert source_no_title.get_display_title() == "Source from https://example.com"


class TestDomainExceptions:
    """Test cases for domain exceptions."""

    def test_domain_exception_hierarchy(self):
        """Test that domain exceptions inherit correctly."""
        assert issubclass(InvalidQueryException, DomainException)
        assert issubclass(DomainException, Exception)

    def test_invalid_query_exception(self):
        """Test InvalidQueryException creation and message."""
        message = "Query text cannot be empty"
        error = InvalidQueryException(message)

        assert str(error) == message
