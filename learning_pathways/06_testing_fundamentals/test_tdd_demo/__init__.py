"""
🔄 TEST-DRIVEN DEVELOPMENT (TDD) DEMONSTRATION

This module provides a complete, step-by-step demonstration of Test-Driven
Development using our AI research system as an example. Perfect for middle
school students learning professional software development practices!

WHAT IS TEST-DRIVEN DEVELOPMENT (TDD)?
======================================
TDD is a programming technique where you write tests BEFORE writing the code.
It follows a simple three-step cycle that professionals use every day:

🔴 RED: Write a test that fails (because the feature doesn't exist yet)
🟢 GREEN: Write just enough code to make the test pass (keep it simple!)
🔄 REFACTOR: Clean up and improve the code while keeping tests green

WHY USE TDD?
============
1. 🎯 Better Design: Writing tests first helps you think about what you really need
2. 🛡️ Fewer Bugs: Tests catch problems immediately
3. 📖 Living Documentation: Tests show exactly how code should work
4. 🏗️ Confidence: You can refactor without fear of breaking things
5. ⚡ Faster Development: Less debugging time overall

THE TDD MINDSET:
===============
- Think about WHAT you want before HOW to build it
- Write the smallest test that could possibly fail
- Write the simplest code that could possibly work
- Refactor mercilessly while tests are green
- Never write production code without a failing test first

REAL-WORLD EXAMPLE:
==================
We'll build a simple Query Analyzer for our AI research system, demonstrating
each step of the TDD cycle with clear explanations of what we're thinking
and why we make each decision.

LEARNING PROGRESSION:
====================
1. 🔴 RED Phase: Write failing tests that define what we want
2. 🟢 GREEN Phase: Write minimal code to pass tests
3. 🔄 REFACTOR Phase: Improve code while keeping tests green
4. 🔁 REPEAT: Add more features using the same cycle

Ready to see how professional programmers really work? Let's go! 🚀
"""

import pytest
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum


# =============================================================================
# TDD CYCLE 1: BASIC QUERY CLASSIFICATION
# =============================================================================


class TestQueryAnalyzer_Cycle1_RED:
    """
    🔴 TDD CYCLE 1 - RED PHASE: Writing Our First Failing Test

    In the RED phase, we write tests for features that don't exist yet.
    This helps us think about WHAT we want before we think about HOW to build it.

    WHAT WE'RE BUILDING:
    A Query Analyzer that can classify different types of research questions.

    WHY WE START HERE:
    This is the simplest possible feature - just categorizing queries.
    We'll add complexity later, but start simple!
    """

    def test_query_analyzer_exists(self):
        """
        🔴 RED TEST 1: Does our QueryAnalyzer class exist?

        This is the most basic test - does the class even exist?
        This test will FAIL initially because we haven't written the class yet.

        TDD PRINCIPLE: Write the test first, then make it pass!
        """
        # This import will fail initially - that's expected in RED phase!
        try:
            from src.educational.query_analyzer import QueryAnalyzer

            analyzer = QueryAnalyzer()
            assert analyzer is not None, "QueryAnalyzer should be instantiable"
        except ImportError:
            pytest.fail(
                "QueryAnalyzer class doesn't exist yet - this is expected in RED phase!"
            )

    def test_query_analyzer_classify_basic(self):
        """
        🔴 RED TEST 2: Can we classify basic query types?

        This test defines WHAT we want our analyzer to do:
        - Take a query string as input
        - Return a classification of the query type

        This will FAIL because the classify method doesn't exist yet.
        """
        try:
            from src.educational.query_analyzer import QueryAnalyzer

            analyzer = QueryAnalyzer()

            # Test environmental query
            result = analyzer.classify(
                "What is the impact of climate change on polar bears?"
            )
            assert (
                result["type"] == "environmental"
            ), "Should classify environmental queries"

            # Test technology query
            result = analyzer.classify("How does machine learning work?")
            assert result["type"] == "technology", "Should classify technology queries"

            # Test general query
            result = analyzer.classify("What is the meaning of life?")
            assert result["type"] == "general", "Should classify general queries"

        except (ImportError, AttributeError):
            pytest.fail(
                "classify method doesn't exist yet - this is expected in RED phase!"
            )


