# Changelog

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
