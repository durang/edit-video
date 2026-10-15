#!/usr/bin/env bash
# edit-video · revisor final. Saca el video entero en hojas de contacto para revisarlo cuadro a cuadro.
# Uso: bash scripts/qa.sh final.mp4 [fps] [tiempos_a_tamaño_completo...]
#   fps por defecto 2 (un fotograma cada 0.5 s)
#   ej.: bash scripts/qa.sh final.mp4 2 1 3 9.5 18.8 46.4
# Deja en final.qa/ : sheet_01.jpg, sheet_02.jpg… (30 cuadros cada una, con su tiempo) y full_<t>.jpg
set -euo pipefail
V="${1:?Uso: qa.sh VIDEO [fps] [tiempos...]}"; FPS="${2:-2}"; shift $(( $# >= 2 ? 2 : 1 ))
OUT="${V%.*}.qa"; rm -rf "$OUT"; mkdir -p "$OUT/f"
W=$(ffprobe -v error -select_streams v:0 -show_entries stream=width -of default=nw=1:nk=1 "$V" | head -1)
H=$(ffprobe -v error -select_streams v:0 -show_entries stream=height -of default=nw=1:nk=1 "$V" | head -1)
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
# Volumen de entrega: redes = −14 LUFS integrados, pico −1 dBTP. Más bajo → "la voz se oye bajita".
LN=$(ffmpeg -hide_banner -i "$V" -af loudnorm=print_format=summary -vn -f null - 2>&1)
LUFS=$(printf '%s\n' "$LN" | awk '/Input Integrated/{print $3}')
TP=$(printf '%s\n' "$LN" | awk '/Input True Peak/{print $4}')
[ -n "$LUFS" ] && awk "BEGIN{exit !($LUFS < -15.5)}" && echo "⚠ VOLUMEN: $LUFS LUFS (meta −14). Master: highpass 70 · presencia +2.5 dB en 3 kHz · compresor 2.5:1 · loudnorm I=-14:TP=-1.5 (ver qa.md)"
[ -n "$LUFS" ] && awk "BEGIN{exit !($LUFS > -12.5)}" && echo "⚠ VOLUMEN ALTO: $LUFS LUFS (meta −14): las apps lo bajan y la voz pierde punch. Re-masteriza con loudnorm I=-14 (ver qa.md)"
[ -n "$TP" ] && awk "BEGIN{exit !($TP > -1.0)}" && echo "⚠ PICO: $TP dBTP (máx −1). El AAC sube el pico ~0.3–0.5 dB: masteriza con loudnorm …:TP=-1.5 (ver qa.md)"
[ -n "$LUFS" ] && echo "  volumen integrado: $LUFS LUFS · pico real: ${TP:-?} dBTP"
SR=$(ffprobe -v error -select_streams a:0 -show_entries stream=sample_rate -of default=nw=1:nk=1 "$V" 2>/dev/null)
[ -n "$SR" ] && [ "$SR" != "48000" ] && echo "⚠ AUDIO a $SR Hz (se entrega SIEMPRE a 48 kHz; a 96 kHz en celular puede no sonar). Re-masteriza con aresample=48000 -ar 48000 (ver qa.md)"
# Primer cuadro quieto (contrato del nivel 3 §1: el video abre ya en movimiento)
FZ=$(ffmpeg -hide_banner -t 3 -i "$V" -an -vf "freezedetect=n=-60dB:d=0.4" -f null - 2>&1 | awk '/freeze_start:/ && !f {sub(/.*freeze_start: /, ""); print; f = 1}')
[ -n "$FZ" ] && awk "BEGIN{exit !($FZ < 0.05)}" && echo "⚠ ARRANQUE QUIETO: el video abre con ≥ 0.4 s sin movimiento. En nivel 3 el primer cuadro ya se mueve (nivel-3.md §1)"
# Borde derecho negro: HyperFrames < 0.8.155 con FFmpeg 7.1/8.0 tiraba a negro las 8 columnas de la derecha
# cuando el ancho es múltiplo de 16 + 8 (1080). 8 px no llegan al 10 % de la alarma de NEGRO: se mide aparte,
# 1 cuadro/s, la franja de 8 px contra la de 16 px de al lado.
ffmpeg -hide_banner -v error -i "$V" -an -filter_complex \
  "[0:v]fps=1,split[a][b];[a]crop=8:ih:iw-8:0,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=$OUT/edge_a.txt[oa];[b]crop=16:ih:iw-24:0,signalstats,metadata=print:key=lavfi.signalstats.YAVG:file=$OUT/edge_b.txt[ob]" \
  -map "[oa]" -f null - -map "[ob]" -f null - 2>/dev/null || true
EDGE=$(paste <(grep -o 'YAVG=[0-9.]*' "$OUT/edge_a.txt" 2>/dev/null | cut -d= -f2) \
             <(grep -o 'YAVG=[0-9.]*' "$OUT/edge_b.txt" 2>/dev/null | cut -d= -f2) \
  | awk '$1 != "" && $2 != "" {n++; if ($1 < 20 && $2 - $1 > 15) k++} END{if (n > 0 && k * 2 >= n) printf "%d de %d s", k, n}')
[ -n "$EDGE" ] && echo "⚠ BORDE DERECHO NEGRO: las 8 columnas de la derecha salen negras ($EDGE). Bug de HyperFrames < 0.8.155 con FFmpeg 7.1/8.0 a 1080 de ancho: re-renderiza con HyperFrames ≥ 0.8.155 (revisa la versión fijada en el package.json del proyecto; ver troubleshooting.md)"
echo "✅ $N cuadros de $DUR s en $OUT/  — ahora MÍRALOS con la lista de references/qa.md"