class TestQueryAnalyzer_Cycle1_GREEN:
    """
    🟢 TDD CYCLE 1 - GREEN PHASE: Making Our Tests Pass

    In the GREEN phase, we write just enough code to make our tests pass.
    We're not trying to be clever or elegant - just make it work!

    THE GREEN PHASE RULE:
    Write the simplest code that could possibly work. Don't overthink it!
    """

    def test_query_analyzer_basic_implementation(self):
        """
        🟢 GREEN TEST: Our basic implementation should work

        This test verifies that our minimal GREEN phase implementation works.
        The code might be ugly, but it should pass the tests!
        """

        # Here's our GREEN phase implementation (inline for demonstration)
        class QueryAnalyzer:
            """SIMPLE GREEN PHASE IMPLEMENTATION - Just make tests pass!"""

            def classify(self, query: str) -> Dict[str, str]:
                query_lower = query.lower()

                # Simple keyword-based classification
                if any(
                    word in query_lower
                    for word in ["climate", "environment", "polar", "green"]
                ):
                    return {"type": "environmental"}
                elif any(
                    word in query_lower
                    for word in ["machine", "learning", "technology", "computer"]
                ):
                    return {"type": "technology"}
                else:
                    return {"type": "general"}

        # Test our GREEN implementation
        analyzer = QueryAnalyzer()

        assert (
            analyzer.classify("What is the impact of climate change on polar bears?")[
                "type"
            ]
            == "environmental"
        )
        assert (
            analyzer.classify("How does machine learning work?")["type"] == "technology"
        )
        assert analyzer.classify("What is the meaning of life?")["type"] == "general"

        print("✅ GREEN PHASE: Basic implementation passes all tests!")


class TestQueryAnalyzer_Cycle1_REFACTOR:
    """
    🔄 TDD CYCLE 1 - REFACTOR PHASE: Improving Our Code

    In the REFACTOR phase, we improve the code while keeping all tests green.
    We can make it more elegant, more efficient, or easier to understand.

    REFACTOR PHASE RULES:
    1. All existing tests must stay green
    2. No new functionality (that requires new tests first)
    3. Focus on code quality: readability, maintainability, performance
    """

    def test_query_analyzer_refactored_implementation(self):
        """
        🔄 REFACTOR TEST: Our improved implementation should still work

        This test verifies that our refactored code still passes all original tests
        while being cleaner and more maintainable.
        """
        from enum import Enum
        from dataclasses import dataclass
        from typing import Dict, List

        # Here's our REFACTORED implementation - cleaner and more professional
        class QueryType(Enum):
            """Enumeration of query types for better type safety"""

            ENVIRONMENTAL = "environmental"
            TECHNOLOGY = "technology"
            GENERAL = "general"

        @dataclass
        class QueryClassification:
            """Data class for query classification results"""

            type: QueryType
            confidence: float
            keywords: List[str]

        class QueryAnalyzer:
            """REFACTORED IMPLEMENTATION - Clean, professional, maintainable"""

            def __init__(self):
                self.classification_keywords = {
                    QueryType.ENVIRONMENTAL: [
                        "climate",
                        "environment",
                        "polar",
                        "green",
                        "sustainability",
                        "carbon",
                    ],
                    QueryType.TECHNOLOGY: [
                        "machine",
                        "learning",
                        "technology",
                        "computer",
                        "ai",
                        "artificial",
                        "algorithm",
                    ],
                }

            def classify(self, query: str) -> Dict[str, str]:
                """Classify a query and return the result in the expected format"""
                classification = self._classify_detailed(query)
                return {"type": classification.type.value}

            def _classify_detailed(self, query: str) -> QueryClassification:
                """Internal method that returns detailed classification"""
                query_lower = query.lower().split()

                # Calculate confidence for each category
                scores = {}
                matched_keywords = {}

                for query_type, keywords in self.classification_keywords.items():
                    matches = [
                        word
                        for word in keywords
                        if any(word in token for token in query_lower)
                    ]
                    matched_keywords[query_type] = matches
                    scores[query_type] = len(matches)

                # Find the best match
                if max(scores.values()) == 0:
                    return QueryClassification(QueryType.GENERAL, 0.5, [])

                best_type = max(scores.keys(), key=lambda k: scores[k])
                confidence = min(scores[best_type] / 3.0, 1.0)  # Normalize confidence

                return QueryClassification(
                    best_type, confidence, matched_keywords[best_type]
                )

        # Test our REFACTORED implementation with original tests
        analyzer = QueryAnalyzer()

        assert (
            analyzer.classify("What is the impact of climate change on polar bears?")[
                "type"
            ]
            == "environmental"
        )
        assert (
            analyzer.classify("How does machine learning work?")["type"] == "technology"
        )
        assert analyzer.classify("What is the meaning of life?")["type"] == "general"

        print("✅ REFACTOR PHASE: Improved implementation passes all tests!")

        # We can also test the detailed classification (but this doesn't break existing interface)
        detailed = analyzer._classify_detailed("machine learning and climate change")
        assert detailed.confidence > 0, "Should have some confidence"
        assert len(detailed.keywords) > 0, "Should identify keywords"

        print(
            f"✅ REFACTOR BONUS: Detailed classification works! Keywords: {detailed.keywords}"
        )


