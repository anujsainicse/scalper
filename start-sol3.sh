#!/bin/bash

# SOL3 Branch Startup Script
# Frontend: http://localhost:3003
# Backend: http://localhost:8003

echo "🚀 Starting SOL3 Branch (Ports 3003/8003)..."

# Kill any processes on these ports
echo "🧹 Cleaning up ports 3003 and 8003..."
lsof -ti:3003,8003 | xargs kill -9 2>/dev/null || true

# Copy environment files
echo "📋 Setting up environment files..."
cp .env.local.sol3 .env.local
cp backend/.env.sol3 backend/.env

# Start backend
echo "🔧 Starting backend on port 8003..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8003 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend on port 3003..."
PORT=3003 npm run dev:frontend &
FRONTEND_PID=$!

echo ""
echo "✅ SOL3 Branch is running!"
echo "📍 Frontend: http://localhost:3003"
echo "📍 Backend API: http://localhost:8003"
echo "📍 API Docs: http://localhost:8003/docs"
echo ""
echo "To stop both servers, run: kill $BACKEND_PID $FRONTEND_PID"
echo "Or use: npm run kill:ports -- 3003,8003"

# Wait for both processes
wait
