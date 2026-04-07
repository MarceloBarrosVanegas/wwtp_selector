@echo off
echo ==========================================
echo Water Program Dashboard - Local Startup
echo ==========================================
echo.

REM Check if PostgreSQL is running
echo Checking PostgreSQL...
pg_isready -h localhost -p 5432 >nul 2>&1
if errorlevel 1 (
    echo ERROR: PostgreSQL is not running!
    echo Please start PostgreSQL first.
    exit /b 1
)

echo PostgreSQL is running
echo.

REM Create database if not exists
echo Creating database if not exists...
createdb -h localhost -U postgres water_program 2>nul || echo Database already exists

REM Initialize data
echo.
echo Initializing data from Excel...
cd backend
python import_data.py

REM Start backend
echo.
echo Starting backend server...
start "Backend API" cmd /k "uvicorn app.main:app --reload --port 8000"

REM Start frontend
cd ..\frontend
echo.
echo Installing frontend dependencies (if needed)...
call npm install

echo.
echo Starting frontend server...
start "Frontend" cmd /k "npm run dev"

echo.
echo ==========================================
echo Servers started!
echo.
echo Frontend: http://localhost:3000
echo API Docs: http://localhost:8000/docs
echo ==========================================
echo.
pause
