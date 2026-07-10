#!/bin/bash

echo "Starting PyRBD-Suite Development Environment..."

# Kill background processes on exit
trap "trap - SIGTERM && kill -- -$$" SIGINT SIGTERM EXIT

# Start FastAPI Backend
echo "Starting FastAPI Backend on port 8000..."
python3 -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!

# Wait a couple seconds for backend to initialize
sleep 2

# Start Vite Frontend
echo "Starting Vite Frontend on port 5173..."
cd frontend && npm run dev &
FRONTEND_PID=$!

echo ""
echo "==========================================================="
echo "🚀 Development Environment Running!"
echo "📡 Backend API:  http://localhost:8000/docs"
echo "🎨 Frontend GUI: http://localhost:5173"
echo "==========================================================="
echo "Press Ctrl+C to stop both servers."

wait
