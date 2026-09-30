# Nivel 3 · Estudio — siempre avanzado

El nivel 3 no es "el 2 con más cosas". Es lo que entregaría un motion designer que además edita al
100 %. Este archivo es el **contrato**: lo que toda pieza de nivel 3 tiene que tener, las técnicas
con las que se consigue en HyperFrames, y lo que ya no se hace. Complementa `motion-design.md`
(recetas probadas en piezas reales).

## 0 · Intensidad — cuánto se carga (se pide así: "nivel 3 · intensidad 2")

El contrato (§1) es el piso de **todas** las intensidades. La intensidad sube la densidad y la
complejidad. Sin decirla, es la 1. Se puede añadir un **énfasis**: `recortes`, `efectos` o `datos`
("nivel 3 · intensidad 2 · énfasis recortes"), que decide dónde se gasta la carga extra.

| | **1 · Profesional** | **2 · Dinámico** | **3 · Extremo** ("¿qué es eso?") |
|---|---|---|---|
| Cambio de estado visual | cada 3–8 s (mediana ~5) | cada 2–4 s | cada 1–2 s |
| Sonido | un SFX por transición o gráfico clave | SFX en cada evento + *riser* antes de los cambios grandes | diseño sonoro denso por capas: evento + ambiente + riser/impacto/sub, sincronizado al cuadro |
| Recortes de la persona | 1 (cierre, `recetario-3.md` R1) | 2–4 congelados con recorte + texto detrás de ella (R2) | **recorte en movimiento** (sigue hablando recortada), gráficos que pasan por delante y por detrás de ella |
| Profundidad | 1 momento | 2–3 (parallax 2.5D) | continua: 2.5D con mapa de profundidad, cámara 3D, objetos 3D |
| Cámara | zoom ≤ 1 cada 5 s | punch-ins + rampas de velocidad | rampas, *whip*, sacudida con intención, cortes en coincidencia |
| Transiciones | motivadas | + máscara con la silueta, estela de desenfoque | todas hechas a medida; glitch ≤ 2 por pieza |
| Énfasis en subtítulos | **uno solo** (igual en las tres) | uno solo | uno solo |
| Tiempo relativo | base | ≈ ×1.5–2 | ≈ ×3 |
| Aprobación | propuesta | propuesta + 2–3 cuadros de muestra | propuesta + **prueba animada de 5–10 s** aprobada antes de hacer el resto |

**Freno de la 3:** la voz se entiende siempre y la idea se puede repetir después de verlo. Si un
efecto tapa lo que se dice, se quita, aunque sea espectacular.

**Cada efecto necesita un motivo en lo que se dice** (sobre todo en la 2 y la 3). Antes de poner uno,
responder *"¿qué palabra o idea lo justifica?"*. Si es una muletilla o una transición de frase
("like if we", "so those are things"), no lleva nada. Más intensidad = más efectos **con sentido**, no
llenar huecos: el director vio la primera intensidad 2 "saturada" porque el congelado, el barrido y
los empujes cayeron en frases sin peso. Congelado con palabra detrás (R2): **uno por pieza**, en la
palabra que resume el mensaje.

**Pendientes para la intensidad 3** (ver `LIMITACIONES.md`): el recorte en movimiento parpadea
(L1), no hay generador de SFX (L4) ni música con licencia (L5). Hasta resolverlos, la 3 usa
congelados con recorte, SFX sintetizados o de biblioteca propia, y sin música salvo que el
director pase la pista.

## 1 · Contrato — el revisor lo comprueba punto por punto

1. **Primer cuadro ya en movimiento.** Nunca se abre en un cuadro quieto: el cerebro registra
   inercia. **Gancho legible en ≤ 1.5 s**; la promesa o el remate, en ≤ 2.5 s. Cero preámbulo.
2. **Sistema de movimiento declarado** (tokens IN / OUT / MOVE + un spring) y usado en todo.
   **Al menos 3 curvas distintas**, ninguna lineal en movimiento espacial.
