"""
Test configuration and fixtures for AI Deep Research MCP

This file configures pytest for our educational research platform,
providing shared fixtures and setup for all tests.

Educational Note for Students:
conftest.py is pytest's "shared testing setup" file - like having
a toolbox that all your test rooms can share!
"""

import os
import sys
from pathlib import Path

# Add the project root to Python path so imports work correctly
# This is like telling Python "hey, our main code is up here!"
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# Also add the src directory explicitly for clean imports
src_path = project_root / "src"
if src_path.exists():
    sys.path.insert(0, str(src_path))

# Ensure we're not accidentally importing from legacy backup
legacy_path = project_root / "_ai_development" / "legacy_reference"
if str(legacy_path) in sys.path:
    sys.path.remove(str(legacy_path))

print(f"✅ Test setup complete - Python can now find our code!")
print(f"   Project root: {project_root}")
print(f"   Source path: {src_path}")
print(f"   Python path: {sys.path[:3]}...")  # Show first 3 entries

# Shared test fixtures will go here
from unittest.mock import AsyncMock, Mock

import pytest

# Global test fixtures that all tests can use
# Think of these as "test helpers" available everywhere!


@pytest.fixture
def mock_api_response():
    """A fake API response for testing without hitting real servers"""
    return {
        "status": "success",
        "data": {
            "title": "Test Research Paper",
            "abstract": "This is a test abstract for educational purposes.",
            "authors": ["Dr. Test", "Prof. Example"],
            "published_date": "2024-01-01",
        },
    }


@pytest.fixture
def sample_research_query():
    """A sample research query for testing our search functionality"""
    return {
        "query": "artificial intelligence education",
        "max_results": 10,
        "source_types": ["arxiv", "semantic_scholar"],
    }
