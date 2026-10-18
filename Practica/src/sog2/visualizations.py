from __future__ import annotations

import argparse
import os
from pathlib import Path
from typing import Optional

os.environ.setdefault("MPLCONFIGDIR", str(Path.cwd() / ".matplotlib-cache"))

import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np
import pandas as pd
import seaborn as sns
from matplotlib.backends.backend_pdf import PdfPages


ESTILO_ACADEMICO = {
    "font.family": "sans-serif",
    "font.size": 10,
    "axes.labelsize": 11,
    "axes.titlesize": 13,
    "xtick.labelsize": 9,
    "ytick.labelsize": 9,
    "legend.fontsize": 9,
    "figure.titlesize": 14,
    "axes.grid": True,
    "grid.alpha": 0.3,
    "axes.edgecolor": "black",
    "axes.linewidth": 1.2,
}

PALETA_COLORES = {
    "primario": "#2E86AB",
    "secundario": "#A23B72",
    "terciario": "#F18F01",
    "cuaternario": "#C73E1D",
    "quinto": "#6A994E",
    "sexto": "#BC4749",
}

GENERO_ETIQUETAS = {0: "Masculino", 1: "Femenino"}
METODO_PAGO_ETIQUETAS = {0: "Efectivo", 1: "Tarjeta credito", 2: "Tarjeta debito"}
NAVEGADOR_ETIQUETAS = {
    0: "Tienda fisica",
    1: "Navegador 1",
    2: "Navegador 2",
    3: "Navegador 3",
    4: "Navegador 4",
}


def _validar_datos(df: pd.DataFrame) -> pd.DataFrame:
    """Valida y limpia datos para visualización."""
    df = df.copy()

    if "edad" in df.columns:
        df = df[(df["edad"] > 0) & (df["edad"] <= 100)]

    if "venta_total" in df.columns:
        df = df[df["venta_total"].notna()]

    if "monto_compra" in df.columns:
        df = df[df["monto_compra"].notna()]

    if "numero_compras" in df.columns:
        df = df[df["numero_compras"] >= 0]

    if "tiempo" in df.columns:
        df = df[(df["tiempo"] >= 0) & (df["tiempo"].notna())]

    return df


def _preparar_fecha_mes(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df["fecha_compra"] = pd.to_datetime(df["fecha_compra"])
    df["mes"] = df["fecha_compra"].dt.month
    return df


def grafica_venta_total_por_mes(
    df: pd.DataFrame,
    titulo: str = "Venta total por mes",
    figsize: tuple = (12, 6),
) -> plt.Figure:
    """Genera grafica de linea con venta total acumulada por mes."""
    df_valido = _preparar_fecha_mes(_validar_datos(df))
    mensual = df_valido.groupby("mes")["venta_total"].sum().reindex(range(1, 13), fill_value=0)

    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(mensual.index, mensual.values, color=PALETA_COLORES["primario"], marker="o", linewidth=2.5)
    ax.set_xlabel("Mes", fontweight="bold")
    ax.set_ylabel("Venta total ($)", fontweight="bold")
    ax.set_title(titulo, fontweight="bold", pad=20)
    ax.set_xticks(range(1, 13))
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"${x:,.0f}"))
    fig.tight_layout()
    return fig


def grafica_barras_metodo_pago(
    df: pd.DataFrame,
    titulo: str = "Distribucion de ventas por metodo de pago",
    figsize: tuple = (10, 6),
) -> plt.Figure:
    """Genera barras de transacciones por metodo de pago."""
    df_valido = _validar_datos(df)
    conteos = df_valido["metodo_pago"].value_counts(dropna=False).sort_index()
    etiquetas = [METODO_PAGO_ETIQUETAS.get(int(i), "Sin dato") if pd.notna(i) else "Sin dato" for i in conteos.index]

    fig, ax = plt.subplots(figsize=figsize)
    barras = ax.bar(etiquetas, conteos.values, color=PALETA_COLORES["primario"], alpha=0.85, edgecolor="black")
    ax.set_ylabel("Transacciones", fontweight="bold")
    ax.set_title(titulo, fontweight="bold", pad=20)
    ax.grid(axis="y", alpha=0.3)
    for barra in barras:
        ax.text(barra.get_x() + barra.get_width() / 2, barra.get_height(), f"{int(barra.get_height())}", ha="center", va="bottom")
    fig.tight_layout()
    return fig