# =============================================================================
# TDD CYCLE 2: ADDING MORE FEATURES
# =============================================================================


class TestQueryAnalyzer_Cycle2_RED:
    """
    🔴 TDD CYCLE 2 - RED PHASE: Adding Time-Based Classification

    Now we'll add a new feature: detecting when users want recent information.
    We start with RED - writing tests for features that don't exist yet.

    NEW FEATURE: Time Sensitivity Detection
    - Detect queries asking for "latest", "recent", "new" information
    - Return time preference in classification results

    TDD PRINCIPLE: Each new feature starts with a failing test!
    """

    def test_time_sensitivity_detection(self):
        """
        🔴 RED TEST: Can we detect when users want recent information?

        This test will FAIL because we haven't implemented time detection yet.
        """
        try:
            from src.educational.query_analyzer import QueryAnalyzer

            analyzer = QueryAnalyzer()

            # Test queries with time sensitivity
            result = analyzer.classify("What are the latest developments in AI?")
            assert "time_preference" in result, "Should include time preference"
            assert (
                result["time_preference"] == "recent"
            ), "Should detect 'latest' as recent"

            result = analyzer.classify("Recent advances in renewable energy")
            assert result["time_preference"] == "recent", "Should detect 'recent'"

            result = analyzer.classify("How does photosynthesis work?")
            assert (
                result["time_preference"] == "any"
            ), "Should default to 'any' for timeless queries"

        except (ImportError, AttributeError, KeyError):
            pytest.fail(
                "Time sensitivity detection not implemented yet - expected in RED phase!"
            )


class TestQueryAnalyzer_Cycle2_GREEN:
    """
    🟢 TDD CYCLE 2 - GREEN PHASE: Implementing Time Detection

    Now we add just enough code to make the time sensitivity tests pass.
    We modify our existing code minimally to support the new feature.
    """

    def test_time_sensitivity_implementation(self):
        """
        🟢 GREEN TEST: Our time detection implementation should work
        """
        from enum import Enum
        from typing import Dict, List

        class QueryType(Enum):
            ENVIRONMENTAL = "environmental"
            TECHNOLOGY = "technology"
            GENERAL = "general"

        class QueryAnalyzer:
            """GREEN PHASE: Added minimal time detection"""

            def __init__(self):
                self.classification_keywords = {
                    QueryType.ENVIRONMENTAL: [
                        "climate",
                        "environment",
                        "polar",
                        "green",
                        "sustainability",
                    ],
                    QueryType.TECHNOLOGY: [
                        "machine",
                        "learning",
                        "technology",
                        "computer",
                        "ai",
                        "artificial",
                    ],
                }
                # NEW: Time sensitivity keywords
                self.time_keywords = [
                    "latest",
                    "recent",
                    "new",
                    "current",
                    "today",
                    "2024",
                    "2025",
                ]

            def classify(self, query: str) -> Dict[str, str]:
                query_lower = query.lower()

                # Existing classification logic
                query_type = QueryType.GENERAL
                for qtype, keywords in self.classification_keywords.items():
                    if any(word in query_lower for word in keywords):
                        query_type = qtype
                        break

                # NEW: Time preference detection
                time_preference = "any"  # default
                if any(word in query_lower for word in self.time_keywords):
                    time_preference = "recent"

                return {"type": query_type.value, "time_preference": time_preference}

        # Test the GREEN implementation
        analyzer = QueryAnalyzer()

        # Test original functionality still works
        assert analyzer.classify("climate change")["type"] == "environmental"
        assert analyzer.classify("machine learning")["type"] == "technology"

        # Test new time sensitivity feature
        result = analyzer.classify("What are the latest developments in AI?")
        assert result["time_preference"] == "recent"
        assert result["type"] == "technology"

        result = analyzer.classify("Recent advances in renewable energy")
        assert result["time_preference"] == "recent"
        assert result["type"] == "environmental"

        result = analyzer.classify("How does photosynthesis work?")
        assert result["time_preference"] == "any"

        print("✅ GREEN PHASE CYCLE 2: Time detection works!")


