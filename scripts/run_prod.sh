#!/bin/bash

# Production server runner

set -e

cd "$(dirname "$0")/.."

echo "🚀 Starting WebSocket Server (Production Mode)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found!"
    echo "   Please run: python3 -m venv venv"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Check dependencies
if ! pip show fastapi > /dev/null 2>&1; then
    echo "Installing dependencies..."
    pip install -r requirements.txt
fi

# Check configuration
if [ ! -f ".env" ] && [ ! -f "config.json" ]; then
    echo "❌ Configuration not found!"
    echo "   Please create .env or config.json"
    exit 1
fi

# Check certificates if TLS is enabled
if grep -q "TLS_ENABLED=true" .env 2>/dev/null; then
    if [ ! -f "certs/server.crt" ]; then
        echo "❌ TLS certificates not found!"
        echo "   Please run: ./scripts/generate_certs.sh"
        exit 1
    fi
fi

# Create logs directory
mkdir -p logs

echo ""
echo "Starting server in production mode..."
echo ""

# Run server with multiple workers
uvicorn main:app \
    --host 0.0.0.0 \
    --port 8765 \
    --workers 4 \
    --log-level info \
    --access-log \
    --no-use-colors

