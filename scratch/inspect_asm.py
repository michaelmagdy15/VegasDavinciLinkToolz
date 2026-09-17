import sys
import subprocess

ps = r"""
$asm = [Reflection.Assembly]::LoadFrom("C:\Program Files\BorisFX\Vegas Pro 2026\ScriptPortal.Vegas.dll")
$type = $asm.GetType("ScriptPortal.Vegas.VideoStream")
if ($type) {
    Write-Host "--- VideoStream Properties ---"
    $type.GetProperties() | ForEach-Object { "$($_.PropertyType.FullName) $($_.Name)" }
}

Write-Host "--- Rotation Types ---"
$asm.GetTypes() | Where-Object { $_.Name -match "Rotat" } | ForEach-Object { $_.FullName }
"""

with open("scratch/check_asm.ps1", "w", encoding="utf-8") as f:
    f.write(ps)

r = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "scratch/check_asm.ps1"], capture_output=True, text=True)
print(r.stdout)
if r.stderr:
    print("Error:", r.stderr)
