# Radar — bitácora

Una entrada por radar, la más nueva arriba. Formato:

```
## AAAA-MM-DD · radar (quincenal | trimestral)
- Nuevo: … → resuelve L# / quizá / nada
- Propuesta: qué archivo cambia, cómo se prueba
- Decisión de Sergio: pendiente | sí | no
```

## 2026-10-01 · radar quincenal

Issues y PRs abiertos en `durang/edit-video`: **ninguno**. HyperFrames 0.8.92 → 0.8.105: nada sobre L2
(video negro con `clip-path`), matting ni tiempos de palabra; solo Studio/preview. GSAP y el skill de
motion de LottieFiles: sin cambios desde el radar inicial. whisper.cpp 1.9.4 (11-sep): nada nuevo para L7.

**Implementado (3.11.1, probado):**
- **clipper entregaba a 96 kHz** (niveles 1–2): `loudnorm` sin re-muestreo. `aresample=48000` + `-ar 48000`
  → probado con un clip real (nivel 2; nivel 1 con `--tighten` y `--no-normalize`): 48 kHz, audio = video.
- **`qa.sh`, 4 alarmas nuevas** (L8): audio ≠ 48 kHz (antes aceptaba 44.1), pico real > −1 dBTP, volumen
  alto (> −12.5 LUFS) y arranque quieto (`freezedetect`, contrato nivel 3 §1). Probado: piezas reales de
  nivel 3 sin falsos positivos; un video que abre quieto, un 44.1 kHz, un 96 kHz y un pico −0.7 dBTP, cazados.
- **Master a `TP=-1.5`**: una pieza de nivel 3 ya entregada mide −0.7 dBTP (el AAC sube el pico). Con
  `TP=-1.5` el mismo master sale a −14.1 LUFS / −1.5 dBTP (probado).
- **SFX sin conexión** (L4, avance): `/media-use` trae 19 SFX con licencia Pixabay (comercial) — riser,
  impactos graves, whoosh, glitch… → `motion-design.md` §7, antes de sintetizar con FFmpeg.
- Dato corregido: `clipper.md` y `clipper/README.md` seguían mandando al tap de Homebrew para libass; ahora
  el entorno conda + `EDIT_VIDEO_FFMPEG` (L3 resuelta).

**Propuestas (decide Sergio):**
- **clipper a −14 LUFS** (niveles 1–2) con `loudnorm` de dos pasadas: hoy apunta a −16 y en clips reales
  mide −17.6/−18 LUFS → `qa.sh` lo marca en cada clip. Archivo: `clipper.py` (render) + `GUIA.md` §1.
  Prueba: render de 3 clips y `qa.sh` sin aviso de volumen. → L-nueva / coherencia con `qa.md`.
- **Catálogo de HeyGen para SFX y música** (L4, L5): `media-use` ya lo usa con `heygen` CLI ≥ 0.3 + OAuth
  (sin créditos, según sus docs). Requiere instalar el CLI y **confirmar la licencia** (la doc del endpoint no
  la dice). Fuentes: `media-use/audio/references/sfx.md` y `bgm.md`; developers.heygen.com (search audio).
- **Parakeet-TDT en HyperFrames** (L7): `npx hyperframes models install parakeet` (~640 MB), español
  incluido, mejor WER que whisper.cpp. Probar si deja huecos reales entre palabras. Ojo: `ingest.sh` no fija
  `--engine`; al instalarlo cambiaría de motor solo → fijar `--engine` en el mismo cambio.
  Fuente: `media-use/references/operations.md`.
- **Safe zone arriba y a la derecha en píxeles** (nivel 2): el rótulo va en y≈178–200 y el logo arriba a la
  derecha a 48 px; Instagram tapa los 210 px de arriba y TikTok ~120 px a la derecha. Propuesta: rótulo en
  y ≥ 230, margen derecho ≥ 120 px, y la regla en `qa.md`. Cambia la línea del nivel 2. Fuente:
  postplanify.com (safe zones 2026).
- **Cobertura de subtítulos N/N automática** (L8) con el OCR de macOS (Vision, sin instalar nada) sobre un
  cuadro por palabra. Archivo nuevo `scripts/subtitulos_nn.swift` o `.py` + `qa.md`.
- **Quizá** (sin limitación inmediata o requiere instalar): MatAnyone 2 (CVPR 2026) para L1; LR-ASD
  (audio-visual) para L9; Higgsfield lista "Mirelo" (SFX) y "Sonilo" (música) pero "Game pipeline only".
- `npx hyperframes skills update` (los skills locales son del 29-sep): con permiso.

**Niveles 2 y 3:** 78.6 % de 13.5 M clips usan subtítulo animado y 1.6 % estático (OpusClip, ene–mar 2026):
confirma la línea del nivel 2. Tendencias de motion y tipografía cinética 2026 siguen en "minimalismo
dinámico" → el contrato del nivel 3 sigue vigente, sin cambios.

- Decisión de Sergio: pendiente

## 2026-09-29 · radar inicial (trimestral)

- **GSAP completo gratis** desde la 3.13 (SplitText, MorphSVG, DrawSVG, CustomEase, MotionPath,
  ScrambleText, Physics2D), también comercial → adoptado en `nivel-3.md`.
- **HyperFrames 0.8.92**: reglas y blueprints de animación con nombre, springs "horneados", desenfoque
  de movimiento, adaptador Three.js → adoptados en `nivel-3.md`.
- **Tiempos y curvas** de referencia (LottieFiles motion-design) → adoptados en `nivel-3.md`.
- **Retención en video corto 2026**: gancho ≤ 1.5 s, cambio visual cada 3–8 s, un solo mecanismo de
  énfasis, fin de la estética "gurú" → contrato del nivel 3.
- **Homebrew ffmpeg sin libass** → L3.
- Decisión de Sergio: aprobado (versión 3.0).
