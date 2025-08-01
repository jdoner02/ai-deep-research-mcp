"""
🔍 QUERY ANALYZER - Educational Implementation

This module demonstrates how to build a sophisticated query analysis system
using professional software development practices. Perfect for middle school
students learning about AI and natural language processing!

WHAT DOES THIS MODULE DO?
========================
This Query Analyzer can:
1. 📝 Classify different types of research questions (environmental, technology, medical, general)
2. ⏰ Detect if users want recent or historical information
3. 🎯 Suggest appropriate sources for different query types
4. 📊 Provide confidence scores for classifications
5. 🔍 Extract relevant keywords from queries

WHY IS THIS IMPORTANT?
=====================
In AI research systems, understanding what users are really asking for is crucial.
This module shows how professional programmers break down complex problems into
manageable pieces and build robust, testable solutions.

PROFESSIONAL CONCEPTS DEMONSTRATED:
==================================
- Object-Oriented Programming (classes and methods)
- Enums for type safety
- Dataclasses for structured data
- Regular expressions for text processing
- Comprehensive error handling
- Professional documentation
- Test-driven development principles

REAL-WORLD APPLICATIONS:
=======================
- Search engines use similar logic to understand queries
- Virtual assistants like Siri and Alexa use query classification
- Research databases use this to recommend relevant papers
- Customer service chatbots use this to route questions

Let's explore how professional programmers build production-ready software! 🚀
"""

from enum import Enum
from dataclasses import dataclass
from typing import Dict, List, Optional
import re
from abc import ABC, abstractmethod


class QueryType(Enum):
    """
    📂 Query Types - Different Categories of Research Questions

    Enums are a professional way to define fixed sets of values.
    This prevents typos and makes code more reliable!

    ENVIRONMENTAL: Questions about climate, nature, sustainability
    TECHNOLOGY: Questions about computers, AI, software, gadgets
    MEDICAL: Questions about health, diseases, treatments
    GENERAL: Questions that don't fit other categories
    """

    ENVIRONMENTAL = "environmental"
    TECHNOLOGY = "technology"
    MEDICAL = "medical"
    GENERAL = "general"

    def __str__(self) -> str:
        """Make the enum print nicely for students to understand"""
        return self.value.title()


class TimePreference(Enum):
    """
    ⏰ Time Preferences - When Information Should Be From

    RECENT: User wants the latest, newest information
    HISTORICAL: User wants information from the past
    ANY: User doesn't care about timing
    """

    RECENT = "recent"
    HISTORICAL = "historical"
    ANY = "any"

    def __str__(self) -> str:
        return self.value.title()


@dataclass
class QueryAnalysis:
    """
    📊 Query Analysis Results - Complete Information About a Query

    Dataclasses are a modern Python way to create classes that hold data.
    They automatically generate useful methods like __init__ and __repr__!

    This class holds all the information we discover about a user's query.
    """

    query_type: QueryType
    time_preference: TimePreference
    confidence: float  # How sure are we? (0.0 to 1.0)
    keywords_found: List[str]  # Which keywords helped us decide?
    suggested_sources: List[str]  # Which websites would be good for this query?
    original_query: str  # The original question the user asked

    def __str__(self) -> str:
        """Make the results easy to read for students"""
        return (
            f"Query: '{self.original_query}'\n"
            f"Type: {self.query_type} (confidence: {self.confidence:.1%})\n"
            f"Time Preference: {self.time_preference}\n"
            f"Keywords: {', '.join(self.keywords_found) if self.keywords_found else 'None'}\n"
            f"Suggested Sources: {len(self.suggested_sources)} available"
        )


class QueryClassifier(ABC):
    """
    🏗️ Abstract Base Class for Query Classifiers

    This demonstrates the "Strategy Pattern" - a professional design pattern
    where different algorithms can be swapped in and out easily.

    Abstract classes define what methods must exist without implementing them.
    This ensures all classifiers work the same way!
    """

    @abstractmethod
    def classify(self, query: str) -> QueryType:
        """Every classifier must be able to classify queries"""
        pass

    @abstractmethod
    def get_confidence(self, query: str, query_type: QueryType) -> float:
        """Every classifier must provide confidence scores"""
        pass


