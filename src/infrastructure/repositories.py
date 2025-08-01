"""
In-Memory Repository Implementations

These provide simple in-memory storage for development and testing.
In production, these would be replaced with database implementations.
"""

from threading import Lock
from typing import Dict, List, Optional

from ..domain.entities import (
    QueryId,
    ResearchQuery,
    ResearchResult,
    ResearchStatus,
)


class InMemoryResearchQueryRepository:
    """In-memory implementation of ResearchQueryRepository."""

    def __init__(self):
        self._queries: Dict[str, ResearchQuery] = {}
        self._lock = Lock()

    def save(self, query: ResearchQuery) -> None:
        """Save a research query."""
        with self._lock:
            self._queries[str(query.id)] = query

    def find_by_id(self, query_id: QueryId) -> Optional[ResearchQuery]:
        """Find a query by its ID."""
        with self._lock:
            return self._queries.get(str(query_id))

    def find_by_requester(self, requester_id: str) -> List[ResearchQuery]:
        """Find queries by requester."""
        with self._lock:
            return [
                query
                for query in self._queries.values()
                if query.requester_id == requester_id
            ]

    def find_all(self) -> List[ResearchQuery]:
        """Find all queries."""
        with self._lock:
            return list(self._queries.values())

    def delete(self, query_id: QueryId) -> None:
        """Delete a query by ID."""
        with self._lock:
            self._queries.pop(str(query_id), None)


class InMemoryResearchResultRepository:
    """In-memory implementation of ResearchResultRepository."""

    def __init__(self):
        self._results: Dict[str, List[ResearchResult]] = {}
        self._lock = Lock()

    def save(self, result: ResearchResult) -> None:
        """Save research results."""
        with self._lock:
            query_id_str = str(result.query.id)
            if query_id_str not in self._results:
                self._results[query_id_str] = []
            self._results[query_id_str].append(result)

    def find_by_query_id(self, query_id: QueryId) -> List[ResearchResult]:
        """Find results by query ID."""
        with self._lock:
            return self._results.get(str(query_id), [])

    def find_completed_results(
        self, limit: int = 10, offset: int = 0
    ) -> List[ResearchResult]:
        """Find completed research results."""
        with self._lock:
            all_results = []
            for results_list in self._results.values():
                all_results.extend(results_list)

            completed = [
                result
                for result in all_results
                if result.status == ResearchStatus.COMPLETED
            ]
            # Sort by completion time, newest first
            completed.sort(key=lambda r: r.completed_at or r.created_at, reverse=True)
            return completed[offset : offset + limit]

    def find_all(self) -> List[ResearchResult]:
        """Find all results."""
        with self._lock:
            all_results = []
            for results_list in self._results.values():
                all_results.extend(results_list)
            return all_results

    def delete_by_query_id(self, query_id: QueryId) -> None:
        """Delete results by query ID."""
        with self._lock:
            self._results.pop(str(query_id), None)
