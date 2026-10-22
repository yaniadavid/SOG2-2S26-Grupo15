CODIGO_PAIS = "base.gt"
CODIGO_MONEDA = "base.GTQ"


def activar_moneda(entorno, referencia):
    moneda = entorno.ref(referencia)
    moneda.write({"active": True})
    return moneda


def localizar_empresa(entorno, referencia_pais, moneda):
    pais = entorno.ref(referencia_pais)
    entorno.company.write({"country_id": pais.id, "currency_id": moneda.id})
    entorno.cr.commit()
    return entorno.company


def describir(empresa):
    return {
        "empresa": empresa.name,
        "pais": empresa.country_id.code,
        "moneda": empresa.currency_id.name,
        "plan_contable": empresa.chart_template,
    }


moneda_guatemala = activar_moneda(env, CODIGO_MONEDA)
print("RESULTADO:", describir(localizar_empresa(env, CODIGO_PAIS, moneda_guatemala)))
