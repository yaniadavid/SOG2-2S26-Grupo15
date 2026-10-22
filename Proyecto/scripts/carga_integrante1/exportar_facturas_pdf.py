"""Exporta a PDF las facturas publicadas con el reporte estandar account.report_invoice.

Ejecutar en la VM (la variable env la provee el shell de Odoo):
    EXPORT_DIR=/tmp/facturas_pdf odoo shell -d <base> --no-http < exportar_facturas_pdf.py
Opcional: PREFIJO_REF (por defecto I1-) filtra por el campo ref de la factura.
"""
import os
import re
from pathlib import Path

REPORTE = "account.report_invoice"
TIPOS_FACTURA = ("out_invoice", "in_invoice")


def nombre_archivo(factura) -> str:
    base = factura.name or f"factura_{factura.id}"
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", f"{base}_{factura.ref or ''}").strip("_") + ".pdf"


def facturas_publicadas(entorno, prefijo: str):
    return entorno["account.move"].search([
        ("state", "=", "posted"),
        ("move_type", "in", TIPOS_FACTURA),
        ("ref", "=like", prefijo + "%"),
    ], order="move_type, name")


def renderizar_pdf(entorno, factura) -> bytes:
    contenido, _formato = entorno["ir.actions.report"]._render_qweb_pdf(REPORTE, [factura.id])
    return contenido


def exportar(entorno, carpeta: Path, prefijo: str) -> list:
    carpeta.mkdir(parents=True, exist_ok=True)
    rutas = []
    for factura in facturas_publicadas(entorno, prefijo):
        ruta = carpeta / nombre_archivo(factura)
        ruta.write_bytes(renderizar_pdf(entorno, factura))
        rutas.append(ruta)
    return rutas


def main(entorno) -> None:
    carpeta = Path(os.environ.get("EXPORT_DIR", "facturas_pdf"))
    rutas = exportar(entorno, carpeta, os.environ.get("PREFIJO_REF", "I1-"))
    print(f"PDF generados: {len(rutas)} en {carpeta.resolve()}")


main(env)  # noqa: F821 - 'env' lo inyecta 'odoo shell'
