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

:: ── Auto-create / fix .env beside monitor.py ────────────────────────────────
:: Get the folder that contains monitor.py
for %%F in ("%MONITOR_PATH%") do set AGENT_DIR=%%~dpF

:: Check if .env exists AND has a real GEMINI_API_KEY value (not blank)
set NEED_KEY=1
if exist "%AGENT_DIR%.env" (
    findstr /i /c:"GEMINI_API_KEY=" "%AGENT_DIR%.env" | findstr /v /c:"GEMINI_API_KEY= " | findstr /v /c:"GEMINI_API_KEY=$" >nul 2>&1
    :: Use a different approach - check if key line has content after the =
    for /f "tokens=2 delims==" %%K in ('findstr /i "GEMINI_API_KEY" "%AGENT_DIR%.env" 2^>nul') do (
        if not "%%K"=="" set NEED_KEY=0
    )
)

if "%NEED_KEY%"=="1" (
    color 0E
    echo.
    echo  ┌──────────────────────────────────────────────────────────┐
    echo  │          Setup Required — AI Key Needed                 │
    echo  └──────────────────────────────────────────────────────────┘
    echo.
    echo  Ask your parent for the GEMINI API key.
    echo  Paste it below and press Enter:
    echo.
    set /p GEMINI_KEY=  API Key: 
    echo.
    (
        echo GEMINI_API_KEY=%GEMINI_KEY%
        echo SAFENET_API=https://safenetkidsproject-production.up.railway.app
    ) > "%AGENT_DIR%.env"
    color 0A
    echo  AI key saved! Gemini Vision monitoring is now active.
    echo.
) else (
    echo  Config OK — AI monitoring enabled.
    echo.
)

:: ── Launch ─────────────────────────────────────────────────────────────────
%PYTHON_CMD% "%MONITOR_PATH%"

:end
echo.
echo  Agent stopped. Press any key to exit.
pause >nul

