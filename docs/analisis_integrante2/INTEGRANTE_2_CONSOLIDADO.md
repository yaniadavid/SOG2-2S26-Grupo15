# Documento Consolidado - Integrante 2
## Sistemas Organizacionales y Gerenciales 2
### Análisis de Ventas Online 2025 - Grupo 15

---

## 1. Introducción

Este documento contiene el análisis detallado de las preguntas estratégicas 8.a y 8.b de la práctica, junto con conclusiones profesionales y recomendaciones basadas en el análisis de 1,003 transacciones de ventas online del año 2025. El análisis se fundamenta en métodos estadísticos rigurosos, calidad de datos validada y decisiones estratégicas documentadas.

La documentación técnica incluye especificaciones completas del módulo de análisis estadístico (`analysis_engine.py`) y visualizaciones de datos (`visualizations.py`).

---

## 2. Respuesta a Pregunta 8.a: Diferenciación frente a la Competencia

### ¿Cómo podrían los insights obtenidos ayudar a diferenciarse de la competencia?

El análisis de datos de ventas online 2025 revela patrones estratégicos que permiten diferenciación competitiva en múltiples dimensiones operacionales y comerciales.

**Segmentación Precisa de Canales de Distribución**

El análisis muestra una distribución heterogénea entre canales: la tienda física y los navegadores digitales presentan patrones de compra diferenciados en volumen, valor promedio de transacción y métodos de pago preferidos. Esta distinción permite optimizar la inversión en infraestructura y marketing según el rendimiento real de cada canal. Mientras la competencia puede operar con una visión genérica de "canal online", el análisis permite identificar qué navegador específico genera mayor valor, qué segmento de edad utiliza preferentemente cada plataforma y cuál es la tasa de conversión efectiva. Esta ventaja competitiva se traduce en decisiones de presupuesto más eficientes y capacidad de escalar canales rentables sin inversión ciega.

**Comportamiento Diferenciado por Género y Edad**

Los datos permiten segmentación detallada por género y grupo etario. El análisis revelará si las mujeres tienen mayor lealtad a promotiones específicas (boletín, vale) en comparación con hombres, o si ciertos rangos de edad muestran patrones de gasto consistentemente superiores. Esta inteligencia permite personalizar campañas de marketing, diseñar productos y servicios dirigidos a segmentos de alto valor, y ajustar mensajes promocionales según receptividad demostrada. La competencia que utiliza un enfoque generalista perderá oportunidades de captar clientes de alto potencial con mensajes irrelevantes.

**Optimización de Políticas de Promoción**

El análisis del impacto del boletín y el vale en el volumen y valor de venta permite responder si estas promociones realmente generan ingresos adicionales o simplemente canibalizan ventas que habrían ocurrido sin descuento. Si se identifica que los boletines aumentan compra en segmentos específicos (por ejemplo, mujeres de 30-50 años) pero no generan retorno en otros, la empresa puede dirigir promociones de forma quirúrgica. La competencia que envía promociones masivas sin discriminación desperdicia presupuesto en clientes insensibles a descuentos y aliena a clientes de valor con comunicaciones irrelevantes.

**Análisis de Preferencia en Métodos de Pago**

La distribución de métodos de pago (efectivo, crédito, débito) permite estimar costos de operación diferenciados: efectivo requiere manejo físico, conciliación manual y riesgo de pérdida; tarjeta de crédito implica comisiones bancarias altas; tarjeta de débito tiene costos menores. Si el análisis demuestra que una sucursal física o navegador específico concentra pagos en efectivo, la empresa puede negociar soluciones de seguridad o implementar incentivos para migración a métodos digitales de menor costo. Esto genera eficiencia operativa que competidores sin análisis no pueden lograr.

**Posicionamiento en Temporalidad y Demanda Estacional**

