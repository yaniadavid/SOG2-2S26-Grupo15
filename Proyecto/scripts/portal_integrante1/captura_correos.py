"""Servidor SMTP de depuracion: guarda cada mensaje como .eml y no reenvia nada.

Escucha SOLO en 127.0.0.1:1025 (Python 3.10, modulo smtpd).

Uso (en la misma maquina que ejecuta Odoo):
    python captura_correos.py --carpeta /tmp/correos_capturados

Apuntar temporalmente Odoo a el (Ajustes > Tecnico > Servidores de correo saliente):
    Servidor SMTP 127.0.0.1, puerto 1025, cifrado Ninguno, sin usuario ni clave.
    Si Odoo corre en Docker, 127.0.0.1 es el contenedor: ejecute este script dentro
    de el o use red de host. Desactive o elimine ese servidor al terminar; el nombre
    del servidor temporal debe llevar el prefijo I1-PORTAL.
Los correos quedan en la carpeta indicada como <fecha>_<n>.eml.
"""
import argparse
import asyncore
import itertools
import smtpd
from datetime import datetime
from pathlib import Path

HOST = "127.0.0.1"
PUERTO = 1025


def nombre_archivo(ahora: datetime, numero: int) -> str:
    return f"{ahora.strftime('%Y%m%d_%H%M%S')}_{numero:04d}.eml"


def guardar(carpeta: Path, nombre: str, datos: bytes) -> Path:
    carpeta.mkdir(parents=True, exist_ok=True)
    destino = carpeta / nombre
    destino.write_bytes(datos)
    return destino


class ServidorCaptura(smtpd.SMTPServer):
    def __init__(self, carpeta: Path):
        super().__init__((HOST, PUERTO), None, decode_data=False)
        self._carpeta = carpeta
        self._contador = itertools.count(1)

    def process_message(self, peer, mailfrom, rcpttos, data, **kwargs):
        nombre = nombre_archivo(datetime.now(), next(self._contador))
        destino = guardar(self._carpeta, nombre, data)
        print(f"Capturado: {destino.name} ({len(data)} bytes)", flush=True)
        return None


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--carpeta", type=Path, default=Path("correos_capturados"))
    args = parser.parse_args()
    ServidorCaptura(args.carpeta)
    print(f"Escuchando en {HOST}:{PUERTO}; guardando en {args.carpeta}", flush=True)
    try:
        asyncore.loop()
    except KeyboardInterrupt:
        print("Detenido.")


if __name__ == "__main__":
    main()
