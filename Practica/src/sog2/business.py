from __future__ import annotations

import csv
import math
import os
from collections import Counter, defaultdict
from dataclasses import asdict, is_dataclass
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from statistics import mean, median, mode, StatisticsError
from typing import Any, Iterable

ROOT_DIR = Path(__file__).resolve().parents[2]
CSV_LIMPIO = ROOT_DIR / "data" / "processed" / "ventas_online_2025_limpio.csv"

MESES = {
    1: "Enero",
    2: "Febrero",
    3: "Marzo",
    4: "Abril",
    5: "Mayo",
    6: "Junio",
    7: "Julio",
    8: "Agosto",
    9: "Septiembre",
    10: "Octubre",
    11: "Noviembre",
    12: "Diciembre",
}

ETIQUETAS_GENERO = {0: "Masculino", 1: "Femenino", None: "Sin dato"}
ETIQUETAS_METODO_PAGO = {
    0: "Efectivo",
    1: "Tarjeta de credito",
    2: "Tarjeta de debito",
    None: "Sin dato",
}
ETIQUETAS_NAVEGADOR = {
    0: "Tienda fisica",
    1: "Navegador 1",
    2: "Navegador 2",
    3: "Navegador 3",
    4: "Navegador 4",
    None: "Sin dato",
}

NUMERICAS = {
    "edad",
    "venta_total",
    "numero_compras",
    "monto_compra",
    "tiempo",
}


def _normalizar(valor: Any) -> Any:
    if isinstance(valor, Decimal):
        return float(valor)
    if isinstance(valor, (date, datetime)):
        return valor.isoformat()
    if is_dataclass(valor):
        return asdict(valor)
    return valor


def _normalizar_dict(fila: dict[str, Any]) -> dict[str, Any]:
    return {clave: _normalizar(valor) for clave, valor in fila.items()}


def _leer_csv_limpio() -> list[dict[str, Any]]:
    filas: list[dict[str, Any]] = []
    with CSV_LIMPIO.open("r", encoding="utf-8", newline="") as archivo:
        lector = csv.DictReader(archivo)
        for fila in lector:
            limpia: dict[str, Any] = {}
            for clave, valor in fila.items():
                if valor == "":
                    limpia[clave] = None
                elif clave in {"fila_origen", "id_cliente", "edad", "genero", "numero_compras", "metodo_pago", "navegador"}:
                    limpia[clave] = int(valor)
                elif clave in {"venta_total", "monto_compra", "tiempo"}:
                    limpia[clave] = float(valor)
                elif clave in {"boletin", "vale"}:
                    limpia[clave] = bool(int(valor))
                elif clave == "fecha_compra":
                    limpia[clave] = valor
                    limpia["anio"] = int(valor[:4])
                    limpia["mes"] = int(valor[5:7])
                else:
                    limpia[clave] = valor
            limpia["genero_codigo"] = limpia.get("genero")
            limpia["metodo_pago_codigo"] = limpia.get("metodo_pago")
            limpia["navegador_codigo"] = limpia.get("navegador")
            limpia["genero"] = ETIQUETAS_GENERO.get(limpia.get("genero_codigo"), "Sin dato")
            limpia["metodo_pago"] = ETIQUETAS_METODO_PAGO.get(limpia.get("metodo_pago_codigo"), "Sin dato")
            limpia["navegador"] = ETIQUETAS_NAVEGADOR.get(limpia.get("navegador_codigo"), "Sin dato")
            filas.append(limpia)
    return filas


def obtener_ventas() -> list[dict[str, Any]]:
    """Obtiene ventas desde PostgreSQL; si no hay credenciales locales, usa el CSV limpio."""
    if not os.getenv("INSTANCE_CONNECTION_NAME") and not os.getenv("DB_USER"):
        return _leer_csv_limpio()

    from sqlalchemy import text

    from sog2.database import obtener_motor

    consulta = text(
        """
        SELECT
            registro_id, id_cliente, edad, genero_codigo, genero, venta_total,
            numero_compras, fecha_compra, anio, mes, monto_compra,
            metodo_pago_codigo, metodo_pago, tiempo, navegador_codigo,
            navegador, boletin, vale
        FROM analytics.ventas_detalle
        """
    )
    with obtener_motor().connect() as conexion:
        return [_normalizar_dict(dict(fila)) for fila in conexion.execute(consulta).mappings()]