El análisis de ventas mes a mes permite identificar meses de pico (Navidad, descuentos estacionales) y meses débiles. La empresa puede prepararse con inventario y personal en picos, mientras reduce operación en valles. La competencia que no ajusta operación a realidad de demanda incurre en costos innecesarios durante depresión y pierde oportunidades de captura durante picos. Con análisis, la empresa puede también identificar oportunidades de contracyclical: promociones específicas en meses débiles dirigidas a clientes identificados como sensibles a descuentos.

---

## 3. Respuesta a Pregunta 8.b: Decisiones Estratégicas para Aumentar Ventas y Satisfacción del Cliente

### ¿Qué decisiones estratégicas podrían tomarse basándose en este análisis para aumentar las ventas y la satisfacción del cliente?

Las decisiones estratégicas derivadas del análisis se estructuran en tres categorías: optimización de canales, personalización de ofertas, y mejora de experiencia.

**Decisión 1: Inversión Diferenciada en Canales Según Rendimiento**

Si el análisis demuestra que navegador específico (por ejemplo, Navegador 2) genera 35% del volumen pero 45% de ingresos, la decisión es asignar recursos de marketing digital y mejora UX preferentemente a ese canal. Inversamente, si Navegador 1 tiene bajo rendimiento a pesar de alto tráfico (bajo valor promedio de transacción), la decisión es reconfigurar interfaz, mejorar recomendaciones de producto o implementar bundles de mayor margen. La inversión en tienda física debe compararse contra canales digitales: si tienda física genera 20% de ventas con 40% de costos, la decisión puede ser optimizar operación antes de expandir, o invertir en e-commerce como canal principal. Esto aumenta ventas concentrando recursos en canales de mayor retorno y satisfacción mejora porque el cliente de cada canal recibe experiencia optimizada para su contexto.

**Decisión 2: Campañas de Retención Segmentadas por Patrón de Compra**

Identificar que clientes que utilizan boletín realizan 4.2 compras al año versus 2.1 en no suscriptores sugiere decisión de impulsar suscripción al boletín, pero solo en segmentos donde demostró efectividad. Si mujeres de 35-50 años en Navegador 2 muestran 60% de compra con boletín versus 30% de baseline, la decisión es asignar presupuesto de email marketing prioritariamente a ese segmento. Crear ofertas personalizadas para clientes que no compran hace 60 días, segmentadas por método de pago preferido (oferta de cashback para usuarios de débito, descuento directo para efectivo). Satisfacción aumenta porque el cliente recibe comunicación relevante, y ventas crecen por reducción de churn (pérdida de clientes) e incremento de frecuencia de compra.

**Decisión 3: Arquitectura de Promociones Basada en ROI por Segmento**

Si el análisis demuestra que vale es utilizado principalmente por clientes de bajo valor promedio de transacción (quizás indicando sensibilidad a precio), la decisión es reducir profundidad de descuento en vale o eliminarlo para este segmento, sustituyendo por programa de puntos que incentiva compra repetida. Inversamente, si vale es usado por clientes de alto valor buscando diversificar compra (quizás compraron con crédito, ahora prueban con descuento), la decisión es expandir vale con mayor profundidad. Implementar teste A/B: ofrecer a 50% de nuevo segmento descuento directo, a otro 50% programa de lealtad acumulativo. Medir cuál genera mayor lifetime value (valor total esperado del cliente durante su relación con la empresa). Satisfacción sube porque promoción es percibida como relevante, no como "descuento genérico", y rentabilidad mejora porque gasto en promoción se concentra en clientes que responden.

**Decisión 4: Optimización de Mix Operacional Tienda Física versus Online**

Si tienda física muestra mayores compras por cliente (número de artículos) pero menor valor total (porque cliente adquiere items de menor precio), la decisión es diseñar la tienda física como hub de impulso y experiencia: inventario de muestras, asesoría personal, bundling, mientras online es canal de eficiencia: búsqueda rápida, envío. Alternativamente, si online es dominante, decisión es escala virtual: mejorar recomendación algorítmica, reducir fricción de checkout, implementar marketplace con terceros. Satisfacción aumenta porque cada canal juega su fortaleza, y ventas crecen por eficiencia operacional.

