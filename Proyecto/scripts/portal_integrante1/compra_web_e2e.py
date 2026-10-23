"""Compra web de extremo a extremo con un cliente nuevo (solo urllib y cookies).

Variables de entorno: ODOO_URL (obligatoria). ODOO_DB, ODOO_USER y ODOO_PASSWORD solo
si no se indica --product-id (se busca un producto I1-PV- publicado por XML-RPC).
Uso: python compra_web_e2e.py [--dry-run] [--product-id N] [--cantidad 1]

Partes del recorrido NO deducibles de las rutas (parametrizadas):
  * campos exactos del formulario de direccion (se toman del HTML de /shop/address),
  * seleccion del metodo de envio (su ruta no aparece en rutas_portal.txt; se asume
    que 'Standard delivery' queda preseleccionado al ser el unico),
  * ruta y parametros del simulador Demo (por defecto /payment/demo/simulate_payment).
"""
import argparse
import http.cookiejar
import json
import os
import re
import ssl
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime
from html.parser import HTMLParser

from comun_portal import MARCA

RUTA_SIMULADOR_DEMO = "/payment/demo/simulate_payment"
CLAVE_RUTA = "transaction_route"
PASSWORD_QA = "Qa-" + "Portal-2026"  # contrasena desechable del usuario de prueba
RECORRIDO_MANUAL = (
    "Recorrido manual equivalente: abrir {url}/web/signup y registrarse; abrir {url}/shop y "
    "agregar un producto I1-PV-; Carrito > Pagar; completar direccion; confirmar envio "
    "'Standard delivery'; en el pago elegir 'Demo' y pulsar Pagar; anotar el numero de orden "
    "de /shop/confirmation."
)

# ---------------------------------------------------------------- logica pura


def marca_temporal(ahora: datetime) -> str:
    return f"{MARCA}-{ahora.strftime('%Y%m%d-%H%M%S')}"


def datos_cliente(marca: str) -> dict:
    return {"login": f"{marca.lower()}@example.com", "name": f"Cliente {marca}"}


class ExtractorHtml(HTMLParser):
    """Recolecta inputs ocultos y los atributos data-* de los elementos de la pagina."""

    def __init__(self):
        super().__init__()
        self.ocultos = {}
        self.elementos_data = []

    def handle_starttag(self, tag, atributos):
        attrs = dict(atributos)
        if tag == "input" and attrs.get("type") == "hidden" and attrs.get("name"):
            self.ocultos[attrs["name"]] = attrs.get("value") or ""
        data = {k: v for k, v in attrs.items() if k.startswith("data-")}
        if data:
            self.elementos_data.append(data)


def analizar_html(html: str) -> ExtractorHtml:
    extractor = ExtractorHtml()
    extractor.feed(html)
    return extractor


def extraer_csrf(html: str) -> str:
    token = analizar_html(html).ocultos.get("csrf_token")
    if not token:
        raise ValueError("No se encontro csrf_token en la pagina")
    return token


def a_snake(clave_data: str) -> str:
    return clave_data.removeprefix("data-").replace("-", "_")


def contexto_pago(html: str) -> dict:
    """Une los data-* de la pagina de pago en un dict con claves snake_case."""
    contexto = {}
    for data in analizar_html(html).elementos_data:
        for clave, valor in data.items():
            contexto.setdefault(a_snake(clave), valor)
    return contexto


def opcion_demo(html: str) -> dict:
    """Primer elemento con data-provider-code=demo (ids de proveedor y metodo)."""
    for data in analizar_html(html).elementos_data:
        if data.get("data-provider-code") == "demo":
            return {a_snake(k): v for k, v in data.items()}
    return {}


PARAMETROS_PERMITIDOS = ("access_token", "landing_route")


def parametros_transaccion(contexto: dict, opcion: dict, csrf: str, forzados: dict) -> dict:
    """Parametros de /shop/payment/transaction/<id>; lo no deducible se puede forzar."""
    base = {k: v for k, v in contexto.items() if k in PARAMETROS_PERMITIDOS}
    base.update({
        "provider_id": opcion.get("provider_id") or opcion.get("payment_option_id"),
        "payment_method_id": opcion.get("payment_method_id"),
        "token_id": None, "flow": "direct", "tokenization_requested": False,
        "is_validation": False, "csrf_token": csrf,
    })
    base.update({k: v for k, v in forzados.items() if v is not None})
    for clave in ("provider_id", "payment_method_id"):
        if base.get(clave) is not None:
            base[clave] = int(base[clave])
    return base


