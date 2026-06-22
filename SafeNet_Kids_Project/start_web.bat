@echo off
title SafeNet Kids — Web Dashboard
echo.
echo  =========================================
echo   SafeNet Kids  ^|  Web Dashboard Launcher
echo  =========================================
echo.
echo  Starting web server...
echo  Once started, open in your browser:
echo.
echo    Chrome : http://localhost:5000
echo    Edge   : http://localhost:5000
echo.
echo  Press Ctrl+C to stop the server.
echo.
cd /d "%~dp0"
python web\server.py
pause