**Decisión 5: Expansión a Segmentos Subutilizados con Alto Potencial**

El análisis de edad permitirá identificar grupos demográficos con baja penetración actual pero alto potencial de gasto. Por ejemplo, si clientes de 60+ representan 8% del volumen pero 15% de ingresos, la decisión es crear línea de productos orientada a ese segmento, considerar asociaciones con programas de adultos mayores, y asignar presupuesto de marketing a canales que alcancen ese grupo (por ejemplo, Facebook en lugar de TikTok). Si clientes de 18-25 tienen alto volumen pero bajo valor, decisión es educación sobre productos premium, crear aspiración de marca, y programas de referencia para viralización. Satisfacción aumenta porque cliente recibe productos diseñados para su necesidad, y ventas escalan por captura de segmentos de alto potencial subutilizados.

---

## 4. Conclusiones

### Conclusión 1: Preparación de Datos como Base de Decisiones Confiables

La implementación de un proceso riguroso de limpieza y validación de datos es el fundamento de cualquier decisión estratégica confiable en análisis de ventas. El conjunto de datos original (1,008 transacciones) contenía heterogeneidad en formatos monetarios (símbolos de dólar, separadores de miles variables, comas como decimales), fechas con múltiples notaciones (AAAA/MM/DD, MM/DD/AAAA, DD-MM-AAAA), valores faltantes no indicados explícitamente, y categorías con variaciones textuales ("Sí", "Si", "No"). La eliminación de únicamente cinco duplicados exactos mediante criterio objetivo permitió conservar 99.5% del volumen mientras se garantizaba integridad de datos. La preservación de valores negativos en ventas (que podrían representar devoluciones o ajustes) reconoce la complejidad del negocio real sin imponer suposiciones simplistas. El tratamiento de valores nulos distingue entre ausencia de información (no capturado), respuesta negativa (boletín = 0), y categoría inválida (navegador fuera de rango 0-4). Esta precisión es crítica porque directivos que tomen decisiones sobre expansión de canales, inversión en promociones o redimensionamiento de personal requieren certidumbre de que números están libres de contaminación. La implementación de auditoría (registro de problemas de calidad por fila) permite rastrabilidad: si venta de cliente específico parece anomalía, es posible investigar si fue normalización de formato o genuina anomalía operacional. La documentación integrada de reglas de limpieza (20 reglas explícitas) asegura reproducibilidad: si nuevos datos llegan en 2026, se pueden aplicar exactas mismas reglas, permitiendo series de tiempo comparables. Modelos de datos relacionales con esquemas separados (staging para recepción temporal, core para datos definitivos, analytics para consultas, audit para trazabilidad) impiden que contaminación de una etapa afecte decisiones basadas en otra. Sin esta preparación, análisis que siga será construcción sobre arena: conclusiones bonitas estadísticamente pero inútiles operacionalmente.

### Conclusión 2: Ventaja Competitiva de Segmentación Granular sobre Decisiones Genéricas

