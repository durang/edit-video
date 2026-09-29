# Setup — quince minutos, una vez

## Las seis piezas

| Pieza | Para qué | Coste |
|---|---|---|
| **Claude Code** | El editor. Lee los archivos, corre comandos, escribe el montaje | Claude Pro ($20/mes) o superior |
| **HyperFrames** | El motor. Convierte una página web en video y renderiza el MP4 | Gratis, open source (HeyGen) |
| **Whisper** | Los oídos. Voz a texto con tiempo por palabra. **HyperFrames trae el suyo** (`hyperframes transcribe`) | Gratis (OpenAI) |
| **FFmpeg** | Los ojos y las tijeras. Frames, cortes, audio, conversión | Gratis |
| **Python 3** | Corre Whisper y los scripts sueltos | Gratis |
| **Node.js 22+** | Corre HyperFrames | Gratis |

HyperFrames se baja su propio Chrome para renderizar.

## Instalación

```bash
# macOS
brew install node ffmpeg python
# whisper-cpp es opcional: HyperFrames transcribe por su cuenta y baja el modelo la primera vez

# Windows
winget install OpenJS.NodeJS.LTS
winget install Gyan.FFmpeg
winget install Python.Python.3.13
python -m pip install faster-whisper
```

Claude Code:

```bash
curl -fsSL https://claude.ai/install.sh | bash      # macOS
irm https://claude.ai/install.ps1 | iex             # Windows
```

El plugin:

```bash
claude plugin marketplace add heygen-com/hyperframes
claude plugin install hyperframes@hyperframes
```

Comprobación:

```bash
npx hyperframes doctor
```

**Después de instalar, abrir una terminal nueva o empezar una sesión de Claude nueva**, para que
el sistema encuentre las herramientas.

## Prompt de instalación asistida

Pegar en una sesión nueva de Claude Code, en cualquier carpeta:

> Quiero que edites mis videos con HyperFrames. Comprueba si este ordenador tiene Node.js 22 o
> más nuevo, FFmpeg, Python 3 y Whisper (faster-whisper en Windows, whisper-cpp en Mac). Instala
> lo que falte, y pregúntame antes de cada instalación. Luego corre
> `claude plugin marketplace add heygen-com/hyperframes` y
> `claude plugin install hyperframes@hyperframes`, y corre `npx hyperframes doctor`.
> Arregla lo que marque y termina con una lista de lo instalado, con versiones.

## Transcribir en español

```bash
npx hyperframes transcribe TOMA.mp4 --json --model small
```

**Nunca `--model small.en` ni `base.en` si se habla español.** Los `.en` son solo inglés y el
plugin los usa en sus ejemplos. Para español: `small` (rápido), `medium` (mejor), `large-v3`
(el mejor, más lento). El modelo se baja la primera vez.

## Render en la nube (opcional)

```bash
npx hyperframes auth login      # una vez, con cuenta HeyGen
npx hyperframes cloud render    # zip, sube, renderiza en HeyGen, descarga el MP4
```

Se paga con créditos de HeyGen. Útil para renders largos o para no tener el Mac ocupado.
El montaje sigue armándose en local.

## Este skill

```bash
git clone https://github.com/durang/claude-video-edit ~/.claude/skills/edit-video
```

Se invoca con **`/edit-video`**, o simplemente pidiendo "edita mi video".

O se sube como skill de cuenta para usarlo desde Cowork.

## Dónde corre

El montaje se arma **en la máquina del usuario**: Node, FFmpeg y los archivos de video viven ahí.
El **render** puede ser local o en la nube de HeyGen (`cloud render`). Una sesión remota de
Cowork puede lanzar los comandos en el ordenador por el puente, pero no puede correr HyperFrames
dentro de su propio contenedor.
