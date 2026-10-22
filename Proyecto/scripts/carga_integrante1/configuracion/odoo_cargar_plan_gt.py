CODIGO_PLANTILLA = "gt"


def cargar_plan_contable(entorno, codigo_plantilla):
    entorno["account.chart.template"].try_loading(codigo_plantilla, entorno.company)
    entorno.cr.commit()
    return entorno.company


def describir_impuestos(entorno):
    impuestos = entorno["account.tax"].search([("company_id", "=", entorno.company.id)])
    return sorted((t.name, t.amount, t.type_tax_use) for t in impuestos)


def describir(entorno):
    return {
        "plan_contable": entorno.company.chart_template,
        "moneda": entorno.company.currency_id.name,
        "cuentas": entorno["account.account"].search_count([]),
        "diarios": sorted(entorno["account.journal"].search([]).mapped("code")),
        "impuestos": describir_impuestos(entorno),
    }


cargar_plan_contable(env, CODIGO_PLANTILLA)
print("RESULTADO:", describir(env))
