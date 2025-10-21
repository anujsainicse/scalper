#!/bin/bash

# SOL1 Branch Startup Script
# Frontend: http://localhost:3001
# Backend: http://localhost:8001

echo "🚀 Starting SOL1 Branch (Ports 3001/8001)..."

# Kill any processes on these ports
echo "🧹 Cleaning up ports 3001 and 8001..."
lsof -ti:3001,8001 | xargs kill -9 2>/dev/null || true

# Copy environment files
echo "📋 Setting up environment files..."
cp .env.local.sol1 .env.local
cp backend/.env.sol1 backend/.env

# Start backend
echo "🔧 Starting backend on port 8001..."
cd backend
source venv/bin/activate
uvicorn app.main:app --reload --host 0.0.0.0 --port 8001 &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend
echo "🎨 Starting frontend on port 3001..."
PORT=3001 npm run dev:frontend &
FRONTEND_PID=$!

echo ""
echo "✅ SOL1 Branch is running!"
echo "📍 Frontend: http://localhost:3001"
echo "📍 Backend API: http://localhost:8001"
echo "📍 API Docs: http://localhost:8001/docs"
echo ""
echo "To stop both servers, run: kill $BACKEND_PID $FRONTEND_PID"
echo "Or use: npm run kill:ports -- 3001,8001"

# Wait for both processes
wait
