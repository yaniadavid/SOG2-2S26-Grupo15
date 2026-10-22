"""Generador puro de datos ficticios de QuetzalMart (Integrante 1). No toca la red."""
import base64
import random
import unicodedata
from datetime import date, datetime, timedelta
from decimal import ROUND_HALF_UP, Decimal

SEMILLA = 20260615
PREFIJO = "I1-"
TASA_IVA = Decimal("0.12")

REF_CLIENTE = PREFIJO + "C-"
REF_PROVEEDOR = PREFIJO + "P-"
COD_PRODUCTO = PREFIJO + "PV-"
COD_MATERIAL = PREFIJO + "MAT-"
REF_EMPLEADO = PREFIJO + "E-"
REF_VENTA = PREFIJO + "V-"
REF_COTIZACION = PREFIJO + "Q-"
REF_COMPRA = PREFIJO + "OC-"
REF_FACTURA_PROVEEDOR = PREFIJO + "FP-"
REF_FACTURA_CLIENTE = PREFIJO + "FC-"
PREFIJO_RESPALDO = PREFIJO + "Respaldo-"

CANTIDADES = {
    "ventas": 50, "cotizaciones": 7, "empleados": 12, "cargos": 2, "departamentos": 2,
    "materiales": 20, "compras": 33, "facturas_proveedor": 33, "facturas_cliente": 17,
    "respaldos": 5,
}

CONTEXTO_FACTURA_PROVEEDOR = {"default_move_type": "in_invoice"}

DEPARTAMENTOS = ("Operaciones de Tienda", "Administracion y Compras")
CARGOS = (
    ("Cajero de Sucursal", "Operaciones de Tienda"),
    ("Analista de Compras", "Administracion y Compras"),
)

NOMBRES_HOMBRE = ("Jose", "Luis", "Carlos", "Marvin", "Oscar", "Edwin", "Byron", "Selvin",
                  "Mario", "Hugo", "Erick", "Julio", "Rolando", "Wilfredo", "Estuardo")
NOMBRES_MUJER = ("Maria", "Ana", "Lucia", "Karla", "Sandra", "Brenda", "Rosa", "Claudia",
                 "Silvia", "Mayra", "Gabriela", "Andrea", "Heidy", "Ingrid", "Wendy")
APELLIDOS = ("Lopez", "Garcia", "Perez", "Morales", "Hernandez", "Gonzalez", "Ramirez",
             "Castillo", "Cifuentes", "Mendez", "Barrios", "Velasquez", "Chavez", "Orozco",
             "Aguilar", "Monzon", "Pineda", "Santizo", "Giron", "Arriaza", "Cabrera",
             "Estrada", "Tzoc", "Xicay", "Alvarado", "Marroquin")

EMPRESAS_CLIENTE = (
    "Restaurante El Fogon Chapin", "Hotel Casa Santo Domingo Express", "Comedor Dona Mercedes",
    "Cafeteria La Antigua", "Colegio Mixto San Jose", "Tienda La Bendicion",
    "Panaderia El Trigal", "Clinica Santa Lucia",
)
EMPRESAS_PROVEEDOR = (
    "Distribuidora La Ceiba, S.A.", "Alimentos del Altiplano, S.A.", "Lacteos Santa Clara, S.A.",
    "Comercial Los Volcanes, S.A.", "Bebidas Atitlan, S.A.", "Granos y Abarrotes Pacifico, S.A.",
    "Carnes Selectas del Norte, S.A.", "Empaques y Plasticos Centroamericanos, S.A.",
    "Suministros de Oficina Zona 4, S.A.", "Higiene y Limpieza Quetzal, S.A.",
    "Frutas y Verduras Palencia, S.A.", "Importadora Mayab, S.A.",
)
CIUDADES = ("Guatemala", "Mixco", "Villa Nueva", "Antigua Guatemala", "Quetzaltenango",
            "Escuintla", "Chinautla", "San Miguel Petapa")
CALLES = ("Avenida Reforma", "5a Avenida", "12 Calle", "Calzada Roosevelt", "7a Avenida",
          "Boulevard Los Proceres", "3a Calle", "Diagonal 6")

