#!/bin/bash

# SOL2 Branch Startup Script
# Frontend: http://localhost:3002
# Backend: http://localhost:8002

echo "🚀 Starting SOL2 Branch (Ports 3002/8002)..."

# Kill any processes on these ports
echo "🧹 Cleaning up ports 3002 and 8002..."
lsof -ti:3002,8002 | xargs kill -9 2>/dev/null || true

# Copy environment files
echo "📋 Setting up environment files..."
cp .env.local.sol2 .env.local
cp backend/.env.sol2 backend/.env

# Start backend
echo "🔧 Starting backend on port 8002..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8002 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend on port 3002..."
PORT=3002 npm run dev:frontend &
FRONTEND_PID=$!

echo ""
echo "✅ SOL2 Branch is running!"
echo "📍 Frontend: http://localhost:3002"
echo "📍 Backend API: http://localhost:8002"
echo "📍 API Docs: http://localhost:8002/docs"
echo ""
echo "To stop both servers, run: kill $BACKEND_PID $FRONTEND_PID"
echo "Or use: npm run kill:ports -- 3002,8002"

# Wait for both processes
wait