class KeywordBasedClassifier(QueryClassifier):
    """
    🔤 Keyword-Based Classifier - Classification Using Word Matching

    This is a simple but effective approach used in many real systems.
    We look for specific words that indicate what type of question it is.

    PROS: Fast, easy to understand, works well for clear categories
    CONS: Can be fooled by context, doesn't understand meaning deeply
    """

    def __init__(self):
        """Set up our keyword patterns for each query type"""
        self.type_keywords = {
            QueryType.ENVIRONMENTAL: {
                "primary": [
                    "climate",
                    "environment",
                    "green",
                    "sustainability",
                    "carbon",
                    "renewable",
                ],
                "secondary": [
                    "polar",
                    "ocean",
                    "forest",
                    "pollution",
                    "ecosystem",
                    "biodiversity",
                    "warming",
                ],
                "sources": [
                    "climate.nasa.gov",
                    "epa.gov",
                    "ipcc.ch",
                    "nature.com/subjects/climate-change",
                ],
            },
            QueryType.TECHNOLOGY: {
                "primary": [
                    "technology",
                    "computer",
                    "ai",
                    "artificial",
                    "machine",
                    "algorithm",
                ],
                "secondary": [
                    "software",
                    "programming",
                    "data",
                    "neural",
                    "robot",
                    "automation",
                    "digital",
                ],
                "sources": ["arxiv.org", "ieee.org", "acm.org", "techcrunch.com"],
            },
            QueryType.MEDICAL: {
                "primary": [
                    "medical",
                    "health",
                    "disease",
                    "treatment",
                    "clinical",
                    "diagnosis",
                ],
                "secondary": [
                    "patient",
                    "therapy",
                    "symptoms",
                    "medicine",
                    "doctor",
                    "hospital",
                    "research",
                ],
                "sources": [
                    "pubmed.ncbi.nlm.nih.gov",
                    "who.int",
                    "nih.gov",
                    "webmd.com",
                ],
            },
        }

    def classify(self, query: str) -> QueryType:
        """
        🎯 Classify a query based on keyword matching

        Args:
            query: The user's research question

        Returns:
            QueryType: The most likely category for this query
        """
        if not query or not query.strip():
            return QueryType.GENERAL

        query_normalized = self._normalize_query(query)
        scores = self._calculate_keyword_scores(query_normalized)

        # Return the type with the highest score, or GENERAL if no matches
        if max(scores.values()) == 0:
            return QueryType.GENERAL

        return max(scores.keys(), key=lambda k: scores[k])

    def get_confidence(self, query: str, query_type: QueryType) -> float:
        """
        📊 Calculate how confident we are in our classification

        Args:
            query: The user's research question
            query_type: The type we classified it as

        Returns:
            float: Confidence score from 0.0 (not confident) to 1.0 (very confident)
        """
        if not query or query_type == QueryType.GENERAL:
            return 0.5  # Neutral confidence for general queries

        query_normalized = self._normalize_query(query)
        scores = self._calculate_keyword_scores(query_normalized)

        if query_type not in scores or scores[query_type] == 0:
            return 0.0

        # Confidence based on how many keywords matched and how strong they are
        max_possible_score = 5  # Arbitrary maximum for normalization
        confidence = min(scores[query_type] / max_possible_score, 1.0)

        return confidence

    def get_keywords_found(self, query: str, query_type: QueryType) -> List[str]:
        """
        🔍 Get the specific keywords that led to this classification

        This helps students understand WHY the system made its decision.
        """
        if query_type == QueryType.GENERAL or query_type not in self.type_keywords:
            return []

        query_normalized = self._normalize_query(query)
        keywords_config = self.type_keywords[query_type]

        found_keywords = []

        # Check primary keywords (more important)
        for keyword in keywords_config["primary"]:
            if keyword in query_normalized:
                found_keywords.append(f"{keyword} (primary)")

        # Check secondary keywords
        for keyword in keywords_config["secondary"]:
            if keyword in query_normalized:
                found_keywords.append(f"{keyword} (secondary)")

        return found_keywords

    def get_suggested_sources(self, query_type: QueryType) -> List[str]:
        """
        🌐 Get suggested sources for this type of query

        Different types of questions are best answered by different sources.
        This helps students learn about authoritative information sources.
        """
        if query_type in self.type_keywords:
            return self.type_keywords[query_type]["sources"].copy()
        return [
            "scholar.google.com",
            "wikipedia.org",
            "britannica.com",
        ]  # General sources

    def _normalize_query(self, query: str) -> str:
        """
        🔄 Clean up the query for consistent processing

        Professional tip: Always normalize your input data!
        This prevents bugs caused by inconsistent formatting.
        """
        # Convert to lowercase for case-insensitive matching
        normalized = query.lower().strip()

        # Remove extra whitespace (multiple spaces become single spaces)
        normalized = re.sub(r"\s+", " ", normalized)

        # Remove punctuation that might interfere with keyword matching
        normalized = re.sub(r"[^\w\s]", " ", normalized)

        return normalized

    def _calculate_keyword_scores(self, query: str) -> Dict[QueryType, int]:
        """
        🧮 Calculate scores for each query type based on keyword matches

        Professional tip: Breaking complex logic into small, testable methods
        makes code easier to understand and debug!
        """
        scores = {qtype: 0 for qtype in QueryType if qtype != QueryType.GENERAL}

        for query_type, keywords_config in self.type_keywords.items():
            # Primary keywords are worth more points
            for keyword in keywords_config["primary"]:
                if keyword in query:
                    scores[query_type] += 3

            # Secondary keywords are worth fewer points
            for keyword in keywords_config["secondary"]:
                if keyword in query:
                    scores[query_type] += 1

        return scores


