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

## Versión de HyperFrames (radar 2026-10-15)

Los arreglos del motor solo llegan si el proyecto usa una versión que los tenga. **Un proyecto creado con
HyperFrames fija `hyperframes@<versión>` en los scripts de su `package.json`** y esa versión no sube sola ni
avisa (skill `hyperframes-studio`). Antes de renderizar un proyecto retomado:
`grep -o 'hyperframes@[0-9.]*' package.json`.

| Defecto | Arreglo |
|---|---|
| **Franja negra de 8 px en el borde derecho** de un MP4 de 1080 de ancho (no la caza la alarma de NEGRO: es < 1 % del cuadro) | Bug de HyperFrames < 0.8.155 con FFmpeg 7.1/8.0 cuando el ancho es múltiplo de 16 + 8 (heygen-com/hyperframes#5559). Re-renderizar con ≥ 0.8.155. `qa.sh` avisa (`⚠ BORDE DERECHO NEGRO`) |
| **Grabación de pantalla que se congela a medio render** (un cuadro se queda y los demás se pierden), con FFmpeg 8 o posterior | Video de frecuencia variable (VFR): FFmpeg 8 respeta la duración de cada cuadro. Arreglado en HyperFrames 0.8.156 (#5572). Con una versión fijada más vieja, pasar el clip a frecuencia constante antes: `ffmpeg -i in.mp4 -fps_mode cfr -r 30 -c:v libx264 -crf 14 -c:a copy cfr.mp4`. Cómo saber si es VFR: `ffprobe -v error -select_streams v:0 -show_entries stream=r_frame_rate,avg_frame_rate -of csv=p=0 in.mp4` — si los dos números no coinciden, lo es (probado: `30/1,600/59` → tras convertir `30/1,30/1`) |

## Disco externo (macOS)

- **Se llenó el disco interno aunque el proyecto estaba en el externo**: el disco no estaba montado y
  `/Volumes/<DISCO>/…` se creó como carpeta normal del interno; o `TMPDIR`/cachés seguían en el interno.
  → `scripts/destino.sh check` antes de renderizar y `eval "$(destino.sh env <carpeta>)"`.
- **Conteos o listas de cuadros al doble en un disco exFAT**: macOS crea `._archivo` al lado de cada archivo.
  → contar con `find … -name '[!.]*'`; `COPYFILE_DISABLE=1` al empaquetar. `qa.sh` e `ingest.sh` ya lo hacen.
- **Render lento o la Mac se congela con 8 GB**: demasiados workers → swap (que además escribe en el interno).
  → 2 workers (`EDIT_VIDEO_WORKERS`), placa única pre-renderizada.
