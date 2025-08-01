#!/bin/bash

# AI Deep Research MCP Server Management Script
# Usage: ./run-mcp-server.sh [start|stop|restart|status|logs]

set -e

PROJECT_DIR="/Users/jessicadoner/0. Knowledge Manager/ai_deep_research_mcp"
VENV_DIR="$PROJECT_DIR/venv"
LOG_FILE="$PROJECT_DIR/logs/mcp-server.log"
PID_FILE="$PROJECT_DIR/mcp-server.pid"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

log() {
    echo -e "${BLUE}[$(date '+%Y-%m-%d %H:%M:%S')]${NC} $1"
}

error() {
    echo -e "${RED}[ERROR]${NC} $1" >&2
}

success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

setup_environment() {
    cd "$PROJECT_DIR"
    
    # Create virtual environment if it doesn't exist
    if [ ! -d "$VENV_DIR" ]; then
        log "Creating Python virtual environment..."
        python3 -m venv "$VENV_DIR"
    fi
    
    # Activate virtual environment
    source "$VENV_DIR/bin/activate"
    
    # Install/update dependencies
    log "Installing dependencies..."
    pip install -q --upgrade pip
    pip install -q -r requirements.txt
    
    # Create logs directory
    mkdir -p logs
}

start_server() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        warning "MCP server is already running (PID: $(cat "$PID_FILE"))"
        return 1
    fi
    
    log "Setting up environment..."
    setup_environment
    
    log "Starting AI Deep Research MCP Server..."
    source "$VENV_DIR/bin/activate"
    
    # Start server in background
    nohup python -m src > "$LOG_FILE" 2>&1 &
    echo $! > "$PID_FILE"
    
    # Wait a moment and check if it started successfully
    sleep 2
    if kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        success "MCP server started successfully (PID: $(cat "$PID_FILE"))"
        log "Logs: tail -f $LOG_FILE"
    else
        error "Failed to start MCP server. Check logs: $LOG_FILE"
        rm -f "$PID_FILE"
        return 1
    fi
}

stop_server() {
    if [ ! -f "$PID_FILE" ]; then
        warning "PID file not found. Server may not be running."
        return 1
    fi
    
    PID=$(cat "$PID_FILE")
    if kill -0 "$PID" 2>/dev/null; then
        log "Stopping MCP server (PID: $PID)..."
        kill "$PID"
        
        # Wait for graceful shutdown
        for i in {1..10}; do
            if ! kill -0 "$PID" 2>/dev/null; then
                break
            fi
            sleep 1
        done
        
        # Force kill if still running
        if kill -0 "$PID" 2>/dev/null; then
            warning "Forcing server shutdown..."
            kill -9 "$PID"
        fi
        
        rm -f "$PID_FILE"
        success "MCP server stopped"
    else
        warning "Server process not found"
        rm -f "$PID_FILE"
    fi
}

server_status() {
    if [ -f "$PID_FILE" ] && kill -0 "$(cat "$PID_FILE")" 2>/dev/null; then
        success "MCP server is running (PID: $(cat "$PID_FILE"))"
        return 0
    else
        warning "MCP server is not running"
        return 1
    fi
}

show_logs() {
    if [ -f "$LOG_FILE" ]; then
        tail -f "$LOG_FILE"
    else
        error "Log file not found: $LOG_FILE"
    fi
}

case "${1:-}" in
    start)
        start_server
        ;;
    stop)
        stop_server
        ;;
    restart)
        stop_server
        sleep 2
        start_server
        ;;
    status)
        server_status
        ;;
    logs)
        show_logs
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status|logs}"
        echo ""
        echo "Commands:"
        echo "  start   - Start the MCP server"
        echo "  stop    - Stop the MCP server"
        echo "  restart - Restart the MCP server"
        echo "  status  - Check server status"
        echo "  logs    - Show server logs"
        exit 1
        ;;
esac
