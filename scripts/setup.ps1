param([string]$Python = 'python')
$ErrorActionPreference = 'Stop'
$skillRoot = Split-Path -Parent $PSScriptRoot
$runtime = Join-Path $skillRoot '.venv'
$exe = Join-Path $runtime 'Scripts\python.exe'
if (-not (Test-Path -LiteralPath $exe)) {
    & $Python -m venv $runtime
    if ($LASTEXITCODE -ne 0) { throw 'Could not create dedicated Python environment' }
}
& $exe -m pip install -r (Join-Path $skillRoot 'requirements.txt')
if ($LASTEXITCODE -ne 0) { throw 'Dependency installation failed' }
& $exe -c 'import swisseph, zoneinfo; print(\"Calculation runtime ready:\", swisseph.version, zoneinfo.ZoneInfo(\"Asia/Kolkata\"))'
if ($LASTEXITCODE -ne 0) { throw 'Runtime import check failed' }