def total_registros_disponibles() -> dict[str, Any]:
    """Cuenta los registros disponibles para analisis."""
    filas = obtener_ventas()
    fuente = "postgresql" if os.getenv("INSTANCE_CONNECTION_NAME") or os.getenv("DB_USER") else "csv_limpio"
    return {
        "registros_disponibles": len(filas),
        "fuente": fuente,
        "descripcion": "Cada registro corresponde a una fila limpia de ventas online 2025.",
    }


def _valores_numericos(filas: Iterable[dict[str, Any]], variable: str) -> list[float]:
    if variable not in NUMERICAS:
        raise ValueError(f"Variable no permitida: {variable}. Use una de {sorted(NUMERICAS)}.")
    valores: list[float] = []
    for fila in filas:
        valor = fila.get(variable)
        if valor is not None:
            valores.append(float(valor))
    if not valores:
        raise ValueError(f"No hay valores validos para {variable}.")
    return valores


def _moda(valores: list[float]) -> float | None:
    try:
        return float(mode(valores))
    except StatisticsError:
        return None


def estadisticas_basicas(variable: str = "venta_total") -> dict[str, Any]:
    """Calcula media, mediana, moda, minimo, maximo y suma para una variable numerica."""
    filas = obtener_ventas()
    valores = _valores_numericos(filas, variable)
    return {
        "variable": variable,
        "cantidad": len(valores),
        "media": round(mean(valores), 4),
        "mediana": round(median(valores), 4),
        "moda": _moda(valores),
        "minimo": round(min(valores), 4),
        "maximo": round(max(valores), 4),
        "suma": round(sum(valores), 4),
    }


def ventas_por_mes() -> dict[str, Any]:
    """Resume venta total, transacciones y promedios por mes."""
    resumen: dict[int, dict[str, Any]] = {}
    for fila in obtener_ventas():
        mes = int(fila["mes"])
        item = resumen.setdefault(mes, {"mes": mes, "nombre_mes": MESES[mes], "venta_total": 0.0, "transacciones": 0})
        item["venta_total"] += float(fila["venta_total"])
        item["transacciones"] += 1

    resultados = []
    for mes in sorted(resumen):
        item = resumen[mes]
        item["venta_promedio"] = round(item["venta_total"] / item["transacciones"], 4)
        item["venta_total"] = round(item["venta_total"], 4)
        resultados.append(item)
    return {"ventas_por_mes": resultados}


def tendencias_ventas() -> dict[str, Any]:
    """Identifica meses con mayor y menor venta total."""
    datos = ventas_por_mes()["ventas_por_mes"]
    mayor = max(datos, key=lambda item: item["venta_total"])
    menor = min(datos, key=lambda item: item["venta_total"])
    return {
        "mes_mayor_venta": mayor,
        "mes_menor_venta": menor,
        "interpretacion": (
            f"El mes con mayor venta fue {mayor['nombre_mes']} y el mes con menor venta fue "
            f"{menor['nombre_mes']}."
        ),
    }


def distribucion_por_metodo_pago() -> dict[str, Any]:
    """Calcula transacciones y venta total por metodo de pago."""
    return _distribucion_categoria("metodo_pago_codigo", "metodo_pago", "metodos_pago")


def distribucion_por_navegador() -> dict[str, Any]:
    """Calcula transacciones y venta total por navegador/canal."""
    datos = _distribucion_categoria("navegador_codigo", "navegador", "navegadores")
    orden = datos["navegadores"]
    navegadores_validos = [item for item in orden if item["codigo"] is not None]
    datos["navegador_mas_preferido"] = max(navegadores_validos, key=lambda item: item["transacciones"])
    datos["navegador_menos_popular"] = min(navegadores_validos, key=lambda item: item["transacciones"])
    return datos


