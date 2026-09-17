from __future__ import annotations

import logging
import os
from typing import Any

from mcp.server.fastmcp import FastMCP
from starlette.requests import Request
from starlette.responses import JSONResponse

from sog2.database import verificar_postgresql


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


# Aqui van las herramientas de negocio que se agreguen despues.


def main() -> None:
    mcp.run(transport="streamable-http")


if __name__ == "__main__":
    main()
