from __future__ import annotations

import atexit
import os
from functools import lru_cache
from typing import Any

from google.cloud.sql.connector import Connector, IPTypes
from sqlalchemy import URL, Engine, create_engine, text


_connector: Connector | None = None


def _variable_requerida(nombre: str) -> str:
    valor = os.getenv(nombre, "").strip()
    if not valor:
        raise RuntimeError(f"Falta la variable {nombre}.")
    return valor


def _conexion_local() -> Engine:
    url = URL.create(
        drivername="postgresql+pg8000",
        username=_variable_requerida("DB_USER"),
        password=_variable_requerida("DB_PASSWORD"),
        host=os.getenv("DB_HOST", "127.0.0.1"),
        port=int(os.getenv("DB_PORT", "5432")),
        database=os.getenv("DB_NAME", "ventas_online"),
    )
    return create_engine(url, pool_pre_ping=True, pool_size=3, max_overflow=2)


def _conexion_cloud_sql() -> Engine:
    global _connector
    _connector = Connector(refresh_strategy="LAZY")
    tipo_ip = IPTypes.PRIVATE if os.getenv("DB_PRIVATE_IP") == "1" else IPTypes.PUBLIC

    def obtener_conexion() -> Any:
        return _connector.connect(
            _variable_requerida("INSTANCE_CONNECTION_NAME"),
            "pg8000",
            user=_variable_requerida("DB_IAM_USER"),
            db=os.getenv("DB_NAME", "ventas_online"),
            enable_iam_auth=True,
            ip_type=tipo_ip,
        )

    return create_engine(
        "postgresql+pg8000://",
        creator=obtener_conexion,
        pool_pre_ping=True,
        pool_size=3,
        max_overflow=2,
    )


@lru_cache(maxsize=1)
def obtener_motor() -> Engine:
    # Aqui se elige la conexion local o la de Cloud SQL.
    if os.getenv("INSTANCE_CONNECTION_NAME"):
        return _conexion_cloud_sql()
    return _conexion_local()


def verificar_postgresql() -> dict[str, Any]:
    with obtener_motor().connect() as conexion:
        datos = conexion.execute(
            text(
                "SELECT current_database() AS base_datos, "
                "current_user AS usuario, CURRENT_TIMESTAMP AS fecha_servidor"
            )
        ).mappings().one()
        total = conexion.execute(
            text("SELECT COUNT(*) FROM analytics.ventas_detalle")
        ).scalar_one()

    return {
        "ok": True,
        "base_datos": datos["base_datos"],
        "usuario": datos["usuario"],
        "fecha_servidor": datos["fecha_servidor"].isoformat(),
        "registros_disponibles": total,
    }


def _cerrar_conexiones() -> None:
    if obtener_motor.cache_info().currsize:
        obtener_motor().dispose()
    if _connector is not None:
        _connector.close()


atexit.register(_cerrar_conexiones)

