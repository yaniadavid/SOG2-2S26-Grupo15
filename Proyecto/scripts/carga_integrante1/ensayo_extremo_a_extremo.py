"""Ensayo de una venta nueva de punta a punta con limpieza segura (Integrante 1).

Flujo: crear venta I1-E2E-<fecha-hora> -> confirmar -> facturar con el asistente estandar
-> escribir ref en la factura -> publicar -> reportar numeros consumidos.
Limpieza: la factura se reabre a borrador y se cancela, y la venta se cancela. Nunca se borra nada.

Variables de entorno: ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASSWORD, ODOO_SSL_NO_VERIFY (opcional).
Uso:
    python ensayo_extremo_a_extremo.py --dry-run       muestra el plan sin conectarse
    python ensayo_extremo_a_extremo.py                 flujo completo + limpieza + verificacion
    python ensayo_extremo_a_extremo.py --solo-crear    flujo sin limpiar (para mostrar el PDF en vivo)
    python ensayo_extremo_a_extremo.py --limpiar       cancela todo residuo I1-E2E- y verifica
Codigos de salida: 0 correcto, 1 conteos fuera de lo esperado, 2 fallo de Odoo o del flujo,
3 la base no esta en el estado inicial esperado (no se crea nada).
"""
import argparse
import re
import sys
import xmlrpc.client
from datetime import datetime

import generador_datos as gen
from cargador_xmlrpc import (comparar_conteos, es_respuesta_no_serializable, estado_de,
                             facturar_con_asistente, facturas_de_orden, resolver_ids_base)
from conexion_odoo import Ejecutor, buscar_ids, conectar_desde_entorno, informar

PREFIJO_E2E = gen.PREFIJO + "E2E-"
CONTEO_BASE = {"ventas": 50, "facturas_cliente": 17, "facturas_proveedor": 33}
CANTIDAD_LINEA = 1
CONTEXTO_SIN_ASISTENTE_CANCELACION = {"disable_cancel_warning": True}


class ErrorEnsayo(Exception):
    """El flujo no dejo a Odoo en el estado esperado."""

# ---------------------------------------------------------------- logica pura


def referencia_e2e(ahora: datetime) -> str:
    return PREFIJO_E2E + ahora.strftime("%Y%m%d-%H%M%S")


def excluir_e2e(campo: str) -> list:
    return ["!", (campo, "=like", PREFIJO_E2E + "%")]


def dominios_conteo() -> dict:
    """Conteos de la base verificada: prefijo I1- sin los documentos del ensayo."""
    de_i1 = lambda campo: [(campo, "=like", gen.PREFIJO + "%")] + excluir_e2e(campo)  # noqa: E731
    return {
        "ventas": ("sale.order", de_i1("client_order_ref") + [("state", "=", "sale")]),
        "facturas_cliente": ("account.move", de_i1("ref") + [("move_type", "=", "out_invoice"),
                                                              ("state", "=", "posted")]),
        "facturas_proveedor": ("account.move", de_i1("ref") + [("move_type", "=", "in_invoice"),
                                                                ("state", "=", "posted")]),
    }


def valores_venta_e2e(referencia: str, cliente: int, producto: dict, impuesto: int) -> dict:
    linea = {
        "product_id": producto["id"], "name": producto["name"],
        "product_uom_qty": CANTIDAD_LINEA, "price_unit": producto["list_price"],
        "tax_id": [(6, 0, [impuesto])],
    }
    return {"partner_id": cliente, "client_order_ref": referencia, "order_line": [(0, 0, linea)]}


def nombre_pdf_esperado(nombre_factura: str, referencia: str) -> str:
    """Replica nombre_archivo de exportar_facturas_pdf.py para avisar que PDF retirar."""
    return re.sub(r"[^A-Za-z0-9_.-]+", "_", f"{nombre_factura}_{referencia}").strip("_") + ".pdf"


def pasos_limpieza_factura(estado: str) -> list:
    return {"posted": ["button_draft", "button_cancel"], "draft": ["button_cancel"]}.get(estado, [])


def requiere_cancelar_venta(estado: str) -> bool:
    return estado in ("draft", "sent", "sale")


def errores_de_estado(documento: str, obtenido: str, esperado: str) -> list:
    if obtenido == esperado:
        return []
    return [f"{documento}: estado {obtenido!r}, se esperaba {esperado!r}"]


def lineas_de_consumo(consumo: dict) -> list:
    return [
        "Numeros consumidos por el ensayo",
        f"  referencia del cliente: {consumo['referencia']}",
        f"  pedido de venta: {consumo['venta']}",
        f"  factura de cliente: {consumo['factura']}",
        f"  PDF que el exportador puede haber generado: {consumo['pdf']}",
    ]


