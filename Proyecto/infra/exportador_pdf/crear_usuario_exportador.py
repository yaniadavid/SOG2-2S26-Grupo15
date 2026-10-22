#!/usr/bin/env python3
"""Crea el usuario interno de minimo privilegio exportador_pdf (solo lectura de contabilidad).

Solo biblioteca estandar. Entorno: ODOO_URL, ODOO_DB, ODOO_ADMIN_USER, ODOO_ADMIN_PASSWORD,
EXPORT_PASSWORD. Idempotente: si el login ya existe no modifica nada.
Grupos asignados: base.group_user (usuario interno) y account.group_account_readonly
(Facturacion: solo lectura). Nunca se asignan grupos de administracion.
"""
import os
import sys
import xmlrpc.client

LOGIN = "exportador_pdf"
NOMBRE = "Exportador PDF (solo lectura)"
GRUPOS_MINIMOS = (("base", "group_user"), ("account", "group_account_readonly"))
VARIABLES = ("ODOO_URL", "ODOO_DB", "ODOO_ADMIN_USER", "ODOO_ADMIN_PASSWORD", "EXPORT_PASSWORD")


# ---------------------------------------------------------------- funciones puras

def variables_faltantes(entorno):
    return [v for v in VARIABLES if not entorno.get(v)]


def valores_usuario(ids_grupos, contrasena):
    """Valores de res.users.create; (6, 0, ids) fija exactamente los grupos minimos."""
    return {
        "name": NOMBRE,
        "login": LOGIN,
        "password": contrasena,
        "groups_id": [(6, 0, list(ids_grupos))],
    }


def decidir_accion(ids_existentes):
    return "omitir" if ids_existentes else "crear"


# ---------------------------------------------------------------- efectos

def conectar(entorno):
    url = entorno["ODOO_URL"].rstrip("/")
    comun = xmlrpc.client.ServerProxy(url + "/xmlrpc/2/common")
    uid = comun.authenticate(
        entorno["ODOO_DB"], entorno["ODOO_ADMIN_USER"], entorno["ODOO_ADMIN_PASSWORD"], {})
    if not uid:
        raise RuntimeError("Autenticacion de administrador rechazada")
    modelos = xmlrpc.client.ServerProxy(url + "/xmlrpc/2/object", allow_none=True)

    def ejecutar(modelo, metodo, args, kwargs=None):
        return modelos.execute_kw(
            entorno["ODOO_DB"], uid, entorno["ODOO_ADMIN_PASSWORD"], modelo, metodo, args, kwargs or {})
    return ejecutar


def buscar_usuarios(ejecutar):
    return ejecutar("res.users", "search", [[["login", "=", LOGIN]]], {"context": {"active_test": False}})


def resolver_grupo(ejecutar, modulo, nombre):
    filas = ejecutar("ir.model.data", "search_read",
                     [[["module", "=", modulo], ["name", "=", nombre], ["model", "=", "res.groups"]]],
                     {"fields": ["res_id"], "limit": 1})
    if not filas:
        raise RuntimeError("Grupo no encontrado: %s.%s" % (modulo, nombre))
    return filas[0]["res_id"]


def crear_usuario(ejecutar, contrasena):
    ids_grupos = [resolver_grupo(ejecutar, m, n) for m, n in GRUPOS_MINIMOS]
    return ejecutar("res.users", "create", [valores_usuario(ids_grupos, contrasena)])


def main():
    faltantes = variables_faltantes(os.environ)
    if faltantes:
        print("Faltan variables de entorno: %s" % ", ".join(faltantes), file=sys.stderr)
        return 2
    try:
        ejecutar = conectar(os.environ)
        if decidir_accion(buscar_usuarios(ejecutar)) == "omitir":
            print("El usuario %s ya existe; no se modifica" % LOGIN)
            return 0
        crear_usuario(ejecutar, os.environ["EXPORT_PASSWORD"])
        print("Usuario %s creado con grupos minimos" % LOGIN)
        return 0
    except (xmlrpc.client.Error, OSError, RuntimeError) as e:
        print("Error: %s" % type(e).__name__, file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
