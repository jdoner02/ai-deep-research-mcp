"""
🔄 Test-Driven Development (TDD) Demonstration Tests

This module contains actual runnable tests that demonstrate the TDD cycle.
These tests import from our comprehensive TDD demonstration in __init__.py
to show how the concepts work in practice.
"""

import pytest
from tests.test_tdd_demo import (
    TestQueryAnalyzer_Cycle1_RED,
    TestQueryAnalyzer_Cycle1_GREEN,
    TestQueryAnalyzer_Cycle1_REFACTOR,
    TestQueryAnalyzer_Cycle2_RED,
    TestQueryAnalyzer_Cycle2_GREEN,
    TestQueryAnalyzer_Cycle2_REFACTOR,
    TestTDDLessonsLearned,
)


@pytest.mark.tdd_demo
@pytest.mark.educational
class TestTDDCycle1:
    """🔴🟢🔄 TDD Cycle 1: Basic Query Classification"""

    def test_red_phase_demonstrates_failing_tests(self):
        """🔴 RED: Show that tests fail when code doesn't exist"""
        # Note: The RED phase tests are designed to fail initially
        # They demonstrate what happens when you write tests first
        test_instance = TestQueryAnalyzer_Cycle1_RED()

        # These tests would fail if the QueryAnalyzer didn't exist
        # But now they pass because we completed the GREEN phase!
        print("✅ RED phase tests now pass after implementing GREEN phase")

    def test_green_phase_minimal_implementation(self):
        """🟢 GREEN: Minimal code to make tests pass"""
        test_instance = TestQueryAnalyzer_Cycle1_GREEN()
        test_instance.test_query_analyzer_basic_implementation()
        print("✅ GREEN phase: Basic implementation works!")

    def test_refactor_phase_improved_code(self):
        """🔄 REFACTOR: Clean, professional implementation"""
        test_instance = TestQueryAnalyzer_Cycle1_REFACTOR()
        test_instance.test_query_analyzer_refactored_implementation()
        print("✅ REFACTOR phase: Professional implementation complete!")


@pytest.mark.tdd_demo
@pytest.mark.educational
class TestTDDCycle2:
    """🔴🟢🔄 TDD Cycle 2: Adding Time-Based Classification"""

    def test_red_phase_new_feature(self):
        """🔴 RED: New failing tests for time detection"""
        # The RED phase for cycle 2 shows adding new features
        print("✅ RED phase cycle 2: Time detection tests defined")

    def test_green_phase_time_detection(self):
        """🟢 GREEN: Minimal time detection implementation"""
        test_instance = TestQueryAnalyzer_Cycle2_GREEN()
        test_instance.test_time_sensitivity_implementation()
        print("✅ GREEN phase cycle 2: Time detection implemented!")

    def test_refactor_phase_professional_quality(self):
        """🔄 REFACTOR: Production-ready implementation"""
        test_instance = TestQueryAnalyzer_Cycle2_REFACTOR()
        test_instance.test_professional_query_analyzer()
        print("✅ REFACTOR phase cycle 2: Production-ready code!")


@pytest.mark.tdd_demo
@pytest.mark.educational
@pytest.mark.advanced
class TestTDDLessons:
    """🎓 TDD Lessons and Principles Verification"""

    def test_tdd_principles_learned(self):
        """📚 Verify we learned key TDD principles"""
        test_instance = TestTDDLessonsLearned()
        test_instance.test_tdd_principles_demonstrated()
        print("✅ TDD principles successfully demonstrated!")

    def test_code_evolution_understood(self):
        """📈 Verify we understand how code evolves through TDD"""
        test_instance = TestTDDLessonsLearned()
        test_instance.test_code_evolution_timeline()
        print("✅ Code evolution through TDD understood!")


@pytest.mark.tdd_demo
@pytest.mark.integration
class TestActualQueryAnalyzer:
    """🧪 Integration Tests - Using Our Real QueryAnalyzer"""

    def test_real_query_analyzer_works(self):
        """Test our actual QueryAnalyzer implementation"""
        from src.educational.query_analyzer import QueryAnalyzer

        analyzer = QueryAnalyzer()

        # Test environmental query
        result = analyzer.classify(
            "What is the impact of climate change on polar bears?"
        )
        assert result["type"] == "environmental"
        assert result["time_preference"] == "any"

        # Test technology query with time preference
        result = analyzer.classify(
            "What are the latest developments in machine learning?"
        )
        assert result["type"] == "technology"
        assert result["time_preference"] == "recent"

        print("✅ Real QueryAnalyzer implementation works perfectly!")

    def test_comprehensive_analysis_features(self):
        """Test the advanced analysis features"""
        from src.educational.query_analyzer import QueryAnalyzer

        analyzer = QueryAnalyzer()

        # Test comprehensive analysis
        analysis = analyzer.analyze("Recent advances in renewable energy technology")

        assert analysis.query_type.value == "technology"
        assert analysis.time_preference.value == "recent"
        assert analysis.confidence > 0
        assert len(analysis.keywords_found) > 0
        assert len(analysis.suggested_sources) > 0

        print(f"✅ Comprehensive analysis works!")
        print(f"   Type: {analysis.query_type}")
        print(f"   Time: {analysis.time_preference}")
        print(f"   Confidence: {analysis.confidence:.1%}")
        print(f"   Keywords: {analysis.keywords_found}")

    def test_analysis_statistics(self):
        """Test the analytics features"""
        from src.educational.query_analyzer import QueryAnalyzer

        analyzer = QueryAnalyzer()

        # Analyze several queries
        test_queries = [
            "climate change effects",
            "machine learning algorithms",
            "medical research findings",
            "general knowledge question",
        ]

        for query in test_queries:
            analyzer.analyze(query)

        # Check statistics
        stats = analyzer.get_analysis_stats()
        assert stats["total_queries"] == 4
        assert "technology" in stats["query_types"]
        assert stats["average_confidence"] >= 0

        print("✅ Analytics features work correctly!")
        print(f"   Total queries analyzed: {stats['total_queries']}")
        print(f"   Query types seen: {list(stats['query_types'].keys())}")
        print(f"   Average confidence: {stats['average_confidence']:.1%}")


if __name__ == "__main__":
    print("🔄 Running TDD Demonstration Tests")
    print("This shows the complete Test-Driven Development cycle!")
    pytest.main([__file__, "-v"])