class TestQueryAnalyzer_Cycle2_REFACTOR:
    """
    🔄 TDD CYCLE 2 - REFACTOR PHASE: Professional Implementation

    Now we refactor to make the code more professional and maintainable.
    All tests must still pass, but the code should be production-ready.
    """

    def test_professional_query_analyzer(self):
        """
        🔄 REFACTOR TEST: Production-ready implementation

        This shows how professional software engineers structure their code.
        """
        from enum import Enum
        from dataclasses import dataclass
        from typing import Dict, List, Optional
        import re

        class QueryType(Enum):
            """Professional enumeration with docstrings"""

            ENVIRONMENTAL = "environmental"
            TECHNOLOGY = "technology"
            MEDICAL = "medical"
            GENERAL = "general"

        class TimePreference(Enum):
            """Time sensitivity preferences"""

            RECENT = "recent"
            HISTORICAL = "historical"
            ANY = "any"

        @dataclass
        class QueryAnalysis:
            """Complete query analysis result"""

            query_type: QueryType
            time_preference: TimePreference
            confidence: float
            keywords_found: List[str]
            suggested_sources: List[str]

        class QueryAnalyzer:
            """
            Professional Query Analyzer with comprehensive features

            This is how you'd write this class in a real software company!
            """

            def __init__(self):
                self.type_patterns = {
                    QueryType.ENVIRONMENTAL: {
                        "keywords": [
                            "climate",
                            "environment",
                            "polar",
                            "green",
                            "sustainability",
                            "carbon",
                            "renewable",
                        ],
                        "sources": ["climate-research.org", "ipcc.ch", "epa.gov"],
                    },
                    QueryType.TECHNOLOGY: {
                        "keywords": [
                            "machine",
                            "learning",
                            "technology",
                            "computer",
                            "ai",
                            "artificial",
                            "algorithm",
                            "neural",
                        ],
                        "sources": ["arxiv.org", "ieee.org", "acm.org"],
                    },
                    QueryType.MEDICAL: {
                        "keywords": [
                            "medical",
                            "health",
                            "disease",
                            "treatment",
                            "diagnosis",
                            "clinical",
                        ],
                        "sources": ["pubmed.ncbi.nlm.nih.gov", "who.int", "nih.gov"],
                    },
                }

                self.time_patterns = {
                    TimePreference.RECENT: [
                        "latest",
                        "recent",
                        "new",
                        "current",
                        "today",
                        "2024",
                        "2025",
                        "now",
                    ],
                    TimePreference.HISTORICAL: [
                        "history",
                        "past",
                        "historical",
                        "evolution",
                        "origins",
                        "before",
                    ],
                }

            def classify(self, query: str) -> Dict[str, str]:
                """Public interface - maintains backward compatibility"""
                analysis = self.analyze(query)
                return {
                    "type": analysis.query_type.value,
                    "time_preference": analysis.time_preference.value,
                }

            def analyze(self, query: str) -> QueryAnalysis:
                """
                Comprehensive query analysis with professional features

                Args:
                    query: The research query to analyze

                Returns:
                    QueryAnalysis: Complete analysis with confidence scores
                """
                if not query or not query.strip():
                    return QueryAnalysis(
                        QueryType.GENERAL, TimePreference.ANY, 0.0, [], []
                    )

                query_normalized = self._normalize_query(query)

                # Analyze query type
                type_result = self._analyze_query_type(query_normalized)

                # Analyze time preference
                time_result = self._analyze_time_preference(query_normalized)

                return QueryAnalysis(
                    query_type=type_result["type"],
                    time_preference=time_result["preference"],
                    confidence=type_result["confidence"],
                    keywords_found=type_result["keywords"],
                    suggested_sources=self.type_patterns.get(
                        type_result["type"], {}
                    ).get("sources", []),
                )

            def _normalize_query(self, query: str) -> str:
                """Normalize query for consistent processing"""
                # Remove extra whitespace and convert to lowercase
                normalized = re.sub(r"\s+", " ", query.lower().strip())
                return normalized

            def _analyze_query_type(self, query: str) -> Dict:
                """Analyze the type of query using keyword matching"""
                scores = {}
                all_keywords = {}

                for qtype, config in self.type_patterns.items():
                    keywords = config["keywords"]
                    matches = [kw for kw in keywords if kw in query]
                    scores[qtype] = len(matches)
                    all_keywords[qtype] = matches

                if max(scores.values()) == 0:
                    return {
                        "type": QueryType.GENERAL,
                        "confidence": 0.5,
                        "keywords": [],
                    }

                best_type = max(scores.keys(), key=lambda k: scores[k])
                confidence = min(scores[best_type] / 3.0, 1.0)

                return {
                    "type": best_type,
                    "confidence": confidence,
                    "keywords": all_keywords[best_type],
                }

            def _analyze_time_preference(self, query: str) -> Dict:
                """Analyze time sensitivity of the query"""
                for time_pref, keywords in self.time_patterns.items():
                    if any(kw in query for kw in keywords):
                        return {"preference": time_pref}

                return {"preference": TimePreference.ANY}

        # Test the professional implementation
        analyzer = QueryAnalyzer()

        # Test backward compatibility
        result = analyzer.classify("latest machine learning developments")
        assert result["type"] == "technology"
        assert result["time_preference"] == "recent"

        # Test advanced features
        analysis = analyzer.analyze("recent climate change research")
        assert analysis.query_type == QueryType.ENVIRONMENTAL
        assert analysis.time_preference == TimePreference.RECENT
        assert analysis.confidence > 0
        assert len(analysis.keywords_found) > 0
        assert len(analysis.suggested_sources) > 0

        print("✅ REFACTOR CYCLE 2: Professional implementation complete!")
        print(f"   Keywords found: {analysis.keywords_found}")
        print(
            f"   Suggested sources: {analysis.suggested_sources[:2]}..."
        )  # Show first 2


