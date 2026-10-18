"""
Módulo de análisis de datos para ventas online.
Proporciona funciones reutilizables para análisis estadístico, segmentación,
correlación y detección de tendencias en datos de ventas.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Callable, Sequence

import numpy as np
import pandas as pd


@dataclass
class Estadisticas:
    """Contiene estadísticas descriptivas de una variable numérica."""
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


@dataclass
class CorrelacionVars:
    """Contiene información de correlación entre dos variables."""
    variable1: str
    variable2: str
    coeficiente: float
    tipo_relacion: str
    cantidad_pares: int


@dataclass
class Tendencia:
    """Contiene información sobre una tendencia temporal detectada."""
    variable: str
    periodo: str
    puntos_datos: int
    promedio_inicial: float
    promedio_final: float
    cambio_porcentaje: float
    direccion: str


def _validar_lista_numerica(valores: Sequence[float], nombre: str) -> list[float]:
    """Valida que una secuencia contenga solo números válidos."""
    if not isinstance(valores, (list, tuple, pd.Series, np.ndarray)):
        raise TypeError(f"{nombre} debe ser una secuencia.")

    lista = []
    for v in valores:
        try:
            num = float(v)
            if not np.isnan(num) and np.isfinite(num):
                lista.append(num)
        except (TypeError, ValueError):
            continue

    if not lista:
        raise ValueError(f"{nombre} debe contener al menos un valor válido.")
    return lista


def _validar_dataframe(df: Any, nombre: str = "DataFrame") -> pd.DataFrame:
    """Valida que el input sea un DataFrame válido."""
    if not isinstance(df, pd.DataFrame):
        raise TypeError(f"{nombre} debe ser un pandas DataFrame.")
    if df.empty:
        raise ValueError(f"{nombre} no puede estar vacío.")
    return df


def calcular_estadisticas(valores: Sequence[float]) -> Estadisticas:
    """Calcula estadísticas descriptivas de un conjunto de números.

    Función pura que calcula media, mediana, desviación estándar,
    cuartiles y otros estadísticos de un conjunto de valores numéricos.

    Args:
        valores: Secuencia de números a analizar.

    Returns:
        Objeto Estadisticas con todos los valores calculados.

    Raises:
        TypeError: Si valores no es una secuencia válida.
        ValueError: Si no hay valores numéricos válidos.
    """
    lista_valida = _validar_lista_numerica(valores, "valores")
    datos_array = np.array(lista_valida)

    cantidad = len(lista_valida)
    media_val = float(np.mean(datos_array))
    mediana_val = float(np.median(datos_array))
    minimo_val = float(np.min(datos_array))
    maximo_val = float(np.max(datos_array))
    rango_val = maximo_val - minimo_val

    if cantidad > 1:
        desv_est = float(np.std(datos_array, ddof=1))
    else:
        desv_est = 0.0

    percentil_25_val = float(np.percentile(datos_array, 25))
    percentil_75_val = float(np.percentile(datos_array, 75))
    rango_iq = percentil_75_val - percentil_25_val

    return Estadisticas(
        cantidad=cantidad,
        media=media_val,
        mediana=mediana_val,
        desviacion_estandar=desv_est,
        minimo=minimo_val,
        maximo=maximo_val,
        rango=rango_val,
        percentil_25=percentil_25_val,
        percentil_75=percentil_75_val,
        rango_intercuartil=rango_iq,
    )


def segmentar_datos(
    df: pd.DataFrame,
    columna_grupo: str,
    columna_valor: str | None = None,
) -> dict[str, pd.DataFrame | Estadisticas]:
    """Segmenta datos por valores de una columna y calcula estadísticas.

    Divide el DataFrame en grupos basados en los valores de una columna,
    opcionalmente calculando estadísticas para cada grupo.

    Args:
        df: DataFrame con los datos a segmentar.
        columna_grupo: Nombre de la columna por la cual agrupar.
        columna_valor: Nombre de la columna para calcular estadísticas.

    Returns:
        Diccionario con estadísticas o DataFrames por grupo.

    Raises:
        TypeError: Si df no es un DataFrame.
        ValueError: Si el DataFrame está vacío o columna no existe.
    """
    df_validado = _validar_dataframe(df)

    if columna_grupo not in df_validado.columns:
        raise ValueError(f"Columna '{columna_grupo}' no encontrada.")

    if columna_valor and columna_valor not in df_validado.columns:
        raise ValueError(f"Columna '{columna_valor}' no encontrada.")

    resultado: dict[str, pd.DataFrame | Estadisticas] = {}

    for valor_grupo, grupo_df in df_validado.groupby(columna_grupo, sort=True):
        if columna_valor is None:
            resultado[str(valor_grupo)] = grupo_df
        else:
            try:
                valores = grupo_df[columna_valor].dropna().tolist()
                resultado[str(valor_grupo)] = calcular_estadisticas(valores)
            except ValueError:
                resultado[str(valor_grupo)] = None

    return resultado


def segmentar_por_rango(
    df: pd.DataFrame,
    columna: str,
    limites: Sequence[float],
    etiquetas: Sequence[str] | None = None,
) -> dict[str, pd.DataFrame]:
    """Segmenta datos por rangos numéricos de una columna.

    Crea segmentos basados en rangos definidos por límites numéricos.

    Args:
        df: DataFrame con los datos.
        columna: Nombre de la columna a usar para los rangos.
        limites: Lista de límites para los rangos.
        etiquetas: Nombres para los rangos. Si es None, usa índices.

    Returns:
        Diccionario con DataFrames por rango.

    Raises:
        ValueError: Si los límites no están ordenados.
    """
    df_validado = _validar_dataframe(df)

    if columna not in df_validado.columns:
        raise ValueError(f"Columna '{columna}' no encontrada.")

    limites_lista = list(limites)
    if limites_lista != sorted(limites_lista):
        raise ValueError("Los límites deben estar en orden ascendente.")

    if etiquetas is None:
        etiquetas = [f"rango_{i}" for i in range(len(limites_lista) - 1)]
    else:
        etiquetas = list(etiquetas)

    if len(etiquetas) != len(limites_lista) - 1:
        raise ValueError("Número de etiquetas incorrecto.")

    resultado: dict[str, pd.DataFrame] = {}

    bins = pd.cut(
        df_validado[columna],
        bins=limites_lista,
        labels=etiquetas,
        include_lowest=True,
        right=False,
    )

    for etiqueta, grupo_df in df_validado.groupby(bins, observed=True, sort=True):
        resultado[str(etiqueta)] = grupo_df

    return resultado


def correlacionar_variables(
    df: pd.DataFrame,
    var1: str,
    var2: str,
) -> CorrelacionVars:
    """Calcula la correlación de Pearson entre dos variables numéricas.

    Función pura que calcula el coeficiente de correlación y clasifica
    la intensidad de la relación entre dos variables.

    Args:
        df: DataFrame con los datos.
        var1: Nombre de la primera variable.
        var2: Nombre de la segunda variable.

    Returns:
        Objeto CorrelacionVars con coeficiente y descripción.

    Raises:
        ValueError: Si alguna variable no existe o no hay datos válidos.
    """
    df_validado = _validar_dataframe(df)

    for var in [var1, var2]:
        if var not in df_validado.columns:
            raise ValueError(f"Columna '{var}' no encontrada.")

    datos_limpios = df_validado[[var1, var2]].dropna()

    if len(datos_limpios) < 2:
        raise ValueError("Se necesitan al menos 2 pares de datos válidos.")

    coef_correlacion = float(datos_limpios[var1].corr(datos_limpios[var2]))

    valor_abs = abs(coef_correlacion)
    if valor_abs > 0.8:
        tipo_relacion = "fuerte positiva" if coef_correlacion > 0 else "fuerte negativa"
    elif valor_abs > 0.5:
        tipo_relacion = "moderada positiva" if coef_correlacion > 0 else "moderada negativa"
    elif valor_abs > 0.2:
        tipo_relacion = "débil positiva" if coef_correlacion > 0 else "débil negativa"
    else:
        tipo_relacion = "muy débil o nula"

    return CorrelacionVars(
        variable1=var1,
        variable2=var2,
        coeficiente=coef_correlacion,
        tipo_relacion=tipo_relacion,
        cantidad_pares=len(datos_limpios),
    )


def correlacionar_multiples(
    df: pd.DataFrame,
    columnas: Sequence[str] | None = None,
) -> pd.DataFrame:
    """Calcula matriz de correlación entre múltiples variables.

    Genera una matriz de correlación de Pearson entre todas las variables
    numéricas especificadas.

    Args:
        df: DataFrame con los datos.
        columnas: Lista de columnas a correlacionar. Si es None, usa todas
                 las numéricas.

    Returns:
        DataFrame con la matriz de correlación.

    Raises:
        ValueError: Si no hay columnas numéricas válidas.
    """
    df_validado = _validar_dataframe(df)

    if columnas is None:
        df_analizar = df_validado.select_dtypes(include=[np.number])
    else:
        columnas_lista = list(columnas)
        for col in columnas_lista:
            if col not in df_validado.columns:
                raise ValueError(f"Columna '{col}' no encontrada.")
        df_analizar = df_validado[columnas_lista].select_dtypes(include=[np.number])

    if df_analizar.empty or df_analizar.shape[1] < 2:
        raise ValueError("Se necesitan al menos 2 columnas numéricas.")

    matriz = df_analizar.corr(method="pearson")

    return matriz


def detectar_tendencias(
    df: pd.DataFrame,
    columna_fecha: str,
    columna_valor: str,
    columna_grupo: str | None = None,
) -> list[Tendencia] | Tendencia:
    """Detecta tendencias temporales en los datos.

    Analiza cambios en los valores a lo largo del tiempo, agrupando
    por períodos para identificar tendencias.

    Args:
        df: DataFrame con los datos.
        columna_fecha: Nombre de la columna con fechas.
        columna_valor: Nombre de la columna numérica a analizar.
        columna_grupo: Opcional. Columna para agrupar tendencias.

    Returns:
        Una o varias Tendencia según columna_grupo.

    Raises:
        ValueError: Si alguna columna no existe o no hay datos válidos.
    """
    df_validado = _validar_dataframe(df)

    for col in [columna_fecha, columna_valor]:
        if col not in df_validado.columns:
            raise ValueError(f"Columna '{col}' no encontrada.")

    if columna_grupo and columna_grupo not in df_validado.columns:
        raise ValueError(f"Columna '{columna_grupo}' no encontrada.")

    df_prep = df_validado[[columna_fecha, columna_valor]].copy()

    if not pd.api.types.is_datetime64_any_dtype(df_prep[columna_fecha]):
        try:
            df_prep[columna_fecha] = pd.to_datetime(df_prep[columna_fecha])
        except Exception as e:
            raise ValueError(f"No se pudo convertir fecha: {str(e)}")

    df_prep = df_prep.sort_values(columna_fecha).reset_index(drop=True)
    df_prep = df_prep.dropna()

    if len(df_prep) < 2:
        raise ValueError("Se necesitan al menos 2 registros válidos.")

    def _calcular_tendencia_grupo(
        grupo_df: pd.DataFrame, nombre_grupo: str = ""
    ) -> Tendencia:
        """Calcula tendencia para un grupo de datos."""
        valores = grupo_df[columna_valor].tolist()
        fechas = grupo_df[columna_fecha].tolist()

        promedio_inicial = float(np.mean(valores[: len(valores) // 2]))
        promedio_final = float(np.mean(valores[len(valores) // 2 :]))

        if promedio_inicial != 0:
            cambio_pct = ((promedio_final - promedio_inicial) / abs(promedio_inicial)) * 100
        else:
            cambio_pct = 0.0

        umbral = 5
        if cambio_pct > umbral:
            direccion = "ascendente"
        elif cambio_pct < -umbral:
            direccion = "descendente"
        else:
            direccion = "estable"

        if len(fechas) >= 2:
            duracion = (fechas[-1] - fechas[0]).days
            if duracion <= 31:
                periodo = "mes"
            elif duracion <= 92:
                periodo = "trimestre"
            else:
                periodo = "anio"
        else:
            periodo = "desconocido"

        return Tendencia(
            variable=nombre_grupo or columna_valor,
            periodo=periodo,
            puntos_datos=len(valores),
            promedio_inicial=promedio_inicial,
            promedio_final=promedio_final,
            cambio_porcentaje=cambio_pct,
            direccion=direccion,
        )

    if columna_grupo is None:
        return _calcular_tendencia_grupo(df_prep)

    df_prep_grupo = df_validado.copy()
    df_prep_grupo[columna_fecha] = pd.to_datetime(df_prep_grupo[columna_fecha])
    df_prep_grupo = df_prep_grupo.dropna(subset=[columna_fecha, columna_valor])

    tendencias: list[Tendencia] = []
    for valor_grupo, grupo_df in df_prep_grupo.groupby(columna_grupo, sort=True):
        try:
            tend = _calcular_tendencia_grupo(
                grupo_df[[columna_fecha, columna_valor]],
                nombre_grupo=f"{columna_valor} ({valor_grupo})",
            )
            tendencias.append(tend)
        except ValueError:
            continue

    if not tendencias:
        raise ValueError("No se pudieron calcular tendencias.")

    return tendencias


def aplicar_filtro(
    df: pd.DataFrame,
    columna: str,
    condicion: Callable[[Any], bool],
) -> pd.DataFrame:
    """Aplica un filtro funcional a un DataFrame.

    Función pura que retorna un nuevo DataFrame sin modificar el original.

    Args:
        df: DataFrame a filtrar.
        columna: Nombre de la columna a evaluar.
        condicion: Función que retorna True para mantener la fila.

    Returns:
        Nuevo DataFrame filtrado.

    Raises:
        ValueError: Si la columna no existe.
    """
    df_validado = _validar_dataframe(df)

    if columna not in df_validado.columns:
        raise ValueError(f"Columna '{columna}' no encontrada.")

    return df_validado[df_validado[columna].apply(condicion)].copy()


def resumir_por_grupo(
    df: pd.DataFrame,
    columna_grupo: str,
    agregaciones: dict[str, str],
) -> pd.DataFrame:
    """Crea un resumen agregado por grupos.

    Aplica funciones de agregación a grupos de datos.

    Args:
        df: DataFrame con los datos.
        columna_grupo: Columna por la cual agrupar.
        agregaciones: Diccionario de agregaciones.

    Returns:
        DataFrame con resumen agregado.

    Raises:
        ValueError: Si la columna de grupo no existe.
    """
    df_validado = _validar_dataframe(df)

    if columna_grupo not in df_validado.columns:
        raise ValueError(f"Columna '{columna_grupo}' no encontrada.")

    return df_validado.groupby(columna_grupo, sort=True).agg(agregaciones)
