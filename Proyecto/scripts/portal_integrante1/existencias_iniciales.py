CANTIDAD_INICIAL = 100
PREFIJO_PRODUCTOS_VENDIBLES = "I1-PV-"


def productos_vendibles(entorno):
    plantillas = entorno["product.template"].search([("default_code", "=like", PREFIJO_PRODUCTOS_VENDIBLES + "%")])
    return plantillas.mapped("product_variant_id")


def ubicacion_de_existencias(entorno):
    almacen = entorno["stock.warehouse"].search([], limit=1)
    return almacen.lot_stock_id


def existencia_actual(entorno, producto, ubicacion):
    return entorno["stock.quant"]._get_available_quantity(producto, ubicacion)


def cargar_existencia(entorno, producto, ubicacion, cantidad):
    quant = entorno["stock.quant"].with_context(inventory_mode=True).create({
        "product_id": producto.id,
        "location_id": ubicacion.id,
        "inventory_quantity": cantidad,
    })
    quant.action_apply_inventory()


def describir(entorno, productos, ubicacion):
    return {
        "ubicacion": ubicacion.display_name,
        "productos": len(productos),
        "almacenables": sum(1 for p in productos if p.is_storable),
        "unidades_totales": sum(existencia_actual(entorno, p, ubicacion) for p in productos),
    }


productos = productos_vendibles(env)
ubicacion = ubicacion_de_existencias(env)
print("ANTES:", describir(env, productos, ubicacion))
for producto in productos:
    if producto.is_storable and existencia_actual(env, producto, ubicacion) == 0:
        cargar_existencia(env, producto, ubicacion, CANTIDAD_INICIAL)
env.cr.commit()
print("DESPUES:", describir(env, productos, ubicacion))
