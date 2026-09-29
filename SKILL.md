---
name: video-edit
description: Use when the user wants an EXISTING video of theirs edited — captions, cutting dead air, punch-in zooms, title cards, lower thirds, pop-ups, music and SFX, reframing 16:9 to 9:16, background removal, 3D objects, or a named style like a movie trailer or a Vox explainer. This edits footage that already exists; it never generates new footage. Runs on the user's own machine with HyperFrames + Whisper + FFmpeg and renders an MP4. Triggers on "edita mi video", "ponle subtítulos", "córtale los silencios", "hazlo vertical para Reels", "edit my video", "add captions", "cut the pauses", "make it look like a movie trailer", or a video file plus an edit request. NOT for generating new shots (use the Seedance/Grok prompting canon), and NOT for multicam re-filming of a take (that is habilidad #7, multiángulo).
---

# video-edit — montar un video que ya existe

**Método original:** "Let Claude Edit Your Videos" de **@pauloshimas / The Creator Stack**.
**Motor:** [HyperFrames](https://github.com/heygen-com/hyperframes), de HeyGen — plugin de Claude Code
que escribe el montaje como una página web y la renderiza en MP4.

Esto **no genera video**. Monta el que ya tienes. Si hace falta material nuevo, eso es otro
sistema (prompting generativo). Si hace falta re-filmar una toma desde otros ángulos, eso es
multiángulo, no esto.

---

## Principio central

**Claude no puede reproducir un video.** Así que antes de editar nada se le dan dos sentidos:

- **Oídos → Whisper**: la transcripción con el tiempo exacto de **cada palabra**
- **Ojos → FFmpeg**: fotogramas fijos, uno por segundo

De ahí sale lo único que importa: **cada efecto se ancla a una PALABRA, no a un segundo.**
El zoom cae en "ahora" porque Whisper sabe que "ahora" empieza en 5.32 s. Eso es lo que separa
un montaje que parece hecho a mano de uno que parece una plantilla.

---

## Reglas duras (no se rompen)

- **Nunca construir antes del beat sheet.** Se presenta la tabla — tiempo, palabras exactas, qué
  aparece, dónde y qué suena — y **se espera el OK**. Cambiar en papel es gratis; cambiar después
  de renderizar no.
- **Rough cut primero, efectos después.** Se cortan los silencios, se confirma la duración nueva,
  y solo entonces entran los efectos.
- **Nunca cortar dentro de una palabra.** Los cortes usan los tiempos de Whisper.
- **Los nombres propios se piden en el primer prompt.** Whisper escribe los nombres como suenan.
  Marca, producto y nombre de la persona se declaran antes de transcribir, y se corrigen en la
  transcripción **y** en los subtítulos.
- **Safe zone siempre.** Nada de texto en el **20% inferior** de la pantalla ni pegado al borde
  derecho: ahí van los botones de la app.
- **Una nota, un cambio, siempre con el tiempo.** Qué, dónde y cuándo — nunca cómo.
- **Versionar antes de cada ronda** (v1, v2, v3...) para poder volver atrás.
- **Verificar con los propios ojos.** Antes de decir que está hecho: `npx hyperframes snapshot`
  del frame en cuestión y mirarlo. Decir "listo" sin haber mirado el frame es mentir.
- **El director es el usuario.** El gusto no se delega.

---

## Flujo

### 0 · Preflight (primera vez en la sesión)

```bash
npx hyperframes doctor
```

Comprueba Node 22+, FFmpeg y Chrome. Si falta algo, se reporta con su comando de instalación
y **se pregunta antes de instalar**. Nunca se adivina alrededor de una herramienta que falta.

### 1 · Oídos y ojos

```bash
# transcripción con tiempo por palabra
whisper-cli -f VIDEO.mp4 --output-json --max-len 1       # macOS (whisper-cpp)
python -m faster_whisper VIDEO.mp4 --word_timestamps True # Windows

# fotogramas
ffmpeg -i VIDEO.mp4 -vf fps=1 -q:v 3 frames/f_%03d.jpg
```

Se leen **todos** los frames junto con las palabras. Luego se le dice al usuario qué dice, cuándo
lo dice y qué hay en el plano en cada momento.

### 2 · Beat sheet, y parada

Tabla: `inicio | fin | palabras exactas | qué aparece | dónde se coloca | sonido`.
Se declara el formato (9:16 Reels / 16:9 / 1:1) y la safe zone. **Se espera el OK.**

### 3 · Rough cut

Se cortan las pausas de más de 0.3 s y las respiraciones, sin entrar en ninguna palabra, dejando
un beat corto antes de cada remate. Se reporta la duración nueva.

### 4 · Construir

HyperFrames escribe el montaje. Cada efecto sincronizado a su palabra.

### 5 · Preview, notas, render

```bash
npx hyperframes preview                    # se mira en el navegador
npx hyperframes render -o final.mp4
```

Notas del usuario: una por línea, con el tiempo. Se aplica, se hace snapshot del frame afectado,
se comprueba, y se vuelve a enseñar.

---

## Cuándo brilla y cuándo no

| Va bien | Va mal |
|---|---|
| Talking-head: subtítulos, zooms, pop-ups | **Material nuevo** — eso es generación, no montaje |
| Explicativos: diagramas y listas que se construyen | Movimiento rápido y desordenado — los recortes salen blandos |
| Tutoriales: zoom en el clic, flechas, callouts | Una hora de golpe — se trabaja por secciones |
| Demos de producto: 3D, títulos, precios | Corrección de color fina — eso es de colorista |
| Clips de podcast: 16:9 → 9:16, subtítulos, nombres | **El gusto** — el director sigue siendo el usuario |
| Datos: números y gráficas animadas | |
| Lotes: el mismo montaje en 10 videos o en 3 idiomas | |

**Regla del pulgar:** si se puede describir en una frase y señalar la palabra donde pasa,
se puede construir.

---

## Referencias

| Archivo | Cuándo |
|---|---|
| `references/setup.md` | Primera vez. Qué se instala y cómo se comprueba |
| `references/film-it-right.md` | **Antes de grabar.** Decide si los recortes salen limpios |
| `references/prompts.md` | Prompts listos: los de diario y los de lucirse |
| `references/styles.md` | Copiar un estilo: con referencias propias o nombrando uno famoso |
| `references/troubleshooting.md` | Cuando algo sale torcido |
| `CLAUDE.md.template` | Las reglas de estilo del usuario, para su carpeta de proyecto |

---

## Crédito

Método: **@pauloshimas · The Creator Stack** (2026). Motor: **HyperFrames**, de HeyGen.
Este skill es la adaptación del método a un flujo repetible, con las reglas duras explícitas.
