"""Carga idempotente por XML-RPC de los datos del Integrante 1.

Variables de entorno: ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASSWORD, ODOO_SSL_NO_VERIFY (opcional).
Uso: python cargador_xmlrpc.py [--dry-run] [--lote 5] [--pausa 1.0]
"""
import argparse
import sys
import xmlrpc.client

import generador_datos as gen
from adjuntar_respaldos import crear_respaldos
from conexion_odoo import Ejecutor, asegurar, buscar_ids, conectar_desde_entorno, informar, pausar

TOLERANCIA_TOTAL = 0.01

DOMINIOS_CONTEO = {
    "clientes": ("res.partner", [("ref", "=like", gen.REF_CLIENTE + "%")]),
    "proveedores": ("res.partner", [("ref", "=like", gen.REF_PROVEEDOR + "%")]),
    "productos": ("product.template", [("default_code", "=like", gen.COD_PRODUCTO + "%")]),
    "materiales": ("product.template", [("default_code", "=like", gen.COD_MATERIAL + "%")]),
    "departamentos": ("hr.department", [("name", "in", list(gen.DEPARTAMENTOS))]),
    "cargos": ("hr.job", [("name", "in", [c[0] for c in gen.CARGOS])]),
    "empleados": ("hr.employee", [("identification_id", "=like", gen.REF_EMPLEADO + "%")]),
    "ventas": ("sale.order", [("client_order_ref", "=like", gen.REF_VENTA + "%"),
                              ("state", "=", "sale")]),
    "cotizaciones": ("sale.order", [("client_order_ref", "=like", gen.REF_COTIZACION + "%"),
                                    ("state", "in", ["draft", "sent"])]),
    "compras": ("purchase.order", [("partner_ref", "=like", gen.REF_COMPRA + "%"),
                                   ("state", "=", "purchase")]),
    "facturas_proveedor": ("account.move", [("ref", "=like", gen.REF_FACTURA_PROVEEDOR + "%"),
                                            ("move_type", "=", "in_invoice"),
                                            ("state", "=", "posted")]),
    "facturas_cliente": ("account.move", [("ref", "=like", gen.REF_FACTURA_CLIENTE + "%"),
                                          ("move_type", "=", "out_invoice"),
                                          ("state", "=", "posted")]),
    "respaldos": ("ir.attachment", [("name", "=like", gen.PREFIJO_RESPALDO + "%"),
                                    ("res_model", "=", "purchase.order")]),
}

# ---------------------------------------------------------------- logica pura


def comparar_conteos(esperados: dict, obtenidos: dict) -> list:
    return [
        f"{nombre}: esperado {esperado}, obtenido {obtenidos.get(nombre)}"
        for nombre, esperado in esperados.items()
        if obtenidos.get(nombre) != esperado
    ]


def comparar_totales(esperados: dict, obtenidos: dict) -> list:
    return [
        f"{ref}: total esperado {esperado:.2f}, en Odoo {obtenidos.get(ref)}"
        for ref, esperado in esperados.items()
        if obtenidos.get(ref) is None or abs(obtenidos[ref] - esperado) > TOLERANCIA_TOTAL
    ]


def totales_esperados(dataset: dict, claves: tuple) -> dict:
    return {doc["ref"]: doc["total_esperado"] for clave in claves for doc in dataset[clave]}


def en_lotes(elementos: list, tamano: int):
    for inicio in range(0, len(elementos), tamano):
        yield elementos[inicio:inicio + tamano]


def resumen_dry_run(dataset: dict) -> list:
    conteos = gen.conteos_dataset(dataset)
    total_ventas = sum(v["total_esperado"] for v in dataset["ventas"])
    total_compras = sum(c["total_esperado"] for c in dataset["compras"])
    return [f"Se crearia {cantidad} x {nombre}" for nombre, cantidad in conteos.items()] + [
        f"Suma total ventas confirmadas (con IVA): Q {total_ventas:,.2f}",
        f"Suma total compras confirmadas (con IVA): Q {total_compras:,.2f}",
    ]

# ------------------------------------------------- capa de efectos (XML-RPC)


