#!/usr/bin/env python3
"""
AI Deep Research MCP - Retriever Component

Handles semantic search and ranking of retrieved chunks from the vector store.
Provides advanced search capabilities including filtering, re-ranking, and
hybrid search combining semantic and keyword matching.

REFACTOR PHASE: Production-ready implementation with improved code quality
"""

import time
import threading
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union, Set
import numpy as np
from concurrent.futures import ThreadPoolExecutor
import logging

from .vector_store import VectorStore, SearchResult


# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class RetrievalResult:
    """
    Represents a search result with ranking and metadata.
    
    This dataclass encapsulates all information about a retrieved document chunk,
    including its relevance score, ranking position, and reasoning for selection.
    """
    chunk_id: str
    text: str
    source_url: str
    metadata: Dict[str, Any]
    relevance_score: float
    rank: int
    reasoning: Optional[str] = None
    
    def __post_init__(self):
        """Validate result data to ensure data integrity."""
        if not self.chunk_id or not self.text or not self.source_url:
            raise ValueError("chunk_id, text, and source_url are required")
        
        if not (0 <= self.relevance_score <= 1):
            raise ValueError("relevance_score must be between 0 and 1")
        
        if self.rank < 1:
            raise ValueError("rank must be >= 1")


@dataclass
class SearchContext:
    """
    Configuration object for search operations.
    
    Encapsulates all search parameters in a single object for cleaner API usage
    and easier parameter management across complex search workflows.
    """
    query: str
    max_results: int = 10
    relevance_threshold: float = 0.0
    filters: Optional[Dict[str, Any]] = None
    rerank: bool = False
    include_reasoning: bool = False
    hybrid_search: bool = False
    
    def __post_init__(self):
        """Validate search context parameters."""
        if not self.query or not self.query.strip():
            raise ValueError("query cannot be empty")
        
        if self.max_results <= 0:
            raise ValueError("max_results must be positive")
        
        if not (0 <= self.relevance_threshold <= 1):
            raise ValueError("relevance_threshold must be between 0 and 1")


