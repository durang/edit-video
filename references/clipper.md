# clipper — video largo a muchos clips

[`durang/clipper`](https://github.com/durang/clipper) corta un video largo en clips cortos con
subtítulos quemados, marca de agua y audio normalizado, en varios formatos a la vez. FFmpeg + Whisper,
sin HyperFrames. Es **sustractivo**: recorta lo que existe. `/edit-video` es **de montaje**: añade.

Ninguno duplica al otro:

| Herramienta | Hace | Motor | Cuándo |
|---|---|---|---|
| **clipper** | Largo → N clips: cortar, subtítulos palabra por palabra, gancho, marca de agua, loudnorm, 3 formatos | FFmpeg + libass | **Volumen**: 10–30 clips de una entrevista, en minutos |
| **/edit-video** | Un video → pieza de estudio: motion, gráficos, mapas, profundidad, SFX, cierre | HyperFrames (Chrome) | **Calidad**: los 1–3 clips que merecen nivel estudio |
| **motion-design** | Animación desde cero, sin metraje | render local propio | Piezas sin cámara |

## Cómo decidir — una pregunta al empezar

Si alguien trae un video largo y pide clips, pregunta **una vez**:

> ¿Rápido (subtítulos, marca de agua y formatos para redes) o de estudio (motion design)?
> ¿O los dos: todos rápidos y los mejores de estudio?

- **Rápido** → clipper entero. El agente propone momentos con motivo (`why`), el humano elige.
- **Estudio** → se corta solo el tramo, **sin subtítulos quemados** (aquí se montan después), y
  entra por el Paso 3. clipper todavía no tiene modo "solo cortar"; mientras, el tramo exacto:
  `ffmpeg -ss INICIO -to FIN -i largo.mp4 -c:v libx264 -crf 16 -c:a aac tramo.mp4` (re-encodado: corte exacto).
- **Los dos** (lo que más rinde) → clipper saca todos; de ahí salen los 1–3 mejores y pasan por aquí.

**La elección de momentos no se automatiza.** Es criterio. El agente puede leer la transcripción y
**proponer** candidatos con su motivo; decide el humano.

## Lo que comparten

- **Transcripción**: la de clipper (`*.transcript.json`, palabras con tiempo) sirve para el Paso 3 si
  el idioma se verificó. No se transcribe dos veces.
- **Diccionario**: `scripts/diccionario.py` lee también `~/clipper-studio/dictionary.json`. Una
  corrección hecha en cualquiera de los dos vale para los dos.
- **Área de clientes** (propuesto para clipper): el logo, la marca de agua y los formatos de un
  cliente viven en `edit-video-clients/clients/<slug>/`, para que las dos herramientas saquen al
  cliente igual.

## Instalar

```bash
git clone https://github.com/durang/clipper ~/clipper && ffmpeg -version | grep -q libass && echo ok
pip install -U openai-whisper yt-dlp
```

Con permiso del usuario, como todo lo demás.
