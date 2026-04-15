#!/bin/bash
cd "$(dirname "$0")"

# Kill any existing instance
lsof -ti:5001 | xargs kill -9 2>/dev/null

echo "Starting Blog Pipeline Dashboard..."
echo "  URL:  http://127.0.0.1:5001"
echo "  Stop: ./stop.sh"
echo ""

.venv/bin/python app.py