La práctica industrial estándar es tomar decisiones agregadas: invertir X en marketing digital, ofrecer descuento del Y% a todos los clientes, dimensionar inventario en base a promedio histórico. El análisis realizado permite cambiar paradigma a decisión segmentada: invertir X en Navegador 2 (porque es canal de mayor ROI), ofrecer vale de profundidad A a clientes sensibles a precio pero descuento directo de B% a clientes insensibles, dimensionar inventario según predicción de demanda por mes y por categoría. Esta granularidad no es puramente teórica; tiene impacto financiero: si 40% del presupuesto de marketing se asignaba uniformemente pero análisis demuestra que Navegador 2 genera 3x retorno de Navegador 1, reasignar presupuesto a proporción demostrada aumenta retorno de marketing sin gasto incremental (eficiencia pura). Similarmente, si vale cuesta 15% de margen pero cliente típico sensible a vale gasta en total 40% menos que cliente sin promoción (es decir, vale canibaliza más de lo que genera), decisión es reducir profundidad o eliminar vale para ese segmento: mejora de margen de 15 a 5 puntos por cliente es incremento de 200% en rentabilidad por cliente si volumen se mantiene. Competidor que no tenga este análisis sigue regla de un tamaño único, incurriendo en eficiencia operacional menor. Satisfacción del cliente se beneficia porque comunicación y oferta de empresa es percibida como más relevante: cliente que recibe promoción porque análisis demostró que su segmento demográfico responde a ella se siente "entendido"; cliente que recibe promoción genérica puede percibirla como spam. A escala de 1,000+ clientes, diferencia de satisfacción impacta en Net Promoter Score (probabilidad de recomendación) y lifetime value (ingresos futuros por cliente). Conclusión es que segmentación granular, habilitada por análisis de datos de calidad, es multiplicador de ventaja competitiva.

---

## 5. Recomendaciones

### Recomendación 1: Implementar Cultura Continua de Validación de Datos

Establecer proceso mensual de validación donde analista verifica que nuevos datos cumplan exactamente las mismas 20 reglas aplicadas al dataset inicial. Crear alertas automáticas cuando proporción de valores nulos en campo específico supera histórico (por ejemplo, si método de pago nulo sube de 10% a 25%, investigar si cambió forma de captura). Implementar dashboard que reporte para cada carga: cantidad de filas rechazadas por regla, distribución de problemas de calidad, desviación estadística de nuevos datos versus baseline 2025. Beneficio: evita que decisiones futuras se basen en datos degradados. Mecanismo: asignar 4 horas mensuales de analista para revisión; costo bajo relativo a riesgo de decisión sobre datos malos.

### Recomendación 2: Pilotar Toma de Decisión Segmentada en Canal de Mayor Impacto Financiero

Identifica el navegador o canal de mayor proporción de ingresos (por ejemplo, si Navegador 2 genera 35% de ingresos totales). Ejecutar teste controlado por 60 días: en ese canal, dirigir promociones solo a segmentos demográficos donde análisis demuestra respuesta (por ejemplo, boletín solo a mujeres 35-50 años). En canales control, mantener promoción genérica actual. Medir: delta de ingresos entre teste y control, cambio en frecuencia de compra, cambio en valor promedio de transacción. Si teste genera delta positivo de 5%+ con gasto promocional igual, escalar a todos los canales. Si delta es negativo o neutral, entonces decisión es investigar por qué segmentación no mejoró resultado (quizás segmentación fue definida incorrectamente, o target fue insensible a oferta). Beneficio: valida hipótesis derivadas del análisis antes de comprometer presupuesto annual. Costo: marginal (requiere ajuste en sistemas de promoción e instrumentación de medición, típicamente 20-40 horas ingeniería).

---

## 6. Documentación Técnica

### 6.1 Módulo analysis_engine.py

#### Descripción General

El módulo `analysis_engine.py` proporciona funciones reutilizables y profesionales para análisis estadístico, segmentación, correlación y detección de tendencias en datos de ventas online.

**Características:**
- Funciones puras sin efectos secundarios
- Validación rigurosa de entrada
- Manejo robusto de errores
- Documentación completa con type hints
- Código testeable y modular

#### Tipos de Datos (Dataclasses)

**Estadisticas**

<<<<<<<< HEAD:docs/analisis_integrante2/INTEGRANTE_2_CONSOLIDADO.md
```python
@dataclass
class Estadisticas:
    cantidad: int
    media: float
    mediana: float
    desviacion_estandar: float
    minimo: float
    maximo: float
    rango: float
    percentil_25: float
    percentil_75: float
    rango_intercuartil: float
```

**CorrelacionVars**
========
Contiene estadísticas descriptivas de una variable numérica.

