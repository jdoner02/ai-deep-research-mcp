# 📖 Scholarly Sources API Reference

**Module**: `src.infrastructure.scholarly_sources`  
**Updated**: July 31, 2025  
**Status**: Production Ready ✅

---

## 📚 Classes Overview

### `ScholarlyPaper`
**Type**: Data Class  
**Purpose**: Standardized representation of academic papers

```python
@dataclass
class ScholarlyPaper:
    title: str                              # Paper title
    authors: List[str]                      # List of author names
    abstract: str                           # Paper abstract/summary
    pdf_url: Optional[str] = None          # Direct PDF download URL
    source_url: Optional[str] = None       # Original paper source URL
    published: Optional[str] = None        # Publication date (YYYY-MM-DD)
    citation_count: Optional[int] = None   # Number of citations
    venue: Optional[str] = None            # Journal/conference name
    year: Optional[int] = None             # Publication year
    source_type: str = "academic"          # Source database type
```

---

## 🔍 ArxivSearcher

**Purpose**: Search arXiv database for academic papers  
**Database**: https://arxiv.org/  
**API**: arXiv API (XML feed)

### Methods

#### `__init__(base_url: str = "http://export.arxiv.org/api/query")`
Initialize the arXiv searcher.

**Parameters:**
- `base_url`: arXiv API endpoint (default: official arXiv API)

#### `search(query: str, max_results: int = 10) -> List[Dict]`
Search arXiv for papers matching the query.

**Parameters:**
- `query`: Search query string (natural language)
- `max_results`: Maximum number of results to return (1-100)

