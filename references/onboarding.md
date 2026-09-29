# Onboarding — la primera vez en una carpeta

Si en la carpeta del video no hay un `AGENTS.md` (o `CLAUDE.md`) con una sección `## edit-video`,
se hace esto **una sola vez**. Son seis preguntas, en un solo mensaje, con respuestas por defecto
para que la persona pueda contestar "todo por defecto" y seguir.

## Las seis preguntas

1. **¿En qué idioma hablas en tus videos?** (por defecto: español) — decide el modelo de Whisper.
2. **¿Cómo se escriben tu nombre, tu @, tu marca y tus productos?** — Whisper los escribe como
   suenan; esto los corrige siempre.
3. **¿Dónde se publica sobre todo?** Reels/TikTok (9:16) · YouTube (16:9) · feed (1:1 o 4:5).
   (por defecto: 9:16)
4. **¿Colores de marca?** Uno principal y uno de acento, en hex o con palabras.
   (por defecto: blanco con acento amarillo)
5. **¿Tipografía?** Una para titulares y otra para subtítulos, o "la que veas".
   (por defecto: una sans gruesa, tipo Inter Black / Montserrat ExtraBold)
6. **¿Tienes logo, música o efectos de sonido?** Rutas a los archivos, o "no".

## Qué se escribe

Con las respuestas, se rellena `templates/AGENTS.md.template` y se guarda como **`AGENTS.md`** en
la carpeta del video. Si el agente es Claude Code, se crea además un **`CLAUDE.md`** de una línea:

```
@AGENTS.md
```

Así Claude Code, OpenClaw, Hermes, Codex y Cursor leen **el mismo archivo**. Si ya existía un
`AGENTS.md` con otras cosas, **no se pisa**: se añade la sección `## edit-video` al final.

## Qué NO se pregunta

- Nada técnico (modelos, fps, codecs). Eso lo decide el skill.
- Nada que se pueda deducir viendo el video (encuadre, luz, fondo).
- Más de seis cosas. Si falta algo, se pregunta cuando haga falta, no antes.