PRODUCTOS_VENTA = (
    ("Arroz blanco 5 lb", 28.50), ("Frijol negro 2 lb", 17.75), ("Azucar blanca 5 lb", 26.00),
    ("Aceite vegetal 900 ml", 22.90), ("Harina de trigo 2 lb", 12.50), ("Sal yodada 1 kg", 5.25),
    ("Cafe molido 400 g", 38.00), ("Leche entera 1 L", 11.75), ("Queso fresco 1 lb", 24.50),
    ("Crema 250 ml", 9.90), ("Huevos blancos cartera 30 u", 46.00), ("Pan de caja 600 g", 19.75),
    ("Tortillas empacadas 1 lb", 6.50), ("Pollo entero fresco 1 lb", 14.25),
    ("Carne molida de res 1 lb", 36.00), ("Chuleta de cerdo 1 lb", 29.50),
    ("Jamon de pavo 1 lb", 32.00), ("Salchicha tipo viena 12 u", 21.50),
    ("Tomate 1 lb", 4.50), ("Cebolla blanca 1 lb", 3.75), ("Papa 1 lb", 4.25),
    ("Banano 1 lb", 2.75), ("Manzana roja 1 lb", 12.00), ("Limon 1 lb", 5.00),
    ("Gaseosa cola 2.5 L", 17.50), ("Agua pura 20 L", 21.00), ("Jugo de naranja 1 L", 13.25),
    ("Cerveza nacional lata 355 ml", 8.50), ("Galletas de soda 6 u", 7.75),
    ("Cereal de maiz 500 g", 31.00), ("Pasta espagueti 500 g", 8.25),
    ("Salsa de tomate 400 g", 10.50), ("Mayonesa 400 g", 18.75), ("Atun en lata 140 g", 13.00),
    ("Detergente en polvo 1 kg", 24.00), ("Jabon de bano 3 u", 14.50),
    ("Papel higienico 12 rollos", 42.00), ("Shampoo 400 ml", 33.50),
    ("Pasta dental 100 ml", 16.25), ("Servilletas 500 u", 11.00),
)
MATERIALES = (
    ("Bolsa plastica camiseta mediana (paquete)", 18.00),
    ("Bolsa plastica camiseta grande (paquete)", 24.00),
    ("Bolsa de papel kraft (paquete 100 u)", 55.00), ("Caja de carton mediana", 6.50),
    ("Rollo de papel termico para caja registradora", 9.75),
    ("Etiquetas de precio adhesivas (rollo)", 14.00), ("Cinta adhesiva de embalaje", 7.25),
    ("Guantes desechables (caja 100 u)", 48.00), ("Cofia desechable (paquete 100 u)", 32.00),
    ("Desinfectante de pisos 4 L", 36.00), ("Trapeador industrial", 28.00),
    ("Escoba plastica", 19.50), ("Papel film de cocina 300 m", 62.00),
    ("Bandeja de duroport para carne (paquete)", 27.50), ("Marcador permanente negro", 5.50),
    ("Carretilla de carga manual", 385.00), ("Canasta plastica de compras", 45.00),
    ("Uniforme de sucursal (camisa polo)", 85.00), ("Calculadora de escritorio", 39.00),
    ("Resma de papel bond carta", 44.00),
)

INICIO_PERIODO = date(2026, 1, 5)
FIN_PERIODO = date(2026, 9, 30)
FORMATO_FECHA_HORA = "%Y-%m-%d %H:%M:%S"


def redondear(valor) -> Decimal:
    return Decimal(valor).quantize(Decimal("0.01"), rounding=ROUND_HALF_UP)


def totales_documento(lineas: list) -> dict:
    """IVA 12 % incluido en el precio (impuesto 'tax_included' de l10n_gt), desglosado por linea."""
    subtotal = iva = Decimal("0")
    for linea in lineas:
        bruto = redondear(Decimal(str(linea["cantidad"])) * Decimal(str(linea["precio"])))
        neto = redondear(bruto / (1 + TASA_IVA))
        subtotal += neto
        iva += bruto - neto
    return {"subtotal": float(subtotal), "iva": float(iva), "total": float(subtotal + iva)}


def sin_acentos(texto: str) -> str:
    return unicodedata.normalize("NFKD", texto).encode("ascii", "ignore").decode()


def correlativo(prefijo: str, numero: int) -> str:
    return f"{prefijo}{numero:03d}"


def telefono(rng: random.Random) -> str:
    return f"+502 {rng.choice((2, 4, 5))}{rng.randint(100, 999)}-{rng.randint(1000, 9999)}"


