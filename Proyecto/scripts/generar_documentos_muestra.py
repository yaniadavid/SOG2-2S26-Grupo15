"""Generate the 15 fictional PDFs used to demonstrate QuetzalMart DMS.

No names, tax identifiers, addresses, or signatures represent real people.
Run: python Proyecto/scripts/generar_documentos_muestra.py
"""

from __future__ import annotations

import json
from pathlib import Path

from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import (
    BaseDocTemplate,
    Frame,
    KeepTogether,
    PageTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)


ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / "output" / "pdf" / "gestion_documental"
NAVY = colors.HexColor("#17324D")
TEAL = colors.HexColor("#148A88")
INK = colors.HexColor("#263746")
MUTED = colors.HexColor("#647687")
PALE = colors.HexColor("#EAF3F5")

STYLES = {
    "eyebrow": ParagraphStyle("eyebrow", fontName="Helvetica-Bold", fontSize=9, textColor=TEAL, spaceAfter=5),
    "title": ParagraphStyle("title", fontName="Helvetica-Bold", fontSize=18, leading=21, textColor=NAVY, spaceAfter=9),
    "subtitle": ParagraphStyle("subtitle", fontName="Helvetica", fontSize=10, leading=14, textColor=MUTED, spaceAfter=16),
    "head": ParagraphStyle("head", fontName="Helvetica-Bold", fontSize=10, leading=14, textColor=NAVY, spaceBefore=14, spaceAfter=6),
    "body": ParagraphStyle("body", fontName="Helvetica", fontSize=9, leading=14, textColor=INK, spaceAfter=8),
    "small": ParagraphStyle("small", fontName="Helvetica", fontSize=8, leading=11, textColor=MUTED),
    "table_head": ParagraphStyle("table_head", fontName="Helvetica-Bold", fontSize=8, leading=10, textColor=colors.white),
    "table": ParagraphStyle("table", fontName="Helvetica", fontSize=8, leading=11, textColor=INK),
    "right": ParagraphStyle("right", fontName="Helvetica-Bold", fontSize=9, leading=12, alignment=TA_RIGHT, textColor=NAVY),
}


def para(text: str, style: str = "body") -> Paragraph:
    return Paragraph(text, STYLES[style])


def page(canvas, doc):
    canvas.saveState()
    w, h = doc.pagesize
    canvas.setFillColor(NAVY)
    canvas.rect(0, h - 1.55 * cm, w, 1.55 * cm, stroke=0, fill=1)
    canvas.setFont("Helvetica-Bold", 11)
    canvas.setFillColor(colors.white)
    canvas.drawString(2 * cm, h - 0.95 * cm, "QUETZALMART  /  ARCHIVO DE DEMOSTRACION")
    canvas.setStrokeColor(colors.HexColor("#D6E4E9"))
    canvas.line(2 * cm, 1.75 * cm, w - 2 * cm, 1.75 * cm)
    canvas.setFont("Helvetica", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(2 * cm, 1.34 * cm, "DOCUMENTO FICTICIO - SOLO PARA PRACTICA ACADEMICA")
    canvas.drawRightString(w - 2 * cm, 1.34 * cm, f"Pagina {doc.page}")
    canvas.restoreState()


def build(path: Path, content: list):
    doc = BaseDocTemplate(str(path), pagesize=(21 * cm, 29.7 * cm),
                          leftMargin=2 * cm, rightMargin=2 * cm,
                          topMargin=2.1 * cm, bottomMargin=2.15 * cm,
                          title=path.stem.replace("_", " "), author="QuetzalMart - datos ficticios")
    frame = Frame(doc.leftMargin, doc.bottomMargin, doc.width, doc.height,
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc.addPageTemplates(PageTemplate(id="main", frames=[frame], onPage=page))
    doc.build(content)


def info(rows):
    data = [[para(k, "table"), para(v, "table")] for k, v in rows]
    t = Table(data, colWidths=[4 * cm, 13 * cm], hAlign="LEFT")
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), PALE),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 9),
        ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 7),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
        ("LINEBELOW", (0, 0), (-1, -2), 0.3, colors.white),
    ]))
    return t