def grafica_venta_por_navegador(
    df: pd.DataFrame,
    titulo: str = "Venta total por navegador",
    figsize: tuple = (10, 6),
) -> plt.Figure:
    """Genera barras de venta total por navegador/canal."""
    df_valido = _validar_datos(df)
    ventas = df_valido.groupby("navegador")["venta_total"].sum().sort_index()
    etiquetas = [NAVEGADOR_ETIQUETAS.get(int(i), "Sin dato") if pd.notna(i) else "Sin dato" for i in ventas.index]

    fig, ax = plt.subplots(figsize=figsize)
    barras = ax.bar(etiquetas, ventas.values, color=PALETA_COLORES["quinto"], alpha=0.85, edgecolor="black")
    ax.set_ylabel("Venta total ($)", fontweight="bold")
    ax.set_title(titulo, fontweight="bold", pad=20)
    ax.tick_params(axis="x", rotation=20)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"${x:,.0f}"))
    for barra in barras:
        ax.text(barra.get_x() + barra.get_width() / 2, barra.get_height(), f"${barra.get_height():,.0f}", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    return fig


def grafica_boletin_por_mes(
    df: pd.DataFrame,
    titulo: str = "Uso de boletin por mes",
    figsize: tuple = (12, 6),
) -> plt.Figure:
    """Genera barras mensuales de compras con boletin."""
    return _grafica_booleano_por_mes(df, "boletin", titulo, figsize, PALETA_COLORES["secundario"])


def grafica_vale_por_mes(
    df: pd.DataFrame,
    titulo: str = "Uso de vale por mes",
    figsize: tuple = (12, 6),
) -> plt.Figure:
    """Genera barras mensuales de compras con vale."""
    return _grafica_booleano_por_mes(df, "vale", titulo, figsize, PALETA_COLORES["terciario"])


def _grafica_booleano_por_mes(
    df: pd.DataFrame,
    columna: str,
    titulo: str,
    figsize: tuple,
    color: str,
) -> plt.Figure:
    df_valido = _preparar_fecha_mes(_validar_datos(df))
    conteos = df_valido[df_valido[columna] == 1].groupby("mes").size().reindex(range(1, 13), fill_value=0)

    fig, ax = plt.subplots(figsize=figsize)
    barras = ax.bar(conteos.index, conteos.values, color=color, alpha=0.85, edgecolor="black")
    ax.set_xlabel("Mes", fontweight="bold")
    ax.set_ylabel("Transacciones", fontweight="bold")
    ax.set_title(titulo, fontweight="bold", pad=20)
    ax.set_xticks(range(1, 13))
    for barra in barras:
        ax.text(barra.get_x() + barra.get_width() / 2, barra.get_height(), f"{int(barra.get_height())}", ha="center", va="bottom", fontsize=8)
    fig.tight_layout()
    return fig


def grafica_venta_promedio_genero_navegador(
    df: pd.DataFrame,
    titulo: str = "Venta promedio por genero y navegador",
    figsize: tuple = (12, 6),
) -> plt.Figure:
    """Genera barras agrupadas de venta promedio por genero y navegador."""
    df_valido = _validar_datos(df).copy()
    df_valido["genero_label"] = df_valido["genero"].map(GENERO_ETIQUETAS)
    df_valido["navegador_label"] = df_valido["navegador"].map(NAVEGADOR_ETIQUETAS)
    tabla = df_valido.pivot_table(
        index="genero_label",
        columns="navegador_label",
        values="venta_total",
        aggfunc="mean",
    )

    fig, ax = plt.subplots(figsize=figsize)
    tabla.plot(kind="bar", ax=ax, width=0.82)
    ax.set_xlabel("Genero", fontweight="bold")
    ax.set_ylabel("Venta promedio ($)", fontweight="bold")
    ax.set_title(titulo, fontweight="bold", pad=20)
    ax.tick_params(axis="x", rotation=0)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"${x:,.0f}"))
    ax.legend(title="Navegador", fontsize=8)
    fig.tight_layout()
    return fig


