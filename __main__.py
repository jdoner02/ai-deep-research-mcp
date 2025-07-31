"""
AI Deep Research MCP Server - Module Entry Point
Allows the MCP server to be run as a module: python -m ai_deep_research_mcp
"""
import sys
from pathlib import Path

# Add the package root to path to ensure imports work
package_root = Path(__file__).parent
sys.path.insert(0, str(package_root))

# Import and run the main server function
try:
    from src.mcp_server import main
    if __name__ == '__main__':
        sys.exit(main())
except ImportError as e:
    print(f"Error importing MCP server: {e}", file=sys.stderr)
    print("Make sure you're running this from the ai_deep_research_mcp directory", file=sys.stderr)
    sys.exit(1)
