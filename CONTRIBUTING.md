# Contributing to AI Deep Research MCP

Thank you for your interest in contributing to AI Deep Research MCP! This document provides guidelines for contributing to the project.

## Development Setup

1. **Clone the repository:**
   ```bash
   git clone https://github.com/jdoner02/ai-deep-research-mcp.git
   cd ai-deep-research-mcp
   ```

2. **Run the development setup script:**
   ```bash
   ./scripts/dev-setup.sh
   ```

3. **Activate the virtual environment:**
   ```bash
   source venv/bin/activate
   ```

## Development Workflow

### Code Quality Standards

- **Python Code Style:** We use Black for formatting with 88-character line limits
- **Import Sorting:** isort with Black profile
- **Linting:** flake8 with E203,W503 extensions ignored
- **Type Hints:** Encouraged for new code, mypy integration available

### Testing Requirements

- **Test Coverage:** Maintain >90% test coverage
- **Test Types:** Unit tests, integration tests, and end-to-end tests
- **TDD Approach:** Follow Red-Green-Refactor methodology
- **Test Performance:** Tests should complete in <60 seconds

### Branch Strategy

- **main:** Production-ready code
- **feature/*:** New features and enhancements
- **bugfix/*:** Bug fixes
- **hotfix/*:** Critical production fixes

### Commit Message Format

```
🎯 <type>: <short description>

<detailed description if needed>

- Key change 1
- Key change 2
- Key change 3

Refs: #issue-number
```

**Types:**
- 🎯 `feat`: New feature
- 🐛 `fix`: Bug fix
- 📚 `docs`: Documentation changes
- 🎨 `style`: Code style/formatting
- ♻️ `refactor`: Code refactoring
- 🧪 `test`: Test additions/modifications
- 🔧 `chore`: Build/tooling changes

## Pull Request Process

1. **Create Feature Branch:**
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make Changes:** Implement your changes following the code quality standards

3. **Run Tests:**
   ```bash
   python -m pytest
   black src/ tests/
   isort src/ tests/ --profile black
   flake8 src/ tests/
   ```

4. **Commit Changes:**
   ```bash
   git add .
   git commit -m "🎯 feat: add your feature description"
   ```

5. **Push and Create PR:**
   ```bash
   git push origin feature/your-feature-name
   ```

## Code Architecture

### Core Components

- **src/api_orchestrator.py:** Main research orchestration
- **src/scholarly_sources.py:** Academic database integration
- **src/web_search.py:** Web search functionality
- **src/citation_manager.py:** Citation formatting
- **src/vector_store.py:** Semantic search and storage

### Testing Structure

- **tests/:** Mirror the src/ structure
- **tests/conftest.py:** Shared test fixtures
- **tests/test_*.py:** Individual module tests

### GitHub Pages Deployment

- **docs/:** Static site files
- **docs/js/:** Client-side JavaScript
- **.github/workflows/:** CI/CD pipelines

## Reporting Issues

### Bug Reports

Include:
- Python version and OS
- Steps to reproduce
- Expected vs actual behavior
- Error messages/stack traces
- Minimal code example

### Feature Requests

Include:
- Use case and motivation
- Proposed API/interface
- Implementation ideas (optional)
- Related issues/discussions

## Security

- Report security vulnerabilities privately to: [security email]
- Do not include sensitive data in issues/PRs
- Follow responsible disclosure practices

## Code of Conduct

- Be respectful and inclusive
- Focus on technical merit
- Help newcomers learn
- Credit contributions appropriately

## Academic Research Ethics

This project handles academic content and citations:

- **Respect Copyright:** Follow fair use guidelines
- **Proper Attribution:** Ensure accurate citations
- **API Compliance:** Follow academic database terms of service
- **Rate Limiting:** Implement appropriate delays between requests

## Local Development Tips

### Running Specific Tests
```bash
# Run scholarly integration tests
python -m pytest tests/test_scholarly_integration.py -v

# Run with coverage
python -m pytest --cov=src --cov-report=html

# Run in parallel
python -m pytest -n auto
```

### Web Interface Development
```bash
cd web_interface
npm install
npm start  # Starts development server
```

### Manual Testing
```bash
# Test the research system
python web_interface/test_system.py

# Test specific components
python -c "from src.scholarly_sources import ArxivSearcher; print(ArxivSearcher().search('AI', max_results=1))"
```

## Release Process

1. Update version numbers
2. Update CHANGELOG.md
3. Create release branch
4. Run full test suite
5. Deploy to staging
6. Create GitHub release
7. Deploy to production

## Getting Help

- **Documentation:** Check README.md and docs/
- **Issues:** Search existing issues before creating new ones
- **Discussions:** Use GitHub Discussions for questions
- **Code Review:** Request reviews from maintainers

Thank you for contributing to AI Deep Research MCP! 🚀
