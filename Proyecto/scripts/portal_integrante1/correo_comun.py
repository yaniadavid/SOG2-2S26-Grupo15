"""Piezas compartidas por los scripts de correo del portal (constantes y argumentos)."""
import argparse
import sys
from pathlib import Path

RAIZ_CARGA = Path(__file__).resolve().parents[2] / "carga_integrante1"
if str(RAIZ_CARGA) not in sys.path:
    sys.path.insert(0, str(RAIZ_CARGA))

from conexion_odoo import (  # noqa: E402,F401
    Ejecutor, asegurar, buscar_ids, conectar_desde_entorno, informar,
)

PREFIJO = "I1-PORTAL"
NOMBRE_PLANTILLA = f"{PREFIJO} Campana post-compra"
NOMBRE_REGLA = f"{PREFIJO} Campana post-compra"
NOMBRE_ACCION = f"{PREFIJO} Enviar campana"
NOMBRE_SERVIDOR = f"{PREFIJO} SMTP"
ASUNTO_CAMPANA = "QuetzalMart - Promocion exclusiva para usted"
MODELO_ORDEN = "sale.order"
MINUTOS_DIFERIDO = 5


def crear_parser(descripcion: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=descripcion)
    modo = parser.add_mutually_exclusive_group()
    modo.add_argument("--dry-run", action="store_true",
                      help="No escribe nada (modo por defecto).")
    modo.add_argument("--aplicar", action="store_true",
                      help="Escribe los cambios en Odoo.")
    return parser


def id_modelo(ejecutar: Ejecutor, modelo: str) -> int:
    ids = buscar_ids(ejecutar, "ir.model", [("model", "=", modelo)])
    if not ids:
        raise SystemExit(f"No existe el modelo {modelo} en ir.model.")
    return ids[0]


def buscar_plantilla(ejecutar: Ejecutor, nombre: str) -> int | None:
    ids = buscar_ids(ejecutar, "mail.template", [("name", "=", nombre)])
    return ids[0] if ids else None
