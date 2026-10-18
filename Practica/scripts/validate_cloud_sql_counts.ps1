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
    Write-Host "No encontre psql.exe." -ForegroundColor Red
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

try {
    & $psql -h 127.0.0.1 -p 5433 -U postgres -d ventas_online -v ON_ERROR_STOP=1 -P pager=off -c "GRANT sog2_owner TO CURRENT_USER; SET ROLE sog2_owner; SELECT 'staging.ventas_online_limpio' AS objeto, COUNT(*) AS registros FROM staging.ventas_online_limpio UNION ALL SELECT 'core.ventas_online', COUNT(*) FROM core.ventas_online UNION ALL SELECT 'analytics.ventas_detalle', COUNT(*) FROM analytics.ventas_detalle ORDER BY objeto; RESET ROLE; REVOKE sog2_owner FROM CURRENT_USER;"
}
finally {
    Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
}
