# Setup — quince minutos, una vez

## Las seis piezas

| Pieza | Para qué | Coste |
|---|---|---|
| **Claude Code** | El editor. Lee los archivos, corre comandos, escribe el montaje | Claude Pro ($20/mes) o superior |
| **HyperFrames** | El motor. Convierte una página web en video y renderiza el MP4 | Gratis, open source (HeyGen) |
| **Whisper** | Los oídos. Voz a texto con tiempo por palabra | Gratis (OpenAI) |
| **FFmpeg** | Los ojos y las tijeras. Frames, cortes, audio, conversión | Gratis |
| **Python 3** | Corre Whisper y los scripts sueltos | Gratis |
| **Node.js 22+** | Corre HyperFrames | Gratis |

HyperFrames se baja su propio Chrome para renderizar.

## Instalación

```bash
# macOS
brew install node ffmpeg python whisper-cpp

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

## Este skill

```bash
git clone https://github.com/durang/claude-video-edit ~/.claude/skills/video-edit
```

O se sube como skill de cuenta para usarlo desde Cowork.

## Dónde corre

**Siempre en la máquina del usuario.** HyperFrames renderiza abriendo un Chrome local sobre los
archivos de video locales. No hay versión en la nube. Una sesión remota puede orquestar los
comandos por un puente, pero el motor, los archivos y el MP4 final viven en la máquina.