def grafica_distribucion_edades(
    df: pd.DataFrame,
    titulo: str = "Distribución de Edades de Clientes",
    color: str = None,
    bins: int = 20,
    figsize: tuple = (10, 6),
) -> plt.Figure:
    """
    Genera histograma de distribución de edades.

    Parámetros:
        df: DataFrame con datos
        titulo: Título de la gráfica
        color: Color de las barras (por defecto primario)
        bins: Número de bins del histograma
        figsize: Tamaño de la figura (ancho, alto)

    Retorna:
        Figure de matplotlib
    """
    color = color or PALETA_COLORES["primario"]
    df_valido = _validar_datos(df)

    fig, ax = plt.subplots(figsize=figsize)
    ax.hist(df_valido["edad"], bins=bins, color=color, alpha=0.7, edgecolor="black")

    ax.set_xlabel("Edad (años)", fontweight="bold")
    ax.set_ylabel("Frecuencia", fontweight="bold")
    ax.set_title(titulo, fontweight="bold", pad=20)
    ax.grid(axis="y", alpha=0.3)

    media = df_valido["edad"].mean()
    mediana = df_valido["edad"].median()
    ax.axvline(media, color=PALETA_COLORES["secundario"], linestyle="--",
               linewidth=2, label=f"Media: {media:.1f}")
    ax.axvline(mediana, color=PALETA_COLORES["terciario"], linestyle="--",
               linewidth=2, label=f"Mediana: {mediana:.1f}")
    ax.legend(loc="upper right")

    fig.tight_layout()
    return fig


def grafica_distribucion_genero(
    df: pd.DataFrame,
    titulo: str = "Distribución por Género",
    figsize: tuple = (10, 6),
) -> plt.Figure:
    """
    Genera gráfica de barras de distribución de género.

    Parámetros:
        df: DataFrame con datos
        titulo: Título de la gráfica
        figsize: Tamaño de la figura

    Retorna:
        Figure de matplotlib
    """
    df_valido = _validar_datos(df)
    genero_counts = df_valido["genero"].value_counts().sort_index()
    genero_labels = [GENERO_ETIQUETAS.get(i, f"Desconocido") for i in genero_counts.index]

    fig, ax = plt.subplots(figsize=figsize)
    colores = [PALETA_COLORES["primario"], PALETA_COLORES["secundario"]]
    barras = ax.bar(genero_labels, genero_counts.values, color=colores[:len(genero_labels)],
                    alpha=0.8, edgecolor="black", linewidth=1.5)

    ax.set_ylabel("Cantidad de Clientes", fontweight="bold")
    ax.set_title(titulo, fontweight="bold", pad=20)
    ax.grid(axis="y", alpha=0.3)

    for barra in barras:
        altura = barra.get_height()
        ax.text(barra.get_x() + barra.get_width()/2., altura,
                f"{int(altura)}",
                ha="center", va="bottom", fontweight="bold")

    fig.tight_layout()
    return fig


def grafica_tendencia_ventas(
    df: pd.DataFrame,
    titulo: str = "Tendencia de Ventas en el Tiempo",
    figsize: tuple = (12, 6),
) -> plt.Figure:
    """
    Genera gráfica de línea mostrando tendencia de ventas totales en el tiempo.

    Parámetros:
        df: DataFrame con datos
        titulo: Título de la gráfica
        figsize: Tamaño de la figura

    Retorna:
        Figure de matplotlib
    """
    df_valido = _validar_datos(df)
    df_ordenado = df_valido.sort_values("fecha_compra")

    df_ordenado["cumulative_ventas"] = df_ordenado["venta_total"].cumsum()

    fig, ax = plt.subplots(figsize=figsize)
    ax.plot(range(len(df_ordenado)), df_ordenado["cumulative_ventas"].values,
            color=PALETA_COLORES["primario"], linewidth=2.5, marker="o",
            markersize=4, alpha=0.7)

    ax.set_xlabel("Número de Transacción", fontweight="bold")
    ax.set_ylabel("Ventas Acumuladas ($)", fontweight="bold")
    ax.set_title(titulo, fontweight="bold", pad=20)
    ax.grid(alpha=0.3)

    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, p: f"${x/1000:.0f}K"))

    fig.tight_layout()
    return fig