def _distribucion_categoria(codigo_col: str, etiqueta_col: str, nombre_salida: str) -> dict[str, Any]:
    resumen: dict[Any, dict[str, Any]] = {}
    for fila in obtener_ventas():
        codigo = fila.get(codigo_col)
        etiqueta = fila.get(etiqueta_col) or "Sin dato"
        item = resumen.setdefault(
            codigo,
            {"codigo": codigo, "categoria": etiqueta, "transacciones": 0, "venta_total": 0.0},
        )
        item["transacciones"] += 1
        item["venta_total"] += float(fila["venta_total"])
    total = sum(item["transacciones"] for item in resumen.values())
    salida = []
    for item in sorted(resumen.values(), key=lambda valor: str(valor["codigo"])):
        item["venta_total"] = round(item["venta_total"], 4)
        item["porcentaje_transacciones"] = round(item["transacciones"] * 100 / total, 4)
        salida.append(item)
    return {nombre_salida: salida}


def ventas_en_efectivo() -> dict[str, Any]:
    """Calcula las ventas pagadas contra entrega o en efectivo."""
    filas = [fila for fila in obtener_ventas() if fila.get("metodo_pago_codigo") == 0]
    total_general = len(obtener_ventas())
    return {
        "metodo_pago": "Efectivo",
        "transacciones": len(filas),
        "venta_total": round(sum(float(fila["venta_total"]) for fila in filas), 4),
        "porcentaje_transacciones": round(len(filas) * 100 / total_general, 4) if total_general else 0,
    }


def uso_boletin_vale_por_mes() -> dict[str, Any]:
    """Resume uso mensual de boletines y vales."""
    resumen: dict[int, dict[str, Any]] = {}
    for fila in obtener_ventas():
        mes = int(fila["mes"])
        item = resumen.setdefault(
            mes,
            {
                "mes": mes,
                "nombre_mes": MESES[mes],
                "transacciones": 0,
                "con_boletin": 0,
                "con_vale": 0,
            },
        )
        item["transacciones"] += 1
        item["con_boletin"] += int(fila.get("boletin") is True)
        item["con_vale"] += int(fila.get("vale") is True)

    datos = [resumen[mes] for mes in sorted(resumen)]
    return {
        "uso_por_mes": datos,
        "mes_mas_boletines": max(datos, key=lambda item: item["con_boletin"]),
        "mes_mas_vales": max(datos, key=lambda item: item["con_vale"]),
    }


def segmentacion_por_edad() -> dict[str, Any]:
    """Agrupa clientes por rangos de edad y resume sus patrones de compra."""
    rangos = [
        ("12-17", 12, 18),
        ("18-25", 18, 26),
        ("26-35", 26, 36),
        ("36-50", 36, 51),
        ("51-65", 51, 66),
        ("66+", 66, 101),
    ]
    resumen = {nombre: {"rango_edad": nombre, "transacciones": 0, "venta_total": 0.0, "numero_compras": 0} for nombre, _, _ in rangos}
    sin_dato = {"rango_edad": "Sin dato", "transacciones": 0, "venta_total": 0.0, "numero_compras": 0}
    for fila in obtener_ventas():
        edad = fila.get("edad")
        destino = sin_dato
        if edad is not None:
            for nombre, inicio, fin in rangos:
                if inicio <= int(edad) < fin:
                    destino = resumen[nombre]
                    break
        destino["transacciones"] += 1
        destino["venta_total"] += float(fila["venta_total"])
        destino["numero_compras"] += int(fila["numero_compras"])

    salida = [*resumen.values(), sin_dato]
    for item in salida:
        item["venta_total"] = round(item["venta_total"], 4)
        item["venta_promedio"] = round(item["venta_total"] / item["transacciones"], 4) if item["transacciones"] else 0
        item["compras_promedio"] = round(item["numero_compras"] / item["transacciones"], 4) if item["transacciones"] else 0
    return {"segmentacion_edad": salida}


def segmentacion_por_genero() -> dict[str, Any]:
    """Compara comportamiento de compra entre generos."""
    return _segmentacion_booleana_o_categoria("genero", "segmentacion_genero")