def nit(rng: random.Random) -> str:
    return f"{rng.randint(1000000, 9999999)}-{rng.choice('123456789K')}"


def direccion(rng: random.Random) -> dict:
    return {
        "street": f"{rng.choice(CALLES)} {rng.randint(1, 30)}-{rng.randint(1, 99)} Zona {rng.randint(1, 18)}",
        "city": rng.choice(CIUDADES),
    }


def correo(nombre: str, dominio: str) -> str:
    base = sin_acentos(nombre).lower().replace(",", "").replace(".", "")
    return ".".join(base.split()[:2]) + "@" + dominio


def generar_clientes(rng: random.Random) -> list:
    personas = []
    while len(personas) < 17:
        nombre = f"{rng.choice(NOMBRES_HOMBRE + NOMBRES_MUJER)} {rng.choice(APELLIDOS)} {rng.choice(APELLIDOS)}"
        if nombre not in personas:
            personas.append(nombre)
    nombres = [(n, True) for n in EMPRESAS_CLIENTE] + [(n, False) for n in personas]
    clientes = []
    for numero, (nombre, es_empresa) in enumerate(nombres, start=1):
        dominio = sin_acentos(nombre).lower().split()[0] + ".com.gt" if es_empresa else "correo.gt"
        clientes.append({
            "ref": correlativo(REF_CLIENTE, numero), "nombre": nombre, "es_empresa": es_empresa,
            "nit": nit(rng), "correo": correo(nombre, dominio), "telefono": telefono(rng),
            **direccion(rng),
        })
    return clientes


def generar_proveedores(rng: random.Random) -> list:
    return [
        {
            "ref": correlativo(REF_PROVEEDOR, numero), "nombre": nombre, "es_empresa": True,
            "nit": nit(rng),
            "correo": "ventas@" + sin_acentos(nombre).lower().split()[0] + ".com.gt",
            "telefono": telefono(rng), **direccion(rng),
        }
        for numero, nombre in enumerate(EMPRESAS_PROVEEDOR, start=1)
    ]


def precio_compra_estimado(rng: random.Random, precio: float) -> float:
    return float(redondear(Decimal(str(precio)) * Decimal(str(rng.uniform(0.68, 0.82)))))


def generar_catalogo(rng: random.Random, prefijo: str, items: tuple, es_vendible: bool) -> list:
    return [
        {
            "codigo": correlativo(prefijo, numero), "nombre": nombre,
            "precio_venta": precio if es_vendible else 0.0,
            "precio_compra": precio_compra_estimado(rng, precio) if es_vendible else precio,
            "es_vendible": es_vendible,
        }
        for numero, (nombre, precio) in enumerate(items, start=1)
    ]


def generar_empleado(rng: random.Random, numero: int, usados: set) -> dict:
    genero = rng.choice(("male", "female"))
    nombre = rng.choice(NOMBRES_HOMBRE if genero == "male" else NOMBRES_MUJER)
    nombre_completo = f"{nombre} {rng.choice(APELLIDOS)} {rng.choice(APELLIDOS)}"
    if nombre_completo in usados:
        nombre_completo += f" {numero}"
    cargo, departamento = CARGOS[numero % len(CARGOS)]
    return {
        "identificacion": correlativo(REF_EMPLEADO, numero), "nombre": nombre_completo,
        "genero": genero, "cargo": cargo, "departamento": departamento,
        "correo_trabajo": correo(nombre_completo, "quetzalmart.gt"),
        "telefono": telefono(rng),
        "nacimiento": date(rng.randint(1980, 2004), rng.randint(1, 12), rng.randint(1, 28)).isoformat(),
    }


def generar_empleados(rng: random.Random) -> list:
    empleados = []
    for numero in range(1, CANTIDADES["empleados"] + 1):
        empleados.append(generar_empleado(rng, numero, {e["nombre"] for e in empleados}))
    return empleados


def fechas_ordenadas(rng: random.Random, cantidad: int) -> list:
    dias = (FIN_PERIODO - INICIO_PERIODO).days
    return sorted(
        datetime.combine(INICIO_PERIODO + timedelta(days=rng.randint(0, dias)), datetime.min.time())
        + timedelta(hours=rng.randint(8, 18), minutes=rng.randint(0, 59))
        for _ in range(cantidad)
    )


