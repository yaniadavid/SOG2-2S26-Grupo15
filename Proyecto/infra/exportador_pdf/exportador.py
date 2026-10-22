#!/usr/bin/env python3
"""Exporta a PDF las facturas publicadas (out_invoice e in_invoice) de Odoo.

Solo biblioteca estandar (Python 3.10). Idempotente: solo descarga lo que falta.
Entorno: ODOO_URL, ODOO_DB, EXPORT_USER, EXPORT_PASSWORD, EXPORT_DIR.
Recomendado ODOO_URL=http://127.0.0.1:8069 (el certificado publico es de la IP, no de loopback).
Imprime unicamente conteos; nunca credenciales ni nombres de clientes.
"""
import json
import os
import re
import sys
import urllib.error
import urllib.request
from http.cookiejar import CookieJar

TIPOS_FACTURA = ["out_invoice", "in_invoice"]
TIMEOUT_SEGUNDOS = 120
VARIABLES = ("ODOO_URL", "ODOO_DB", "EXPORT_USER", "EXPORT_PASSWORD", "EXPORT_DIR")


class SesionExpirada(Exception):
    """La sesion HTTP ya no es valida y hay que autenticar de nuevo."""


# ---------------------------------------------------------------- funciones puras

def sanitizar_numero(numero):
    """Deja solo letras, digitos, punto y guion; el resto pasa a guion bajo."""
    limpio = re.sub(r"[^A-Za-z0-9.\-]+", "_", str(numero or "")).strip("._")
    return limpio


def nombre_base(factura):
    limpio = sanitizar_numero(factura.get("name"))
    return limpio if limpio else "sin_numero_%s" % factura["id"]


def nombres_de_archivo(facturas):
    """Mapa id -> nombre de archivo .pdf; si dos numeros chocan se agrega el id."""
    bases = [nombre_base(f) for f in facturas]
    repetidas = {b for b in bases if bases.count(b) > 1}
    return {
        f["id"]: "%s%s.pdf" % (b, "_%s" % f["id"] if b in repetidas else "")
        for f, b in zip(facturas, bases)
    }


def facturas_faltantes(facturas, archivos_existentes):
    """Devuelve [(factura, nombre)] de las facturas cuyo PDF aun no existe."""
    existentes = set(archivos_existentes)
    nombres = nombres_de_archivo(facturas)
    return [(f, nombres[f["id"]]) for f in facturas if nombres[f["id"]] not in existentes]


def es_pdf(contenido):
    return contenido[:5] == b"%PDF-"


def leer_configuracion(entorno):
    """Devuelve (configuracion, variables_faltantes)."""
    faltantes = [v for v in VARIABLES if not entorno.get(v)]
    config = {v: entorno.get(v, "") for v in VARIABLES}
    config["ODOO_URL"] = config["ODOO_URL"].rstrip("/")
    return config, faltantes


def error_de_sesion(respuesta_json):
    """True si la respuesta JSON-RPC indica sesion expirada o falta de acceso."""
    error = respuesta_json.get("error")
    if not error:
        return False
    datos = error.get("data") or {}
    nombre = str(datos.get("name", ""))
    return "SessionExpired" in nombre or error.get("code") == 100


# ---------------------------------------------------------------- efectos

def crear_cliente():
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))


def pedir(cliente, url, cuerpo=None):
    cabeceras = {"Content-Type": "application/json"} if cuerpo is not None else {}
    datos = json.dumps(cuerpo).encode() if cuerpo is not None else None
    peticion = urllib.request.Request(url, data=datos, headers=cabeceras)
    try:
        with cliente.open(peticion, timeout=TIMEOUT_SEGUNDOS) as r:
            return r.read(), r.headers.get("Content-Type", "")
    except urllib.error.HTTPError as e:
        if e.code in (401, 403):
            raise SesionExpirada() from e
        raise


def llamar_json(cliente, url, params):
    cuerpo, _ = pedir(cliente, url, {"jsonrpc": "2.0", "method": "call", "params": params})
    respuesta = json.loads(cuerpo)
    if error_de_sesion(respuesta):
        raise SesionExpirada()
    if respuesta.get("error"):
        raise RuntimeError("Odoo devolvio un error JSON-RPC")
    return respuesta["result"]


def autenticar(cliente, config):
    resultado = llamar_json(cliente, config["ODOO_URL"] + "/web/session/authenticate", {
        "db": config["ODOO_DB"],
        "login": config["EXPORT_USER"],
        "password": config["EXPORT_PASSWORD"],
    })
    if not resultado.get("uid"):
        raise RuntimeError("Autenticacion rechazada")


def listar_facturas(cliente, config):
    return llamar_json(cliente, config["ODOO_URL"] + "/web/dataset/call_kw", {
        "model": "account.move",
        "method": "search_read",
        "args": [[["state", "=", "posted"], ["move_type", "in", TIPOS_FACTURA]]],
        "kwargs": {"fields": ["id", "name"], "order": "id asc"},
    })


def descargar_pdf(cliente, config, id_factura):
    url = "%s/report/pdf/account.report_invoice/%s" % (config["ODOO_URL"], id_factura)
    contenido, _ = pedir(cliente, url)
    if not es_pdf(contenido):
        # Una sesion expirada redirige al login (HTML), no devuelve PDF
        raise SesionExpirada()
    return contenido


def guardar_atomico(carpeta, nombre, contenido):
    destino = os.path.join(carpeta, nombre)
    temporal = destino + ".part"
    with open(temporal, "wb") as f:
        f.write(contenido)
    os.replace(temporal, destino)


def con_reautenticacion(cliente, config, operacion):
    """Ejecuta operacion(); si la sesion expiro, autentica de nuevo y reintenta una vez."""
    try:
        return operacion()
    except SesionExpirada:
        autenticar(cliente, config)
        return operacion()


def archivos_pdf_existentes(carpeta):
    return [n for n in os.listdir(carpeta) if n.endswith(".pdf")]


def exportar(config):
    carpeta = config["EXPORT_DIR"]
    os.makedirs(carpeta, exist_ok=True)
    cliente = crear_cliente()
    autenticar(cliente, config)
    facturas = con_reautenticacion(cliente, config, lambda: listar_facturas(cliente, config))
    pendientes = facturas_faltantes(facturas, archivos_pdf_existentes(carpeta))
    descargadas = fallidas = 0
    for factura, nombre in pendientes:
        try:
            pdf = con_reautenticacion(
                cliente, config, lambda: descargar_pdf(cliente, config, factura["id"]))
            guardar_atomico(carpeta, nombre, pdf)
            descargadas += 1
        except (urllib.error.URLError, OSError, RuntimeError, SesionExpirada):
            fallidas += 1
    print("publicadas=%d ya_existian=%d descargadas=%d fallidas=%d" % (
        len(facturas), len(facturas) - len(pendientes), descargadas, fallidas))
    return fallidas


def main():
    config, faltantes = leer_configuracion(os.environ)
    if faltantes:
        print("Faltan variables de entorno: %s" % ", ".join(faltantes), file=sys.stderr)
        return 2
    try:
        return 1 if exportar(config) else 0
    except (urllib.error.URLError, OSError, RuntimeError, SesionExpirada, ValueError) as e:
        print("Error: %s" % type(e).__name__, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
