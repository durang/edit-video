# Changelog

## 3.13.0 — 2026-10-06
- **Nueva receta de nivel 4: `references/pintado-a-mano.md`** — película con personaje pintado (gouache + crayón)
  que actúa cuadro a cuadro: guion y voz primero (cortes por la envolvente, sin `...` en el TTS), hoja de modelo,
  una base por plano, animar editando la pintura un cambio a la vez, fijar dibujos, hoja de exposición con fundido
  de 1 cuadro y boil a 12 fps, intercalados por flujo óptico, pase en blanco para mover al personaje, gráficos y
  sonido en código en las mismas señales. Prompts exactos (hoja de modelo, base, edición, cambio de luz, pase en
  blanco), costos (2 créditos por imagen), 9 trampas reales y el revisor propio. Enlazada desde `SKILL.md`,
  `nivel-4.md`, `niveles.md` y `GUIA.md` (§4.1).
- **Herramientas nuevas en `scripts/pintado/`**, con autopruebas:
  - `composite_frames.py` — alinea cada dibujo con la base usando solo el fondo (ORB + RANSAC, afinado ECC; sin
    OpenCV, correlación de fase), iguala color en lo que no cambió, máscara de cambio (diferencia suavizada antes
    del umbral, sin islas), pega solo el cambio. `--chain` para cadenas largas de ediciones (el encuadre deriva),
    `--roi` / `rois.json` para pegar solo la zona pedida, modo `"light"` para encender una luz sin mover nada,
    máscara de píxeles válidos para no pegar el borde inventado por la alineación.
  - `flow_inbetween.py` — intercalados Farneback entre pares de dibujos, con corte a la mitad donde el flujo no
    sigue la forma (sin fantasmas); `map.json` con dónde quedó cada original.
  - `exposure_sheet.js` — `sheetDraw(id, [[t, dibujo], …], t)` para HyperFrames: fundido de 1 cuadro por cambio
    (o propio: `[t, dibujo, cuadros]`), boil determinista a 12 fps (`boilT` lo congela), `loop()` para bucles.

## 3.12.2 — 2026-10-03
- **Recetario, por probar:** "placa única pre-renderizada" (todo el metraje en un `footage.mp4` 1:1 con
  colas bajo los barridos; un solo `<video>`, render ligero en máquinas de 8 GB) y la variante de R2
  "congelado asentado después de la palabra".
- **`troubleshooting.md`:** tiempos falsos de Whisper en arranques gritados/susurrados (verificar con la
  envolvente de 50 ms), clips raíz de HyperFrames anclados a 0,0 (usar `margin`), error silencioso que
  deja sin registrar la línea de tiempo tras pasar escenas a sub-composiciones, subtítulo que se aparta
  del elemento protagonista del plano.

## 3.12.1 — 2026-10-02
- **`qa.sh`: arreglo con ffprobe 9** — `csv=p=0` devolvía `1920,` (coma final) y rompía el cálculo de
  miniaturas (`syntax error: operand expected`). Ahora `default=nw=1:nk=1` para ancho, alto y sample rate.
- **clipper: `gancho.y` en la plantilla** — posición vertical del gancho (default 300 en 9:16 / 170 en
  16:9). Para cuando la persona está sentada alta y el gancho le pisa la cabeza: bajarlo al pecho (~1000).
- Nota de encuadre: en planos fijos a dos, `--fit auto` puede quedarse en un hablante; Whisper estira la
  última palabra hasta la siguiente, así que el corte de hablante va ~0.5 s antes de su `end`.

## 3.12.0 — 2026-10-01
- **Nueva receta `references/logo-motion-tejido.md`** — logo motion desde cero para marcas cuyo
  isotipo se compone de piezas: hilos → piezas reales del isotipo segmentado (pieslice por ángulo)
  → snap con brillo en el golpe → **crossfade al logo real** → wordmark → tagline → destejido →
  cierre "powered by" con logos de partners en tarjetas. Nace de una pieza real (16:9 + 9:16).
- **`qa.md`: regla nueva (bloqueante) — validación de lockup contra el original.** El lockup final de
  cualquier logo motion se valida con overlay/diff contra el PNG oficial: mismo espaciado, mismas
  proporciones, cero encimados (el wordmark nunca toca el isotipo). Hojas cada 0.25 s en lockup y
  destejido. Salió de feedback real: el wordmark se encimaba al isotipo y el tagline cruzaba las piezas.