def plan_dry_run(referencia: str, modo: str) -> list:
    pasos = [
        f"1. crear sale.order con client_order_ref {referencia}",
        "2. sale.order.action_confirm",
        "3. sale.advance.payment.inv (delivered) + create_invoices (se tolera 'cannot marshal None')",
        f"4. account.move.write ref = {referencia}",
        "5. account.move.action_post",
        "6. reportar numeros consumidos",
    ]
    limpieza = [
        "7. account.move.button_draft + button_cancel (sin borrar)",
        "8. sale.order.action_cancel (sin borrar)",
    ]
    cierre = ["9. verificar conteos I1- (sin I1-E2E-): " +
              ", ".join(f"{k}={v}" for k, v in CONTEO_BASE.items())]
    if modo == "limpiar":
        return limpieza + cierre
    return pasos + ([] if modo == "solo-crear" else limpieza) + cierre

# ------------------------------------------------- capa de efectos (XML-RPC)


def llamar_tolerando_nulo(ejecutar: Ejecutor, modelo: str, metodo: str, ids: list,
                          contexto: dict = None) -> None:
    """Metodos que devuelven None fallan al empaquetar la respuesta aunque el efecto se aplica.

    Solo se tolera ese fallo; cada llamada va seguida de una verificacion de estado.
    """
    try:
        ejecutar(modelo, metodo, [ids], {"context": contexto or {}})
    except xmlrpc.client.Fault as fallo:
        if not es_respuesta_no_serializable(fallo):
            raise


def exigir_estado(ejecutar: Ejecutor, modelo: str, registro: int, documento: str, esperado: str) -> None:
    errores = errores_de_estado(documento, estado_de(ejecutar, modelo, registro), esperado)
    if errores:
        raise ErrorEnsayo(errores[0])


def contar_i1(ejecutar: Ejecutor) -> dict:
    return {nombre: ejecutar(modelo, "search_count", [dominio], {"context": {"active_test": False}})
            for nombre, (modelo, dominio) in dominios_conteo().items()}


def elegir_datos_base(ejecutar: Ejecutor) -> dict:
    clientes = buscar_ids(ejecutar, "res.partner", [("ref", "=like", gen.REF_CLIENTE + "%")])
    productos = ejecutar("product.product", "search_read",
                         [[("default_code", "=like", gen.COD_PRODUCTO + "%"), ("sale_ok", "=", True)]],
                         {"fields": ["name", "list_price"], "limit": 1})
    if not clientes or not productos:
        raise ErrorEnsayo("No hay cliente o producto I1- para armar la venta")
    return {"cliente": clientes[0], "producto": productos[0],
            "impuesto": resolver_ids_base(ejecutar)["impuesto_venta"]}


def paso_crear_venta(ejecutar: Ejecutor, referencia: str, datos: dict) -> dict:
    valores = valores_venta_e2e(referencia, datos["cliente"], datos["producto"], datos["impuesto"])
    orden = ejecutar("sale.order", "create", [valores])
    nombre = ejecutar("sale.order", "read", [[orden], ["name"]])[0]["name"]
    return {"id": orden, "name": nombre}


def paso_confirmar(ejecutar: Ejecutor, orden: dict) -> None:
    llamar_tolerando_nulo(ejecutar, "sale.order", "action_confirm", [orden["id"]])
    exigir_estado(ejecutar, "sale.order", orden["id"], orden["name"], "sale")


def paso_facturar(ejecutar: Ejecutor, orden: dict) -> int:
    facturar_con_asistente(ejecutar, orden["id"])
    facturas = facturas_de_orden(ejecutar, orden["name"])
    if len(facturas) != 1:
        raise ErrorEnsayo(f"{orden['name']}: se esperaba 1 factura y hay {len(facturas)}")
    return facturas[0]


def paso_escribir_referencia(ejecutar: Ejecutor, factura: int, referencia: str) -> None:
    ejecutar("account.move", "write", [[factura], {"ref": referencia}])


def paso_publicar(ejecutar: Ejecutor, factura: int) -> str:
    llamar_tolerando_nulo(ejecutar, "account.move", "action_post", [factura])
    exigir_estado(ejecutar, "account.move", factura, "factura", "posted")
    return ejecutar("account.move", "read", [[factura], ["name"]])[0]["name"]


