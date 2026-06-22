@echo off
title SafeNet Kids — Child Protection Agent
color 0A
echo.
echo  ===================================
echo   SafeNet Kids — Protection Agent
echo  ===================================
echo.

:: Set your Gemini API key as a Windows Environment Variable instead of here.
:: Go to: Windows Search > "Edit system environment variables" > Environment Variables > New
:: Variable name: GEMINI_API_KEY   Value: your_key_here
set SAFENET_API=https://safenetkidsproject-production.up.railway.app


echo  [1] Ask your parent for the Link Code
echo  [2] Type it below when asked
echo.
python agent/monitor.py

echo.
echo  Agent stopped. Press any key to exit.
pause > nul
