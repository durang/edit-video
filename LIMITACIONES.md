# Limitaciones abiertas

Lo que hoy no sale bien, sale a mano, o no se puede. **El radar (cada 2 semanas) busca si algo nuevo
resuelve cada una.** Cuando una se resuelve, se mueve abajo con la fecha y cómo.

| # | Limitación | Nivel | Arreglo provisional | Qué la resolvería |
|---|---|---|---|---|
| L1 | **Palabra detrás de la persona**: el recorte de video (`remove-background`) deja halo o parpadea en tomas con paneo | 3 | Palabra delante | Un matting de video estable en pelo y bordes, que HyperFrames o Higgsfield acepten. **Avance (2026-09-30):** el recorte de VIDEO de Higgsfield (`remove_background` sobre el clip) sí es estable entre cuadros. Alfa: black-key del mate (lumakey tol 0.07; la diferencia con el plate NO separa). Usar el mate solo como alfa y el color del metraje original (erode 1 px) para evitar ribete oscuro. |
| L2 | **Video negro en HyperFrames** (0.8.9x, captura por screenshot): un `<video>` recortado con `clip-path` **y escalado hacia abajo** sale negro. Mismo código de video en v4 sale limpio y en v5 negro; sin SFX ni imágenes sigue negro → la causa exacta está pendiente de bisección | 3 | **Pre-render 1:1 con FFmpeg** del contenido del recuadro (`nivel-3.md` §3); el metraje grande solo escala hacia arriba | Causa exacta (bisección v4↔v5) y arreglo o aviso en HyperFrames |
| L4 | **No hay generador de efectos de sonido** en las herramientas conectadas (Higgsfield solo hace voz) | 3–4 | Sintetizar con FFmpeg | Un generador de SFX con licencia comercial accesible por MCP o CLI |
| L5 | **No hay fuente de música con licencia** integrada | 3–4 | El usuario pasa la pista | Catálogo con licencia en HyperFrames (`media-use`) o por MCP |
| L9 | **Hablante activo**: una cara de perfil no deja ver la boca (nunca gana el plano) y el cambio de hablante llega con 1–5 s de retraso | 1–2 | `"fit": "blur"` en ese clip, o `crop_x` a mano | Cruzar movimiento de boca con la energía de la voz (o diarización) |
| L7 | **whisper.cpp pega los tiempos** entre palabras → quitar silencios por huecos no funciona | todos | `silencedetect` por energía | Tiempos por palabra con huecos reales en el motor de HyperFrames |
| L8 | **El constructor se revisa a sí mismo y se le escapan defectos** grandes | 3 | Revisor independiente + alarmas de `qa.sh` | Más alarmas automáticas (cara tapada, texto cortado, bordes rectos en recortes) |

## Resueltas

| # | Limitación | Resuelta | Cómo |
|---|---|---|---|
| — | Transcribir en el idioma equivocado | 2026-09-29 | Detección y verificación del idioma en `ingest.sh` y en clipper |
| — | Nombres mal escritos una y otra vez | 2026-09-29 | Diccionario permanente en capas |
| L3 | El FFmpeg de Homebrew (macOS) no trae libass: los niveles 1–2 no quemaban subtítulos | 2026-09-30 | Un FFmpeg aparte con libass (`conda create -n edit-video-ffmpeg -c conda-forge ffmpeg`) y `EDIT_VIDEO_FFMPEG` en `~/.config/edit-video/config`; clipper y `check.sh` lo usan solos. No toca el FFmpeg del sistema |
| — | clipper no leía la transcripción de `ingest.sh` (lista de palabras) | 2026-09-30 | `read_transcript()` acepta los tres formatos (clipper, ingest/HyperFrames, Whisper) en render, tighten y shotgun |
| L6 | Recorte vertical sin detección de cara | 2026-09-30 | `--fit auto`: MediaPipe en entorno aislado (`clipper/caras.py`), hablante activo por la boca, cámara suave y corte seco. Queda L9 |
