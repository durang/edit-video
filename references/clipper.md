# clipper — video largo a muchos clips

`clipper/` (dentro de este skill desde la 3.0; antes `durang/clipper`) corta un video largo en clips cortos con
subtítulos quemados, marca de agua y audio normalizado, en varios formatos a la vez. FFmpeg + Whisper,
sin HyperFrames. Es **sustractivo**: recorta lo que existe. `/edit-video` es **de montaje**: añade.

Ninguno duplica al otro:

| Herramienta | Hace | Motor | Cuándo |
|---|---|---|---|
| **clipper** | Largo → N clips: cortar, subtítulos palabra por palabra, gancho, marca de agua, loudnorm, 3 formatos | FFmpeg + libass | **Volumen**: 10–30 clips de una entrevista, en minutos |
| **/edit-video** | Un video → pieza de estudio: motion, gráficos, mapas, profundidad, SFX, cierre | HyperFrames (Chrome) | **Calidad**: los 1–3 clips que merecen nivel estudio |
| **motion-design** | Animación desde cero, sin metraje | render local propio | Piezas sin cámara |

## Tres niveles de clipper

| Nivel | Qué sale | Quién lo termina |
|---|---|---|
| **1 · Recorte** (`--nivel 1`) | Subtítulo blanco con contorno, palabra activa amarilla, gancho, logo | clipper, en minutos |
| **2 · Editorial** (`--nivel 2`) | La tipografía de este skill (Inter Tight, Instrument Serif, JetBrains Mono), paleta tinta/papel/acento, palabra activa sobre caja medida al píxel, rótulo, barra de progreso, gancho en dos líneas, grade | clipper, en minutos |
| **3 · Estudio** (`--nivel 3`) | Corte limpio en el encuadre original + `*-PROPUESTA.md` con el beat sheet cronometrado y 3 cuadros | **Este skill**, después de que el director apruebe la propuesta |

**Nivel 3, paso a paso:**
1. `clipper.py render t.json clips.json --nivel 3 --cliente <slug>` → corte limpio + propuesta.
2. Completa la propuesta: concepto, estilo (kit del cliente), gráficos únicos (`motion-design.md`),
   imágenes a generar con Higgsfield (prompts), sonido.
3. Enséñala con 2–3 **cuadros de muestra** (imágenes de Higgsfield o un `snapshot` de HyperFrames).
4. **PARADA hasta el OK del director.** Cambiar en papel es gratis.
5. Con el OK: Paso 3 de este skill sobre el corte limpio, y se construye.

La plantilla del cliente para clipper vive en `edit-video-clients/clients/<slug>/clipper.json`
(colores, rótulos, logo) y se aplica con `--cliente <slug>`.

**macOS:** el ffmpeg de Homebrew core ya no trae libass; clipper lo detecta y da el comando
(`brew tap homebrew-ffmpeg/ffmpeg && brew install homebrew-ffmpeg/ffmpeg/ffmpeg`). El nivel 3 no lo necesita.

## Cómo decidir — una pregunta al empezar

Si alguien trae un video largo y pide clips, pregunta **una vez**:

> ¿Nivel 1 (rápido), 2 (editorial: tipografía y detalles) o 3 (estudio: propuesta + motion)?
> ¿O combinados: todos en 1 o 2 y los mejores en 3?

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
| Vertical que sigue a la persona | `--fit auto`: cara detectada, cámara suave, corte al cambiar de hablante (ver abajo) |
| Vertical sin fondo borroso, a mano | `--fit crop` + `crop_x` por clip (el agente mira los frames y decide) |
| Candidatos con puntaje | `candidatos` (y al final de `analyze`): rúbrica 0–10 con motivo → `clipeabilidad.md` |
| Portada de cada clip | por defecto: `NN-slug-thumb.jpg` con titular (`--no-thumbs` para quitarla) |
| Una carpeta entera | `lote <carpeta>` → propuestas → OK → `lote <carpeta> --render` |
| Palabra activa resaltada | por defecto (`--no-highlight` para quitarla) |
| Subtítulos que no tapa la app y que caben | por defecto: por encima de y=1536 y partidos por caracteres |
| Tapar subtítulos quemados del original | `--cover-subs 0.2` |
| Quitar silencios | `--tighten 0.35` (o `tighten` → JSON de tramos) |
| Gancho arriba los primeros 3 s | `"hook": "…"` en el clip |
| Idioma | `--lang auto` detecta; si lo pasas, lo verifica |