def grafica_scatter_edad_ventas(
    df: pd.DataFrame,
    titulo: str = "Correlación entre Edad y Ventas Totales",
    figsize: tuple = (10, 6),
) -> plt.Figure:
    """
    Genera gráfica scatter mostrando relación entre edad y ventas totales.

    Parámetros:
        df: DataFrame con datos
        titulo: Título de la gráfica
        figsize: Tamaño de la figura

    Retorna:
        Figure de matplotlib
    """
    df_valido = _validar_datos(df)

    fig, ax = plt.subplots(figsize=figsize)
    scatter = ax.scatter(df_valido["edad"], df_valido["venta_total"],
                         alpha=0.6, s=80, c=df_valido["numero_compras"],
                         cmap="viridis", edgecolors="black", linewidth=0.5)

    z = np.polyfit(df_valido["edad"], df_valido["venta_total"], 1)
    p = np.poly1d(z)
    x_linea = np.linspace(df_valido["edad"].min(), df_valido["edad"].max(), 100)
    ax.plot(x_linea, p(x_linea), color=PALETA_COLORES["secundario"],
            linewidth=2.5, linestyle="--", alpha=0.8, label="Tendencia")

    ax.set_xlabel("Edad (años)", fontweight="bold")
    ax.set_ylabel("Ventas Totales ($)", fontweight="bold")
    ax.set_title(titulo, fontweight="bold", pad=20)
    ax.grid(alpha=0.3)
    ax.legend()

    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Número de Compras", fontweight="bold")

    fig.tight_layout()
    return fig


def grafica_matriz_correlacion(
    df: pd.DataFrame,
    titulo: str = "Matriz de Correlación entre Variables",
    figsize: tuple = (10, 8),
) -> plt.Figure:
    """
    Genera heatmap de matriz de correlación entre variables numéricas.

    Parámetros:
        df: DataFrame con datos
        titulo: Título de la gráfica
        figsize: Tamaño de la figura

    Retorna:
        Figure de matplotlib
    """
    df_valido = _validar_datos(df)

    columnas_numericas = [
        "edad", "venta_total", "numero_compras", "monto_compra", "tiempo"
    ]
    df_numerico = df_valido[columnas_numericas].astype(float)

    correlacion = df_numerico.corr()

    fig, ax = plt.subplots(figsize=figsize)
    sns.heatmap(correlacion, annot=True, fmt=".2f", cmap="coolwarm", center=0,
                square=True, linewidths=1, cbar_kws={"shrink": 0.8}, ax=ax,
                vmin=-1, vmax=1)

    ax.set_title(titulo, fontweight="bold", pad=20)
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right")
    plt.setp(ax.get_yticklabels(), rotation=0)

    fig.tight_layout()
    return fig


def grafica_boxplot_monto_genero(
    df: pd.DataFrame,
    titulo: str = "Distribución de Montos por Género",
    figsize: tuple = (10, 6),
) -> plt.Figure:
    """
    Genera boxplot mostrando distribución de montos de compra por género.

    Parámetros:
        df: DataFrame con datos
        titulo: Título de la gráfica
        figsize: Tamaño de la figura

    Retorna:
        Figure de matplotlib
    """
    df_valido = _validar_datos(df)

    df_valido["genero_label"] = df_valido["genero"].map(GENERO_ETIQUETAS)

    fig, ax = plt.subplots(figsize=figsize)
    colores = [PALETA_COLORES["primario"], PALETA_COLORES["secundario"]]

    bp = ax.boxplot(
        [df_valido[df_valido["genero"] == 0]["monto_compra"].dropna(),
         df_valido[df_valido["genero"] == 1]["monto_compra"].dropna()],
        labels=["Masculino", "Femenino"],
        patch_artist=True,
        widths=0.6,
    )

    for patch, color in zip(bp["boxes"], colores):
        patch.set_facecolor(color)
        patch.set_alpha(0.7)

    for elemento in ["whiskers", "fliers", "means", "medians", "caps"]:
        plt.setp(bp[elemento], color="black", linewidth=1.5)

    ax.set_ylabel("Monto de Compra ($)", fontweight="bold")
    ax.set_title(titulo, fontweight="bold", pad=20)
    ax.grid(axis="y", alpha=0.3)

    fig.tight_layout()
    return fig


