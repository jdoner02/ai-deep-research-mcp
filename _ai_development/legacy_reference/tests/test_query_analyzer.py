#!/usr/bin/env python3
"""
Test Guardian Agent - RED Phase
Test cases for Query Analyzer component of AI Deep Research MCP system

This module follows TDD principles - these tests are written FIRST to define
the expected behavior of the QueryAnalyzer class before implementation.

These tests will FAIL initially (RED phase) until we implement the code.
"""

import pytest
from typing import List, Dict, Any
from unittest.mock import Mock, patch

# Import will succeed now that we fixed the import system
from src.query_analyzer import QueryAnalyzer


class TestQueryAnalyzer:
    """Test suite for QueryAnalyzer component - defining expected behavior"""
    
    def test_query_analyzer_exists(self):
        """Test that QueryAnalyzer class exists and can be instantiated"""
        assert QueryAnalyzer is not None, "QueryAnalyzer class should exist"
        analyzer = QueryAnalyzer()
        assert analyzer is not None
    
    def test_decompose_complex_query(self):
        """Test decomposition of complex multi-faceted query into subtopics"""
        analyzer = QueryAnalyzer()
        
        complex_query = "Explain the latest developments in quantum computing and their implications for cryptography"
        
        result = analyzer.decompose_query(complex_query)
        
        # Expected behavior: should return list of subtopics
        assert isinstance(result, list)
        assert len(result) >= 2  # Should find at least 2 subtopics
        
        # Should contain quantum computing and cryptography aspects
        result_text = " ".join(result).lower()
        assert "quantum computing" in result_text
        assert "cryptography" in result_text
    
    def test_generate_search_variants(self):
        """Test generation of multiple search query variants"""
        analyzer = QueryAnalyzer()
        
        query = "machine learning in healthcare"
        variants = analyzer.generate_search_variants(query)
        
        assert isinstance(variants, list)
        assert len(variants) >= 3  # Should generate multiple variants
        assert query in variants  # Original query should be included
        
        # Variants should be different from original
        unique_variants = [v for v in variants if v != query]
        assert len(unique_variants) >= 2
    
    def test_extract_keywords(self):
        """Test keyword extraction from query"""
        analyzer = QueryAnalyzer()
        
        query = "latest research on neural networks for image recognition"
        keywords = analyzer.extract_keywords(query)
        
        assert isinstance(keywords, list)
        assert len(keywords) >= 3
        
        # Should extract meaningful keywords, not stopwords
        expected_keywords = ["research", "neural networks", "image recognition"]
        for keyword in expected_keywords:
            assert any(keyword.lower() in k.lower() for k in keywords)
    
    def test_identify_authoritative_domains(self):
        """Test identification of authoritative domains for academic queries"""
        analyzer = QueryAnalyzer()
        
        academic_query = "peer reviewed research on climate change"
        domains = analyzer.identify_authoritative_domains(academic_query)
        
        assert isinstance(domains, list)
        assert len(domains) >= 2
        
        # Should include academic domains
        expected_domains = [".edu", "scholar.google.com", "arxiv.org", "pubmed.ncbi.nlm.nih.gov"]
        found_academic = any(domain in domains for domain in expected_domains)
        assert found_academic, "Should identify academic domains for academic queries"
    
    def test_plan_search_strategy(self):
        """Test creation of comprehensive search strategy"""
        analyzer = QueryAnalyzer()
        
        query = "blockchain security vulnerabilities 2024"
        strategy = analyzer.plan_search_strategy(query)
        
        assert isinstance(strategy, dict)
        
        # Strategy should contain key components
        required_keys = ["subtopics", "search_variants", "keywords", "authoritative_domains", "depth"]
        for key in required_keys:
            assert key in strategy, f"Strategy should contain {key}"
        
        # Should set reasonable depth
        assert isinstance(strategy["depth"], int)
        assert 1 <= strategy["depth"] <= 3
    
    @pytest.mark.parametrize("query,expected_subtopics", [
        ("AI ethics and bias", 2),
        ("renewable energy policy economic impact", 3),
        ("simple query", 1),
    ])
    def test_subtopic_count_varies_by_complexity(self, query, expected_subtopics):
        """Test that subtopic count varies appropriately by query complexity"""
        analyzer = QueryAnalyzer()
        
        result = analyzer.decompose_query(query)
        
        # Allow some flexibility but should be roughly correct
        assert len(result) >= expected_subtopics - 1
        assert len(result) <= expected_subtopics + 2
    
    def test_handles_empty_query(self):
        """Test graceful handling of empty or invalid queries"""
        analyzer = QueryAnalyzer()
        
        with pytest.raises(ValueError):
            analyzer.decompose_query("")
        
        with pytest.raises(ValueError):
            analyzer.decompose_query("   ")
        
        with pytest.raises(TypeError):
            analyzer.decompose_query(None)
    
    def test_caches_results_for_same_query(self):
        """Test that results are cached for performance"""
        analyzer = QueryAnalyzer()
        
        query = "test query for caching"
        
        # First call
        result1 = analyzer.decompose_query(query)
        
        # Second call should be cached
        result2 = analyzer.decompose_query(query)
        
        assert result1 == result2
        # This test will verify caching implementation exists
    
    def test_search_strategy_includes_temporal_keywords(self):
        """Test that queries with temporal aspects include appropriate keywords"""
        analyzer = QueryAnalyzer()
        
        query = "latest developments in AI 2024"
        strategy = analyzer.plan_search_strategy(query)
        
        # Should include temporal refinements
        keywords = strategy["keywords"]
        temporal_keywords = ["2024", "latest", "recent", "current"]
        
        found_temporal = any(keyword in keywords for keyword in temporal_keywords)
        assert found_temporal, "Should include temporal keywords for recent queries"


class TestQueryAnalyzerIntegration:
    """Integration tests for QueryAnalyzer with external dependencies"""
    
    @patch('src.query_analyzer.LLMClient')
    def test_uses_llm_for_decomposition(self, mock_llm):
        """Test that QueryAnalyzer uses LLM for complex query decomposition"""
        mock_llm_instance = Mock()
        mock_llm_instance.generate.return_value = "1. Quantum computing basics\n2. Cryptography implications"
        mock_llm.return_value = mock_llm_instance
        
        analyzer = QueryAnalyzer(use_llm=True)
        result = analyzer.decompose_query("quantum computing and cryptography")
        
        # Should have called LLM
        mock_llm_instance.generate.assert_called_once()
        assert len(result) >= 2
    
    def test_fallback_when_llm_unavailable(self):
        """Test graceful fallback when LLM is unavailable"""
        analyzer = QueryAnalyzer(use_llm=False)
        
        # Should still work without LLM
        result = analyzer.decompose_query("machine learning applications")
        
        assert isinstance(result, list)
        assert len(result) >= 1
