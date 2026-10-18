# Proceso de analisis y metodologia

## Proceso de analisis

### Enfoque paso a paso para limpiar y preparar los datos

El proceso inicio con la revision del archivo `ventas_online_2025.csv`, el cual contenia
1,008 filas y 12 columnas relacionadas con clientes, ventas, compras, fechas, metodos de
pago, navegador, boletin y uso de vale. Antes de hacer cualquier calculo se definio que
la preparacion debia ser reproducible, por lo que se implemento un script de limpieza en
Python y no una edicion manual del CSV.

Primero se verifico que el archivo tuviera exactamente las columnas esperadas por el
enunciado: `Id_cliente`, `Edad`, `Genero`, `Venta_total`, `N_Compras`, `FechaCompra`,
`MontoCompra`, `MetodoPago`, `Tiempo`, `Navegador`, `Boletin` y `Vale`. Luego se
identificaron duplicados exactos. Solo se eliminaron las filas que repetian los 12
valores originales, para evitar borrar compras que compartieran cliente pero tuvieran
montos o fechas distintas. Con ese criterio se eliminaron 5 duplicados exactos y se
conservaron 1,003 registros limpios.

Despues se normalizaron los tipos de datos. Los identificadores de cliente y el numero de
compras se convirtieron a enteros. Las variables monetarias `Venta_total` y
`MontoCompra` se convirtieron a valores decimales, limpiando simbolos, espacios, comas,
comillas y formatos mixtos. Las fechas se estandarizaron al formato `YYYY-MM-DD`,
aceptando distintos formatos presentes en la fuente. Las variables codificadas se
validaron contra los dominios del enunciado: genero `0` masculino y `1` femenino; metodo
de pago `0` efectivo, `1` tarjeta de credito y `2` tarjeta de debito; navegador `0`
tienda fisica y `1` a `4` navegadores digitales; boletin y vale como valores booleanos.

Los valores faltantes o fuera de dominio no se reemplazaron por ceros ni por promedios.
Se conservaron como nulos para distinguir un dato realmente ausente de un valor valido.
Tambien se conservaron montos negativos porque podrian representar devoluciones, ajustes
o registros contables especiales. En lugar de eliminarlos sin evidencia, se marcaron como
incidencias de calidad. Cada fila conserva una columna de problemas de calidad para
facilitar auditoria posterior.

Una vez generado el CSV limpio, se preparo el modelo relacional en PostgreSQL. Se crearon
esquemas separados para `staging`, `core`, `analytics` y `audit`. El esquema `staging`
recibe los datos limpios en formato texto; `core` almacena los datos tipados y los
catalogos; `analytics` contiene la vista estable que usan las consultas y el MCP; y
`audit` registra cargas e incidencias. La tabla principal `core.ventas_online` usa una
llave tecnica porque `Id_cliente` no es unico en el archivo. Finalmente, la vista
`analytics.ventas_detalle` integra las etiquetas de catalogos y los campos derivados de
fecha para facilitar el analisis.

### Decisiones tomadas durante el analisis exploratorio

Durante el analisis exploratorio se decidio trabajar sobre los datos limpios y no sobre
el archivo original. Esta decision evita que formatos monetarios inconsistentes,
duplicados exactos o categorias invalidas afecten los resultados. Tambien se decidio que
las metricas del agente y del informe debian salir de funciones reutilizables, no de
calculos manuales aislados. Por eso se implementaron herramientas de negocio en el MCP
para consultar estadisticas, tendencias, segmentaciones y correlaciones.

Las primeras metricas exploratorias fueron conteos generales, media, mediana, moda,
minimos, maximos y suma de variables numericas como `venta_total`, `monto_compra`,
`numero_compras`, `edad` y `tiempo`. Luego se analizaron ventas por mes para identificar
periodos de mayor y menor actividad. Tambien se agruparon las ventas por metodo de pago,
navegador, boletin y vale, ya que esas variables estan directamente relacionadas con los
puntos solicitados en la practica.

Para tendencias, se compararon las ventas mensuales y se identificaron los meses con
mayor y menor venta total. Para segmentacion, se agruparon clientes por rangos de edad,
por genero y por uso de promociones. Para correlacion, se calculo la relacion entre edad
y venta total mediante correlacion de Pearson, y se usaron tablas de contingencia con
Cramer's V para asociaciones categoricas como genero contra metodo de pago y boletin
contra vale.

