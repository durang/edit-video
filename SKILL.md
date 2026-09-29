---
name: edit-video
description: Edit or package a video that ALREADY EXISTS — captions, cutting dead air, punch-in zooms, title cards, lower thirds, graphic overlays, pop-ups, music and SFX, 16:9 to 9:16 reframing, background removal, 3D objects, a named style (movie trailer, Vox explainer), or assembling several clips (for example shots generated with Seedance, Grok, Veo or Kling) into one finished MP4. Works in any agent that reads SKILL.md (Claude Code, OpenClaw, Hermes Agent, Codex, Cursor…) on top of the HyperFrames skills. Triggers on /edit-video, "edita mi video", "ponle subtítulos", "córtale los silencios", "hazlo vertical para Reels", "monta estos clips", "edit my video", "add captions", "cut the pauses", or a video file plus an edit request. NOT for generating new footage from a text prompt, and NOT for re-filming one take from new camera angles.
metadata:
  version: 2.1.0
  author: Sergio Duran
  method: "Let Claude Edit Your Videos — @pauloshimas / The Creator Stack"
  engine: heygen-com/hyperframes
---

# /edit-video — montar un video que ya existe

Tú (el agente) no reproduces video. Así que antes de editar nada te das **oídos** (transcripción
con el tiempo de cada palabra) y **ojos** (fotogramas). Con eso planeas el montaje, lo enseñas,
esperas el OK, y le pasas la construcción a los skills de **HyperFrames**, que escriben el video
como una página web y lo renderizan en MP4.

**Cada efecto se ancla a una PALABRA, no a un segundo.** Eso es lo que hace que parezca hecho a mano.

Este skill **no reimplementa HyperFrames**: pone el método, las reglas y el idioma, y enruta.

---

## Paso 0 · ¿Editar o crear?

| El usuario tiene… | Qué hacer |
|---|---|
| Un video grabado, o clips ya generados | **Seguir aquí** |
| Solo una idea, sin material filmado | **No es este skill.** Se genera primero (Seedance, Grok, Veo, Kling…) y el montaje entra al final. Ver `references/pipeline.md` |
| Solo gráficos, sin cámara (logo animado, explicativo sin cara) | Enrutar directo a HyperFrames: `/motion-graphics`, `/faceless-explainer` |

Si no está claro, **una** pregunta de una línea.

## Paso 1 · Todo instalado — el skill se instala lo que le falta

`SKILL_DIR` es la carpeta donde está este `SKILL.md`. Normalmente una de estas:
`~/.agents/skills/edit-video` · `~/.claude/skills/edit-video` · `~/.openclaw/skills/edit-video` ·
`~/.hermes/skills/edit-video`. Si no la sabes: `ls -d ~/.*/skills/edit-video ~/.agents/skills/edit-video`.

```bash
bash SKILL_DIR/scripts/check.sh
```

- **Sale en verde** → sigue al Paso 2.
- **Falta algo** → corre `bash SKILL_DIR/scripts/setup.sh`. **Sin `--yes` no instala nada**: solo
  imprime el plan exacto (qué falta y con qué comando) y sale con código 2. **Enséñale ese plan al
  usuario tal cual, pide permiso**, y con su sí vuelve a correr `bash SKILL_DIR/scripts/setup.sh --yes`.
  Instala FFmpeg, Node, whisper-cpp, los skills de HyperFrames en este agente y el modelo de Whisper
  multilingüe, y termina con `check.sh`.
- **Nunca instales sin permiso. Nunca trabajes alrededor de lo que falta.**

Una vez en verde, no se vuelve a instalar: las siguientes sesiones pasan directo.

## Paso 2 · Reglas del proyecto — onboarding la primera vez

Busca en la carpeta del video un `AGENTS.md` (o `CLAUDE.md`) con una sección `## edit-video`.

- **Si existe**, léela y aplícala en todo: idioma, nombres, colores, tipografías, safe zone, ritmo.
- **Si no existe**, haz el onboarding de `references/onboarding.md`: seis preguntas cortas, y
  escribe el archivo de reglas desde `templates/AGENTS.md.template`. Una sola vez; las siguientes
  sesiones ya lo encuentran.

## Paso 3 · Oídos y ojos

```bash
bash <SKILL_DIR>/scripts/ingest.sh TOMA.mp4 es        # idioma hablado: es, en, pt…
```

Deja en `TOMA.edit/`: `metadata.json`, `transcript.json` (palabras con `start`/`end`),
`transcript.txt` legible con tiempos, y `frames/` (2 fps si dura ≤10 s, 1 fps si más).

- **El idioma siempre se pasa.** El modelo por defecto de HyperFrames es `small.en`, **solo
  inglés**: sin `-l es` el español sale destrozado. Con `-l es` cambia solo al modelo multilingüe.
