"""Generador puro de tarjetas PNG originales (800x800) solo con zlib y struct."""
import hashlib
import struct
import zlib

LADO = 800
CELDAS = 8
FIRMA_PNG = b"\x89PNG\r\n\x1a\n"


def color_base(codigo: str) -> tuple:
    """Color RGB estable derivado del default_code, en un rango medio para buen contraste."""
    resumen = hashlib.sha256(codigo.encode("utf-8")).digest()
    return tuple(60 + resumen[i] % 140 for i in range(3))


def aclarar(color: tuple, factor: float) -> tuple:
    return tuple(int(c + (255 - c) * factor) for c in color)


def oscurecer(color: tuple, factor: float) -> tuple:
    return tuple(int(c * (1 - factor)) for c in color)


def color_celda(fila: int, columna: int, base: tuple) -> tuple:
    """Anillos concentricos alternados; las diagonales principales van mas oscuras."""
    if fila == columna or fila + columna == CELDAS - 1:
        return oscurecer(base, 0.35)
    anillo = min(fila, columna, CELDAS - 1 - fila, CELDAS - 1 - columna)
    return base if anillo % 2 == 0 else aclarar(base, 0.45)


def fila_pixeles(fila_celda: int, base: tuple, lado: int) -> bytes:
    ancho_celda = lado // CELDAS
    return b"".join(bytes(color_celda(fila_celda, c, base)) * ancho_celda for c in range(CELDAS))


def chunk(tipo: bytes, datos: bytes) -> bytes:
    cuerpo = tipo + datos
    return struct.pack(">I", len(datos)) + cuerpo + struct.pack(">I", zlib.crc32(cuerpo) & 0xFFFFFFFF)


def generar_png(codigo: str, lado: int = LADO) -> bytes:
    """Devuelve los bytes de un PNG RGB de lado x lado (lado multiplo de 8)."""
    if lado % CELDAS:
        raise ValueError("El lado debe ser multiplo de %d" % CELDAS)
    base = color_base(codigo)
    alto_celda = lado // CELDAS
    crudo = bytearray()
    for fila_celda in range(CELDAS):
        linea = b"\x00" + fila_pixeles(fila_celda, base, lado)
        crudo += linea * alto_celda
    cabecera = struct.pack(">IIBBBBB", lado, lado, 8, 2, 0, 0, 0)
    return (FIRMA_PNG + chunk(b"IHDR", cabecera)
            + chunk(b"IDAT", zlib.compress(bytes(crudo), 9)) + chunk(b"IEND", b""))


def leer_dimensiones(png: bytes) -> tuple:
    """Valida firma y CRC del IHDR y devuelve (ancho, alto)."""
    if png[:8] != FIRMA_PNG:
        raise ValueError("Firma PNG invalida")
    longitud, tipo = struct.unpack(">I4s", png[8:16])
    if tipo != b"IHDR" or longitud != 13:
        raise ValueError("IHDR ausente")
    datos = png[16:29]
    if struct.unpack(">I", png[29:33])[0] != zlib.crc32(tipo + datos) & 0xFFFFFFFF:
        raise ValueError("CRC del IHDR invalido")
    return struct.unpack(">II", datos[:8])


def descomprimir_idat(png: bytes) -> bytes:
    posicion, idat = 8, b""
    while posicion < len(png):
        longitud, tipo = struct.unpack(">I4s", png[posicion:posicion + 8])
        if tipo == b"IDAT":
            idat += png[posicion + 8:posicion + 8 + longitud]
        posicion += 12 + longitud
    return zlib.decompress(idat)


def prueba_local() -> None:
    png = generar_png("I1-PV-001")
    ancho, alto = leer_dimensiones(png)
    assert (ancho, alto) == (LADO, LADO), (ancho, alto)
    assert len(descomprimir_idat(png)) == LADO * (1 + 3 * LADO)
    assert generar_png("I1-PV-001") == png, "debe ser determinista"
    assert generar_png("I1-PV-002") != png, "colores distintos por codigo"
    print(f"OK PNG {ancho}x{alto}, {len(png)} bytes, firma y datos validos")


if __name__ == "__main__":
    prueba_local()
