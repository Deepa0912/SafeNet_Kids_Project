@echo off
title SafeNet Kids — Child Protection Agent
color 0A
echo.
echo  ===================================
echo   SafeNet Kids ^| Protection Agent
echo  ===================================
echo.
echo  [1] Ask your parent for the Link Code
echo  [2] Type it below when asked
echo.

:: Change to the folder where this bat file lives
cd /d "%~dp0"

:: ── Find Python ────────────────────────────────────────────────────────────
:: Try the Windows Python Launcher first (py), then python3, then python
set PYTHON_CMD=

where py >nul 2>&1
if %errorlevel%==0 (
    set PYTHON_CMD=py
    goto :run
)

where python3 >nul 2>&1
if %errorlevel%==0 (
    set PYTHON_CMD=python3
    goto :run
)

where python >nul 2>&1
if %errorlevel%==0 (
    :: Verify it's real Python, not the Microsoft Store alias
    python --version >nul 2>&1
    if %errorlevel%==0 (
        set PYTHON_CMD=python
        goto :run
    )
)

:: ── Python not found ───────────────────────────────────────────────────────
color 0C
echo.
echo  ╔══════════════════════════════════════════════════════════╗
echo  ║            Python is not installed!                     ║
echo  ╠══════════════════════════════════════════════════════════╣
echo  ║  1. Open this link in your browser:                     ║
echo  ║     https://www.python.org/downloads/                   ║
echo  ║                                                          ║
echo  ║  2. Download the latest Python 3.x installer            ║
echo  ║                                                          ║
echo  ║  3. Run the installer and CHECK:                         ║
echo  ║     [x] Add Python to PATH                              ║
echo  ║                                                          ║
echo  ║  4. Also disable the Store alias:                        ║
echo  ║     Settings > Apps > Advanced app settings             ║
echo  ║     > App execution aliases                              ║
echo  ║     Turn OFF "python.exe" and "python3.exe"             ║
echo  ║                                                          ║
echo  ║  5. Restart this file after installing.                  ║
echo  ╚══════════════════════════════════════════════════════════╝
echo.
goto :end

:: ── Run agent ──────────────────────────────────────────────────────────────
:run
echo  Using Python: %PYTHON_CMD%
echo.

:: Install required packages if missing
%PYTHON_CMD% -m pip install httpx psutil python-dotenv pynput pygetwindow pillow --quiet --disable-pip-version-check 2>nul

:: Launch the monitoring agent
%PYTHON_CMD% agent/monitor.py

:end
echo.
echo  Agent stopped. Press any key to exit.
pause >nul

