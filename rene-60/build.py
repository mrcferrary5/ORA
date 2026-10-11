"""Genera index.html (documento completo, listo para cualquier hosting estático) a partir de invitacion.html."""
from pathlib import Path

here = Path(__file__).parent
body = (here / "invitacion.html").read_text(encoding="utf-8")

# Cambia esta URL por la dirección final donde publiques la invitación
# (WhatsApp necesita una URL absoluta para mostrar la foto de vista previa).
SITE_URL = "https://TU-DOMINIO/rene-60/"

head = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#1c0507">
<meta name="description" content="Christmas came early. René Ferrari celebra sus 60 con una fiesta de Navidad ochentera. 17 de octubre, 6:00 PM.">
<meta property="og:type" content="website">
<meta property="og:title" content="René Ferrari · The Big 6-0!">
<meta property="og:description" content="80s Christmas Birthday Party · 17 de octubre · 6:00 PM · Dress code: 80s Christmas">
<meta property="og:image" content="{SITE_URL}fotos/og.jpg">
<meta property="og:url" content="{SITE_URL}">
<meta name="twitter:card" content="summary_large_image">
<style>*,*::before,*::after{{box-sizing:border-box}}body{{margin:0}}[hidden]{{display:none!important}}</style>
</head>
<body>
"""
(here / "index.html").write_text(head + body + "\n</body>\n</html>\n", encoding="utf-8")
print("index.html generado")
