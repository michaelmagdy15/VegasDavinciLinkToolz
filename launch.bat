@echo off
title Vegas - Resolve Timeline Bridge
setlocal enabledelayedexpansion
cd /d "%~dp0"

:: 1. Find valid Python executable dynamically
set "PYTHON_BIN="
for %%V in (Python313 Python312 Python311 Python310) do (
    if not defined PYTHON_BIN (
        if exist "%LOCALAPPDATA%\Programs\Python\%%V\python.exe" (
            set "PYTHON_BIN=%LOCALAPPDATA%\Programs\Python\%%V\python.exe"
        )
    )
)

if not defined PYTHON_BIN (
    for %%P in (python py) do (
        where %%P >nul 2>&1
        if !ERRORLEVEL! equ 0 (
            set "PYTHON_BIN=%%P"
            goto :found_python
        )
    )
)

:found_python
if not exist "%PYTHON_BIN%" (
    where python >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        set "PYTHON_BIN=python"
    ) else (
        echo.
        echo ====================================================================
        echo   Python is not detected on your system!
        echo ====================================================================
        echo.
        echo   Please install Python 3.8 or newer from https://www.python.org/
        echo   Make sure to check "Add Python to PATH".
        echo.
        pause
        exit /b 1
    )
)

:: 2. Launch application
if not "%~1"=="" (
    "%PYTHON_BIN%" main.py "%~1"
) else (
    "%PYTHON_BIN%" main.py
)

if %ERRORLEVEL% neq 0 (
    echo.
    echo Application stopped with error code %ERRORLEVEL%.
    pause
)
