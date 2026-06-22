@echo off
echo.
echo  ========================================
echo   SafeNet Kids v2 -- Full Stack Launcher
echo  ========================================
echo.

:: Start FastAPI Backend
echo [1/2] Starting FastAPI Backend on port 8000...
start "SafeNet Backend" cmd /k ".venv\Scripts\uvicorn backend.main:sio_app --host 0.0.0.0 --port 8000 --reload"
timeout /t 3 >nul

:: Start Parent Dashboard (Dev Mode)
echo [2/2] Starting Parent Dashboard on port 3000...
start "SafeNet Parent Dashboard" cmd /k "cd frontend-parent && npm run dev"

echo.
echo  Both servers are starting!
echo.
echo  Parent Dashboard : http://localhost:3000
echo  API Docs         : http://localhost:8000/docs
echo.
echo  To start child agent on another device/terminal:
echo    python agent/monitor.py
echo.
pause