class TimeAnalyzer:
    """
    ⏰ Time Analyzer - Detecting When Users Want Recent vs Historical Information

    This class specializes in understanding temporal aspects of queries.
    Professional tip: Single Responsibility Principle - each class should do one thing well!
    """

    def __init__(self):
        """Set up patterns for detecting time preferences"""
        self.time_patterns = {
            TimePreference.RECENT: [
                "latest",
                "recent",
                "new",
                "current",
                "today",
                "now",
                "contemporary",
                "2024",
                "2025",
                "modern",
                "up-to-date",
                "fresh",
                "breaking",
            ],
            TimePreference.HISTORICAL: [
                "history",
                "historical",
                "past",
                "ancient",
                "old",
                "traditional",
                "origins",
                "development",
                "evolution",
                "began",
                "started",
                "originally",
            ],
        }

    def analyze_time_preference(self, query: str) -> TimePreference:
        """
        📅 Determine if the user wants recent or historical information

        Args:
            query: The user's research question

        Returns:
            TimePreference: RECENT, HISTORICAL, or ANY
        """
        if not query:
            return TimePreference.ANY

        query_lower = query.lower()

        # Check for recent indicators
        for keyword in self.time_patterns[TimePreference.RECENT]:
            if keyword in query_lower:
                return TimePreference.RECENT

        # Check for historical indicators
        for keyword in self.time_patterns[TimePreference.HISTORICAL]:
            if keyword in query_lower:
                return TimePreference.HISTORICAL

        # Default to ANY if no time indicators found
        return TimePreference.ANY


