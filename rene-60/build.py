"""Genera index.html (documento completo, listo para cualquier hosting estático) a partir de invitacion.html."""
from pathlib import Path

here = Path(__file__).parent
body = (here / "invitacion.html").read_text(encoding="utf-8")

# Canción de Spotify (en el sitio publicado aparece el reproductor de Spotify).
SPOTIFY_TRACK = "7vQbuQcyTflfCIOu3Uzzya"
SPOTIFY_PLAYLIST = "69JsbUGgywKEQz2SDQMsHd"  # playlist navideña con René
# Pega aquí el enlace "Insertar un mapa" de Google Maps (el src del iframe) cuando lo tengas.
MAP_EMBED_SRC = ""
MAP_LINK = "https://maps.app.goo.gl/iPZB8zmNUsduWHAe8"  # enlace normal de Google Maps para el botón "Abrir en Google Maps"

body = body.replace('<div id="spotify-embed"></div>',
    f'<div id="spotify-embed"><iframe src="https://open.spotify.com/embed/playlist/{SPOTIFY_PLAYLIST}?theme=0" '
    'allow="autoplay; clipboard-write; encrypted-media; fullscreen; picture-in-picture" loading="lazy" '
    'title="Canción de la fiesta en Spotify"></iframe></div>')
if MAP_EMBED_SRC:
    body = body.replace('<span class="label">Residencial Pinares</span>',
        f'<iframe src="{MAP_EMBED_SRC}" loading="lazy" referrerpolicy="no-referrer-when-downgrade" title="Mapa: Residencial Pinares"></iframe>')
if MAP_LINK:
    import re
    body = re.sub(r'id="maps-link" target="_blank" rel="noopener" href="[^"]*"', f'id="maps-link" target="_blank" rel="noopener" href="{MAP_LINK}"', body)

# Cambia esta URL por la dirección final donde publiques la invitación
# (WhatsApp necesita una URL absoluta para mostrar la foto de vista previa).
SITE_URL = ""  # ej. "https://rene60.netlify.app/" (con / al final) para la foto de vista previa en WhatsApp

OG_URL = f'<meta property="og:url" content="{SITE_URL}">' if SITE_URL else ""

head = f"""<!doctype html>
<html lang="es">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="theme-color" content="#1c0507">
<meta name="description" content="Christmas came early. René Ferrari celebra sus 60 con una fiesta de Navidad ochentera. 17 de octubre, 6:30 p. m., Residencial Pinares.">
<meta property="og:type" content="website">
<meta property="og:title" content="René Ferrari · The Big 6-0!">
<meta property="og:description" content="Fiesta navideña de los 80 · 17 de octubre · 6:30 p. m. · Residencial Pinares">
<meta property="og:image" content="{SITE_URL}fotos/og.jpg">
{OG_URL}
<meta name="twitter:card" content="summary_large_image">
<style>*,*::before,*::after{{box-sizing:border-box}}body{{margin:0}}[hidden]{{display:none!important}}</style>
</head>
<body>
"""
(here / "index.html").write_text(head + body + "\n</body>\n</html>\n", encoding="utf-8")
print("index.html generado")
