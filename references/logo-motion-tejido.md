# Receta — Logo motion "Tejido" (isotipo segmentado → lockup real)

Genérica y reutilizable para cualquier marca cuyo **isotipo esté compuesto por piezas**
(bandas, pétalos, cuñas, sectores de una apertura/hexágono/flor). Nivel 3 · desde cero.
Probada en una pieza real (16:9 + 9:16, nivel estudio). **Sin datos de ningún cliente aquí.**

## Concepto

El isotipo se **teje**: hilos de color cruzan el cuadro → las piezas reales del isotipo
entran desde varias direcciones y se entrelazan → *snap* con brillo en el golpe de audio →
**crossfade al logo real** → entra el wordmark → tagline → la marca se **desteje** → cierre
"powered by" con los logos de los partners en tarjetas. ~8 s, 30 fps.

## Pre-producción de assets (una vez)

1. **Recorta el isotipo y el wordmark** del PNG oficial a sus *bounding boxes* de alfa
   (`PIL.getbbox()`), por separado. Guarda `icon.png` y el wordmark.
2. **Wordmark en blanco** para fondo oscuro: recolorea a blanco conservando el alfa
   (merge de RGB blanco + alfa original). Nunca re-tipografíes a mano.
3. **Segmenta el isotipo en N piezas** por ángulo alrededor de su centro con
   `PIL.ImageDraw.pieslice` (máscara de sector, `min(alfa, sector)`), una por color/banda.
   Cada pieza se guarda **del tamaño del lienzo del icono** para que reensamblen al píxel.
   Verifica el reensamblado (`alpha_composite` de las N → debe dar el icono exacto).
4. **Logos de partners**: recórtalos a su bbox; van sobre **tarjetas blancas redondeadas con
   sombra** (consistencia premium aunque un logo no tenga versión clara).

## Geometría del lockup = EXACTA al original (crítico)

Mide en el PNG oficial, en px: `iconW,iconH`, `wordW,wordH`, `gap` (borde derecho del icono →
borde izquierdo del wordmark) y los centros verticales. Reglas que salieron de revisión:

- **El wordmark NO se encima al icono.** Reproduce el `gap` real (típico ~13–16 % del ancho
  del icono) — nunca lo acerques "a ojo".
- **Proporción wordmark/icono fija**: `wordH/iconH` del archivo (no inventes un tamaño).
- **Alineación vertical**: normalmente icono y wordmark comparten centro vertical.
- Escala todo por un único `s = hexAlto / iconH`; deriva `wordW, gap` de `s`. Coloca el lockup
  centrado y calcula los *offsets* `X_HEX`, `X_WORD` desde el centro del cuadro.
- **Vertical (9:16)**: usa el **mismo lockup horizontal** del original (icono izq, wordmark der),
  centrado, ~80–86 % del ancho útil. **No apiles** el wordmark bajo el icono.

## Choreografía (anclada al audio)

| Fase | Qué | Audio |
|---|---|---|
| Hilos | N líneas de color (los colores de la marca) barren en diagonal con luz; se recogen hacia el centro | swish |
| Tejido | las N piezas reales entran desde sus direcciones (orden de pares opuestos), overshoot + rotación + desenfoque; push-in 2.5D | *swell* |
| **Snap** | las piezas cierran; **destello** + barrido de luz enmascarado a la forma real; micro-shake | **golpe** (alinéalo al cuadro recortando el sting) |
| **Crossfade** | ~6 frames de las piezas tejidas → **imagen real del icono** (lockup pixel-idéntico) | — |
| Wordmark | el icono se mueve a su sitio del lockup; el wordmark real entra con *wipe* (`clip-path`), posición final = original | — |
| Tagline | debajo del wordmark (o centrado al lockup si no cabe), letra a letra, tracking moderado, **nbsp** entre palabras para que no colapsen en flex | — |
| Destejido | **el texto sale primero** (sin cruces texto/pieza); crossfade icono→piezas; las piezas vuelan y se desvanecen | whoosh |
| Cierre | "POWERED BY" + logos de partners en tarjetas blancas; subrayado de color; **hold ≥ 1 s** con micro-push | ticks |

## Detalles que valen oro (de feedback real)

- **Crossfade al logo real en el snap**: aunque las piezas reensamblen bien, cambiar a
  `icon.png` garantiza un lockup final idéntico al oficial y limpia cualquier costura.
- **Tagline**: espacios con `String.fromCharCode(160)` (nbsp) **y** `flex-shrink:0` en cada
  letra — en un flex los spans de espacio vacíos se encogen a 0 y las palabras se pegan.
  Tamaño legible (≥ 26 px en 1080 de alto; ≥ 34 px en vertical). Nunca cortado ni sobre el icono.
- **Destejido**: desvanece el tagline/wordmark **antes** de que las piezas pasen por encima.
- **Cierre**: "powered by" legible (≥ 28 px / ≥ 36 px vertical), tarjetas generosas, todo por
  encima del 20 % inferior, **hold ≥ 1 s**.
- **Audio**: el golpe del sting cae en el *snap* (recorta el inicio del sting para alinearlo);
  master a **−14 LUFS / TP = −1.5 / 48 kHz** (el AAC sube el pico ~0.3–0.5 dB).
- **Render en primer plano** dentro del turno (si se va a segundo plano y el turno cierra, se
  cancela — `render_cancelled_parent_exited`).

## Validación obligatoria

- Hojas de contacto cada **0.25 s** en el tramo del lockup y del destejido: **cero encimados**
  texto/logo en cualquier cuadro.
- **Overlay/diff del cuadro final del lockup contra el PNG original** escalado: mismo
  espaciado y proporciones (ver `qa.md`, regla de validación de lockup).
