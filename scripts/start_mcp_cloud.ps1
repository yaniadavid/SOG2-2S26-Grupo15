$ErrorActionPreference = "Stop"

Set-Location -Path (Resolve-Path "$PSScriptRoot\..")

$env:DB_HOST = "127.0.0.1"
$env:DB_PORT = "5433"
$env:DB_NAME = "ventas_online"
$env:DB_USER = "postgres"
$env:MCP_HOST = "127.0.0.1"
$env:PORT = "8080"

$securePassword = Read-Host "Ingrese la contrasena real de Cloud SQL para el usuario postgres" -AsSecureString
$bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($securePassword)
try {
    $env:DB_PASSWORD = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
}
finally {
    [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
}

Write-Host ""
Write-Host "Validando conexion y total de registros..." -ForegroundColor Cyan
python -c "from sog2.business import total_registros_disponibles; print(total_registros_disponibles())"

if ($LASTEXITCODE -ne 0) {
    Write-Host ""
    Write-Host "La validacion fallo. Revise que Cloud SQL Proxy este corriendo en 127.0.0.1:5433 y que la contrasena sea correcta." -ForegroundColor Red
    exit $LASTEXITCODE
}

Write-Host ""
Write-Host "Validacion correcta. Iniciando MCP en http://127.0.0.1:8080/mcp" -ForegroundColor Green
Write-Host "Deje esta ventana abierta mientras use ADK." -ForegroundColor Yellow
python -m sog2.server
