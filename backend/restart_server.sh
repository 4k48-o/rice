#!/bin/bash
# Restart the FastAPI server

cd "$(dirname "$0")"

echo "🔄 Restarting FastAPI server..."

# Stop the server
./stop_server.sh

# Wait a moment
sleep 1

# Start the server
./start_server.sh
