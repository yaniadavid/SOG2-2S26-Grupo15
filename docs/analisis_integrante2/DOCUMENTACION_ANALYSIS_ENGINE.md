# Módulo analysis_engine.py

## Descripción General

El módulo `analysis_engine.py` proporciona funciones reutilizables y profesionales para análisis estadístico, segmentación, correlación y detección de tendencias en datos de ventas online.

**Características:**
- Funciones puras sin efectos secundarios
- Validación rigurosa de entrada
- Manejo robusto de errores
- Documentación completa con type hints
- Código testeable y modular

---

## Tipos de Datos (Dataclasses)

### Estadisticas

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

### CorrelacionVars

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

### Tendencia

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

---

## Funciones Principales

### calcular_estadisticas()

Calcula estadísticas descriptivas de un conjunto de números.

**Firma:**
```python
def calcular_estadisticas(valores: Sequence[float]) -> Estadisticas:
```

**Características:**
- Calcula media, mediana, desviación estándar
- Detecta automáticamente valores NaN e infinito
- Trabaja con listas, tuplas, Series de pandas y arrays de numpy

### segmentar_datos()

Segmenta datos por valores de una columna y calcula estadísticas.

### correlacionar_variables()

Calcula la correlación de Pearson entre dos variables numéricas.

**Clasificación de relaciones:**
- **Fuerte positiva/negativa:** |r| > 0.8
- **Moderada positiva/negativa:** 0.5 < |r| ≤ 0.8
- **Débil positiva/negativa:** 0.2 < |r| ≤ 0.5
- **Muy débil o nula:** |r| ≤ 0.2

### detectar_tendencias()

Detecta tendencias temporales en los datos.

**Características:**
- Detecta tendencias ascendentes, descendentes o estables
- Clasifica períodos automáticamente (mes, trimestre, año)
- Calcula cambio porcentual
- Umbral de estabilidad: 5%

---

## Características de Diseño

### 1. Funciones Puras
No modifica el DataFrame original, retorna copias.

### 2. Type Hints Completos
Todas las funciones tienen anotaciones de tipos.

### 3. Documentación Detallada
Docstrings completos con Args, Returns, Raises.

### 4. Validación Rigurosa
Cada función valida sus inputs con mensajes descriptivos.

---

## Caso de Uso Completo

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

---

## Instalación de Dependencias

```bash
pip install pandas numpy
```
