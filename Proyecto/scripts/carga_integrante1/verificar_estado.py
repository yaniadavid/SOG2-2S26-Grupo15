from collections import Counter

from conexion_odoo import conectar_desde_entorno

MODULOS_RELEVANTES = ("sale_management", "purchase", "account", "hr", "stock", "l10n_gt",
                      "dms", "crm", "website", "website_sale", "mass_mailing")


def contar(ejecutar, modelo, dominio):
    return ejecutar(modelo, "search_count", [dominio])


def agrupar(ejecutar, modelo, dominio, campo):
    filas = ejecutar(modelo, "search_read", [dominio], {"fields": [campo]})
    return dict(Counter(str(f[campo]) for f in filas))


def resumen_ventas(ejecutar):
    prefijo_venta = [("client_order_ref", "=like", "I1-V-%")]
    return {
        "ventas I1": contar(ejecutar, "sale.order", prefijo_venta + [("state", "=", "sale")]),
        "cotizaciones I1": contar(ejecutar, "sale.order", [("client_order_ref", "=like", "I1-Q-%")]),
        "ventas I1 por estado de facturacion": agrupar(ejecutar, "sale.order", prefijo_venta, "invoice_status"),
        "ventas totales en la base": contar(ejecutar, "sale.order", [("state", "=", "sale")]),
    }


def resumen_compras_y_facturas(ejecutar):
    return {
        "compras I1": contar(ejecutar, "purchase.order", [("partner_ref", "=like", "I1-OC-%")]),
        "facturas cliente publicadas": contar(ejecutar, "account.move", [("move_type", "=", "out_invoice"), ("state", "=", "posted")]),
        "facturas proveedor publicadas": contar(ejecutar, "account.move", [("move_type", "=", "in_invoice"), ("state", "=", "posted")]),
        "facturas I1 por moneda": agrupar(ejecutar, "account.move", [("ref", "=like", "I1-F%")], "currency_id"),
    }


def resumen_empleados(ejecutar):
    return {
        "empleados activos (todos)": contar(ejecutar, "hr.employee", [("active", "=", True)]),
        "empleados I1": contar(ejecutar, "hr.employee", [("identification_id", "=like", "I1-%")]),
        "cargos": contar(ejecutar, "hr.job", []),
        "departamentos": contar(ejecutar, "hr.department", []),
    }


def resumen_sistema(ejecutar):
    modulos = ejecutar("ir.module.module", "search_read",
                       [[("name", "in", list(MODULOS_RELEVANTES)), ("state", "=", "installed")]],
                       {"fields": ["name"]})
    usuarios = ejecutar("res.users", "search_read", [[("share", "=", False)]], {"fields": ["login", "active"]})
    return {
        "modulos relevantes instalados": sorted(m["name"] for m in modulos),
        "usuarios internos": sorted((u["login"], u["active"]) for u in usuarios),
        "adjuntos de respaldo I1": contar(ejecutar, "ir.attachment", [("name", "=like", "I1-Respaldo-%")]),
        "productos I1 (todos / materiales)": (
            contar(ejecutar, "product.template", [("default_code", "=like", "I1-%")]),
            contar(ejecutar, "product.template", [("default_code", "=like", "I1-MAT-%")]),
        ),
    }


def main():
    ejecutar = conectar_desde_entorno()
    for titulo, resumen in (("VENTAS", resumen_ventas), ("COMPRAS Y FACTURAS", resumen_compras_y_facturas),
                            ("EMPLEADOS", resumen_empleados), ("SISTEMA", resumen_sistema)):
        print(f"## {titulo}")
        for clave, valor in resumen(ejecutar).items():
            print(f"  {clave}: {valor}")


main()
