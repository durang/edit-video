# /edit-video

Skill para **montar un video que ya existe** — subtítulos, cortar silencios, zooms, rótulos,
pop-ups, música, reencuadre a vertical, recorte de fondo, objetos 3D y estilos con nombre.

No genera video. Monta el que ya tienes.

## Cómo funciona

Claude no puede reproducir un video, así que se le dan dos sentidos antes de editar:

- **Oídos → Whisper**: transcripción con el tiempo de **cada palabra**
- **Ojos → FFmpeg**: fotogramas fijos

De ahí sale lo único que importa: **cada efecto se ancla a una palabra, no a un segundo.**

El montaje lo construye **[HyperFrames](https://github.com/heygen-com/hyperframes)** (HeyGen), que
ya trae unos veinte skills propios — subtítulos, gráficos encima, montaje libre, audio, recorte
de fondo. **Este skill no los reimplementa**: es la capa encima que pone el método, el idioma
(español por defecto), las reglas de marca y el checkpoint del beat sheet, y le pasa la
construcción al skill del plugin que toca.

## Instalación

```bash
# el skill
git clone https://github.com/durang/claude-video-edit ~/.claude/skills/edit-video

# las herramientas (macOS)
brew install node ffmpeg python

# el motor
claude plugin marketplace add heygen-com/hyperframes
claude plugin install hyperframes@hyperframes
npx hyperframes doctor
```

Detalle completo, incluido Windows: [`references/setup.md`](references/setup.md).

## Uso

En la carpeta donde esté tu video:

```
/edit-video take.mp4 — subtítulos, córtale los silencios y hazlo vertical para Reels
```

o sin la barra: *"edita take.mp4, ponle subtítulos…"*

Claude transcribe, mira los frames, te enseña el **beat sheet** y espera tu OK antes de construir
nada. Luego rough cut, efectos, preview y render.

Copia `CLAUDE.md.template` como `CLAUDE.md` en tu carpeta con tus fuentes, colores y safe zone,
y no tendrás que repetirlas nunca.

## Contenido

| Archivo | Qué es |
|---|---|
| `SKILL.md` | El método y las reglas duras |
| `references/setup.md` | Instalación y comprobación |
| `references/routing.md` | Qué skill de HyperFrames construye cada cosa |
| `references/pipeline.md` | Combinar con Seedance / Grok / cine-grade: generar → montar |
| `references/film-it-right.md` | Cómo grabar una toma editable — **léelo antes de grabar** |
| `references/prompts.md` | Prompts listos, de diario y para lucirse |
| `references/styles.md` | Copiar un estilo con referencias o nombrando uno famoso |
| `references/troubleshooting.md` | Defecto → arreglo |
| `CLAUDE.md.template` | Tus reglas de estilo |

## Dónde corre

El montaje se arma **en tu máquina**. El render puede ser local (`hyperframes render`) o en la
nube de HeyGen (`hyperframes cloud render`, con créditos).

## Crédito

Método original: **[@pauloshimas](https://github.com/aipauloshimas) · The Creator Stack** (2026),
"Let Claude Edit Your Videos". Motor: **HyperFrames**, de HeyGen.
Este repo es la adaptación del método a un skill repetible, con las reglas duras explícitas.

MIT.
