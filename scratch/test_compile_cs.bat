@echo off
"C:\Windows\Microsoft.NET\Framework64\v4.0.30319\csc.exe" /target:library /r:"C:\Program Files\BorisFX\Vegas Pro 2026\ScriptPortal.Vegas.dll" /r:System.Windows.Forms.dll /out:"%TEMP%\TestVegasPlugin.dll" "plugins\vegas\SendToResolve.cs"
if %errorlevel% neq 0 (
    echo [FAIL] Compilation failed
    exit /b %errorlevel%
)
echo [OK] Compilation succeeded!