def resolver_ids_base(ejecutar: Ejecutor) -> dict:
    def primero(modelo: str, dominio: list) -> int:
        encontrados = buscar_ids(ejecutar, modelo, dominio)
        if not encontrados:
            raise SystemExit(f"No se encontro en Odoo: {modelo} {dominio}")
        return encontrados[0]

    impuesto = [("amount", "=", 12.0), ("amount_type", "=", "percent"), ("name", "=", "12%")]
    return {
        "pais": primero("res.country", [("code", "=", "GT")]),
        "impuesto_venta": primero("account.tax", impuesto + [("type_tax_use", "=", "sale")]),
        "impuesto_compra": primero("account.tax", impuesto + [("type_tax_use", "=", "purchase")]),
        "diario_venta": primero("account.journal", [("code", "=", "INV"), ("type", "=", "sale")]),
        "diario_compra": primero("account.journal", [("code", "=", "BILL"), ("type", "=", "purchase")]),
    }


def cargar_simples(ejecutar: Ejecutor, modelo: str, specs: list, ids: dict, parametros: dict,
                   clase_id: str, clave_de, dominio_de, valores_de) -> dict:
    """Crea (si falta) cada spec en lotes y devuelve {clase:clave -> id}."""
    nuevos, creados = {}, 0
    for lote in en_lotes(specs, parametros["lote"]):
        for spec in lote:
            registro, creado = asegurar(ejecutar, modelo, dominio_de(spec), valores_de(spec, ids))
            nuevos[gen.clave_id(clase_id, clave_de(spec))] = registro
            creados += creado
        pausar(parametros["pausa"])
    informar(f"  {modelo}: {creados} creados, {len(specs) - creados} ya existian")
    return nuevos


def ids_de_productos(ejecutar: Ejecutor) -> dict:
    filas = ejecutar("product.product", "search_read", [[("default_code", "=like", gen.PREFIJO + "%")]],
                     {"fields": ["default_code"], "context": {"active_test": False}})
    return {gen.clave_id("producto", f["default_code"]): f["id"] for f in filas}


def estado_de(ejecutar: Ejecutor, modelo: str, registro: int) -> str:
    return ejecutar(modelo, "read", [[registro], ["state"]])[0]["state"]


def ids_lineas_compra(ejecutar: Ejecutor, ref: str, orden: int) -> dict:
    lineas = ejecutar("purchase.order.line", "search", [[("order_id", "=", orden)]],
                      {"order": "sequence, id"})
    return {gen.clave_id("linea_compra", f"{ref}:{i}"): l for i, l in enumerate(lineas)}


def cargar_orden(ejecutar: Ejecutor, modelo: str, campo_ref: str, metodo_confirmar: str,
                 spec: dict, valores: dict, confirmar: bool) -> tuple:
    """Crea la orden si falta, la confirma y restituye date_order. Devuelve (id, creada)."""
    orden, creada = asegurar(ejecutar, modelo, [(campo_ref, "=", spec["ref"])], valores)
    if confirmar and estado_de(ejecutar, modelo, orden) in ("draft", "sent"):
        ejecutar(modelo, metodo_confirmar, [[orden]])
        ejecutar(modelo, "write", [[orden], {"date_order": spec["fecha"]}])
    return orden, creada


def marcar_cotizacion_enviada(ejecutar: Ejecutor, orden: int) -> None:
    try:
        ejecutar("sale.order", "action_quotation_sent", [[orden]])
    except xmlrpc.client.Fault:
        informar("  aviso: no se pudo marcar una cotizacion como enviada; queda en borrador")


def cargar_ventas(ejecutar: Ejecutor, specs: list, ids: dict, parametros: dict,
                  confirmar: bool) -> dict:
    creadas = 0
    for lote in en_lotes(specs, parametros["lote"]):
        for spec in lote:
            orden, creada = cargar_orden(ejecutar, "sale.order", "client_order_ref", "action_confirm",
                                         spec, gen.valores_venta(spec, ids), confirmar)
            if spec.get("enviada") and estado_de(ejecutar, "sale.order", orden) == "draft":
                marcar_cotizacion_enviada(ejecutar, orden)
            creadas += creada
        pausar(parametros["pausa"])
    informar(f"  sale.order ({'confirmadas' if confirmar else 'cotizaciones'}): "
             f"{creadas} creadas, {len(specs) - creadas} ya existian")
    return {}


def cargar_compras(ejecutar: Ejecutor, specs: list, ids: dict, parametros: dict) -> dict:
    nuevos, creadas = {}, 0
    for lote in en_lotes(specs, parametros["lote"]):
        for spec in lote:
            orden, creada = cargar_orden(ejecutar, "purchase.order", "partner_ref", "button_confirm",
                                         spec, gen.valores_compra(spec, ids), True)
            nuevos[gen.clave_id("compra", spec["ref"])] = orden
            nuevos.update(ids_lineas_compra(ejecutar, spec["ref"], orden))
            creadas += creada
        pausar(parametros["pausa"])
    informar(f"  purchase.order (confirmadas): {creadas} creadas, {len(specs) - creadas} ya existian")
    return nuevos


