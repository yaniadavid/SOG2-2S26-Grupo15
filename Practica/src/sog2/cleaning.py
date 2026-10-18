from __future__ import annotations

import argparse
import csv
import hashlib
import json
import unicodedata
from collections import Counter, defaultdict
from datetime import datetime
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from pathlib import Path
from typing import Any


COLUMNAS_ORIGEN = [
    "Id_cliente",
    "Edad",
    "Genero",
    "Venta_total",
    "N_Compras",
    "FechaCompra",
    "MontoCompra",
    "MetodoPago",
    "Tiempo",
    "Navegador",
    "Boletín",
    "Vale",
]

COLUMNAS_SALIDA = [
    "fila_origen",
    "id_cliente",
    "edad",
    "genero",
    "venta_total",
    "numero_compras",
    "fecha_compra",
    "monto_compra",
    "metodo_pago",
    "tiempo",
    "navegador",
    "boletin",
    "vale",
    "problemas_calidad",
    "hash_fila",
]

VERSION_REGLAS = "1.0"
DOS_DECIMALES = Decimal("0.01")


def _texto_normalizado(valor: str) -> str:
    texto = unicodedata.normalize("NFKD", valor.strip().lower())
    return "".join(caracter for caracter in texto if not unicodedata.combining(caracter))


def _decimal(valor: str) -> tuple[Decimal, bool]:
    original = valor
    limpio = valor.strip().replace("$", "").replace('"', "").replace(" ", "")
    if not limpio:
        raise ValueError("valor decimal vacío")

    if "," in limpio and "." in limpio:
        if limpio.rfind(",") > limpio.rfind("."):
            limpio = limpio.replace(".", "").replace(",", ".")
        else:
            limpio = limpio.replace(",", "")
    elif "," in limpio:
        partes = limpio.split(",")
        if len(partes[-1]) == 2:
            limpio = "".join(partes[:-1]) + "." + partes[-1]
        else:
            limpio = "".join(partes)

    try:
        numero = Decimal(limpio).quantize(DOS_DECIMALES, rounding=ROUND_HALF_UP)
    except InvalidOperation as error:
        raise ValueError(f"decimal inválido: {original}") from error

    fue_normalizado = original != format(numero, ".2f")
    return numero, fue_normalizado


def _fecha(valor: str) -> datetime:
    limpio = valor.strip()
    formatos = (
        ("%Y/%m/%d", limpio[:4].isdigit() and "/" in limpio),
        ("%Y-%m-%d", limpio[:4].isdigit() and "-" in limpio),
        ("%m/%d/%Y", "/" in limpio and not limpio[:4].isdigit()),
        ("%d-%m-%Y", "-" in limpio and not limpio[:4].isdigit()),
    )
    for formato, aplica in formatos:
        if aplica:
            try:
                return datetime.strptime(limpio, formato)
            except ValueError:
                break
    raise ValueError(f"fecha inválida: {valor}")


def _entero_requerido(valor: str, campo: str, minimo: int | None = None) -> int:
    try:
        numero = int(valor.strip())
    except (TypeError, ValueError) as error:
        raise ValueError(f"{campo} inválido: {valor}") from error
    if minimo is not None and numero < minimo:
        raise ValueError(f"{campo} menor que {minimo}: {valor}")
    return numero


def _edad(valor: str, problemas: list[str]) -> int | None:
    if not valor.strip():
        problemas.append("edad_faltante")
        return None
    try:
        numero = int(valor.strip())
    except ValueError:
        problemas.append("edad_invalida")
        return None
    if numero <= 0 or numero > 100:
        problemas.append("edad_fuera_rango")
        return None
    if numero < 18:
        problemas.append("edad_menor_18")
    return numero


def _codigo(
    valor: str,
    validos: set[int],
    etiquetas: dict[str, int],
    campo: str,
    problemas: list[str],
) -> int | None:
    limpio = valor.strip()
    if not limpio:
        problemas.append(f"{campo}_faltante")
        return None

    etiqueta = _texto_normalizado(limpio)
    if etiqueta in etiquetas:
        problemas.append(f"{campo}_texto_normalizado")
        return etiquetas[etiqueta]

    try:
        numero = int(limpio)
    except ValueError:
        problemas.append(f"{campo}_invalido")
        return None
    if numero not in validos:
        problemas.append(f"{campo}_invalido")
        return None
    return numero


def _booleano(valor: str, campo: str, problemas: list[str]) -> bool | None:
    codigo = _codigo(
        valor,
        {0, 1},
        {"si": 1, "no": 0},
        campo,
        problemas,
    )
    if codigo is None:
        return None
    return bool(codigo)


def _valor_csv(valor: Any) -> str:
    if valor is None:
        return ""
    if isinstance(valor, bool):
        return "1" if valor else "0"
    if isinstance(valor, Decimal):
        return format(valor, ".2f")
    return str(valor)