def generar_lineas(rng: random.Random, catalogo: list, minimo: int, maximo: int,
                   cantidad_max: int, campo_precio: str) -> list:
    elegidos = rng.sample(catalogo, rng.randint(minimo, maximo))
    return [
        {
            "producto": item["codigo"], "descripcion": item["nombre"],
            "cantidad": float(rng.randint(1, cantidad_max)), "precio": item[campo_precio],
        }
        for item in elegidos
    ]


def con_total(documento: dict) -> dict:
    return {**documento, "total_esperado": totales_documento(documento["lineas"])["total"]}


def generar_ventas(rng: random.Random, clientes: list, productos: list) -> list:
    return [
        con_total({
            "ref": correlativo(REF_VENTA, numero), "cliente": rng.choice(clientes)["ref"],
            "fecha": fecha.strftime(FORMATO_FECHA_HORA),
            "lineas": generar_lineas(rng, productos, 2, 6, 40, "precio_venta"),
        })
        for numero, fecha in enumerate(fechas_ordenadas(rng, CANTIDADES["ventas"]), start=1)
    ]


def generar_cotizaciones(rng: random.Random, clientes: list, productos: list) -> list:
    return [
        con_total({
            "ref": correlativo(REF_COTIZACION, numero), "cliente": rng.choice(clientes)["ref"],
            "fecha": fecha.strftime(FORMATO_FECHA_HORA),
            "vigencia": (fecha.date() + timedelta(days=30)).isoformat(),
            "enviada": numero > 5,
            "lineas": generar_lineas(rng, productos, 2, 5, 20, "precio_venta"),
        })
        for numero, fecha in enumerate(fechas_ordenadas(rng, CANTIDADES["cotizaciones"]), start=1)
    ]


def generar_compras(rng: random.Random, proveedores: list, catalogo: list) -> list:
    return [
        con_total({
            "ref": correlativo(REF_COMPRA, numero), "proveedor": rng.choice(proveedores)["ref"],
            "fecha": fecha.strftime(FORMATO_FECHA_HORA),
            "lineas": generar_lineas(rng, catalogo, 2, 5, 60, "precio_compra"),
        })
        for numero, fecha in enumerate(fechas_ordenadas(rng, CANTIDADES["compras"]), start=1)
    ]


def fecha_de(texto_fecha_hora: str) -> date:
    return datetime.strptime(texto_fecha_hora, FORMATO_FECHA_HORA).date()


def generar_facturas_proveedor(rng: random.Random, compras: list) -> list:
    return [
        {
            "ref": correlativo(REF_FACTURA_PROVEEDOR, numero), "compra": compra["ref"],
            "proveedor": compra["proveedor"],
            "fecha": (fecha_de(compra["fecha"]) + timedelta(days=rng.randint(2, 9))).isoformat(),
            "lineas": compra["lineas"], "total_esperado": compra["total_esperado"],
        }
        for numero, compra in enumerate(compras, start=1)
    ]


def generar_facturas_cliente(ventas: list) -> list:
    return [
        {
            "ref": correlativo(REF_FACTURA_CLIENTE, numero), "venta": venta["ref"],
            "fecha": fecha_de(venta["fecha"]).isoformat(),
            "total_esperado": venta["total_esperado"],
        }
        for numero, venta in enumerate(ventas[:CANTIDADES["facturas_cliente"]], start=1)
    ]


def texto_respaldo(compra: dict) -> list:
    detalle = [
        f"{l['descripcion']} x {l['cantidad']:.0f} a Q {l['precio']:.2f}" for l in compra["lineas"]
    ]
    return [
        "QuetzalMart - Respaldo de orden de compra",
        f"Orden: {compra['ref']}  Fecha: {compra['fecha'][:10]}",
        f"Proveedor: {compra['proveedor']}",
        *detalle,
        f"Total con IVA: Q {compra['total_esperado']:.2f}",
    ]


def generar_respaldos(compras: list) -> list:
    return [
        {
            "nombre": f"{PREFIJO_RESPALDO}{numero:03d}.pdf", "compra": compra["ref"],
            "lineas_texto": texto_respaldo(compra),
        }
        for numero, compra in enumerate(compras[:CANTIDADES["respaldos"]], start=1)
    ]


