#!/bin/bash

# Start FastAPI development server
# This script ensures the virtual environment is activated before running uvicorn

cd "$(dirname "$0")"

if [ -d "venv" ]; then
    source venv/bin/activate
    echo "✓ Virtual environment activated"
else
    echo "⚠ Warning: venv not found. Using system Python."
fi

echo "Starting FastAPI server..."
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
