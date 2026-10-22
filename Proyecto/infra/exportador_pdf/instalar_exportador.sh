#!/usr/bin/env bash
# Instala el exportador de PDF. Ejecutar EN la VM como root (sudo), desde la carpeta que contiene
# exportador.py y los archivos .service/.timer. NO crea /etc/quetzalmart/exportador.env (lo hace
# el orquestador con la contrasena); el timer se habilita pero no arranca hasta que ese archivo exista.
set -euo pipefail

USUARIO="quetzalmart-export"
DIR_APP="/opt/quetzalmart"
DIR_DATOS="/var/lib/quetzalmart/facturas_pdf"
DIR_ENTORNO="/etc/quetzalmart"
ARCHIVO_ENTORNO="${DIR_ENTORNO}/exportador.env"
ORIGEN="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

exigir_root() { [ "$(id -u)" -eq 0 ] || { echo "Ejecutar con sudo" >&2; exit 1; }; }

crear_usuario_sistema() {
  if id "$USUARIO" >/dev/null 2>&1; then
    echo "usuario $USUARIO ya existe"
  else
    useradd --system --no-create-home --home-dir /nonexistent --shell /usr/sbin/nologin "$USUARIO"
  fi
}

crear_carpetas() {
  install -d -m 0755 -o root -g root "$DIR_APP"
  install -d -m 0750 -o root -g root "$DIR_ENTORNO"
  install -d -m 0755 -o root -g root /var/lib/quetzalmart
  install -d -m 0750 -o "$USUARIO" -g "$USUARIO" "$DIR_DATOS"
}

copiar_archivos() {
  install -m 0755 -o root -g root "${ORIGEN}/exportador.py" "${DIR_APP}/exportador.py"
  install -m 0644 -o root -g root "${ORIGEN}/quetzalmart-exportador.service" /etc/systemd/system/
  install -m 0644 -o root -g root "${ORIGEN}/quetzalmart-exportador.timer" /etc/systemd/system/
}

habilitar_timer() {
  systemctl daemon-reload
  systemctl enable quetzalmart-exportador.timer
}

arrancar_si_hay_entorno() {
  if [ -f "$ARCHIVO_ENTORNO" ]; then
    systemctl start quetzalmart-exportador.timer
    echo "timer iniciado"
  else
    echo "Falta ${ARCHIVO_ENTORNO} (600, root). Crearlo y luego: systemctl start quetzalmart-exportador.timer"
  fi
}

main() {
  exigir_root
  crear_usuario_sistema
  crear_carpetas
  copiar_archivos
  habilitar_timer
  arrancar_si_hay_entorno
}

main "$@"
