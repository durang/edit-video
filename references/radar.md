# Radar — bitácora

Una entrada por radar, la más nueva arriba. Formato:

```
## AAAA-MM-DD · radar (quincenal | trimestral)
- Nuevo: … → resuelve L# / quizá / nada
- Propuesta: qué archivo cambia, cómo se prueba
- Decisión de Sergio: pendiente | sí | no
```

## 2026-11-15 · radar quincenal

Issues y PRs abiertos en `durang/edit-video`: **ninguno** (tampoco cerrados). Desde el último radar no hubo commits
(3.14.2 sigue siendo lo último). Fuentes: HyperFrames 0.8.226 → **0.9.52** (≈ 60 versiones; la **0.9.0** del 2-nov
solo rompe el render distribuido en Lambda/Cloud Run); los proyectos locales siguen fijados en 0.8.105/0.8.106.
whisper.cpp 1.9.5 y openai-whisper sin cambios; GSAP **3.15.1** (4-nov, parche); skill de motion de LottieFiles y
MatAnyone 2 sin commits; FFmpeg de Homebrew 9.0.2_1, sigue sin libass (L3 resuelta aparte).

**Implementado (3.14.3, probado lo que se puede probar aquí):**
- **`troubleshooting.md` · HyperFrames 0.8.226 → 0.9.52** (de sus notas de versión, sin probar: requiere subir):
  audio **mezclado dos veces** si el nombre del archivo lleva espacio o acento (< 0.9.47, #7747 — nos toca de lleno
  en español), render en blanco donde un `set` corta un tween (< 0.9.20, #7318), acentos en otra fuente/peso
  (< 0.9.20, #7299), snapshot que falla en vez de salir negro (≥ 0.9.4), el render limita picos y avisa si baja la
  mezcla (≥ 0.8.228), menos disco en renders largos (≥ 0.9.17/0.9.40), `check` de safe zones 9:16 (≥ 0.9.44).
- **`qa.md` (Técnico)** · medios sin espacios ni acentos, con comando: probado en una carpeta de prueba (caza
  `voz final.wav` y `canción.mp3`, ignora `._*`) y en 5 proyectos reales de HyperFrames (0 falsos positivos).
  Más: avisos `outside_safe_zone` en 0 o justificados (≥ 0.9.44); `set` que corta un tween, cuadro a cuadro.
- `donde-renderizar.md`: disco justo con ≥ 0.9.17/0.9.40.

**Limitaciones:**
- **L5** · términos de Sonilo **leídos** (sonilo.com/licensing): la API es comercial (también para clientes finales),
  de prepago, sin plan y sin atribución; Pro cubre anuncios, clientes y YouTube monetizado; lo del plan gratis no es
  comercial; no garantizan cero reclamos de Content ID; no se puede distribuir la pista a Spotify/Apple Music.
- **L1** · VideoMaMa++ (20-oct, KAIST/Adobe): no comercial y solo NVIDIA → descartado. MatAnyone 2 sin cambios.
- **L2** · ningún issue de `clip-path`; 0.9.40 "los píxeles de un cuadro ya no dependen de los anteriores" y extrae
  cada video al tamaño en que se ve → re-probar el caso v5 al subir.
- **L8** · `check` ≥ 0.9.44 avisa del texto fuera de las safe zones de TikTok/Reels/Shorts (#7680).
- **L10** · ports MLX de SeedVR2 3B/7B y un 1.4B destilado (jul). **L4** · los términos de Mirelo siguen sin
  aparecer. **L7, L9**: nada nuevo (la ASD de los artículos de podcast usa la pista del micrófono activo, no la boca).

**Propuestas (decide Sergio):**
- **Subir HyperFrames a ≥ 0.9.52 y `npx hyperframes skills update`** (con permiso): ahora es un salto de menor
  (0.8 → 0.9) y el CLI ya no lo da solo. Trae #7747 (audio doble), #7318 (set/tween), #7680 (safe zone) y lo del
  radar anterior. Prueba: re-render de una pieza de nivel 3 vieja + `qa.sh`; `check` sobre un 9:16; y el caso L2.
- **L5 · Sonilo por API como fuente de música** cuando el director no pasa pista: `motion-design.md` §7 y
  `nivel-3.md` §1.8, con su licencia en `CREDITS.md`. Prueba: una cama de 30 s para una pieza de nivel 3 (≈ US$0.07)
  y subir un privado a YouTube para ver si hay reclamo. Requiere cuenta y gasto → tu decisión.
- **Safe zone 9:16 (propuesta pendiente, con dato nuevo):** Meta unificó Stories y Reels en mar-2026: arriba 14 %
  (≈ 269 px en 1080×1920), abajo 20–35 % (384–672 px), lados 6 % (≈ 65 px) (billo.app). → el rótulo superior del
  nivel 2 en **y ≥ 270** (antes se proponía 230); el 20 % inferior se queda como mínimo; con CTA de anuncio, 35 %.
- **clipper con material de otros:** Instagram (abr-2026, según socialpilot, terceros) baja el alcance a cuentas que
  en 30 días publican sobre todo contenido reciclado y a lo que lleva marca de agua de otra plataforma → una línea en
  `clipper.md`: clips de terceros solo con permiso, y nunca con la marca de agua de origen (ya está en `qa.md`).
- **Tarea programada del radar**: su texto sigue diciendo `~/clawd/projects/edit-video` (no existe; tercer radar
  que tiene que buscar el repo). Cambiarlo a `~/clawd/projects/Edit Video/edit-video`.
- **WIP sin subir en el repo de clientes**, el mismo que el 1-nov (`_general/tiempos.jsonl`, `APRENDIZAJES.md` de dos
  clientes y un `kit/ESTILO.md`): el radar lo apartó otra vez con `git stash` y lo devolvió al terminar. Subirlo
  quien lo escribió (`sync.sh push`), o decir si se descarta.
- Siguen pendientes las del 1-oct, 15-oct y 1-nov (clipper a −14 LUFS, catálogo HeyGen, Parakeet, `--engine whisper`
  fijo, OCR N/N, Mirelo, MatAnyone 2, SeedVR2).

**Niveles 2 y 3:** sin datos nuevos de peso. OpusClip 2026 (12.2 M clips): 80.2 % con subtítulos, 78.6 % animados vs
1.6 % estáticos → la línea del nivel 2 sigue. Instagram traduce solo subtítulos y audio de Reels (es/en/pt/hi): el
subtítulo quemado sigue siendo lo que se ve sin sonido; no cambia nada. Tendencias de motion "2027": artículos
genéricos, nada que cambie el contrato del nivel 3 (sigue el "autenticidad sobre pulido" del radar anterior).

- Decisión de Sergio: pendiente

## 2026-11-01 · radar quincenal

Issues y PRs abiertos en `durang/edit-video`: **ninguno**. Desde el último radar entraron 3.14.0 y 3.14.1 (dónde
renderizar + `destino.sh`, `PEDIDO.md`/`ESTADO.md`, documental narrado, QA por muestreo + `subcov.py`); el WIP del
13-oct ya está subido y la sección de Grok de `pintado-a-mano.md` ya no está duplicada. Fuentes: HyperFrames
0.8.162 → **0.8.226** (69 versiones; en la Mac el caché de `npx` ya no tiene ninguna: el próximo `ingest.sh` baja
la última). whisper.cpp sigue en 1.9.5, openai-whisper sin versión nueva, GSAP 3.15.0, skill de motion de
LottieFiles y MatAnyone 2 sin commits nuevos. FFmpeg local 9.0.2.

**Implementado (3.14.2, probado):**
- **`sync.sh` avisa si `EDIT_VIDEO_SRC` no es un repo** y usa el clon desde el que corre. El 31-oct el repo se movió
  otra vez (`~/clawd/projects/edit-video` → `~/clawd/projects/Edit Video/…`) y `sync.sh pull` del radar dijo
  "✓ al día" sin tocar el repo público (comprobado a mano con `git fetch`: estaba al día). 4 casos probados.
- Dato corregido en la Mac (no en el repo): `EDIT_VIDEO_SRC` → la ruta real del clon
  (`sync.sh config`, copia de la config anterior en `~/.config/edit-video/config.antes-radar-2026-11-01`).
- **`troubleshooting.md` + `qa.md` + `donde-renderizar.md`** · trampas de HyperFrames por versión (de sus notas de
  versión, sin probar aquí: requiere subir): tirón cada 8 cuadros con varios workers o por tramos cuando dos tweens
  escriben la misma propiedad (< 0.8.216, #6707 — toca a `EDIT_VIDEO_WORKERS=2` y al render por tramos), snapshot
  negro en silencio (< 0.8.197), grade en blanco en GPU (< 0.8.211), español devuelto en inglés con Parakeet
  (< 0.8.177), `render --start/--end` (≥ 0.8.222).

**Novedades que tocan limitaciones (sin adoptar):**
- **L8** · `hyperframes check` ≥ 0.8.220 marca como error cada palabra de subtítulo tapada por un recorte (antes
  6 de 7 salían como "info", #6770) y juzga el texto detrás de un video transparente por su alfa real (#5657).
- **L7** · `hyperframes audio --read` lee pausas, picos de efectos y voz contra música (#6546), y `beats` analiza un
  archivo directo (#6812). Nada nuevo en whisper.cpp.
- **L4** · Mirelo SFX 2.0 (14-oct, video → diseño sonoro, quita la música que metió el generador, conserva el
  diálogo) con API y MCP propios; un catálogo lo marca "comercial restringido" sin detalle. ElevenLabs y ACE Studio
  se anuncian como SFX libres de regalías (artículo de Sonilo, competidor). Licencias por leer.
- **L5** · Sonilo-MCP ya va en la 0.27 (PyPI); sus términos siguen por leer. **L1, L2, L9, L10**: nada nuevo
  (SeedVR2 MLX sigue igual; MatAnyone 2 sin commits; ningún issue de `clip-path` en HyperFrames).
- Seedance 2.5 en Higgsfield (desde ago): 30 s por toma con audio nativo (ambiente, foley) sincronizado → para
  insertos de nivel 4 trae su propio sonido; no resuelve L4 sobre metraje real.

**Propuestas (decide Sergio):**
- **Subir HyperFrames a ≥ 0.8.226 y `npx hyperframes skills update`** (con permiso): trae lo de arriba, sobre todo
  #6707 (render multi-worker correcto) y `check` de subtítulos tapados (L8). Prueba: render de una pieza de nivel 3
  vieja con 2 workers en la versión nueva + `qa.sh`; `check` sobre un proyecto con R2.
- **`ingest.sh` con `--engine whisper` fijo** (ya propuesto el 1-oct junto a Parakeet): hoy la transcripción usa la
  versión de HyperFrames que baje `npx` y el motor que esa versión elija. Prueba: una toma en español y comparar.
- **Tarea programada del radar**: su texto dice `~/clawd/projects/edit-video`, que ya no existe. Cambiarlo a
  `~/clawd/projects/Edit Video/edit-video` (o recrear el enlace). Esta corrida encontró el repo buscándolo.
- Safe zones (adaptlypost, act. 20-oct-2026): Reels arriba 210 / abajo 310 / derecha 84 px; TikTok 108 / 320 /
  120 px; zona segura común 900×1400 centrada → la regla del 20 % inferior (384 px) cubre; **refuerza la propuesta
  pendiente** de rótulo en y ≥ 230 y margen derecho ≥ 120 px.
- Siguen pendientes las propuestas del 1-oct y del 15-oct (clipper a −14 LUFS, catálogo HeyGen, Parakeet, safe zone,
  OCR N/N, Mirelo/Sonilo, MatAnyone 2, SeedVR2).
- **WIP sin subir en el repo de clientes** (`_general/tiempos.jsonl`, `APRENDIZAJES.md` de dos clientes y un
  `kit/ESTILO.md`): el radar lo apartó con `git stash` para no subirlo y lo devolvió al terminar.

**Niveles 2 y 3:** sin datos nuevos de peso. Lo más citado sigue siendo OpusClip (78.6 % de clips con subtítulo
animado vs 1.6 % estático) → línea del nivel 2 vigente. Tendencias de motion 2026 (autoae): "autenticidad sobre
pulido" — grano, analógico, recortes de papel/collage → encaja con la vida ambiente del contrato del nivel 3 y con
el "quizá" de papel rasgado del 15-oct; no cambia el contrato.

- Decisión de Sergio: pendiente

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