def ejecutar_flujo(ejecutar: Ejecutor, referencia: str) -> dict:
    datos = elegir_datos_base(ejecutar)
    orden = paso_crear_venta(ejecutar, referencia, datos)
    informar(f"  venta creada: {orden['name']}")
    paso_confirmar(ejecutar, orden)
    informar("  venta confirmada")
    factura = paso_facturar(ejecutar, orden)
    informar("  factura generada con el asistente")
    paso_escribir_referencia(ejecutar, factura, referencia)
    nombre_factura = paso_publicar(ejecutar, factura)
    informar(f"  factura publicada: {nombre_factura}")
    return {"referencia": referencia, "venta": orden["name"], "factura": nombre_factura,
            "pdf": nombre_pdf_esperado(nombre_factura, referencia)}


def limpiar_factura(ejecutar: Ejecutor, factura: int) -> None:
    for metodo in pasos_limpieza_factura(estado_de(ejecutar, "account.move", factura)):
        llamar_tolerando_nulo(ejecutar, "account.move", metodo, [factura])
    exigir_estado(ejecutar, "account.move", factura, "factura", "cancel")


def limpiar_orden(ejecutar: Ejecutor, orden: dict) -> None:
    facturas = ejecutar("account.move", "search", [[("invoice_origin", "=", orden["name"]),
                                                    ("move_type", "=", "out_invoice")]])
    for factura in facturas:
        limpiar_factura(ejecutar, factura)
    if requiere_cancelar_venta(orden["state"]):
        llamar_tolerando_nulo(ejecutar, "sale.order", "action_cancel", [orden["id"]],
                              CONTEXTO_SIN_ASISTENTE_CANCELACION)
    exigir_estado(ejecutar, "sale.order", orden["id"], orden["name"], "cancel")
    informar(f"  limpiado {orden['name']} ({len(facturas)} factura(s) canceladas, nada borrado)")


def limpiar_residuos(ejecutar: Ejecutor) -> int:
    ordenes = ejecutar("sale.order", "search_read",
                       [[("client_order_ref", "=like", PREFIJO_E2E + "%"), ("state", "!=", "cancel")]],
                       {"fields": ["name", "state"]})
    for orden in ordenes:
        limpiar_orden(ejecutar, orden)
    return len(ordenes)


def verificar_base(ejecutar: Ejecutor) -> list:
    return comparar_conteos(CONTEO_BASE, contar_i1(ejecutar))


def ejecutar_modo(ejecutar: Ejecutor, modo: str) -> int:
    previos = verificar_base(ejecutar)
    if previos and modo != "limpiar":
        informar("La base no esta en el estado inicial; no se crea nada:\n" +
                 "\n".join(" - " + e for e in previos))
        return 3
    if modo != "limpiar":
        informar("Flujo")
        consumo = ejecutar_flujo(ejecutar, referencia_e2e(datetime.now()))
        informar("\n".join(lineas_de_consumo(consumo)))
    if modo != "solo-crear":
        informar("Limpieza")
        informar(f"  documentos de ensayo pendientes encontrados: {limpiar_residuos(ejecutar)}")
    errores = verificar_base(ejecutar)
    informar("Conteos I1- (sin I1-E2E-): " + ", ".join(f"{k}={v}" for k, v in contar_i1(ejecutar).items()))
    if errores:
        informar("DISCREPANCIAS:\n" + "\n".join(" - " + e for e in errores))
        return 1
    if modo == "solo-crear":
        informar("Pendiente: ejecutar --limpiar al terminar de mostrar el PDF y retirar el PDF listado.")
    informar("OK: conteos de la base verificada intactos.")
    return 0


def leer_argumentos(argv: list) -> argparse.Namespace:
    analizador = argparse.ArgumentParser(description="Ensayo de venta a factura con limpieza segura")
    modo = analizador.add_mutually_exclusive_group()
    modo.add_argument("--dry-run", action="store_true", help="imprime el plan sin conectarse")
    modo.add_argument("--solo-crear", action="store_true", help="ejecuta el flujo sin limpiar")
    modo.add_argument("--limpiar", action="store_true", help="cancela los residuos I1-E2E- y verifica")
    return analizador.parse_args(argv)


def modo_de(argumentos: argparse.Namespace) -> str:
    if argumentos.solo_crear:
        return "solo-crear"
    return "limpiar" if argumentos.limpiar else "completo"


def main(argv: list) -> int:
    argumentos = leer_argumentos(argv)
    modo = modo_de(argumentos)
    if argumentos.dry_run:
        informar("\n".join(plan_dry_run(referencia_e2e(datetime.now()), "completo")))
        return 0
    ejecutar = conectar_desde_entorno()
    try:
        return ejecutar_modo(ejecutar, modo)
    except (xmlrpc.client.Fault, ErrorEnsayo) as fallo:
        mensaje = getattr(fallo, "faultString", str(fallo))
        informar("El ensayo se detuvo: " + str(mensaje)[-800:])
        informar("Ejecute --limpiar para cancelar cualquier documento I1-E2E- que haya quedado.")
        return 2


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