def sobre_jsonrpc(parametros: dict) -> bytes:
    return json.dumps({"jsonrpc": "2.0", "method": "call", "params": parametros}).encode()


def parametros_simulacion(referencia: str, estado: str = "done") -> dict:
    return {"reference": referencia, "payment_details": "", "simulated_state": estado}


def nombre_orden_desde(html: str, referencia: str) -> str:
    """Nombre de orden: patron S0000N en la confirmacion, o prefijo de la referencia."""
    coincidencia = re.search(r"\bS\d{4,}\b", html)
    if coincidencia:
        return coincidencia.group(0)
    return re.split(r"[-/]", referencia)[0] if referencia else ""


def plan_texto(url: str, marca: str, producto, cantidad: int, simulador: str) -> list:
    cliente = datos_cliente(marca)
    return [
        f"1. GET  {url}/web/signup  (extraer csrf_token)",
        f"2. POST {url}/web/signup  login={cliente['login']} name={cliente['name']}",
        f"3. POST {url}/shop/cart/update_json  product_id={producto or '(buscar I1-PV-)'} add_qty={cantidad}",
        f"4. GET  {url}/shop/checkout ; si pide direccion: POST {url}/shop/address/submit",
        f"5. GET  {url}/shop/confirm_order ; GET {url}/shop/payment  (ids de proveedor Demo)",
        f"6. POST {url}/shop/payment/transaction/<order_id>  (JSON-RPC, flujo direct)",
        f"7. POST {url}{simulador}  simulated_state=done  (parametros NO verificados)",
        f"8. GET  {url}/shop/payment/validate -> /shop/confirmation ; devolver nombre de orden",
        RECORRIDO_MANUAL.format(url=url),
    ]

# ------------------------------------------------------ efectos de red (HTTP)


class Navegador:
    def __init__(self, url: str, sin_verificar_ssl: bool):
        self.url = url
        contexto = ssl._create_unverified_context() if sin_verificar_ssl else ssl.create_default_context()
        jar = http.cookiejar.CookieJar()
        self.opener = urllib.request.build_opener(
            urllib.request.HTTPCookieProcessor(jar), urllib.request.HTTPSHandler(context=contexto))

    def _abrir(self, peticion):
        with self.opener.open(peticion, timeout=60) as r:
            return r.geturl(), r.read().decode("utf-8", "replace")

    def get(self, ruta: str):
        return self._abrir(urllib.request.Request(self.url + ruta))

    def post_form(self, ruta: str, campos: dict):
        cuerpo = urllib.parse.urlencode(campos).encode()
        return self._abrir(urllib.request.Request(self.url + ruta, data=cuerpo))

    def post_json(self, ruta: str, parametros: dict):
        peticion = urllib.request.Request(
            self.url + ruta, data=sobre_jsonrpc(parametros),
            headers={"Content-Type": "application/json"})
        _, texto = self._abrir(peticion)
        respuesta = json.loads(texto)
        if respuesta.get("error"):
            detalle = respuesta["error"].get("data", {}).get("message", respuesta["error"])
            raise RuntimeError(f"{ruta}: {detalle}")
        return respuesta.get("result")


def buscar_producto_xmlrpc() -> int:
    from conexion_odoo import conectar_desde_entorno
    ejecutar = conectar_desde_entorno()
    filas = ejecutar("product.product", "search_read", [[
        ("default_code", "=like", "I1-PV-%"), ("website_published", "=", True),
        ("sale_ok", "=", True)]], {"fields": ["id"], "limit": 1})
    if not filas:
        raise SystemExit("No hay producto I1-PV- publicado; indique --product-id.")
    return filas[0]["id"]


def buscar_metodo_envio_xmlrpc() -> int:
    from conexion_odoo import conectar_desde_entorno
    ejecutar = conectar_desde_entorno()
    filas = ejecutar("delivery.carrier", "search_read", [[("is_published", "=", True)]],
                     {"fields": ["id"], "limit": 1})
    if not filas:
        raise SystemExit("No hay metodo de envio publicado.")
    return filas[0]["id"]


def registrar(nav: Navegador, marca: str) -> dict:
    _, html = nav.get("/web/signup")
    cliente = datos_cliente(marca)
    nav.post_form("/web/signup", {
        "csrf_token": extraer_csrf(html), "login": cliente["login"], "name": cliente["name"],
        "password": PASSWORD_QA, "confirm_password": PASSWORD_QA, "redirect": ""})
    return cliente


