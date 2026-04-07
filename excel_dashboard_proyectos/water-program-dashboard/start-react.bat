@echo off
chcp 65001 >nul
echo ============================================
echo React Frontend - Development Mode
echo ============================================
echo.

node --version >nul 2>&1
if errorlevel 1 (
    echo ❌ ERROR: Node.js no está instalado
    echo.
    echo Por favor instala Node.js desde:
    echo https://nodejs.org
    echo.
    echo Luego vuelve a ejecutar este script.
    pause
    exit /b 1
)

echo ✅ Node.js detectado
echo.

cd frontend

echo 📦 Instalando dependencias (si es necesario)...
call npm install
if errorlevel 1 (
    echo ❌ Error instalando dependencias
    pause
    exit /b 1
)

echo.
echo 🚀 Iniciando React dev server...
echo    URL: http://localhost:3000 (o 3001 si está ocupado)
echo    API Proxy: http://localhost:8000/api
echo.
echo Presiona Ctrl+C para detener
echo.

npm run dev