```python
@dataclass
class Estadisticas:
    cantidad: int                   # Número de observaciones
    media: float                    # Promedio aritmético
    mediana: float                  # Valor central
    desviacion_estandar: float      # Desviación estándar
    minimo: float                   # Valor mínimo
    maximo: float                   # Valor máximo
    rango: float                    # Max - Min
    percentil_25: float             # Cuartil inferior
    percentil_75: float             # Cuartil superior
    rango_intercuartil: float       # Q3 - Q1
```

**CorrelacionVars**

Contiene información de correlación entre dos variables.

```python
@dataclass
class CorrelacionVars:
    variable1: str                  # Nombre de la primera variable
    variable2: str                  # Nombre de la segunda variable
    coeficiente: float              # Correlación de Pearson (-1 a 1)
    tipo_relacion: str              # "fuerte positiva", "débil", etc.
    cantidad_pares: int             # Número de pares válidos
```

**Tendencia**

Contiene información sobre una tendencia temporal detectada.

```python
@dataclass
class Tendencia:
    variable: str                   # Nombre de la variable
    periodo: str                    # "mes", "trimestre", "anio"
    puntos_datos: int               # Número de puntos en serie temporal
    promedio_inicial: float         # Promedio del primer período
    promedio_final: float           # Promedio del último período
    cambio_porcentaje: float        # Cambio % del inicial al final
    direccion: str                  # "ascendente", "descendente", "estable"
```

#### Funciones Principales

**calcular_estadisticas()**

Calcula estadísticas descriptivas de un conjunto de números.

```python
def calcular_estadisticas(valores: Sequence[float]) -> Estadisticas:
```

Características:
- Calcula media, mediana, desviación estándar
- Detecta automáticamente valores NaN e infinito
- Trabaja con listas, tuplas, Series de pandas y arrays de numpy

**segmentar_datos()**

Segmenta datos por valores de una columna y calcula estadísticas.

**correlacionar_variables()**

Calcula la correlación de Pearson entre dos variables numéricas.

Clasificación de relaciones:
- **Fuerte positiva/negativa:** |r| > 0.8
- **Moderada positiva/negativa:** 0.5 < |r| ≤ 0.8
- **Débil positiva/negativa:** 0.2 < |r| ≤ 0.5
- **Muy débil o nula:** |r| ≤ 0.2

**detectar_tendencias()**

Detecta tendencias temporales en los datos.

Características:
- Detecta tendencias ascendentes, descendentes o estables
- Clasifica períodos automáticamente (mes, trimestre, año)
- Calcula cambio porcentual
- Umbral de estabilidad: 5%

#### Características de Diseño

1. **Funciones Puras**: No modifica el DataFrame original, retorna copias.
2. **Type Hints Completos**: Todas las funciones tienen anotaciones de tipos.
3. **Documentación Detallada**: Docstrings completos con Args, Returns, Raises.
4. **Validación Rigurosa**: Cada función valida sus inputs con mensajes descriptivos.

#### Caso de Uso Completo

```python
import pandas as pd
from sog2.analysis_engine import (
    calcular_estadisticas,
    segmentar_datos,
    correlacionar_variables,
)

df = pd.read_csv('ventas_online_2025_limpio.csv')

stats = calcular_estadisticas(df['venta_total'])
print(f"Venta promedio: ${stats.media:.2f}")

corr = correlacionar_variables(df, 'edad', 'venta_total')
print(f"Correlación: {corr.coeficiente:.3f}")
```

#### Instalación de Dependencias

```bash
pip install pandas numpy
```

---

### 6.2 Módulo visualizations.py

#### Panorama General

El módulo `visualizations.py` proporciona 8 tipos de gráficas diferentes diseñadas para análisis comprehensivo de datos de ventas online. Cada gráfica está optimizada para revelar diferentes aspectos de los datos mediante visualización académica profesional.

#### Gráfica 1: Distribución de Edades de Clientes

**Archivo**: `01_distribucion_edades.png/pdf`

**Tipo**: Histograma con indicadores estadísticos

**Función**: `grafica_distribucion_edades(df, titulo, color, bins, figsize)`

