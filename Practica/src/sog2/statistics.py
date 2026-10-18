"""
Módulo de Análisis Estadístico para datos de ventas online
Integrante 2 - Segundo Semestre 2026

Funcionalidades:
- Estadísticas descriptivas (media, mediana, desviación estándar, cuartiles)
- Análisis de tendencias temporales
- Segmentación por categorías principales
- Matriz de correlación
- Generación de datasets de resultados para visualización
"""

import pandas as pd
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from pathlib import Path
import json
from datetime import datetime


class EstadisticasDescriptivas:
    """Calcula estadísticas descriptivas para variables numéricas"""

    @staticmethod
    def calcular_stats(serie: pd.Series, nombre_variable: str = "") -> Dict[str, Any]:
        """
        Calcula estadísticas descriptivas completas para una serie numérica

        Parámetros:
            serie: pd.Series - Serie de datos numéricos
            nombre_variable: str - Nombre de la variable para referencia

        Retorna:
            dict - Diccionario con todas las estadísticas
        """
        serie_limpia = serie.dropna()

        if len(serie_limpia) == 0:
            return {
                "variable": nombre_variable,
                "n_valores": 0,
                "n_valores_nulos": len(serie) - len(serie_limpia),
                "error": "No hay valores válidos"
            }

        return {
            "variable": nombre_variable,
            "n_valores": len(serie_limpia),
            "n_valores_nulos": len(serie) - len(serie_limpia),
            "media": float(serie_limpia.mean()),
            "mediana": float(serie_limpia.median()),
            "moda": float(serie_limpia.mode()[0]) if not serie_limpia.mode().empty else None,
            "desv_estandar": float(serie_limpia.std()),
            "varianza": float(serie_limpia.var()),
            "rango": float(serie_limpia.max() - serie_limpia.min()),
            "minimo": float(serie_limpia.min()),
            "maximo": float(serie_limpia.max()),
            "q1": float(serie_limpia.quantile(0.25)),
            "q2_mediana": float(serie_limpia.quantile(0.50)),
            "q3": float(serie_limpia.quantile(0.75)),
            "iqr": float(serie_limpia.quantile(0.75) - serie_limpia.quantile(0.25)),
            "coeficiente_variacion": float((serie_limpia.std() / serie_limpia.mean()) * 100) if serie_limpia.mean() != 0 else None,
            "sesgo": float(serie_limpia.skew()),
            "curtosis": float(serie_limpia.kurtosis()),
            "suma": float(serie_limpia.sum()),
            "promedio_ponderado": float(serie_limpia.mean())
        }

    @staticmethod
    def analizar_todas_variables(df: pd.DataFrame) -> pd.DataFrame:
        """
        Analiza todas las variables numéricas del dataframe

        Parámetros:
            df: pd.DataFrame - Datos a analizar

        Retorna:
            pd.DataFrame - Tabla con estadísticas de todas las variables
        """
        variables_numericas = df.select_dtypes(include=[np.number]).columns

        resultados = []
        for var in variables_numericas:
            stats = EstadisticasDescriptivas.calcular_stats(df[var], var)
            resultados.append(stats)

        return pd.DataFrame(resultados)


