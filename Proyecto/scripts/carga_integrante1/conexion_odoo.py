"""Capa fina de efectos colaterales: unica puerta de acceso XML-RPC a Odoo."""
import os
import ssl
import sys
import time
import xmlrpc.client
from dataclasses import dataclass
from typing import Any, Callable

VARIABLES_REQUERIDAS = ("ODOO_URL", "ODOO_DB", "ODOO_USER", "ODOO_PASSWORD")
VALORES_VERDADEROS = {"1", "true", "si", "yes"}

Ejecutor = Callable[..., Any]


@dataclass(frozen=True)
class Configuracion:
    url: str
    base_datos: str
    usuario: str
    clave: str
    sin_verificar_ssl: bool


def leer_configuracion(entorno: dict) -> Configuracion:
    faltantes = [v for v in VARIABLES_REQUERIDAS if not entorno.get(v)]
    if faltantes:
        raise SystemExit("Faltan variables de entorno: " + ", ".join(faltantes))
    return Configuracion(
        url=entorno["ODOO_URL"].rstrip("/"),
        base_datos=entorno["ODOO_DB"],
        usuario=entorno["ODOO_USER"],
        clave=entorno["ODOO_PASSWORD"],
        sin_verificar_ssl=entorno.get("ODOO_SSL_NO_VERIFY", "").lower() in VALORES_VERDADEROS,
    )


def crear_contexto_ssl(sin_verificar: bool) -> ssl.SSLContext:
    if sin_verificar:
        return ssl._create_unverified_context()
    return ssl.create_default_context()


def _proxy(url: str, ruta: str, contexto: ssl.SSLContext) -> xmlrpc.client.ServerProxy:
    return xmlrpc.client.ServerProxy(
        f"{url}/xmlrpc/2/{ruta}", context=contexto, allow_none=True
    )


def conectar(config: Configuracion) -> Ejecutor:
    """Devuelve ejecutar(modelo, metodo, args, kwargs) ya autenticado."""
    contexto = crear_contexto_ssl(config.sin_verificar_ssl)
    uid = _proxy(config.url, "common", contexto).authenticate(
        config.base_datos, config.usuario, config.clave, {}
    )
    if not uid:
        raise SystemExit("Autenticacion rechazada por Odoo (revise usuario y base de datos).")
    objeto = _proxy(config.url, "object", contexto)

    def ejecutar(modelo: str, metodo: str, args: list = None, kwargs: dict = None):
        return objeto.execute_kw(
            config.base_datos, uid, config.clave, modelo, metodo, args or [], kwargs or {}
        )

    return ejecutar


def conectar_desde_entorno() -> Ejecutor:
    return conectar(leer_configuracion(os.environ))


def buscar_ids(ejecutar: Ejecutor, modelo: str, dominio: list) -> list:
    return ejecutar(modelo, "search", [dominio], {"context": {"active_test": False}})


def asegurar(ejecutar: Ejecutor, modelo: str, dominio: list, valores: dict,
             contexto: dict = None) -> tuple:
    """Idempotente: devuelve (id, creado) sin duplicar el registro de clave natural."""
    existentes = buscar_ids(ejecutar, modelo, dominio)
    if existentes:
        return existentes[0], False
    nuevo = ejecutar(modelo, "create", [valores], {"context": contexto or {}})
    return nuevo, True


def pausar(segundos: float) -> None:
    if segundos > 0:
        time.sleep(segundos)


def informar(mensaje: str) -> None:
    print(mensaje, file=sys.stdout, flush=True)