**Descripción**

Histograma que muestra la distribución de frecuencias de las edades de los clientes. Incluye líneas de referencia para media y mediana, permitiendo identificar patrones en la población.

**Características Técnicas**

- Bins: 20 (ajustable)
- Colores: Azul primario con borde negro
- Líneas de referencia: Media (púrpura) y Mediana (naranja)
- Validación: Excluye edades <= 0 o > 100

**Insights Típicos**

- Identifica grupos de edad dominantes
- Compara media y mediana para detectar asimetría
- Ayuda a segmentar campañas por edad
- Revela si hay distribución uniforme o concentrada

**Parámetros Personalizables**

```python
grafica_distribucion_edades(
    df=datos,
    titulo="Distribución de Edades",
    color="#2E86AB",  # Color personalizado
    bins=25,          # Más bins = más granularidad
    figsize=(12, 7)   # Tamaño de figura
)
```

#### Especificaciones de Exportación

**Formatos**

PNG: 
- Resolución: 300 DPI (profesional)
- Fondo: Blanco
- Compresión: Automática
- Uso: Presentaciones, reportes

PDF:
- Formato: Vectorial escalable
- Fondo: Blanco
- Tamaño: Automático
- Uso: Impresión, reportes formales
- Nota: Se genera también un PDF combinado con todas las gráficas

**Paleta de Colores Estándar**

```
Primario:     #2E86AB (Azul)
Secundario:   #A23B72 (Púrpura)
Terciario:    #F18F01 (Naranja)
Cuaternario:  #C73E1D (Rojo)
Quinto:       #6A994E (Verde)
Sexto:        #BC4749 (Rojo Oscuro)
```

**Estilos Académicos Aplicados**

- Fuente: sans-serif (sistema)
- Tamaño base: 10pt
- Títulos: 13pt, negrita, 20pt padding
- Etiquetas ejes: 11pt, negrita
- Grid: alfa 0.3, solo en necesario

#### Gráficas Adicionales Documentadas

1. **Gráfico de línea: Venta Total por Mes** - Permite identificar patrones de estacionalidad, meses pico, meses débiles. Eje X es mes (Enero a Diciembre 2025), eje Y es venta acumulada mensual en dólares. Línea continua permite visualizar tendencia.

2. **Gráfico de Barras: Distribución por Método de Pago** - Eje X es categoría (Efectivo, Tarjeta Crédito, Tarjeta Débito, Sin Dato), eje Y es cantidad de transacciones. Altura de barra indica prevalencia.

3. **Gráfico de Barras: Rendimiento por Navegador** - Eje X es navegador (Tienda Física, Nav 1, Nav 2, Nav 3, Nav 4), eje Y es venta total en dólares. Barras están coloreadas por navegador para distinguibilidad.

4. **Gráfico de Barras: Uso de Boletín por Mes** - Eje X es mes, eje Y es cantidad de compras con boletín activado. Apilación opcional por género permite ver si patrón es diferenciado.
>>>>>>>> origin/main:docs/analisis_integrante2/respue2.md

```python
@dataclass
class CorrelacionVars:
    variable1: str
    variable2: str
    coeficiente: float
    tipo_relacion: str
    cantidad_pares: int
```

<<<<<<<< HEAD:docs/analisis_integrante2/INTEGRANTE_2_CONSOLIDADO.md
**Tendencia**

```python
@dataclass
class Tendencia:
    variable: str
    periodo: str
    puntos_datos: int
    promedio_inicial: float
    promedio_final: float
    cambio_porcentaje: float
    direccion: str
```
========
6. **Gráfico de Dispersión: Edad versus Venta Total** - Cada punto es una transacción; posición horizontal es edad cliente, vertical es venta total. Permite identificar visualmente si clientes mayores gastan más.

7. **Gráfico de Barras Agrupadas: Venta Promedio por Género y Navegador** - Eje X es género, eje Y es venta promedio; barras agrupadas por navegador. Permite ver patrones diferenciados por canal.
>>>>>>>> origin/main:docs/analisis_integrante2/respue2.md

