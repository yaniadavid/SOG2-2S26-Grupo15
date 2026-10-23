"""Piezas compartidas por los scripts de QA del portal (sin credenciales)."""
import os
import re
import sys
import xmlrpc.client

RAIZ_SCRIPTS = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
sys.path.insert(0, os.path.join(RAIZ_SCRIPTS, "carga_integrante1"))

MARCA = "I1-PORTAL-QA"
CARPETA_PDF_VM = "/var/lib/quetzalmart/facturas_pdf"
ERROR_NO_SERIALIZABLE = "cannot marshal None"


def contiene_marca(*textos) -> bool:
    return any(MARCA.lower() in str(t).lower() for t in textos if t)


def sanitizar_numero(numero) -> str:
    """Misma regla que el exportador de la VM para nombrar el PDF."""
    return re.sub(r"[^A-Za-z0-9.\-]+", "_", str(numero or "")).strip("._")


def nombre_pdf(numero_factura) -> str:
    return sanitizar_numero(numero_factura) + ".pdf"


def comando_ls_pdf(numero_factura) -> str:
    return f"sudo ls -l {CARPETA_PDF_VM}/{nombre_pdf(numero_factura)}"


def es_fallo_no_serializable(fallo: xmlrpc.client.Fault) -> bool:
    return ERROR_NO_SERIALIZABLE in str(fallo.faultString)


def ejecutar_tolerante(ejecutar, modelo, metodo, args, kwargs=None):
    """Tolera solo el fallo de empaquetado de la respuesta; el efecto ya se aplico."""
    try:
        return ejecutar(modelo, metodo, args, kwargs or {})
    except xmlrpc.client.Fault as fallo:
        if not es_fallo_no_serializable(fallo):
            raise
        return None
