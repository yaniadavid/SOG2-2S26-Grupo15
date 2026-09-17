# SOG2-2S26-Grupo15

Base técnica para la práctica de ventas online 2025. Incluye la limpieza del CSV,
el modelo relacional, la carga reproducible en PostgreSQL y un servidor MCP base.

## Implementación incluida

- CSV original revisado: 1,008 filas y 12 columnas.
- CSV limpio: 1,003 filas; se eliminaron 5 duplicados exactos.
- PostgreSQL 16 probado con 1,003 registros cargados.
- Roles internos de lectura, carga, migración y MCP probados.
- Servidor MCP probado mediante Streamable HTTP.
- Herramienta `verificar_conexion_postgresql` probada con respuesta estructurada.
- Arquitectura y procedimiento de despliegue definidos para GCP.

## Estructura

```text
data/processed/             CSV limpio y reporte de calidad
docs/documentacion_practica.md  Documentación completa de la práctica
sql/                        Esquema, permisos y carga
src/sog2/cleaning.py        Limpieza reproducible del CSV
src/sog2/database.py        Conexión local o Cloud SQL
src/sog2/server.py          Servidor MCP base
compose.yaml                PostgreSQL y MCP para desarrollo local
Dockerfile                  Imagen del servidor MCP
```

## Ejecución local

La limpieza no instala librerías:

```bash
python3 src/sog2/cleaning.py
```

La contraseña local se define en la terminal y no se guarda en el repositorio.

```bash
export POSTGRES_PASSWORD=<CONTRASENA_LOCAL>
docker-compose up -d db
docker-compose exec -T db psql -U postgres -d ventas_online -f sql/001_esquema.sql
docker-compose exec -T db psql -U postgres -d ventas_online -f sql/002_permisos.sql
docker-compose exec -T db psql -U postgres -d ventas_online -f sql/003_carga.sql
docker-compose build mcp
docker-compose up -d mcp
curl http://127.0.0.1:8080/health
```

En equipos con Docker Compose moderno se puede reemplazar `docker-compose` por
`docker compose`.

Para ver los servicios y sus registros:

```bash
docker-compose ps
docker-compose logs --tail=100 mcp
```

Para detenerlos sin borrar la base local:

```bash
docker-compose stop
```

## Documentación principal

- [Documentación completa de la práctica](docs/documentacion_practica.md)

El documento reúne las reglas de limpieza, el diccionario, el modelo relacional, la
infraestructura, el despliegue, el contrato de integración, las validaciones y el
contenido del informe final.