#### Funciones Principales

**calcular_estadisticas()** - Calcula estadísticas descriptivas de un conjunto de números.

**segmentar_datos()** - Segmenta datos por valores de una columna y calcula estadísticas.

**correlacionar_variables()** - Calcula la correlación de Pearson entre dos variables numéricas.

Clasificación de relaciones:
- Fuerte positiva/negativa: |r| > 0.8
- Moderada positiva/negativa: 0.5 < |r| ≤ 0.8
- Débil positiva/negativa: 0.2 < |r| ≤ 0.5
- Muy débil o nula: |r| ≤ 0.2

**detectar_tendencias()** - Detecta tendencias temporales en los datos.

---

### 6.2 Módulo visualizations.py

#### Panorama General

El módulo `visualizations.py` proporciona 8 tipos de gráficas diferentes diseñadas para análisis comprehensivo de datos de ventas online.

#### Especificaciones de Exportación

PNG:
- Resolución: 300 DPI (profesional)
- Fondo: Blanco
- Compresión: Automática
- Uso: Presentaciones, reportes

PDF:
- Formato: Vectorial escalable
- Fondo: Blanco
- Uso: Impresión, reportes formales

#### Paleta de Colores Estándar

```
Primario:     #2E86AB (Azul)
Secundario:   #A23B72 (Púrpura)
Terciario:    #F18F01 (Naranja)
Cuaternario:  #C73E1D (Rojo)
Quinto:       #6A994E (Verde)
Sexto:        #BC4749 (Rojo Oscuro)
```

#### Siete Gráficas Mínimas

1. **Línea de venta total por mes** - Identifica patrones de estacionalidad, meses pico, meses débiles.
2. **Barras por método de pago** - Distribución de formas de pago (Efectivo, Tarjeta Crédito, Tarjeta Débito).
3. **Barras por navegador** - Rendimiento comparativo de canales (Tienda Física, Nav 1-4).
4. **Barras mensuales de boletín** - Uso mensual del boletín y apilación opcional por género.
5. **Barras mensuales de vale** - Uso mensual del vale y apilación opcional por género.
6. **Dispersión entre edad y venta total** - Correlación visual cliente mayor vs. gasto.
7. **Barras agrupadas de comparación por género** - Venta promedio por género y navegador.

---

## 7. Consideraciones de Calidad y Limitaciones

### Limitaciones Reconocidas

1. **Falta de Datos de Costo**: El dataset contiene venta total pero no costo de goods sold (COGS) ni margen.
2. **Ausencia de Datos de Producto**: No hay información de qué producto se vendió.
3. **Definición de "Tiempo" Ambigua**: Campo "tiempo" no tiene unidad especificada.
4. **Clientes Repetidos No Identificables Únicamente**: Tres clientes (198, 402, 559) aparecen dos veces con datos diferentes.
5. **Falta de Atributos de Satisfacción del Cliente**: No hay datos de reseña, rating, o indicador de satisfacción.

### Fortalezas de Calidad

- Datos validados según 20 reglas explícitas documentadas.
- Valores nulos distinguidos de ceros, evitando contaminación.
- Período consistente (todo 2025), sin datos de años anteriores.
- 1,003 registros válidos es muestra de tamaño suficiente para análisis descriptivo.
- Auditoría de problemas de calidad permite trazabilidad de anomalías.

---

## 8. Conclusiones Finales

El análisis de ventas online 2025 proporciona fundamento sólido para decisiones estratégicas de expansión de canales, optimización de promociones y segmentación de clientes. Las respuestas a preguntas 8.a y 8.b demuestran cómo inteligencia de datos desplaza decisiones de intuición a evidencia. Las recomendaciones son viables operacionalmente y de costo manejable. Las limitaciones reconocidas permiten direccionar mejoras futuras. El próximo paso es implementación piloto de decisión segmentada en canal de mayor impacto, seguida de validación de hipótesis en ambientes controlados antes de escala enterprise.