3. **Tres capas en cada escena**: acción principal, movimiento secundario (sigue o reacciona a la
   principal) y **vida ambiente** (textura, grano, deriva lenta, brillo). Nada completamente quieto.
4. **Cambio de estado visual cada 3–8 s** (mediana ~5 s). Nunca más de 8 s sin que algo cambie.
5. **Al menos un momento de profundidad**: palabra detrás de la persona, desenfoque de profundidad,
   capas de texto en Z, parallax 2.5D o un objeto 3D.
6. **Al menos un gráfico único ligado al contenido** (mapa, dato que cuenta, lista que se construye,
   diagrama). Nada de gráficos de stock genéricos.
7. **Transiciones motivadas**: por velocidad (la salida y la entrada comparten dirección y rapidez),
   por máscara, por escala o por corte en coincidencia. Nunca un corte plano entre dos bloques gráficos.
8. **Diseño sonoro completo** y **entrega a −14 LUFS, −1 dBTP** (la voz al frente): un sonido por evento visual con intención, cama musical con ducking si
   hay música con licencia, y un cierre sonoro. La voz manda (SFX ≤ −16 dBFS).
9. **Grade de color** que case el metraje con la paleta.
10. **Cierre firma** con movimiento hasta el último cuadro (personaje recortado, emblema, logo).
11. **Un solo mecanismo de énfasis** en subtítulos (caja, color o peso — nunca mezclados).
12. **Propuesta aprobada antes** de construir, **revisor final** después (`qa.sh` con sus alarmas).

## 2 · Tiempos y curvas

| Elemento | Duración | Curva |
|---|---|---|
| Micro (pop de chip, tic) | 80–150 ms | `power2.out` |
| Entrada de tarjeta / rótulo | 200–350 ms | `expo.out` (desacelera) |
| Salida | 60–75 % de lo que tardó en entrar | `power2.in` (acelera) |
| Movimiento en pantalla / cambio de encuadre | 400–800 ms | `expo.inOut` |
| Revelado dramático / cierre | 600–1200 ms | spring ζ = 1 (asentamiento largo = "premium") |

- **En vertical todo es más rápido**: un revelado de 2 s en 16:9 tiene que caer en < 1 s en 9:16.
- **La distancia escala la duración**: 100 px = base, 200 px ≈ ×1.3, 400 px ≈ ×1.6.
- **Regla de 1/3**: nada recorre más de un tercio de la pantalla sin un fotograma clave intermedio,
  y no se anima más de un tercio de los elementos a la vez. **Primero entra el protagonista.**
- **Escalonados**: micro 20–40 ms, estándar 50–100 ms, dramático 100–200 ms (total < 600 ms).
- **El rebote va solo en transformaciones**, nunca en opacidad ni color. ζ < 0.8 solo si el tono es
  explícitamente juguetón.
- **Texto en pantalla**: el tiempo suficiente para leerlo **dos veces**.
- **Movimientos rápidos llevan desenfoque de movimiento** (estela de obturador), no saltos secos.

## 3 · Técnicas en HyperFrames (nombres reales del skill `hyperframes-animation`)

GSAP es gratis entero desde la 3.13, incluidos **SplitText, MorphSVG, DrawSVG, CustomEase,
MotionPath, ScrambleText y Physics2D**, también para uso comercial.

| Para… | Reglas / blueprints |
|---|---|
| Gancho | `kinetic-beat-slam`, `spring-pop-entrance`, blueprint `kinetic-type-beats`, `titlecard-reveal` |
| Palabra clave | `asr-keyword-glow`, `gradient-text-sweep`, `discrete-text-sequence` |
| Profundidad | `3d-text-depth-layers`, `depth-of-field-blur`, patrón *text-behind-subject* (`hyperframes-creative`) |
| Cámara | `coordinate-target-zoom`, `multi-phase-camera`, `3d-camera-flight`, blueprint `camera-journey` |
| Datos | `counting-dynamic-scale`, `stat-bars-and-fills`, `chart-scrub-readout`, blueprint `dataviz-countup` |
| Trazos, mapas, iconos | `svg-path-draw`, `svg-icon-enrichment` (con `pathLength="1"`, ver `motion-design.md`) |
| Transiciones | `scale-swap-transition`, `motion-blur-streak`, `theme-crossfade-morph`, máscaras `clip-path` |
| Vida ambiente | `ambient-glow-bloom`, `sine-wave-loop` (sin `repeat:-1`), grano/papel |
| Acentos con moderación | `particle-burst`, `chromatic-glitch` (1 vez por pieza como mucho) |
| Cierre | blueprint `logo-assemble-lockup`, receta "cierre con personaje" de `motion-design.md` |