class Retriever:
    """
    Semantic search and ranking component for the AI Deep Research system.
    
    This class provides advanced search capabilities including:
    - Semantic similarity search via vector store integration
    - Result filtering and ranking with customizable algorithms
    - Hybrid search combining semantic and keyword matching
    - Performance monitoring and concurrent search support
    - Extensible re-ranking mechanisms for relevance optimization
    
    The retriever acts as the bridge between raw vector search results and
    the final ranked, filtered results presented to users or downstream components.
    """
    
    # Class constants for configuration
    DEFAULT_SEARCH_MULTIPLIER = 2  # Get 2x results for filtering
    MAX_KEYWORD_BOOST = 0.3        # Maximum boost from keyword matching
    KEYWORD_BOOST_PER_MATCH = 0.1  # Boost per keyword match
    
    def __init__(
        self,
        vector_store: VectorStore,
        enable_reranking: bool = False,
        hybrid_search: bool = False,
        track_performance: bool = False
    ):
        """
        Initialize the Retriever with configuration options.
        
        Args:
            vector_store: Vector database for semantic search operations
            enable_reranking: Whether to enable advanced re-ranking algorithms
            hybrid_search: Whether to enable hybrid semantic+keyword search by default
            track_performance: Whether to track and expose search performance metrics
        """
        self.vector_store = vector_store
        self.enable_reranking = enable_reranking
        self.hybrid_search = hybrid_search
        self.track_performance = track_performance
        
        # Initialize thread-safe performance tracking
        self._search_lock = threading.Lock()
        self._reset_performance_metrics()
    
    def search(
        self,
        query: str,
        max_results: int = 10,
        relevance_threshold: float = 0.0,
        filters: Optional[Dict[str, Any]] = None,
        hybrid_search: Optional[bool] = None
    ) -> List[RetrievalResult]:
        """
        Perform semantic search for relevant chunks with advanced filtering.
        
        This is the main search interface that combines vector similarity search
        with optional hybrid scoring, relevance filtering, and result ranking.
        
        Args:
            query: Search query string (cannot be empty)
            max_results: Maximum number of results to return (must be > 0)
            relevance_threshold: Minimum relevance score (0-1) for inclusion
            filters: Optional metadata filters for result filtering
            hybrid_search: Override instance hybrid search setting
            
        Returns:
            List of ranked RetrievalResult objects, ordered by relevance
            
        Raises:
            ValueError: If query is invalid or parameters are out of range
        """
        # Validate inputs with descriptive error messages
        self._validate_search_parameters(query, max_results, relevance_threshold)
        
        start_time = time.time()
        
        try:
            # Determine search strategy
            use_hybrid = hybrid_search if hybrid_search is not None else self.hybrid_search
            
            # Perform initial vector search with buffer for filtering
            search_results = self._perform_vector_search(query, max_results, filters)
            
            # Apply hybrid scoring if enabled
            if use_hybrid:
                search_results = self._apply_hybrid_scoring(query, search_results)
            
            # Apply relevance threshold filtering
            filtered_results = self._filter_by_relevance(search_results, relevance_threshold)
            
            # Limit to requested number of results
            limited_results = filtered_results[:max_results]
            
            # Convert to ranked RetrievalResults
            ranked_results = self.rank_results(limited_results, query)
            
            # Track performance metrics if enabled
            if self.track_performance:
                self._update_performance_metrics(
                    search_time=time.time() - start_time,
                    results_count=len(ranked_results)
                )
            
            return ranked_results
            
        except Exception as e:
            logger.error(f"Search failed for query '{query[:50]}...': {e}")
            return []
    
    def search_with_context(self, context: SearchContext) -> List[RetrievalResult]:
        """
        Perform search using a SearchContext configuration object.
        
        This method provides a more structured way to perform complex searches
        with multiple configuration options, especially useful for programmatic
        search operations or when search parameters need to be passed around.
        
        Args:
            context: SearchContext object containing all search parameters
            
        Returns:
            List of ranked RetrievalResult objects with optional enhancements
        """
        # Perform basic search with context parameters
        results = self.search(
            query=context.query,
            max_results=context.max_results,
            relevance_threshold=context.relevance_threshold,
            filters=context.filters,
            hybrid_search=context.hybrid_search
        )
        
        # Add reasoning explanations if requested
        if context.include_reasoning:
            self._add_reasoning_to_results(results, context.query)
        
        # Apply advanced re-ranking if requested and enabled
        if context.rerank and self.enable_reranking:
            results = self._advanced_rerank(results, context.query)
        
        return results
    
    def rank_results(
        self,
        search_results: List[SearchResult],
        query: str
    ) -> List[RetrievalResult]:
        """
        Convert SearchResults to RetrievalResults with proper ranking.
        
        This method handles the transformation from raw vector search results
        to the structured RetrievalResult format with ranking information.
        
        Args:
            search_results: Raw search results from vector store
            query: Original search query for context
            
        Returns:
            List of ranked RetrievalResult objects, sorted by relevance
        """
        # Sort by relevance score in descending order
        sorted_results = sorted(search_results, key=lambda x: x.score, reverse=True)
        
        # Convert to RetrievalResults with rank assignment
        ranked_results = []
        for rank, result in enumerate(sorted_results, 1):
            retrieval_result = RetrievalResult(
                chunk_id=result.id,
                text=result.text,
                source_url=result.source_url,
                metadata=result.metadata,
                relevance_score=result.score,
                rank=rank,
                reasoning=None  # Added later if requested
            )
            ranked_results.append(retrieval_result)
        
        return ranked_results
    
    def get_performance_metrics(self) -> Dict[str, float]:
        """
        Get current performance metrics for monitoring and optimization.
        
        Returns:
            Dictionary containing performance metrics:
            - search_time: Time taken for last search
            - total_searches: Total number of searches performed
            - avg_results_per_search: Average number of results returned
            - total_search_time: Cumulative search time
        """
        with self._search_lock:
            return self._performance_metrics.copy()
    
    def clear_performance_metrics(self):
        """Reset all performance metrics to initial state."""
        with self._search_lock:
            self._reset_performance_metrics()
    
    # Private helper methods for improved code organization
    
    def _validate_search_parameters(self, query: str, max_results: int, relevance_threshold: float):
        """Validate search parameters with descriptive error messages."""
        if not query or query.strip() == "":
            raise ValueError("Query cannot be empty")
        
        if query is None:
            raise ValueError("Query cannot be None")
        
        if max_results <= 0:
            raise ValueError("max_results must be > 0")
        
        if not (0 <= relevance_threshold <= 1):
            raise ValueError("relevance_threshold must be between 0 and 1")
    
    def _perform_vector_search(
        self,
        query: str,
        max_results: int,
        filters: Optional[Dict[str, Any]]
    ) -> List[SearchResult]:
        """Perform the actual vector search with proper error handling."""
        return self.vector_store.search_by_text(
            query_text=query,
            top_k=max_results * self.DEFAULT_SEARCH_MULTIPLIER,
            filters=filters
        )
    
    def _filter_by_relevance(
        self,
        search_results: List[SearchResult],
        threshold: float
    ) -> List[SearchResult]:
        """Filter search results by relevance threshold."""
        return [result for result in search_results if result.score >= threshold]
    
    def _apply_hybrid_scoring(
        self,
        query: str,
        search_results: List[SearchResult]
    ) -> List[SearchResult]:
        """
        Apply hybrid scoring combining semantic and keyword matching.
        
        This method enhances semantic similarity scores with keyword matching
        bonuses to improve relevance for queries with specific terms.
        
        Args:
            query: Original search query
            search_results: Results from semantic search
            
        Returns:
            Enhanced search results with hybrid scores
        """
        query_words = self._extract_query_words(query)
        
        for result in search_results:
            keyword_boost = self._calculate_keyword_boost(query_words, result.text)
            hybrid_score = min(result.score + keyword_boost, 1.0)
            result.score = hybrid_score
        
        return search_results
    
    def _extract_query_words(self, query: str) -> Set[str]:
        """Extract meaningful words from query for keyword matching."""
        # Simple word extraction - could be enhanced with NLP
        return set(word.lower().strip() for word in query.split() if len(word) > 2)
    
    def _calculate_keyword_boost(self, query_words: Set[str], text: str) -> float:
        """Calculate keyword matching boost for hybrid scoring."""
        text_words = set(word.lower().strip() for word in text.split())
        keyword_matches = len(query_words.intersection(text_words))
        return min(keyword_matches * self.KEYWORD_BOOST_PER_MATCH, self.MAX_KEYWORD_BOOST)
    
    def _add_reasoning_to_results(self, results: List[RetrievalResult], query: str):
        """Add human-readable reasoning to search results."""
        for result in results:
            result.reasoning = self._generate_reasoning(query, result)
    
    def _generate_reasoning(self, query: str, result: RetrievalResult) -> str:
        """
        Generate human-readable reasoning for result selection.
        
        Args:
            query: Original search query
            result: RetrievalResult to explain
            
        Returns:
            Human-readable explanation of why this result was selected
        """
        # Categorize relevance score
        if result.relevance_score > 0.8:
            score_desc = "high"
        elif result.relevance_score > 0.5:
            score_desc = "moderate"
        else:
            score_desc = "low"
        
        reasoning = (f"Ranked #{result.rank} with {score_desc} semantic similarity "
                    f"({result.relevance_score:.2f}) to query")
        
        # Check for keyword matches to enhance explanation
        query_words = self._extract_query_words(query)
        text_words = self._extract_query_words(result.text)
        keyword_matches = query_words.intersection(text_words)
        
        if keyword_matches:
            # Show up to 3 key matching terms
            match_list = list(keyword_matches)[:3]
            reasoning += f". Contains key terms: {', '.join(match_list)}"
        
        return reasoning
    
    def _advanced_rerank(
        self,
        results: List[RetrievalResult],
        query: str
    ) -> List[RetrievalResult]:
        """
        Apply advanced re-ranking algorithms for improved relevance.
        
        This method implements sophisticated re-ranking strategies that go
        beyond simple similarity scores to improve result quality.
        
        Args:
            results: Initial ranked results
            query: Original query for context
            
        Returns:
            Re-ranked results with updated scores and positions
        """
        query_lower = query.lower()
        
        # Apply phrase matching boost
        for result in results:
            if query_lower in result.text.lower():
                # Boost exact phrase matches significantly
                result.relevance_score = min(result.relevance_score + 0.2, 1.0)
        
        # Re-sort by updated scores and update ranks
        results.sort(key=lambda x: x.relevance_score, reverse=True)
        for i, result in enumerate(results, 1):
            result.rank = i
        
        return results
    
    def _update_performance_metrics(self, search_time: float, results_count: int):
        """Update performance tracking metrics in a thread-safe manner."""
        with self._search_lock:
            self._performance_metrics["total_searches"] += 1
            self._performance_metrics["total_search_time"] += search_time
            self._performance_metrics["total_results_returned"] += results_count
            self._performance_metrics["search_time"] = search_time
            
            # Recalculate averages
            if self._performance_metrics["total_searches"] > 0:
                self._performance_metrics["avg_results_per_search"] = (
                    self._performance_metrics["total_results_returned"] / 
                    self._performance_metrics["total_searches"]
                )
    
    def _reset_performance_metrics(self):
        """Initialize/reset performance metrics to default values."""
        self._performance_metrics = {
            "total_searches": 0,
            "total_search_time": 0.0,
            "total_results_returned": 0,
            "avg_results_per_search": 0.0,
            "search_time": 0.0
        }
