# Defecto → arreglo

Describe qué ves y cuándo, o pega el error.

| Síntoma | Arreglo |
|---|---|
| **Nombres mal escritos** | Dar los nombres y marcas en el primer prompt. Corrige la transcripción **y** los subtítulos |
| **El texto queda tapado por los botones de la app** | Declarar la safe zone: nada en el 20% inferior ni pegado al borde derecho |
| **El efecto llega tarde** | Nombrar **la palabra** en la que debe empezar. El agente tiene el tiempo exacto de cada una |
| **Dice que está hecho pero se ve mal** | `snapshot el frame en 0:07 y revísalo tú mismo`. Entonces ve lo que ves tú |
| **El preview o el render fallan** | `npx hyperframes doctor`, y pegarle el error |
| **Un cambio rompió algo** | Guardar versión antes de cada ronda (v1, v2...) y volver atrás |
| **Los subtítulos van demasiado rápido** | `De 0:12 a 0:14 los subtítulos van muy rápido. Muestra dos palabras a la vez` |
| **El recorte tiene bordes blandos** | Movimiento demasiado rápido o poca separación de la pared. Se vuelve a grabar, no se arregla en montaje |
| **Video negro dentro de un recuadro** (el render sale negro pero el preview se ve bien) | Pre-render 1:1: FFmpeg saca `box.mp4` con lo que se ve en el recuadro, a su tamaño exacto; `<video>` sin transform ni clip-path. Grade con FFmpeg, no con CSS. Worker, GPU, caché o render por tramos **no** lo arreglan (probado) |
| **Rectángulo o astilla al final de un `clip-path` que se cierra a un punto** | Desvanecer la capa (opacity → 0) **durante** el cierre, empezando casi a la vez; nunca dejar que el inset llegue a 0 × 0 visible |
| **El clean plate no existe** | Los efectos de capas no se pueden hacer. Se graban 2 s de sala vacía y se repite |

## Hábitos que evitan casi todo

- **Un cambio por mensaje.**
- **Siempre con el tiempo:** "en 0:07".
- **Decir qué se quiere ver, no cómo programarlo.**
- **Aprobar el plan antes de construir.**

## Atajos

- Rough cut primero, efectos después.
- Previsualizar secciones cortas antes de un render completo.
- Las reglas de estilo (tipografías, colores, safe zone) en un `CLAUDE.md` en la carpeta.
  El agente lo lee cada vez.
- Cuando un efecto funcione, pedir que lo guarde como plantilla.

## Racionalizaciones que hay que rechazar

| Pensamiento | Realidad |
|---|---|
| "Lo construyo y ya lo enseño luego" | El beat sheet es más barato que un render. Siempre |
| "Está hecho, seguro que se ve bien" | Si no has mirado el frame, no lo sabes. Snapshot y mirar |
| "Le meto un efecto más y queda mejor" | Más de un zoom cada cinco segundos cansa. Lo raro es lo que impacta |
| "Grabo y ya veré si hace falta el clean plate" | Sin él, la mitad de los efectos buenos quedan fuera |

## Aprendido en piezas reales (2026-10-03)

| Defecto | Arreglo |
|---|---|
| Whisper pone tiempos falsos al inicio gritado o susurrado (dice que una palabra empieza en 0.0 s y el audio está mudo hasta 1.2 s) | Antes de cortar o subtitular, mirar la envolvente de 50 ms: `ffmpeg -ss A -t D -i toma.mp4 -vn -af "aresample=16000,asetnsamples=800,astats=metadata=1:reset=1,ametadata=print:key=lavfi.astats.Overall.RMS_level:file=-" -f null -` — los valles (< −35 dB) son los límites reales |
| Un clip de nivel raíz de HyperFrames aparece pegado arriba a la izquierda | El runtime fuerza `top:0; left:0` en los hijos directos con `data-start`: posicionarlos con `margin`, no con `top`/`left` |
| Tras pasar escenas a sub-composiciones, en el snapshot desaparecen TODOS los textos | Una llamada del script principal a una función que se movió al sub-archivo lanza un error y la línea de tiempo principal nunca se registra. Snapshot después de cada cambio estructural |
| El subtítulo tapa el elemento protagonista del plano (el círculo rojo en la pantalla de un teléfono) | Mover la franja de subtítulos durante ese plano a la zona libre (arriba, bajo la pastilla); nunca encima del protagonista |
| `"dwell"`/`fromTo` repetidos sobre el mismo elemento sin línea base (`gsap_repeated_fromto_without_baseline`) | `immediateRender: false` en todos menos el primero |
