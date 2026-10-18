# Documental narrado — guion + archivo + voz

Para piezas que **no parten de un video grabado** sino de un guion, material de archivo (dominio público, CC,
propio) y una narración (grabada o TTS): explicativos, historia, curiosidades, videos de YouTube de 8–12 min y
sus Shorts. El método es el mismo (beat sheet → OK → construir → QA → aprender); cambian los oídos, el motor y
la estructura.

## 1 · Fuentes y licencias primero

- Cada toma con **fuente** (archivo, URL, timecode) y **licencia** verificada en `fuentes.md`. Sin licencia, no entra.
- Dominio público: quitar bandas sonoras y carteles de restauración añadidos en la copia (esos sí tienen dueño).
- CC BY: el crédito exacto va en la descripción/créditos.
- Plataformas con detección automática (Content ID): subida privada de prueba 24–48 h antes de publicar.

## 2 · Oídos desde la voz (sin Whisper si se puede)

- **TTS con alineación** (p. ej. ElevenLabs con timestamps por carácter/palabra): convertir esa alineación a
  `transcript.json` / `words.json` (`text`, `start`, `end`) — tiempos exactos, sin transcribir.
- **Voz grabada**: `ingest.sh` sobre el audio (idioma verificado, diccionario).
- Por párrafos: generar la voz por párrafo y guardar el inicio/fin de cada uno (`timeline.json`) para poder rehacer
  un párrafo sin mover el resto.
- La regla 10 se lee como "la voz **de una persona** nunca se sustituye": si el `CLIENTE.md` declara
  `voz: tts <proveedor/voz>`, esa voz es la del canal.

## 3 · Beat sheet de documental

```
| inicio | fin | palabras exactas | toma (fuente + timecode) | licencia | qué aparece / gráfico | sonido |
```
Lo que se ve tiene que ser lo que se dice, palabra por palabra. Los datos llevan su fuente en `fuentes.md`.

## 4 · Estructura de pieza larga (8–12 min)

- Gancho concreto en < 15 s, sin intro de canal.
- Open loop antes del 1:00, resuelto entre el 50 y el 85 % de la pieza.
- Re-gancho cada 20–60 s (pregunta nueva, giro, imagen rara).
- 2–3 momentos de impacto pensados para ser "lo más repetido" (congelado, cuadro a cuadro, número tachado…).
- Giro final y fin inmediato (sin despedida larga); hueco para la pantalla final si la plataforma la usa.

## 5 · Insertos generados

- Son nivel 4 (`nivel-4.md`): se aprueban uno por uno.
- **Nunca pasan por material de archivo**: etiqueta visible mientras duran (la que fije el cliente) y, si
  parecen reales, la divulgación de contenido alterado/IA de la plataforma.
- Sin texto generado dentro del plano (el texto se monta).

## 6 · Motor

- HyperFrames por defecto. Si el kit del cliente trae **motor propio** (`kit/motor/README.md`: p. ej. Python +
  FFmpeg con sus plantillas), se usa ese — `check.sh --motor <kit/motor>` valida dependencias.
- Rutas **relativas a la carpeta del proyecto** (nunca rutas absolutas de otra máquina).
- Render por trozos con un `.ok` por trozo, reanudable; concat al final; audio mezclado aparte y muxeado al final.
- Workers según la máquina (`destino.sh env` → `EDIT_VIDEO_WORKERS`; 2 en 8 GB).

## 7 · Formatos y safe zone

- **16:9 (YouTube largo)**: nada importante en el 10 % inferior (barra del reproductor y subtítulos de la
  plataforma), la esquina de la marca de agua libre, y los últimos 5–20 s con hueco para la pantalla final.
- **Shorts 9:16**: se **recomponen**, no se recortan; safe zone de apps (nada en el 20 % inferior ni en el borde
  derecho). Loop perfecto: el último cuadro empata con el primero (imagen y sonido).

## 8 · QA

Piezas de más de 3 min: **modo muestreo** (`qa.md` §1b) en la máquina que renderiza, con los subtítulos
verificados por código (`scripts/subcov.py`). Tiempos: `tiempos.py … --tipo largo`.