def generar_dataset(semilla: int = SEMILLA) -> dict:
    rng = random.Random(semilla)
    clientes = generar_clientes(rng)
    proveedores = generar_proveedores(rng)
    productos = generar_catalogo(rng, COD_PRODUCTO, PRODUCTOS_VENTA, True)
    materiales = generar_catalogo(rng, COD_MATERIAL, MATERIALES, False)
    compras = generar_compras(rng, proveedores, productos + materiales)
    ventas = generar_ventas(rng, clientes, productos)
    return {
        "clientes": clientes, "proveedores": proveedores, "productos": productos,
        "materiales": materiales, "departamentos": list(DEPARTAMENTOS),
        "cargos": [{"nombre": n, "departamento": d} for n, d in CARGOS],
        "empleados": generar_empleados(rng), "ventas": ventas,
        "cotizaciones": generar_cotizaciones(rng, clientes, productos),
        "compras": compras,
        "facturas_proveedor": generar_facturas_proveedor(rng, compras),
        "facturas_cliente": generar_facturas_cliente(ventas),
        "respaldos": generar_respaldos(compras),
    }


def conteos_dataset(dataset: dict) -> dict:
    return {clave: len(valor) for clave, valor in dataset.items()}


def clave_id(clase: str, clave: str) -> str:
    return f"{clase}:{clave}"


def impuestos_venta(ids: dict) -> list:
    return [(6, 0, [ids["impuesto_venta"]])]


def impuestos_compra(ids: dict) -> list:
    return [(6, 0, [ids["impuesto_compra"]])]


def valores_socio(spec: dict, ids: dict, es_cliente: bool) -> dict:
    return {
        "name": spec["nombre"], "ref": spec["ref"], "vat": spec["nit"],
        "email": spec["correo"], "phone": spec["telefono"], "street": spec["street"],
        "city": spec["city"], "country_id": ids["pais"], "is_company": spec["es_empresa"],
        "customer_rank": 1 if es_cliente else 0, "supplier_rank": 0 if es_cliente else 1,
    }


def valores_producto(spec: dict, ids: dict) -> dict:
    return {
        "name": spec["nombre"], "default_code": spec["codigo"], "type": "consu",
        "is_storable": True, "list_price": spec["precio_venta"],
        "sale_ok": spec["es_vendible"], "purchase_ok": True,
        "taxes_id": impuestos_venta(ids), "supplier_taxes_id": impuestos_compra(ids),
    }


def valores_departamento(nombre: str) -> dict:
    return {"name": nombre}


def valores_cargo(spec: dict, ids: dict) -> dict:
    return {"name": spec["nombre"], "department_id": ids[clave_id("departamento", spec["departamento"])]}


def valores_empleado(spec: dict, ids: dict) -> dict:
    return {
        "name": spec["nombre"], "identification_id": spec["identificacion"],
        "gender": spec["genero"], "job_id": ids[clave_id("cargo", spec["cargo"])],
        "job_title": spec["cargo"],
        "department_id": ids[clave_id("departamento", spec["departamento"])],
        "work_email": spec["correo_trabajo"], "work_phone": spec["telefono"],
        "birthday": spec["nacimiento"],
    }


def linea_orden_venta(linea: dict, ids: dict) -> tuple:
    return (0, 0, {
        "product_id": ids[clave_id("producto", linea["producto"])], "name": linea["descripcion"],
        "product_uom_qty": linea["cantidad"], "price_unit": linea["precio"],
        "tax_id": impuestos_venta(ids),
    })


def valores_venta(spec: dict, ids: dict) -> dict:
    valores = {
        "partner_id": ids[clave_id("socio", spec["cliente"])], "date_order": spec["fecha"],
        "client_order_ref": spec["ref"],
        "order_line": [linea_orden_venta(l, ids) for l in spec["lineas"]],
    }
    if "vigencia" in spec:
        valores["validity_date"] = spec["vigencia"]
    return valores


def linea_orden_compra(linea: dict, ids: dict) -> tuple:
    return (0, 0, {
        "product_id": ids[clave_id("producto", linea["producto"])], "name": linea["descripcion"],
        "product_qty": linea["cantidad"], "price_unit": linea["precio"],
        "taxes_id": impuestos_compra(ids),
    })


def valores_compra(spec: dict, ids: dict) -> dict:
    return {
        "partner_id": ids[clave_id("socio", spec["proveedor"])], "date_order": spec["fecha"],
        "partner_ref": spec["ref"],
        "order_line": [linea_orden_compra(l, ids) for l in spec["lineas"]],
    }