def _limpiar_fila(fila: dict[str, str], numero_fila: int) -> dict[str, Any]:
    problemas: list[str] = []
    id_cliente = _entero_requerido(fila["Id_cliente"], "Id_cliente", 1)
    edad = _edad(fila["Edad"], problemas)
    genero = _codigo(
        fila["Genero"],
        {0, 1},
        {"masculino": 0, "femenino": 1},
        "genero",
        problemas,
    )

    venta_total, venta_normalizada = _decimal(fila["Venta_total"])
    if venta_normalizada:
        problemas.append("venta_total_formato_normalizado")
    if venta_total < 0:
        problemas.append("venta_total_negativa")

    numero_compras = _entero_requerido(fila["N_Compras"], "N_Compras", 0)
    fecha_compra = _fecha(fila["FechaCompra"]).date().isoformat()

    monto_compra, monto_normalizado = _decimal(fila["MontoCompra"])
    if monto_normalizado:
        problemas.append("monto_compra_formato_normalizado")
    if monto_compra < 0:
        problemas.append("monto_compra_negativo")
    if monto_compra > venta_total and venta_total >= 0:
        problemas.append("monto_mayor_venta_total")
    if numero_compras == 0 and venta_total != 0:
        problemas.append("compras_cero_con_venta")

    metodo_pago = _codigo(
        fila["MetodoPago"],
        {0, 1, 2},
        {},
        "metodo_pago",
        problemas,
    )

    tiempo, tiempo_normalizado = _decimal(fila["Tiempo"])
    if tiempo < 0:
        raise ValueError(f"Tiempo negativo en la fila {numero_fila}")
    if tiempo_normalizado and fila["Tiempo"].strip() != format(tiempo.normalize(), "f"):
        problemas.append("tiempo_formato_normalizado")

    navegador = _codigo(
        fila["Navegador"],
        {0, 1, 2, 3, 4},
        {},
        "navegador",
        problemas,
    )
    boletin = _booleano(fila["Boletín"], "boletin", problemas)
    vale = _booleano(fila["Vale"], "vale", problemas)

    limpia: dict[str, Any] = {
        "fila_origen": numero_fila,
        "id_cliente": id_cliente,
        "edad": edad,
        "genero": genero,
        "venta_total": venta_total,
        "numero_compras": numero_compras,
        "fecha_compra": fecha_compra,
        "monto_compra": monto_compra,
        "metodo_pago": metodo_pago,
        "tiempo": tiempo,
        "navegador": navegador,
        "boletin": boletin,
        "vale": vale,
        "problemas_calidad": "|".join(sorted(set(problemas))),
    }
    canonica = {clave: _valor_csv(valor) for clave, valor in limpia.items()}
    contenido_hash = json.dumps(canonica, ensure_ascii=False, sort_keys=True, separators=(",", ":"))
    limpia["hash_fila"] = hashlib.sha256(contenido_hash.encode("utf-8")).hexdigest()
    return limpia


def limpiar_archivo(origen: Path, destino: Path, reporte_destino: Path) -> dict[str, Any]:
    hash_origen = hashlib.sha256(origen.read_bytes()).hexdigest()
    filas_limpias: list[dict[str, Any]] = []
    filas_duplicadas: list[int] = []
    filas_vistas: set[tuple[str, ...]] = set()

    with origen.open("r", encoding="utf-8-sig", newline="") as archivo:
        lector = csv.DictReader(archivo)
        if lector.fieldnames != COLUMNAS_ORIGEN:
            raise ValueError(
                "Las columnas no coinciden. "
                f"Esperadas: {COLUMNAS_ORIGEN}. Recibidas: {lector.fieldnames}."
            )

        for numero_fila, fila in enumerate(lector, start=2):
            firma_original = tuple(fila[columna] for columna in COLUMNAS_ORIGEN)
            if firma_original in filas_vistas:
                filas_duplicadas.append(numero_fila)
                continue
            filas_vistas.add(firma_original)
            filas_limpias.append(_limpiar_fila(fila, numero_fila))

    destino.parent.mkdir(parents=True, exist_ok=True)
    with destino.open("w", encoding="utf-8", newline="") as archivo:
        escritor = csv.DictWriter(archivo, fieldnames=COLUMNAS_SALIDA, lineterminator="\n")
        escritor.writeheader()
        for fila in filas_limpias:
            escritor.writerow({clave: _valor_csv(fila[clave]) for clave in COLUMNAS_SALIDA})

    ids: dict[int, list[int]] = defaultdict(list)
    incidencias: Counter[str] = Counter()
    for fila in filas_limpias:
        ids[fila["id_cliente"]].append(fila["fila_origen"])
        if fila["problemas_calidad"]:
            incidencias.update(fila["problemas_calidad"].split("|"))

    ids_repetidos = {
        str(id_cliente): numeros
        for id_cliente, numeros in sorted(ids.items())
        if len(numeros) > 1
    }
    filas_leidas = len(filas_limpias) + len(filas_duplicadas)
    reporte = {
        "archivo_origen": origen.name,
        "sha256_origen": hash_origen,
        "version_reglas": VERSION_REGLAS,
        "filas_leidas": filas_leidas,
        "filas_salida": len(filas_limpias),
        "duplicados_exactos_eliminados": len(filas_duplicadas),
        "filas_duplicadas_eliminadas": filas_duplicadas,
        "ids_repetidos_con_datos_distintos": ids_repetidos,
        "cantidad_ids_repetidos_con_datos_distintos": len(ids_repetidos),
        "incidencias_en_filas_conservadas": dict(sorted(incidencias.items())),
    }
    reporte_destino.parent.mkdir(parents=True, exist_ok=True)
    reporte_destino.write_text(
        json.dumps(reporte, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    return reporte


def main() -> None:
    parser = argparse.ArgumentParser(description="Limpia y valida el archivo de ventas online.")
    parser.add_argument("--origen", type=Path, default=Path("ventas_online_2025.csv"))
    parser.add_argument(
        "--destino",
        type=Path,
        default=Path("data/processed/ventas_online_2025_limpio.csv"),
    )
    parser.add_argument(
        "--reporte",
        type=Path,
        default=Path("data/processed/reporte_calidad.json"),
    )
    argumentos = parser.parse_args()
    resultado = limpiar_archivo(argumentos.origen, argumentos.destino, argumentos.reporte)
    print(
        f"Limpieza terminada: {resultado['filas_salida']} filas guardadas y "
        f"{resultado['duplicados_exactos_eliminados']} duplicados eliminados."
    )


if __name__ == "__main__":
    main()