def grafica_pastel_metodo_pago(
    df: pd.DataFrame,
    titulo: str = "Distribución de Métodos de Pago",
    figsize: tuple = (10, 7),
) -> plt.Figure:
    """
    Genera gráfica de pastel mostrando distribución de métodos de pago.

    Parámetros:
        df: DataFrame con datos
        titulo: Título de la gráfica
        figsize: Tamaño de la figura

    Retorna:
        Figure de matplotlib
    """
    df_valido = _validar_datos(df)

    metodo_counts = df_valido["metodo_pago"].value_counts().sort_index()
    metodo_labels = [METODO_PAGO_ETIQUETAS.get(i, f"Desconocido") for i in metodo_counts.index]

    fig, ax = plt.subplots(figsize=figsize)
    colores = [PALETA_COLORES["primario"], PALETA_COLORES["secundario"],
               PALETA_COLORES["terciario"]]

    wedges, texts, autotexts = ax.pie(
        metodo_counts.values,
        labels=metodo_labels,
        autopct="%1.1f%%",
        colors=colores[:len(metodo_labels)],
        startangle=90,
        textprops={"fontweight": "bold", "fontsize": 10},
    )

    for autotext in autotexts:
        autotext.set_color("white")
        autotext.set_fontweight("bold")
        autotext.set_fontsize(11)

    ax.set_title(titulo, fontweight="bold", pad=20)

    fig.tight_layout()
    return fig


def grafica_barras_navegadores(
    df: pd.DataFrame,
    titulo: str = "Navegadores Más Utilizados",
    figsize: tuple = (10, 6),
    top_n: int = 5,
) -> plt.Figure:
    """
    Genera gráfica de barras horizontal mostrando navegadores más usados.

    Parámetros:
        df: DataFrame con datos
        titulo: Título de la gráfica
        figsize: Tamaño de la figura
        top_n: Número de navegadores a mostrar

    Retorna:
        Figure de matplotlib
    """
    df_valido = _validar_datos(df)

    navegador_counts = df_valido["navegador"].value_counts().head(top_n).sort_values()
    navegador_labels = [NAVEGADOR_ETIQUETAS.get(i, f"Desconocido") for i in navegador_counts.index]

    fig, ax = plt.subplots(figsize=figsize)
    colores_gradiente = [PALETA_COLORES["primario"] if i < top_n/2
                         else PALETA_COLORES["secundario"]
                         for i in range(len(navegador_labels))]

    barras = ax.barh(navegador_labels, navegador_counts.values, color=colores_gradiente,
                     alpha=0.8, edgecolor="black", linewidth=1.5)

    ax.set_xlabel("Cantidad de Usuarios", fontweight="bold")
    ax.set_title(titulo, fontweight="bold", pad=20)
    ax.grid(axis="x", alpha=0.3)

    for i, barra in enumerate(barras):
        ancho = barra.get_width()
        ax.text(ancho, barra.get_y() + barra.get_height()/2.,
                f" {int(ancho)}",
                ha="left", va="center", fontweight="bold", fontsize=10)

    fig.tight_layout()
    return fig


def grafica_segmentacion_cliente(
    df: pd.DataFrame,
    titulo: str = "Segmentación de Clientes por Valor y Frecuencia",
    figsize: tuple = (11, 7),
) -> plt.Figure:
    """
    Genera scatter plot mostrando segmentación de clientes.

    Parámetros:
        df: DataFrame con datos
        titulo: Título de la gráfica
        figsize: Tamaño de la figura

    Retorna:
        Figure de matplotlib
    """
    df_valido = _validar_datos(df)

    fig, ax = plt.subplots(figsize=figsize)

    scatter = ax.scatter(df_valido["numero_compras"], df_valido["venta_total"],
                        s=df_valido["tiempo"]*10, alpha=0.6, c=df_valido["edad"],
                        cmap="plasma", edgecolors="black", linewidth=0.5)

    mediana_compras = df_valido["numero_compras"].median()
    mediana_ventas = df_valido["venta_total"].median()

    ax.axvline(mediana_compras, color="red", linestyle="--", linewidth=2, alpha=0.7)
    ax.axhline(mediana_ventas, color="red", linestyle="--", linewidth=2, alpha=0.7)

    ax.text(df_valido["numero_compras"].max() * 0.95, mediana_ventas * 1.05,
            "VIP", fontsize=12, fontweight="bold", ha="right",
            bbox=dict(boxstyle="round", facecolor=PALETA_COLORES["primario"], alpha=0.7))
    ax.text(df_valido["numero_compras"].min() * 1.05, mediana_ventas * 0.95,
            "Ocasional", fontsize=12, fontweight="bold", ha="left",
            bbox=dict(boxstyle="round", facecolor=PALETA_COLORES["secundario"], alpha=0.7))

    ax.set_xlabel("Número de Compras", fontweight="bold")
    ax.set_ylabel("Ventas Totales ($)", fontweight="bold")
    ax.set_title(titulo, fontweight="bold", pad=20)
    ax.grid(alpha=0.3)

    cbar = plt.colorbar(scatter, ax=ax)
    cbar.set_label("Edad del Cliente", fontweight="bold")

    fig.tight_layout()
    return fig


