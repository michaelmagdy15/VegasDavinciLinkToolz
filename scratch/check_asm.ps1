
$asm = [Reflection.Assembly]::LoadFrom("C:\Program Files\BorisFX\Vegas Pro 2026\ScriptPortal.Vegas.dll")
$type = $asm.GetType("ScriptPortal.Vegas.VideoStream")
if ($type) {
    Write-Host "--- VideoStream Properties ---"
    $type.GetProperties() | ForEach-Object { "$($_.PropertyType.FullName) $($_.Name)" }
}

Write-Host "--- Rotation Types ---"
$asm.GetTypes() | Where-Object { $_.Name -match "Rotat" } | ForEach-Object { $_.FullName }
