# 🐳 VS Code Docker Deployment Guide for MCP Servers

This guide demonstrates professional Docker deployment practices for Model Context Protocol (MCP) servers in VS Code development environments.

## 🎯 Educational Overview

This setup teaches students how modern software teams deploy AI applications using:
- **Docker containerization** for consistent environments
- **VS Code Dev Containers** for unified development 
- **Multi-stage builds** for production efficiency
- **Docker Compose** for orchestrating services

## 🚀 Quick Start for VS Code

### Option 1: Dev Container (Recommended for Learning)

1. **Open in VS Code**:
   ```bash
   code /path/to/ai-deep-research-mcp
   ```

2. **Reopen in Container**:
   - Press `Ctrl+Shift+P` (or `Cmd+Shift+P` on Mac)
   - Select: "Dev Containers: Reopen in Container"
   - VS Code will build and connect to the development container

3. **Verify Setup**:
   ```bash
   # Inside the container terminal
   python --version  # Should show Python 3.12
   pytest tests/ -v  # Run the test suite
   python -m src     # Start the MCP server
   ```

### Option 2: Docker Compose (Production-like)

1. **Build and Start Services**:
   ```bash
   docker-compose up --build
   ```

2. **Access the Application**:
   - MCP Server: http://localhost:8000
   - Nginx Proxy: http://localhost:80

3. **View Logs**:
   ```bash
   docker-compose logs -f ai-deep-research-mcp
   ```

## 🏗️ Architecture Overview

### Multi-Stage Dockerfile Benefits

Our Dockerfile uses a **multi-stage build** pattern:

```dockerfile
# Stage 1: Builder (includes build tools)
FROM python:3.12-slim AS builder
# Install dependencies, compile packages

# Stage 2: Runtime (minimal for production)  
FROM python:3.12-slim AS runtime
# Copy only what's needed for running
```

**Educational Benefits:**
- **Smaller Images**: Production image excludes build tools
- **Security**: Fewer packages mean smaller attack surface
- **Efficiency**: Faster deployments and downloads

### Docker Compose Services

```yaml
services:
  ai-deep-research-mcp:    # Main application
  nginx:                   # Reverse proxy (optional)
```

**Why This Pattern?**
- **Separation of Concerns**: Each service has one responsibility
- **Scalability**: Easy to add load balancing or multiple instances
- **Development**: Can run services independently

## 🛠️ Development Workflow

### 1. Code Changes
Edit files in VS Code as normal - changes are immediately reflected in the container.

### 2. Run Tests
```bash
# In VS Code integrated terminal
pytest tests/ --cov=src --cov-report=html
```

### 3. Debug the MCP Server
```bash
# Start with debugging enabled
python -m src --debug --log-level=DEBUG
```

### 4. Test MCP Client Connections
```bash
# Test the MCP protocol
echo '{"jsonrpc": "2.0", "id": 1, "method": "tools/list"}' | nc localhost 8000
```

## 🧪 Testing in Containerized Environment

### Unit Tests
```bash
docker-compose exec ai-deep-research-mcp pytest tests/unit/ -v
```

### Integration Tests
```bash
docker-compose exec ai-deep-research-mcp pytest tests/integration/ -v
```

### Full Test Suite with Coverage
```bash
docker-compose exec ai-deep-research-mcp pytest tests/ \
  --cov=src \
  --cov-report=html \
  --cov-report=term-missing
```

## 🔧 Common MCP Server Configurations

### Environment Variables

```bash
# In .env file or docker-compose.yml
MCP_LOG_LEVEL=INFO          # Logging level
MCP_PORT=8000               # Server port
PYTHONPATH=/app             # Python module path
SEMANTIC_SCHOLAR_API_KEY=   # Optional API key
```

### Volume Mounts for Development

```yaml
volumes:
  - ./src:/app/src           # Live code reloading
  - ./tests:/app/tests       # Test development
  - ./data:/app/data         # Persistent data
  - ./logs:/app/logs         # Log files
```

## 🚨 Troubleshooting

### Container Won't Start
```bash
# Check container logs
docker-compose logs ai-deep-research-mcp

# Check container status
docker-compose ps
```

### Import Errors
```bash
# Verify Python path inside container
docker-compose exec ai-deep-research-mcp python -c "import sys; print(sys.path)"

# Check if modules are installed
docker-compose exec ai-deep-research-mcp pip list
```

### Port Already in Use
```bash
# Find what's using port 8000
lsof -i :8000

# Use different port in docker-compose.yml
ports:
  - "8001:8000"  # Map host port 8001 to container port 8000
```

### VS Code Dev Container Issues
1. Ensure Docker Desktop is running
2. Restart VS Code and try "Rebuild Container"
3. Check Docker extension is installed and enabled

## 📚 Learning Resources

### Docker Concepts Demonstrated
- **Multi-stage builds**: Optimized production images
- **Layer caching**: Faster subsequent builds
- **Health checks**: Automated service monitoring
- **Volume mounts**: Persistent data and development

### MCP Server Patterns
- **Protocol compliance**: Following MCP specifications
- **Clean architecture**: Separating concerns properly
- **Error handling**: Graceful failure and recovery
- **Logging**: Professional debugging practices

### Production Considerations
- **Security**: Non-root users, minimal attack surface
- **Monitoring**: Health checks and logging
- **Scalability**: Easy horizontal scaling with compose
- **Maintenance**: Automated updates and backups

## 🎓 Educational Extension Activities

1. **Modify the Dockerfile** to use a different Python version
2. **Add environment-specific configs** for dev/staging/prod
3. **Implement health check endpoints** in the MCP server
4. **Add database services** to docker-compose.yml
5. **Create production deployment scripts** with security hardening

This Docker setup provides a professional foundation for learning modern software deployment while maintaining the educational focus on AI and research systems.
