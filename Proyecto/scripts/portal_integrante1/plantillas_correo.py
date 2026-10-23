"""Crea la plantilla de la campana post-compra y reporta la plantilla estandar del recibo.

Uso:
    python plantillas_correo.py              # dry-run (por defecto)
    python plantillas_correo.py --aplicar    # crea o actualiza la plantilla
    python plantillas_correo.py --aplicar --minutos 5 --reemplazar-cuerpo

Variables de entorno: ODOO_URL, ODOO_DB, ODOO_USER, ODOO_PASSWORD.

El envio diferido usa mail.template.scheduled_date (campo char con expresion
renderizada en el momento del envio). El cuerpo es provisional: si la plantilla ya
existe NO se pisa el cuerpo salvo con --reemplazar-cuerpo (diseno del Integrante 2).
"""
from correo_comun import (
    ASUNTO_CAMPANA, MINUTOS_DIFERIDO, MODELO_ORDEN, NOMBRE_PLANTILLA, Ejecutor,
    buscar_plantilla, conectar_desde_entorno, crear_parser, id_modelo, informar,
)

CUERPO_PROVISIONAL = (
    '<div style="font-family: Arial, sans-serif; color: #333333; max-width: 560px;">'
    '<p>Hola <t t-out="object.partner_id.name or \'cliente\'"/>,</p>'
    "<p>Gracias por su compra en QuetzalMart. Tenemos una promocion exclusiva "
    "preparada para usted.</p>"
    '<p><a t-attf-href="{{ object.get_base_url() }}/shop" '
    'style="color: #1a5276;">Visitar la tienda</a></p>'
    "<p>Equipo QuetzalMart</p></div>"
)

PLANTILLAS_ESTANDAR = (("sale", "email_template_edi_sale"),
                       ("website_sale", "mail_template_sale_confirmation"))


def expresion_envio_diferido(minutos: int) -> str:
    return ("{{ (datetime.datetime.now() + datetime.timedelta(minutes=%d))"
            ".strftime('%%Y-%%m-%%d %%H:%%M:%%S') }}" % minutos)


def valores_plantilla(modelo_id: int, minutos: int, con_cuerpo: bool) -> dict:
    valores = {
        "name": NOMBRE_PLANTILLA,
        "model_id": modelo_id,
        "subject": ASUNTO_CAMPANA,
        "email_to": "{{ object.partner_id.email }}",
        "use_default_to": False,
        "scheduled_date": expresion_envio_diferido(minutos) if minutos > 0 else False,
        "auto_delete": True,
    }
    if con_cuerpo:
        valores["body_html"] = CUERPO_PROVISIONAL
    return valores


def asuntos_distintos(asunto_recibo: str | None, asunto_campana: str) -> bool:
    return bool(asunto_recibo) and asunto_recibo.strip() != asunto_campana.strip()


def localizar_plantilla_estandar(ejecutar: Ejecutor) -> dict | None:
    for modulo, nombre in PLANTILLAS_ESTANDAR:
        datos = ejecutar("ir.model.data", "search_read",
                         [[("module", "=", modulo), ("name", "=", nombre),
                           ("model", "=", "mail.template")]],
                         {"fields": ["res_id"], "limit": 1})
        if datos:
            leida = ejecutar("mail.template", "read", [[datos[0]["res_id"]]],
                             {"fields": ["name", "subject"]})
            if leida:
                return {**leida[0], "xmlid": f"{modulo}.{nombre}"}
    return None


def sincronizar(ejecutar: Ejecutor, minutos: int, reemplazar_cuerpo: bool, aplicar: bool) -> None:
    existente = buscar_plantilla(ejecutar, NOMBRE_PLANTILLA)
    modelo = id_modelo(ejecutar, MODELO_ORDEN)
    if existente is None:
        informar(f"[{'CREAR' if aplicar else 'DRY'}] plantilla '{NOMBRE_PLANTILLA}'")
        if aplicar:
            ejecutar("mail.template", "create", [valores_plantilla(modelo, minutos, True)])
        return
    informar(f"[{'ACTUALIZAR' if aplicar else 'DRY'}] plantilla id={existente}")
    if aplicar:
        ejecutar("mail.template", "write",
                 [[existente], valores_plantilla(modelo, minutos, reemplazar_cuerpo)])


def reportar_estandar(ejecutar: Ejecutor) -> None:
    estandar = localizar_plantilla_estandar(ejecutar)
    if estandar is None:
        informar("Plantilla estandar de confirmacion: NO localizada por xml id; verificar a mano.")
        return
    informar(f"Plantilla estandar {estandar['xmlid']} asunto: {estandar['subject']}")
    informar(f"Asunto de campana: {ASUNTO_CAMPANA}")
    distintos = asuntos_distintos(estandar["subject"], ASUNTO_CAMPANA)
    informar("Asuntos distintos: " + ("SI" if distintos else "NO"))


def main() -> None:
    parser = crear_parser(__doc__.splitlines()[0])
    parser.add_argument("--minutos", type=int, default=MINUTOS_DIFERIDO,
                        help="Minutos de diferimiento (0 desactiva).")
    parser.add_argument("--reemplazar-cuerpo", action="store_true")
    args = parser.parse_args()
    if args.minutos < 0:
        raise SystemExit("--minutos no puede ser negativo.")
    ejecutar = conectar_desde_entorno()
    sincronizar(ejecutar, args.minutos, args.reemplazar_cuerpo, args.aplicar)
    reportar_estandar(ejecutar)


if __name__ == "__main__":
    main()
