#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Sellos de tinta para bolsa kraft — Cerrato's Food
Genera:
  design/sellos/sello-1-logo-100mm.pdf      (arte vectorial a tamano real)
  design/sellos/sello-2-frase-55mm.pdf      (arte vectorial a tamano real)
  design/sellos/sello-1-logo-600dpi.png     (bitmap para fabricante de sellos)
  design/sellos/sello-2-frase-600dpi.png
  design/hoja-especificaciones.pdf          (hoja de produccion A4)
  design/previews/*.png                     (previsualizaciones)
"""
import os
import math

from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdfcanvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.lib.colors import Color

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FONTS = "/root/.claude/skills/canvas-design/canvas-fonts"
OUT_SELLOS = os.path.join(ROOT, "design", "sellos")
OUT_DESIGN = os.path.join(ROOT, "design")
OUT_PREV = os.path.join(ROOT, "design", "previews")
for d in (OUT_SELLOS, OUT_PREV):
    os.makedirs(d, exist_ok=True)

pdfmetrics.registerFont(TTFont("EricaOne", f"{FONTS}/EricaOne-Regular.ttf"))
pdfmetrics.registerFont(TTFont("BigShouldersBold", f"{FONTS}/BigShoulders-Bold.ttf"))
pdfmetrics.registerFont(TTFont("WorkSansBold", f"{FONTS}/WorkSans-Bold.ttf"))
pdfmetrics.registerFont(TTFont("DMMono", f"{FONTS}/DMMono-Regular.ttf"))
pdfmetrics.registerFont(TTFont("IBMPlexMonoBold", f"{FONTS}/IBMPlexMono-Bold.ttf"))

BLACK = Color(0, 0, 0)
WHITE = Color(1, 1, 1)
KRAFT = Color(0.792, 0.667, 0.490)      # papel kraft
KRAFT_DEEP = Color(0.690, 0.557, 0.384)
INK = Color(0.10, 0.08, 0.06)           # tinta sobre kraft (casi negro)


# ---------------------------------------------------------------- geometria --
def loaf_path(c, s=1.0):
    """Silueta simplificada del pan (torpedo). Coordenadas locales, eje
    horizontal, centrada en (0,0). Largo ~110*s, alto ~44*s. Devuelve path."""
    p = c.beginPath()
    L = 55.0 * s   # semilargo
    H = 21.0 * s   # semialto
    # cola izquierda tipo "envoltorio": dos puntas romas con muesca en V
    p.moveTo(-L, 7.0 * s)
    p.lineTo(-L + 9.0 * s, 0.0)
    p.lineTo(-L, -7.0 * s)
    # curva inferior hacia la derecha
    p.curveTo(-L + 18 * s, -15 * s, -26 * s, -H, 0, -H)
    p.curveTo(26 * s, -H, L - 18 * s, -15 * s, L, -3.0 * s)
    # punta derecha roma
    p.lineTo(L, 3.0 * s)
    # curva superior de regreso
    p.curveTo(L - 18 * s, 15 * s, 26 * s, H, 0, H)
    p.curveTo(-26 * s, H, -L + 18 * s, 15 * s, -L, 7.0 * s)
    p.close()
    return p


def draw_score_marks(c, s=1.0, color=WHITE):
    """Marcas de grenado del pan: tres chevrons ondulados calados, arriba a la
    izquierda del pan (como en el logo original)."""
    c.saveState()
    c.setStrokeColor(color)
    c.setLineWidth(2.8 * s)
    c.setLineCap(1)
    c.setLineJoin(1)
    for i in range(3):
        x0 = -23.5 * s + i * 10.5 * s
        y0 = 8.2 * s + i * 1.5 * s
        p = c.beginPath()
        p.moveTo(x0, y0)
        p.curveTo(x0 + 2.0 * s, y0 + 4.4 * s, x0 + 4.2 * s, y0 + 5.8 * s,
                  x0 + 7.2 * s, y0 + 6.4 * s)
        c.drawPath(p, fill=0, stroke=1)
    c.restoreState()


def draw_tracked_text(c, font, size, text, x, y, tracking=0.0, color=None,
                      centered=True):
    """Texto con tracking manual (en puntos). Devuelve el ancho total."""
    widths = [pdfmetrics.stringWidth(ch, font, size) for ch in text]
    total = sum(widths) + tracking * (len(text) - 1)
    cx = x - total / 2.0 if centered else x
    if color is not None:
        c.setFillColor(color)
    c.setFont(font, size)
    for ch, w in zip(text, widths):
        c.drawString(cx, y, ch)
        cx += w + tracking
    return total


def tracked_width(font, size, text, tracking=0.0):
    widths = [pdfmetrics.stringWidth(ch, font, size) for ch in text]
    return sum(widths) + tracking * (len(text) - 1)


# ------------------------------------------------------------------ sello 1 --
def draw_sello1(c, cx, cy, width_mm=100.0, ink=BLACK):
    """Logo simplificado: pan solido con texto calado, rotado. El ancho total
    del arte (bounding box) = width_mm."""
    angle = 17.0  # grados de rotacion del pan
    # ancho del bbox de un rect L x H rotado: L*cos(a) + H*sin(a)
    a = math.radians(angle)
    L_local, H_local = 110.0, 44.0
    bbox_w_unit = L_local * math.cos(a) + H_local * math.sin(a)
    s = (width_mm * mm) / bbox_w_unit  # escala: unidades locales -> puntos
    c.saveState()
    c.translate(cx, cy)
    c.rotate(angle)
    # cuerpo del pan
    c.setFillColor(ink)
    p = loaf_path(c, s)
    c.drawPath(p, fill=1, stroke=0)
    # grenado calado
    draw_score_marks(c, s, color=WHITE)
    # CERRATO'S calado
    draw_tracked_text(c, "EricaOne", 14.4 * s, "CERRATO'S",
                      2.5 * s, -5.0 * s, tracking=0.55 * s, color=WHITE)
    # FOOD calado, mas pequeno y espaciado
    draw_tracked_text(c, "EricaOne", 7.0 * s, "FOOD",
                      9.0 * s, -15.0 * s, tracking=2.8 * s, color=WHITE)
    c.restoreState()


# ------------------------------------------------------------------ sello 2 --
def draw_sello2(c, cx, cy, width_mm=55.0, ink=BLACK):
    """Frase en dos lineas, mayusculas bold, centrada. Ancho total = width_mm."""
    font = "EricaOne"
    line1, line2 = "SE ANTOJÓ,", "SE CERRÓ."
    tr = 1.2
    # tamano de fuente tal que la linea mas ancha = width_mm
    size = 10.0
    w1 = tracked_width(font, size, line1, tr)
    scale = (width_mm * mm) / w1
    size *= scale
    tr *= scale
    leading = size * 1.06
    c.setFillColor(ink)
    total_h = leading
    y_top = cy + total_h / 2.0 - size * 0.72
    draw_tracked_text(c, font, size, line1, cx, y_top, tracking=tr, color=ink)
    draw_tracked_text(c, font, size, line2, cx, y_top - leading,
                      tracking=tr, color=ink)


def sello2_height_mm(width_mm=55.0):
    font, tr0, size0 = "EricaOne", 1.2, 10.0
    w1 = tracked_width(font, size0, "SE ANTOJÓ,", tr0)
    size = size0 * (width_mm * mm) / w1
    return (size * 1.06 + size * 0.78) / mm


# --------------------------------------------------- PDFs de arte a tamano real
def make_sello1_pdf():
    W, H = 120 * mm, 90 * mm
    path = os.path.join(OUT_SELLOS, "sello-1-logo-100mm.pdf")
    c = pdfcanvas.Canvas(path, pagesize=(W, H))
    c.setTitle("Cerrato's Food — Sello 1 (logo) — arte 100 mm")
    draw_sello1(c, W / 2, H / 2, 100.0)
    c.showPage()
    c.save()
    return path


def make_sello2_pdf():
    W, H = 70 * mm, 35 * mm
    path = os.path.join(OUT_SELLOS, "sello-2-frase-55mm.pdf")
    c = pdfcanvas.Canvas(path, pagesize=(W, H))
    c.setTitle("Cerrato's Food — Sello 2 (frase) — arte 55 mm")
    draw_sello2(c, W / 2, H / 2, 55.0)
    c.showPage()
    c.save()
    return path


# ------------------------------------------------------- hoja de especificacion
A4W, A4H = 210 * mm, 297 * mm


def dim_line(c, x0, y0, x1, y1, label, offset=4 * mm, ink=INK):
    """Linea de cota horizontal con flechas y etiqueta."""
    c.saveState()
    c.setStrokeColor(ink)
    c.setLineWidth(0.5)
    y = y0 - offset
    c.line(x0, y0 - 1.2 * mm, x0, y - 1.2 * mm)
    c.line(x1, y1 - 1.2 * mm, x1, y - 1.2 * mm)
    c.line(x0, y, x1, y)
    for xx, d in ((x0, 1), (x1, -1)):
        c.setFillColor(ink)
        p = c.beginPath()
        p.moveTo(xx, y)
        p.lineTo(xx + d * 2.2 * mm, y + 0.8 * mm)
        p.lineTo(xx + d * 2.2 * mm, y - 0.8 * mm)
        p.close()
        c.drawPath(p, fill=1, stroke=0)
    c.setFont("DMMono", 6.5)
    c.setFillColor(ink)
    c.drawCentredString((x0 + x1) / 2, y - 3.2 * mm, label)
    c.restoreState()


def bag_diagram(c, cx, cy, w, h, ink=INK, face="front"):
    """Bolsa kraft esquematica (vista frontal), con guarda dentada arriba."""
    c.saveState()
    c.setStrokeColor(ink)
    c.setLineWidth(1.1)
    c.setLineJoin(1)
    x0, y0 = cx - w / 2, cy - h / 2
    # cuerpo
    c.rect(x0, y0, w, h, fill=0, stroke=1)
    # borde dentado superior
    teeth = 8
    tw = w / teeth
    p = c.beginPath()
    p.moveTo(x0, y0 + h)
    for i in range(teeth):
        p.lineTo(x0 + tw * (i + 0.5), y0 + h + 2.6 * mm)
        p.lineTo(x0 + tw * (i + 1.0), y0 + h)
    c.setLineWidth(0.9)
    c.drawPath(p, fill=0, stroke=1)
    # pliegue de fondo
    c.setLineWidth(0.6)
    c.setDash(2, 2)
    c.line(x0, y0 + 5.5 * mm, x0 + w, y0 + 5.5 * mm)
    c.setDash()
    c.restoreState()


def make_spec_sheet():
    path = os.path.join(OUT_DESIGN, "hoja-especificaciones.pdf")
    c = pdfcanvas.Canvas(path, pagesize=(A4W, A4H))
    c.setTitle("Cerrato's Food — Sellos para bolsa kraft — Especificaciones")

    # fondo kraft
    c.setFillColor(KRAFT)
    c.rect(0, 0, A4W, A4H, fill=1, stroke=0)

    M = 16 * mm
    # ------------------------------------------------------------- cabecera --
    c.setFillColor(INK)
    c.setFont("DMMono", 7)
    c.drawString(M, A4H - 14 * mm, "CERRATO'S FOOD — ESPECIFICACIÓN DE PRODUCCIÓN")
    c.drawRightString(A4W - M, A4H - 14 * mm, "DOC. SEL-01 · AGO 2026")
    c.setLineWidth(0.8)
    c.setStrokeColor(INK)
    c.line(M, A4H - 17 * mm, A4W - M, A4H - 17 * mm)

    c.setFont("BigShouldersBold", 30)
    c.drawString(M, A4H - 29 * mm, "SELLOS DE TINTA · BOLSA KRAFT")
    c.setFont("DMMono", 7)
    c.drawString(M, A4H - 35 * mm,
                 "UNA TINTA: NEGRO (PANTONE BLACK C / K:100) · SIN TRAMAS · SIN DEGRADADOS")

    # --------------------------------------------------- fig 01: sello 1 -----
    fig1_cy = A4H - 84 * mm
    c.setFont("IBMPlexMonoBold", 7.5)
    c.drawString(M, A4H - 44 * mm, "FIG. 01 — SELLO 1 · LOGO (FRENTE)  ·  ESCALA 1:1")
    draw_sello1(c, A4W / 2, fig1_cy, 100.0, ink=INK)
    dim_line(c, A4W / 2 - 50 * mm, fig1_cy - 27 * mm,
             A4W / 2 + 50 * mm, fig1_cy - 27 * mm, "100 mm", offset=3 * mm)

    # --------------------------------------------------- fig 02: sello 2 -----
    fig2_label_y = A4H - 128 * mm
    fig2_cy = A4H - 143 * mm
    c.setFont("IBMPlexMonoBold", 7.5)
    c.drawString(M, fig2_label_y, "FIG. 02 — SELLO 2 · FRASE (REVERSO)  ·  ESCALA 1:1")
    draw_sello2(c, A4W / 2, fig2_cy, 55.0, ink=INK)
    dim_line(c, A4W / 2 - 27.5 * mm, fig2_cy - 9 * mm,
             A4W / 2 + 27.5 * mm, fig2_cy - 9 * mm, "55 mm", offset=3 * mm)

    # ------------------------------------------- fig 03: ubicacion en bolsa --
    figs_y = A4H - 172 * mm
    c.setFont("IBMPlexMonoBold", 7.5)
    c.drawString(M, figs_y, "FIG. 03 — UBICACIÓN EN BOLSA")

    bag_w, bag_h = 40 * mm, 50 * mm
    bag1_cx, bag2_cx = A4W / 2 - 38 * mm, A4W / 2 + 38 * mm
    bag_cy = figs_y - 33 * mm
    # frente
    bag_diagram(c, bag1_cx, bag_cy, bag_w, bag_h, ink=INK)
    draw_sello1(c, bag1_cx, bag_cy + 1.5 * mm, 26.0, ink=INK)
    c.setFont("DMMono", 6.5)
    c.setFillColor(INK)
    c.drawCentredString(bag1_cx, bag_cy - bag_h / 2 - 6 * mm,
                        "FRENTE · SELLO 1 CENTRADO")
    c.drawCentredString(bag1_cx, bag_cy - bag_h / 2 - 10 * mm,
                        "MARGEN SUP./INF. ≥ 40 mm")
    # reverso
    bag_diagram(c, bag2_cx, bag_cy, bag_w, bag_h, ink=INK)
    draw_sello2(c, bag2_cx, bag_cy + 1.5 * mm, 16.0, ink=INK)
    c.setFont("DMMono", 6.5)
    c.setFillColor(INK)
    c.drawCentredString(bag2_cx, bag_cy - bag_h / 2 - 6 * mm,
                        "REVERSO · SELLO 2 CENTRADO")
    c.drawCentredString(bag2_cx, bag_cy - bag_h / 2 - 10 * mm,
                        "EJE VERTICAL AL CENTRO DEL PANEL")

    # ------------------------------------------------------- tabla de specs --
    ty = 46 * mm
    c.setLineWidth(0.8)
    c.line(M, ty + 6 * mm, A4W - M, ty + 6 * mm)
    rows = [
        ("SELLO 1 · LOGO", "100 mm ancho · negro 1 tinta · trazo sólido ≥ 1,2 mm · calados ≥ 1,0 mm"),
        ("SELLO 2 · FRASE", "55 mm ancho (rango 50–60) · mayúsculas bold · sin cursiva · mismo negro"),
        ("SOPORTE", "papel kraft natural · la tinta debe ser apta para contacto indirecto con alimentos"),
        ("PRUEBA", "OBLIGATORIA: prueba de impresión sobre kraft antes de aprobar el lote completo —"),
        ("", "verificar que el detalle (calados y greñado) no se pierda al estampar."),
    ]
    c.setFillColor(INK)
    yy = ty
    for k, v in rows:
        c.setFont("IBMPlexMonoBold", 7)
        c.drawString(M, yy, k)
        c.setFont("DMMono", 7)
        c.drawString(M + 38 * mm, yy, v)
        yy -= 5.2 * mm

    # pie
    c.setFont("DMMono", 6)
    c.drawString(M, 14 * mm, "TINTA SELLADA · SE ANTOJÓ, SE CERRÓ.")
    c.drawRightString(A4W - M, 14 * mm, "APROBACIÓN PENDIENTE DE PRUEBA EN KRAFT")

    c.showPage()
    c.save()
    return path


# ------------------------------------------------------------------- renders --
def render_png(pdf_path, png_path, dpi=300):
    import fitz
    doc = fitz.open(pdf_path)
    page = doc[0]
    pix = page.get_pixmap(dpi=dpi)
    pix.save(png_path)
    doc.close()


if __name__ == "__main__":
    p1 = make_sello1_pdf()
    p2 = make_sello2_pdf()
    ps = make_spec_sheet()
    render_png(p1, os.path.join(OUT_SELLOS, "sello-1-logo-600dpi.png"), 600)
    render_png(p2, os.path.join(OUT_SELLOS, "sello-2-frase-600dpi.png"), 600)
    render_png(p1, os.path.join(OUT_PREV, "sello-1-preview.png"), 150)
    render_png(p2, os.path.join(OUT_PREV, "sello-2-preview.png"), 150)
    render_png(ps, os.path.join(OUT_PREV, "hoja-especificaciones-preview.png"), 110)
    print("OK")
