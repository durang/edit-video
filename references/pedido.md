# PEDIDO.md — pasar el trabajo a la máquina que renderiza

Para cuando **un agente orquesta** (investiga, escribe el guion, genera la voz y los clips, publica) y **otro
construye** en la máquina elegida en el Paso 1b (edita, renderiza, revisa). El orquestador gasta poco; el
trabajo pesado corre con la cuota y el hardware de la máquina que renderiza.

## Carpeta del proyecto

```
<carpeta_videos>/<proyecto>/
  PEDIDO.md       ← lo escribe el orquestador (qué hacer, entradas, criterios de aceptación)
  ESTADO.md       ← lo actualiza el constructor en cada fase
  guion.md · beatsheet.md (APROBADO) · fuentes.md
  vo/             voz (mp3/wav) + alineación por palabra (words.json)
  footage/ inserts/ music/
  out/            final · preview_720p (≤ 100 MB) · shorts/ · qa/ (RESUMEN.md, hojas)
  LOG/build.jsonl stream-json del constructor (para tiempos.py avance)
  .tmp/           TMPDIR; se borra al cerrar
```

Plantillas: `templates/PEDIDO.md.template` y `templates/ESTADO.md.template`.

## Estados (`estado:` en `ESTADO.md`)

`PEDIDO → EN_CURSO → QA → LISTO_REVISION → APROBADO → PUBLICADO → ARCHIVADO`, más `BLOQUEADO` (con motivo).
- El constructor solo mueve hasta `LISTO_REVISION` (o `BLOQUEADO`).
- `APROBADO` lo da el director; `PUBLICADO` y `ARCHIVADO` los marca el orquestador.
- `ARCHIVADO`: se borran `.tmp/` e intermedios; se quedan el máster, la preview y los insumos.

## Arranque del constructor (Claude Code)

```bash
cd "<carpeta_del_proyecto>" && mkdir -p LOG && \
eval "$(bash SKILL_DIR/scripts/destino.sh env "$PWD")" && \
claude -p "Lee PEDIDO.md y ejecútalo con /edit-video. Actualiza ESTADO.md en cada fase." \
  --output-format stream-json --verbose > LOG/build.jsonl
```

Lo lanza el usuario, o el orquestador con su permiso. Avance: `tiempos.py avance --log LOG/build.jsonl …`.

## Reglas

1. **El beat sheet llega aprobado.** El constructor no rehace la historia; si algo no cuadra, `BLOQUEADO` + pregunta.
2. **Criterios de aceptación explícitos** en el pedido: duración, formato, volumen, safe zone, lista de tiempos clave.
3. **QA en la máquina que renderiza** (modo muestreo si el pedido lo dice, `qa.md` §1b); el resumen va a
   `out/qa/RESUMEN.md`. El orquestador revisa ese resumen y unos pocos cuadros, no el video entero otra vez.
4. **El constructor no publica** ni sube a servicios externos: eso lo hace el orquestador con el OK del director.
5. Al cerrar: `tiempos.py registrar`, aprendizajes del cliente y `sync.sh push` (Paso 9).
