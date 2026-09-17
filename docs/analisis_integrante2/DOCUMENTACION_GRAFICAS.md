# Documentación de Visualizaciones de Datos

## Panorama General

El módulo `visualizations.py` proporciona 8 tipos de gráficas diferentes diseñadas para análisis comprehensivo de datos de ventas online. Cada gráfica está optimizada para revelar diferentes aspectos de los datos mediante visualización académica profesional.

---

## Gráfica 1: Distribución de Edades de Clientes

**Archivo**: `01_distribucion_edades.png/pdf`

**Tipo**: Histograma con indicadores estadísticos

**Función**: `grafica_distribucion_edades(df, titulo, color, bins, figsize)`

### Descripción

Histograma que muestra la distribución de frecuencias de las edades de los clientes. Incluye líneas de referencia para media y mediana, permitiendo identificar patrones en la población.

### Características Técnicas

- Bins: 20 (ajustable)
- Colores: Azul primario con borde negro
- Líneas de referencia: Media (púrpura) y Mediana (naranja)
- Validación: Excluye edades <= 0 o > 100

### Insights Típicos

- Identifica grupos de edad dominantes
- Compara media y mediana para detectar asimetría
- Ayuda a segmentar campañas por edad
- Revela si hay distribución uniforme o concentrada

### Parámetros Personalizables

```python
grafica_distribucion_edades(
    df=datos,
    titulo="Distribución de Edades",
    color="#2E86AB",  # Color personalizado
    bins=25,          # Más bins = más granularidad
    figsize=(12, 7)   # Tamaño de figura
)
```

---

## Especificaciones de Exportación

### Formatos

**PNG**: 
- Resolución: 300 DPI (profesional)
- Fondo: Blanco
- Compresión: Automática
- Uso: Presentaciones, reportes

**PDF**:
- Formato: Vectorial escalable
- Fondo: Blanco
- Tamaño: Automático
- Uso: Impresión, reportes formales
- Nota: Se genera también un PDF combinado con todas las gráficas

### Paleta de Colores Estándar

```
Primario:     #2E86AB (Azul)
Secundario:   #A23B72 (Púrpura)
Terciario:    #F18F01 (Naranja)
Cuaternario:  #C73E1D (Rojo)
Quinto:       #6A994E (Verde)
Sexto:        #BC4749 (Rojo Oscuro)
```

### Estilos Académicos Aplicados

- Fuente: sans-serif (sistema)
- Tamaño base: 10pt
- Títulos: 13pt, negrita, 20pt padding
- Etiquetas ejes: 11pt, negrita
- Grid: alfa 0.3, solo en necesario