class AnalisisTendencias:
    """Analiza tendencias temporales en los datos"""

    @staticmethod
    def procesar_fechas(df: pd.DataFrame, columna_fecha: str) -> pd.DataFrame:
        """
        Convierte columna de fechas y extrae componentes temporales

        Parámetros:
            df: pd.DataFrame - Datos
            columna_fecha: str - Nombre de la columna con fechas

        Retorna:
            pd.DataFrame - DataFrame con columnas temporales adicionales
        """
        df_temp = df.copy()
        df_temp[columna_fecha] = pd.to_datetime(df_temp[columna_fecha])

        df_temp['anio'] = df_temp[columna_fecha].dt.year
        df_temp['mes'] = df_temp[columna_fecha].dt.month
        df_temp['semana'] = df_temp[columna_fecha].dt.isocalendar().week
        df_temp['dia_semana'] = df_temp[columna_fecha].dt.day_name()
        df_temp['trimestre'] = df_temp[columna_fecha].dt.quarter

        return df_temp

    @staticmethod
    def tendencia_por_mes(df: pd.DataFrame, columna_fecha: str,
                         variables_analizar: List[str]) -> Dict[str, Any]:
        """
        Analiza tendencias mensuales de variables seleccionadas

        Parámetros:
            df: pd.DataFrame - Datos con fechas
            columna_fecha: str - Columna de fecha
            variables_analizar: List[str] - Variables a analizar

        Retorna:
            dict - Diccionario con tendencias por mes
        """
        df_temp = AnalisisTendencias.procesar_fechas(df, columna_fecha)

        tendencias = {}
        for var in variables_analizar:
            if var in df_temp.columns:
                tendencia_mensual = df_temp.groupby('mes')[var].agg(['mean', 'sum', 'count', 'std'])
                tendencias[var] = tendencia_mensual.to_dict('index')

        return tendencias

    @staticmethod
    def estadisticas_por_periodo(df: pd.DataFrame, columna_fecha: str,
                                columna_valor: str, periodo: str = 'mes') -> pd.DataFrame:
        """
        Agrupa datos por período temporal y calcula estadísticas

        Parámetros:
            df: pd.DataFrame - Datos
            columna_fecha: str - Columna de fecha
            columna_valor: str - Columna a agregar
            periodo: str - 'mes', 'semana', 'trimestre'

        Retorna:
            pd.DataFrame - Estadísticas por período
        """
        df_temp = AnalisisTendencias.procesar_fechas(df, columna_fecha)

        periodo_col = f'{periodo}'

        resultados = df_temp.groupby(periodo_col)[columna_valor].agg([
            'mean', 'median', 'std', 'min', 'max', 'sum', 'count'
        ]).reset_index()

        return resultados


class SegmentacionCategorias:
    """Segmenta datos por categorías principales"""

    @staticmethod
    def segmentar_por_categoria(df: pd.DataFrame, columna_categoria: str,
                               columna_valor: str, agg_functions: List[str] = None) -> Dict[str, Any]:
        """
        Segmenta datos por una variable categórica

        Parámetros:
            df: pd.DataFrame - Datos
            columna_categoria: str - Variable categórica para segmentación
            columna_valor: str - Variable a agregar
            agg_functions: List[str] - Funciones de agregación

        Retorna:
            dict - Segmentación por categoría
        """
        if agg_functions is None:
            agg_functions = ['mean', 'sum', 'count', 'std']

        segmentacion = df.groupby(columna_categoria)[columna_valor].agg(agg_functions).to_dict('index')
        return segmentacion

    @staticmethod
    def segmentacion_multivariable(df: pd.DataFrame, columna_categoria: str,
                                  columnas_valor: List[str]) -> pd.DataFrame:
        """
        Segmenta múltiples variables por categoría

        Parámetros:
            df: pd.DataFrame - Datos
            columna_categoria: str - Variable categórica
            columnas_valor: List[str] - Variables a analizar

        Retorna:
            pd.DataFrame - Tabla de segmentación multivariable
        """
        resultados = []

        for valor in columnas_valor:
            if valor in df.columns:
                seg = df.groupby(columna_categoria)[valor].agg(['mean', 'sum', 'count']).reset_index()
                seg['variable'] = valor
                seg.columns = ['categoria', 'media', 'suma', 'cantidad', 'variable']
                resultados.append(seg)

        return pd.concat(resultados, ignore_index=True) if resultados else pd.DataFrame()

    @staticmethod
    def analisis_por_genero(df: pd.DataFrame, columna_genero: str = 'genero') -> Dict[str, Any]:
        """
        Análisis específico por género

        Parámetros:
            df: pd.DataFrame - Datos
            columna_genero: str - Columna de género

        Retorna:
            dict - Análisis por género
        """
        if columna_genero not in df.columns:
            return {}

        variables_numericas = df.select_dtypes(include=[np.number]).columns.tolist()
        variables_numericas = [v for v in variables_numericas if v != columna_genero]

        analisis = {}

        for genero in df[columna_genero].dropna().unique():
            datos_genero = df[df[columna_genero] == genero]
            analisis[f'genero_{genero}'] = {
                'cantidad': len(datos_genero),
                'proporciones': {}
            }

            for var in variables_numericas[:5]:
                stats = EstadisticasDescriptivas.calcular_stats(datos_genero[var])
                analisis[f'genero_{genero}']['proporciones'][var] = {
                    'media': stats.get('media'),
                    'mediana': stats.get('mediana'),
                    'std': stats.get('desv_estandar')
                }

        return analisis

    @staticmethod
    def analisis_por_metodo_pago(df: pd.DataFrame, columna_pago: str = 'metodo_pago',
                                columna_valor: str = 'venta_total') -> Dict[str, Any]:
        """
        Análisis de ventas por método de pago

        Parámetros:
            df: pd.DataFrame - Datos
            columna_pago: str - Columna de método de pago
            columna_valor: str - Columna de monto

        Retorna:
            dict - Análisis por método de pago
        """
        if columna_pago not in df.columns or columna_valor not in df.columns:
            return {}

        analisis = {}

        for metodo in df[columna_pago].dropna().unique():
            datos_metodo = df[df[columna_pago] == metodo]

            analisis[f'metodo_{metodo}'] = {
                'cantidad_transacciones': len(datos_metodo),
                'venta_total': float(datos_metodo[columna_valor].sum()),
                'venta_promedio': float(datos_metodo[columna_valor].mean()),
                'venta_max': float(datos_metodo[columna_valor].max()),
                'venta_min': float(datos_metodo[columna_valor].min()),
                'std_venta': float(datos_metodo[columna_valor].std())
            }

        return analisis