- **Detalles de lockup y tagline** en la receta: reproducir el `gap` y la proporción wordmark/icono
  EXACTOS del archivo (no "a ojo"); en vertical, lockup horizontal (no apilar); tagline con nbsp +
  `flex-shrink:0` (si no, los espacios colapsan en flex); el texto se desvanece ANTES de que las piezas
  pasen por encima (salida con `overwrite:"auto"` para que no queden letras rezagadas).

## 3.11.1 — 2026-10-01 (radar quincenal)
- **clipper (niveles 1–2) ya entrega el audio a 48 kHz.** `loudnorm` sin re-muestreo dejaba el AAC a 96 kHz
  (en algunos celulares no suena). `aresample=48000` + `-ar 48000`; probado con un clip real.
- **`qa.sh`: 4 alarmas nuevas** — audio ≠ 48 kHz (también 44.1), pico real > −1 dBTP, volumen alto
  (> −12.5 LUFS) y arranque quieto (contrato del nivel 3 §1). Probado sin falsos positivos en piezas reales.
- **Master a `TP=-1.5`** (`qa.md`): el AAC sube el pico 0.3–0.5 dB; con `TP=-1` una pieza salió a −0.7 dBTP.
- `motion-design.md` §7: primero la biblioteca de 19 SFX de `/media-use` (offline, licencia Pixabay
  comercial), después síntesis con FFmpeg. L4 con avance.
- `clipper.md` y `clipper/README.md`: libass en macOS con el entorno conda + `EDIT_VIDEO_FFMPEG` (L3).
- `LIMITACIONES.md` y `radar.md`: entrada del radar con propuestas (−14 LUFS en clipper, catálogo de HeyGen,
  Parakeet, safe zone superior/derecha en píxeles, OCR para la cobertura N/N).

## 3.11.0 — 2026-09-30
- **La guía siempre visible y al día.** `scripts/guia.py` saca de `GUIA.md` la "Guía rápida" arriba
  del README (mapa quiero → uso → tiempo + link), la descripción del repo en GitHub (versión, qué hace y
  link a la guía) y el resumen para el chat cuando se pide "la guía". `sync.sh push` lo regenera en cada
  actualización; `guia.py check` avisa si el README quedó viejo. `SKILL.md`: todo cambio que toque lo que
  el usuario pide o recibe actualiza `GUIA.md` en el mismo commit.

## 3.10.0 — 2026-09-30
- **`GUIA.md`**: guía de uso de toda la máquina. Cada nivel y herramienta empieza con una descripción,
  sigue con cómo pedirlo (frases de ejemplo) y termina con qué se recibe, cuánto tarda y el comando.
  Mapa rápido "quiero… → uso…", intensidades del nivel 3, tabla de notas de corrección, problemas comunes.
- **Modo desde cero** (sin metraje: audio, guion, idea o web) documentado y enrutado en `SKILL.md`
  Paso 0: beat sheet → OK → cuadros → HyperFrames → `.mp4` + `.html`. Con audio, cada animación se
  ancla a la palabra. Cómo escribir un guion que anima bien. Primera pieza de estilo editorial: pendiente.

## 3.9.0 — 2026-09-30
**clipper: elegir, empaquetar y encuadrar solo** — las 4 mejoras aprobadas, probadas con video real.
- **Rúbrica de clipeabilidad** (`clipper/rubrica.py`, `references/clipeabilidad.md`): `candidatos`
  (y al final de `analyze`) puntúa tramos 0–10 en gancho, dato, remate, autonomía y emoción, sin
  solaparse, en ES y EN → `*.candidatos.json` con motivo. Pre-filtro: el humano decide.
- **Miniatura por clip**: `NN-slug-thumb.jpg` con titular en la tipografía de la plantilla (nivel 1
  y 2, `"serif|DISPLAY"`), degradado en 12 bandas (con 2 se veían bordes duros), cuadro por
  `thumbnail` de FFmpeg o por la cara más expresiva. `--no-thumbs`, `thumb_t`.
- **Modo lote**: `lote <carpeta>` (transcribe con caché, propone, `LOTE.md`) → OK → `lote --render`.
  Videos con < 40 palabras salen como "poca voz".
