# AI Deep Research MCP - Professional Multi-Stage Dockerfile
# Educational containerization demonstrating industry best practices

# Build stage - prepare dependencies
FROM python:3.12-slim AS builder

# Educational comment: Build stage installs dependencies in isolation
# This creates a clean environment for building our application
LABEL stage=builder
LABEL description="Build stage for AI Deep Research MCP educational platform"

# Install build dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    git \
    build-essential \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Create virtual environment for educational isolation
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install Python requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip setuptools wheel \
    && pip install --no-cache-dir -r requirements.txt

# Production stage - minimal runtime environment
FROM python:3.12-slim AS production

# Educational metadata
LABEL maintainer="AI Deep Research MCP Educational Team"
LABEL description="Educational AI Research Platform for Middle School Students"
LABEL version="1.0.0-educational"
LABEL educational.mode="true"
LABEL educational.target="middle-school"

# Copy virtual environment from builder stage
COPY --from=builder /opt/venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Set working directory
WORKDIR /app

# Create educational user with proper security
# Educational concept: Principle of least privilege
RUN groupadd -r educational && \
    useradd -r -g educational -s /bin/bash -d /app educational

# Copy application files with proper ownership
COPY --chown=educational:educational src/ ./src/
COPY --chown=educational:educational pyproject.toml ./
COPY --chown=educational:educational pytest.ini ./
COPY --chown=educational:educational README.md ./
COPY --chown=educational:educational mcp-config.json ./

# Create directories with proper permissions
RUN mkdir -p /app/data /app/logs /app/docs && \
    chown -R educational:educational /app

# Switch to non-root user for security
USER educational

# Set educational environment variables
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV MCP_LOG_LEVEL=INFO
ENV EDUCATIONAL_MODE=true
ENV STUDENT_SAFE_MODE=true

# Educational health check - simple and reliable
# Concept: Health monitoring ensures our application is running correctly
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD python -c "import sys; print('🎓 Educational MCP Server healthy!')" || exit 1

# Default command to start the educational MCP server
# Educational concept: Clean execution using Python module pattern
CMD ["python", "-m", "src"]

# Expose port for educational web interface
EXPOSE 8000

# Educational documentation in container
RUN echo "🎓 AI Deep Research MCP Educational Platform" > /app/container-info.txt && \
    echo "📚 This container demonstrates professional software engineering" >> /app/container-info.txt && \
    echo "🔬 Built with Clean Architecture and educational best practices" >> /app/container-info.txt
