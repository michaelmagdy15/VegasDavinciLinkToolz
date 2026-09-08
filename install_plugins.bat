@echo off
title Install VEGAS <-> DaVinci Resolve Live Bridge Plugins
setlocal enabledelayedexpansion

echo ====================================================================
echo   VEGAS Pro ^<--^> DaVinci Resolve Live Bridge Plugin Installer
echo ====================================================================
echo.

set SCRIPT_DIR=%~dp0
set VEGAS_SEND_CS=%SCRIPT_DIR%plugins\vegas\SendToResolve.cs
set VEGAS_RECV_CS=%SCRIPT_DIR%plugins\vegas\ReceiveFromResolve.cs
set RESOLVE_IMP_PY=%SCRIPT_DIR%plugins\resolve\ImportFromVegas.py
set RESOLVE_EXP_PY=%SCRIPT_DIR%plugins\resolve\ExportToVegas.py

:: 1. Install to VEGAS Pro Script Menus
echo [1/2] Installing to VEGAS Pro...
set VEGAS_COUNT=0

for %%V in (2026.0 23.0 22.0 21.0 20.0) do (
    set TARGET_DIR=%APPDATA%\VEGAS Pro\%%V\Script Menu
    if exist "%APPDATA%\VEGAS Pro\%%V" (
        if not exist "!TARGET_DIR!" mkdir "!TARGET_DIR!"
        copy /Y "%VEGAS_SEND_CS%" "!TARGET_DIR!\Send to DaVinci Resolve.cs" >nul 2>&1
        copy /Y "%VEGAS_RECV_CS%" "!TARGET_DIR!\Receive from DaVinci Resolve.cs" >nul 2>&1
        if !ERRORLEVEL! equ 0 (
            echo   [OK] Installed to VEGAS Pro %%V ^(Send to DaVinci Resolve ^& Receive from DaVinci Resolve^)
            set /a VEGAS_COUNT+=1
        )
    )
)

if %VEGAS_COUNT% equ 0 (
    set TARGET_DIR=%APPDATA%\VEGAS Pro\2026.0\Script Menu
    mkdir "!TARGET_DIR!" >nul 2>&1
    copy /Y "%VEGAS_SEND_CS%" "!TARGET_DIR!\Send to DaVinci Resolve.cs" >nul 2>&1
    copy /Y "%VEGAS_RECV_CS%" "!TARGET_DIR!\Receive from DaVinci Resolve.cs" >nul 2>&1
    echo   [OK] Installed to VEGAS Pro 2026.0
)

echo.
:: 2. Install to DaVinci Resolve Script Menu
echo [2/2] Installing to DaVinci Resolve...
set RESOLVE_TARGET=%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Developer\Scripting\Scripts\Utility
if not exist "%RESOLVE_TARGET%" mkdir "%RESOLVE_TARGET%"
copy /Y "%RESOLVE_IMP_PY%" "%RESOLVE_TARGET%\ImportFromVegas.py" >nul 2>&1
copy /Y "%RESOLVE_EXP_PY%" "%RESOLVE_TARGET%\ExportToVegas.py" >nul 2>&1
if %ERRORLEVEL% equ 0 (
    echo   [OK] Installed to DaVinci Resolve ^(ImportFromVegas ^& ExportToVegas^)
) else (
    echo   [WARN] Could not copy to Resolve Scripts folder.
)

:: 3. Create Bridge directory in UserProfile
set BRIDGE_DIR=%USERPROFILE%\.timeline_bridge
if not exist "%BRIDGE_DIR%" mkdir "%BRIDGE_DIR%"
copy /Y "%SCRIPT_DIR%core\live_bridge.py" "%BRIDGE_DIR%\live_bridge.py" >nul 2>&1

echo.
echo ====================================================================
echo   Installation Complete!
echo.
echo   VEGAS Pro:
echo     - Tools -^> Scripting -^> Send to DaVinci Resolve
echo     - Tools -^> Scripting -^> Receive from DaVinci Resolve
echo.
echo   DaVinci Resolve:
echo     - Workspace -^> Scripts -^> ImportFromVegas
echo     - Workspace -^> Scripts -^> ExportToVegas
echo ====================================================================
echo.
pause
