---
name: edit-video
description: Use when the user wants a video that ALREADY EXISTS edited or packaged — captions, cutting dead air, punch-in zooms, title cards, lower thirds, graphic overlays, pop-ups, music and SFX, 16:9 to 9:16 reframing, background removal, 3D objects, a named style (movie trailer, Vox explainer), or assembling several clips (for example shots generated in Seedance or Grok) into one finished piece. Sergio's layer on top of the HyperFrames plugin — Spanish-first defaults, his brand rules, the beat-sheet checkpoint — that routes the build to the right HyperFrames skill. Triggers on /edit-video, "edita mi video", "ponle subtítulos", "córtale los silencios", "hazlo vertical para Reels", "monta estos clips", "edit my video", a video file plus an edit request. NOT for generating new footage from a prompt (that is the Seedance/Grok canon) and NOT for multicam re-filming of one take (multiángulo).
---

# /edit-video — montar un video que ya existe

**Método:** "Let Claude Edit Your Videos", **@pauloshimas / The Creator Stack**.
**Motor:** plugin **HyperFrames** de HeyGen, que ya trae ~20 skills propios.

Este skill **no reimplementa HyperFrames**. Es la capa de Sergio encima: decide **qué** se hace,
con **qué reglas** y en **qué idioma**, y le entrega la construcción al skill del plugin que toca.

---

## Paso 0 · ¿Esto es editar o crear?

| El usuario tiene… | Va a… |
|---|---|
| Un video grabado, o clips ya generados | **Aquí.** Seguir leyendo |
| Solo una idea, sin material | **No es aquí.** Es generación: canon Seedance/Grok |
| Una toma y quiere verla desde otros ángulos | **No es aquí.** Es multiángulo (Seedance) |
| Una toma y quiere la luz de una película | **No es aquí.** Es cine-grade (Seedance) |

Si no está claro, se pregunta en una línea. Si hay que generar **y** montar, se genera primero
y el montaje entra al final (ver `references/pipeline.md`).

## Paso 1 · Preflight (una vez por sesión)

```bash
npx hyperframes doctor
claude plugin list | grep -i hyperframes
```

Si el plugin no está, se instala con permiso del usuario (`references/setup.md`). Nunca se
trabaja alrededor de una herramienta que falta.

## Paso 2 · Oídos y ojos

```bash
npx hyperframes transcribe TOMA.mp4 --json --model small      # multilingüe
ffmpeg -i TOMA.mp4 -vf fps=1 -q:v 3 frames/f_%03d.jpg
```

- **Nunca un modelo `.en`** (`small.en`, `base.en`) si se habla español. El propio plugin trae
  `small.en` en sus ejemplos y con eso el español sale destrozado. Español → `small`, `medium`
  o `large-v3`.
- **Los nombres propios se dan antes de transcribir** — nombre, marca, producto — y se corrigen
  en la transcripción y en los subtítulos. Whisper escribe los nombres como suenan.
- Se leen **todos** los frames junto con las palabras, y se le cuenta al usuario qué dice,
  cuándo, y qué hay en el plano en cada momento.

**Cada efecto se ancla a una PALABRA, no a un segundo.** Es lo que hace que parezca hecho a mano.

## Paso 3 · Beat sheet, y PARADA

Tabla: `inicio | fin | palabras exactas | qué aparece | dónde | sonido`.
Declarar formato y safe zone. **Esperar el OK. Nunca construir antes.**

## Paso 4 · Rough cut

Pausas de más de 0.3 s y respiraciones fuera, nunca dentro de una palabra, un beat corto antes
de cada remate. Reportar la duración nueva.

## Paso 5 · Construir — se enruta al skill del plugin

| Lo que se pide | Skill de HyperFrames |
|---|---|
| Subtítulos, sin tocar el metraje | `/embedded-captions` |
| Tarjetas gráficas encima: títulos, rótulos, datos, citas, PiP | `/talking-head-recut` |
| Montaje libre, varios clips, reel, sizzle, remix | `/general-video` |
| Pieza corta de motion: logo, contador, mapa, titular animado | `/motion-graphics` |
| Música, ducking, fades, efectos de audio | `/hyperframes-audio` |
| Recorte de fondo, TTS, música, imágenes, SFX | `/media-use` |
| No está claro | `/hyperframes` — la puerta de entrada del plugin |

Detalle en `references/routing.md`. Al skill del plugin se le pasa **el beat sheet aprobado y
las reglas del `CLAUDE.md`**: él construye, este skill vigila que se cumplan.

## Paso 6 · Preview, notas, verificar, render

```bash
npx hyperframes preview                  # el usuario mira en el navegador
npx hyperframes snapshot                 # Claude mira el frame antes de decir "listo"
npx hyperframes render -o final.mp4      # render local
npx hyperframes cloud render             # o en la nube de HeyGen, con créditos
```

---

## Reglas duras

- **Beat sheet antes de construir.** Siempre. Cambiar en papel es gratis.
- **Rough cut primero, efectos después.**
- **Nunca cortar dentro de una palabra.**
- **Español por defecto**: modelo multilingüe, subtítulos en español, nombres corregidos.
- **Safe zone**: nada de texto en el 20% inferior ni pegado al borde derecho.
- **Una nota, un cambio, con el tiempo.** Qué, dónde, cuándo — nunca cómo.
- **Versionar** antes de cada ronda (v1, v2, v3…).
- **Snapshot antes de decir "listo".** Decirlo sin haber mirado el frame es mentir.
- **La voz del usuario nunca se sustituye ni se re-sintetiza.**
- **El director es el usuario.** El gusto no se delega.

## Dónde corre

El montaje se arma **en la máquina del usuario** (Node, FFmpeg, sus archivos). El render puede
ser local (`render`) o en la nube de HeyGen (`cloud render`, con créditos, tras
`npx hyperframes auth login`). Una sesión remota de Cowork puede lanzar los comandos en el
ordenador por el puente, pero no puede correr HyperFrames dentro de su propio contenedor.

## Referencias

| Archivo | Cuándo |
|---|---|
| `references/setup.md` | Instalación y comprobación |
| `references/routing.md` | Qué skill del plugin construye cada cosa |
| `references/pipeline.md` | Combinar con Seedance / Grok / cine-grade: generar → montar |
| `references/film-it-right.md` | **Antes de grabar** |
| `references/prompts.md` | Prompts listos, de diario y para lucirse |
| `references/styles.md` | Copiar un estilo |
| `references/troubleshooting.md` | Defecto → arreglo |
| `CLAUDE.md.template` | Las reglas de marca del usuario, para su carpeta |
