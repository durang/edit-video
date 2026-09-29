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

# whisper-cpp (HyperFrames transcribe con whisper-cli)
if command -v whisper-cli >/dev/null 2>&1; then g "whisper-cpp $(command -v whisper-cli)"
else w "whisper-cpp no está — HyperFrames lo usa para transcribir" "$PM whisper-cpp"; fi

# HyperFrames CLI
if command -v npx >/dev/null 2>&1; then
  hv=$(npx -y hyperframes --version 2>/dev/null | tail -1)
  if [ -n "$hv" ]; then g "HyperFrames CLI $hv"; else b "HyperFrames CLI no responde" "npx -y hyperframes doctor"; fi
fi

# Skills de HyperFrames y edit-video, agente por agente
hf=""; ev=""
for pair in "Claude Code:$HOME/.claude/skills" "OpenClaw:$HOME/.openclaw/skills" "Hermes:$HOME/.hermes/skills" "Codex:$HOME/.codex/skills" "Cursor:$HOME/.cursor/skills" "Gemini:$HOME/.gemini/skills"; do
  name="${pair%%:*}"; d="${pair#*:}"
  [ -d "$d" ] || continue
  [ -e "$d/embedded-captions" ] && hf="$hf, $name"
  [ -e "$d/edit-video" ] && ev="$ev, $name"
done
# En Claude Code, HyperFrames suele venir como plugin oficial
if command -v claude >/dev/null 2>&1 && claude plugin list 2>/dev/null | grep -q "hyperframes@hyperframes"; then
  case "$hf" in *"Claude Code"*) ;; *) hf="$hf, Claude Code (plugin)";; esac
fi
if [ -n "$ev" ]; then g "edit-video en: ${ev#, }"; else w "edit-video no está en ningún agente" "bash install.sh"; fi
if [ -n "$hf" ]; then g "HyperFrames en: ${hf#, }"
else b "No encuentro los skills de HyperFrames en ningún agente" "bash install.sh   (o: npx skills add heygen-com/hyperframes -g -y)"; fi

# Doctor de HyperFrames (Chrome headless, deps de render)
if [ "$ok" -eq 0 ]; then
  if npx -y hyperframes doctor >/tmp/edit-video-doctor.log 2>&1; then
    opt=$(sed 's/\x1b\[[0-9;]*m//g' /tmp/edit-video-doctor.log | awk '/✗/{sub(/^.*✗[ ]*/,""); print $1}' | paste -sd',' - | sed 's/,/, /g')
    if [ -n "$opt" ]; then g "hyperframes doctor: lo necesario, en verde (opcional sin instalar: $opt)"
    else g "hyperframes doctor en verde"; fi
    grep -q "Low memory" /tmp/edit-video-doctor.log && w "Poca memoria libre — los renders pueden fallar" "cerrar otras apps, o usar: npx hyperframes cloud render"
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
