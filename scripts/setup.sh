#!/usr/bin/env bash
# edit-video · auto-instalación. Deja listo TODO lo que el skill necesita, en cualquier agente.
#
#   bash setup.sh                 enseña el plan (qué falta y con qué comando) y NO instala nada
#   bash setup.sh --yes           instala lo que falte, sin preguntar
#   opciones:  --agents claude-code,openclaw,hermes-agent   (por defecto: donde ya esté edit-video)
#              --lang es          idioma del modelo de Whisper a precargar (por defecto: es)
#              --no-warm          no precargar el modelo de Whisper
#
# Pensado para que lo corra un AGENTE: sin --yes solo imprime el plan y sale con código 2,
# para que el agente se lo enseñe al usuario, pida permiso, y vuelva a correrlo con --yes.
set -u

YES=0; WARM=1; LANG_CODE="es"; AGENTS=""
while [ $# -gt 0 ]; do
  case "$1" in
    --yes|-y) YES=1 ;;
    --no-warm) WARM=0 ;;
    --lang) LANG_CODE="${2:-es}"; shift ;;
    --agents) AGENTS="${2:-}"; shift ;;
    -h|--help) sed -n '2,12p' "$0"; exit 0 ;;
  esac
  shift
done

SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"
OS="$(uname -s)"
say(){ printf '%s\n' "$*"; }
have(){ command -v "$1" >/dev/null 2>&1; }

# ── 1. Agentes destino ──────────────────────────────────────────────────────────
if [ -z "$AGENTS" ]; then
  for pair in "claude-code:$HOME/.claude/skills" "openclaw:$HOME/.openclaw/skills" "hermes-agent:$HOME/.hermes/skills" \
              "codex:$HOME/.codex/skills" "cursor:$HOME/.cursor/skills" "gemini-cli:$HOME/.gemini/skills"; do
    a="${pair%%:*}"; d="${pair#*:}"
    [ -e "$d/edit-video" ] && AGENTS="$AGENTS,$a"
  done
  AGENTS="${AGENTS#,}"
fi
if [ -z "$AGENTS" ]; then
  [ -d "$HOME/.claude" ] && AGENTS="$AGENTS,claude-code"
  [ -d "$HOME/.openclaw" ] && AGENTS="$AGENTS,openclaw"
  [ -d "$HOME/.hermes" ] && AGENTS="$AGENTS,hermes-agent"
  AGENTS="${AGENTS#,}"
fi

# ── 2. Qué falta ────────────────────────────────────────────────────────────────
PLAN=()      # comandos a correr
NOTES=()     # cosas que no se pueden automatizar

node_ok(){ have node && [ "$(node -v | sed 's/^v//' | cut -d. -f1)" -ge 22 ] 2>/dev/null; }

case "$OS" in
  Darwin)
    have brew || NOTES+=("Instala Homebrew primero: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
    PKGS=""
    node_ok || PKGS="$PKGS node"
    { have ffmpeg && have ffprobe; } || PKGS="$PKGS ffmpeg"
    have python3 || PKGS="$PKGS python"
    have whisper-cli || PKGS="$PKGS whisper-cpp"
    [ -n "$PKGS" ] && PLAN+=("brew install$PKGS")
    ;;
  Linux)
    SUDO=""; [ "$(id -u)" -ne 0 ] && SUDO="sudo"
    PKGS=""
    { have ffmpeg && have ffprobe; } || PKGS="$PKGS ffmpeg"
    have python3 || PKGS="$PKGS python3"
    have git || PKGS="$PKGS git"
    # HyperFrames compila whisper.cpp solo en Linux si hay cmake y compilador
    have whisper-cli || { have cmake || PKGS="$PKGS cmake"; have cc || PKGS="$PKGS build-essential"; }
    [ -n "$PKGS" ] && PLAN+=("$SUDO apt-get update && $SUDO apt-get install -y$PKGS")
    node_ok || PLAN+=("curl -fsSL https://deb.nodesource.com/setup_22.x | $SUDO -E bash - && $SUDO apt-get install -y nodejs")
    ;;
  MINGW*|MSYS*|CYGWIN*)
    NOTES+=("Windows: en PowerShell → winget install OpenJS.NodeJS.LTS; winget install Gyan.FFmpeg; winget install Python.Python.3.13")
    ;;
  *) NOTES+=("Sistema no reconocido ($OS). Hace falta: Node 22+, FFmpeg, Python 3 y whisper.cpp.") ;;
esac

