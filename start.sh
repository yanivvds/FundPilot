#!/bin/bash

# Quick start script for Fundpilot Database Chat
# This activates the virtual environment and starts the server

echo "🚀 Starting Fundpilot Database Chat Server..."

# Check if virtual environment exists
if [ ! -d ".venv" ]; then
    echo "❌ Virtual environment not found. Please run ./setup.sh first."
    exit 1
fi

# Activate virtual environment
source .venv/bin/activate

# Check if .env exists
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please copy .env.example to .env and configure it."
    exit 1
fi

# Start the server
echo "Starting server on http://localhost:8000..."
python start_server.py