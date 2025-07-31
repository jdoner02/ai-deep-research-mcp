#!/bin/bash
# AI Deep Research MCP - Production Deployment Script
# Repository Engineer Agent - Professional Deployment

set -e

echo "🚀 AI Deep Research MCP - Production Deployment"
echo "=============================================="

# Configuration
REPO_NAME="ai-deep-research-mcp"
GITHUB_USERNAME="jdoner02"
REPO_URL="https://github.com/${GITHUB_USERNAME}/${REPO_NAME}.git"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m'

print_status() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Check prerequisites
check_prerequisites() {
    print_status "Checking prerequisites..."
    
    # Check git configuration
    if ! git config user.name &> /dev/null; then
        print_error "Git user.name not configured"
        echo "Run: git config --global user.name 'Your Name'"
        exit 1
    fi
    
    if ! git config user.email &> /dev/null; then
        print_error "Git user.email not configured"
        echo "Run: git config --global user.email 'your.email@example.com'"
        exit 1
    fi
    
    print_success "Git configuration verified"
}

# Clean up repository
cleanup_repo() {
    print_status "Cleaning up repository..."
    
    # Remove temporary files
    find . -name "*.pyc" -delete
    find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
    find . -name ".pytest_cache" -type d -exec rm -rf {} + 2>/dev/null || true
    
    # Remove development artifacts
    rm -f .coverage*
    rm -f debug_vector_store.py
    
    # Clean up old TDD reports (move to archive)
    if [ -d "_Test_Guardian_Homebase" ]; then
        mkdir -p _Test_Guardian_Homebase/archive
        mv TDD_*.md _Test_Guardian_Homebase/archive/ 2>/dev/null || true
    fi
    
    print_success "Repository cleaned"
}

# Format code
format_code() {
    print_status "Formatting code..."
    
    # Install formatting tools if not available
    pip install black isort flake8 --quiet
    
    # Format Python code
    black src/ tests/ scripts/ --quiet
    isort src/ tests/ scripts/ --profile black --quiet
    
    # Check code style
    flake8 src/ tests/ --max-line-length=88 --extend-ignore=E203,W503 || {
        print_warning "Code style issues detected - continuing deployment"
    }
    
    print_success "Code formatted"
}

# Run comprehensive tests
run_tests() {
    print_status "Running comprehensive test suite..."
    
    # Run core tests
    python -m pytest tests/test_scholarly_integration.py tests/test_web_based_research.py -v --tb=short
    
    if [ $? -eq 0 ]; then
        print_success "Core tests passed"
    else
        print_error "Tests failed - stopping deployment"
        exit 1
    fi
}

# Setup GitHub remote
setup_github_remote() {
    print_status "Setting up GitHub remote..."
    
    # Check if remote already exists
    if git remote get-url origin &> /dev/null; then
        print_warning "Remote 'origin' already exists"
        CURRENT_URL=$(git remote get-url origin)
        if [ "$CURRENT_URL" != "$REPO_URL" ]; then
            git remote set-url origin "$REPO_URL"
            print_success "Updated remote URL to $REPO_URL"
        fi
    else
        git remote add origin "$REPO_URL"
        print_success "Added remote origin: $REPO_URL"
    fi
}

# Commit and push changes
commit_and_push() {
    print_status "Committing and pushing changes..."
    
    # Add all changes
    git add .
    
    # Check if there are changes to commit
    if git diff --staged --quiet; then
        print_warning "No changes to commit"
    else
        # Commit with professional message
        git commit -m "🚀 Production deployment preparation

Repository Engineering improvements:
- Professional code formatting and cleanup  
- Enhanced development setup scripts
- Comprehensive deployment automation
- Improved repository structure and organization
- Production-ready configuration

Infrastructure updates:
- Automated setup and deployment scripts
- Pre-commit hooks for code quality
- Comprehensive testing pipeline
- Clean repository structure

Ready for production deployment with GitHub Pages integration."
        
        print_success "Changes committed"
    fi
    
    # Push to GitHub
    print_status "Pushing to GitHub..."
    git push -u origin main
    
    if [ $? -eq 0 ]; then
        print_success "Successfully pushed to GitHub"
    else
        print_error "Failed to push to GitHub"
        print_status "Please ensure the repository exists at: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}"
        exit 1
    fi
}

# Verify deployment
verify_deployment() {
    print_status "Verifying deployment..."
    
    # Wait a moment for GitHub to process
    sleep 5
    
    # Check if repository is accessible
    if curl -sf "https://api.github.com/repos/${GITHUB_USERNAME}/${REPO_NAME}" > /dev/null; then
        print_success "GitHub repository is accessible"
    else
        print_warning "Repository may not be publicly accessible yet"
    fi
    
    print_status "GitHub Actions will automatically deploy GitHub Pages"
    print_status "Monitor deployment at: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}/actions"
}

# Main deployment flow
main() {
    echo "Starting production deployment for AI Deep Research MCP..."
    echo ""
    
    check_prerequisites
    cleanup_repo
    format_code
    run_tests
    setup_github_remote
    commit_and_push
    verify_deployment
    
    echo ""
    print_success "🎉 Production deployment complete!"
    echo ""
    echo "📋 Next Steps:"
    echo "1. Monitor GitHub Actions: https://github.com/${GITHUB_USERNAME}/${REPO_NAME}/actions"
    echo "2. GitHub Pages will be available at: https://${GITHUB_USERNAME}.github.io/${REPO_NAME}/"
    echo "3. Setup typically takes 5-10 minutes for first deployment"
    echo ""
    echo "🔧 Local Development:"
    echo "1. Run: ./scripts/dev-setup.sh"
    echo "2. Activate venv: source venv/bin/activate"
    echo "3. Start web interface: cd web_interface && npm start"
    echo ""
}

# Check if repository exists (manual step required)
check_repo_exists() {
    print_status "Checking if GitHub repository exists..."
    
    if ! curl -sf "https://api.github.com/repos/${GITHUB_USERNAME}/${REPO_NAME}" > /dev/null; then
        print_error "GitHub repository does not exist!"
        echo ""
        echo "📋 MANUAL STEP REQUIRED:"
        echo "1. Go to https://github.com"
        echo "2. Click 'New repository'"
        echo "3. Repository name: ${REPO_NAME}"
        echo "4. Owner: ${GITHUB_USERNAME}"
        echo "5. Make it Public"
        echo "6. Do NOT initialize with README, .gitignore, or license"
        echo "7. Click 'Create repository'"
        echo ""
        echo "Then run this script again."
        exit 1
    fi
}

# Run with repository check
check_repo_exists
main
