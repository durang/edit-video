# Changelog

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
