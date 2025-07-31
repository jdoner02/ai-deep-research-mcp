"""
Test GitHub Pages deployment and pipeline integration
Following Test Guardian Agent TDD methodology
"""
import pytest
import requests
import subprocess
import os
from pathlib import Path


class TestGitHubIntegration:
    """Test GitHub repository and GitHub Pages deployment"""
    
    def test_git_remote_configured(self):
        """RED: Test that Git remote is configured"""
        result = subprocess.run(['git', 'remote', '-v'], 
                              capture_output=True, text=True)
        assert result.returncode == 0
        assert 'origin' in result.stdout, "Git remote 'origin' should be configured"
        assert 'github.com' in result.stdout, "Remote should point to GitHub"
    
    def test_github_repository_exists(self):
        """RED: Test that GitHub repository exists and is accessible"""
        # This test will fail until repository is created
        repo_url = "https://api.github.com/repos/jdoner02/ai-deep-research-mcp"
        response = requests.get(repo_url)
        assert response.status_code == 200, f"GitHub repository should exist. Got {response.status_code}"
    
    def test_github_pages_configuration_files_exist(self):
        """Test that GitHub Pages files are properly configured"""
        docs_dir = Path("docs")
        assert docs_dir.exists(), "docs/ directory should exist for GitHub Pages"
        
        # Check required files
        assert (docs_dir / "index.html").exists(), "docs/index.html should exist"
        assert (docs_dir / "_config.yml").exists(), "docs/_config.yml should exist"
        assert (docs_dir / "js").exists(), "docs/js/ directory should exist"
        
        # Check JavaScript files
        js_dir = docs_dir / "js"
        required_js_files = [
            "research-engine.js",
            "api-client.js", 
            "citation-formatter.js",
            "ui-controller.js"
        ]
        
        for js_file in required_js_files:
            assert (js_dir / js_file).exists(), f"docs/js/{js_file} should exist"
    
    def test_github_actions_workflow_files_exist(self):
        """Test that GitHub Actions workflow files are configured"""
        workflows_dir = Path(".github/workflows")
        assert workflows_dir.exists(), ".github/workflows/ directory should exist"
        
        # Check required workflow files
        assert (workflows_dir / "deploy-pages.yml").exists(), "deploy-pages.yml workflow should exist"
        assert (workflows_dir / "test.yml").exists(), "test.yml workflow should exist"
    
    @pytest.mark.integration
    def test_github_pages_site_accessibility(self):
        """RED: Test that GitHub Pages site is accessible"""
        # This will fail until deployed
        pages_url = "https://jdoner02.github.io/ai-deep-research-mcp/"
        response = requests.get(pages_url)
        assert response.status_code == 200, f"GitHub Pages site should be accessible. Got {response.status_code}"
        assert "AI Deep Research MCP" in response.text, "Site should contain project title"
    
    def test_repository_structure_for_deployment(self):
        """Test that repository has proper structure for deployment"""
        required_files = [
            "README.md",
            "requirements.txt", 
            "setup.py",
            "LICENSE",
            ".gitignore"
        ]
        
        for file_name in required_files:
            assert Path(file_name).exists(), f"{file_name} should exist for proper deployment"
    
    def test_package_json_in_web_interface(self):
        """Test that web interface has proper Node.js configuration"""
        web_interface_dir = Path("web_interface")
        assert web_interface_dir.exists(), "web_interface/ directory should exist"
        
        package_json = web_interface_dir / "package.json"
        assert package_json.exists(), "web_interface/package.json should exist"
        
        # Verify package.json has required scripts
        import json
        with open(package_json) as f:
            package_data = json.load(f)
        
        assert "scripts" in package_data, "package.json should have scripts section"
        assert "start" in package_data["scripts"], "package.json should have start script"


class TestDeploymentIntegration:
    """Test deployment pipeline integration"""
    
    def test_pytest_configuration(self):
        """Test that pytest is properly configured"""
        # Run pytest to check it works
        result = subprocess.run(['python', '-m', 'pytest', '--version'], 
                              capture_output=True, text=True)
        assert result.returncode == 0, "pytest should be available"
        assert "pytest" in result.stdout.lower(), "Should show pytest version"
    
    def test_can_run_test_suite(self):
        """Test that the test suite can run successfully"""
        # Run a quick test to verify the test environment works - using specific modules to avoid timeouts
        result = subprocess.run(['python', '-m', 'pytest', 'tests/test_scholarly_integration.py', 'tests/test_web_based_research.py', '-v', '--tb=short'], 
                              capture_output=True, text=True, timeout=60)
        
        # Test suite should run (even if some tests fail, pytest should execute)
        assert result.returncode in [0, 1], f"pytest should run successfully. Return code: {result.returncode}"
        assert "test session starts" in result.stdout, "pytest should start test session"
