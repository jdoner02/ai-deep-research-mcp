"""
AI Deep Research MCP - Source Package

This package contains the core components of the AI Deep Research MCP system,
implementing a self-hosted, AI-powered deep research system similar to 
Firecrawl's Deep Research tier.

Components:
- query_analyzer: Query decomposition and search planning
- web_crawler: Intelligent web crawling with headless browsing
- document_parser: Multi-format document parsing and content extraction
- embedder: Text chunking and semantic embedding
- vector_store: Semantic search and retrieval
- retriever: Semantic search and retrieval management
- llm_client: LLM integration and response generation
- citation_manager: Citation formatting and management
- api_orchestrator: Orchestrates the complete research workflow

Developed following Test-Driven Development (TDD) principles.
"""

__version__ = "0.1.0"
__author__ = "Test Guardian Agent"

# Import strategy: Try each module individually and collect available classes
# This ensures maximum compatibility and clear error tracking

# Query Analyzer
try:
    from .query_analyzer import QueryAnalyzer, SearchStrategy
except ImportError:
    QueryAnalyzer = None
    SearchStrategy = None

# Web Crawler
try:
    from .web_crawler import WebCrawler, CrawlResult
except ImportError:
    WebCrawler = None
    CrawlResult = None

# Document Parser
try:
    from .document_parser import DocumentParser, ParsedDocument
except ImportError:
    DocumentParser = None
    ParsedDocument = None

# Embedder
try:
    from .embedder import Embedder, EmbeddedChunk, TextChunk
except ImportError:
    Embedder = None
    EmbeddedChunk = None
    TextChunk = None

# Vector Store
try:
    from .vector_store import VectorStore, StoredChunk, SearchResult
except ImportError:
    VectorStore = None
    StoredChunk = None
    SearchResult = None

# Retriever
try:
    from .retriever import Retriever, RetrievalResult, SearchContext
except ImportError:
    Retriever = None
    RetrievalResult = None
    SearchContext = None

# LLM Client
try:
    from .llm_client import (
        LLMClient, GenerationResponse, ChatMessage, TokenUsage, 
        LLMConfig, MessageRole, GenerationError
    )
except ImportError:
    LLMClient = None
    GenerationResponse = None
    ChatMessage = None
    TokenUsage = None
    LLMConfig = None
    MessageRole = None
    GenerationError = None

# Citation Manager
try:
    from .citation_manager import (
        CitationManager, SourceInfo, Citation, CitationStyle,
        CiteError
    )
except ImportError:
    CitationManager = None
    SourceInfo = None
    Citation = None
    CitationStyle = None
    CiteError = None

# API Orchestrator
try:
    from .api_orchestrator import (
        APIOrchestrator, ResearchRequest, ResearchResponse, 
        ResearchProgress, ResearchStage, OrchestrationError
    )
except ImportError:
    APIOrchestrator = None
    ResearchRequest = None
    ResearchResponse = None
    ResearchProgress = None
    ResearchStage = None
    OrchestrationError = None

# Define what gets imported with "from src import *"
__all__ = [
    # Core classes
    'QueryAnalyzer', 'SearchStrategy',
    'WebCrawler', 'CrawlResult',
    'DocumentParser', 'ParsedDocument',
    'Embedder', 'EmbeddedChunk', 'TextChunk',
    'VectorStore', 'StoredChunk', 'SearchResult',
    'Retriever', 'RetrievalResult', 'SearchContext',
    'LLMClient', 'GenerationResponse', 'ChatMessage', 'TokenUsage', 'LLMConfig', 'MessageRole', 'GenerationError',
    'CitationManager', 'SourceInfo', 'Citation', 'CitationStyle', 'CiteError',
    'APIOrchestrator', 'ResearchRequest', 'ResearchResponse', 'ResearchProgress', 'ResearchStage', 'OrchestrationError'
]