def linea_factura_proveedor(compra: str, indice: int, linea: dict, ids: dict) -> tuple:
    return (0, 0, {
        "product_id": ids[clave_id("producto", linea["producto"])], "name": linea["descripcion"],
        "quantity": linea["cantidad"], "price_unit": linea["precio"],
        "tax_ids": impuestos_compra(ids),
        "purchase_line_id": ids[clave_id("linea_compra", f"{compra}:{indice}")],
    })


def valores_factura_proveedor(spec: dict, ids: dict) -> dict:
    return {
        "partner_id": ids[clave_id("socio", spec["proveedor"])], "ref": spec["ref"],
        "invoice_date": spec["fecha"], "date": spec["fecha"],
        "journal_id": ids["diario_compra"],
        "invoice_line_ids": [
            linea_factura_proveedor(spec["compra"], i, l, ids) for i, l in enumerate(spec["lineas"])
        ],
    }


def construir_pdf_simple(lineas: list) -> bytes:
    """PDF de una pagina con texto (Helvetica) generado en memoria."""
    def escapar(texto: str) -> str:
        return sin_acentos(texto).replace("\\", "\\\\").replace("(", "\\(").replace(")", "\\)")

    flujo = "BT /F1 11 Tf 50 780 Td 16 TL\n" + "".join(
        f"({escapar(l)}) Tj T*\n" for l in lineas) + "ET"
    cuerpo = flujo.encode("latin-1")
    objetos = [
        b"<< /Type /Catalog /Pages 2 0 R >>",
        b"<< /Type /Pages /Kids [3 0 R] /Count 1 >>",
        b"<< /Type /Page /Parent 2 0 R /MediaBox [0 0 612 842] /Contents 4 0 R "
        b"/Resources << /Font << /F1 5 0 R >> >> >>",
        b"<< /Length " + str(len(cuerpo)).encode() + b" >>\nstream\n" + cuerpo + b"\nendstream",
        b"<< /Type /Font /Subtype /Type1 /BaseFont /Helvetica >>",
    ]
    salida = b"%PDF-1.4\n"
    posiciones = []
    for numero, objeto in enumerate(objetos, start=1):
        posiciones.append(len(salida))
        salida += f"{numero} 0 obj\n".encode() + objeto + b"\nendobj\n"
    inicio_xref = len(salida)
    salida += f"xref\n0 {len(objetos) + 1}\n0000000000 65535 f \n".encode()
    salida += b"".join(f"{p:010d} 00000 n \n".encode() for p in posiciones)
    salida += (f"trailer\n<< /Size {len(objetos) + 1} /Root 1 0 R >>\n"
               f"startxref\n{inicio_xref}\n%%EOF\n").encode()
    return salida


def valores_respaldo(spec: dict, ids: dict) -> dict:
    contenido = construir_pdf_simple(spec["lineas_texto"])
    return {
        "name": spec["nombre"], "type": "binary",
        "datas": base64.b64encode(contenido).decode("ascii"),
        "res_model": "purchase.order", "res_id": ids[clave_id("compra", spec["compra"])],
    }


def construir_registros(dataset: dict, ids: dict) -> list:
    """Lista plana (modelo, valores) de todo lo que el generador crea; sin red."""
    registros = []
    registros += [("res.partner", valores_socio(s, ids, True)) for s in dataset["clientes"]]
    registros += [("res.partner", valores_socio(s, ids, False)) for s in dataset["proveedores"]]
    registros += [("product.template", valores_producto(s, ids))
                  for s in dataset["productos"] + dataset["materiales"]]
    registros += [("hr.department", valores_departamento(n)) for n in dataset["departamentos"]]
    registros += [("hr.job", valores_cargo(s, ids)) for s in dataset["cargos"]]
    registros += [("hr.employee", valores_empleado(s, ids)) for s in dataset["empleados"]]
    registros += [("sale.order", valores_venta(s, ids))
                  for s in dataset["ventas"] + dataset["cotizaciones"]]
    registros += [("purchase.order", valores_compra(s, ids)) for s in dataset["compras"]]
    registros += [("account.move", valores_factura_proveedor(s, ids))
                  for s in dataset["facturas_proveedor"]]
    registros += [("ir.attachment", valores_respaldo(s, ids)) for s in dataset["respaldos"]]
    return registros


if __name__ == "__main__":
    for nombre, cantidad in conteos_dataset(generar_dataset()).items():
        print(f"{nombre}: {cantidad}")
