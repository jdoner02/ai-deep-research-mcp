# Production Deployment Scripts for AI Deep Research MCP

## GitHub Pages Deployment Infrastructure

This directory contains production-ready deployment scripts and configurations for the AI Deep Research MCP platform.

### Files Overview

- `deploy.yml` - GitHub Actions workflow for CI/CD and GitHub Pages deployment
- `production-setup.sh` - Production environment setup script  
- `health-check.py` - System health monitoring script
- `backup-restore.sh` - Data backup and restore utilities

### Deployment Process

1. **Continuous Integration**
   - Run tests on Python 3.9, 3.10, 3.11, 3.12
   - Code quality checks (flake8, mypy)
   - Security scanning (bandit, safety)

2. **Build Process**
   - Generate API documentation
   - Create production build artifacts
   - Optimize static assets

3. **Deployment**
   - Deploy to GitHub Pages automatically on main branch
   - Update production environment
   - Run health checks

### Manual Deployment

For manual deployment or local testing:

```bash
# Set up production environment
chmod +x scripts/production-setup.sh
./scripts/production-setup.sh

# Run health checks
python scripts/health-check.py

# Deploy to GitHub Pages (requires proper permissions)
# This is handled automatically by GitHub Actions
```

### Monitoring and Maintenance

- Automated health checks run every 15 minutes
- Security scans on every deployment
- Performance monitoring via GitHub Actions
- Backup procedures for research data and configurations

### Environment Variables

Required for production deployment:

```bash
GITHUB_TOKEN=<your-github-token>
DEPLOYMENT_ENV=production
API_BASE_URL=https://jdoner02.github.io/ai-deep-research-mcp
```

### Troubleshooting

Common deployment issues and solutions:

1. **Tests failing**: Check requirements.txt and Python version compatibility
2. **Build errors**: Verify all dependencies are properly specified
3. **Deployment timeout**: Large artifacts may need optimization
4. **Permission errors**: Ensure GitHub Pages is enabled in repository settings

For detailed logs, check the GitHub Actions tab in the repository.
