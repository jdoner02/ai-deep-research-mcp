# 📚 Scholarly Sources - Complete Usage Guide

**Updated**: July 31, 2025  
**Status**: FULLY IMPLEMENTED ✅  
**Educational Level**: Middle School to Professional

---

## 🎯 What You'll Learn

This guide shows you how to use our **real, working** scholarly source integration to search academic databases like arXiv and Semantic Scholar. You'll learn professional patterns for accessing academic research programmatically.

---

## 🚀 Quick Start Examples

### Example 1: Simple arXiv Search

```python
# Search arXiv for machine learning papers
from src.infrastructure import ArxivSearcher

searcher = ArxivSearcher()
papers = searcher.search("machine learning", max_results=5)

print(f"Found {len(papers)} papers from arXiv:")
for i, paper in enumerate(papers, 1):
    print(f"{i}. {paper['title']}")
    print(f"   Authors: {', '.join(paper['authors'])}")
    print(f"   Published: {paper['published']}")
    print(f"   PDF: {paper['pdf_url']}")
    print()
```

**What this does:**
- Connects to the real arXiv database
- Searches for papers about machine learning
- Gets actual academic papers with real authors and URLs
- Shows you professional API usage patterns

### Example 2: Semantic Scholar with Citations

```python
# Search Semantic Scholar for deep learning papers with citation counts
from src.infrastructure import SemanticScholarSearcher

searcher = SemanticScholarSearcher()
papers = searcher.search("deep learning", max_results=3)

print("Top Deep Learning Papers by Citation Count:")
for i, paper in enumerate(papers, 1):
    citations = paper.get('citation_count', 'Unknown')
    print(f"{i}. {paper['title'][:60]}...")
    print(f"   Citations: {citations}")
    print(f"   Year: {paper.get('year', 'Unknown')}")
    print(f"   Venue: {paper.get('venue', 'Unknown')}")
    print()
```

**What this does:**
- Uses the Semantic Scholar API (real academic database)
- Gets citation counts (how many times papers have been referenced)
- Shows recent research trends in deep learning
- Demonstrates professional data handling

### Example 3: Multi-Source Research

```python
# Search multiple academic databases at once
from src.infrastructure import UnifiedScholarlySearcher

searcher = UnifiedScholarlySearcher()
papers = searcher.search("neural networks", max_results=8)

print(f"Found {len(papers)} unique papers from multiple sources:")

# Group by source type
by_source = {}
for paper in papers:
    source = paper['source_type']
    if source not in by_source:
        by_source[source] = []
    by_source[source].append(paper)

for source, source_papers in by_source.items():
    print(f"\n📚 From {source.upper()}:")
    for paper in source_papers[:3]:  # Show first 3 from each source
        print(f"  • {paper['title'][:50]}...")
```

**What this does:**
- Searches both arXiv AND Semantic Scholar simultaneously
- Removes duplicate papers automatically
- Groups results by database source
- Shows how to handle multiple data sources professionally

---

## 🔬 Advanced Usage Patterns

### Pattern 1: Research Topic Analysis

```python
# Analyze research trends across multiple queries
from src.infrastructure import UnifiedScholarlySearcher

def analyze_research_topic(topic, subtopics):
    """Analyze a research topic by searching multiple subtopics"""
    searcher = UnifiedScholarlySearcher()
    
    all_papers = []
    for subtopic in subtopics:
        query = f"{topic} {subtopic}"
        papers = searcher.search(query, max_results=5)
        all_papers.extend(papers)
        print(f"📖 Found {len(papers)} papers for '{query}'")
    
    # Analyze by year
    years = [p.get('year') for p in all_papers if p.get('year')]
    if years:
        avg_year = sum(years) / len(years)
        print(f"📅 Average publication year: {avg_year:.1f}")
    
    # Find most cited
    with_citations = [p for p in all_papers if p.get('citation_count')]
    if with_citations:
        most_cited = max(with_citations, key=lambda p: p['citation_count'])
        print(f"🏆 Most cited paper: {most_cited['title'][:50]}... ({most_cited['citation_count']} citations)")
    
    return all_papers

# Example usage
ai_papers = analyze_research_topic(
    "artificial intelligence",
    ["machine learning", "neural networks", "computer vision", "natural language processing"]
)
```

### Pattern 2: Academic Source Validation

```python
# Validate and categorize academic sources
from src.infrastructure import UnifiedScholarlySearcher

def categorize_papers(papers):
    """Categorize papers by academic rigor and recency"""
    categories = {
        'high_impact': [],      # High citations, recent
        'emerging': [],         # Low citations, very recent  
        'foundational': [],     # High citations, older
        'preliminary': []       # Low citations, older
    }
    
    current_year = 2024
    
    for paper in papers:
        year = paper.get('year', current_year)
        citations = paper.get('citation_count', 0)
        
        is_recent = (current_year - year) <= 3
        is_highly_cited = citations > 100
        
        if is_recent and is_highly_cited:
            categories['high_impact'].append(paper)
        elif is_recent and not is_highly_cited:
            categories['emerging'].append(paper)
        elif not is_recent and is_highly_cited:
            categories['foundational'].append(paper)
        else:
            categories['preliminary'].append(paper)
    
    return categories

# Example usage
searcher = UnifiedScholarlySearcher()
papers = searcher.search("transformer neural networks", max_results=15)
categorized = categorize_papers(papers)

for category, category_papers in categorized.items():
    if category_papers:
        print(f"\n📊 {category.replace('_', ' ').title()} Papers ({len(category_papers)}):")
        for paper in category_papers[:2]:  # Show top 2 in each category
            print(f"  • {paper['title'][:60]}...")
```

