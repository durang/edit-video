# /edit-video

**Monta videos que ya existen, con cualquier agente.** Subtítulos, cortar silencios, zooms,
rótulos, gráficos encima, música, reencuadre a vertical, recorte de fondo, objetos 3D, estilos con
nombre — y unir clips generados con IA en una pieza terminada.

No genera video. Monta el que ya tienes.

Funciona en **Claude Code, OpenClaw, Hermes Agent, Codex, Cursor, Gemini CLI** y cualquier agente
que lea skills en formato `SKILL.md`.

## Instalar

```bash
git clone https://github.com/durang/edit-video && cd edit-video && bash install.sh
```

Detecta tus agentes, instala el skill y el motor ([HyperFrames](https://github.com/heygen-com/hyperframes))
en todos, y comprueba que no falte nada. Detalle y Windows: [`references/setup.md`](references/setup.md).

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

## Por qué funciona

Un agente no puede ver un video. Así que se le dan **oídos** (Whisper: cada palabra con su tiempo)
y **ojos** (FFmpeg: fotogramas). Con eso **cada efecto cae en una palabra exacta**, no en un segundo
adivinado. Es lo que separa un montaje hecho a mano de una plantilla.

## Contenido

| | |
|---|---|
| `SKILL.md` | El método, los pasos y las reglas duras |
| `install.sh` | Instala en todos tus agentes |
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

El modelo de Whisper por defecto de HyperFrames es **solo inglés** (`small.en`). Este skill siempre
le pasa el idioma, así que cambia solo al modelo multilingüe. Si transcribes a mano:
`npx hyperframes transcribe video.mp4 -l es`.

## English

`/edit-video` edits footage that already exists — captions, dead-air cuts, zooms, overlays, music,
reframing, background removal — in any agent that reads `SKILL.md` skills, on top of HyperFrames.
Install with `bash install.sh`. Docs are in Spanish; the skill works in any language.

## Crédito

Método: **"Let Claude Edit Your Videos"**, [@pauloshimas](https://github.com/aipauloshimas) · The
Creator Stack (2026). Motor: **HyperFrames**, de HeyGen. Skill: Sergio Duran. MIT.
