# Changelog

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
