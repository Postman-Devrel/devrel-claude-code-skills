#!/bin/bash
lsof -ti:5001 | xargs kill -9 2>/dev/null && echo "Stopped." || echo "Not running."
