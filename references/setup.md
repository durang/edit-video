# Instalación — en cualquier agente

`edit-video` es un skill en formato `SKILL.md`, el estándar abierto que leen Claude Code,
OpenClaw, Hermes Agent, Codex, Cursor, Gemini CLI y más de 70 agentes. **Es la misma carpeta
para todos.**

## Lo que hace falta

| Pieza | Para qué | Coste |
|---|---|---|
| **Un agente** | Claude Code, OpenClaw, Hermes Agent, Codex, Cursor… | Según el agente |
| **HyperFrames** | El motor: escribe el video como página web y lo renderiza en MP4 | Gratis, open source (HeyGen) |
| **whisper-cpp** | Los oídos: HyperFrames transcribe con él (`whisper-cli`) | Gratis |
| **FFmpeg** | Los ojos y las tijeras: frames, cortes, audio | Gratis |
| **Node.js 22+** | Corre HyperFrames | Gratis |
| **Python 3** | Scripts auxiliares | Gratis |

HyperFrames usa el Chrome que tengas (o baja uno) y descarga el modelo de Whisper la primera vez.

## Opción A — un comando (recomendado)

```bash
git clone https://github.com/durang/edit-video && cd edit-video && bash install.sh
```

`install.sh` detecta qué agentes tienes (Claude Code, OpenClaw, Hermes, Codex, Cursor, Gemini),
instala `edit-video` y los skills de HyperFrames en todos, y corre la comprobación.

Solo en uno:

```bash
bash install.sh hermes-agent
bash install.sh claude-code,openclaw
```

## Opción B — que lo instale el propio agente

El skill trae su instalador. Cualquier agente con terminal puede hacerlo solo:

```bash
npx skills add durang/edit-video -g -y
bash ~/.agents/skills/edit-video/scripts/setup.sh          # enseña el plan, no instala
bash ~/.agents/skills/edit-video/scripts/setup.sh --yes    # con permiso del usuario
```

## Opción C — a mano con el instalador universal

```bash
npx skills add durang/edit-video -g -a claude-code -a openclaw -a hermes-agent -y
npx skills add heygen-com/hyperframes -g -a claude-code -a openclaw -a hermes-agent --skill '*' -y
```

En **Claude Code** también se puede usar el plugin oficial en vez de los skills sueltos:

```bash
claude plugin marketplace add heygen-com/hyperframes
claude plugin install hyperframes@hyperframes
```

(`install.sh` lo detecta y no duplica.)

## Las herramientas del sistema

```bash
# macOS
brew install node ffmpeg python whisper-cpp

# Windows
winget install OpenJS.NodeJS.LTS
winget install Gyan.FFmpeg
winget install Python.Python.3.13

# Linux
sudo apt-get install -y nodejs ffmpeg python3
```

## Comprobar

```bash
bash scripts/check.sh          # desde la carpeta del skill
npx hyperframes doctor
```

**Después de instalar, abre una terminal nueva o una sesión nueva del agente** para que encuentre
las herramientas y el skill.

## Transcribir en otro idioma que no sea inglés

```bash
npx hyperframes transcribe TOMA.mp4 -l es -m small --json
```

El modelo por defecto de HyperFrames es **`small.en`, solo inglés**. Con `-l es` (o `pt`, `fr`…)
cambia solo al modelo multilingüe. **Sin `-l`, el español sale destrozado.** `scripts/ingest.sh`
ya lo hace bien.

## Render en la nube (opcional)

```bash
npx hyperframes auth login      # una vez, con cuenta de HeyGen
npx hyperframes cloud render    # sube, renderiza en HeyGen, descarga el MP4
```

Se paga con créditos de HeyGen. Útil para renders largos. El montaje sigue armándose en local.

## Dónde corre

En **la máquina del usuario**: ahí están Node, FFmpeg y los videos. Un agente remoto sin acceso
al disco no puede correr esto.
