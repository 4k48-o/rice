#!/bin/bash
# Start the FastAPI server

cd "$(dirname "$0")"

echo "🚀 Starting FastAPI server..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please create it first."
    exit 1
fi

# Activate virtual environment and start server
venv/bin/uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
