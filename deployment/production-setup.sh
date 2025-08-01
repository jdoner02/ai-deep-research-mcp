#!/bin/bash

# Production Setup Script for AI Deep Research MCP
# This script prepares the system for production deployment

set -e  # Exit on any error

echo "🚀 AI Deep Research MCP - Production Setup"
echo "========================================"

# Color codes for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

print_status() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check Python version
print_status "Checking Python version..."
python_version=$(python3 --version 2>&1 | awk '{print $2}')
if [[ $(echo "$python_version" | cut -d. -f1) -eq 3 ]] && [[ $(echo "$python_version" | cut -d. -f2) -ge 9 ]]; then
    print_success "Python $python_version detected"
else
    print_error "Python 3.9+ required. Current version: $python_version"
    exit 1
fi

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    print_status "Creating Python virtual environment..."
    python3 -m venv venv
    print_success "Virtual environment created"
else
    print_status "Using existing virtual environment"
fi

# Activate virtual environment
print_status "Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
print_status "Upgrading pip..."
pip install --upgrade pip

# Install production dependencies
print_status "Installing production dependencies..."
pip install -r requirements.txt

# Install development dependencies for testing
print_status "Installing development dependencies..."
pip install -r requirements-dev.txt

# Run security checks
print_status "Running security checks..."
if command -v bandit &> /dev/null; then
    bandit -r src/ -ll
    print_success "Security scan completed"
else
    print_warning "Bandit not available, installing..."
    pip install bandit
    bandit -r src/ -ll
fi

# Run dependency security check
print_status "Checking dependency security..."
if command -v safety &> /dev/null; then
    safety check
    print_success "Dependency security check completed"
else
    print_warning "Safety not available, installing..."
    pip install safety
    safety check
fi

# Code quality checks
print_status "Running code quality checks..."
if command -v flake8 &> /dev/null; then
    flake8 src --max-line-length=127 --ignore=E203,W503
    print_success "Code quality check passed"
else
    print_warning "flake8 not available, installing..."
    pip install flake8
    flake8 src --max-line-length=127 --ignore=E203,W503
fi

# Type checking
print_status "Running type checks..."
if command -v mypy &> /dev/null; then
    mypy src --ignore-missing-imports || print_warning "Some type issues found, but continuing..."
    print_success "Type checking completed"
else
    print_warning "mypy not available, installing..."
    pip install mypy
    mypy src --ignore-missing-imports || print_warning "Some type issues found, but continuing..."
fi

# Run comprehensive tests
print_status "Running comprehensive test suite..."
export PYTHONPATH=$(pwd)
python -m pytest tests/ -v --tb=short

if [ $? -eq 0 ]; then
    print_success "All tests passed!"
else
    print_error "Some tests failed. Please review and fix before deploying."
    exit 1
fi

# Create production build info
print_status "Creating production build info..."
mkdir -p docs
cat > docs/build-info.txt << EOF
Build Date: $(date)
Python Version: $python_version
Git Commit: $(git rev-parse HEAD 2>/dev/null || echo "N/A")
Git Branch: $(git branch --show-current 2>/dev/null || echo "N/A")
Tests Status: PASSED
Security Scan: COMPLETED
Quality Check: PASSED
Environment: Production Ready
EOF

# Generate API documentation
print_status "Generating API documentation..."
python -c "
import json
import sys
sys.path.insert(0, '.')
from src.presentation.web_interface import WebInterfaceHandler

try:
    handler = WebInterfaceHandler()
    docs = handler.get_api_documentation()
    
    import os
    os.makedirs('docs/api', exist_ok=True)
    
    with open('docs/api/openapi.json', 'w') as f:
        json.dump(docs, f, indent=2)
    
    print('✅ API documentation generated successfully')
except Exception as e:
    print(f'⚠️  API documentation generation failed: {e}')
    print('Continuing with deployment...')
"

# Performance optimization
print_status "Optimizing for production..."

# Create .gitignore for production files if not exists
if [ ! -f ".gitignore" ]; then
    cat > .gitignore << EOF
# Production files
venv/
__pycache__/
*.pyc
*.pyo
*.pyd
.pytest_cache/
.mypy_cache/
.coverage
htmlcov/

# IDE files
.vscode/
.idea/
*.swp
*.swo

# OS files
.DS_Store
Thumbs.db

# Environment files
.env
.env.local
.env.production

# Logs
*.log
logs/

# Data files
data/
*.db
*.sqlite3

# Build artifacts
build/
dist/
*.egg-info/
EOF
    print_success "Created .gitignore file"
fi

# Final system check
print_status "Running final system health check..."
python -c "
import sys
sys.path.insert(0, '.')

# Test core imports
try:
    from src.domain.entities import ResearchQuery
    from src.application.scholarly_use_cases import ScholarlyResearchUseCase
    from src.presentation.web_interface import WebInterfaceHandler
    print('✅ All core modules import successfully')
except ImportError as e:
    print(f'❌ Import error: {e}')
    sys.exit(1)

# Test basic functionality
try:
    handler = WebInterfaceHandler()
    print('✅ Web interface handler initializes successfully')
except Exception as e:
    print(f'❌ Web interface error: {e}')
    sys.exit(1)

print('🎉 System health check passed!')
"

if [ $? -eq 0 ]; then
    print_success "Production setup completed successfully!"
    echo ""
    echo "=========================================="
    echo -e "${GREEN}🚀 READY FOR DEPLOYMENT! 🚀${NC}"
    echo "=========================================="
    echo ""
    print_status "Next steps:"
    echo "  1. Commit your changes: git add -A && git commit -m 'Production ready'"
    echo "  2. Push to main branch: git push origin main"
    echo "  3. GitHub Actions will automatically deploy to GitHub Pages"
    echo "  4. Monitor deployment at: https://github.com/$(git config --get remote.origin.url | sed 's/.*github.com[:\/]\([^\/]*\/[^\/]*\).git/\1/')/actions"
    echo ""
    print_success "Virtual environment is activated and ready for development"
else
    print_error "Production setup failed. Please review errors above."
    exit 1
fi