Antes de escribir a mano: `npx hyperframes add <bloque>` y adaptar (reutilizar primero). Leer
`hyperframes-creative/references/house-style.md` (la lista de "defaults perezosos" que hay que
cuestionar) y `video-composition.md`.

**Video dentro de un recuadro** (L2): nunca un `<video>` con `clip-path` y escala < 1 — puede salir
negro en el render. El contenido del recuadro se **pre-renderiza 1:1 con FFmpeg** (tamaño exacto del
recuadro, crop con expresión si hay paneo, CRF 14, sin audio) y va en su propio `<video>` sin
transform; el metraje grande solo aparece a pantalla completa, escalando hacia arriba. **Color con
FFmpeg** (`source_graded.mp4`), nunca `filter:` CSS sobre video. Receta completa: `troubleshooting.md`.

Reglas técnicas de HyperFrames que no se rompen: nada de `Math.random()` ni `Date.now()`, nada de
`repeat: -1`, posiciones precalculadas (no `getBoundingClientRect()` en render), timeline pausada en
`window.__timelines`.

## 4 · Lo que ya NO se hace (2026)

- **La estética "gurú"**: letra Impact con amarillo/verde neón, emojis por todas partes, whoosh y pop
  de catálogo en cada corte. El público la clasifica al instante como contenido barato y se va.
- **Gráficos de stock genéricos** que no nacen del contenido.
- **Zooms en cada frase**: máximo uno cada 5 s; uno deliberado y grande (≈ ×1.5) vale más que diez.
- **Mezclar mecanismos de énfasis** (caja + color + peso + emoji a la vez).

La dirección vigente es **minimalismo dinámico**: tipografía limpia, sombras suaves, transiciones
fluidas, y el movimiento al servicio de lo que se dice.

## 5 · La propuesta (antes de construir)

`clipper.py render … --nivel 3` deja el corte limpio y `*-PROPUESTA.md` con el beat sheet
cronometrado. Se completa con:

1. **Concepto** en una frase y **referencia visual** con nombre.
2. **Qué punto del contrato cumple cada beat** (tabla).
3. **Gráficos únicos** y **momento de profundidad**.
4. **Imágenes a generar** con Higgsfield (prompts; nunca texto dentro de la imagen).
5. **Sonido**: SFX por evento, música (¿cuál, con qué licencia?).
6. **2–3 cuadros de muestra**: `npx hyperframes snapshot` de un boceto o imágenes de Higgsfield.

**PARADA hasta el OK del director.** Después: Pasos 3–9 de `SKILL.md`.

## Fuentes

- [HyperFrames — skills `motion-graphics` y `hyperframes-animation`](https://github.com/heygen-com/hyperframes)
- [LottieFiles — motion-design skill (tiempos, curvas, escalonados, regla de 1/3)](https://github.com/LottieFiles/motion-design-skill/blob/main/skills/motion-design/SKILL.md)
- [GSAP 3.13 — todos los plugins gratis](https://gsap.com/blog/3-13/)
- [Envato — motion graphics para video corto vertical (gancho 1.5 s, primer cuadro en movimiento)](https://elements.envato.com/learn/motion-graphics-for-short-form-video)
- [Ali Abdaal medido cuadro a cuadro (cadencia 3–8 s, un solo énfasis, remate ≤ 2.5 s)](https://www.writepanda.ai/blog/how-to-edit-shorts-like-ali-abdaal/)
- [El estilo Hormozi en 2026 (qué sigue funcionando y qué ya no)](https://joyspace.ai/hormozi-editing-style-2026-analysis)
