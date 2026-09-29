# /edit-video

**Monta videos que ya existen, con cualquier agente.** Subtítulos, cortar silencios, zooms,
rótulos, gráficos encima, música, reencuadre a vertical, recorte de fondo, objetos 3D, estilos con
nombre — y unir clips generados con IA en una pieza terminada.

No genera video. Monta el que ya tienes.

Funciona en **Claude Code, OpenClaw, Hermes Agent, Codex, Cursor, Gemini CLI** y cualquier agente
que lea skills en formato `SKILL.md`.

## Instalar

### Si eres una persona


```bash
git clone https://github.com/durang/edit-video && cd edit-video && bash install.sh
```

Detecta tus agentes, instala el skill, **y el skill instala todo lo demás** que le falte:
[HyperFrames](https://github.com/heygen-com/hyperframes), FFmpeg, Node, whisper-cpp y el modelo de
Whisper. Te enseña el plan y te pide permiso antes de instalar nada.

### Si eres un agente (o se lo pasas a uno)

Pégale esto a Claude Code, OpenClaw, Hermes o el que uses:

> Instala el skill de https://github.com/durang/edit-video con
> `npx skills add durang/edit-video -g -y`. Luego corre
> `bash ~/.agents/skills/edit-video/scripts/setup.sh`, enséñame el plan que imprima y pídeme
> permiso antes de instalar. Cuando esté en verde, usa el skill edit-video para editar mi video.

Eso es todo: el skill trae su propio instalador y su propia comprobación. Detalle y Windows: [`references/setup.md`](references/setup.md).

## Usar

Abre tu agente en la carpeta de tu video y di:

```
/edit-video mi-video.mp4 — subtítulos, córtale los silencios y hazlo vertical para Reels
```

o en lenguaje normal: *"edita mi-video.mp4, ponle subtítulos y quítale las pausas"*.

La primera vez te hace **seis preguntas** (idioma, cómo se escribe tu nombre, dónde publicas,
colores, tipografía, logo) y guarda tus reglas en `AGENTS.md`. Nunca más las repites.

Luego, siempre igual:

1. **Escucha y mira** — transcripción con el tiempo de cada palabra, y fotogramas
2. **Te enseña el plan** (beat sheet) y **espera tu OK**
3. **Rough cut** — fuera silencios y respiraciones
4. **Construye** — cada efecto anclado a una palabra
5. **Preview** — le das notas con el tiempo: *"en 0:07 el logo me tapa la cara"*
6. **Render** — MP4 final, local o en la nube

## ¿Tiene que estar prendido mi ordenador?

Corre **donde corre el agente**:

| Tu agente está… | ¿Ordenador prendido? |
|---|---|
| En tu Mac o PC (Claude Code, OpenClaw o Hermes local) | **Sí** |
| En un servidor (OpenClaw o Hermes en un VPS, por Telegram o WhatsApp) | **No** — corre en el servidor |
| En una app de chat sin terminal | No puede correrlo |

El render pesado también puede irse a la nube de HeyGen: `npx hyperframes cloud render`.

## Por qué funciona

Un agente no puede ver un video. Así que se le dan **oídos** (Whisper: cada palabra con su tiempo)
y **ojos** (FFmpeg: fotogramas). Con eso **cada efecto cae en una palabra exacta**, no en un segundo
adivinado. Es lo que separa un montaje hecho a mano de una plantilla.

## Contenido

| | |
|---|---|
| `SKILL.md` | El método, los pasos y las reglas duras |
| `install.sh` | Instala en todos tus agentes |
| `scripts/setup.sh` | **El skill se instala lo que le falta**: plan, permiso, instalación, comprobación |
| `scripts/check.sh` | Comprueba que no falte nada |
| `scripts/ingest.sh` | Oídos y ojos en un comando, con el idioma bien puesto |
| `templates/AGENTS.md.template` | Tus reglas de marca |
| `references/onboarding.md` | Las seis preguntas de la primera vez |
| `references/setup.md` | Instalación en detalle |
| `references/routing.md` | Qué skill de HyperFrames construye cada cosa |
| `references/pipeline.md` | Combinar con Seedance, Grok, Veo, Kling: generar → montar |
| `references/film-it-right.md` | **Cómo grabar una toma editable — léelo antes de grabar** |
| `references/prompts.md` | Pedidos listos, de diario y para lucirse |
| `references/styles.md` | Copiar un estilo |
| `references/troubleshooting.md` | Defecto → arreglo |

## Si hablas español (o cualquier idioma que no sea inglés)

El modelo de Whisper por defecto de HyperFrames es **solo inglés** (`small.en`). Prueba real, el
mismo audio en español:

| | Resultado |
|---|---|
| `hyperframes transcribe audio.wav` | *"We are going to do this for you, for you to do what you want, for you to do what you want…"* |
| `hyperframes transcribe audio.wav -l es` | *"Trabajamos para que tú estés seguro, para que duermas tranquilo, para que tengas la seguridad de que tu propiedad va a estar en buenas manos."* |

Sin el idioma, **inventa**. Este skill siempre le pasa el idioma. A mano: `-l es`.

## English

`/edit-video` edits footage that already exists — captions, dead-air cuts, zooms, overlays, music,
reframing, background removal — in any agent that reads `SKILL.md` skills, on top of HyperFrames.
Install with `bash install.sh`. Docs are in Spanish; the skill works in any language.

## Crédito

Método: **"Let Claude Edit Your Videos"**, [@pauloshimas](https://github.com/aipauloshimas) · The
Creator Stack (2026). Motor: **HyperFrames**, de HeyGen. Skill: Sergio Duran. MIT.