def segmentacion_por_promociones() -> dict[str, Any]:
    """Agrupa por boletin y vale para analizar patrones de compra."""
    return {
        "por_boletin": _segmentacion_booleana_o_categoria("boletin", "segmentacion")["segmentacion"],
        "por_vale": _segmentacion_booleana_o_categoria("vale", "segmentacion")["segmentacion"],
        "por_boletin_y_vale": _segmentacion_doble("boletin", "vale"),
    }


def _segmentacion_booleana_o_categoria(columna: str, nombre_salida: str) -> dict[str, Any]:
    resumen: dict[str, dict[str, Any]] = {}
    for fila in obtener_ventas():
        valor = fila.get(columna)
        etiqueta = "Sin dato" if valor is None else str(valor)
        if isinstance(valor, bool):
            etiqueta = "Si" if valor else "No"
        item = resumen.setdefault(etiqueta, {"categoria": etiqueta, "transacciones": 0, "venta_total": 0.0, "numero_compras": 0})
        item["transacciones"] += 1
        item["venta_total"] += float(fila["venta_total"])
        item["numero_compras"] += int(fila["numero_compras"])
    salida = list(resumen.values())
    for item in salida:
        item["venta_total"] = round(item["venta_total"], 4)
        item["venta_promedio"] = round(item["venta_total"] / item["transacciones"], 4)
        item["compras_promedio"] = round(item["numero_compras"] / item["transacciones"], 4)
    return {nombre_salida: sorted(salida, key=lambda item: item["categoria"])}


def _segmentacion_doble(columna1: str, columna2: str) -> list[dict[str, Any]]:
    resumen: dict[tuple[str, str], dict[str, Any]] = {}
    for fila in obtener_ventas():
        valor1 = "Si" if fila.get(columna1) is True else "No" if fila.get(columna1) is False else "Sin dato"
        valor2 = "Si" if fila.get(columna2) is True else "No" if fila.get(columna2) is False else "Sin dato"
        item = resumen.setdefault((valor1, valor2), {"boletin": valor1, "vale": valor2, "transacciones": 0, "venta_total": 0.0})
        item["transacciones"] += 1
        item["venta_total"] += float(fila["venta_total"])
    salida = list(resumen.values())
    for item in salida:
        item["venta_total"] = round(item["venta_total"], 4)
        item["venta_promedio"] = round(item["venta_total"] / item["transacciones"], 4)
    return sorted(salida, key=lambda item: (item["boletin"], item["vale"]))


def correlacion_edad_venta() -> dict[str, Any]:
    """Calcula la correlacion de Pearson entre edad y venta total."""
    filas = [fila for fila in obtener_ventas() if fila.get("edad") is not None]
    return _correlacion_pearson(filas, "edad", "venta_total")


def _correlacion_pearson(filas: list[dict[str, Any]], x_col: str, y_col: str) -> dict[str, Any]:
    pares = [(float(fila[x_col]), float(fila[y_col])) for fila in filas if fila.get(x_col) is not None and fila.get(y_col) is not None]
    if len(pares) < 2:
        raise ValueError("Se necesitan al menos dos pares validos.")
    xs = [par[0] for par in pares]
    ys = [par[1] for par in pares]
    media_x = mean(xs)
    media_y = mean(ys)
    numerador = sum((x - media_x) * (y - media_y) for x, y in pares)
    denom_x = math.sqrt(sum((x - media_x) ** 2 for x in xs))
    denom_y = math.sqrt(sum((y - media_y) ** 2 for y in ys))
    coef = numerador / (denom_x * denom_y) if denom_x and denom_y else 0.0
    return {
        "variable_1": x_col,
        "variable_2": y_col,
        "coeficiente_pearson": round(coef, 6),
        "cantidad_pares": len(pares),
        "interpretacion": _interpretar_correlacion(coef),
    }


def _interpretar_correlacion(coeficiente: float) -> str:
    valor = abs(coeficiente)
    if valor > 0.8:
        fuerza = "fuerte"
    elif valor > 0.5:
        fuerza = "moderada"
    elif valor > 0.2:
        fuerza = "debil"
    else:
        fuerza = "muy debil o nula"
    direccion = "positiva" if coeficiente > 0 else "negativa" if coeficiente < 0 else "nula"
    return f"Relacion {fuerza} {direccion}."


