# Enrutado — qué skill de HyperFrames construye cada cosa

El plugin de HeyGen trae unos veinte skills. `/edit-video` no los sustituye: decide cuál toca,
le pasa el beat sheet aprobado y las reglas del `CLAUDE.md`, y vigila el resultado.

**Ante la duda, `/hyperframes`.** Es la puerta de entrada del plugin y su capa de intención es
la que decide rutas. Nunca se inventa una ruta que el plugin no tiene.

## Editar lo que ya existe

| Sergio dice… | Skill | Nota |
|---|---|---|
| "ponle subtítulos", "subtítulos como los de Hormozi", "subtítulos detrás de mí" | `/embedded-captions` | 35 estilos con nombre. El metraje no se toca. Subtítulos detrás del sujeto = recorte |
| "ponle títulos, rótulos, datos, citas", "vístelo", "que salga un panel al lado" | `/talking-head-recut` | Tarjetas gráficas sobre el clip, que se reproduce entero debajo |
| "monta estos clips", "hazme un reel con esto", "un sizzle", "remix" | `/general-video` | Varias escenas, varios clips, montaje libre |
| "córtale los silencios" | `/general-video` o el skill activo | Rough cut con los tiempos de Whisper |
| "hazlo vertical" | el skill activo, con `--canvas 9:16` | Mantener la cara centrada |
| "ponle música", "baja la música cuando hablo", "fade" | `/hyperframes-audio` | Ducking, crossfades, EQ, compresor |
| "quítame el fondo", "desaparéceme" | `/media-use` → `remove-background` | Necesita el clean plate |
| "ponle una voz", "un whoosh aquí", "música que no tengo" | `/media-use` | TTS, SFX, música, imágenes, LUT |

## Crear algo nuevo con HyperFrames (sin cámara)

Esto no es montar, pero vive en el mismo plugin y a veces se mete dentro de un montaje:

| Sergio dice… | Skill |
|---|---|
| "un logo animado", "un contador que suba", "un mapa que haga zoom", "un tweet animado" | `/motion-graphics` |
| "un explicativo sin cara sobre este tema" | `/faceless-explainer` |
| "un video de lanzamiento de esta web" | `/product-launch-video` |
| "un video con el beat de esta canción" | `/music-to-video` |
| "una presentación / un deck" | `/slideshow` — produce un deck navegable, no un MP4 |

**Ojo:** esto crea con gráficos y tipografía. **No genera personas ni escenas filmadas.** Para
eso es Seedance o Grok (ver `pipeline.md`).

## Lo que se le pasa siempre al skill del plugin

1. El **beat sheet aprobado** (tabla con tiempos y palabras exactas).
2. El `transcript.json` ya corregido — nombres bien escritos.
3. Las reglas del `CLAUDE.md`: idioma, fuentes, colores, safe zone, ritmo.
4. El formato final: 9:16 / 16:9 / 1:1 / 4:5.

## Mantener el plugin al día

Los skills del plugin se actualizan con frecuencia. Antes de un trabajo largo, **con permiso**:

```bash
npx hyperframes skills update
```
