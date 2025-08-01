"""
GitHub Repository Setup Script
Test Guardian Agent - GREEN Phase Implementation
"""
import subprocess
import sys
import time
import requests
from pathlib import Path


def check_git_credentials():
    """Check if Git credentials are configured"""
    try:
        result = subprocess.run(['git', 'config', 'user.name'], 
                              capture_output=True, text=True)
        if result.returncode != 0 or not result.stdout.strip():
            print("❌ Git user.name is not configured")
            print("   Run: git config --global user.name 'Your Name'")
            return False
            
        result = subprocess.run(['git', 'config', 'user.email'], 
                              capture_output=True, text=True)
        if result.returncode != 0 or not result.stdout.strip():
            print("❌ Git user.email is not configured")
            print("   Run: git config --global user.email 'your.email@example.com'")
            return False
            
        print("✅ Git credentials are configured")
        return True
    except Exception as e:
        print(f"❌ Error checking Git credentials: {e}")
        return False


def add_github_remote(repo_url):
    """Add GitHub remote to the repository"""
    try:
        # Check if remote already exists
        result = subprocess.run(['git', 'remote', 'get-url', 'origin'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Remote origin already exists: {result.stdout.strip()}")
            return True
            
        # Add remote
        result = subprocess.run(['git', 'remote', 'add', 'origin', repo_url], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ Added remote origin: {repo_url}")
            return True
        else:
            print(f"❌ Failed to add remote: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error adding remote: {e}")
        return False


def push_to_github():
    """Push the repository to GitHub"""
    try:
        print("📤 Pushing to GitHub...")
        result = subprocess.run(['git', 'push', '-u', 'origin', 'main'], 
                              capture_output=True, text=True)
        if result.returncode == 0:
            print("✅ Successfully pushed to GitHub")
            return True
        else:
            print(f"❌ Failed to push: {result.stderr}")
            return False
    except Exception as e:
        print(f"❌ Error pushing to GitHub: {e}")
        return False


def check_github_repository_exists(repo_url):
    """Check if GitHub repository exists and is accessible"""
    try:
        # Convert git URL to API URL
        if repo_url.startswith('https://github.com/'):
            api_url = repo_url.replace('https://github.com/', 'https://api.github.com/repos/')
            if api_url.endswith('.git'):
                api_url = api_url[:-4]  # Remove .git extension
        else:
            print(f"❌ Unsupported repository URL format: {repo_url}")
            return False
            
        response = requests.get(api_url, timeout=10)
        if response.status_code == 200:
            print("✅ GitHub repository exists and is accessible")
            return True
        elif response.status_code == 404:
            print("❌ GitHub repository does not exist")
            print(f"   Please create repository at: {repo_url}")
            return False
        else:
            print(f"❌ Error checking repository: HTTP {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Error checking repository: {e}")
        return False


def wait_for_github_pages_deployment():
    """Wait for GitHub Pages to deploy"""
    pages_url = "https://jdoner02.github.io/ai-deep-research-mcp/"
    print(f"🕐 Waiting for GitHub Pages deployment at {pages_url}")
    
    for attempt in range(20):  # Wait up to 10 minutes
        try:
            response = requests.get(pages_url, timeout=10)
            if response.status_code == 200:
                print("✅ GitHub Pages is live!")
                return True
        except Exception:
            pass
            
        print(f"   Attempt {attempt + 1}/20: Waiting for deployment...")
        time.sleep(30)  # Wait 30 seconds between checks
    
    print("⏰ GitHub Pages deployment is taking longer than expected")
    print("   This is normal for first deployments. Check the Actions tab in GitHub.")
    return False


def setup_github_repository():
    """Main setup function for GitHub repository"""
    print("🚀 Setting up GitHub repository for AI Deep Research MCP...")
    print()
    
    # Check prerequisites
    if not check_git_credentials():
        return False
    
    repo_url = "https://github.com/jdoner02/ai-deep-research-mcp.git"
    
    # Step 1: Check if repository exists on GitHub
    if not check_github_repository_exists(repo_url):
        print()
        print("📋 MANUAL STEP REQUIRED:")
        print("1. Go to https://github.com")
        print("2. Click 'New repository'")
        print("3. Repository name: ai-deep-research-mcp")
        print("4. Owner: jdoner02")
        print("5. Make it Public")
        print("6. Do NOT initialize with README, .gitignore, or license (we have them)")
        print("7. Click 'Create repository'")
        print()
        print("Then run this script again.")
        return False
    
    # Step 2: Add remote and push
    if not add_github_remote(repo_url):
        return False
    
    if not push_to_github():
        return False
    
    # Step 3: Wait for GitHub Pages deployment
    print()
    print("🌐 GitHub Pages will be automatically deployed via GitHub Actions")
    print("   Check: https://github.com/jdoner02/ai-deep-research-mcp/actions")
    
    # Optional: Wait for deployment
    wait_for_github_pages_deployment()
    
    print()
    print("🎉 Setup complete! Your research system should be available at:")
    print("   https://jdoner02.github.io/ai-deep-research-mcp/")
    print()
    print("📊 To verify deployment, run:")
    print("   python -m pytest tests/test_github_deployment.py -v")
    
    return True


if __name__ == "__main__":
    success = setup_github_repository()
    sys.exit(0 if success else 1)
