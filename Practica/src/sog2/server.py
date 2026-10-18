from __future__ import annotations

import logging
import os
from pathlib import Path
from typing import Any

from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from sog2.business import (
    asociacion_boletin_vale,
    asociacion_genero_metodo_pago,
    correlacion_edad_venta,
    distribucion_por_metodo_pago,
    distribucion_por_navegador,
    estadisticas_basicas,
    resumen_puntos_2_al_6,
    segmentacion_por_edad,
    segmentacion_por_genero,
    segmentacion_por_promociones,
    tendencias_ventas,
    total_registros_disponibles,
    uso_boletin_vale_por_mes,
    ventas_en_efectivo,
    ventas_por_mes,
)
from sog2.database import verificar_postgresql
from sog2.visualizations import exportar_visualizaciones


logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))
logger = logging.getLogger(__name__)

mcp = FastMCP(
    "Ventas Online 2025",
    instructions="Herramientas para consultar y analizar las ventas online de 2025.",
    host=os.getenv("MCP_HOST", "127.0.0.1"),
    port=int(os.getenv("PORT", "8080")),
    streamable_http_path="/mcp",
    stateless_http=True,
    json_response=True,
)


@mcp.custom_route("/health", methods=["GET"])
async def health(_: Request) -> JSONResponse:
    return JSONResponse({"estado": "ok"})


@mcp.tool()
def verificar_conexion_postgresql() -> dict[str, Any]:
    """Comprueba la conexión con PostgreSQL y cuenta los registros disponibles."""
    try:
        return verificar_postgresql()
    except Exception as error:
        logger.error("No se pudo consultar PostgreSQL: %s", type(error).__name__)
        return {
            "ok": False,
            "mensaje": "No se pudo conectar con PostgreSQL.",
        }


@mcp.tool()
def consultar_total_registros() -> dict[str, Any]:
    """Devuelve el total real de registros disponibles para analisis."""
    return total_registros_disponibles()


@mcp.tool()
def calcular_estadisticas_basicas(variable: str = "venta_total") -> dict[str, Any]:
    """Calcula media, mediana, moda, minimo, maximo y suma de una variable numerica.

    Variables permitidas: edad, venta_total, numero_compras, monto_compra y tiempo.
    """
    return estadisticas_basicas(variable)


@mcp.tool()
def consultar_ventas_por_mes() -> dict[str, Any]:
    """Devuelve la venta total, transacciones y venta promedio por mes."""
    return ventas_por_mes()


@mcp.tool()
def consultar_tendencias_de_ventas() -> dict[str, Any]:
    """Identifica los meses con mayor y menor venta total."""
    return tendencias_ventas()


@mcp.tool()
def consultar_distribucion_metodos_pago() -> dict[str, Any]:
    """Devuelve transacciones, venta total y porcentaje por metodo de pago."""
    return distribucion_por_metodo_pago()


@mcp.tool()
def consultar_ventas_en_efectivo() -> dict[str, Any]:
    """Devuelve el total de ventas pagadas en efectivo o contra entrega."""
    return ventas_en_efectivo()


@mcp.tool()
def consultar_distribucion_navegadores() -> dict[str, Any]:
    """Devuelve transacciones, venta total, navegador mas preferido y menos popular."""
    return distribucion_por_navegador()


@mcp.tool()
def consultar_uso_boletin_vale_por_mes() -> dict[str, Any]:
    """Devuelve el uso mensual de boletines y vales, incluyendo los meses de mayor uso."""
    return uso_boletin_vale_por_mes()


@mcp.tool()
def consultar_segmentacion_por_edad() -> dict[str, Any]:
    """Agrupa clientes por rangos de edad y resume venta y compras promedio."""
    return segmentacion_por_edad()


@mcp.tool()
def consultar_segmentacion_por_genero() -> dict[str, Any]:
    """Compara patrones de compra por genero."""
    return segmentacion_por_genero()


@mcp.tool()
def consultar_segmentacion_por_promociones() -> dict[str, Any]:
    """Agrupa ventas por uso de boletin, vale y combinacion boletin-vale."""
    return segmentacion_por_promociones()


@mcp.tool()
def consultar_correlacion_edad_venta() -> dict[str, Any]:
    """Calcula la correlacion de Pearson entre edad del cliente y venta total."""
    return correlacion_edad_venta()


@mcp.tool()
def consultar_asociacion_genero_metodo_pago() -> dict[str, Any]:
    """Calcula la asociacion entre genero y metodo de pago usando tabla de contingencia y Cramer's V."""
    return asociacion_genero_metodo_pago()


@mcp.tool()
def consultar_asociacion_boletin_vale() -> dict[str, Any]:
    """Calcula la asociacion entre clientes que usan boletin y clientes que usan vale."""
    return asociacion_boletin_vale()


@mcp.tool()
def consultar_resumen_puntos_2_al_6() -> dict[str, Any]:
    """Devuelve un resumen integrado de los puntos 2 al 6 del alcance de la practica."""
    return resumen_puntos_2_al_6()


@mcp.tool()
def generar_graficas_requeridas(
    directorio_salida: str = "output/visualizaciones",
    formato: str = "png",
) -> dict[str, Any]:
    """Genera las graficas requeridas para el informe y devuelve las rutas creadas.

    Formatos permitidos: png, pdf o ambos.
    """
    if formato not in {"png", "pdf", "ambos"}:
        return {"ok": False, "mensaje": "Formato invalido. Use png, pdf o ambos."}
    archivos = exportar_visualizaciones(
        archivo_datos=Path("data/processed/ventas_online_2025_limpio.csv"),
        directorio_salida=Path(directorio_salida),
        formato=formato,
    )
    return {
        "ok": True,
        "directorio_salida": directorio_salida,
        "archivos": {nombre: str(ruta) for nombre, ruta in archivos.items()},
    }


def main() -> None:
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
