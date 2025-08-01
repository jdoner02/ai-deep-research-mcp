# 🧠 AI Deep Research MCP - Educational Version

*Learn AI, Programming, and Research Systems by Building Real Tools!*

![Python](https://img.shields.io/badge/python-3.9%2B-blue.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)
![Educational](https://img.shields.io/badge/educational-middle%20school%2B-brightgreen.svg)
![AI Research](https://img.shields.io/badge/AI-research%20system-orange.svg)
![Status](https://img.shields.io/badge/status-educational%20complete-success.svg)

---

## ✨ What Makes This Special?

This is a **complete educational transformation** of a professional AI research system into the ultimate learning resource for students, educators, and researchers. We've created a comprehensive framework that teaches AI, programming, and software engineering through building a real, functional research system.

> **Perfect for**: Curious middle school students, high school computer science classes, college AI courses, and professors needing research tools.

### 🎓 **Educational Excellence Achieved**

**22+ comprehensive learning modules** with professional analogies that make complex AI research concepts accessible to middle school students while maintaining industry relevance for professors and researchers.

**Key Features**:
- 🔬 **Real-World Analogies**: Healthcare diagnostics, master chef recipes, detective investigations
- 💡 **Hands-On Learning**: 200+ complete code examples with full context  
- 🏗️ **Professional Patterns**: Industry-standard design patterns and best practices
- 📚 **Progressive Complexity**: Builds from simple concepts to enterprise-level systems
- 🎯 **Dual Purpose**: Educational tool AND functional research platform

---

## 🎯 What You'll Learn

### 🐍 **Python Programming**
- Object-oriented programming (classes, inheritance, polymorphism)
- Professional code organization and design patterns
- Error handling and debugging techniques
- Testing and quality assurance

### 🤖 **Artificial Intelligence Concepts**
- How AI "understands" and processes text (Natural Language Processing)
- Vector embeddings and semantic search (how computers find meaning)
- Retrieval-Augmented Generation (RAG) - making AI answers more accurate
- Large Language Models and how they work

### 🏗️ **Software Engineering**
- Professional project structure and organization
- Version control with Git and GitHub
- Continuous Integration/Continuous Deployment (CI/CD)
- Documentation and collaborative development

### 🔬 **Research and Data Science**
- Web scraping and data collection techniques
- Document processing and information extraction
- Database design and vector storage
- Citation management and academic standards

---

## � What You'll Build

By the end of this learning journey, you'll have created a **complete AI research system** that can:

1. **Understand Complex Questions**: Break down research queries into manageable parts
2. **Search the Web Intelligently**: Find relevant academic papers and articles
3. **Process Documents**: Extract and understand information from various sources
4. **Generate Smart Answers**: Use AI to synthesize information with proper citations
5. **Provide Web Interface**: Create a user-friendly way for others to use your system
6. **Work with VS Code**: Function as a tool that GitHub Copilot agents can use

### Real-World Applications
- Academic research assistance
- Fact-checking and verification
- Content creation with citations
- Educational project support
- Professional research workflows

---

## 🗺️ Your Learning Journey

We've organized everything into a progressive learning path that builds from simple concepts to professional-level skills:

### 📚 **Level 1: Foundations** (Start Here!)
- Understanding what the system does and why it's useful
- Basic Python concepts and project setup
- Your first "Hello, Research World!" program

### 🔧 **Level 2: Core Components**  
- Building individual system pieces (web search, document parsing, etc.)
- Learning object-oriented programming through practical examples
- Understanding how different parts work together

### ⚙️ **Level 3: System Integration**
- Connecting components into a working pipeline
- Adding error handling and making the system robust
- Creating tests to ensure everything works correctly

### 🎨 **Level 4: User Interfaces**
- Building a web interface for easy interaction
- Creating APIs for other programs to use
- Making the system accessible and user-friendly

### 🚀 **Level 5: Advanced Features**
- Performance optimization and scaling
- Adding new capabilities and customizations
- Contributing to open source projects

---

## 🛠️ Quick Start Guide

### Prerequisites (Don't worry, we'll help you get set up!)
- Basic computer skills (can navigate files and folders)
- Curiosity about how things work
- Willingness to experiment and learn from mistakes

### Option 1: Try the Legacy Version Online
Visit **[https://jdoner02.github.io/ai-deep-research-mcp/](https://jdoner02.github.io/ai-deep-research-mcp/)** to see what we're building toward!

### Option 2: Install the Educational Version (Recommended!)
```bash
# 1. Clone this repository
git clone https://github.com/jdoner02/ai-deep-research-mcp.git
cd ai-deep-research-mcp

# 2. Start with our guided setup
# Follow: learning_materials/getting_started/installation_guide.md

# 3. Begin your first lesson
python -m learning_materials.lessons.lesson_01_hello_research
```

### Option 3: Explore the Complete Legacy System
```bash
# See the full production system in the legacy/ directory
cd legacy/

# Install dependencies (advanced users)
pip install -r requirements.txt

# Run comprehensive tests
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
from src.infrastructure import ArxivSearcher

searcher = ArxivSearcher()
papers = searcher.search("machine learning", max_results=10)
```

### Google Scholar Integration
```python
from src.infrastructure import GoogleScholarSearcher

searcher = GoogleScholarSearcher()
papers = searcher.search("neural networks", max_results=5)
```

### Semantic Scholar Integration
```python
from src.infrastructure import SemanticScholarSearcher

searcher = SemanticScholarSearcher()
papers = searcher.search("deep learning", max_results=8)
```

### Unified Search
```python
from src.infrastructure import UnifiedScholarlySearcher

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
