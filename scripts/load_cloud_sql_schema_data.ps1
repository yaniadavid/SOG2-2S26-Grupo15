$ErrorActionPreference = "Stop"

Set-Location -Path (Resolve-Path "$PSScriptRoot\..")

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
    Write-Host "No encontre psql.exe. Instale PostgreSQL client o agregue psql al PATH." -ForegroundColor Red
    exit 1
}

$proxy = netstat -ano | findstr ":5433"
if (-not $proxy) {
    Write-Host "No veo Cloud SQL Proxy escuchando en 127.0.0.1:5433." -ForegroundColor Red
    Write-Host "Primero ejecute el proxy hacia soyg2-practica1-g15:us-central1:sog2-postgres." -ForegroundColor Yellow
    exit 1
}

$securePassword = Read-Host "Ingrese la contrasena real de Cloud SQL para postgres" -AsSecureString
$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
try {
    $env:PGPASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
}
finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
}

function Invoke-PsqlFile {
    param([string]$File)

    Write-Host ""
    Write-Host "Ejecutando $File..." -ForegroundColor Cyan
    & $psql -h 127.0.0.1 -p 5433 -U postgres -d ventas_online -v DBNAME=ventas_online -f $File
    if ($LASTEXITCODE -ne 0) {
        throw "Fallo ejecutando $File"
    }
}

try {
    Invoke-PsqlFile "sql/001_esquema.sql"
    Invoke-PsqlFile "sql/002_permisos.sql"
    Invoke-PsqlFile "sql/003_carga.sql"

    Write-Host ""
    Write-Host "Validando conteos finales..." -ForegroundColor Cyan
    & $psql -h 127.0.0.1 -p 5433 -U postgres -d ventas_online -v ON_ERROR_STOP=1 -P pager=off -c "GRANT sog2_owner TO CURRENT_USER; SET ROLE sog2_owner; SELECT 'staging.ventas_online_limpio' AS objeto, COUNT(*) AS registros FROM staging.ventas_online_limpio UNION ALL SELECT 'core.ventas_online', COUNT(*) FROM core.ventas_online UNION ALL SELECT 'analytics.ventas_detalle', COUNT(*) FROM analytics.ventas_detalle ORDER BY objeto; RESET ROLE; REVOKE sog2_owner FROM CURRENT_USER;"
    if ($LASTEXITCODE -ne 0) {
        throw "Fallo validando conteos"
    }

    Write-Host ""
    Write-Host "Carga completa. Si los tres conteos son 1003, reinicie el MCP y luego ADK." -ForegroundColor Green
}
finally {
    Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
}