class QueryAnalyzer:
    """
    🧠 Main Query Analyzer - The Complete System

    This is the main class that coordinates all the different components.
    This demonstrates the "Composition Pattern" - building complex systems
    from simpler, focused components.

    DESIGN PRINCIPLES DEMONSTRATED:
    - Single Responsibility: Each component does one thing well
    - Composition over Inheritance: We use other classes rather than inheriting
    - Dependency Injection: Components can be swapped out easily
    - Interface Segregation: Clean, simple public methods
    """

    def __init__(self, classifier: Optional[QueryClassifier] = None):
        """
        🏗️ Initialize the Query Analyzer

        Args:
            classifier: The classification strategy to use (defaults to keyword-based)
        """
        # Use dependency injection pattern - allows different classifiers to be used
        self.classifier = classifier or KeywordBasedClassifier()
        self.time_analyzer = TimeAnalyzer()

        # Keep track of analysis history for learning purposes
        self.analysis_history: List[QueryAnalysis] = []

    def classify(self, query: str) -> Dict[str, str]:
        """
        🔄 Legacy Interface - Maintains backward compatibility

        This method exists to support the old API while we transition to the new one.
        Professional tip: When refactoring, always maintain backward compatibility!

        Args:
            query: The user's research question

        Returns:
            Dict containing 'type' and 'time_preference' keys
        """
        analysis = self.analyze(query)
        return {
            "type": analysis.query_type.value,
            "time_preference": analysis.time_preference.value,
        }

    def analyze(self, query: str) -> QueryAnalysis:
        """
        🔍 Complete Query Analysis - The Main Public Method

        This is the primary method that external code should use.
        It coordinates all the different analysis components.

        Args:
            query: The user's research question

        Returns:
            QueryAnalysis: Complete analysis results with all information
        """
        # Input validation - always check your inputs!
        if not query or not isinstance(query, str) or not query.strip():
            return self._create_empty_analysis(query or "")

        try:
            # Step 1: Classify the query type
            query_type = self.classifier.classify(query)

            # Step 2: Get confidence score
            confidence = self.classifier.get_confidence(query, query_type)

            # Step 3: Extract keywords that influenced the decision
            keywords_found = []
            if hasattr(self.classifier, "get_keywords_found"):
                keywords_found = self.classifier.get_keywords_found(query, query_type)

            # Step 4: Get suggested sources
            suggested_sources = []
            if hasattr(self.classifier, "get_suggested_sources"):
                suggested_sources = self.classifier.get_suggested_sources(query_type)

            # Step 5: Analyze time preference
            time_preference = self.time_analyzer.analyze_time_preference(query)

            # Step 6: Create comprehensive result
            analysis = QueryAnalysis(
                query_type=query_type,
                time_preference=time_preference,
                confidence=confidence,
                keywords_found=keywords_found,
                suggested_sources=suggested_sources,
                original_query=query,
            )

            # Step 7: Store for learning purposes
            self.analysis_history.append(analysis)

            return analysis

        except Exception as e:
            # Professional error handling - never let exceptions crash the system
            print(f"⚠️ Error analyzing query '{query}': {e}")
            return self._create_empty_analysis(query)

    def get_analysis_stats(self) -> Dict[str, any]:
        """
        📊 Get Statistics About Past Analyses

        This helps students understand what kinds of queries the system has seen.
        Professional systems often include analytics like this.
        """
        if not self.analysis_history:
            return {"total_queries": 0, "query_types": {}, "average_confidence": 0.0}

        # Count query types
        type_counts = {}
        total_confidence = 0.0

        for analysis in self.analysis_history:
            query_type = analysis.query_type.value
            type_counts[query_type] = type_counts.get(query_type, 0) + 1
            total_confidence += analysis.confidence

        return {
            "total_queries": len(self.analysis_history),
            "query_types": type_counts,
            "average_confidence": total_confidence / len(self.analysis_history),
            "most_common_type": (
                max(type_counts.keys(), key=lambda k: type_counts[k])
                if type_counts
                else "none"
            ),
        }

    def _create_empty_analysis(self, query: str) -> QueryAnalysis:
        """
        🔧 Create a safe default analysis for edge cases

        Professional tip: Always have safe fallbacks for error conditions!
        """
        return QueryAnalysis(
            query_type=QueryType.GENERAL,
            time_preference=TimePreference.ANY,
            confidence=0.0,
            keywords_found=[],
            suggested_sources=["scholar.google.com", "wikipedia.org"],
            original_query=query,
        )


# Example usage and demonstration
if __name__ == "__main__":
    """
    🎮 Interactive Demonstration

    This section runs when the file is executed directly.
    It shows students how to use the Query Analyzer in practice.
    """

    print("🔍 AI Research Query Analyzer - Interactive Demo")
    print("=" * 50)

    # Create an analyzer
    analyzer = QueryAnalyzer()

    # Test queries to demonstrate different features
    test_queries = [
        "What are the latest developments in artificial intelligence?",
        "How does climate change affect polar bears?",
        "What is the history of medical treatments for diabetes?",
        "Recent advances in renewable energy technology",
        "General information about photosynthesis",
    ]

    print("🧪 Testing Different Types of Queries:\n")

    for i, query in enumerate(test_queries, 1):
        print(f"Test {i}: {query}")
        print("-" * 40)

        # Analyze the query
        analysis = analyzer.analyze(query)
        print(analysis)
        print()

    # Show statistics
    print("📊 Analysis Statistics:")
    print("-" * 40)
    stats = analyzer.get_analysis_stats()
    for key, value in stats.items():
        print(f"{key.replace('_', ' ').title()}: {value}")

    print("\n✨ This is how professional AI systems understand human language!")
    print("Try running this with different queries to see how it works!")
