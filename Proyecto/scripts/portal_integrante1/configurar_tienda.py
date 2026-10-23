"""Configura la tienda web QuetzalMart: sitio, categorias, publicacion, imagenes, envio, impuestos.

Simulacion por defecto; use --aplicar para escribir. Credenciales por ODOO_URL, ODOO_DB,
ODOO_USER y ODOO_PASSWORD.
"""
import base64

from comun import (MARCA, METODO_ENVIO, NOMBRE_SITIO, PREFIJO_VENTA, asegurar, conectar_desde_entorno,
                   crear_parser, escribir, informar, leer_uno, modo_aplicar)
from imagenes_producto import generar_png

CATEGORIAS = {
    "Abarrotes": ("Arroz blanco 5 lb", "Frijol negro 2 lb", "Azucar blanca 5 lb", "Aceite vegetal 900 ml",
                  "Harina de trigo 2 lb", "Sal yodada 1 kg", "Cafe molido 400 g", "Pasta espagueti 500 g",
                  "Salsa de tomate 400 g", "Mayonesa 400 g", "Atun en lata 140 g", "Cereal de maiz 500 g",
                  "Galletas de soda 6 u"),
    "Lacteos y huevos": ("Leche entera 1 L", "Queso fresco 1 lb", "Crema 250 ml", "Huevos blancos cartera 30 u"),
    "Panaderia": ("Pan de caja 600 g", "Tortillas empacadas 1 lb"),
    "Carnes y embutidos": ("Pollo entero fresco 1 lb", "Carne molida de res 1 lb", "Chuleta de cerdo 1 lb",
                           "Jamon de pavo 1 lb", "Salchicha tipo viena 12 u"),
    "Frutas y verduras": ("Tomate 1 lb", "Cebolla blanca 1 lb", "Papa 1 lb", "Banano 1 lb",
                          "Manzana roja 1 lb", "Limon 1 lb"),
    "Bebidas": ("Gaseosa cola 2.5 L", "Agua pura 20 L", "Jugo de naranja 1 L", "Cerveza nacional lata 355 ml"),
    "Hogar y cuidado personal": ("Detergente en polvo 1 kg", "Jabon de bano 3 u", "Papel higienico 12 rollos",
                                 "Shampoo 400 ml", "Pasta dental 100 ml", "Servilletas 500 u"),
}
PRECIO_ENVIO_DEFECTO = 25.0
TOTAL_PRODUCTOS = 40
CAMPOS_PRODUCTO = ["name", "default_code", "taxes_id", "is_published", "website_id",
                   "public_categ_ids", "description_ecommerce", "image_1920"]


def categoria_de(nombre: str):
    for categoria, nombres in CATEGORIAS.items():
        if nombre in nombres:
            return categoria
    return None


def descripcion_comercial(nombre: str, categoria: str) -> str:
    return (f"<p>{nombre}, disponible en la categoria {categoria} de {NOMBRE_SITIO}. "
            f"Precio en quetzales con IVA incluido y entrega a domicilio.</p>")


def valores_producto_web(producto: dict, ids_categoria: dict, website_id: int) -> dict:
    """Solo los campos que difieren del estado actual (idempotencia), sin la imagen."""
    categoria = categoria_de(producto["name"])
    deseado = {"is_published": True, "website_id": website_id}
    if categoria:
        deseado["public_categ_ids"] = [(6, 0, [ids_categoria[categoria]])]
        deseado["description_ecommerce"] = descripcion_comercial(producto["name"], categoria)
    actual = {
        "is_published": producto["is_published"],
        "website_id": producto["website_id"][0] if producto["website_id"] else False,
        "public_categ_ids": [(6, 0, sorted(producto["public_categ_ids"]))],
        "description_ecommerce": producto["description_ecommerce"] or "",
    }
    return {campo: valor for campo, valor in deseado.items() if actual[campo] != valor}


def imagen_base64(codigo: str) -> str:
    return base64.b64encode(generar_png(codigo)).decode("ascii")


def evaluar_impuestos(productos: list, impuestos: dict) -> list:
    """Incidencias de productos cuyo impuesto de venta no sea IVA 12 % con precio incluido."""
    incidencias = []
    for p in productos:
        ids = p["taxes_id"]
        if len(ids) != 1:
            incidencias.append(f"{p['default_code']}: tiene {len(ids)} impuestos de venta")
            continue
        t = impuestos[ids[0]]
        if not (t["price_include"] and abs(t["amount"] - 12.0) < 1e-9
                and t["amount_type"] == "percent" and t["type_tax_use"] == "sale"):
            incidencias.append(f"{p['default_code']}: impuesto '{t['name']}' no es IVA 12 % incluido")
    return incidencias


