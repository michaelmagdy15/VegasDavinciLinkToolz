import sys
import subprocess

ps = r"""
$asm = [Reflection.Assembly]::LoadFrom("C:\Program Files\BorisFX\Vegas Pro 2026\ScriptPortal.Vegas.dll")
$enumType = $asm.GetType("ScriptPortal.Vegas.VideoOutputRotation")
[Enum]::GetNames($enumType)
"""

with open("scratch/check_enum.ps1", "w", encoding="utf-8") as f:
    f.write(ps)

r = subprocess.run(["powershell", "-ExecutionPolicy", "Bypass", "-File", "scratch/check_enum.ps1"], capture_output=True, text=True)
print("VideoOutputRotation values:")
print(r.stdout)
