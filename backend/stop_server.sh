#!/bin/bash
# Stop the FastAPI server and ensure port is released

cd "$(dirname "$0")"

echo "🛑 Stopping FastAPI server..."

# Method 1: Find process by port 8000 (most reliable)
PORT=8000
PIDS=$(lsof -ti:$PORT 2>/dev/null)

if [ -z "$PIDS" ]; then
    # Method 2: Find uvicorn processes
    PIDS=$(ps aux | grep "uvicorn.*app.main:app" | grep -v grep | awk '{print $2}' | tr '\n' ' ')
    
    if [ -z "$PIDS" ]; then
        # Method 3: Find any uvicorn process on port 8000
        PIDS=$(ps aux | grep "uvicorn" | grep "8000" | grep -v grep | awk '{print $2}' | tr '\n' ' ')
    fi
fi

if [ -z "$PIDS" ]; then
    echo "ℹ️  No server process found on port $PORT"
    echo "✅ Port $PORT is available"
    exit 0
fi

echo "Found process(es): $PIDS"

# Kill all found processes
for PID in $PIDS; do
    if ps -p $PID > /dev/null 2>&1; then
        echo "Stopping process $PID..."
        kill $PID 2>/dev/null
        
        # Wait a bit for graceful shutdown
        sleep 2
        
        # Check if process is still running
        if ps -p $PID > /dev/null 2>&1; then
            echo "⚠️  Process $PID still running, forcing kill..."
            kill -9 $PID 2>/dev/null
            sleep 1
        fi
    fi
done

# Verify port is released
sleep 1
if lsof -ti:$PORT > /dev/null 2>&1; then
    echo "❌ Warning: Port $PORT is still in use"
    echo "Remaining processes on port $PORT:"
    lsof -ti:$PORT | xargs ps -p
    exit 1
else
    echo "✅ Server stopped successfully"
    echo "✅ Port $PORT is now available"
    exit 0
fi
