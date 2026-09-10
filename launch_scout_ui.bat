@echo off
title Vegas Scout AI — Windows 11 WinUI 3 Launcher
setlocal

set SCRIPT_DIR=%~dp0
set EXE_DEBUG=%SCRIPT_DIR%apps\VegasScoutUI\bin\Debug\net9.0-windows10.0.26100.0\win-x64\VegasScoutUI.exe
set EXE_RELEASE=%SCRIPT_DIR%apps\VegasScoutUI\bin\Release\net9.0-windows10.0.26100.0\win-x64\VegasScoutUI.exe

if exist "%EXE_RELEASE%" (
    start "" "%EXE_RELEASE%"
    exit /b 0
)

if exist "%EXE_DEBUG%" (
    start "" "%EXE_DEBUG%"
    exit /b 0
)

echo Building Vegas Scout AI (WinUI 3)...
dotnet build "%SCRIPT_DIR%apps\VegasScoutUI\VegasScoutUI.csproj" -c Release
if %ERRORLEVEL% equ 0 (
    if exist "%EXE_RELEASE%" (
        start "" "%EXE_RELEASE%"
        exit /b 0
    )
)

if exist "%EXE_DEBUG%" (
    start "" "%EXE_DEBUG%"
    exit /b 0
)

echo [Error] Could not launch Vegas Scout AI. Please ensure .NET 9 SDK is installed.
pause
