"""Utilidades compartidas de los scripts del portal: ruta de conexion_odoo, argumentos, escritura."""
import argparse
import sys
from pathlib import Path

RAIZ_SCRIPTS = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(RAIZ_SCRIPTS / "carga_integrante1"))

from conexion_odoo import asegurar, buscar_ids, conectar_desde_entorno, informar  # noqa: E402

MARCA = "I1-PORTAL"
NOMBRE_SITIO = "QuetzalMart"
METODO_ENVIO = "Standard delivery"
PREFIJO_VENTA = "I1-PV-"
PREFIJO_MATERIAL = "I1-MAT-"


def crear_parser(descripcion: str) -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=descripcion)
    parser.add_argument("--aplicar", action="store_true",
                        help="Escribe en Odoo. Sin esta opcion es simulacion (--dry-run, por defecto).")
    parser.add_argument("--dry-run", action="store_true", help="Simulacion; es el comportamiento por defecto.")
    return parser


def modo_aplicar(argumentos: argparse.Namespace) -> bool:
    if argumentos.aplicar and argumentos.dry_run:
        raise SystemExit("Use --aplicar o --dry-run, no ambos.")
    return argumentos.aplicar


def escribir(ejecutar, aplicar: bool, modelo: str, ids: list, valores: dict, etiqueta: str) -> None:
    """Efecto aislado: write si se aplica; siempre informa."""
    informar(f"[{'APLICA' if aplicar else 'SIMULA'}] {modelo} {ids}: {etiqueta}")
    if aplicar and valores:
        ejecutar(modelo, "write", [ids, valores])


def leer_uno(ejecutar, modelo: str, dominio: list, campos: list):
    filas = ejecutar(modelo, "search_read", [dominio],
                     {"fields": campos, "limit": 1, "context": {"active_test": False}})
    return filas[0] if filas else None
