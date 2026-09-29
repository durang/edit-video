#!/usr/bin/env bash
# edit-video · preflight. Comprueba todo lo que hace falta y dice exactamente qué falta.
# Uso: bash scripts/check.sh            Sale con 0 si está todo, 1 si falta algo.
set -u
ok=0; warn=0
g(){ printf '  \033[32m✓\033[0m %s\n' "$1"; }
b(){ printf '  \033[31m✗\033[0m %s\n      → %s\n' "$1" "$2"; ok=1; }
w(){ printf '  \033[33m!\033[0m %s\n      → %s\n' "$1" "$2"; warn=1; }

OS="$(uname -s)"
if [ "$OS" = "Darwin" ]; then PM="brew install"; else PM="sudo apt-get install -y"; fi

echo "── edit-video · preflight ──"

# Node 22+
if command -v node >/dev/null 2>&1; then
  v=$(node -v | sed 's/^v//' | cut -d. -f1)
  if [ "${v:-0}" -ge 22 ]; then g "Node $(node -v)"; else b "Node $(node -v) — hace falta 22 o más" "$PM node"; fi
else b "Node no está instalado" "$PM node"; fi

# FFmpeg + ffprobe
if command -v ffmpeg >/dev/null 2>&1 && command -v ffprobe >/dev/null 2>&1; then
  g "FFmpeg $(ffmpeg -version 2>/dev/null | head -1 | awk '{print $3}')"
else b "FFmpeg / ffprobe no están" "$PM ffmpeg"; fi

# Python (opcional, lo usan scripts sueltos)
if command -v python3 >/dev/null 2>&1; then g "Python $(python3 --version 2>&1 | awk '{print $2}')"
else w "Python 3 no está (opcional)" "$PM python"; fi

# HyperFrames CLI
if command -v npx >/dev/null 2>&1; then
  hv=$(npx -y hyperframes --version 2>/dev/null | tail -1)
  if [ -n "$hv" ]; then g "HyperFrames CLI $hv"; else b "HyperFrames CLI no responde" "npx -y hyperframes doctor"; fi
fi

# Skills de HyperFrames en algún agente
found=""
for d in "$HOME/.claude/plugins" "$HOME/.claude/skills" "$HOME/.openclaw/skills" "$HOME/.hermes/skills" "$HOME/.agents/skills" "$HOME/.codex/skills"; do
  if [ -d "$d" ] && grep -rqs "name: embedded-captions" "$d" 2>/dev/null; then found="$found ${d/#$HOME/~}"; fi
done
if [ -n "$found" ]; then g "Skills de HyperFrames en:$found"
else b "No encuentro los skills de HyperFrames en ningún agente" "npx skills add heygen-com/hyperframes -g -y   (o: bash install.sh)"; fi

# Doctor de HyperFrames (Chrome headless, deps de render)
if [ "$ok" -eq 0 ]; then
  if npx -y hyperframes doctor >/tmp/edit-video-doctor.log 2>&1; then g "hyperframes doctor en verde"
  else w "hyperframes doctor marcó algo" "cat /tmp/edit-video-doctor.log  y seguir su indicación"; fi
fi

echo "──────────────────────────"
if [ "$ok" -eq 0 ]; then
  [ "$warn" -eq 0 ] && echo "✅ Todo listo." || echo "✅ Listo, con avisos."
  exit 0
else
  echo "❌ Falta algo. Pide permiso al usuario antes de instalar."
  exit 1
fi
