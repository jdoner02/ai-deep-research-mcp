# AI Deep Research MCP

![Tests](https://github.com/jdoner02/ai-deep-research-mcp/workflows/Test%20Suite/badge.svg)
![GitHub Pages](https://github.com/jdoner02/ai-deep-research-mcp/workflows/Deploy%20to%20GitHub%20Pages/badge.svg)
![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

**AI-powered deep research system with arXiv, Google Scholar, and Semantic Scholar integration**

🚀 **[Live Demo on GitHub Pages](https://jdoner02.github.io/ai-deep-research-mcp/)**

## Overview

AI Deep Research MCP is a comprehensive, self-hosted research system that mirrors the capabilities of Firecrawl's Deep Research tier. It autonomously crawls scholarly databases, processes academic papers, and generates detailed research summaries with proper citations.

### Key Features

- 🎓 **Multi-Source Integration**: arXiv, Google Scholar, Semantic Scholar, and web sources
- 📄 **PDF Processing**: Automatic download and text extraction from academic papers
- 🔍 **Intelligent Search**: Query decomposition and multi-strategy search approaches
- 📝 **Citation Management**: APA, MLA, Chicago, and IEEE citation formats
- 🌐 **GitHub Pages Ready**: Client-side interface for public deployment
- 🧪 **Test-Driven Development**: 181 comprehensive tests with 100% pass rate

## Quick Start

### GitHub Pages (No Installation Required)

Visit **[https://jdoner02.github.io/ai-deep-research-mcp/](https://jdoner02.github.io/ai-deep-research-mcp/)** to use the research engine directly in your browser.

### Local Installation

```bash
# Clone the repository
git clone https://github.com/jdoner02/ai-deep-research-mcp.git
cd ai-deep-research-mcp

# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Start the web interface
cd web_interface
npm install
npm start
```

## Architecture

The system follows a modular architecture with the following components:

### Core Components

- **Query Analyzer**: Decomposes complex queries into searchable sub-topics
- **Scholarly Sources**: Integrates with arXiv, Google Scholar, and Semantic Scholar APIs
- **Web Crawler**: Intelligent crawling with rate limiting and content extraction
- **Document Parser**: Multi-format parsing (HTML, PDF, Markdown, JSON)
- **Vector Store**: Semantic indexing using ChromaDB or FAISS
- **LLM Client**: Integration with language models for synthesis
- **Citation Manager**: Academic citation formatting and bibliography generation

### Data Flow

```
Query → Analysis → Multi-Source Search → Document Processing → 
Semantic Indexing → Retrieval → LLM Synthesis → Formatted Response
```

## Scholarly Source Integration

### arXiv Integration
```python
from src.scholarly_sources import ArxivSearcher

searcher = ArxivSearcher()
papers = searcher.search("machine learning", max_results=10)
```

### Google Scholar Integration
```python
from src.scholarly_sources import GoogleScholarSearcher

searcher = GoogleScholarSearcher()
papers = searcher.search("neural networks", max_results=5)
```

### Semantic Scholar Integration
```python
from src.scholarly_sources import SemanticScholarSearcher

searcher = SemanticScholarSearcher()
papers = searcher.search("deep learning", max_results=8)
```

### Unified Search
```python
from src.scholarly_sources import UnifiedScholarlySearcher

searcher = UnifiedScholarlySearcher()
papers = searcher.search("artificial intelligence", max_results=20)
```

## Citation Management

The system supports multiple academic citation formats:

```python
from src.citation_manager import CitationManager, CitationStyle

citation_manager = CitationManager()

# Format academic paper citation
apa_citation = citation_manager.format_academic_citation(paper_data, CitationStyle.APA)
mla_citation = citation_manager.format_academic_citation(paper_data, CitationStyle.MLA)
```

## API Usage

### Complete Research Workflow

```python
from src.api_orchestrator import APIOrchestrator, ResearchRequest

orchestrator = APIOrchestrator()

request = ResearchRequest(
    query="quantum computing applications in cryptography",
    max_sources=15,
    citation_style="APA",
    max_depth=2
)

async def progress_callback(progress):
    print(f"Progress: {progress.stage} - {progress.message}")

response = await orchestrator.conduct_research(request, progress_callback)

print(f"Answer: {response.answer}")
print(f"Sources: {len(response.sources)}")
print(f"Execution time: {response.execution_time:.2f}s")
```

## GitHub Pages Deployment

The system includes a complete GitHub Pages setup for public deployment:

### Features
- **Client-side JavaScript**: Full research functionality in the browser
- **Responsive Design**: Works on desktop and mobile devices
- **Real-time Progress**: Live updates during research process
- **Export Options**: JSON and PDF export capabilities
- **Citation Display**: Properly formatted academic citations

### Deployment
1. Fork this repository
2. Enable GitHub Pages in repository settings
3. Select "GitHub Actions" as the source
4. The site will be automatically deployed at `https://yourusername.github.io/ai-deep-research-mcp/`

## Development

### Project Structure

```
ai_deep_research_mcp/
├── src/                          # Core Python modules
│   ├── scholarly_sources.py     # Academic database integration
│   ├── web_search.py            # Enhanced web search
│   ├── citation_manager.py     # Citation formatting
│   ├── api_orchestrator.py     # Main orchestration
│   └── ...
├── tests/                       # Comprehensive test suite
├── docs/                        # GitHub Pages site
│   ├── index.html              # Main interface
│   ├── js/                     # Client-side functionality
│   └── _config.yml             # Jekyll configuration
├── web_interface/              # Node.js web server
├── .github/workflows/          # CI/CD pipelines
└── README.md
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=src --cov-report=html

# Run specific test categories
pytest tests/test_scholarly_integration.py
pytest tests/test_github_pages_integration.py
```

### Test Coverage

The project maintains comprehensive test coverage:

- **181 total tests** with 100% pass rate
- **Unit tests** for all core components
- **Integration tests** for scholarly sources
- **End-to-end tests** for complete workflows
- **GitHub Pages tests** for deployment readiness

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Add tests for new functionality
4. Ensure all tests pass (`pytest`)
5. Commit changes (`git commit -m 'Add amazing feature'`)
6. Push to branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

### Development Principles

- **Test-Driven Development**: All features must have comprehensive tests
- **Modular Architecture**: Clean separation of concerns
- **Academic Standards**: Proper citation and research methodologies
- **Performance**: Efficient crawling and processing
- **Reliability**: Robust error handling and fallbacks

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- Built following the architectural principles described in the AI Deep Research MCP specification
- Inspired by Firecrawl's Deep Research capabilities
- Developed using Test-Driven Development methodology
- Academic source integrations respect API guidelines and rate limits

## Research Ethics

This tool is designed for academic and research purposes. Users should:

- Respect the terms of service of scholarly databases
- Properly cite all sources in their work  
- Use rate limiting to avoid overwhelming servers
- Comply with copyright and fair use guidelines

---

**🚀 [Try the live demo](https://jdoner02.github.io/ai-deep-research-mcp/) | 📚 [Read the docs](docs/) | 🐛 [Report issues](issues/)**
