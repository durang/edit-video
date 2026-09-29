# Limitaciones abiertas

Lo que hoy no sale bien, sale a mano, o no se puede. **El radar (cada 2 semanas) busca si algo nuevo
resuelve cada una.** Cuando una se resuelve, se mueve abajo con la fecha y cómo.

| # | Limitación | Nivel | Arreglo provisional | Qué la resolvería |
|---|---|---|---|---|
| L1 | **Palabra detrás de la persona**: el recorte de video (`remove-background`) deja halo o parpadea en tomas con paneo | 3 | Palabra delante | Un matting de video estable en pelo y bordes, que HyperFrames o Higgsfield acepten |
| L2 | **Video negro en HyperFrames** cuando el video va dentro de un recuadro recortado que se mueve y lleva filtros; la caché lo repite | 3 | Render con extract fresco y GPU por software (en prueba) | Arreglo en HyperFrames, o un patrón de composición que lo evite siempre |
| L3 | **El FFmpeg de Homebrew (macOS) no trae libass** → los niveles 1–2 no queman subtítulos | 1–2 | Tap `homebrew-ffmpeg/ffmpeg` | Homebrew lo vuelve a incluir, o un binario oficial con libass |
| L4 | **No hay generador de efectos de sonido** en las herramientas conectadas (Higgsfield solo hace voz) | 3–4 | Sintetizar con FFmpeg | Un generador de SFX con licencia comercial accesible por MCP o CLI |
| L5 | **No hay fuente de música con licencia** integrada | 3–4 | El usuario pasa la pista | Catálogo con licencia en HyperFrames (`media-use`) o por MCP |
| L6 | **Recorte vertical sin detección de cara**: `crop_x` lo decide el agente mirando frames; si el plano cambia, falla | 1–2 | `--fit blur` o partir el clip | Detección de cara ligera, sin dependencias pesadas |
| L7 | **whisper.cpp pega los tiempos** entre palabras → quitar silencios por huecos no funciona | todos | `silencedetect` por energía | Tiempos por palabra con huecos reales en el motor de HyperFrames |
| L8 | **El constructor se revisa a sí mismo y se le escapan defectos** grandes | 3 | Revisor independiente + alarmas de `qa.sh` | Más alarmas automáticas (cara tapada, texto cortado, bordes rectos en recortes) |

## Resueltas

| # | Limitación | Resuelta | Cómo |
|---|---|---|---|
| — | Transcribir en el idioma equivocado | 2026-09-29 | Detección y verificación del idioma en `ingest.sh` y en clipper |
| — | Nombres mal escritos una y otra vez | 2026-09-29 | Diccionario permanente en capas |