---

## 🛠️ Professional Integration Patterns

### Pattern 1: Error Handling and Fallbacks

```python
# Professional error handling for production systems
from src.infrastructure import ArxivSearcher, SemanticScholarSearcher
import logging
import time

def robust_academic_search(query, max_results=10):
    """Search with proper error handling and fallbacks"""
    results = []
    
    # Try arXiv first
    try:
        arxiv_searcher = ArxivSearcher()
        arxiv_results = arxiv_searcher.search(query, max_results//2)
        results.extend(arxiv_results)
        logging.info(f"arXiv search successful: {len(arxiv_results)} papers")
    except Exception as e:
        logging.warning(f"arXiv search failed: {e}")
    
    # Try Semantic Scholar as backup/supplement
    try:
        time.sleep(1)  # Respectful rate limiting
        semantic_searcher = SemanticScholarSearcher()
        semantic_results = semantic_searcher.search(query, max_results//2)
        results.extend(semantic_results)
        logging.info(f"Semantic Scholar search successful: {len(semantic_results)} papers")
    except Exception as e:
        logging.warning(f"Semantic Scholar search failed: {e}")
    
    if not results:
        logging.error(f"All academic sources failed for query: {query}")
        return []
    
    return results[:max_results]

# Example usage with logging
logging.basicConfig(level=logging.INFO)
papers = robust_academic_search("quantum computing", max_results=8)
print(f"Robust search found {len(papers)} papers total")
```

### Pattern 2: Caching for Performance

```python
# Simple caching to avoid repeated API calls
from src.infrastructure import UnifiedScholarlySearcher
import json
import os
from datetime import datetime, timedelta

class CachedScholarlySearcher:
    """Wrapper that caches search results to avoid API limits"""
    
    def __init__(self, cache_dir="./cache", cache_hours=24):
        self.searcher = UnifiedScholarlySearcher()
        self.cache_dir = cache_dir
        self.cache_duration = timedelta(hours=cache_hours)
        
        # Create cache directory
        os.makedirs(cache_dir, exist_ok=True)
    
    def search(self, query, max_results=10):
        """Search with caching"""
        cache_key = f"{query.replace(' ', '_')}_{max_results}"
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.json")
        
        # Check if cached result exists and is fresh
        if os.path.exists(cache_file):
            with open(cache_file, 'r') as f:
                cached_data = json.load(f)
            
            cache_time = datetime.fromisoformat(cached_data['timestamp'])
            if datetime.now() - cache_time < self.cache_duration:
                print(f"📁 Using cached results for '{query}'")
                return cached_data['results']
        
        # Perform fresh search
        print(f"🔍 Searching academic databases for '{query}'")
        results = self.searcher.search(query, max_results)
        
        # Save to cache
        cache_data = {
            'timestamp': datetime.now().isoformat(),
            'query': query,
            'results': results
        }
        
        with open(cache_file, 'w') as f:
            json.dump(cache_data, f, indent=2)
        
        return results

# Example usage
cached_searcher = CachedScholarlySearcher()
papers1 = cached_searcher.search("machine learning", max_results=5)  # Fresh search
papers2 = cached_searcher.search("machine learning", max_results=5)  # Cached result
```

---

## 🎓 Educational Exercises

### Exercise 1: Compare Research Areas
Write a program that compares the research activity between two topics by counting papers published in the last 3 years.

### Exercise 2: Citation Analysis
Find the most influential papers in a field by analyzing citation counts across multiple sources.

### Exercise 3: Research Timeline
Create a timeline showing how research in a field has evolved by analyzing publication dates and topics.

### Exercise 4: Author Network Analysis
Track papers from the same authors across different academic databases to understand research collaboration.

---

## 🏆 What You've Learned

After working through these examples, you now understand:

1. **Real API Integration**: How to connect to actual academic databases
2. **Error Handling**: Professional patterns for dealing with service failures
3. **Data Processing**: How to clean, categorize, and analyze academic data
4. **Performance Optimization**: Caching and rate limiting strategies
5. **Research Methodology**: How to analyze academic literature programmatically

---

## 🚀 Next Steps

Ready to build more advanced features? Try:
- Integrating these searches into the web interface
- Building a research paper recommendation system
- Creating academic citation networks
- Developing automated literature review tools

---

**Status**: ✅ All examples tested and working with real academic databases  
**Updated**: July 31, 2025 by Knowledge Librarian  
**Educational Impact**: Students can now perform real academic research programmatically!
