"""Recortes rectangulares 4:5 de las fotos de René (formato foto impresa).
Uso: python prints_build.py <carpeta_con_fotos_originales>"""
import sys
from pathlib import Path
from PIL import Image, ImageEnhance, ImageOps

SRC = Path(sys.argv[1])
OUT = Path(__file__).parent / "collage"
CROPS = {  # nombre: (archivo, x, y, ancho)  -> alto = ancho * 1.25
    "foto-chaqueta": ("57c34bd2-image.jpg", 300, 640, 1340),
    "foto-pastel": ("9843a93e-image.jpg", 66, 300, 1800),
    "foto-gala": ("f3cbec50-image.jpg", 600, 120, 1040),
    "foto-sombrero": ("a5e47b0f-image.jpg", 100, 300, 760),
    "foto-perrito": ("bb4d1775-image.jpg", 0, 0, 1932),
    "foto-pijama": ("3a92ee36-image.jpg", 1000, 950, 900),
    "foto-90s": ("cd0ae850-image.jpg", 640, 0, 320),
}
for name, (f, x, y, w) in CROPS.items():
    im = ImageOps.exif_transpose(Image.open(SRC / f)).convert("RGB")
    h = round(w * 1.25)
    im = im.crop((x, y, x + w, y + h)).resize((720, 900), Image.LANCZOS)
    im = ImageEnhance.Contrast(im).enhance(1.06)
    im = ImageEnhance.Color(im).enhance(1.08)
    im.save(OUT / f"{name}.jpg", quality=80, optimize=True, progressive=True)
    print(name)
