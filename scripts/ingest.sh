#!/usr/bin/env bash
# edit-video · oídos y ojos.
# Uso: bash scripts/ingest.sh VIDEO [idioma] [modelo]
#   idioma: código ISO (es, en, pt, fr…) o auto. Por defecto: auto (detecta con 30 s de audio).
#           Si lo pasas y el audio dice otra cosa con claridad, se detiene: evita transcribir inglés
#           como español (error real: 50 min perdidos). Forzar: EDIT_VIDEO_FORCE_LANG=1
#   modelo: small | medium | large-v3. Por defecto: small
# Deja todo en VIDEO.edit/ : metadata.json · audio.wav · transcript.json · transcript.txt · frames/
set -euo pipefail

VIDEO="${1:?Uso: ingest.sh VIDEO [idioma] [modelo]}"
LANG_CODE="${2:-auto}"
MODEL="${3:-small}"
[ -f "$VIDEO" ] || { echo "No existe: $VIDEO" >&2; exit 1; }

BASE="${VIDEO%.*}"
OUT="${BASE}.edit"
mkdir -p "$OUT/frames"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

# ⓪ Idioma: detectar con 30 s de audio (desde el 10 % del video) y el modelo multilingüe ya descargado
detect_lang(){
  local m="$HOME/.cache/hyperframes/whisper/models/ggml-small.bin" d ss
  command -v whisper-cli >/dev/null 2>&1 && [ -f "$m" ] || return 1
  d=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$VIDEO")
  ss=$(awk "BEGIN{s=$d*0.1; if(s>60)s=60; print s}")
  ffmpeg -y -v error -ss "$ss" -t 30 -i "$VIDEO" -vn -ac 1 -ar 16000 "$OUT/_lang.wav" || return 1
  whisper-cli -m "$m" -f "$OUT/_lang.wav" -dl 2>&1 | sed -n 's/.*auto-detected language: \([a-z]*\) (p = \([0-9.]*\)).*/\1 \2/p' | head -1
  rm -f "$OUT/_lang.wav"
}
DET="$(detect_lang || true)"; DL="${DET%% *}"; DP="${DET##* }"
if [ "$LANG_CODE" = "auto" ]; then
  [ -n "$DL" ] || { echo "✗ No pude detectar el idioma. Pásalo: ingest.sh VIDEO es|en|pt…" >&2; exit 1; }
  LANG_CODE="$DL"; echo "⓪ Idioma detectado: $LANG_CODE (p=$DP)"
  awk "BEGIN{exit !($DP < 0.5)}" && echo "   ⚠ detección dudosa (p<0.5): ¿casi sin voz, o música? Si hay voz, repite con el idioma: ingest.sh VIDEO es|en…" >&2
elif [ -n "$DL" ] && [ "$DL" != "$LANG_CODE" ] && awk "BEGIN{exit !($DP >= 0.6)}" && [ -z "${EDIT_VIDEO_FORCE_LANG:-}" ]; then
  echo "✗ Pediste '$LANG_CODE' pero el audio suena a '$DL' (p=$DP). Repite con '$DL', o fuerza con EDIT_VIDEO_FORCE_LANG=1." >&2
  exit 3
fi

# Nunca un modelo .en si el idioma no es inglés: el default de HyperFrames es small.en.
if [ "$LANG_CODE" != "en" ] && [[ "$MODEL" == *.en ]]; then
  echo "⚠ $MODEL es solo inglés y el idioma es '$LANG_CODE'. Uso ${MODEL%.en}." >&2
  MODEL="${MODEL%.en}"
fi

echo "① Metadatos"
ffprobe -v error -print_format json -show_format -show_streams "$VIDEO" > "$OUT/metadata.json"
DUR=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$VIDEO")
FPS=$(ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate -of default=nw=1:nk=1 "$VIDEO" | head -1)
RES=$(ffprobe -v error -select_streams v:0 -show_entries stream=width,height -of csv=s=x:p=0 "$VIDEO" | head -1)
printf '   %.2f s · %s · %s fps\n' "$DUR" "$RES" "$FPS"

echo "② Audio (16 kHz mono para Whisper)"
ffmpeg -y -v error -i "$VIDEO" -vn -ac 1 -ar 16000 -c:a pcm_s16le "$OUT/audio.wav"

echo "③ Transcripción · idioma=$LANG_CODE · modelo=$MODEL"
npx -y hyperframes transcribe "$OUT/audio.wav" -d "$OUT" -l "$LANG_CODE" -m "$MODEL" --json > "$OUT/transcribe.log" 2>&1 || {
  echo "   ✗ Falló la transcripción. Ver $OUT/transcribe.log" >&2; exit 1; }
[ -f "$OUT/transcript.json" ] || { echo "   ✗ No se generó transcript.json. Ver $OUT/transcribe.log" >&2; exit 1; }

# Diccionario permanente: global → clipper → cliente → proyecto, antes de que nadie lo lea
python3 "$SKILL_DIR/scripts/diccionario.py" aplicar "$OUT/transcript.json" || echo "   ⚠ diccionario no aplicado" >&2

# transcript.txt legible: una línea por frase — corta en pausas > 0.35 s, en puntuación o cada 10 palabras
python3 - "$OUT/transcript.json" "$OUT/transcript.txt" <<'PY' || true
import json, sys
d = json.load(open(sys.argv[1]))
words = d["words"] if isinstance(d, dict) and "words" in d else d
lines, cur, start, prev_end = [], [], None, None
for w in words:
    t = (w.get("text") or w.get("word") or "").strip()
    s, e = float(w.get("start", 0)), float(w.get("end", 0))
    brk = cur and prev_end is not None and (s - prev_end > 0.35 or cur[-1][-1:] in ".?!,;:" or len(cur) >= 10)
    if brk:
        lines.append((start, prev_end, " ".join(cur))); cur, start = [], None
    if start is None: start = s
    cur.append(t); prev_end = e
if cur: lines.append((start, prev_end, " ".join(cur)))
with open(sys.argv[2], "w") as f:
    for s, e, txt in lines:
        f.write(f"{s:7.2f} → {e:7.2f}   {txt}\n")
print(f"   {len(words)} palabras · {len(lines)} frases")
PY

echo "④ Fotogramas"
if awk "BEGIN{exit !($DUR <= 10)}"; then RATE=2; else RATE=1; fi
ffmpeg -y -v error -i "$VIDEO" -vf "fps=$RATE,scale=960:-2" -q:v 3 "$OUT/frames/f_%04d.jpg"
N=$(ls "$OUT/frames" | wc -l | tr -d ' ')
echo "   $N frames a $RATE fps (frame n = segundo $( [ $RATE = 2 ] && echo '(n-1)/2' || echo 'n-1'))"

echo "✅ Listo en $OUT/"
echo "   Siguiente: revisar nombres propios (cada corrección nueva → diccionario.py agregar), leer TODOS los frames, y armar el beat sheet."