def cargar_facturas(ejecutar: Ejecutor, specs: list, ids: dict, parametros: dict,
                    tipo: str, fabricar_valores, contexto: dict) -> None:
    creadas = 0
    for lote in en_lotes(specs, parametros["lote"]):
        for spec in lote:
            factura, creada = asegurar(
                ejecutar, "account.move", [("ref", "=", spec["ref"]), ("move_type", "=", tipo)],
                fabricar_valores(spec, ids), contexto)
            if estado_de(ejecutar, "account.move", factura) == "draft":
                ejecutar("account.move", "action_post", [[factura]])
            creadas += creada
        pausar(parametros["pausa"])
    informar(f"  account.move {tipo} (publicadas): {creadas} creadas, {len(specs) - creadas} ya existian")


def contexto_asistente(orden: int) -> dict:
    return {"active_model": "sale.order", "active_ids": [orden], "active_id": orden}


def facturas_de_orden(ejecutar: Ejecutor, nombre_orden: str) -> list:
    return buscar_ids(ejecutar, "account.move",
                      [("invoice_origin", "=", nombre_orden), ("move_type", "=", "out_invoice")])


ERROR_RESPUESTA_NO_SERIALIZABLE = "cannot marshal None"


def es_respuesta_no_serializable(fallo: xmlrpc.client.Fault) -> bool:
    return ERROR_RESPUESTA_NO_SERIALIZABLE in str(fallo.faultString)


def facturar_con_asistente(ejecutar: Ejecutor, orden: int) -> None:
    """Flujo estandar de Odoo 18: sale.advance.payment.inv + create_invoices.

    create_invoices crea y confirma la factura antes de armar su respuesta; esa
    respuesta incluye valores nulos que XML-RPC no admite, por lo que el servidor
    la rechaza aunque el efecto ya se haya aplicado. Solo ese fallo se tolera.
    """
    contexto = {"context": contexto_asistente(orden)}
    asistente = ejecutar("sale.advance.payment.inv", "create",
                         [{"advance_payment_method": "delivered"}], contexto)
    try:
        ejecutar("sale.advance.payment.inv", "create_invoices", [[asistente]], contexto)
    except xmlrpc.client.Fault as fallo:
        if not es_respuesta_no_serializable(fallo):
            raise


def cargar_facturas_cliente(ejecutar: Ejecutor, specs: list, parametros: dict) -> None:
    creadas = 0
    for lote in en_lotes(specs, parametros["lote"]):
        for spec in lote:
            orden = ejecutar("sale.order", "search_read", [[("client_order_ref", "=", spec["venta"])]],
                             {"fields": ["name"], "limit": 1})[0]
            facturas = facturas_de_orden(ejecutar, orden["name"])
            if not facturas:
                facturar_con_asistente(ejecutar, orden["id"])
                facturas = facturas_de_orden(ejecutar, orden["name"])
                if not facturas:
                    raise SystemExit(f"El asistente no genero factura para la orden {orden['name']}")
                creadas += 1
            factura = facturas[0]
            if estado_de(ejecutar, "account.move", factura) == "draft":
                ejecutar("account.move", "write",
                         [[factura], {"ref": spec["ref"], "invoice_date": spec["fecha"]}])
                ejecutar("account.move", "action_post", [[factura]])
        pausar(parametros["pausa"])
    informar(f"  account.move out_invoice (desde asistente, publicadas): "
             f"{creadas} creadas, {len(specs) - creadas} ya existian")


def totales_en_odoo(ejecutar: Ejecutor, modelo: str, campo_ref: str, refs: list, extra: list) -> dict:
    filas = ejecutar(modelo, "search_read", [[(campo_ref, "in", refs)] + extra],
                     {"fields": [campo_ref, "amount_total"]})
    return {f[campo_ref]: f["amount_total"] for f in filas}


def verificar_totales(ejecutar: Ejecutor, dataset: dict) -> list:
    consultas = (
        ("sale.order", "client_order_ref", ("ventas", "cotizaciones"), []),
        ("purchase.order", "partner_ref", ("compras",), []),
        ("account.move", "ref", ("facturas_proveedor",), [("move_type", "=", "in_invoice")]),
        ("account.move", "ref", ("facturas_cliente",), [("move_type", "=", "out_invoice")]),
    )
    discrepancias = []
    for modelo, campo, claves, extra in consultas:
        esperados = totales_esperados(dataset, claves)
        obtenidos = totales_en_odoo(ejecutar, modelo, campo, list(esperados), extra)
        discrepancias += comparar_totales(esperados, obtenidos)
    return discrepancias


