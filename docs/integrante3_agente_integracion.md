# Integrante 3 - Agente conversacional e integracion MCP

## Alcance realizado

La parte del integrante 3 implementa la capa conversacional solicitada en la practica.
El objetivo es que el usuario pueda preguntar en lenguaje natural por los resultados de
los puntos 2 al 6 y que el agente responda usando herramientas deterministicas del MCP.

Se agregaron los siguientes componentes:

- `src/sog2/business.py`: funciones de negocio para estadisticas, tendencias,
  segmentacion, correlaciones y resumen del alcance.
- `src/sog2/server.py`: herramientas MCP expuestas al agente conversacional.
- `src/sog2/adk_agent/agent.py`: agente de Google ADK configurado con Gemini Flash.
- `src/sog2/visualizations.py`: graficas alineadas con los campos del enunciado.

## Modelo configurado

El agente usa Google ADK con el modelo `gemini-flash-latest` por defecto. Se puede
cambiar con la variable de entorno:

```bash
SOG2_AGENT_MODEL=gemini-flash-latest
```

La URL del MCP se configura con:

```bash
SOG2_MCP_URL=http://127.0.0.1:8080/mcp
```

## Herramientas MCP de negocio

El MCP expone herramientas para:

- verificar la conexion con PostgreSQL;
- calcular estadisticas basicas de variables numericas;
- consultar ventas por mes;
- identificar mes de mayor venta y mes de menor venta;
- consultar distribucion por metodo de pago;
- consultar ventas pagadas en efectivo;
- consultar distribucion por navegador, navegador mas usado y menos usado;
- consultar uso mensual de boletin y vale;
- segmentar por edad;
- segmentar por genero;
- segmentar por boletin, vale y combinacion boletin-vale;
- calcular correlacion edad-venta total;
- calcular asociacion genero-metodo de pago;
- calcular asociacion boletin-vale;
- generar las graficas requeridas;
- devolver un resumen integrado de los puntos 2 al 6.

## Ejecucion local

Primero se instalan las dependencias:

```bash
python -m pip install -e .
```

Luego se levanta la base y el MCP:

```bash
set POSTGRES_PASSWORD=<CONTRASENA_LOCAL>
docker-compose up -d db
docker-compose exec -T db psql -U postgres -d ventas_online -f sql/001_esquema.sql
docker-compose exec -T db psql -U postgres -d ventas_online -f sql/002_permisos.sql
docker-compose exec -T db psql -U postgres -d ventas_online -f sql/003_carga.sql
docker-compose build mcp
docker-compose up -d mcp
```

La salud del MCP se valida con:

```bash
curl http://127.0.0.1:8080/health
```

Para abrir el agente en ADK Web:

```bash
set SOG2_MCP_URL=http://127.0.0.1:8080/mcp
set SOG2_AGENT_MODEL=gemini-flash-latest
adk web src/sog2
```

En Windows, si aparece un error de recarga del servidor, usar:

```bash
adk web src/sog2 --no-reload
```

## Prompts sugeridos para evidencias

1. Calcule media, mediana y moda de venta total.
2. Cual fue el mes con mayor venta y el mes con menor venta?
3. Cual fue el navegador mas usado y cual fue el menos popular?
4. Cuantas ventas fueron pagadas en efectivo?
5. Muestre el uso mensual de boletines y vales.
6. Agrupe los clientes por edad y explique sus patrones de compra.
7. Compare el comportamiento de compra entre generos.
8. Existe relacion entre edad y venta total?
9. Existe asociacion entre genero y metodo de pago?
10. Genere las graficas requeridas para el informe.

## Comparacion con calculos reales

Para validar el comportamiento del agente se deben comparar sus respuestas contra los
resultados de las herramientas MCP o contra consultas directas a PostgreSQL. En la prueba
local con el CSV limpio se obtuvieron, entre otros, estos valores:

| Calculo | Resultado |
|---|---:|
| Registros analizados | 1,003 |
| Media de venta total | 1,093.4795 |
| Mediana de venta total | 1,146.42 |
| Suma de venta total | 1,096,759.94 |
| Mes con mayor venta | Octubre |
| Venta total en octubre | 121,466.66 |
| Mes con menor venta | Enero |
| Venta total en enero | 66,796.10 |
| Navegador mas usado | Navegador 3 |
| Transacciones de Navegador 3 | 217 |
| Navegador menos popular valido | Navegador 1 |
| Transacciones de Navegador 1 | 160 |
| Ventas en efectivo | 290 |
| Venta total en efectivo | 317,180.70 |
| Correlacion edad-venta | 0.010023 |
| Asociacion boletin-vale, Cramer's V | 0.006964 |

