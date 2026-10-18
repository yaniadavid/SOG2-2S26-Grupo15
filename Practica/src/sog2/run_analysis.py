#!/usr/bin/env python
"""Script para ejecutar análisis estadístico completo"""

import sys
import os
from pathlib import Path

# Agregar directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

from statistics import (
    EstadisticasDescriptivas,
    AnalisisTendencias,
    SegmentacionCategorias,
    AnalisisCorrelacion,
    GeneradorReportes,
    ejecutar_analisis_completo
)

import pandas as pd
import json

def main():
    # Rutas
    ruta_csv = r"C:\Users\javie\Escritorio\SOG2-2S26-Grupo15\data\processed\ventas_online_2025_limpio.csv"
    ruta_salida = r"C:\Users\javie\AppData\Local\Temp\claude\C--Users-javie-Escritorio-SOG2-2S26-Grupo15\1a3daf7e-0193-45ed-8aba-02e24e0e4fdb\scratchpad\resultados_analisis"

    # Crear directorio de salida
    Path(ruta_salida).mkdir(parents=True, exist_ok=True)

    print("=" * 70)
    print("ANÁLISIS ESTADÍSTICO - INTEGRANTE 2")
    print("=" * 70)
    print(f"\nArchivo de entrada: {ruta_csv}")
    print(f"Directorio de salida: {ruta_salida}\n")

    # Cargar datos
    print("Cargando datos...")
    df = pd.read_csv(ruta_csv)
    print(f"Datos cargados: {len(df)} filas, {len(df.columns)} columnas\n")

    # 1. ESTADÍSTICAS DESCRIPTIVAS
    print("=" * 70)
    print("1. ESTADÍSTICAS DESCRIPTIVAS")
    print("=" * 70)

    stats_df = EstadisticasDescriptivas.analizar_todas_variables(df)
    ruta_stats = f'{ruta_salida}/01_estadisticas_descriptivas.csv'
    stats_df.to_csv(ruta_stats, index=False)
    print(f"Archivo guardado: {ruta_stats}\n")
    print("Resumen de estadísticas:")
    print(stats_df[['variable', 'n_valores', 'media', 'mediana', 'desv_estandar', 'minimo', 'maximo']].to_string())

    # 2. ANÁLISIS DE TENDENCIAS TEMPORALES
    print("\n" + "=" * 70)
    print("2. ANÁLISIS DE TENDENCIAS TEMPORALES")
    print("=" * 70)

    if 'fecha_compra' in df.columns:
        df_temp = AnalisisTendencias.procesar_fechas(df, 'fecha_compra')
        print(f"Rango de fechas: {df_temp['fecha_compra'].min()} a {df_temp['fecha_compra'].max()}")

        # Tendencias mensuales
        variables_tendencia = ['venta_total', 'numero_compras', 'monto_compra']
        for var in variables_tendencia:
            if var in df.columns:
                tendencias = AnalisisTendencias.estadisticas_por_periodo(df, 'fecha_compra', var)
                ruta_tend = f'{ruta_salida}/02_tendencias_{var}.csv'
                tendencias.to_csv(ruta_tend, index=False)
                print(f"Archivo guardado: {ruta_tend}")
                print(f"\nTendencias de {var} por mes:")
                print(tendencias[['mes', 'mean', 'sum', 'count']].to_string())
                print()
    else:
        print("No se encontró columna de fecha.")

    # 3. SEGMENTACIÓN POR CATEGORÍAS
    print("\n" + "=" * 70)
    print("3. SEGMENTACIÓN POR CATEGORÍAS")
    print("=" * 70)

    # Por género
    if 'genero' in df.columns:
        print("\n3.1 Segmentación por género:")
        seg_genero = SegmentacionCategorias.segmentacion_multivariable(
            df, 'genero',
            ['venta_total', 'numero_compras', 'edad', 'monto_compra']
        )
        ruta_seg_genero = f'{ruta_salida}/03_segmentacion_genero.csv'
        seg_genero.to_csv(ruta_seg_genero, index=False)
        print(f"Archivo guardado: {ruta_seg_genero}")
        print(seg_genero.to_string())

    # Por método de pago
    if 'metodo_pago' in df.columns:
        print("\n3.2 Segmentación por método de pago:")
        seg_pago = SegmentacionCategorias.segmentacion_multivariable(
            df, 'metodo_pago',
            ['venta_total', 'numero_compras', 'edad']
        )
        ruta_seg_pago = f'{ruta_salida}/04_segmentacion_metodo_pago.csv'
        seg_pago.to_csv(ruta_seg_pago, index=False)
        print(f"Archivo guardado: {ruta_seg_pago}")
        print(seg_pago.to_string())

    # Por navegador
    if 'navegador' in df.columns:
        print("\n3.3 Segmentación por navegador:")
        seg_nav = SegmentacionCategorias.segmentacion_multivariable(
            df, 'navegador',
            ['venta_total', 'tiempo', 'numero_compras']
        )
        ruta_seg_nav = f'{ruta_salida}/05_segmentacion_navegador.csv'
        seg_nav.to_csv(ruta_seg_nav, index=False)
        print(f"Archivo guardado: {ruta_seg_nav}")
        print(seg_nav.head(10).to_string())

    # 4. MATRIZ DE CORRELACIÓN
    print("\n" + "=" * 70)
    print("4. MATRIZ DE CORRELACIÓN")
    print("=" * 70)

    matriz_corr = AnalisisCorrelacion.matriz_correlacion(df)
    ruta_corr = f'{ruta_salida}/06_matriz_correlacion_pearson.csv'
    matriz_corr.to_csv(ruta_corr)
    print(f"Archivo guardado: {ruta_corr}\n")
    print("Matriz de correlación (Pearson):")
    print(matriz_corr.to_string())

    # Correlaciones significativas
    print("\n4.1 Correlaciones significativas (umbral >= 0.30):")
    corr_sig = AnalisisCorrelacion.correlaciones_significativas(df, umbral=0.30)
    ruta_corr_sig = f'{ruta_salida}/07_correlaciones_significativas.json'
    with open(ruta_corr_sig, 'w', encoding='utf-8') as f:
        json.dump(corr_sig, f, indent=2, ensure_ascii=False)
    print(f"Archivo guardado: {ruta_corr_sig}\n")

    if corr_sig:
        print("Top 15 correlaciones:")
        for i, corr in enumerate(corr_sig[:15], 1):
            print(f"{i:2d}. {corr['variable_1']:15s} <-> {corr['variable_2']:15s}: {corr['correlacion']:7.4f} ({corr['fuerza']:12s}, {corr['tipo']})")
    else:
        print("No hay correlaciones significativas con el umbral especificado.")

    # 5. MATRIZ DE CORRELACIÓN SPEARMAN
    print("\n" + "=" * 70)
    print("5. MATRIZ DE CORRELACIÓN DE SPEARMAN")
    print("=" * 70)

    matriz_spearman = AnalisisCorrelacion.matriz_correlacion_spearman(df)
    ruta_spearman = f'{ruta_salida}/08_matriz_correlacion_spearman.csv'
    matriz_spearman.to_csv(ruta_spearman)
    print(f"Archivo guardado: {ruta_spearman}")

    # 6. RESUMEN FINAL
    print("\n" + "=" * 70)
    print("6. RESUMEN FINAL")
    print("=" * 70)

    resumen = {
        'timestamp': pd.Timestamp.now().isoformat(),
        'total_filas': len(df),
        'total_columnas': len(df.columns),
        'variables_numericas': len(df.select_dtypes(include=['number']).columns),
        'variables_categoricas': len(df.select_dtypes(exclude=['number']).columns),
        'columnas': list(df.columns),
        'tipos_datos': df.dtypes.astype(str).to_dict(),
        'estadisticas_basicas': {
            'filas': len(df),
            'columnas': len(df.columns),
            'valores_nulos_totales': int(df.isnull().sum().sum()),
            'porcentaje_valores_nulos': float((df.isnull().sum().sum() / (len(df) * len(df.columns)) * 100))
        }
    }

    ruta_resumen = f'{ruta_salida}/09_resumen_analisis.json'
    with open(ruta_resumen, 'w', encoding='utf-8') as f:
        json.dump(resumen, f, indent=2, ensure_ascii=False)
    print(f"Archivo guardado: {ruta_resumen}\n")

    print("Información del dataset:")
    for k, v in resumen['estadisticas_basicas'].items():
        print(f"  {k}: {v}")

    # Resumen de archivos generados
    print("\n" + "=" * 70)
    print("ARCHIVOS GENERADOS")
    print("=" * 70)

    archivos = sorted([f for f in os.listdir(ruta_salida) if os.path.isfile(os.path.join(ruta_salida, f))])
    for i, archivo in enumerate(archivos, 1):
        ruta_completa = os.path.join(ruta_salida, archivo)
        tamaño = os.path.getsize(ruta_completa) / 1024  # KB
        print(f"{i:2d}. {archivo:45s} ({tamaño:8.2f} KB)")

    print("\n" + "=" * 70)
    print("ANÁLISIS COMPLETADO EXITOSAMENTE")
    print("=" * 70)

if __name__ == "__main__":
    main()