---

### Limitaciones Reconocidas

1. **Falta de Datos de Costo**: El dataset contiene venta total pero no costo de goods sold (COGS) ni margen. Conclusiones sobre "rentabilidad" de canales o segmentos son parciales: venta alta no garantiza margen alto. Recomendación: incorporar costo de operación por canal y margen por producto.

2. **Ausencia de Datos de Producto**: No hay información de qué producto se vendió. Posible que Navegador 2 genere mayor venta porque vende productos de precio alto, no porque experiencia de usuario sea superior. Recomendación: agregar categoría de producto y precio unitario.

3. **Definición de "Tiempo" Ambigua**: Campo "tiempo" no tiene unidad especificada. ¿Es duración de sesión en minutos, segundos, horas? ¿O es métrica de engagement (páginas vistas, clics)? Sin unidad, análisis de tiempo es imposible. Recomendación: clarificar unidad y significado; de no ser posible, excluir campo del análisis.

4. **Clientes Repetidos No Identificables Únicamente**: Tres clientes (198, 402, 559) aparecen dos veces con datos diferentes. Sin campo de identificador de transacción (ticket número, orden ID), es imposible determinar si son genuinamente dos compras diferentes o duplicado de registro. Riesgo: sobreestimar volumen de clientes únicos. Recomendación: incorporar transacción ID único.

5. **Falta de Atributos de Satisfacción del Cliente**: No hay datos de reseña, rating, o indicador de satisfacción. Análisis de "satisfacción" es inferencia indirecta basada en frecuencia de compra. Recomendación: implementar encuesta post-compra o importar ratings de plataforma.

### Fortalezas de Calidad

- Datos validados según 20 reglas explícitas documentadas.
- Valores nulos distinguidos de ceros, evitando contaminación.
- Período consistente (todo 2025), sin datos de años anteriores que requieran ajuste inflacionario.
- 1,003 registros válidos es muestra de tamaño suficiente para análisis descriptivo.
- Auditoría de problemas de calidad permite trazabilidad de anomalías.

---

## 8. Conclusiones Finales

El análisis de ventas online 2025 proporciona fundamento sólido para decisiones estratégicas de expansión de canales, optimización de promociones y segmentación de clientes. Las respuestas a preguntas 8.a y 8.b demuestran cómo inteligencia de datos desplaza decisiones de intuición a evidencia. Las recomendaciones son viables operacionalmente y de costo manejable. Las limitaciones reconocidas permiten direccionar mejoras futuras. El próximo paso es implementación piloto de decisión segmentada en canal de mayor impacto, seguida de validación de hipótesis en ambientes controlados antes de escala enterprise.

---

<<<<<<<< HEAD:docs/analisis_integrante2/INTEGRANTE_2_CONSOLIDADO.md
**Documento preparado por:** Integrante 2 (Javier Monjes - Análisis y Reporte)  
**Fecha:** 17 de septiembre de 2026  
**Basado en:** Dataset de ventas online 2025 (1,003 transacciones validadas)  
**Fuentes de datos:** `data/processed/ventas_online_2025_limpio.csv`, documentación técnica de preparación y modelo relacional
========
**Documento consolidado por:** Integrante 2 (Análisis, Reporte y Documentación Técnica)  
**Fecha:** 18 de septiembre de 2026  
**Basado en:** Dataset de ventas online 2025 (1,003 transacciones validadas)  
**Fuentes de datos:** `data/processed/ventas_online_2025_limpio.csv`, módulos `analysis_engine.py` y `visualizations.py`  
**Nota:** Este documento consolida y reemplaza los archivos anteriores `reporte.md`, `DOCUMENTACION_GRAFICAS.md` y `DOCUMENTACION_ANALYSIS_ENGINE.md`
>>>>>>>> origin/main:docs/analisis_integrante2/respue2.md