def exportar_visualizaciones(
    archivo_datos: Path,
    directorio_salida: Path,
    formato: str = "png",
    dpi: int = 300,
) -> dict[str, Path]:
    """
    Genera y exporta todas las visualizaciones.

    Parámetros:
        archivo_datos: Ruta del archivo CSV limpio
        directorio_salida: Directorio donde guardar las gráficas
        formato: Formato de exportación ("png", "pdf", o "ambos")
        dpi: Resolución de las imágenes (dots per inch)

    Retorna:
        Diccionario con rutas de los archivos generados
    """
    plt.rcParams.update(ESTILO_ACADEMICO)

    df = pd.read_csv(archivo_datos)
    directorio_salida.mkdir(parents=True, exist_ok=True)

    archivos_generados = {}

    visualizaciones = [
        ("01_venta_total_por_mes", grafica_venta_total_por_mes, {}),
        ("02_barras_metodo_pago", grafica_barras_metodo_pago, {}),
        ("03_venta_por_navegador", grafica_venta_por_navegador, {}),
        ("04_boletin_por_mes", grafica_boletin_por_mes, {}),
        ("05_vale_por_mes", grafica_vale_por_mes, {}),
        ("06_scatter_edad_ventas", grafica_scatter_edad_ventas, {}),
        ("07_genero_navegador", grafica_venta_promedio_genero_navegador, {}),
        ("08_distribucion_edades", grafica_distribucion_edades, {}),
        ("09_matriz_correlacion", grafica_matriz_correlacion, {}),
    ]

    for nombre, funcion, kwargs in visualizaciones:
        print(f"Generando {nombre}...")
        fig = funcion(df, **kwargs)

        if formato in ("png", "ambos"):
            archivo_png = directorio_salida / f"{nombre}.png"
            fig.savefig(archivo_png, dpi=dpi, bbox_inches="tight", facecolor="white")
            archivos_generados[f"{nombre}.png"] = archivo_png
            print(f"  Guardado: {archivo_png}")

        if formato in ("pdf", "ambos"):
            archivo_pdf = directorio_salida / f"{nombre}.pdf"
            fig.savefig(archivo_pdf, format="pdf", bbox_inches="tight", facecolor="white")
            archivos_generados[f"{nombre}.pdf"] = archivo_pdf
            print(f"  Guardado: {archivo_pdf}")

        plt.close(fig)

    if formato in ("pdf", "ambos"):
        archivo_pdf_combinado = directorio_salida / "visualizaciones_completas.pdf"
        with PdfPages(archivo_pdf_combinado) as pdf:
            for nombre, funcion, kwargs in visualizaciones:
                fig = funcion(df, **kwargs)
                pdf.savefig(fig, bbox_inches="tight")
                plt.close(fig)

        archivos_generados["visualizaciones_completas.pdf"] = archivo_pdf_combinado
        print(f"PDF combinado guardado: {archivo_pdf_combinado}")

    print(f"\nTotal de archivos generados: {len(archivos_generados)}")
    return archivos_generados


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Genera visualizaciones académicas profesionales de datos de ventas."
    )
    parser.add_argument(
        "--datos",
        type=Path,
        default=Path("data/processed/ventas_online_2025_limpio.csv"),
        help="Ruta del archivo CSV con datos limpios",
    )
    parser.add_argument(
        "--salida",
        type=Path,
        default=Path("visualizations"),
        help="Directorio de salida para las gráficas",
    )
    parser.add_argument(
        "--formato",
        choices=["png", "pdf", "ambos"],
        default="ambos",
        help="Formato de exportación",
    )
    parser.add_argument(
        "--dpi",
        type=int,
        default=300,
        help="Resolución de las imágenes (dpi)",
    )

    argumentos = parser.parse_args()

    archivos = exportar_visualizaciones(
        argumentos.datos,
        argumentos.salida,
        formato=argumentos.formato,
        dpi=argumentos.dpi,
    )

    print("\nArchivos generados:")
    for nombre, ruta in archivos.items():
        print(f"  - {nombre}: {ruta}")


if __name__ == "__main__":
    main()
