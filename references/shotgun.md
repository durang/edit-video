# Shotgun de estilo — cambiar el diseño eligiendo, no adivinando

Método de `/design-shotgun` (gstack) adaptado a video. **Solo se usa en tres casos:**

1. El director pide **un cambio de diseño** ("cambio completo de diseño", "shotgun de estilo",
   "explora direcciones", "solo cambia la tipografía / el color / las animaciones").
2. **Cliente nuevo** (todavía no tiene línea de diseño).
3. **Propuesta de nivel 3** cuando el concepto visual no está claro.

**"Otro video como el de X" NO pasa por aquí**: se usa el kit del cliente tal cual.

## Pasos

1. **Contexto en una pregunta** (máx. 2 rondas): para quién, qué debe sentirse, qué NO quiere.
   Lee antes `CLIENTE.md`, `APRENDIZAJES.md` y el **gusto** del cliente (`shotgun.py gusto --cliente X`).
2. **Conceptos por escrito primero** — 3 por defecto (hasta 5), una línea cada uno:
   `A) "Nombre" — tipografía · color · cómo se mueve`. **Aprobación antes de renderizar.**
3. **Anti-parecido (obligatorio)**: cada dirección con **otra fuente de titular, otro acento y otra
   disposición** (palabra activa caja/color/subrayado, gancho izquierda/centro, mayúsculas). Si
   cambiar el texto de una a otra no se notaría, una sobra. `shotgun.py` lo comprueba y se niega.
   Si el pedido es parcial ("solo el color"), varía **solo esa dimensión**.
4. **Cuadros de estilo reales** sobre el metraje real — nunca imágenes generadas (escriben mal las
   letras y no muestran el video):
   - **Nivel 2**: `shotgun.py preparar` renderiza cada dirección y saca 2 cuadros (gancho + subtítulo).
   - **Nivel 3**: por dirección, una composición mínima de HyperFrames con el cuadro del metraje y
     `npx hyperframes snapshot --at` en 3 momentos (gancho, gráfico, cierre).
5. **Enséñalas en el chat** (Read de cada PNG) y **abre el tablero**: `shotgun.py tablero DIR`.
   Con gstack instalado usa su tablero (favorito, estrellas, notas, *Regenerate*, *Remix*); sin
   gstack, se elige en el chat. Remix = "la A con el color de la C" → nueva ronda con eso.
6. **Confirma lo entendido** en una línea y **guarda**: `shotgun.py elegir DIR --cliente X`.
   - La dirección elegida pasa a ser la plantilla del cliente (`clipper.json`); la anterior se guarda
     con fecha (`clipper.AAAA-MM-DD.json`).
   - **Gusto**: suma aprobado/rechazado por dimensión en `clients/X/gusto.json` (o el general en
     `~/.config/edit-video/gusto.json`). Olvida un 5 % por semana. Las siguientes propuestas parten
     de ahí; si el pedido contradice un gusto fuerte, se avisa en una línea.
7. En nivel 3, la dirección elegida alimenta la propuesta y el kit (`kit/plantilla.html`).

## Comandos

```bash
S=SKILL_DIR/clipper/shotgun.py
python3 $S preparar t.json clips.json direcciones.json --out shotgun-FECHA --cliente X --clip 1
python3 $S tablero  shotgun-FECHA
python3 $S elegir   shotgun-FECHA --cliente X            # lee feedback.json del tablero, o --elegida A
python3 $S gusto    --cliente X
```

`direcciones.json` — solo lo que cambia sobre el nivel 2:

```json
{"direcciones": [
  {"id": "A", "nombre": "Editorial papel", "plantilla": {}},
  {"id": "B", "nombre": "Grotesk expandido", "plantilla": {
     "fuentes": {"display": "Clipper Wide", "serif": "Clipper Soft Italic", "mono": "Clipper Mono B"},
     "colores": {"acento": "#FF5A36", "tinta": "#0E1A2B"},
     "subtitulo": {"activa": "color", "mayusculas": true},
     "gancho": {"alineacion": "centro"}}}
]}
```

## Tipografías incluidas (niveles 1–2)

| Familia | Qué es | Para |
|---|---|---|
| Clipper Display | Inter Tight 800 | titular editorial limpio |
| Clipper Wide | Archivo expandido 900 | titular potente, horizontal |
| Clipper Condensed | Oswald 700 | titular alto y estrecho |
| Clipper Soft Serif | Fraunces 700 (suave) | titular de revista |
| Clipper Serif | Instrument Serif Italic | acento editorial |
| Clipper Soft Italic | Fraunces Italic | acento cálido |
| Clipper Mono · Mono B | JetBrains Mono · IBM Plex Mono | rótulos |

Todas OFL, con métricas en `fonts/metrics.json` (la caja de la palabra activa se mide al píxel).
Para añadir una fuente: instancia estática, renombrarla "Clipper …", y sus métricas en `metrics.json`.