# Skills de HyperFrames en cada agente
aflags(){ local out=(); IFS=',' read -ra L <<< "$1"; for a in "${L[@]}"; do [ -n "$a" ] && out+=(-a "$a"); done; printf '%s\n' "${out[@]}"; }
HF_SKILL_AGENTS=""
CLAUDE_PLUGIN=0
IFS=',' read -ra AL <<< "$AGENTS"
for a in "${AL[@]}"; do
  [ -z "$a" ] && continue
  case "$a" in
    claude-code)
      if have claude && claude plugin list 2>/dev/null | grep -q "hyperframes@hyperframes"; then :
      elif [ -e "$HOME/.claude/skills/embedded-captions" ]; then :
      elif have claude; then CLAUDE_PLUGIN=1
      else HF_SKILL_AGENTS="$HF_SKILL_AGENTS,claude-code"; fi ;;
    openclaw)     [ -e "$HOME/.openclaw/skills/embedded-captions" ] || HF_SKILL_AGENTS="$HF_SKILL_AGENTS,openclaw" ;;
    hermes-agent) [ -e "$HOME/.hermes/skills/embedded-captions" ]   || HF_SKILL_AGENTS="$HF_SKILL_AGENTS,hermes-agent" ;;
    *)            HF_SKILL_AGENTS="$HF_SKILL_AGENTS,$a" ;;
  esac
done
HF_SKILL_AGENTS="${HF_SKILL_AGENTS#,}"
[ "$CLAUDE_PLUGIN" = 1 ] && PLAN+=("claude plugin marketplace add heygen-com/hyperframes && claude plugin install hyperframes@hyperframes")
[ -n "$HF_SKILL_AGENTS" ] && PLAN+=("npx -y skills add heygen-com/hyperframes -g $(aflags "$HF_SKILL_AGENTS" | paste -sd' ' -) --skill '*' -y")

# Modelo de Whisper multilingüe (se baja la primera vez; mejor ahora que a mitad de un trabajo)
MODEL_DIR="$HOME/.cache/hyperframes/whisper/models"
if [ "$WARM" = 1 ] && ! ls "$MODEL_DIR"/ggml-small.bin >/dev/null 2>&1; then
  PLAN+=("precargar el modelo de Whisper 'small' multilingüe (~470 MB, una vez)")
fi

# ── 3. Enseñar el plan ──────────────────────────────────────────────────────────
say "── edit-video · setup ──"
say "Agentes: ${AGENTS:-ninguno detectado}"
if [ ${#NOTES[@]} -gt 0 ]; then say ""; say "A mano, antes:"; for n in "${NOTES[@]}"; do say "  • $n"; done; fi
if [ ${#PLAN[@]} -eq 0 ]; then
  say ""; say "✅ No falta nada."
  bash "$SKILL_DIR/scripts/check.sh"; exit $?
fi
say ""; say "Plan:"
i=1; for p in "${PLAN[@]}"; do say "  $i. $p"; i=$((i+1)); done

if [ "$YES" != 1 ]; then
  if [ -t 0 ]; then
    printf '\n¿Instalo esto? [s/N] '; read -r r
    case "$r" in s|S|si|sí|y|Y|yes) YES=1 ;; *) say "Nada instalado."; exit 2 ;; esac
  else
    say ""; say "Nada instalado. Enséñale este plan al usuario, pide permiso, y vuelve a correr:"
    say "  bash \"$SKILL_DIR/scripts/setup.sh\" --yes"
    exit 2
  fi
fi

# ── 4. Instalar ─────────────────────────────────────────────────────────────────
fail=0
for p in "${PLAN[@]}"; do
  case "$p" in
    precargar*)
      say "→ precargando Whisper 'small' ($LANG_CODE)…"
      tmp="$(mktemp -d)"
      ffmpeg -v error -f lavfi -i "sine=frequency=440:duration=2" -ar 16000 -ac 1 "$tmp/warm.wav" \
        && npx -y hyperframes transcribe "$tmp/warm.wav" -d "$tmp" -l "$LANG_CODE" -m small --json >/dev/null 2>&1
      rm -rf "$tmp"
      ;;
    *)
      say "→ $p"
      bash -c "$p" || { say "   ✗ falló"; fail=1; }
      ;;
  esac
done

# ── 5. Comprobar ────────────────────────────────────────────────────────────────
say ""
bash "$SKILL_DIR/scripts/check.sh"; rc=$?
[ "$fail" = 1 ] && rc=1
exit $rc