## Candidatos, miniaturas, lote y recorte automático (3.9)

**Rúbrica de clipeabilidad** — `clipper.py candidatos <transcripción> [--min 15 --max 60 --top 10]`
(corre sola al final de `analyze`; acepta también la `transcript.json` de `ingest.sh`). Puntúa
ventanas de frases completas en gancho (0–3), dato (0–2), remate (0–2), autonomía (0–2) y emoción
(0–1), sin solaparse, y deja `<video>.candidatos.json` en formato `clips.json` con `why` = puntaje +
motivo. Es un **pre-filtro**: el agente lee, mueve bordes, escribe `hook` y propone; decide el humano.
Criterio completo: `references/clipeabilidad.md`.

**Miniaturas** — cada `render` deja `NN-slug-thumb.jpg` junto al clip (1080×1920; 1280×720 si es
horizontal). Titular: `titulo` del clip (acepta `"serif|DISPLAY"` en nivel 2) > `hook` > primeras
palabras. Cuadro: `thumb_t` si lo das; con `--fit auto`, la cara más grande y expresiva de los primeros
4 s; si no, el filtro `thumbnail` de FFmpeg (evita parpadeos). Tipografía y paleta de la plantilla del
nivel/cliente; degradado arriba para leerse. ~1.3 s por miniatura.

**Modo lote** — dos pasos, con el OK en medio (la regla no se salta):

```bash
python3 clipper/clipper.py lote ~/grabaciones            # 1: transcribe (caché), rúbrica, LOTE.md
#   → revisar cada <video>.clips.json, ajustar, "aprobado": true
python3 clipper/clipper.py lote ~/grabaciones --render --nivel 2 --fit auto   # 2: solo lo aprobado
```

Transcribe con Whisper de OpenAI si está; si no, con `ingest.sh` (whisper.cpp). Videos con < 40
palabras (música, b-roll) salen como "poca voz" sin propuesta. Cada render queda en `tiempos.py`.

**Recorte por cara / hablante activo** — `--fit auto` (por clip también: `"fit": "auto"`):

- `clipper/caras.py` corre en un **entorno aislado** (clipper sigue siendo solo librería estándar):
  ```bash
  /opt/homebrew/bin/python3.11 -m venv ~/.config/edit-video/venv-caras     # o cualquier python 3.9–3.12
  ~/.config/edit-video/venv-caras/bin/pip install mediapipe==0.10.21
  ```
  clipper lo encuentra solo (o `EDIT_VIDEO_CARAS_PY=<python>` en `~/.config/edit-video/config`). El
  modelo (`face_landmarker.task`, 3.7 MB) se baja la primera vez a `~/.config/edit-video/modelos/`.
  **mediapipe 1.0.x falla en macOS** ("graph_service: Service is unavailable"): usar 0.10.21.
- Detector de rango completo (caras chicas de plano abierto) + Face Landmarker sobre cada cara para
  medir la boca (`jawOpen`). A 6 fps: ~7 s de análisis por 40 s de video en un M-series.
- **Hablante activo** = la boca que más se mueve (ventana 1.5 s), con histéresis: el otro tiene que
  llevar ≥ 0.8 s hablando más; 1 s mínimo entre cortes; si el sujeto desaparece < 1.5 s (el detector lo
  pierde) se sostiene el plano. Si todas las caras caben en el 9:16, encuadre de grupo.
- Cámara virtual: zona muerta + suavizado dentro de un sujeto; **corte seco** al cambiar de hablante.
  Se aplica con `sendcmd` sobre `crop` (respeta `--tighten`).
- Sin entorno o sin caras → cae a `blur` y lo dice. Fuente ya vertical → recorte al centro.
- **Límite conocido**: una cara de **perfil** no deja ver la boca (el landmarker da `jawOpen` = 0) →
  nunca "gana" el plano. En entrevistas donde el entrevistador está de perfil, la cámara se queda en
  el entrevistado (lo normal que se quiere); si hace falta la pregunta, `"fit": "blur"` en ese clip.

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
# viene con el skill: SKILL_DIR/clipper/clipper.py
ffmpeg -hide_banner -filters | grep -q " ass " && echo "libass ok"
pip install -U openai-whisper yt-dlp      # transcribir y bajar (opcionales si ya hay transcripción)
```

Con permiso del usuario, como todo lo demás.
