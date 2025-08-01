#!/usr/bin/env python3
"""
AI Deep Research MCP - Query Analyzer Module

This module provides query analysis and search planning capabilities for the
AI Deep Research MCP system. It follows Test-Driven Development (TDD) principles.

The QueryAnalyzer class decomposes complex queries into searchable subtopics,
generates search variants, extracts keywords, and identifies authoritative domains.

IMPLEMENTATION STATUS: REFACTOR Phase - Clean, maintainable code
"""

import re
from typing import List, Dict, Any, Optional, Set
from dataclasses import dataclass
import logging

# Configure logging
logger = logging.getLogger(__name__)


@dataclass
class SearchStrategy:
    """Represents a comprehensive search strategy for a query"""
    subtopics: List[str]
    search_variants: List[str]
    keywords: List[str]
    authoritative_domains: List[str]
    depth: int


class QueryAnalyzer:
    """
    Analyzes user queries and creates comprehensive search strategies.
    
    This class decomposes complex queries into searchable subtopics,
    generates search variants, extracts keywords, and identifies
    authoritative domains for academic research.
    
    Features:
    - Rule-based and LLM-powered query decomposition
    - Academic domain identification
    - Search variant generation
    - Keyword extraction with phrase detection
    - Result caching for performance
    """
    
    # Class constants for better maintainability
    ACADEMIC_DOMAINS = [
        ".edu", "scholar.google.com", "arxiv.org", "pubmed.ncbi.nlm.nih.gov",
        "ieee.org", "acm.org", "springer.com", "sciencedirect.com",
        "jstor.org", "researchgate.net", "nature.com", "science.org"
    ]
    
    STOPWORDS = {
        "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
        "of", "with", "by", "is", "are", "was", "were", "be", "been", "being",
        "have", "has", "had", "do", "does", "did", "will", "would", "could",
        "should", "may", "might", "can", "about", "what", "how", "when", "where"
    }
    
    TECHNICAL_PHRASES = [
        "machine learning", "artificial intelligence", "neural networks",
        "deep learning", "computer vision", "natural language processing",
        "quantum computing", "climate change", "renewable energy",
        "image recognition", "data analysis", "research methodology"
    ]
    
    QUERY_SEPARATORS = [" and ", " or ", " vs ", " versus ", " in ", " for ", " on ", " of "]
    
    def __init__(self, use_llm: bool = False):
        """
        Initialize the QueryAnalyzer.
        
        Args:
            use_llm: Whether to use LLM for query decomposition
        """
        self.use_llm = use_llm
        self._cache: Dict[str, List[str]] = {}
        self._llm_client: Optional['LLMClient'] = None
        
        if use_llm:
            try:
                self._llm_client = LLMClient()
                logger.info("LLM client initialized for query analysis")
            except Exception as e:
                logger.warning(f"Failed to initialize LLM client: {e}")
                self._llm_client = None
    
    def decompose_query(self, query: str) -> List[str]:
        """
        Decompose a complex query into subtopics.
        
        Args:
            query: The input query string
            
        Returns:
            List of subtopic strings
            
        Raises:
            ValueError: If query is empty or whitespace only
            TypeError: If query is not a string
        """
        self._validate_query(query)
        query = query.strip()
        
        # Check cache first  
        if query in self._cache:
            logger.debug(f"Retrieved cached decomposition for query: {query[:50]}...")
            return self._cache[query]
        
        # Try LLM decomposition first if enabled
        subtopics = self._llm_decomposition(query) if self.use_llm else []
        
        # Fall back to rule-based decomposition
        if not subtopics:
            subtopics = self._rule_based_decomposition(query)
        
        # Cache and return result
        self._cache[query] = subtopics
        logger.debug(f"Decomposed query into {len(subtopics)} subtopics")
        return subtopics
    
    def _validate_query(self, query: Any) -> None:
        """Validate query input"""
        if query is None:
            raise TypeError("Query cannot be None")
        
        if not isinstance(query, str):
            raise TypeError("Query must be a string")
            
        if not query.strip():
            raise ValueError("Query cannot be empty")
    
    def _llm_decomposition(self, query: str) -> List[str]:
        """Use LLM for query decomposition"""
        if not self._llm_client:
            return []
        
        try:
            response = self._llm_client.generate(f"Decompose this query into subtopics: {query}")
            return self._parse_llm_response(response)
        except Exception as e:
            logger.warning(f"LLM decomposition failed: {e}")
            return []
    
    def _parse_llm_response(self, response: str) -> List[str]:
        """Parse LLM response into subtopics"""
        subtopics = []
        lines = response.split('\n')
        
        for line in lines:
            line = line.strip()
            if line and line.startswith(('1.', '2.', '3.', '-', '*')):
                subtopic = re.sub(r'^[\d\.\-\*\s]+', '', line).strip()
                if subtopic and len(subtopic) > 5:
                    subtopics.append(subtopic)
                    
        return subtopics
    
    
    def _rule_based_decomposition(self, query: str) -> List[str]:
        """Rule-based query decomposition without LLM"""
        # Start with the full query
        current_topics = [query]
        
        # Split on conjunctions that indicate multiple concepts
        for separator in self.QUERY_SEPARATORS:
            current_topics = self._split_topics_by_separator(current_topics, separator)
        
        # Handle complex multi-word phrases
        if len(query.split()) >= 4:
            concept_topics = self._extract_concept_topics(query)
            if len(concept_topics) > 1:
                current_topics = concept_topics
        
        # Clean and deduplicate topics
        return self._clean_topics(current_topics, query)
    
    def _split_topics_by_separator(self, topics: List[str], separator: str) -> List[str]:
        """Split topics by a given separator"""
        new_topics = []
        for topic in topics:
            if separator in topic.lower():
                parts = [part.strip() for part in topic.split(separator) if part.strip()]
                new_topics.extend(parts if len(parts) > 1 else [topic])
            else:
                new_topics.append(topic)
        return new_topics
    
    def _extract_concept_topics(self, query: str) -> List[str]:
        """Extract key concepts from complex queries"""
        concepts = []
        query_words = query.split()
        query_lower = query.lower()
        
        # Look for compound terms and concepts
        concept_patterns = [
            (["energy"], ["renewable", "solar", "wind"], "renewable energy"),
            (["policy"], ["energy"], "energy policy"),
            (["economic"], ["impact"], "economic impact"),
            (["climate"], ["change"], "climate change"),
            (["machine", "artificial"], ["learning", "intelligence"], "AI and ML"),
        ]
        
        for required_words, context_words, concept_name in concept_patterns:
            if (any(word in query_words for word in required_words) and 
                any(word in query_words for word in context_words)):
                concepts.append(concept_name)
        
        return concepts if concepts else [query]
    
    def _clean_topics(self, topics: List[str], original_query: str) -> List[str]:
        """Clean and deduplicate topic list"""
        cleaned_topics = []
        seen: Set[str] = set()
        
        for topic in topics:
            topic = topic.strip()
            if len(topic) > 5 and topic not in seen:
                cleaned_topics.append(topic)
                seen.add(topic)
        
        # Ensure we have at least one subtopic
        return cleaned_topics if cleaned_topics else [original_query]
    
    def generate_search_variants(self, query: str) -> List[str]:
        """
        Generate multiple search query variants.
        
        Args:
            query: The input query
            
        Returns:
            List of search variants including the original
        """
        variants = [query]  # Always include original
        
        # Add temporal variants
        variants.extend(self._generate_temporal_variants(query))
        
        # Add academic variants
        variants.extend(self._generate_academic_variants(query))
        
        # Remove duplicates while preserving order
        return self._deduplicate_list(variants)
    
    def _generate_temporal_variants(self, query: str) -> List[str]:
        """Generate time-based query variants"""
        variants = []
        query_lower = query.lower()
        
        if "latest" in query_lower or "recent" in query_lower:
            variants.append(query.replace("latest", "current").replace("recent", "new"))
            variants.append(f"{query} 2024")
        
        return variants
    
    def _generate_academic_variants(self, query: str) -> List[str]:
        """Generate academic-focused query variants"""
        variants = []
        query_lower = query.lower()
        
        if "research" not in query_lower:
            variants.extend([f"{query} research", f"research on {query}"])
        
        variants.extend([f"{query} study", f"{query} analysis"])
        return variants
    
    def _deduplicate_list(self, items: List[str]) -> List[str]:
        """Remove duplicates while preserving order"""
        unique_items = []
        seen: Set[str] = set()
        
        for item in items:
            if item not in seen:
                unique_items.append(item)
                seen.add(item)
                
        return unique_items
    
    def extract_keywords(self, query: str) -> List[str]:
        """
        Extract meaningful keywords from query.
        
        Args:
            query: The input query
            
        Returns:
            List of extracted keywords
        """
        # Extract individual words
        words = self._extract_words(query)
        
        # Extract technical phrases
        phrases = self._extract_phrases(query)
        
        # Combine and deduplicate
        return self._deduplicate_list(words + phrases)
    
    def _extract_words(self, query: str) -> List[str]:
        """Extract individual meaningful words"""
        words = re.findall(r'\b\w+\b', query.lower())
        return [word for word in words 
                if word not in self.STOPWORDS and len(word) > 2]
    
    def _extract_phrases(self, query: str) -> List[str]:
        """Extract meaningful technical phrases"""
        query_lower = query.lower()
        return [phrase for phrase in self.TECHNICAL_PHRASES 
                if phrase in query_lower]
    
    def identify_authoritative_domains(self, query: str) -> List[str]:
        """
        Identify authoritative domains for the query.
        
        Args:
            query: The input query
            
        Returns:
            List of authoritative domain patterns
        """
        domains = [".edu", "scholar.google.com"]  # Base academic domains
        query_lower = query.lower()
        
        # Add domain-specific authorities
        domain_mappings = [
            (["research", "study", "paper", "academic", "peer reviewed"], 
             ["arxiv.org", "pubmed.ncbi.nlm.nih.gov", "ieee.org"]),
            (["medical", "health", "clinical", "disease"], 
             ["pubmed.ncbi.nlm.nih.gov", "who.int", "cdc.gov"]),
            (["technology", "computer", "software", "ai", "ml"], 
             ["arxiv.org", "ieee.org", "acm.org"]),
            (["science", "physics", "chemistry", "biology"], 
             ["nature.com", "science.org", "springer.com"]),
        ]
        
        for keywords, auth_domains in domain_mappings:
            if any(keyword in query_lower for keyword in keywords):
                domains.extend(auth_domains)
        
        return self._deduplicate_list(domains)
    
    def plan_search_strategy(self, query: str) -> Dict[str, Any]:
        """
        Create a comprehensive search strategy.
        
        Args:
            query: The input query
            
        Returns:
            Dictionary containing search strategy components
        """
        return {
            "subtopics": self.decompose_query(query),
            "search_variants": self.generate_search_variants(query),
            "keywords": self.extract_keywords(query),
            "authoritative_domains": self.identify_authoritative_domains(query),
            "depth": self._calculate_search_depth(query)
        }
    
    def _calculate_search_depth(self, query: str) -> int:
        """Calculate appropriate search depth based on query complexity"""
        subtopics = self.decompose_query(query)
        query_lower = query.lower()
        
        # Base depth
        depth = 1
        
        # Increase for complex queries
        if len(subtopics) > 2:
            depth = 2
            
        # Increase for comprehensive analysis requests
        comprehensive_terms = ["comprehensive", "detailed", "thorough", "exhaustive", "complete analysis"]
        if any(term in query_lower for term in comprehensive_terms):
            depth = min(depth + 1, 3)  # Cap at 3
            
        return depth


class LLMClient:
    """Mock LLM client for testing and development"""
    
    def generate(self, prompt: str) -> str:
        """Generate response to prompt"""
        # Simple rule-based responses for testing
        if "decompose" in prompt.lower() and "quantum computing" in prompt.lower():
            return "1. Quantum computing basics\n2. Cryptography implications"
        return "Mock LLM response"
