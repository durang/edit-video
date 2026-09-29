# video-edit

Skill para **montar un video que ya existe** — subtítulos, cortar silencios, zooms, rótulos,
pop-ups, música, reencuadre a vertical, recorte de fondo, objetos 3D y estilos con nombre.

No genera video. Monta el que ya tienes.

## Cómo funciona

Claude no puede reproducir un video, así que se le dan dos sentidos antes de editar:

- **Oídos → Whisper**: transcripción con el tiempo de **cada palabra**
- **Ojos → FFmpeg**: fotogramas fijos

De ahí sale lo único que importa: **cada efecto se ancla a una palabra, no a un segundo.**

El montaje lo escribe **[HyperFrames](https://github.com/heygen-com/hyperframes)** (HeyGen) como
una página web, y lo renderiza en MP4. Sin timeline, sin Premiere.

## Instalación

```bash
# el skill
git clone https://github.com/durang/claude-video-edit ~/.claude/skills/video-edit

# las herramientas (macOS)
brew install node ffmpeg python whisper-cpp

# el motor
claude plugin marketplace add heygen-com/hyperframes
claude plugin install hyperframes@hyperframes
npx hyperframes doctor
```

Detalle completo, incluido Windows: [`references/setup.md`](references/setup.md).

## Uso

En la carpeta donde esté tu video:

```
edita take.mp4 — subtítulos, córtale los silencios y hazlo vertical para Reels
```

Claude transcribe, mira los frames, te enseña el **beat sheet** y espera tu OK antes de construir
nada. Luego rough cut, efectos, preview y render.

Copia `CLAUDE.md.template` como `CLAUDE.md` en tu carpeta con tus fuentes, colores y safe zone,
y no tendrás que repetirlas nunca.

## Contenido

| Archivo | Qué es |
|---|---|
| `SKILL.md` | El método y las reglas duras |
| `references/setup.md` | Instalación y comprobación |
| `references/film-it-right.md` | Cómo grabar una toma editable — **léelo antes de grabar** |
| `references/prompts.md` | Prompts listos, de diario y para lucirse |
| `references/styles.md` | Copiar un estilo con referencias o nombrando uno famoso |
| `references/troubleshooting.md` | Defecto → arreglo |
| `CLAUDE.md.template` | Tus reglas de estilo |

## Dónde corre

**Siempre en tu máquina.** HyperFrames renderiza con un Chrome local sobre tus archivos. No hay
versión en la nube. Una sesión remota puede lanzar los comandos por un puente, pero el motor,
los archivos y el MP4 viven en tu ordenador.

## Crédito

Método original: **[@pauloshimas](https://github.com/aipauloshimas) · The Creator Stack** (2026),
"Let Claude Edit Your Videos". Motor: **HyperFrames**, de HeyGen.
Este repo es la adaptación del método a un skill repetible, con las reglas duras explícitas.

MIT.
