#!/bin/bash

# Development server runner

set -e

cd "$(dirname "$0")/.."

echo "🚀 Starting WebSocket Server (Development Mode)"
echo ""

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -q --upgrade pip
pip install -q -r requirements.txt

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "⚠️  .env file not found. Copying from env.example..."
    cp env.example .env
fi

# Check if certificates exist
if [ ! -f "certs/server.crt" ]; then
    echo "⚠️  TLS certificates not found. Generating..."
    ./scripts/generate_certs.sh
fi

# Create logs directory
mkdir -p logs

echo ""
echo "Starting server..."
echo ""

# Run server with hot reload
uvicorn main:app --reload --host 0.0.0.0 --port 8765

