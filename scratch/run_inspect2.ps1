$asm = [Reflection.Assembly]::LoadFrom("C:\Program Files\BorisFX\Vegas Pro 2026\ScriptPortal.Vegas.dll")
$vm = $asm.GetType("ScriptPortal.Vegas.VideoMotion")
Write-Host "VideoMotion properties:"
foreach ($p in $vm.GetProperties()) {
    Write-Host ("  " + $p.Name + " : " + $p.PropertyType.Name)
}

$env = $asm.GetType("ScriptPortal.Vegas.Envelope")
Write-Host "Envelope properties:"
foreach ($p in $env.GetProperties()) {
    Write-Host ("  " + $p.Name + " : " + $p.PropertyType.Name)
}
