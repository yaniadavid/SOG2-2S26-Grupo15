#!/usr/bin/env bash
# Verificacion de solo lectura del entorno Odoo. Ejecutar EN la VM.
# Variables requeridas: PGHOST PGUSER PGPASSWORD PGDATABASE (nunca en el archivo).
# Variables opcionales: MIN_MEM_MB (def. 1024), MIN_DISK_MB (def. 5120), LOG_LINEAS (def. 15)
set -euo pipefail

MIN_MEM_MB="${MIN_MEM_MB:-1024}"
MIN_DISK_MB="${MIN_DISK_MB:-5120}"
LOG_LINEAS="${LOG_LINEAS:-15}"
FALLAS=0

reportar() {
  local estado="$1" nombre="$2"
  if [ "$estado" = "0" ]; then
    printf 'OK     %s\n' "$nombre"
  else
    printf 'FALLA  %s\n' "$nombre"
    FALLAS=$((FALLAS + 1))
  fi
}

comprobar() {
  local nombre="$1"; shift
  if "$@" >/dev/null 2>&1; then reportar 0 "$nombre"; else reportar 1 "$nombre"; fi
}

servicio_activo() { systemctl is-active --quiet "$1"; }

# Devuelve 0 si el puerto escucha y TODAS sus direcciones son 127.0.0.1
puerto_solo_loopback() {
  local puerto="$1" direcciones
  direcciones="$(ss -H -ltn "sport = :${puerto}" | awk '{print $4}')"
  [ -n "$direcciones" ] || return 1
  ! printf '%s\n' "$direcciones" | grep -qv '^127\.0\.0\.1:'
}

https_responde() {
  local codigo
  codigo="$(curl -ks -o /dev/null -w '%{http_code}' --max-time 15 https://127.0.0.1/web/login)"
  case "$codigo" in 2??|3??) return 0 ;; *) return 1 ;; esac
}

http_redirige_a_https() {
  local salida
  salida="$(curl -s -o /dev/null -w '%{http_code} %{redirect_url}' --max-time 10 http://127.0.0.1/)"
  case "$salida" in
    30[1278]\ https://*) return 0 ;;
    *) return 1 ;;
  esac
}

variables_pg_definidas() {
  : "${PGHOST:?}" "${PGUSER:?}" "${PGPASSWORD:?}" "${PGDATABASE:?}"
}

postgres_responde() {
  command -v psql >/dev/null 2>&1 || return 1
  [ "$(PGCONNECT_TIMEOUT=10 psql -tA -c 'SELECT 1')" = "1" ]
}

memoria_suficiente() {
  local mb
  mb="$(free -m | awk '/^Mem:/ {print $7}')"
  [ "${mb:-0}" -ge "$MIN_MEM_MB" ]
}

disco_suficiente() {
  local mb
  mb="$(df -Pm / | awk 'NR==2 {print $4}')"
  [ "${mb:-0}" -ge "$MIN_DISK_MB" ]
}

mostrar_recursos() {
  echo "--- Recursos"
  free -h | awk 'NR<=2'
  df -h / | awk 'NR<=2'
}

mostrar_errores_odoo() {
  echo "--- Ultimos errores de odoo (journalctl, prioridad err o superior)"
  journalctl -u odoo -p err -n "$LOG_LINEAS" --no-pager 2>&1 || true
}

main() {
  echo "=== Verificacion de entorno Odoo ($(date -Is)) ==="
  comprobar "servicio odoo activo" servicio_activo odoo
  comprobar "servicio nginx activo" servicio_activo nginx
  comprobar "puerto 8069 solo en 127.0.0.1" puerto_solo_loopback 8069
  comprobar "puerto 8072 solo en 127.0.0.1" puerto_solo_loopback 8072
  comprobar "HTTPS 443 responde (curl -k)" https_responde
  comprobar "puerto 80 redirige a https" http_redirige_a_https
  comprobar "variables PG* definidas" variables_pg_definidas
  comprobar "PostgreSQL SELECT 1 (requiere psql)" postgres_responde
  comprobar "memoria disponible >= ${MIN_MEM_MB} MB" memoria_suficiente
  comprobar "disco libre en / >= ${MIN_DISK_MB} MB" disco_suficiente
  mostrar_recursos
  mostrar_errores_odoo
  echo "=== Fallas: ${FALLAS} ==="
  [ "$FALLAS" -eq 0 ]
}

main "$@"
