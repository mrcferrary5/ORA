# René Ferrari · The Big 6-0!

Invitación web para la fiesta de los 60 años de René Ferrari: 80s Christmas Birthday Party, 17 de octubre, 6:30 p. m..

## Archivos

- `invitacion.html`: el contenido de la página (lo que se edita).
- `index.html`: documento completo generado por `build.py`, listo para subir a cualquier hosting estático (GitHub Pages, Netlify, Vercel, etc.).
- `fotos/`: fotos de René recortadas y comprimidas, más `og.jpg` (vista previa al compartir por WhatsApp).

## Personalizar

Todo el texto está en `invitacion.html`. Después de editar, ejecuta:

```bash
python3 build.py
```

- **Fecha de la cuenta regresiva:** busca `2026-10-17T18:30:00-06:00`.
- **WhatsApp:** busca `wa.me/50433337644` (número y mensaje predefinido).
- **Calendario:** busca `calendar.google.com` (fecha, hora y zona horaria).
- **Fotos:** reemplaza los archivos en `fotos/` con el mismo nombre (formato vertical 4:5).
- **Vista previa en WhatsApp:** en `build.py`, cambia `SITE_URL` por la URL final donde publiques la página para que se vea la foto `og.jpg`.

## Música

El soundtrack es una versión synth-pop ochentera de "Jingle Bells" (dominio público) generada en vivo con Web Audio: no usa archivos de audio ni se reproduce sola. Se activa con el botón SOUNDTRACK.