class AnalisisCorrelacion:
    """Calcula y analiza correlaciones entre variables"""

    @staticmethod
    def matriz_correlacion(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula la matriz de correlación de Pearson

        Parámetros:
            df: pd.DataFrame - Datos

        Retorna:
            pd.DataFrame - Matriz de correlación
        """
        variables_numericas = df.select_dtypes(include=[np.number])
        return variables_numericas.corr(method='pearson')

    @staticmethod
    def matriz_correlacion_spearman(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calcula la matriz de correlación de Spearman

        Parámetros:
            df: pd.DataFrame - Datos

        Retorna:
            pd.DataFrame - Matriz de correlación Spearman
        """
        variables_numericas = df.select_dtypes(include=[np.number])
        return variables_numericas.corr(method='spearman')

    @staticmethod
    def correlaciones_significativas(df: pd.DataFrame, umbral: float = 0.5) -> List[Dict[str, Any]]:
        """
        Identifica correlaciones significativas entre variables

        Parámetros:
            df: pd.DataFrame - Datos
            umbral: float - Valor mínimo de correlación absoluta

        Retorna:
            List[Dict] - Lista de correlaciones significativas
        """
        matriz = AnalisisCorrelacion.matriz_correlacion(df)

        correlaciones_sig = []

        for i in range(len(matriz.columns)):
            for j in range(i + 1, len(matriz.columns)):
                valor = matriz.iloc[i, j]

                if abs(valor) >= umbral:
                    correlaciones_sig.append({
                        'variable_1': matriz.columns[i],
                        'variable_2': matriz.columns[j],
                        'correlacion': float(valor),
                        'tipo': 'positiva' if valor > 0 else 'negativa',
                        'fuerza': AnalisisCorrelacion._clasificar_fuerza(abs(valor))
                    })

        return sorted(correlaciones_sig, key=lambda x: abs(x['correlacion']), reverse=True)

    @staticmethod
    def _clasificar_fuerza(valor_abs: float) -> str:
        """Clasifica la fuerza de una correlación"""
        if valor_abs >= 0.9:
            return "muy fuerte"
        elif valor_abs >= 0.7:
            return "fuerte"
        elif valor_abs >= 0.5:
            return "moderada"
        elif valor_abs >= 0.3:
            return "débil"
        else:
            return "muy débil"


class GeneradorReportes:
    """Genera reportes y datasets de resultados"""

    @staticmethod
    def generar_reporte_completo(df: pd.DataFrame, ruta_salida: str = 'resultados') -> Dict[str, str]:
        """
        Genera un reporte completo de análisis

        Parámetros:
            df: pd.DataFrame - Datos a analizar
            ruta_salida: str - Ruta para guardar resultados

        Retorna:
            dict - Diccionario con rutas de archivos generados
        """
        Path(ruta_salida).mkdir(exist_ok=True)

        rutas_generadas = {}

        # 1. Estadísticas descriptivas
        stats_df = EstadisticasDescriptivas.analizar_todas_variables(df)
        ruta_stats = f'{ruta_salida}/estadisticas_descriptivas.csv'
        stats_df.to_csv(ruta_stats, index=False)
        rutas_generadas['estadisticas_descriptivas'] = ruta_stats

        # 2. Matriz de correlación
        matriz_corr = AnalisisCorrelacion.matriz_correlacion(df)
        ruta_corr = f'{ruta_salida}/matriz_correlacion.csv'
        matriz_corr.to_csv(ruta_corr)
        rutas_generadas['matriz_correlacion'] = ruta_corr

        # 3. Correlaciones significativas
        corr_sig = AnalisisCorrelacion.correlaciones_significativas(df)
        ruta_corr_sig = f'{ruta_salida}/correlaciones_significativas.json'
        with open(ruta_corr_sig, 'w') as f:
            json.dump(corr_sig, f, indent=2, ensure_ascii=False)
        rutas_generadas['correlaciones_significativas'] = ruta_corr_sig

        return rutas_generadas

    @staticmethod
    def exportar_dataset_segmentacion(df: pd.DataFrame, columna_categoria: str,
                                     ruta_salida: str = 'resultados') -> str:
        """
        Exporta dataset de segmentación por categoría

        Parámetros:
            df: pd.DataFrame - Datos
            columna_categoria: str - Variable categórica
            ruta_salida: str - Ruta de salida

        Retorna:
            str - Ruta del archivo generado
        """
        Path(ruta_salida).mkdir(exist_ok=True)

        seg = SegmentacionCategorias.segmentacion_multivariable(
            df, columna_categoria,
            df.select_dtypes(include=[np.number]).columns.tolist()[:5]
        )

        ruta_seg = f'{ruta_salida}/segmentacion_{columna_categoria}.csv'
        seg.to_csv(ruta_seg, index=False)

        return ruta_seg

    @staticmethod
    def exportar_tendencias_temporales(df: pd.DataFrame, columna_fecha: str,
                                      columna_valor: str, ruta_salida: str = 'resultados') -> str:
        """
        Exporta análisis de tendencias temporales

        Parámetros:
            df: pd.DataFrame - Datos
            columna_fecha: str - Columna de fecha
            columna_valor: str - Variable a analizar
            ruta_salida: str - Ruta de salida

        Retorna:
            str - Ruta del archivo generado
        """
        Path(ruta_salida).mkdir(exist_ok=True)

        tendencias = AnalisisTendencias.estadisticas_por_periodo(df, columna_fecha, columna_valor)

        ruta_tend = f'{ruta_salida}/tendencias_temporales_{columna_valor}.csv'
        tendencias.to_csv(ruta_tend, index=False)

        return ruta_tend

    @staticmethod
    def generar_resumen_json(df: pd.DataFrame, ruta_salida: str = 'resultados') -> str:
        """
        Genera un resumen completo en formato JSON

        Parámetros:
            df: pd.DataFrame - Datos
            ruta_salida: str - Ruta de salida

        Retorna:
            str - Ruta del archivo generado
        """
        Path(ruta_salida).mkdir(exist_ok=True)

        resumen = {
            'timestamp': datetime.now().isoformat(),
            'total_filas': len(df),
            'total_columnas': len(df.columns),
            'variables_numericas': len(df.select_dtypes(include=[np.number]).columns),
            'variables_categoricas': len(df.select_dtypes(exclude=[np.number]).columns),
            'columnas': list(df.columns),
            'tipos_datos': df.dtypes.astype(str).to_dict()
        }

        ruta_resumen = f'{ruta_salida}/resumen_datos.json'
        with open(ruta_resumen, 'w') as f:
            json.dump(resumen, f, indent=2, ensure_ascii=False)

        return ruta_resumen


def ejecutar_analisis_completo(ruta_csv: str, ruta_salida: str = 'resultados') -> Dict[str, Any]:
    """
    Ejecuta análisis estadístico completo

    Parámetros:
        ruta_csv: str - Ruta del archivo CSV
        ruta_salida: str - Ruta para guardar resultados

    Retorna:
        dict - Resumen de resultados
    """
    # Cargar datos
    df = pd.read_csv(ruta_csv)

    Path(ruta_salida).mkdir(exist_ok=True)

    resultados = {
        'estado': 'éxito',
        'timestamp': datetime.now().isoformat(),
        'datos_info': {
            'total_filas': len(df),
            'total_columnas': len(df.columns),
            'columnas': list(df.columns)
        },
        'archivos_generados': {}
    }

    # 1. Estadísticas descriptivas
    print("Generando estadísticas descriptivas...")
    stats_df = EstadisticasDescriptivas.analizar_todas_variables(df)
    ruta_stats = f'{ruta_salida}/estadisticas_descriptivas.csv'
    stats_df.to_csv(ruta_stats, index=False)
    resultados['archivos_generados']['estadisticas_descriptivas'] = ruta_stats

    # 2. Matriz de correlación
    print("Calculando matriz de correlación...")
    matriz_corr = AnalisisCorrelacion.matriz_correlacion(df)
    ruta_corr = f'{ruta_salida}/matriz_correlacion.csv'
    matriz_corr.to_csv(ruta_corr)
    resultados['archivos_generados']['matriz_correlacion'] = ruta_corr

    # 3. Correlaciones significativas
    print("Identificando correlaciones significativas...")
    corr_sig = AnalisisCorrelacion.correlaciones_significativas(df, umbral=0.3)
    ruta_corr_sig = f'{ruta_salida}/correlaciones_significativas.json'
    with open(ruta_corr_sig, 'w') as f:
        json.dump(corr_sig, f, indent=2, ensure_ascii=False)
    resultados['archivos_generados']['correlaciones_significativas'] = ruta_corr_sig
    resultados['correlaciones_top'] = corr_sig[:10]

    # 4. Tendencias temporales (si existe fecha_compra)
    if 'fecha_compra' in df.columns:
        print("Analizando tendencias temporales...")
        variables_analizar = ['venta_total', 'numero_compras', 'monto_compra']
        for var in variables_analizar:
            if var in df.columns:
                tendencias = AnalisisTendencias.estadisticas_por_periodo(df, 'fecha_compra', var)
                ruta_tend = f'{ruta_salida}/tendencias_{var}.csv'
                tendencias.to_csv(ruta_tend, index=False)
                resultados['archivos_generados'][f'tendencias_{var}'] = ruta_tend

    # 5. Segmentación por categorías
    print("Realizando segmentación por categorías...")

    # Por género
    if 'genero' in df.columns:
        seg_genero = SegmentacionCategorias.segmentacion_multivariable(
            df, 'genero',
            ['venta_total', 'numero_compras', 'edad', 'monto_compra']
        )
        ruta_seg_genero = f'{ruta_salida}/segmentacion_genero.csv'
        seg_genero.to_csv(ruta_seg_genero, index=False)
        resultados['archivos_generados']['segmentacion_genero'] = ruta_seg_genero

    # Por método de pago
    if 'metodo_pago' in df.columns:
        seg_pago = SegmentacionCategorias.segmentacion_multivariable(
            df, 'metodo_pago',
            ['venta_total', 'numero_compras', 'edad']
        )
        ruta_seg_pago = f'{ruta_salida}/segmentacion_metodo_pago.csv'
        seg_pago.to_csv(ruta_seg_pago, index=False)
        resultados['archivos_generados']['segmentacion_metodo_pago'] = ruta_seg_pago

    # Por navegador
    if 'navegador' in df.columns:
        seg_nav = SegmentacionCategorias.segmentacion_multivariable(
            df, 'navegador',
            ['venta_total', 'tiempo', 'numero_compras']
        )
        ruta_seg_nav = f'{ruta_salida}/segmentacion_navegador.csv'
        seg_nav.to_csv(ruta_seg_nav, index=False)
        resultados['archivos_generados']['segmentacion_navegador'] = ruta_seg_nav

    # 6. Resumen en JSON
    print("Generando resumen final...")
    ruta_resumen = GeneradorReportes.generar_resumen_json(df, ruta_salida)
    resultados['archivos_generados']['resumen'] = ruta_resumen

    return resultados


if __name__ == "__main__":
    # Ejemplo de uso
    ruta_csv = "data/processed/ventas_online_2025_limpio.csv"
    ruta_salida = "resultados_analisis"

    resultados = ejecutar_analisis_completo(ruta_csv, ruta_salida)

    print("\n=== ANÁLISIS ESTADÍSTICO COMPLETADO ===")
    print(f"Total de filas: {resultados['datos_info']['total_filas']}")
    print(f"Total de columnas: {resultados['datos_info']['total_columnas']}")
    print(f"\nArchivos generados:")
    for nombre, ruta in resultados['archivos_generados'].items():
        print(f"  - {nombre}: {ruta}")

    if resultados.get('correlaciones_top'):
        print(f"\nTop 5 correlaciones significativas:")
        for i, corr in enumerate(resultados['correlaciones_top'][:5], 1):
            print(f"  {i}. {corr['variable_1']} <-> {corr['variable_2']}: {corr['correlacion']:.3f} ({corr['fuerza']})")
