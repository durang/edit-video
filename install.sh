#!/usr/bin/env bash
# edit-video · instalador de una línea, para personas.
#
#   bash install.sh                                   detecta tus agentes e instala en todos
#   bash install.sh hermes-agent                      solo en uno
#   bash install.sh claude-code,openclaw,hermes-agent varios
#
# Hace dos cosas:
#   1. Pone el skill edit-video en tus agentes (con el instalador universal: npx skills)
#   2. Corre scripts/setup.sh, que instala TODO lo demás que haga falta (HyperFrames, FFmpeg,
#      Whisper y su modelo) y comprueba que quede en verde.
set -euo pipefail
REPO="durang/edit-video"

if [ $# -ge 1 ] && [[ "$1" != --* ]]; then AGENTS="$1"; shift
else
  AGENTS=""
  [ -d "$HOME/.claude" ]   && AGENTS="$AGENTS,claude-code"
  [ -d "$HOME/.openclaw" ] && AGENTS="$AGENTS,openclaw"
  [ -d "$HOME/.hermes" ]   && AGENTS="$AGENTS,hermes-agent"
  [ -d "$HOME/.codex" ]    && AGENTS="$AGENTS,codex"
  [ -d "$HOME/.cursor" ]   && AGENTS="$AGENTS,cursor"
  [ -d "$HOME/.gemini" ]   && AGENTS="$AGENTS,gemini-cli"
  AGENTS="${AGENTS#,}"
fi
[ -n "$AGENTS" ] || { echo "No detecté ningún agente. Pásalo a mano: bash install.sh claude-code"; exit 1; }
command -v npx >/dev/null 2>&1 || { echo "Falta Node.js 22+ (trae npx). macOS: brew install node · Linux: https://nodejs.org"; exit 1; }
echo "Agentes: $AGENTS"

# npx skills quiere un -a por agente
AF=(); IFS=',' read -ra L <<< "$AGENTS"; for a in "${L[@]}"; do [ -n "$a" ] && AF+=(-a "$a"); done

echo "① edit-video"
npx -y skills add "$REPO" -g "${AF[@]}" -y

echo "② todo lo demás"
SETUP="$HOME/.agents/skills/edit-video/scripts/setup.sh"
[ -f "$SETUP" ] || SETUP="$(cd "$(dirname "$0")" && pwd)/scripts/setup.sh"
bash "$SETUP" --agents "$AGENTS" "$@"

echo
echo "Listo. Abre tu agente en la carpeta de tu video y di:  /edit-video mi-video.mp4"
