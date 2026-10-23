"""Automatizacion base_automation: envia la campana al confirmarse una orden del sitio web.

Uso:
    python regla_post_compra.py --contar            # solo lectura: ordenes historicas que coinciden
    python regla_post_compra.py                     # dry-run (por defecto)
    python regla_post_compra.py --aplicar [--modo mail_post|codigo]

Disparador: trigger 'on_state_set' con trg_selection_field_id = sale.order.state 'sale'
(solo al TRANSICIONAR a confirmada, nunca sobre las ordenes ya existentes). Filtro
(filter_domain): website_id != False, state = sale y que la orden no tenga ya un mensaje
con el asunto de la campana (una sola vez). Accion: ir.actions.server state 'mail_post'
con template_id (o, con --modo codigo, state 'code' que llama a send_mail).
Requiere haber ejecutado plantillas_correo.py --aplicar.
"""
from correo_comun import (
    ASUNTO_CAMPANA, MODELO_ORDEN, NOMBRE_ACCION, NOMBRE_PLANTILLA, NOMBRE_REGLA,
    Ejecutor, buscar_ids, buscar_plantilla, conectar_desde_entorno, crear_parser,
    id_modelo, informar,
)

DOMINIO_HISTORICO = [("website_id", "!=", False), ("state", "=", "sale")]


def dominio_filtro() -> list:
    return DOMINIO_HISTORICO + [("message_ids.subject", "not ilike", ASUNTO_CAMPANA)]


def codigo_envio(plantilla_id: int) -> str:
    return (f"template = env['mail.template'].browse({plantilla_id})\n"
            "for record in records:\n"
            "    template.send_mail(record.id, force_send=False)")


def valores_accion(modelo_id: int, plantilla_id: int, modo: str) -> dict:
    base = {"name": NOMBRE_ACCION, "model_id": modelo_id}
    if modo == "codigo":
        return {**base, "state": "code", "code": codigo_envio(plantilla_id)}
    return {**base, "state": "mail_post", "template_id": plantilla_id,
            "mail_post_method": "email", "mail_post_autofollow": False}


def valores_regla(modelo_id: int, seleccion_id: int, accion: dict) -> dict:
    return {
        "name": NOMBRE_REGLA,
        "model_id": modelo_id,
        "trigger": "on_state_set",
        "trg_selection_field_id": seleccion_id,
        "filter_domain": repr(dominio_filtro()),
        "active": True,
        "action_server_ids": [(0, 0, accion)],
    }


def contar(ejecutar: Ejecutor) -> None:
    total = ejecutar(MODELO_ORDEN, "search_count", [[]])
    web = ejecutar(MODELO_ORDEN, "search_count", [[("website_id", "!=", False)]])
    historicas = ejecutar(MODELO_ORDEN, "search_count", [dominio_filtro()])
    informar(f"Ordenes totales: {total}; con sitio web: {web}")
    informar(f"Ordenes historicas que coinciden con el filtro: {historicas}")
    informar("(La regla ademas solo dispara al TRANSICIONAR a 'sale'; esperado: 0)")


def id_seleccion_estado(ejecutar: Ejecutor) -> int:
    ids = buscar_ids(ejecutar, "ir.model.fields.selection",
                     [("field_id.model", "=", MODELO_ORDEN),
                      ("field_id.name", "=", "state"), ("value", "=", "sale")])
    if not ids:
        raise SystemExit("No se hallo el valor 'sale' del campo state de sale.order.")
    return ids[0]


def actualizar(ejecutar: Ejecutor, regla_id: int, valores: dict, accion: dict) -> None:
    acciones = ejecutar("base.automation", "read", [[regla_id]],
                        {"fields": ["action_server_ids"]})[0]["action_server_ids"]
    cambios = {k: v for k, v in valores.items() if k != "action_server_ids"}
    ejecutar("base.automation", "write", [[regla_id], cambios])
    if acciones:
        ejecutar("ir.actions.server", "write", [acciones[:1], accion])
    else:
        ejecutar("base.automation", "write",
                 [[regla_id], {"action_server_ids": [(0, 0, accion)]}])


def sincronizar(ejecutar: Ejecutor, modo: str, aplicar: bool) -> None:
    plantilla = buscar_plantilla(ejecutar, NOMBRE_PLANTILLA)
    if plantilla is None:
        raise SystemExit("Falta la plantilla; ejecute plantillas_correo.py --aplicar primero.")
    modelo = id_modelo(ejecutar, MODELO_ORDEN)
    accion = valores_accion(modelo, plantilla, modo)
    valores = valores_regla(modelo, id_seleccion_estado(ejecutar), accion)
    existente = buscar_ids(ejecutar, "base.automation", [("name", "=", NOMBRE_REGLA)])
    if not existente:
        informar(f"[{'CREAR' if aplicar else 'DRY'}] automatizacion '{NOMBRE_REGLA}' (modo {modo})")
        if aplicar:
            ejecutar("base.automation", "create", [valores])
        return
    informar(f"[{'ACTUALIZAR' if aplicar else 'DRY'}] automatizacion id={existente[0]}")
    if aplicar:
        actualizar(ejecutar, existente[0], valores, accion)


def main() -> None:
    parser = crear_parser(__doc__.splitlines()[0])
    parser.add_argument("--contar", action="store_true",
                        help="Solo lectura: cuenta ordenes historicas que coinciden.")
    parser.add_argument("--modo", choices=("mail_post", "codigo"), default="mail_post")
    args = parser.parse_args()
    ejecutar = conectar_desde_entorno()
    if args.contar:
        contar(ejecutar)
        return
    sincronizar(ejecutar, args.modo, args.aplicar)


if __name__ == "__main__":
    main()