def contar_final(ejecutar: Ejecutor) -> dict:
    return {
        nombre: ejecutar(modelo, "search_count", [dominio], {"context": {"active_test": False}})
        for nombre, (modelo, dominio) in DOMINIOS_CONTEO.items()
    }


def ejecutar_carga(ejecutar: Ejecutor, dataset: dict, parametros: dict) -> dict:
    """Orquesta el orden correcto: maestros, ventas, compras, facturas, respaldos."""
    ids = resolver_ids_base(ejecutar)
    informar("Datos maestros")
    ids |= cargar_simples(ejecutar, "hr.department", dataset["departamentos"], ids, parametros,
                          "departamento", lambda s: s, lambda s: [("name", "=", s)],
                          lambda s, _: gen.valores_departamento(s))
    ids |= cargar_simples(ejecutar, "hr.job", dataset["cargos"], ids, parametros, "cargo",
                          lambda s: s["nombre"], lambda s: [("name", "=", s["nombre"])],
                          gen.valores_cargo)
    ids |= cargar_simples(ejecutar, "hr.employee", dataset["empleados"], ids, parametros, "empleado",
                          lambda s: s["identificacion"],
                          lambda s: [("identification_id", "=", s["identificacion"])],
                          gen.valores_empleado)
    for clave, es_cliente in (("clientes", True), ("proveedores", False)):
        ids |= cargar_simples(ejecutar, "res.partner", dataset[clave], ids, parametros, "socio",
                              lambda s: s["ref"], lambda s: [("ref", "=", s["ref"])],
                              lambda s, i, c=es_cliente: gen.valores_socio(s, i, c))
    for clave in ("productos", "materiales"):
        cargar_simples(ejecutar, "product.template", dataset[clave], ids, parametros, "plantilla",
                       lambda s: s["codigo"], lambda s: [("default_code", "=", s["codigo"])],
                       gen.valores_producto)
    ids |= ids_de_productos(ejecutar)
    informar("Ventas y cotizaciones")
    cargar_ventas(ejecutar, dataset["ventas"], ids, parametros, True)
    cargar_ventas(ejecutar, dataset["cotizaciones"], ids, parametros, False)
    informar("Compras")
    ids |= cargar_compras(ejecutar, dataset["compras"], ids, parametros)
    informar("Facturas")
    cargar_facturas(ejecutar, dataset["facturas_proveedor"], ids, parametros, "in_invoice",
                    gen.valores_factura_proveedor, gen.CONTEXTO_FACTURA_PROVEEDOR)
    cargar_facturas_cliente(ejecutar, dataset["facturas_cliente"], parametros)
    informar("Respaldos")
    crear_respaldos(ejecutar, dataset["respaldos"], ids)
    return ids


def leer_argumentos(argv: list) -> argparse.Namespace:
    analizador = argparse.ArgumentParser(description="Carga de datos del Integrante 1 en Odoo")
    analizador.add_argument("--dry-run", action="store_true", help="solo imprime lo que se crearia")
    analizador.add_argument("--lote", type=int, default=5, help="registros por lote")
    analizador.add_argument("--pausa", type=float, default=1.0, help="segundos entre lotes")
    return analizador.parse_args(argv)


def main(argv: list) -> int:
    argumentos = leer_argumentos(argv)
    dataset = gen.generar_dataset()
    if argumentos.dry_run:
        informar("\n".join(resumen_dry_run(dataset)))
        return 0
    ejecutar = conectar_desde_entorno()
    try:
        ejecutar_carga(ejecutar, dataset, {"lote": argumentos.lote, "pausa": argumentos.pausa})
        obtenidos = contar_final(ejecutar)
        errores = comparar_conteos(gen.conteos_dataset(dataset), obtenidos)
        errores += verificar_totales(ejecutar, dataset)
    except xmlrpc.client.Fault as fallo:
        informar("Odoo respondio con error: " + str(fallo.faultString)[-800:])
        return 2
    informar("Resumen final (esperado = obtenido)")
    esperados = gen.conteos_dataset(dataset)
    for nombre, valor in obtenidos.items():
        informar(f"  {nombre}: {valor} / {esperados[nombre]}")
    if errores:
        informar("DISCREPANCIAS:\n" + "\n".join(" - " + e for e in errores))
        return 1
    informar("OK: conteos y totales coinciden.")
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
