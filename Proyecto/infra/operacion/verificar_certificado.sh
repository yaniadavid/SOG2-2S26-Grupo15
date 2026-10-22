#!/usr/bin/env bash
# Verificacion de solo lectura del certificado de Let's Encrypt. Ejecutar EN la VM.
# Opcionales: CERTBOT (def. /snap/bin/certbot), HOST_TLS (def. localhost), MIN_DIAS (def. 2),
#             DIR_GANCHOS (def. /etc/letsencrypt/renewal-hooks/deploy)
# Las direcciones IPv4 se enmascaran en toda la salida impresa.
set -euo pipefail

CERTBOT="${CERTBOT:-/snap/bin/certbot}"
HOST_TLS="${HOST_TLS:-localhost}"
MIN_DIAS="${MIN_DIAS:-2}"
DIR_GANCHOS="${DIR_GANCHOS:-/etc/letsencrypt/renewal-hooks/deploy}"
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
  if "$@"; then reportar 0 "$nombre"; else reportar 1 "$nombre"; fi
}

enmascarar_ip() { sed -E 's/[0-9]{1,3}(\.[0-9]{1,3}){3}/<IP>/g'; }

como_root() {
  if [ "$(id -u)" -eq 0 ]; then "$@"; else sudo "$@"; fi
}

temporizador_activo() { systemctl is-active --quiet snap.certbot.renew.timer; }
temporizador_habilitado() { systemctl is-enabled --quiet snap.certbot.renew.timer; }

gancho_existe() {
  [ -d "$DIR_GANCHOS" ] && find "$DIR_GANCHOS" -maxdepth 1 -type f -perm -u+x | grep -q .
}

listar_certificados() {
  echo "--- certbot certificates"
  como_root "$CERTBOT" certificates 2>&1 | enmascarar_ip
}

simular_renovacion() {
  local salida
  echo "--- certbot renew --dry-run"
  if salida="$(como_root "$CERTBOT" renew --dry-run 2>&1)"; then
    printf '%s\n' "$salida" | enmascarar_ip | tail -n 8
    return 0
  fi
  printf '%s\n' "$salida" | enmascarar_ip | tail -n 15
  return 1
}

# Imprime el certificado servido por Nginx en formato PEM
certificado_servido() {
  openssl s_client -connect "${HOST_TLS}:443" </dev/null 2>/dev/null \
    | openssl x509 2>/dev/null
}

# Imprime el notAfter servido como epoch; falla si no se pudo leer
vencimiento_epoch() {
  local pem fecha
  pem="$(certificado_servido)" || return 1
  [ -n "$pem" ] || return 1
  fecha="$(printf '%s\n' "$pem" | openssl x509 -noout -enddate | cut -d= -f2)"
  echo "notAfter servido: $fecha" >&2
  date -d "$fecha" +%s
}

dias_restantes() {
  local venc="$1" ahora
  ahora="$(date +%s)"
  echo $(( (venc - ahora) / 86400 ))
}

margen_suficiente() {
  local venc dias
  venc="$(vencimiento_epoch)" || return 1
  dias="$(dias_restantes "$venc")"
  echo "dias restantes: $dias (minimo exigido: $MIN_DIAS)" >&2
  [ "$dias" -ge "$MIN_DIAS" ]
}

main() {
  echo "=== Verificacion de certificado ($(date -Is)) ==="
  comprobar "snap.certbot.renew.timer activo" temporizador_activo
  comprobar "snap.certbot.renew.timer habilitado" temporizador_habilitado
  systemctl list-timers snap.certbot.renew.timer --no-pager 2>&1 | enmascarar_ip | head -n 3 || true
  comprobar "gancho ejecutable en $DIR_GANCHOS" gancho_existe
  comprobar "certbot certificates" listar_certificados
  comprobar "certbot renew --dry-run" simular_renovacion
  comprobar "vigencia servida >= ${MIN_DIAS} dias" margen_suficiente
  echo "=== Fallas: ${FALLAS} ==="
  [ "$FALLAS" -eq 0 ]
}

main "$@"