# =============================================================================
# TDD DEMO SUMMARY AND LESSONS
# =============================================================================


class TestTDDLessonsLearned:
    """
    🎓 TDD LESSONS LEARNED - What We Discovered

    This test class summarizes the key lessons from our TDD demonstration.
    Perfect for reflecting on what we learned!
    """

    def test_tdd_principles_demonstrated(self):
        """
        📚 WHAT WE LEARNED ABOUT TDD

        This test summarizes the key principles we demonstrated:
        """
        tdd_principles = {
            "red_green_refactor_cycle": "Always start with failing tests, make them pass, then improve",
            "simple_solutions_first": "Write the simplest code that works before making it elegant",
            "test_driven_design": "Tests help you think about what you want before how to build it",
            "refactor_with_confidence": "Good tests let you improve code without fear",
            "incremental_development": "Add features one small step at a time",
            "living_documentation": "Tests show exactly how code should behave",
        }

        # Each principle should be true based on our demonstration
        for principle, description in tdd_principles.items():
            assert (
                len(description) > 10
            ), f"Principle {principle} should have meaningful description"
            print(f"✅ {principle.replace('_', ' ').title()}: {description}")

        print("\n🎉 TDD DEMONSTRATION COMPLETE!")
        print("You've seen how professional programmers use Test-Driven Development!")

    def test_code_evolution_timeline(self):
        """
        📈 HOW OUR CODE EVOLVED THROUGH TDD

        This shows the progression from simple to sophisticated code.
        """
        evolution_stages = [
            {
                "stage": "RED - Cycle 1",
                "description": "Wrote failing tests for basic classification",
                "code_quality": "No code yet",
                "test_coverage": "Tests exist but fail",
            },
            {
                "stage": "GREEN - Cycle 1",
                "description": "Simple if/else logic to pass tests",
                "code_quality": "Basic but working",
                "test_coverage": "100% of existing features",
            },
            {
                "stage": "REFACTOR - Cycle 1",
                "description": "Cleaner code with enums and better structure",
                "code_quality": "Professional structure",
                "test_coverage": "100% of existing features",
            },
            {
                "stage": "RED - Cycle 2",
                "description": "Added failing tests for time detection",
                "code_quality": "Some tests fail",
                "test_coverage": "Tests for new features fail",
            },
            {
                "stage": "GREEN - Cycle 2",
                "description": "Added minimal time detection code",
                "code_quality": "Working but basic",
                "test_coverage": "100% of all features",
            },
            {
                "stage": "REFACTOR - Cycle 2",
                "description": "Production-ready with full documentation",
                "code_quality": "Professional grade",
                "test_coverage": "100% with comprehensive tests",
            },
        ]

        # Verify our evolution made sense
        assert len(evolution_stages) == 6, "Should have 6 stages in our TDD evolution"

        for i, stage in enumerate(evolution_stages):
            print(f"Stage {i+1} - {stage['stage']}: {stage['description']}")
            assert stage["code_quality"], "Each stage should describe code quality"
            assert stage["test_coverage"], "Each stage should describe test coverage"

        print("\n✨ This is how professional software evolves through TDD!")


if __name__ == "__main__":
    print("🔄 TDD Demonstration - Learn How Professionals Code!")
    print("Run with: pytest tests/test_tdd_demo/ -v")
    print("Watch the RED-GREEN-REFACTOR cycle in action!")
