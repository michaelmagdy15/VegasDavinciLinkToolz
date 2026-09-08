@echo off
title Vegas ^<--^> Resolve Timeline Bridge
setlocal enabledelayedexpansion
cd /d "%~dp0"

:: Check if Python is installed
python --version >nul 2>&1
if %ERRORLEVEL% neq 0 (
    echo.
    echo ====================================================================
    echo   Python is not detected on your system!
    echo ====================================================================
    echo.
    echo   To run this tool, you need Python 3.8 or newer.
    echo.
    echo   1. Download from: https://www.python.org/downloads/
    echo   2. Run the installer
    echo   3. IMPORTANT: Check the box "Add python.exe to PATH"
    echo   4. Re-launch this file
    echo.
    echo ====================================================================
    echo.
    pause
    exit /b 1
)

:: If a file was dragged and dropped onto launch.bat
if not "%~1"=="" (
    start "" python main.py "%~1"
) else (
    start "" python main.py
)