def invoice(n: int):
    vendors = ["Suministros Ceiba", "Distribuidora Amanecer", "Papelera Horizonte",
               "Servicios Nube Clara", "Logistica Volcan"]
    products = ["Cajas de empaque", "Etiquetas adhesivas", "Papel de oficina",
                "Soporte de equipos", "Material de embalaje"]
    quantity = 10 + n * 2
    unit = 35 + n * 7
    amount = quantity * unit
    code = f"QM-FP-2026-{n:03d}"
    rows = [
        [para("Concepto", "table_head"), para("Cantidad", "table_head"),
         para("Precio Q", "table_head"), para("Total Q", "table_head")],
        [para(products[n - 1], "table"), para(str(quantity), "table"),
         para(f"{unit:,.2f}", "table"), para(f"{amount:,.2f}", "table")],
    ]
    t = Table(rows, colWidths=[8 * cm, 2.5 * cm, 3 * cm, 3.5 * cm])
    t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), NAVY),
        ("BACKGROUND", (0, 1), (-1, 1), PALE),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 9),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 9),
    ]))
    story = [para("FACTURA DE PROVEEDOR", "eyebrow"), para(code, "title"),
             para("Comprobante de muestra para clasificacion documental.", "subtitle"),
             info([("Emisor", vendors[n - 1]), ("Receptor", "QuetzalMart (empresa ficticia)"),
                   ("Fecha", f"2026-09-{n + 9:02d}"), ("Referencia", code)]),
             para("Detalle", "head"), t, Spacer(1, 12),
             para(f"Total del documento: Q {amount:,.2f}", "right"),
             para("Condiciones", "head"),
             para("Documento ilustrativo. No tiene validez fiscal ni representa una transaccion real."),
             para("Clasificacion: Facturas de proveedores. Etiquetas: factura, proveedor, muestra."),
             para("Todos los nombres y montos son inventados para demostrar el gestor documental.", "small")]
    return code, story


def contract(n: int, employee: bool):
    if employee:
        code = f"QM-CE-2026-{n:03d}"
        title = "Contrato de empleado"
        counterparty = f"Persona Ficticia {n:02d}"
        role = ["Auxiliar de ventas", "Analista de inventario", "Asistente administrativo",
                "Auxiliar de compras", "Operador de almacen"][n - 1]
        service = f"Cargo de muestra: {role}. Jornada y remuneracion sujetas a acuerdo definitivo."
        category = "Contratos de empleados"
        tags = "contrato, empleado, confidencial, muestra"
    else:
        code = f"QM-CO-2026-{n:03d}"
        title = "Contrato de outsourcing"
        counterparty = ["Servicios Condor", "Tecnologia Laguna", "Limpieza Bambu",
                        "Transporte Aurora", "Diseno Naranjo"][n - 1]
        service = ["Mantenimiento preventivo de equipos", "Soporte de software",
                   "Limpieza de instalaciones", "Transporte local de paquetes",
                   "Diseno de material promocional"][n - 1]
        category = "Contratos de outsourcing"
        tags = "contrato, outsourcing, muestra"
    story = [para(category.upper(), "eyebrow"), para(f"{title} - {code}", "title"),
             para("Modelo ficticio para archivo y busqueda en Odoo.", "subtitle"),
             info([("Contratante", "QuetzalMart (empresa ficticia)"),
                   ("Contraparte", counterparty),
                   ("Referencia", code),
                   ("Fecha", f"2026-09-{n + 14:02d}"),
                   ("Vigencia", "Tres meses de demostracion")]),
             para("1. Objeto", "head"), para(service),
             para("2. Alcance", "head"),
             para("Las partes describiran las actividades, entregables y responsables en un anexo operativo. Este texto solo sirve para ensayar el archivo, las etiquetas y los permisos de consulta."),
             para("3. Seguimiento", "head"),
             para("QuetzalMart registrara la recepcion de entregables y cualquier observacion por escrito. Los cambios requeriran una nueva version del documento."),
             para("4. Tratamiento documental", "head"),
             para("El archivo se conservara en su categoria correspondiente y solo podran consultarlo los usuarios autorizados por el gestor documental."),
             Spacer(1, 14),
             para("SIN FIRMAS - DOCUMENTO FICTICIO SIN EFECTOS LEGALES", "small"),
             para(f"Clasificacion: {category}. Etiquetas: {tags}.", "small")]
    return code, story


def main():
    OUT.mkdir(parents=True, exist_ok=True)
    manifest = []
    for category, maker in [
        ("Facturas de proveedores", lambda n: invoice(n)),
        ("Contratos de outsourcing", lambda n: contract(n, False)),
        ("Contratos de empleados", lambda n: contract(n, True)),
    ]:
        for n in range(1, 6):
            code, story = maker(n)
            path = OUT / f"{code}.pdf"
            build(path, story)
            manifest.append({"code": code, "category": category, "file": path.name})
    (OUT / "manifest.json").write_text(json.dumps(manifest, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Generated {len(manifest)} PDFs in {OUT}")


if __name__ == "__main__":
    main()
