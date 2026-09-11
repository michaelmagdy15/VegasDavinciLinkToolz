$asm = [Reflection.Assembly]::LoadFrom("C:\Program Files\BorisFX\Vegas Pro 2026\ScriptPortal.Vegas.dll")
$te = $asm.GetType("ScriptPortal.Vegas.TrackEvent")
$fade = $te.GetProperty("FadeIn").PropertyType
Write-Host "Fade properties:"
foreach ($p in $fade.GetProperties()) {
    Write-Host ("  " + $p.Name + " : " + $p.PropertyType.Name)
}

$ae = $asm.GetType("ScriptPortal.Vegas.AudioEvent")
Write-Host "AudioEvent properties:"
foreach ($p in $ae.GetProperties()) {
    Write-Host ("  " + $p.Name + " : " + $p.PropertyType.Name)
}

$ve = $asm.GetType("ScriptPortal.Vegas.VideoEvent")
Write-Host "VideoEvent properties:"
foreach ($p in $ve.GetProperties()) {
    Write-Host ("  " + $p.Name + " : " + $p.PropertyType.Name)
}
