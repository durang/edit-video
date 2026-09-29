#!/usr/bin/env bash
# edit-video · instalador para cualquier agente.
# Uso:
#   bash install.sh                 detecta los agentes que tienes y los instala en todos
#   bash install.sh claude-code     solo en uno  (nombres: claude-code, openclaw, hermes-agent, codex, cursor…)
#   bash install.sh claude-code,openclaw,hermes-agent
# Usa el instalador universal de skills (npx skills), que soporta más de 70 agentes.
set -euo pipefail
REPO="durang/edit-video"

if [ $# -ge 1 ]; then
  AGENTS="$1"
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
echo "Agentes: $AGENTS"

echo "① Skill edit-video"
npx -y skills add "$REPO" -g -a "$AGENTS" -y

echo "② Skills de HyperFrames (el motor)"
HF_AGENTS="$AGENTS"
# En Claude Code, si ya está el plugin oficial, no se duplican los skills.
if [[ ",$AGENTS," == *",claude-code,"* ]] && command -v claude >/dev/null 2>&1 \
   && claude plugin list 2>/dev/null | grep -q "hyperframes@hyperframes"; then
  HF_AGENTS=$(echo ",$AGENTS," | sed 's/,claude-code,/,/; s/^,//; s/,$//')
  echo "   Claude Code ya tiene el plugin oficial de HyperFrames — no lo duplico."
fi
[ -n "$HF_AGENTS" ] && npx -y skills add heygen-com/hyperframes -g -a "$HF_AGENTS" --skill '*' -y

echo "③ Comprobación"
DIR="$(cd "$(dirname "$0")" && pwd)"
if [ -f "$DIR/scripts/check.sh" ]; then bash "$DIR/scripts/check.sh" || true; fi

echo
echo "Listo. Abre tu agente en la carpeta de tu video y di:  /edit-video mi-video.mp4"
