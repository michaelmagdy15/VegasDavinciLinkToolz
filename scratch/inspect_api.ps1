$asm = [System.Reflection.Assembly]::LoadFrom("C:\Program Files\BorisFX\Vegas Pro 2026\ScriptPortal.Vegas.dll")

Write-Host "=== VideoStream Properties ==="
$vs = $asm.GetType("ScriptPortal.Vegas.VideoStream")
$vs.GetProperties() | ForEach-Object {
    if ($_.Name -match "Rotat|Orient|Aspect|Width|Height") {
        Write-Host "$($_.Name) : $($_.PropertyType.Name)"
    }
}

Write-Host "`n=== VideoStream Methods ==="
$vs.GetMethods() | ForEach-Object {
    if ($_.Name -match "Rotat|Orient") {
        Write-Host "$($_.Name)"
    }
}

Write-Host "`n=== VideoEvent Properties ==="
$ve = $asm.GetType("ScriptPortal.Vegas.VideoEvent")
$ve.GetProperties() | ForEach-Object {
    if ($_.Name -match "Rotat|Orient") {
        Write-Host "$($_.Name) : $($_.PropertyType.Name)"
    }
}

Write-Host "`n=== VideoMotion Properties ==="
$vm = $asm.GetType("ScriptPortal.Vegas.VideoMotion")
if ($vm) {
    $vm.GetProperties() | ForEach-Object {
        Write-Host "$($_.Name) : $($_.PropertyType.Name)"
    }
}

Write-Host "`n=== Enums with Rotation ==="
$asm.GetTypes() | Where-Object { $_.IsEnum -and ($_.Name -match "Rotat|Orient") } | ForEach-Object {
    Write-Host "$($_.FullName)"
    [Enum]::GetNames($_) | ForEach-Object { Write-Host "  $_" }
}
