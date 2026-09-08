@echo off
title Vegas - Resolve Timeline Bridge
setlocal enabledelayedexpansion
cd /d "%~dp0"

:: 1. Find valid Python executable
set "PYTHON_BIN=C:\Users\Mi5a\AppData\Local\Programs\Python\Python312\python.exe"
if exist "%PYTHON_BIN%" goto :found_python

for %%P in (python py) do (
    where %%P >nul 2>&1
    if !ERRORLEVEL! equ 0 (
        set "PYTHON_BIN=%%P"
        goto :found_python
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