def asociacion_genero_metodo_pago() -> dict[str, Any]:
    """Examina la asociacion entre genero y metodo de pago preferido."""
    return _asociacion_categorica("genero", "metodo_pago")


def asociacion_boletin_vale() -> dict[str, Any]:
    """Examina la asociacion entre uso de boletin y uso de vale."""
    return _asociacion_categorica("boletin", "vale")


def _asociacion_categorica(columna1: str, columna2: str) -> dict[str, Any]:
    filas = [fila for fila in obtener_ventas() if fila.get(columna1) is not None and fila.get(columna2) is not None]
    tabla: dict[str, Counter[str]] = defaultdict(Counter)
    for fila in filas:
        val1 = str(fila[columna1])
        val2 = str(fila[columna2])
        tabla[val1][val2] += 1

    filas_etiquetas = sorted(tabla)
    columnas_etiquetas = sorted({col for conteos in tabla.values() for col in conteos})
    total = sum(sum(tabla[fila].values()) for fila in filas_etiquetas)
    if total == 0:
        raise ValueError("No hay pares validos para calcular asociacion.")

    chi2 = 0.0
    total_filas = {fila: sum(tabla[fila].values()) for fila in filas_etiquetas}
    total_columnas = {col: sum(tabla[fila][col] for fila in filas_etiquetas) for col in columnas_etiquetas}
    for fila in filas_etiquetas:
        for col in columnas_etiquetas:
            esperado = total_filas[fila] * total_columnas[col] / total
            observado = tabla[fila][col]
            if esperado:
                chi2 += (observado - esperado) ** 2 / esperado

    minimo_dim = min(len(filas_etiquetas) - 1, len(columnas_etiquetas) - 1)
    cramers_v = math.sqrt(chi2 / (total * minimo_dim)) if minimo_dim > 0 else 0.0
    return {
        "variable_1": columna1,
        "variable_2": columna2,
        "tabla_contingencia": {
            fila: {col: tabla[fila][col] for col in columnas_etiquetas}
            for fila in filas_etiquetas
        },
        "chi_cuadrado": round(chi2, 6),
        "cramers_v": round(cramers_v, 6),
        "cantidad_pares": total,
        "interpretacion": _interpretar_cramers_v(cramers_v),
    }


def _interpretar_cramers_v(valor: float) -> str:
    if valor >= 0.5:
        fuerza = "fuerte"
    elif valor >= 0.3:
        fuerza = "moderada"
    elif valor >= 0.1:
        fuerza = "debil"
    else:
        fuerza = "muy debil o nula"
    return f"Asociacion {fuerza} segun Cramer's V."


def resumen_puntos_2_al_6() -> dict[str, Any]:
    """Devuelve un resumen compacto de los puntos 2 al 6 solicitados por la practica."""
    return {
        "analisis_exploratorio": {
            "venta_total": estadisticas_basicas("venta_total"),
            "monto_compra": estadisticas_basicas("monto_compra"),
            "numero_compras": estadisticas_basicas("numero_compras"),
            "ventas_por_mes": ventas_por_mes()["ventas_por_mes"],
            "metodos_pago": distribucion_por_metodo_pago()["metodos_pago"],
            "navegadores": distribucion_por_navegador()["navegadores"],
            "boletin_vale_por_mes": uso_boletin_vale_por_mes()["uso_por_mes"],
        },
        "tendencias": tendencias_ventas(),
        "segmentacion": {
            "edad": segmentacion_por_edad()["segmentacion_edad"],
            "genero": segmentacion_por_genero()["segmentacion_genero"],
            "promociones": segmentacion_por_promociones(),
        },
        "correlaciones": {
            "edad_venta": correlacion_edad_venta(),
            "genero_metodo_pago": asociacion_genero_metodo_pago(),
            "boletin_vale": asociacion_boletin_vale(),
        },
    }
