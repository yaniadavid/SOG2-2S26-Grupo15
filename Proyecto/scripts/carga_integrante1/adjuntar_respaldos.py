"""Crea los ir.attachment de respaldo (PDF generado en memoria) ligados a ordenes de compra.

Uso independiente: python adjuntar_respaldos.py   (requiere variables ODOO_*)
"""
import sys
import xmlrpc.client

import generador_datos as gen
from conexion_odoo import Ejecutor, asegurar, buscar_ids, conectar_desde_entorno, informar


def ids_de_compras(ejecutar: Ejecutor, refs: list) -> dict:
    filas = ejecutar("purchase.order", "search_read", [[("partner_ref", "in", refs)]],
                     {"fields": ["partner_ref"]})
    return {gen.clave_id("compra", f["partner_ref"]): f["id"] for f in filas}


def crear_respaldos(ejecutar: Ejecutor, specs: list, ids: dict) -> int:
    creados = 0
    for spec in specs:
        dominio = [("name", "=", spec["nombre"]), ("res_model", "=", "purchase.order")]
        _, creado = asegurar(ejecutar, "ir.attachment", dominio, gen.valores_respaldo(spec, ids))
        creados += creado
    informar(f"  ir.attachment: {creados} creados, {len(specs) - creados} ya existian")
    return creados


def main() -> int:
    ejecutar = conectar_desde_entorno()
    specs = gen.generar_dataset()["respaldos"]
    try:
        ids = ids_de_compras(ejecutar, [s["compra"] for s in specs])
        faltantes = [s["compra"] for s in specs if gen.clave_id("compra", s["compra"]) not in ids]
        if faltantes:
            informar("Faltan ordenes de compra (ejecute primero cargador_xmlrpc.py): " + ", ".join(faltantes))
            return 1
        crear_respaldos(ejecutar, specs, ids)
    except xmlrpc.client.Fault as fallo:
        informar("Odoo respondio con error: " + str(fallo.faultString)[-800:])
        return 2
    cantidad = len(buscar_ids(ejecutar, "ir.attachment",
                              [("name", "=like", gen.PREFIJO_RESPALDO + "%")]))
    informar(f"Respaldos presentes: {cantidad}")
    return 0 if cantidad == gen.CANTIDADES["respaldos"] else 1


if __name__ == "__main__":
    sys.exit(main())
