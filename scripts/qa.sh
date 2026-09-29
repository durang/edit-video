#!/usr/bin/env bash
# edit-video · revisor final. Saca el video entero en hojas de contacto para revisarlo cuadro a cuadro.
# Uso: bash scripts/qa.sh final.mp4 [fps] [tiempos_a_tamaño_completo...]
#   fps por defecto 2 (un fotograma cada 0.5 s)
#   ej.: bash scripts/qa.sh final.mp4 2 1 3 9.5 18.8 46.4
# Deja en final.qa/ : sheet_01.jpg, sheet_02.jpg… (30 cuadros cada una, con su tiempo) y full_<t>.jpg
set -euo pipefail
V="${1:?Uso: qa.sh VIDEO [fps] [tiempos...]}"; FPS="${2:-2}"; shift $(( $# >= 2 ? 2 : 1 ))
OUT="${V%.*}.qa"; rm -rf "$OUT"; mkdir -p "$OUT/f"
W=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of csv=p=0 "$V" | head -1)
H=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of csv=p=0 "$V" | head -1)
DUR=$(ffprobe -v error -show_entries format=duration -of default=nw=1:nk=1 "$V")
# miniatura de 216 px de ancho, conservando proporción
TW=216; TH=$(( H * TW / W )); TH=$(( TH - TH % 2 ))
ffmpeg -v error -i "$V" -vf "fps=$FPS,scale=$TW:$TH" -q:v 3 "$OUT/f/%04d.jpg"
N=$(ls "$OUT/f" | wc -l | tr -d ' ')
PER=30; S=1; K=1
while [ $S -le $N ]; do
  ffmpeg -v error -y -start_number $S -i "$OUT/f/%04d.jpg" -frames:v 1 \
    -vf "tile=10x3:padding=4:color=0xFF0000" "$OUT/sheet_$(printf %02d $K).jpg" 2>/dev/null || true
  T0=$(awk "BEGIN{printf \"%.1f\", ($S-1)/$FPS}"); T1=$(awk "BEGIN{t=($S+$PER-2)/$FPS; if(t>$DUR) t=$DUR; printf \"%.1f\", t}")
  echo "sheet_$(printf %02d $K).jpg  →  $T0 s … $T1 s  (fila por fila, izquierda a derecha, cada $(awk "BEGIN{print 1/$FPS}") s)"
  S=$((S+PER)); K=$((K+1))
done
for t in "$@"; do
  ffmpeg -v error -y -ss "$t" -i "$V" -frames:v 1 -q:v 2 "$OUT/full_$t.jpg"
done
# Alarmas automáticas (no sustituyen mirar; avisan de lo que un ojo cansado se salta)
BF=$(ffmpeg -hide_banner -i "$V" -vf "fps=2,blackframe=amount=10:threshold=24" -f null - 2>&1 \
  | sed -n 's/.* t:\([0-9.]*\) .*/\1/p' | awk '{printf "%.1f ", $1}')
if [ -n "$BF" ]; then
  echo "⚠ NEGRO: ≥10 % del cuadro en negro puro en t = $BF"
  echo "   (video que no pinta, capa que tapa, recuadro vacío). Míralos a tamaño completo."
fi
TAIL=$(ffmpeg -hide_banner -sseof -0.8 -i "$V" -vn -af volumedetect -f null - 2>&1 | sed -n 's/.*max_volume: \([-0-9.]*\) dB.*/\1/p')
[ -n "$TAIL" ] && awk "BEGIN{exit !($TAIL < -60)}" && echo "⚠ SILENCIO: los últimos 0.8 s están en silencio digital ($TAIL dB). ¿Muere en seco?"
echo "✅ $N cuadros de $DUR s en $OUT/  — ahora MÍRALOS con la lista de references/qa.md"