Otra decision importante fue no afirmar conclusiones sobre rentabilidad, costos o
satisfaccion directa cuando el dataset no contiene esas variables. El archivo permite
analizar ventas y comportamiento de compra, pero no incluye costos, productos, margenes,
inventario, encuestas o calificaciones de clientes. Por esa razon, las interpretaciones
se limitaron a lo que los datos pueden respaldar.

### Desafios encontrados y como se superaron

Uno de los primeros desafios fue la calidad del archivo original. Habia fechas en varios
formatos, montos con simbolos y separadores distintos, categorias invalidas, valores
faltantes y duplicados exactos. Esto se supero creando reglas de limpieza explicitas y
reproducibles. En lugar de corregir a mano, se implemento un proceso que genera siempre
el mismo CSV limpio y un reporte de calidad.

Otro desafio fue que `Id_cliente` no podia usarse como llave primaria porque algunos
clientes aparecian mas de una vez con informacion diferente. Para resolverlo se diseno
una llave tecnica `registro_id` y se conservo `fila_origen` para rastrear cada registro
hasta el CSV original. Asi se evita perder informacion valida o forzar una unicidad que
el dataset no cumple.

Tambien hubo desafios al cargar la base en Cloud SQL. Inicialmente solo existia la tabla
de `staging`, por lo que el MCP no podia calcular estadisticas porque la vista
`analytics.ventas_detalle` no tenia datos. Se identifico que faltaban los esquemas
`core`, `analytics` y `audit`, asi como la carga final hacia `core.ventas_online`. Para
resolverlo se ejecutaron los scripts `001_esquema.sql`, `002_permisos.sql` y
`003_carga.sql` en el orden correcto. Ademas, se ajustaron permisos y propietarios de
esquemas existentes para que los roles internos pudieran crear tablas, cargar datos y
consultar la vista analitica.

El agente conversacional tambien presento un desafio: si no se obliga al modelo a usar
herramientas, puede inventar cifras. Para resolverlo se creo una herramienta MCP
especifica para consultar el total de registros y se reforzaron las instrucciones del
agente para que no responda cantidades, promedios, tendencias ni correlaciones sin llamar
al MCP. De esta forma, el chat funciona como una interfaz conversacional sobre calculos
verificados y no como una fuente libre de respuestas.

Finalmente, se encontro que el MCP podia estar activo pero conectado a una base sin datos
o con credenciales incorrectas. Para superar esto se agregaron validaciones directas de
conteos y pruebas de conexion. La verificacion final debe comprobar que
`staging.ventas_online_limpio`, `core.ventas_online` y `analytics.ventas_detalle` tengan
1,003 registros.

## Metodologia

### Seleccion de visualizaciones

Las visualizaciones se seleccionaron segun los objetivos del enunciado y el tipo de
variable analizada. Se priorizaron graficas simples, interpretables y adecuadas para un
informe de analista junior. No se usaron graficas 3D ni efectos decorativos porque pueden
dificultar la lectura y no aportan valor al analisis.

Para mostrar la evolucion temporal de las ventas se eligio un grafico de linea de venta
total por mes. Este tipo de grafico permite observar picos, caidas y patrones de
estacionalidad durante 2025. Para comparar categorias como metodo de pago y navegador se
usaron graficos de barras, ya que permiten comparar rapidamente cantidades o montos entre
grupos discretos.

El uso de boletin y vale se represento con barras mensuales, porque el objetivo era
identificar en que meses se usaron mas estas promociones. Para analizar la posible
relacion entre edad y venta total se uso un grafico de dispersion, ya que cada punto
representa una transaccion y permite observar si existe una tendencia visual entre ambas
variables. Para comparar patrones por genero y navegador se uso una grafica de barras
agrupadas, porque permite contrastar varios segmentos al mismo tiempo.

Tambien se incluyeron visualizaciones complementarias como distribucion de edades y
matriz de correlacion. La distribucion de edades ayuda a entender la composicion de los
clientes, mientras que la matriz de correlacion ofrece una vista general de relaciones
entre variables numericas. Todas las graficas usan titulos en espanol, ejes etiquetados,
unidades monetarias cuando corresponde y una paleta consistente.

La seleccion final cubre los puntos solicitados por la practica: distribucion de ventas
por mes, metodo de pago, navegador, boletin y vale; analisis de segmentos; y relacion
entre edad y venta total. Estas visualizaciones se generaron desde funciones de Python
para que puedan reproducirse cuando cambien los datos o se necesiten evidencias nuevas.