- **Recorte por cara / hablante activo**: `--fit auto` con `clipper/caras.py` (MediaPipe 0.10.21 en
  venv aislado; clipper sigue en librería estándar). Detector de rango completo + `jawOpen` por cara,
  histéresis de 0.8 s, 1 s mínimo entre cortes, encuadre de grupo, cámara suave con corte seco entre
  hablantes vía `sendcmd`. Resuelve L6.
- Aprendizajes: mediapipe 1.0.x revienta en macOS ("graph_service: Service is unavailable"); el seek
  por milisegundos de OpenCV no funciona en .mp4 de iPhone (usar cuadros); una pista vieja en la
  misma x robaba el "más cercano" y abría pistas nuevas a cada muestra; un margen absoluto de
  actividad de boca retrasaba 7 s el cambio de hablante en planos abiertos (ahora relativo).
- `ingest.sh`: avisa si la detección de idioma es dudosa (p < 0.5): era música, no voz.
- Nota: las versiones 3.4.0–3.8.1 están descritas en sus mensajes de commit.

## 3.3.1 — 2026-09-30
- `niveles.md`: Clipper Studio como la puerta sin terminal a los niveles 1–2 (y al corte del 3), y
  cómo mantener al día un Studio que corre como servicio.

## 3.3.0 — 2026-09-29
**Shotgun de estilo: cambiar el diseño eligiendo, no adivinando** (método de /design-shotgun de
gstack, adaptado a video).
- `clipper/shotgun.py`: `preparar` (renderiza N direcciones sobre el metraje real y saca cuadros de
  estilo; se niega si dos direcciones se parecen), `tablero` (el de gstack si está; si no, el chat),
  `elegir` (la elegida pasa a ser la plantilla del cliente, la anterior se guarda con fecha) y `gusto`
  (aprobado/rechazado por dimensión, con olvido del 5 % por semana).
- Nivel 2 más flexible: `fuentes`, palabra activa `caja | color | subrayado`, `mayusculas`, gancho
  `izquierda | centro`.
- 5 fuentes nuevas incluidas (OFL, con métricas): Clipper Wide (Archivo expandido), Condensed
  (Oswald), Soft Serif e Soft Italic (Fraunces), Mono B (IBM Plex Mono).
- `references/shotgun.md`; `SKILL.md` y `niveles.md`: "otro igual" usa el kit; "cambio de diseño"
  usa el shotgun.

## 3.2.0 — 2026-09-29
**Quien descarga el skill también se mantiene al día.**
- `check.sh`: compara la versión instalada con la de GitHub en cada sesión y avisa con el comando
  para actualizar (el agente pide permiso).
- `CONTRIBUTING.md`: cómo proponer mejoras (issue / PR), nunca con datos de clientes.
- `mejora-continua.md`: el radar del dueño revisa también issues y PRs (nunca fusiona solo); quien
  descarga recibe mejoras por actualización y propone por issue/PR; radar propio en modo informe.

## 3.1.0 — 2026-09-29
**Mejora continua con ritmo, no a ciegas.**
- `references/mejora-continua.md`: retro de 3 preguntas en cada entrega (sin internet), búsqueda
  dirigida solo con razón, y **radar cada 2 semanas** (días 1 y 15) con revisión profunda de los
  niveles 2 y 3. Lo obvio lo implementa (probado y versionado); lo demás lo propone a Sergio.
- `LIMITACIONES.md`: 8 limitaciones abiertas con su arreglo provisional y qué las resolvería. El radar
  busca primero soluciones a estas, no novedades por novedad.
- `references/radar.md`: bitácora; primera entrada con lo investigado para la 3.0.

## 3.0.1 — 2026-09-29
- Aprendizaje: un `": "` sin comillas en la `description` de `SKILL.md` rompe el YAML y `npx skills`
  deja de ver el skill ("No valid skills found"). `sync.sh push` ya no sube si pasa.

## 3.0.0 — 2026-09-29
**Una sola máquina de edición, en niveles.**
- **clipper entra al repo** (`clipper/`, con su historial completo): motor de los niveles 1–2 y del
  corte limpio del 3. `durang/clipper` queda como puntero.
