"""
Pytest configuration file to fix import paths for the AI Deep Research MCP project.

This file is automatically loaded by pytest and ensures that the src package
can be imported correctly during test execution.
"""
import sys
from pathlib import Path

# Add the project root to Python path so 'src' package can be imported
project_root = Path(__file__).parent
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

# Ensure we can import from src
try:
    import src
    print(f"✅ src package imported successfully from {project_root}")
except ImportError as e:
    print(f"❌ Failed to import src package: {e}")
    # Don't fail here, let individual tests handle the import errors
