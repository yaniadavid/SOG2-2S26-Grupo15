param(
    [string]$Ruta = (Join-Path $env:LOCALAPPDATA 'QuetzalMartRPA\credencial.dat')
)

$ErrorActionPreference = 'Stop'
$usuario = Read-Host 'Usuario de integración de Odoo (correo)'
if ([string]::IsNullOrWhiteSpace($usuario)) { throw 'El usuario no puede estar vacío.' }
$segura = Read-Host 'Clave de API de Odoo' -AsSecureString
$puntero = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($segura)
$texto = $null
$bytes = $null
try {
    $texto = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($puntero)
    if ([string]::IsNullOrWhiteSpace($texto)) { throw 'La clave no puede estar vacía.' }
    $bytes = [Text.Encoding]::UTF8.GetBytes($texto)
    $cifrada = [Security.Cryptography.ProtectedData]::Protect(
        $bytes, $null, [Security.Cryptography.DataProtectionScope]::CurrentUser
    )
    $carpeta = Split-Path -Path $Ruta -Parent
    New-Item -ItemType Directory -Path $carpeta -Force | Out-Null
    [IO.File]::WriteAllLines($Ruta, @($usuario.Trim(), [Convert]::ToBase64String($cifrada)), [Text.Encoding]::UTF8)
    Write-Output "Credencial guardada para el usuario actual de Windows en $Ruta"
}
finally {
    if ($bytes) { [Array]::Clear($bytes, 0, $bytes.Length) }
    if ($puntero -ne [IntPtr]::Zero) { [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($puntero) }
    $texto = $null
}
