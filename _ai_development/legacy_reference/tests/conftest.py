"""
Test configuration and fixtures for AI Deep Research MCP system

This file contains pytest configuration and shared fixtures used across
all test modules in the Test Guardian Agent implementation.
"""

import pytest
import tempfile
import shutil
from pathlib import Path
from unittest.mock import Mock


@pytest.fixture
def temp_dir():
    """Create a temporary directory for test files"""
    temp_path = tempfile.mkdtemp()
    yield Path(temp_path)
    shutil.rmtree(temp_path)


@pytest.fixture
def mock_llm_client():
    """Mock LLM client for testing without actual LLM calls"""
    mock_client = Mock()
    mock_client.generate.return_value = "Mocked LLM response"
    return mock_client


@pytest.fixture
def sample_documents():
    """Sample documents for testing document processing"""
    return [
        {
            "url": "https://example.com/doc1",
            "title": "AI Research Overview",
            "content": "Artificial intelligence is transforming industries. Machine learning algorithms are becoming more sophisticated."
        },
        {
            "url": "https://arxiv.org/abs/2024.01234",
            "title": "Deep Learning Advances",
            "content": "Recent advances in deep learning include transformer architectures and attention mechanisms."
        }
    ]


@pytest.fixture
def sample_chunks():
    """Sample text chunks for testing embedding and retrieval"""
    return [
        {
            "text": "Machine learning is a subset of artificial intelligence that focuses on algorithms.",
            "source": "https://example.com/ml-intro",
            "chunk_id": "chunk_1"
        },
        {
            "text": "Deep learning uses neural networks with multiple layers to process data.",
            "source": "https://example.com/dl-basics", 
            "chunk_id": "chunk_2"
        }
    ]


@pytest.fixture
def mock_vector_store():
    """Mock vector store for testing retrieval without actual embedding computation"""
    mock_store = Mock()
    mock_store.add_documents.return_value = True
    mock_store.similarity_search.return_value = [
        {"text": "Sample relevant text 1", "source": "source1"},
        {"text": "Sample relevant text 2", "source": "source2"}
    ]
    return mock_store
