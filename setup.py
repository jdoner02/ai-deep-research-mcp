#!/usr/bin/env python3
"""
Development setup script for AI Deep Research MCP
"""
import subprocess
import sys
import os
from pathlib import Path

def install_python_requirements():
    """Install Python dependencies"""
    requirements = [
        "pytest>=7.0.0",
        "pytest-asyncio>=0.21.0",
        "pytest-cov>=4.0.0",
        "requests>=2.31.0",
        "beautifulsoup4>=4.12.0",
        "lxml>=4.9.0",
        "feedparser>=6.0.10",
        "scholarly>=1.7.11",
        "sentence-transformers>=2.2.2",
        "chromadb>=0.4.0",
        "faiss-cpu>=1.7.4",
        "PyPDF2>=3.0.1",
        "python-docx>=0.8.11",
        "ddg-search>=3.0.0",
        "numpy>=1.24.0",
        "aiohttp>=3.8.0",
        "uvicorn>=0.23.0",
        "fastapi>=0.103.0",
        "pydantic>=2.0.0",
        "python-multipart>=0.0.6",
        "jinja2>=3.1.0",
        "markupsafe>=2.1.0"
    ]
    
    print("Installing Python dependencies...")
    for req in requirements:
        print(f"Installing {req}...")
        subprocess.run([sys.executable, "-m", "pip", "install", req], check=True)

def setup_web_interface():
    """Set up Node.js web interface"""
    web_dir = Path("web_interface")
    if web_dir.exists():
        print("Setting up Node.js web interface...")
        os.chdir(web_dir)
        subprocess.run(["npm", "install"], check=True)
        os.chdir("..")

def run_tests():
    """Run the test suite"""
    print("Running test suite...")
    result = subprocess.run([sys.executable, "-m", "pytest", "-v"], capture_output=True, text=True)
    print(result.stdout)
    if result.stderr:
        print("STDERR:", result.stderr)
    return result.returncode == 0

def main():
    """Main setup function"""
    print("🚀 Setting up AI Deep Research MCP...")
    
    try:
        install_python_requirements()
        setup_web_interface()
        
        print("✅ Setup complete!")
        print("\n📊 Running tests to verify installation...")
        
        if run_tests():
            print("✅ All tests passed! System is ready.")
            print("\n🌐 To start the web interface:")
            print("   cd web_interface")
            print("   npm start")
            print("\n📚 To run research queries:")
            print("   python -m src.simple_web_research")
        else:
            print("❌ Some tests failed. Please check the output above.")
            return 1
            
    except subprocess.CalledProcessError as e:
        print(f"❌ Setup failed: {e}")
        return 1
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return 1
    
    return 0

if __name__ == "__main__":
    sys.exit(main())
