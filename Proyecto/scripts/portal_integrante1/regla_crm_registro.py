"""Automatizacion: al crearse un usuario de portal por registro web, crea un crm.lead con su contacto.

Simulacion por defecto; use --aplicar para crear. Idempotente por nombre.
"""
from comun import MARCA, buscar_ids, conectar_desde_entorno, crear_parser, informar, modo_aplicar

NOMBRE_AUTOMATIZACION = f"{MARCA} Crear lead al registrarse en la tienda"
NOMBRE_ACCION = f"{MARCA} Accion: lead de registro web"
FILTRO_PORTAL = "[('share', '=', True)]"

CODIGO_ACCION = """for usuario in records:
    if not usuario.share or not usuario.partner_id:
        continue
    nombre = 'I1-PORTAL Registro web: %s' % usuario.name
    if env['crm.lead'].sudo().search_count([('name', '=', nombre), ('partner_id', '=', usuario.partner_id.id)]):
        continue
    equipo = env['crm.team'].sudo().search([('name', '=', 'Website')], limit=1)
    env['crm.lead'].sudo().create({
        'name': nombre,
        'type': 'opportunity',
        'partner_id': usuario.partner_id.id,
        'contact_name': usuario.name,
        'email_from': usuario.email or usuario.login,
        'team_id': equipo.id or False,
        'description': 'Cliente registrado desde el portal web de QuetzalMart.',
    })
"""


def valores_accion(id_modelo_usuario: int) -> dict:
    return {"name": NOMBRE_ACCION, "model_id": id_modelo_usuario, "state": "code", "code": CODIGO_ACCION}


def valores_automatizacion(id_modelo_usuario: int, id_accion: int) -> dict:
    return {
        "name": NOMBRE_AUTOMATIZACION, "model_id": id_modelo_usuario, "trigger": "on_create",
        "filter_domain": FILTRO_PORTAL, "active": True,
        "action_server_ids": [(6, 0, [id_accion])],
    }


def asegurar_regla(ejecutar, aplicar: bool) -> None:
    modelo = ejecutar("ir.model", "search", [[("model", "=", "res.users")]])
    if not modelo:
        raise SystemExit("No se encontro el modelo res.users")
    id_modelo = modelo[0]
    if buscar_ids(ejecutar, "base.automation", [("name", "=", NOMBRE_AUTOMATIZACION)]):
        informar("La automatizacion ya existe; no se modifica.")
        return
    accion = buscar_ids(ejecutar, "ir.actions.server", [("name", "=", NOMBRE_ACCION)])
    if not aplicar:
        informar(f"[SIMULA] se crearia la accion '{NOMBRE_ACCION}' y la automatizacion "
                 f"'{NOMBRE_AUTOMATIZACION}' (on_create en res.users, filtro {FILTRO_PORTAL})")
        return
    id_accion = accion[0] if accion else ejecutar("ir.actions.server", "create", [valores_accion(id_modelo)])
    id_regla = ejecutar("base.automation", "create", [valores_automatizacion(id_modelo, id_accion)])
    informar(f"Automatizacion creada (id {id_regla}) con accion id {id_accion}")


def main() -> None:
    argumentos = crear_parser(__doc__).parse_args()
    aplicar = modo_aplicar(argumentos)
    informar("Modo: " + ("APLICAR" if aplicar else "SIMULACION (--dry-run)"))
    asegurar_regla(conectar_desde_entorno(), aplicar)


if __name__ == "__main__":
    main()
