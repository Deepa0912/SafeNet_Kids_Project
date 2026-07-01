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

:: ── Install required packages ───────────────────────────────────────────────
echo  Installing / checking required packages...
echo  (This only happens once — please wait)
echo.
%PYTHON_CMD% -m pip install httpx psutil python-dotenv pynput pygetwindow pillow pyautogui --upgrade

if %errorlevel% neq 0 (
    color 0C
    echo.
    echo  ╔══════════════════════════════════════════════════════════╗
    echo  ║        Package installation FAILED!                     ║
    echo  ╠══════════════════════════════════════════════════════════╣
    echo  ║  Try running this command manually in Command Prompt:   ║
    echo  ║                                                          ║
    echo  ║    pip install httpx psutil python-dotenv pynput        ║
    echo  ║               pygetwindow pillow                        ║
    echo  ║                                                          ║
    echo  ║  Then run this file again.                              ║
    echo  ╚══════════════════════════════════════════════════════════╝
    echo.
    goto :end
)

echo.
echo  All packages ready!
echo.

:: ── Find monitor.py (works in any folder layout) ───────────────────────────
set MONITOR_PATH=

if exist "agent\monitor.py"            set MONITOR_PATH=agent\monitor.py
if exist "safenet_agent\monitor.py"    set MONITOR_PATH=safenet_agent\monitor.py
if exist "monitor.py"                  set MONITOR_PATH=monitor.py

if "%MONITOR_PATH%"=="" (
    color 0C
    echo.
    echo  ERROR: Cannot find monitor.py
    echo  Make sure this bat file is in the SafeNet agent folder.
    echo.
    goto :end
)

echo  Launching agent: %MONITOR_PATH%
echo.

:: ── Auto-create .env beside monitor.py (so agent gets API keys) ─────────────
:: Get the folder that contains monitor.py
for %%F in ("%MONITOR_PATH%") do set AGENT_DIR=%%~dpF

if not exist "%AGENT_DIR%.env" (
    echo  ┌──────────────────────────────────────────────────────────┐
    echo  │           First-time Setup — API Key Required           │
    echo  └──────────────────────────────────────────────────────────┘
    echo.
    echo  Your parent will give you a setup key.
    echo  Paste it below and press Enter:
    echo.
    set /p GEMINI_KEY=  API Key: 
    echo.
    (
        echo GEMINI_API_KEY=%GEMINI_KEY%
        echo SAFENET_API=https://safenetkidsproject-production.up.railway.app
    ) > "%AGENT_DIR%.env"
    echo  Setup complete! Key saved. You won't be asked again.
    echo.
) else (
    echo  Config already set up.
    echo.
)

:: ── Launch ─────────────────────────────────────────────────────────────────
%PYTHON_CMD% "%MONITOR_PATH%"

:end
echo.
echo  Agent stopped. Press any key to exit.
pause >nul