def configurar_sitio(ejecutar, aplicar: bool) -> int:
    sitio = leer_uno(ejecutar, "website", [], ["name", "show_line_subtotals_tax_selection"])
    if sitio["name"] != NOMBRE_SITIO:
        escribir(ejecutar, aplicar, "website", [sitio["id"]], {"name": NOMBRE_SITIO},
                 f"renombrar '{sitio['name']}' a '{NOMBRE_SITIO}'")
    informar(f"Visualizacion de impuestos del sitio: {sitio['show_line_subtotals_tax_selection']} "
             "(tax_included muestra precios con IVA; solo se reporta, no se modifica)")
    return sitio["id"]


def configurar_categorias(ejecutar, aplicar: bool, website_id: int) -> dict:
    ids = {}
    for orden, nombre in enumerate(CATEGORIAS, start=1):
        dominio = [("name", "=", nombre), ("website_id", "in", [False, website_id])]
        if aplicar:
            ids[nombre], creado = asegurar(ejecutar, "product.public.category", dominio, {
                "name": nombre, "sequence": orden, "website_id": website_id,
                "website_meta_keywords": MARCA})
            informar(f"Categoria '{nombre}': {'creada' if creado else 'ya existia'} (id {ids[nombre]})")
        else:
            existente = leer_uno(ejecutar, "product.public.category", dominio, ["name"])
            ids[nombre] = existente["id"] if existente else 0
            informar(f"[SIMULA] categoria '{nombre}': {'existe' if existente else 'se crearia'}")
    return ids


def configurar_productos(ejecutar, aplicar: bool, ids_categoria: dict, website_id: int) -> list:
    productos = ejecutar("product.template", "search_read", [[("default_code", "=like", PREFIJO_VENTA + "%")]],
                         {"fields": CAMPOS_PRODUCTO, "context": {"active_test": False}})
    if len(productos) != TOTAL_PRODUCTOS:
        informar(f"ADVERTENCIA: se esperaban {TOTAL_PRODUCTOS} productos {PREFIJO_VENTA} y hay {len(productos)}")
    for p in productos:
        if categoria_de(p["name"]) is None:
            informar(f"ADVERTENCIA: '{p['name']}' sin categoria definida")
        valores = valores_producto_web(p, ids_categoria, website_id)
        if not p["image_1920"]:
            valores["image_1920"] = imagen_base64(p["default_code"])
        if valores:
            escribir(ejecutar, aplicar, "product.template", [p["id"]], valores,
                     f"{p['default_code']} campos {sorted(valores)}")
    return productos


def configurar_envio(ejecutar, aplicar: bool, precio: float) -> None:
    metodo = leer_uno(ejecutar, "delivery.carrier", [("name", "=", METODO_ENVIO)],
                      ["fixed_price", "delivery_type", "is_published"])
    if not metodo:
        informar(f"ADVERTENCIA: no existe el metodo de envio '{METODO_ENVIO}'")
        return
    if metodo["delivery_type"] != "fixed":
        informar(f"ADVERTENCIA: '{METODO_ENVIO}' no es de precio fijo ({metodo['delivery_type']})")
        return
    if abs(metodo["fixed_price"] - precio) > 1e-9:
        escribir(ejecutar, aplicar, "delivery.carrier", [metodo["id"]], {"fixed_price": precio},
                 f"fixed_price {metodo['fixed_price']} -> {precio} GTQ")
    else:
        informar(f"Envio '{METODO_ENVIO}' ya en {precio} GTQ")


def verificar_impuestos(ejecutar, productos: list) -> None:
    ids = sorted({i for p in productos for i in p["taxes_id"]})
    filas = ejecutar("account.tax", "read", [ids], {"fields": [
        "name", "price_include", "amount", "amount_type", "type_tax_use"]}) if ids else []
    incidencias = evaluar_impuestos(productos, {f["id"]: f for f in filas})
    if incidencias:
        informar("INCIDENCIAS DE IMPUESTO:")
        for i in incidencias:
            informar("  " + i)
    else:
        informar(f"Impuestos OK: {len(productos)} productos con IVA 12 % de precio incluido")


def main() -> None:
    parser = crear_parser(__doc__)
    parser.add_argument("--precio-envio", type=float, default=PRECIO_ENVIO_DEFECTO,
                        help="Precio fijo en GTQ de 'Standard delivery' (defecto %(default)s)")
    argumentos = parser.parse_args()
    aplicar = modo_aplicar(argumentos)
    if argumentos.precio_envio < 0:
        raise SystemExit("--precio-envio no puede ser negativo")
    ejecutar = conectar_desde_entorno()
    informar("Modo: " + ("APLICAR" if aplicar else "SIMULACION (--dry-run)"))
    website_id = configurar_sitio(ejecutar, aplicar)
    ids_categoria = configurar_categorias(ejecutar, aplicar, website_id)
    productos = configurar_productos(ejecutar, aplicar, ids_categoria, website_id)
    configurar_envio(ejecutar, aplicar, argumentos.precio_envio)
    verificar_impuestos(ejecutar, productos)


if __name__ == "__main__":
    main()