- **Corrige los nombres propios** (de las reglas del proyecto) en la transcripción antes de usarla.
  Whisper escribe los nombres como suenan.
- **Lee TODOS los frames junto con las palabras.** Luego cuéntale al usuario, breve: qué dice,
  cuándo, qué hay en el plano, dónde están la cara, las manos y los huecos libres.

## Paso 4 · Beat sheet, y PARADA

```
| inicio | fin | palabras exactas | qué aparece en pantalla | dónde | sonido |
```

Declara formato (9:16 / 16:9 / 1:1 / 4:5), safe zone y duración estimada.
**Espera el OK explícito. No construyas nada antes.** Cambiar en papel es gratis.

## Paso 5 · Rough cut

Fuera las pausas de más de 0.3 s y las respiraciones, **nunca dentro de una palabra**, con un beat
corto antes de cada remate. Reporta la duración nueva. Efectos, después.

## Paso 6 · Construir — enrutar al skill de HyperFrames

| Lo que se pide | Skill |
|---|---|
| Subtítulos, sin tocar el metraje | `/embedded-captions` |
| Tarjetas encima: títulos, rótulos, datos, citas, panel lateral, PiP | `/talking-head-recut` |
| Varios clips, reel, sizzle, remix, montaje libre | `/general-video` |
| Pieza corta de motion: logo, contador, mapa, titular animado | `/motion-graphics` |
| Música, ducking, fades, efectos de audio | `/hyperframes-audio` |
| Recorte de fondo, TTS, SFX, música, imágenes | `/media-use` |
| No está claro | `/hyperframes` — la puerta de entrada de HyperFrames |

Al skill de HyperFrames le pasas: **el beat sheet aprobado, el `transcript.json` corregido, las
reglas del proyecto y el formato**. Él construye; tú vigilas que se cumpla cada regla.
Detalle: `references/routing.md`.

## Paso 7 · Preview, notas, verificar, render

```bash
npx hyperframes preview                 # el usuario lo mira en su navegador
npx hyperframes snapshot                # TÚ miras el frame antes de decir "listo"
npx hyperframes render -o final.mp4     # render local
npx hyperframes cloud render            # o en la nube de HeyGen (créditos, requiere auth login)
```

Notas del usuario: una por línea, con el tiempo. Aplica, haz snapshot del frame afectado,
míralo, y vuelve a enseñar. Guarda `v1`, `v2`, `v3`… antes de cada ronda.

---

## Reglas duras

1. **Beat sheet antes de construir.** Siempre.
2. **Rough cut primero, efectos después.**
3. **Nunca cortar dentro de una palabra.**
4. **El idioma siempre se declara al transcribir.** Nunca el modelo `.en` por defecto si no es inglés.
5. **Nombres propios corregidos** en transcripción y subtítulos.
6. **Safe zone**: nada de texto en el 20% inferior ni pegado al borde derecho (botones de la app).
7. **Una nota = un cambio**, con el tiempo. Qué, dónde, cuándo — nunca cómo.
8. **Versionar** antes de cada ronda.
9. **Snapshot antes de decir "listo".** Decirlo sin haber mirado el frame es mentir.
10. **La voz del usuario nunca se sustituye ni se re-sintetiza.**
11. **Máximo un zoom cada cinco segundos.** Lo raro es lo que impacta.
12. **El director es el usuario.** El gusto no se delega.

## Dónde corre

**Donde corre el agente.** Necesita el disco con los videos, Node, FFmpeg y whisper-cpp.

- Agente en tu ordenador (Claude Code, OpenClaw o Hermes en tu Mac) → **el ordenador tiene que
  estar prendido**.
- Agente en un servidor (OpenClaw o Hermes en un VPS, hablándole por Telegram o WhatsApp) → corre
  en el servidor; **tu ordenador puede estar apagado**. `setup.sh` funciona igual en Linux.
- El render pesado puede irse a la nube de HeyGen con `npx hyperframes cloud render`.
- Un chat sin terminal ni disco (una app de chat en la nube) no puede correrlo.

## Referencias

| Archivo | Cuándo |
|---|---|
| `references/onboarding.md` | Primera vez en una carpeta: las seis preguntas |
| `references/setup.md` | Instalación en cualquier agente |
| `references/routing.md` | Qué skill de HyperFrames construye cada cosa |
| `references/pipeline.md` | Combinar con modelos generativos: generar → montar |
| `references/film-it-right.md` | **Antes de grabar** |
| `references/prompts.md` | Pedidos listos, de diario y para lucirse |
| `references/styles.md` | Copiar un estilo |
| `references/troubleshooting.md` | Defecto → arreglo |
| `scripts/check.sh` · `scripts/setup.sh` · `scripts/ingest.sh` | Comprobar · auto-instalar · oídos y ojos |
| `templates/AGENTS.md.template` | Reglas del proyecto del usuario |
