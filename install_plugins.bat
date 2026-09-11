@echo off
title Install VEGAS <-> DaVinci Resolve Live Bridge Plugins
setlocal enabledelayedexpansion

echo ====================================================================
echo   VEGAS Pro ^<--^> DaVinci Resolve Live Bridge Plugin Installer
echo ====================================================================
echo.

set SCRIPT_DIR=%~dp0
set VEGAS_SRC=%SCRIPT_DIR%plugins\vegas
set RESOLVE_IMP_PY=%SCRIPT_DIR%plugins\resolve\ImportFromVegas.py
set RESOLVE_EXP_PY=%SCRIPT_DIR%plugins\resolve\ExportToVegas.py

:: 1. Install to VEGAS Pro Script Menus
echo [1/2] Installing to VEGAS Pro...
set VEGAS_COUNT=0

:: Copy helper macro
set SCRIPT_LIST="Send to DaVinci Resolve.cs" "Receive from DaVinci Resolve.cs" "Import AI Selects.cs" "Clear All Markers.cs" "Toggle Proxies vs RAW.cs" "Close Timeline Gaps.cs" "Auto Speed Ramp.cs" "Impact Snap Zoom.cs" "Auto Exposure Fix.cs" "Batch Flash Transitions.cs" "Batch Audio Fades.cs" "Color Code Footage.cs" "Clean Media Pool.cs" "Render Regions as Clips.cs"

for %%V in (2026.0 23.0 22.0 21.0 20.0 19.0 18.0 17.0 16.0 15.0 14.0) do (
    set TARGET_DIR=%APPDATA%\VEGAS Pro\%%V\Script Menu
    if exist "%APPDATA%\VEGAS Pro\%%V" (
        if not exist "!TARGET_DIR!" mkdir "!TARGET_DIR!"
        copy /Y "%VEGAS_SRC%\SendToResolve.cs" "!TARGET_DIR!\Send to DaVinci Resolve.cs" >nul 2>&1
        copy /Y "%VEGAS_SRC%\ReceiveFromResolve.cs" "!TARGET_DIR!\Receive from DaVinci Resolve.cs" >nul 2>&1
        copy /Y "%VEGAS_SRC%\ImportAISelects.cs" "!TARGET_DIR!\Import AI Selects.cs" >nul 2>&1
        copy /Y "%VEGAS_SRC%\ClearMarkers.cs" "!TARGET_DIR!\Clear All Markers.cs" >nul 2>&1
        copy /Y "%VEGAS_SRC%\ToggleProxies.cs" "!TARGET_DIR!\Toggle Proxies vs RAW.cs" >nul 2>&1
        copy /Y "%VEGAS_SRC%\CloseTimelineGaps.cs" "!TARGET_DIR!\Close Timeline Gaps.cs" >nul 2>&1
        copy /Y "%VEGAS_SRC%\AutoSpeedRamp.cs" "!TARGET_DIR!\Auto Speed Ramp.cs" >nul 2>&1
        copy /Y "%VEGAS_SRC%\ImpactSnapZoom.cs" "!TARGET_DIR!\Impact Snap Zoom.cs" >nul 2>&1
        copy /Y "%VEGAS_SRC%\AutoExposureFix.cs" "!TARGET_DIR!\Auto Exposure Fix.cs" >nul 2>&1
        copy /Y "%VEGAS_SRC%\BatchFlashTransitions.cs" "!TARGET_DIR!\Batch Flash Transitions.cs" >nul 2>&1
        copy /Y "%VEGAS_SRC%\BatchAudioFades.cs" "!TARGET_DIR!\Batch Audio Fades.cs" >nul 2>&1
        copy /Y "%VEGAS_SRC%\ColorCodeFootage.cs" "!TARGET_DIR!\Color Code Footage.cs" >nul 2>&1
        copy /Y "%VEGAS_SRC%\CleanMediaPool.cs" "!TARGET_DIR!\Clean Media Pool.cs" >nul 2>&1
        copy /Y "%VEGAS_SRC%\RenderRegionsAsClips.cs" "!TARGET_DIR!\Render Regions as Clips.cs" >nul 2>&1
        if !ERRORLEVEL! equ 0 (
            echo   [OK] Installed 14 scripts to VEGAS Pro %%V ^(AppData^)
            set /a VEGAS_COUNT+=1
        )
    )

    :: Check Standard Program Files installation
    set PROG_DIR=%PROGRAMFILES%\VEGAS\VEGAS Pro %%V\Script Menu
    if exist "%PROGRAMFILES%\VEGAS\VEGAS Pro %%V" (
        if not exist "!PROG_DIR!" mkdir "!PROG_DIR!" >nul 2>&1
        copy /Y "%VEGAS_SRC%\*.cs" "!PROG_DIR!\" >nul 2>&1
        echo   [OK] Installed scripts to Program Files VEGAS Pro %%V
        set /a VEGAS_COUNT+=1
    )
)

