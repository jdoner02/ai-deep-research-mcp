#!/usr/bin/env python3
"""
Test script to verify the AI Deep Research MCP system works end-to-end
before launching the web interface.
"""
import sys
import os
import asyncio
from pathlib import Path
import pytest

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

@pytest.mark.asyncio
async def test_research_system():
    try:
        print("🔬 Testing AI Deep Research MCP System...")
        
        from src.api_orchestrator import APIOrchestrator, ResearchRequest
        
        orchestrator = APIOrchestrator()
        
        # Create a simple test request
        request = ResearchRequest(
            query="What is machine learning?",
            max_sources=2,
            max_depth=1,
            citation_style="APA"
        )
        
        print(f"📋 Query: {request.query}")
        print(f"📊 Max Sources: {request.max_sources}")
        print(f"🔍 Max Depth: {request.max_depth}")
        
        # Progress callback
        async def progress_callback(progress):
            print(f"📈 Progress: {progress.stage} - {progress.message}")
        
        print("\n🚀 Starting research...")
        response = await orchestrator.conduct_research(request, progress_callback=progress_callback)
        
        print(f"\n✅ Research completed successfully!")
        print(f"⏱️  Execution time: {response.execution_time:.2f} seconds")
        print(f"📝 Answer length: {len(response.answer)} characters")
        print(f"📚 Sources found: {len(response.sources)}")
        print(f"🎯 Success: {response.success}")
        
        print(f"\n📄 Sample Answer Preview:")
        print(f"{response.answer[:200]}...")
        
        print(f"\n📋 Sources Used:")
        for i, source in enumerate(response.sources_used[:3], 1):
            print(f"  {i}. {source}")
            
        return True
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    success = asyncio.run(test_research_system())
    if success:
        print("\n🎉 System test PASSED! Ready for web interface.")
        sys.exit(0)
    else:
        print("\n💥 System test FAILED! Check the errors above.")
        sys.exit(1)
