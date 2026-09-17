
$asm = [Reflection.Assembly]::LoadFrom("C:\Program Files\BorisFX\Vegas Pro 2026\ScriptPortal.Vegas.dll")
$enumType = $asm.GetType("ScriptPortal.Vegas.VideoOutputRotation")
[Enum]::GetNames($enumType)