La respuesta del agente debe coincidir con estos calculos cuando se le hagan las mismas
preguntas. Si el texto cambia, los valores numericos no deben cambiar.

## Respuesta 8.e

Implementar un chat conversacional de IA si afectaria positivamente a la empresa para
entregar el analisis de datos en el futuro, siempre que el chat se conecte a herramientas
confiables y no responda solo con su conocimiento general. El beneficio principal es que
usuarios no tecnicos podrian consultar ventas, tendencias, segmentos y correlaciones en
lenguaje natural, sin escribir SQL ni ejecutar scripts de Python. Esto reduce el tiempo
entre una pregunta de negocio y una respuesta util para tomar decisiones. Tambien permite
reutilizar los mismos calculos oficiales mediante el MCP, evitando que cada persona cree
su propia version de las metricas.

El chat puede ayudar a que gerentes, analistas y personal operativo obtengan resultados
rapidos sobre meses de mayor venta, metodos de pago, navegadores preferidos, boletines,
vales y comportamiento por segmento. Ademas, puede generar graficas bajo demanda para
presentaciones o revisiones internas. Sin embargo, el impacto no es automaticamente
positivo si no existe control de calidad. El agente debe validar sus respuestas contra la
base de datos y las funciones de negocio, registrar evidencias, respetar permisos y avisar
cuando una pregunta no puede contestarse con los datos disponibles. Tambien se debe
evitar que invente conclusiones sobre costos, rentabilidad o satisfaccion cuando el
dataset no contiene esas variables.

En conclusion, el chat conversacional mejora la velocidad, accesibilidad y continuidad
del analisis, pero debe considerarse una interfaz de consulta sobre datos verificados, no
un sustituto de la limpieza, modelado, validacion y criterio del analista.

## Conclusion del integrante 3

La integracion del agente conversacional demuestra que el valor del analisis no depende
solo de calcular metricas, sino tambien de hacerlas accesibles para quienes toman
decisiones.
El uso de Google ADK permite construir una interfaz conversacional ordenada, donde el
modelo interpreta la pregunta del usuario y selecciona herramientas especificas.
El MCP funciona como una capa intermedia que protege la logica de negocio y evita que el
agente consulte la base de datos de forma improvisada.
Esta separacion es importante porque mantiene los calculos oficiales en funciones
reutilizables y verificables.
Las herramientas creadas cubren el analisis exploratorio, las tendencias, la
segmentacion, la correlacion y la generacion de graficas.
Con esto se cumple el requisito de que los puntos 2 al 6 puedan solicitarse mediante el
chat de IA.
El agente no necesita acceso directo a las tablas internas, ya que puede trabajar por
medio del MCP y de la vista analitica preparada para consulta.
Esta decision reduce riesgos de seguridad y facilita auditar que informacion se entrega
al usuario.
La configuracion con Gemini Flash favorece respuestas rapidas y suficientes para una
practica academica de analisis de ventas.
Al mismo tiempo, las respuestas importantes no quedan en manos del modelo, sino de
calculos deterministas.
La comparacion contra resultados reales permite detectar desviaciones entre lo que el
chat dice y lo que la base contiene.
Esta validacion es necesaria porque un agente puede redactar bien incluso cuando un dato
esta mal interpretado.
Las graficas generadas complementan las respuestas numericas y ayudan a presentar los
hallazgos de forma clara.
La documentacion del agente, del MCP y de las pruebas facilita que otro integrante pueda
reproducir el funcionamiento.
Tambien permite que el proyecto sea desplegado localmente o en la nube con cambios
minimos en variables de entorno.
El enfoque implementado deja una base extensible para agregar nuevas preguntas de
negocio en futuras cargas de datos.
Si la empresa agrega datos de productos, costos, inventario o satisfaccion, el MCP puede
crecer sin redisenar todo el chat.
La principal limitacion sigue siendo el contenido del dataset, no la interfaz
conversacional.
Por eso las respuestas deben indicar cuando una conclusion requiere informacion
adicional.
En general, la integracion convierte el analisis en una herramienta consultable,
reproducible y mas cercana al uso diario de la empresa.

## Recomendaciones del integrante 3

1. Mantener el MCP como unica fuente de herramientas del agente y agregar nuevas
   metricas mediante funciones probadas antes de exponerlas al chat. Esto reduce el
   riesgo de respuestas inventadas o calculos inconsistentes.

2. Crear un conjunto fijo de preguntas de validacion para cada nueva carga de datos,
   comparando la respuesta del agente contra SQL o Python. La empresa deberia guardar
   esas evidencias antes de usar el chat para decisiones operativas.