:: Check BorisFX / VEGAS Pro 2026 installation path
set BORIS_DIR=%PROGRAMFILES%\BorisFX\Vegas Pro 2026\Script Menu
if exist "%PROGRAMFILES%\BorisFX\Vegas Pro 2026" (
    if not exist "!BORIS_DIR!" mkdir "!BORIS_DIR!" >nul 2>&1
    copy /Y "%VEGAS_SRC%\SendToResolve.cs" "!BORIS_DIR!\Send to DaVinci Resolve.cs" >nul 2>&1
    copy /Y "%VEGAS_SRC%\ReceiveFromResolve.cs" "!BORIS_DIR!\Receive from DaVinci Resolve.cs" >nul 2>&1
    copy /Y "%VEGAS_SRC%\ImportAISelects.cs" "!BORIS_DIR!\Import AI Selects.cs" >nul 2>&1
    copy /Y "%VEGAS_SRC%\ClearMarkers.cs" "!BORIS_DIR!\Clear All Markers.cs" >nul 2>&1
    copy /Y "%VEGAS_SRC%\ToggleProxies.cs" "!BORIS_DIR!\Toggle Proxies vs RAW.cs" >nul 2>&1
    copy /Y "%VEGAS_SRC%\CloseTimelineGaps.cs" "!BORIS_DIR!\Close Timeline Gaps.cs" >nul 2>&1
    copy /Y "%VEGAS_SRC%\AutoSpeedRamp.cs" "!BORIS_DIR!\Auto Speed Ramp.cs" >nul 2>&1
    copy /Y "%VEGAS_SRC%\ImpactSnapZoom.cs" "!BORIS_DIR!\Impact Snap Zoom.cs" >nul 2>&1
    copy /Y "%VEGAS_SRC%\AutoExposureFix.cs" "!BORIS_DIR!\Auto Exposure Fix.cs" >nul 2>&1
    copy /Y "%VEGAS_SRC%\BatchFlashTransitions.cs" "!BORIS_DIR!\Batch Flash Transitions.cs" >nul 2>&1
    copy /Y "%VEGAS_SRC%\BatchAudioFades.cs" "!BORIS_DIR!\Batch Audio Fades.cs" >nul 2>&1
    copy /Y "%VEGAS_SRC%\ColorCodeFootage.cs" "!BORIS_DIR!\Color Code Footage.cs" >nul 2>&1
    copy /Y "%VEGAS_SRC%\CleanMediaPool.cs" "!BORIS_DIR!\Clean Media Pool.cs" >nul 2>&1
    copy /Y "%VEGAS_SRC%\RenderRegionsAsClips.cs" "!BORIS_DIR!\Render Regions as Clips.cs" >nul 2>&1
    echo   [OK] Installed 14 scripts to BorisFX Vegas Pro 2026 ^(Program Files^)
    set /a VEGAS_COUNT+=1
)

echo.
:: 2. Install to DaVinci Resolve Script Menu
echo [2/2] Installing to DaVinci Resolve...
set RESOLVE_TARGET1=%PROGRAMDATA%\Blackmagic Design\DaVinci Resolve\Fusion\Scripts\Utility
set RESOLVE_TARGET2=%APPDATA%\Blackmagic Design\DaVinci Resolve\Support\Fusion\Scripts\Utility

if not exist "%RESOLVE_TARGET1%" mkdir "%RESOLVE_TARGET1%" >nul 2>&1
copy /Y "%RESOLVE_IMP_PY%" "%RESOLVE_TARGET1%\ImportFromVegas.py" >nul 2>&1
copy /Y "%RESOLVE_EXP_PY%" "%RESOLVE_TARGET1%\ExportToVegas.py" >nul 2>&1

if not exist "%RESOLVE_TARGET2%" mkdir "%RESOLVE_TARGET2%" >nul 2>&1
copy /Y "%RESOLVE_IMP_PY%" "%RESOLVE_TARGET2%\ImportFromVegas.py" >nul 2>&1
copy /Y "%RESOLVE_EXP_PY%" "%RESOLVE_TARGET2%\ExportToVegas.py" >nul 2>&1

echo   [OK] Installed to DaVinci Resolve Fusion Scripts ^(ImportFromVegas ^& ExportToVegas^)

:: 3. Create Bridge directory in UserProfile
set BRIDGE_DIR=%USERPROFILE%\.timeline_bridge
if not exist "%BRIDGE_DIR%" mkdir "%BRIDGE_DIR%"
copy /Y "%SCRIPT_DIR%core\live_bridge.py" "%BRIDGE_DIR%\live_bridge.py" >nul 2>&1
copy /Y "%SCRIPT_DIR%plugins\resolve\run_live_sync.py" "%BRIDGE_DIR%\run_live_sync.py" >nul 2>&1

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
