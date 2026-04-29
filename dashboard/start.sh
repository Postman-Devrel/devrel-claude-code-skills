#!/bin/bash
cd "$(dirname "$0")"

# Gracefully stop any existing instance (SIGTERM first, SIGKILL after 10s)
PIDS=$(lsof -ti:5001 2>/dev/null)
if [ -n "$PIDS" ]; then
    echo "$PIDS" | xargs kill -TERM 2>/dev/null
    for i in $(seq 1 10); do
        lsof -ti:5001 >/dev/null 2>&1 || break
        sleep 1
    done
    # Force-kill only if still alive after 10s
    PIDS=$(lsof -ti:5001 2>/dev/null)
    if [ -n "$PIDS" ]; then
        echo "$PIDS" | xargs kill -9 2>/dev/null
    fi
fi

echo "Starting Blog Pipeline Dashboard..."
echo "  URL:  http://127.0.0.1:5001"
echo "  Stop: ./stop.sh"
echo ""

.venv/bin/python app.py
