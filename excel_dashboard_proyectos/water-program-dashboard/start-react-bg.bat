@echo off
REM Start React in background and log to file
set PATH=C:\Program Files\nodejs;%PATH%
cd /d "C:\Users\Alienware\OneDrive\00_OFC\12_documentos_ofc\01_ToR\01_san_cristobal\00_ptar_cristobal\00_codigos\excel_dashboard_proyectos\water-program-dashboard\frontend"
npm run dev > "C:\Users\Alienware\OneDrive\00_OFC\12_documentos_ofc\01_ToR\01_san_cristobal\00_ptar_cristobal\00_codigos\excel_dashboard_proyectos\water-program-dashboard\react-dev.log" 2>&1