- **Niveles** en `SKILL.md`, `README.md` y `references/niveles.md`: 1 Recorte, 2 Editorial,
  3 Estudio, 4 Director (propuesto). Cada uno con su motor, su línea de diseño y su aprobación.
- `references/nivel-3.md`: **contrato del nivel 3** (12 puntos que el revisor comprueba), tiempos y
  curvas, técnicas con los nombres reales de HyperFrames, GSAP completo gratis, lo que ya no se hace
  en 2026, y la propuesta. Con fuentes.
- `references/nivel-4.md`: propuesta del nivel Director (insertos generados, 2.5D/3D, música,
  versiones del gancho, másters por formato; tres puertas de aprobación).
- `check.sh`: libass (niveles 1–2) y el motor clipper.

## 2.6.0 — 2026-09-29
**clipper en tres niveles, y el nivel 3 pasa por aquí con aprobación.**
- `references/clipper.md`: niveles 1 Clásico, 2 Editorial (la tipografía y la paleta de este skill,
  hechas con FFmpeg/libass) y 3 Estudio (corte limpio + propuesta → OK del director → construir aquí).
  Plantilla de clipper por cliente en el área privada. Aviso de libass en macOS.

## 2.5.2 — 2026-09-29
- `scripts/qa.sh`: alarmas automáticas — cuadros con ≥10 % en negro (luma < 24; el negro de video es 16, no 0) (video que no pinta, capa
  que tapa) y final en silencio digital.
- `references/qa.md`: seis errores reales más de la ronda 5 (video negro que el constructor dio por
  bueno, recorte hecho sobre un cuadro recortado, artefacto de máscara, créditos sobre la persona,
  tarjeta vacía antes del contenido, final en silencio).

## 2.5.1 — 2026-09-29
- `references/clipper.md`: lo que clipper ya hace (recorte 9:16, palabra activa, zona segura,
  tapar subtítulos quemados, silencios, idioma, diccionario por cliente) y cómo pedírselo; el corte
  "solo cortar" para nivel estudio es `--no-captions`.
- Aprendizaje: whisper.cpp pega los tiempos de palabras contiguas; para quitar silencios sobre una
  transcripción de HyperFrames hay que usar `silencedetect` (energía), no los huecos entre palabras.

## 2.5.0 — 2026-09-29
**Lo mejor de clipper, sin duplicarlo.**
- `scripts/diccionario.py`: diccionario permanente de correcciones en capas (global → clipper →
  cliente → proyecto). Palabra completa, sin mayúsculas, y **correcciones de varias palabras a nivel de
  palabra** ("near Turing" → "nearshoring" funde los tokens y conserva los tiempos). `ingest.sh` lo
  aplica solo; cada corrección nueva se guarda con `agregar`.
- `ingest.sh`: el idioma **se detecta** (30 s, modelo multilingüe ya descargado) si no se pasa, y
  **se verifica** si se pasa: si el audio dice otra cosa, se detiene con código 3.
- `references/clipper.md` y Paso 0: video largo → muchos clips va a clipper; aquí solo los que
  merecen nivel estudio. Una pregunta al empezar: rápido, estudio o los dos.

## 2.4.0 — 2026-09-29
**Dos repos y autoaprendizaje.**
- Área de clientes en un repo **privado** aparte (`edit-video-clients`): por cliente `CLIENTE.md`
  (reglas), `APRENDIZAJES.md`, `HISTORIAL.md` y `kit/` (plantilla, tokens, generadores, sonidos,
  fondos). El segundo video de un cliente parte de su kit.
- `scripts/sync.sh`: `init`, `status`, `pull` (al empezar), `new-client`, `push` (al entregar).
  Guardia: si una `palabra_privada` de un cliente va a subir al repo público, no sube.
- `SKILL.md`: Paso 2 lee el cliente antes del beat sheet; **Paso 9 · Aprender** obligatorio: lo general
  a este repo, lo del cliente al privado. Regla dura 13.
- `references/aprendizaje.md`: el ciclo completo. `install.sh --clients <url>`, `check.sh` y la
  plantilla de `AGENTS.md` conocen el área de clientes.

