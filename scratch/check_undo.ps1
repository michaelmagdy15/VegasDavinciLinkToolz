$asm = [System.Reflection.Assembly]::LoadFrom('C:\Program Files\BorisFX\Vegas Pro 2026\ScriptPortal.Vegas.dll')
$asm.GetTypes() | Where-Object { $_.Name -like '*Undo*' } | ForEach-Object {
    Write-Host "Type: " $_.FullName
    $_.GetConstructors() | ForEach-Object { Write-Host "   ctor: " $_.ToString() }
}
