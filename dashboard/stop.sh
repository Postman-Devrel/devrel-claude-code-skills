#!/bin/bash
PIDS=$(lsof -ti:5001 2>/dev/null)
if [ -z "$PIDS" ]; then
    echo "Not running."
    exit 0
fi

echo "$PIDS" | xargs kill -TERM 2>/dev/null
for i in $(seq 1 10); do
    lsof -ti:5001 >/dev/null 2>&1 || { echo "Stopped."; exit 0; }
    sleep 1
done

# Force-kill only if still alive after 10s
lsof -ti:5001 2>/dev/null | xargs kill -9 2>/dev/null
echo "Stopped (forced)."
