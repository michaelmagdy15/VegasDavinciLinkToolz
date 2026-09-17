@echo off
title VEGAS Pro to DaVinci Resolve 21 Live Transfer
setlocal enabledelayedexpansion
color 0B

echo ====================================================================
echo   VEGAS Pro -^> DaVinci Resolve 21.1 Live Transfer
echo ====================================================================
echo.

:: Locate Python
set "PYTHON_BIN=python"
if exist "%LOCALAPPDATA%\Programs\Python\Python312\python.exe" (
    set "PYTHON_BIN=%LOCALAPPDATA%\Programs\Python\Python312\python.exe"
)

echo [1/2] Checking timeline manifest...
if not exist "%USERPROFILE%\.timeline_bridge\vegas_timeline.json" (
    color 0C
    echo [ERROR] No VEGAS timeline manifest found!
    echo Please open VEGAS Pro and run:
    echo   Tools -^> Scripting -^> Send to DaVinci Resolve
    echo.
    pause
    exit /b 1
)

echo [2/2] Synchronizing into DaVinci Resolve 21...
"%PYTHON_BIN%" "C:\Users\Mi5a\VegasDavinciLinkTool\plugins\resolve\run_live_sync.py"

echo.
echo ====================================================================
echo   Transfer Finished!
echo   If Resolve did not automatically focus, open DaVinci Resolve
echo   and click: Workspace -^> Scripts -^> ImportFromVegas
echo ====================================================================
echo.
pause
