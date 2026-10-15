# Radar — bitácora

Una entrada por radar, la más nueva arriba. Formato:

```
## AAAA-MM-DD · radar (quincenal | trimestral)
- Nuevo: … → resuelve L# / quizá / nada
- Propuesta: qué archivo cambia, cómo se prueba
- Decisión de Sergio: pendiente | sí | no
```

## 2026-10-15 · radar quincenal

Issues y PRs abiertos en `durang/edit-video`: **ninguno**. Fuentes: HyperFrames 0.8.105 → **0.8.162** (57
versiones; en la Mac el caché de `npx` llega a 0.8.146 y los skills locales son del 4-oct). whisper.cpp 1.9.5
(6-oct): mantenimiento, nada para L7. openai-whisper: sin versión nueva. GSAP: 3.15.0 (abr) sigue siendo la
última. Skill de motion de LottieFiles: sin commits. FFmpeg local 9.0.2.

**Implementado (3.13.2, probado):**
- **`qa.sh` · `⚠ BORDE DERECHO NEGRO`**: HyperFrames < 0.8.155 con FFmpeg 7.1/8.0 dejaba negras las 8 columnas de
  la derecha a 1080 de ancho (#5559); la alarma de NEGRO no lo ve (< 1 % del cuadro). Caza la franja en un video
  de prueba (5/5 s); cero falsos positivos en uno limpio, uno casi negro y dos piezas reales. Las 12 piezas
  entregadas revisadas (9:16 y 16:9) están limpias.
- **`troubleshooting.md` · versión de HyperFrames**: los proyectos fijan `hyperframes@<versión>` en su
  `package.json`; congelado de grabaciones de pantalla VFR con FFmpeg 8+ (arreglado en 0.8.156, #5572) y arreglo a
  mano (pasar a CFR, probado; detección con `ffprobe`).
- Dato corregido en la Mac (no en el repo): `~/.config/edit-video/config` apuntaba `EDIT_VIDEO_SRC` a
  `~/clawd/projects/edit-video`, que ya no existía (el repo se movió a `edit-video-skill/edit-video` el 1-oct) →
  `sync.sh pull/push` saltaban el repo público en silencio. Se creó el enlace `~/clawd/projects/edit-video →
  edit-video-skill/edit-video` (nada borrado).

**Novedades de HyperFrames que tocan limitaciones (sin adoptar: requieren subir de versión):**
- `hyperframes audio` (0.8.160): mide inicios, picos, **pausas** y volumen sin Chrome → posible sustituto de
  `silencedetect` en el rough cut (L7). `parakeet-mlx` detecta el idioma (0.8.139) → Parakeet nativo en Mac (L7).
- La transcripción conserva las palabras antes del inicio detectado de la voz (0.8.140) → toca la trampa de
  "tiempos falsos en arranques gritados" de `troubleshooting.md`.
- Capturas JPEG sin ruido de color en metraje graduado (0.8.151), el grade se conserva en el primer cuadro
  (0.8.157), desenfoque de movimiento correcto sobre video (0.8.140). Nada sobre L2 (`clip-path` + escala → negro).

**Propuestas (decide Sergio):**
- **Subir HyperFrames a ≥ 0.8.162 y `npx hyperframes skills update`** (con permiso): trae todo lo de arriba.
  Prueba: render de una pieza de nivel 3 vieja con la versión nueva + `qa.sh`; luego probar `hyperframes audio`
  contra `silencedetect` en una toma con pausas (L7).
- **L4 · Mirelo SFX por Replicate** (el MCP de Replicate ya está conectado): video mudo → SFX sincronizados, 2–4
  variantes, máx. 10 s, US$0.01/s por variante. **La página no dice la licencia** → confirmarla antes. Archivo:
  `motion-design.md` §7 como 3.ª fuente. Fuente: replicate.com/mirelo/video-to-sfx-v1.5.
- **L5 · Sonilo** (API, CLI y MCP): texto→música US$0.135/min, video→música US$0.54/min; según Sonilo, licencia
  no exclusiva, sin regalías ni atribución para generaciones pagadas (no menciona Instagram ni Content ID). Es su
  propio blog: leer los términos antes. Fuente: sonilo.com/blog (pay-as-you-go… commercial use rights).
- **L1 · MatAnyone 2** (CVPR 2026 Highlight) ya tiene código público (`pq-yang/MatAnyone2`): probarlo contra el
  recorte de video de Higgsfield en una toma con pelo. Requiere instalar (PyTorch).
- **L10 · SeedVR2** (escalador por difusión de un paso; hay port a MLX para Apple Silicon): probar en un clip de
  416×752. Requiere instalar. Fuente: upsampler.com (SeedVR vs FlashVSR 2026).
- Siguen pendientes de decisión las 5 propuestas del radar del 1-oct (clipper a −14 LUFS, catálogo HeyGen,
  Parakeet, safe zone superior/derecha, OCR N/N).
- **WIP sin subir del 13-oct** en este repo (reglas duras 14–15 en `SKILL.md` y una sección de Grok en
  `pintado-a-mano.md`, **duplicada**) y en el de clientes: el radar la apartó con `git stash` para no subirla con
  su commit y la devolvió al terminar. Revisarla y subirla quien la escribió (`sync.sh push`).

**Niveles 2 y 3:** los subtítulos animados de 2–3 palabras siguen siendo lo que más rinde (OpusClip, 13.5 M
clips, T1 2026; dato de proveedor) → clipper ya usa 3 por defecto: la línea del nivel 2 sigue vigente. Safe zone
de Reels (trymypost, mar-2026): arriba 150 px, abajo 280, derecha 90–100 → la regla del 20 % inferior (384 px)
cubre de sobra; refuerza la propuesta de margen derecho ≥ 120 px. Tendencias de motion 2026 (Videobolt): trazo
a mano, texturas analógicas, papel rasgado, maquetas editoriales modulares, 2D + 3D híbrido, vidrio/dispersión —
"lo artesanal destaca entre tanta IA". Encaja con el contrato del nivel 3 (vida ambiente con grano/papel) y con
`pintado-a-mano.md`; no cambia el contrato. **Quizá** (para "Por probar" si al director le gusta): transición de
papel rasgado a cuadros reducidos (12 fps) entre bloques gráficos, intensidad 2.

- Decisión de Sergio: pendiente

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
