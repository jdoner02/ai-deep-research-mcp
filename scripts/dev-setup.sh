#!/bin/bash
# AI Deep Research MCP - Development Environment Setup
# Repository Engineer Agent - Production Quality Setup

set -e  # Exit on any error

echo "🚀 AI Deep Research MCP - Development Setup"
echo "==========================================="

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to print colored output
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

# Check if Python 3.9+ is available
check_python() {
    print_status "Checking Python version..."
    if command -v python3 &> /dev/null; then
        PYTHON_VERSION=$(python3 --version | cut -d' ' -f2)
        MAJOR_VERSION=$(echo $PYTHON_VERSION | cut -d'.' -f1)
        MINOR_VERSION=$(echo $PYTHON_VERSION | cut -d'.' -f2)
        
        if [ "$MAJOR_VERSION" -eq 3 ] && [ "$MINOR_VERSION" -ge 9 ]; then
            print_success "Python $PYTHON_VERSION detected"
            PYTHON_CMD="python3"
        else
            print_error "Python 3.9+ required, found $PYTHON_VERSION"
            exit 1
        fi
    else
        print_error "Python 3 not found"
        exit 1
    fi
}

# Create virtual environment
setup_virtualenv() {
    print_status "Setting up virtual environment..."
    
    if [ ! -d "venv" ]; then
        $PYTHON_CMD -m venv venv
        print_success "Virtual environment created"
    else
        print_warning "Virtual environment already exists"
    fi
    
    # Activate virtual environment
    source venv/bin/activate
    print_success "Virtual environment activated"
    
    # Upgrade pip
    pip install --upgrade pip
    print_success "pip upgraded"
}

# Install dependencies
install_dependencies() {
    print_status "Installing Python dependencies..."
    
    # Install from requirements.txt
    if [ -f "requirements.txt" ]; then
        pip install -r requirements.txt
        print_success "Python dependencies installed"
    else
        print_error "requirements.txt not found"
        exit 1
    fi
    
    # Install development dependencies
    pip install black isort flake8 mypy pytest-xdist
    print_success "Development dependencies installed"
}

# Setup pre-commit hooks
setup_precommit() {
    print_status "Setting up pre-commit hooks..."
    
    pip install pre-commit
    
    # Create pre-commit config if it doesn't exist
    if [ ! -f ".pre-commit-config.yaml" ]; then
        cat > .pre-commit-config.yaml << EOF
repos:
  - repo: https://github.com/psf/black
    rev: 23.7.0
    hooks:
      - id: black
        language_version: python3

  - repo: https://github.com/pycqa/isort
    rev: 5.12.0
    hooks:
      - id: isort
        args: ["--profile", "black"]

  - repo: https://github.com/pycqa/flake8
    rev: 6.0.0
    hooks:
      - id: flake8
        args: ["--max-line-length=88", "--extend-ignore=E203,W503"]

  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.5.1
    hooks:
      - id: mypy
        additional_dependencies: [types-requests, types-PyYAML]
EOF
    fi
    
    pre-commit install
    print_success "Pre-commit hooks installed"
}

# Setup Node.js for web interface
setup_nodejs() {
    print_status "Setting up Node.js dependencies..."
    
    if command -v npm &> /dev/null; then
        cd web_interface
        if [ -f "package.json" ]; then
            npm install
            print_success "Node.js dependencies installed"
        else
            print_warning "package.json not found in web_interface/"
        fi
        cd ..
    else
        print_warning "npm not found - Node.js setup skipped"
    fi
}

# Run tests to verify setup
verify_setup() {
    print_status "Verifying setup with tests..."
    
    # Run a subset of tests to verify everything works
    python -m pytest tests/test_scholarly_integration.py -v
    
    if [ $? -eq 0 ]; then
        print_success "Setup verification passed"
    else
        print_error "Setup verification failed"
        exit 1
    fi
}

# Main setup flow
main() {
    check_python
    setup_virtualenv
    install_dependencies
    setup_precommit
    setup_nodejs
    verify_setup
    
    echo ""
    print_success "🎉 Development environment setup complete!"
    echo ""
    echo "Next steps:"
    echo "1. Activate virtual environment: source venv/bin/activate"
    echo "2. Run tests: python -m pytest"
    echo "3. Start web interface: cd web_interface && npm start"
    echo "4. Format code: black src/ tests/"
    echo ""
}

# Run main function
main