## 2.3.0 — 2026-09-29
**Motion design nivel estudio.** Lo aprendido llevando un reel real de entrevista (16:9 → 9:16) de v1 a v5.
- `references/motion-design.md`: sistema de coherencia (IN/OUT/MOVE, staggers, una sola `.pill`,
  margen único), mapas con datos reales (Natural Earth, precalculado, `pathLength="1"`, etiquetas sin
  solape, arcos con punto viajero), hacer sitio paneando, palabras detrás de la persona con mate y su
  fallback, fondos generados, cierre con personaje recortado + parallax, diseño sonoro con niveles, y
  reparto director/constructor.
- `references/routing.md`: pedidos "que se vea de estudio" → motion-design; SFX sintetizados con
  FFmpeg cuando no hay catálogo. Higgsfield `generate_audio` es solo voz.

## 2.2.0 — 2026-09-29
**Revisor final obligatorio.**
- `scripts/qa.sh`: el MP4 renderizado entero en hojas de contacto (un cuadro cada 0.5 s) más
  cuadros a tamaño completo en los tiempos clave.
- `references/qa.md`: la checklist que decide si se entrega — palabras partidas o cortadas, glifos
  sueltos, cara tapada, safe zone, legibilidad en teléfono, subtítulos o logos del original
  asomando, zonas muertas, coherencia de movimiento, sincronía. Con los errores reales que ya cazó.
- `SKILL.md` Paso 8: el que construye no aprueba; si hay subagentes, revisa otro agente.

## 2.1.0 — 2026-09-29
**El skill se instala lo que le falta.**
- `scripts/setup.sh`: detecta qué falta (FFmpeg, Node, whisper-cpp, skills de HyperFrames en cada
  agente, modelo de Whisper multilingüe), imprime el plan, pide permiso y lo instala. macOS y Linux.
  Sin `--yes` nunca instala: pensado para que un agente le enseñe el plan al usuario.
- `SKILL.md` Paso 1: el agente comprueba, y si falta algo corre `setup.sh` con permiso.
- `install.sh` delega en `setup.sh`: una sola lógica para personas y agentes.
- README: instrucción lista para pegarle a cualquier agente, y cuándo tiene que estar prendido el ordenador.

## 2.0.1 — 2026-09-29
Probado de verdad: instalado desde GitHub en Claude Code, OpenClaw y Hermes, y transcripción real en español.
- `install.sh`: `npx skills` quiere un `-a` por agente, no una lista con comas.
- `scripts/check.sh`: comprueba agente por agente dónde está `edit-video` y dónde HyperFrames
  (incluido el plugin de Claude Code); comprueba `whisper-cli`; separa lo opcional del doctor;
  avisa de poca memoria y ofrece el render en la nube.
- `scripts/ingest.sh`: `transcript.txt` corta en puntuación y cada 10 palabras; resolución y fps en una línea.
- `whisper-cpp` vuelve a la lista de macOS: HyperFrames transcribe con `whisper-cli`.
- README: la prueba real de por qué hay que pasar el idioma.

## 2.0.0 — 2026-09-29
**Portable a cualquier agente.**
- Renombrado a `edit-video` (repo y skill). Se invoca con `/edit-video`.
- Funciona en Claude Code, OpenClaw, Hermes Agent, Codex, Cursor, Gemini CLI y más: lenguaje neutro,
  sin dependencias de un solo agente.
- `install.sh`: detecta los agentes instalados y pone el skill y los skills de HyperFrames en todos.
- `scripts/check.sh`: preflight portable con el comando exacto de cada cosa que falte.
- `scripts/ingest.sh`: metadatos, audio, transcripción con idioma, `transcript.txt` legible y frames,
  en un comando.
- Onboarding: seis preguntas la primera vez; las reglas se guardan en `AGENTS.md` (y `CLAUDE.md` →
  `@AGENTS.md`), el mismo archivo para todos los agentes.
- Corregido: el modelo por defecto de HyperFrames es `small.en` (solo inglés); ahora siempre se pasa
  `-l <idioma>`.
- Capa sobre HyperFrames en vez de reimplementarlo: enruta a `embedded-captions`,
  `talking-head-recut`, `general-video`, `motion-graphics`, `hyperframes-audio`, `media-use`.
- `references/pipeline.md`: generar con IA → montar. El texto nunca se genera, se monta.
- Render en la nube de HeyGen documentado (`hyperframes cloud render`).

## 1.0.0 — 2026-09-29
Primera versión, a partir del PDF de @pauloshimas.
