# SOG2-2S26-Grupo15

Base tecnica para la practica de ventas online 2025. Incluye la limpieza del CSV,
el modelo relacional, la carga reproducible en PostgreSQL, un servidor MCP y un agente
conversacional con Google ADK.

## Implementacion incluida

- CSV original revisado: 1,008 filas y 12 columnas.
- CSV limpio: 1,003 filas; se eliminaron 5 duplicados exactos.
- PostgreSQL 16 probado con 1,003 registros cargados.
- Roles internos de lectura, carga, migracion y MCP probados.
- Servidor MCP probado mediante Streamable HTTP.
- Herramienta `verificar_conexion_postgresql` probada con respuesta estructurada.
- Herramientas MCP de negocio para estadisticas, tendencias, segmentacion,
  correlaciones y graficas.
- Agente conversacional Google ADK configurado con Gemini Flash e integrado al MCP.
- Arquitectura y procedimiento de despliegue definidos para GCP.

## Estructura

```text
data/processed/             CSV limpio y reporte de calidad
docs/documentacion_practica.md  Documentacion completa de la practica
docs/integrante3_agente_integracion.md  Documentacion del agente y MCP
sql/                        Esquema, permisos y carga
src/sog2/cleaning.py        Limpieza reproducible del CSV
src/sog2/database.py        Conexion local o Cloud SQL
src/sog2/business.py        Calculos de negocio expuestos al MCP
src/sog2/server.py          Servidor MCP
src/sog2/adk_agent/         Agente conversacional Google ADK
compose.yaml                PostgreSQL y MCP para desarrollo local
Dockerfile                  Imagen del servidor MCP
```

## Ejecucion local

La limpieza no instala librerias:

```bash
python3 src/sog2/cleaning.py
```

La contrasena local se define en la terminal y no se guarda en el repositorio.

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

Para usar el agente ADK con el MCP local:

```bash
python -m pip install -e .
export SOG2_MCP_URL=http://127.0.0.1:8080/mcp
export SOG2_AGENT_MODEL=gemini-flash-latest
adk web src/sog2
```

En Windows se puede usar `set` en lugar de `export`. Si ADK Web presenta problemas con
la recarga automatica en Windows, ejecutar:

```bash
adk web src/sog2 --no-reload
```

Para generar graficas sin abrir el agente:

```bash
sog2-graficas --formato ambos --salida output/visualizaciones
```

Para ver los servicios y sus registros:

```bash
docker-compose ps
docker-compose logs --tail=100 mcp
```

Para detenerlos sin borrar la base local:

```bash
docker-compose stop
```

## Documentacion principal

- [Documentacion completa de la practica](docs/documentacion_practica.md)
- [Integrante 3: agente e integracion MCP](docs/integrante3_agente_integracion.md)

El documento principal reune las reglas de limpieza, el diccionario, el modelo
relacional, la infraestructura, el despliegue, el contrato de integracion, las
validaciones y el contenido del informe final.
