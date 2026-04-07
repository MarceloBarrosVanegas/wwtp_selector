@echo off
chcp 65001 >nul
echo ============================================
echo Water Program Dashboard - Development Mode
echo ============================================
echo.

echo [1/2] Iniciando Backend (FastAPI)...
echo         URL: http://localhost:8000
echo         Docs: http://localhost:8000/docs
echo.

cd backend
start "Backend API" cmd /k "uvicorn app.main:app --reload --port 8000"
cd ..

echo.
echo [2/2] Verificando Node.js...
node --version >nul 2>&1
if errorlevel 1 (
    echo.
    echo ⚠️  NODE.JS NO ESTÁ INSTALADO
    echo.
    echo Para usar el frontend React:
    echo 1. Descarga Node.js desde https://nodejs.org
    echo 2. Instala la versión LTS
    echo 3. Cierra y abre una nueva terminal
    echo 4. Ejecuta: start-react.bat
    echo.
) else (
    echo ✅ Node.js instalado y disponible
    echo.
    echo Para iniciar React (en otra terminal):
    echo    start-react.bat
    echo.
    echo O manualmente:
    echo    cd frontend ^&^& npm run dev
    echo.
    echo React estará disponible en:
    echo    http://localhost:3000 (o 3001 si 3000 está ocupado)
    echo.
)

echo ============================================
echo Backend corriendo en http://localhost:8000
echo ============================================
echo.
pause