def completar_direccion(nav: Navegador, cliente: dict, args) -> None:
    """Envia /shop/address/submit mientras el checkout redirija a un formulario de direccion
    (primero facturacion y luego entrega, con el partner_id que indica la URL)."""
    for _ in range(3):
        destino, _html = nav.get("/shop/checkout")
        if "/shop/address" not in destino:
            return
        consulta = urllib.parse.parse_qs(urllib.parse.urlparse(destino).query)
        _, formulario = nav.get(urllib.parse.urlparse(destino).path + "?" + urllib.parse.urlparse(destino).query)
        campos = dict(analizar_html(formulario).ocultos)
        campos.update({
            "csrf_token": extraer_csrf(formulario), "name": cliente["name"], "email": cliente["login"],
            "phone": "50255550000", "street": "Calle QA 1", "city": "Guatemala", "zip": "01001",
            "country_id": args.pais_id,
        })
        campos["partner_id"] = consulta.get("partner_id", ["-1"])[0]
        campos["address_type"] = consulta.get("address_type", [campos.get("address_type", "billing")])[0]
        nav.post_form("/shop/address/submit", campos)


def ejecutar_compra(nav: Navegador, marca: str, args) -> str:
    cliente = registrar(nav, marca)
    producto = args.product_id or buscar_producto_xmlrpc()
    nav.post_json("/shop/cart/update_json", {"product_id": producto, "add_qty": args.cantidad})
    completar_direccion(nav, cliente, args)
    nav.get("/shop/confirm_order")
    nav.post_json("/shop/set_delivery_method", {"dm_id": buscar_metodo_envio_xmlrpc()})
    _, pago = nav.get("/shop/payment")
    contexto, opcion = contexto_pago(pago), opcion_demo(pago)
    orden_id = args.order_id or contexto.get("sale_order_id") or contexto.get("order_id")
    if not orden_id or not (opcion or args.provider_id):
        raise SystemExit("No se dedujo orden/proveedor Demo del HTML de pago; use --order-id y "
                         "--provider-id, o el recorrido manual.\n" + RECORRIDO_MANUAL.format(url=nav.url))
    forzados = {"provider_id": args.provider_id, "payment_method_id": args.payment_method_id}
    params = parametros_transaccion(contexto, opcion, extraer_csrf(pago), forzados)
    ruta = contexto.get(CLAVE_RUTA) or f"/shop/payment/transaction/{orden_id}"
    resultado = nav.post_json(ruta, params) or {}
    referencia = resultado.get("reference", "")
    nav.post_json(args.ruta_simulador, parametros_simulacion(referencia))
    _, confirmacion = nav.get("/shop/payment/validate")
    return nombre_orden_desde(confirmacion, referencia)

# ------------------------------------------------------------------ entrada


def construir_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    p.add_argument("--dry-run", action="store_true", help="solo imprime el plan")
    p.add_argument("--product-id", type=int, help="product.product a comprar")
    p.add_argument("--cantidad", type=int, default=1)
    p.add_argument("--pais-id", default="90", help="res.country id de Guatemala (verificar en la base)")
    p.add_argument("--order-id", help="forzar id de sale.order si no se deduce del HTML")
    p.add_argument("--provider-id", help="forzar payment.provider Demo")
    p.add_argument("--payment-method-id", help="forzar payment.method")
    p.add_argument("--ruta-simulador", default=RUTA_SIMULADOR_DEMO)
    return p


def main() -> None:
    args = construir_parser().parse_args()
    url = os.environ.get("ODOO_URL", "").rstrip("/")
    if not url:
        raise SystemExit("Falta la variable de entorno ODOO_URL")
    marca = marca_temporal(datetime.now())
    if args.dry_run:
        print("\n".join(plan_texto(url, marca, args.product_id, args.cantidad, args.ruta_simulador)))
        return
    sin_ssl = os.environ.get("ODOO_SSL_NO_VERIFY", "").lower() in {"1", "true", "si", "yes"}
    try:
        orden = ejecutar_compra(Navegador(url, sin_ssl), marca, args)
    except (urllib.error.URLError, RuntimeError, ValueError) as error:
        print(f"Fallo del recorrido: {error}\n" + RECORRIDO_MANUAL.format(url=url), file=sys.stderr)
        raise SystemExit(1)
    print(f"Marca: {marca}\nOrden: {orden}")


if __name__ == "__main__":
    main()
