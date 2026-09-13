@echo off
title VEGAS Pro - DaVinci Resolve Live Link Dashboard
setlocal enabledelayedexpansion
cd /d "%~dp0"

:: Find Python binary
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
if not defined PYTHON_BIN set "PYTHON_BIN=python"

echo Launching VEGAS Pro - DaVinci Resolve Live Link Dashboard...
start "" "%PYTHON_BIN%" gui\live_link_dashboard.py
exit /b 0
