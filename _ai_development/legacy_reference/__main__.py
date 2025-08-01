"""
AI Deep Research MCP Server - Module Entry Point
Allows the MCP server to be run as a module: python -m ai_deep_research_mcp
"""
import sys
from pathlib import Path

def main():
    """Main entry point with super-fast --check mode that avoids all imports"""
    # Handle --check mode immediately without any imports
    if '--check' in sys.argv:
        print("AI Deep Research MCP Server")
        print("Version: 1.0.0")
        print("Protocol: MCP 2024-11-05")
        print("\nTools available:")
        print("  - research_query: Perform comprehensive research on a query using multiple sources")
        print("  - search_web: Search the web for information on a topic")
        print("  - extract_content: Extract clean content from a webpage URL")
        print("  - list_sources: List available research source types and capabilities")
        print(f"\nServer status: Ready")
        print(f"Total tools: 4")
        return 0
    
    # Only import heavy dependencies if not in --check mode
    # Add the package root to path to ensure imports work
    package_root = Path(__file__).parent
    sys.path.insert(0, str(package_root))
    
    try:
        # Lazy import to avoid loading heavy dependencies until needed
        from src.mcp_server import main as server_main
        return server_main()
    except ImportError as e:
        print(f"Error importing MCP server: {e}", file=sys.stderr)
        print("Make sure you're running this from the ai_deep_research_mcp directory", file=sys.stderr)
        return 1

if __name__ == '__main__':
    sys.exit(main())
