$ErrorActionPreference = "Stop"

Set-Location -Path (Resolve-Path "$PSScriptRoot\..")

$env:DB_HOST = "127.0.0.1"
$env:DB_PORT = "5433"
$env:DB_NAME = "ventas_online"
$env:DB_USER = "postgres"

$securePassword = Read-Host "Ingrese la contrasena real de Cloud SQL para postgres" -AsSecureString
$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
try {
    $env:DB_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
    $env:PGPASSWORD = $env:DB_PASSWORD
}
finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
}

Write-Host ""
Write-Host "1) Probando con Python/pg8000..." -ForegroundColor Cyan
try {
    python -c "from sog2.business import total_registros_disponibles; print(total_registros_disponibles())"
    Write-Host "Python/pg8000: OK" -ForegroundColor Green
}
catch {
    Write-Host "Python/pg8000: FALLO" -ForegroundColor Red
}

Write-Host ""
Write-Host "2) Probando con psql si esta instalado..." -ForegroundColor Cyan
$psqlCandidates = @(
    "C:\Program Files\PostgreSQL\17\bin\psql.exe",
    "C:\Program Files\PostgreSQL\16\bin\psql.exe",
    "psql.exe"
)

$psql = $null
foreach ($candidate in $psqlCandidates) {
    $cmd = Get-Command $candidate -ErrorAction SilentlyContinue
    if ($cmd) {
        $psql = $cmd.Source
        break
    }
}

if (-not $psql) {
    Write-Host "No encontre psql.exe en rutas comunes." -ForegroundColor Yellow
    exit 0
}

& $psql -h 127.0.0.1 -p 5433 -U postgres -d ventas_online -c "SELECT current_user, current_database(), COUNT(*) AS registros FROM analytics.ventas_detalle;"

if ($LASTEXITCODE -eq 0) {
    Write-Host "psql: OK" -ForegroundColor Green
}
else {
    Write-Host "psql: FALLO" -ForegroundColor Red
}
