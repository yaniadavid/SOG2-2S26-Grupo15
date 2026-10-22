NOMBRE_EMPRESA = "QuetzalMart"


def renombrar_empresa(entorno, nombre):
    empresa = entorno.company
    empresa.write({"name": nombre})
    entorno.cr.commit()
    return empresa


def describir(empresa):
    return {
        "empresa": empresa.name,
        "socio_asociado": empresa.partner_id.name,
        "moneda": empresa.currency_id.name,
        "pais": empresa.country_id.code,
    }


print("RESULTADO:", describir(renombrar_empresa(env, NOMBRE_EMPRESA)))
