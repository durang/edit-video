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
  entra por el Paso 3: `clipper.py render t.json clips.json --horizontal --no-captions`.
- **Los dos** (lo que más rinde) → clipper saca todos; de ahí salen los 1–3 mejores y pasan por aquí.

**La elección de momentos no se automatiza.** Es criterio. El agente puede leer la transcripción y
**proponer** candidatos con su motivo; decide el humano.

## Lo que comparten

- **Transcripción**: la de clipper (`*.transcript.json`, palabras con tiempo) sirve para el Paso 3 si
  el idioma se verificó. No se transcribe dos veces.
- **Diccionario**: `scripts/diccionario.py` lee también `~/clipper-studio/dictionary.json`. Una
  corrección hecha en cualquiera de los dos vale para los dos.
- **Área de clientes**: `--cliente <slug>` en clipper aplica el diccionario privado del cliente, el
  mismo que usa este skill. Logo y formatos del cliente viven en su `kit/`.

## Lo que clipper ya hace bien (y cómo pedírselo)

| Pedido | clipper |
|---|---|
| Vertical sin fondo borroso | `--fit crop` + `crop_x` por clip (el agente mira los frames y decide) |
| Palabra activa resaltada | por defecto (`--no-highlight` para quitarla) |
| Subtítulos que no tapa la app y que caben | por defecto: por encima de y=1536 y partidos por caracteres |
| Tapar subtítulos quemados del original | `--cover-subs 0.2` |
| Quitar silencios | `--tighten 0.35` (o `tighten` → JSON de tramos) |
| Gancho arriba los primeros 3 s | `"hook": "…"` en el clip |
| Idioma | `--lang auto` detecta; si lo pasas, lo verifica |

## Silencios: ojo con de dónde salen los tiempos

`tighten` corta entre palabras usando sus tiempos. **Whisper de OpenAI** (el de clipper) deja huecos
reales entre palabras; **whisper.cpp** (el que usa HyperFrames para este skill) tiende a pegar el
final de una palabra con el inicio de la siguiente, y entonces no ve los silencios. Para el rough cut
del Paso 5 sobre una transcripción de HyperFrames, detecta silencios por energía y corta solo entre
palabras:

```bash
ffmpeg -i TOMA.mp4 -af silencedetect=noise=-35dB:d=0.3 -f null - 2>&1 | grep silence_
```

## Instalar

```bash
git clone https://github.com/durang/clipper ~/clipper && ffmpeg -version | grep -q libass && echo ok
pip install -U openai-whisper yt-dlp
```

Con permiso del usuario, como todo lo demás.
