#!/bin/bash

echo "=========================================="
echo "Water Program Dashboard - Local Startup"
echo "=========================================="
echo ""

# Check if PostgreSQL is running
echo "Checking PostgreSQL..."
if ! pg_isready -h localhost -p 5432 > /dev/null 2>&1; then
    echo "ERROR: PostgreSQL is not running!"
    echo "Please start PostgreSQL first."
    exit 1
fi

echo "PostgreSQL is running"
echo ""

# Create database if not exists
echo "Creating database if not exists..."
createdb -h localhost -U postgres water_program 2>/dev/null || echo "Database already exists"

# Initialize data
echo ""
echo "Initializing data from Excel..."
cd backend
python import_data.py

# Start backend
echo ""
echo "Starting backend server..."
uvicorn app.main:app --reload --port 8000 &
BACKEND_PID=$!

# Start frontend
cd ../frontend
echo ""
echo "Installing frontend dependencies (if needed)..."
npm install

echo ""
echo "Starting frontend server..."
npm run dev &
FRONTEND_PID=$!

echo ""
echo "=========================================="
echo "Servers started!"
echo ""
echo "Frontend: http://localhost:3000"
echo "API Docs: http://localhost:8000/docs"
echo "=========================================="
echo ""
echo "Press Ctrl+C to stop all servers"

# Wait for interrupt
trap "kill $BACKEND_PID $FRONTEND_PID; exit" INT
wait
