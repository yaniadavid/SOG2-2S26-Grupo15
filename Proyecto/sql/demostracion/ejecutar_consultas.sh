#!/usr/bin/env bash
# Ejecuta las consultas de verificacion en orden dentro de una transaccion de solo lectura.
# Requiere las variables de entorno PGHOST, PGUSER, PGPASSWORD y PGDATABASE (opcional: PGPORT, PGSSLMODE).
# La contrasena nunca se imprime ni se pasa por linea de comandos.
set -euo pipefail

for var in PGHOST PGUSER PGPASSWORD PGDATABASE; do
    if [ -z "${!var:-}" ]; then
        echo "Falta la variable de entorno $var" >&2
        exit 1
    fi
done

if ! command -v psql >/dev/null 2>&1; then
    echo "psql no esta instalado o no esta en el PATH" >&2
    exit 1
fi

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ARCHIVOS=(
    01_conteos_requisitos.sql
    02_ventas.sql
    03_compras.sql
    04_facturas.sql
    05_empleados.sql
    06_integridad.sql
)

for archivo in "${ARCHIVOS[@]}"; do
    [ -f "$DIR/$archivo" ] || { echo "No existe $DIR/$archivo" >&2; exit 1; }
done

echo "Base: $PGDATABASE en $PGHOST (usuario $PGUSER)"

{
    echo "\\pset null '-'"
    echo "\\pset pager off"
    echo "BEGIN READ ONLY;"
    for archivo in "${ARCHIVOS[@]}"; do
        echo "\\echo"
        echo "\\echo >>>>>>>>>> $archivo"
        cat "$DIR/$archivo"
    done
    echo "ROLLBACK;"
} | psql -X -q -v ON_ERROR_STOP=1 --no-password