**Returns:**
List of paper dictionaries with fields:
- `title`: Paper title
- `authors`: List of author names
- `abstract`: Paper abstract
- `pdf_url`: Direct PDF download URL
- `source_url`: arXiv paper page URL
- `published`: Publication date (YYYY-MM-DD format)
- `venue`: Always "arXiv"
- `source_type`: Always "arxiv"
- `citation_count`: Always None (arXiv doesn't provide citations)

**Example:**
```python
from src.infrastructure import ArxivSearcher

searcher = ArxivSearcher()
papers = searcher.search("quantum computing", max_results=5)

for paper in papers:
    print(f"Title: {paper['title']}")
    print(f"Authors: {', '.join(paper['authors'])}")
    print(f"PDF: {paper['pdf_url']}")
    print(f"Published: {paper['published']}")
    print()
```

**Search Strategies:**
The searcher automatically tries multiple query formats:
1. Exact phrase search: `all:"your query"`
2. AND search: `all:your AND query`
3. Title/abstract search: `ti:"your query" OR abs:"your query"`
4. Simple plus search: `all:your+query`

---

## 🧠 SemanticScholarSearcher

**Purpose**: Search Semantic Scholar API for academic papers  
**Database**: https://www.semanticscholar.org/  
**API**: Semantic Scholar Academic Graph API

### Methods

#### `__init__(api_key: Optional[str] = None)`
Initialize the Semantic Scholar searcher.

**Parameters:**
- `api_key`: Optional Semantic Scholar API key for higher rate limits

**Rate Limiting:**
- Without API key: 1 request per second
- With API key: Higher limits (see Semantic Scholar documentation)

#### `search(query: str, max_results: int = 10) -> List[Dict]`
Search Semantic Scholar for papers matching the query.

**Parameters:**
- `query`: Search query string
- `max_results`: Maximum number of results (1-100, API limited)

**Returns:**
List of paper dictionaries with fields:
- `title`: Paper title
- `authors`: List of author names
- `abstract`: Paper abstract
- `pdf_url`: Open access PDF URL (if available)
- `source_url`: Semantic Scholar paper page URL
- `published`: Publication year as string
- `venue`: Journal or conference name
- `citation_count`: Number of citations
- `source_type`: Always "semantic_scholar"
- `year`: Publication year as integer

**Example:**
```python
from src.infrastructure import SemanticScholarSearcher

# Without API key (rate limited)
searcher = SemanticScholarSearcher()

# With API key (higher limits)
searcher = SemanticScholarSearcher(api_key="your-api-key")

papers = searcher.search("neural networks", max_results=5)

for paper in papers:
    print(f"Title: {paper['title']}")
    print(f"Citations: {paper.get('citation_count', 'Unknown')}")
    print(f"Year: {paper.get('year')}")
    print(f"Venue: {paper.get('venue')}")
    print()
```

---

## 🎓 GoogleScholarSearcher

**Purpose**: Search Google Scholar for academic papers  
**Status**: Placeholder implementation (returns mock data)  
**Database**: https://scholar.google.com/

### Methods

#### `__init__()`
Initialize the Google Scholar searcher.

**Note**: Current implementation returns mock data. For production use, integrate with the `scholarly` Python library or implement web scraping.

#### `search(query: str, max_results: int = 10) -> List[Dict]`
Search Google Scholar (placeholder implementation).

**Returns:** Mock paper data for testing purposes.

---

## 🔗 UnifiedScholarlySearcher

**Purpose**: Search multiple academic databases simultaneously  
**Combines**: arXiv + Semantic Scholar + (Google Scholar)

### Methods

#### `__init__(semantic_scholar_api_key: Optional[str] = None)`
Initialize the unified searcher with all sub-searchers.

**Parameters:**
- `semantic_scholar_api_key`: Optional API key for Semantic Scholar

#### `search(query: str, max_results: int = 20, sources: Optional[List[str]] = None, results_per_source: Optional[int] = None) -> List[Dict]`
Search across multiple scholarly sources.

**Parameters:**
- `query`: Search query string
- `max_results`: Total maximum number of results to return
- `sources`: List of sources to search (default: ['arxiv', 'semantic_scholar'])
- `results_per_source`: Maximum results per source (auto-calculated if None)

**Available Sources:**
- `'arxiv'`: arXiv database
- `'semantic_scholar'`: Semantic Scholar database
- `'google_scholar'`: Google Scholar (mock data)

**Returns:**
List of deduplicated papers from all sources, sorted by citation count.

**Features:**
- **Deduplication**: Removes duplicate papers based on title similarity
- **Source Attribution**: Each result includes `source_type` field
- **Citation Ranking**: Results sorted by citation count (when available)
- **Error Resilience**: Continues if individual sources fail

**Example:**
```python
from src.infrastructure import UnifiedScholarlySearcher

searcher = UnifiedScholarlySearcher()

# Search all sources
papers = searcher.search("machine learning", max_results=10)

# Search specific sources only
papers = searcher.search(
    "deep learning", 
    max_results=15,
    sources=['arxiv', 'semantic_scholar']
)

# Custom results per source
papers = searcher.search(
    "artificial intelligence",
    max_results=20,
    results_per_source=7
)

# Group results by source
by_source = {}
for paper in papers:
    source = paper['source_type']
    if source not in by_source:
        by_source[source] = []
    by_source[source].append(paper)

for source, source_papers in by_source.items():
    print(f"\n{source.upper()}: {len(source_papers)} papers")
```

---

## 📁 PaperProcessor

**Purpose**: Download and process academic papers  
**Formats**: PDF processing (placeholder implementation)

### Methods

#### `__init__()`
Initialize the paper processor.

#### `download_pdf(pdf_url: str, max_size_mb: int = 50) -> Optional[bytes]`
Download PDF content from URL.

**Parameters:**
- `pdf_url`: Direct URL to PDF file
- `max_size_mb`: Maximum file size to download (safety limit)

**Returns:**
- PDF content as bytes if successful
- None if download failed or file too large

**Features:**
- Size checking before and during download
- Stream downloading for memory efficiency
- Error handling and logging
- Respectful User-Agent header

#### `extract_text_from_pdf(pdf_content: bytes) -> Optional[str]`
Extract text from PDF content.

**Status**: Placeholder implementation (returns None)  
**Note**: Requires PyPDF2 or similar library for implementation

**Example:**
```python
from src.infrastructure import PaperProcessor

processor = PaperProcessor()

# Download PDF
pdf_content = processor.download_pdf("https://arxiv.org/pdf/1706.03762.pdf")

if pdf_content:
    print(f"Downloaded PDF: {len(pdf_content)} bytes")
    
    # Extract text (placeholder)
    text = processor.extract_text_from_pdf(pdf_content)
    if text:
        print(f"Extracted text: {len(text)} characters")
```

---

## 🛠️ Error Handling

All searchers implement robust error handling:

- **Network Errors**: Return empty list, log warning
- **API Errors**: Return empty list, log error details
- **Rate Limiting**: Automatic delays between requests
- **Invalid Responses**: Skip malformed entries, continue processing
- **Timeout Handling**: 30-second timeout for all requests

**Logging:**
All components use Python's `logging` module with appropriate levels:
- `INFO`: Successful operations and progress
- `WARNING`: Non-fatal errors, fallbacks
- `ERROR`: Fatal errors, complete failures

---

## 📊 Performance Considerations

### Rate Limits
- **arXiv**: No official rate limit, but be respectful
- **Semantic Scholar**: 1 request/second without API key
- **Unified Search**: Combines delays from all sources

### Caching Recommendations
Implement caching for production use:
```python
# Simple file-based cache example
import json
import os
from datetime import datetime, timedelta

def cached_search(searcher, query, max_results, cache_hours=24):
    cache_file = f"cache_{query.replace(' ', '_')}_{max_results}.json"
    
    if os.path.exists(cache_file):
        with open(cache_file, 'r') as f:
            data = json.load(f)
        
        cache_time = datetime.fromisoformat(data['timestamp'])
        if datetime.now() - cache_time < timedelta(hours=cache_hours):
            return data['results']
    
    # Fresh search
    results = searcher.search(query, max_results)
    
    # Save cache
    with open(cache_file, 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': results
        }, f)
    
    return results
```

### Memory Usage
- Results are returned as dictionaries (not objects) for memory efficiency
- Large abstracts are included in full (no truncation)
- PDF downloading includes size limits to prevent memory issues

---

## 🔗 Integration Examples

### With Existing Research System
```python
from src.infrastructure import UnifiedScholarlySearcher
from src.domain.entities import ResearchQuery, ResearchSource

def create_research_sources_from_papers(papers):
    """Convert scholarly papers to domain entities"""
    sources = []
    
    for paper in papers:
        source = ResearchSource(
            url=paper.get('source_url', ''),
            title=paper.get('title', ''),
            content=paper.get('abstract', ''),
            source_type='academic',
            relevance_score=0.8,  # High relevance for academic sources
            citation_count=paper.get('citation_count', 0)
        )
        sources.append(source)
    
    return sources

# Usage
searcher = UnifiedScholarlySearcher()
papers = searcher.search("artificial intelligence", max_results=10)
sources = create_research_sources_from_papers(papers)
```

### With Web Interface
```python
# Flask/FastAPI endpoint example
from flask import Flask, request, jsonify
from src.infrastructure import UnifiedScholarlySearcher

app = Flask(__name__)
searcher = UnifiedScholarlySearcher()

@app.route('/api/scholarly-search', methods=['POST'])
def scholarly_search():
    data = request.json
    query = data.get('query', '')
    max_results = data.get('max_results', 10)
    sources = data.get('sources', ['arxiv', 'semantic_scholar'])
    
    papers = searcher.search(
        query=query,
        max_results=max_results,
        sources=sources
    )
    
    return jsonify({
        'query': query,
        'results': papers,
        'count': len(papers)
    })
```

---

**Documentation Status**: ✅ Complete and tested  
**Last Updated**: July 31, 2025  
**Knowledge Librarian**: Documentation aligned with implemented functionality
