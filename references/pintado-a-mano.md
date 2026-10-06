# Pintado a mano — película con personaje pintado (gouache + crayón) · receta de nivel 4

Una pieza que parece **pintada a mano cuadro a cuadro**: un personaje inventado en gouache y crayón de cera
que actúa (mira el teléfono, suspira, estira el brazo), animado **editando la pintura anterior un cambio a la
vez**, con la información, los efectos y el sonido hechos **en código** en el mismo estilo. Las pinturas salen
de Nano Banana Pro (Higgsfield); el tiempo, los gráficos, el sonido y el render, de aquí.

Es una receta del **nivel 4 · Director** (`nivel-4.md`): mete material que no existía, cuesta créditos y pide
tres aprobaciones (tratamiento → hoja de modelo + primera base → cada plano animado).

## Cuándo sí, cuándo no

| Sí | No |
|---|---|
| Un anuncio o explicativo con **un personaje que siente algo** (insomnio, procrastinar, trabajo que no acaba) | Una persona real (nunca se pinta a alguien que existe) |
| Guion de 45–60 s, 12–25 líneas, **una idea y una imagen por línea** | Acción rápida, peleas, muchos personajes, cámara que gira 360° |
| Voz en off (TTS o grabada) que marca el tiempo | Texto largo en pantalla dentro de la pintura (el texto se monta, nunca se pinta) |
| Dos o tres escenarios como mucho | Diez escenarios distintos (cada uno es otra base y otra hoja de modelo de luz) |

## Costos y tiempos (reales)

- **Nano Banana Pro: 2 créditos por imagen** (2K, 9:16 o 16:9). Se generan **dos variantes por paso** y se
  queda la que se movió menos.
- Pieza de ~55 s con 2 planos: hoja de modelo (2) + 2 bases × 2 + ~14 pasos de edición × 2 + reintentos ≈
  **45–55 imágenes ≈ 90–110 créditos**. Presupuestar ~2× por si una base sale rota.
- Voz: un par de tomas del guion completo (Higgsfield `seed_audio` o la que use el cliente).
- Tiempo de agente: ~4–6 h la primera vez por idioma; la segunda versión de idioma reutiliza todas las
  pinturas (solo voz, subtítulos, rótulos y re-tiempo): ~1 h.

## El flujo, en orden

1. **Guion y voz primero.** La voz decide la duración de todo. Una toma del guion completo, transcrita con
   Whisper; se corta en líneas por los **silencios de la envolvente** (Whisper solo dice qué silencio es
   cuál: sus tiempos de palabra se desvían hasta 0.8 s). Cada evento visual se ancla a **línea + fracción de
   línea**, no a segundos: así la versión en otro idioma re-temporiza sola.
   - **Nunca `...` en el texto del TTS**: inventa habla en la pausa. Las pausas (respirar 4 s, sostener 3 s)
     se insertan en el montaje.
   - Marcas que el TTS pronuncia mal: se escriben como suenan solo en el texto de la voz; los subtítulos
     salen del guion, bien escritos.
2. **Hoja de modelo (una vez).** Tres vistas del personaje sobre fondo liso. Se adjunta como referencia en
   todas las bases. Plantilla abajo.
3. **Una pintura base por plano.** El cuarto, la luz y el personaje en su primera pose. Dos variantes, se
   elige una. Dejar **espacio vacío** (una pared, un cielo) donde vivirán los gráficos de código y los
   subtítulos.
4. **Animar editando la pintura.** Cada dibujo = el anterior con **un** cambio. Se adjunta **solo el dibujo
   anterior** como referencia. Un cuerpo por paso: el brazo, luego la mano, luego la cabeza. Dos variantes,
   gana la que se movió menos. Si una prop saltó, la cara cambió o el encuadre se movió: **se rechaza y se
   vuelve un paso atrás; nunca se arregla con otra edición.**
5. **Fijar los dibujos** (`scripts/pintado/composite_frames.py`): alinear cada dibujo con la base usando solo
   el fondo, igualar color en lo que no cambió, y pegar **solo lo que cambió** sobre la base. El cuarto queda
   idéntico al píxel en todo el plano.
6. **Hoja de exposición** (`scripts/pintado/exposure_sheet.js`): `[[segundo, dibujo], …]`, fundido de 1
   cuadro en cada cambio y un **boil** de 12 fps que mantiene vivo el dibujo quieto.
7. **Intercalados por flujo óptico** (`scripts/pintado/flow_inbetween.py`) para cambios lentos (un brazo que
   baja, algo que se derrite): 3–4 intercalados por par; donde la forma cambia demasiado, corte limpio a la
   mitad en vez de fantasma.
8. **Mover al personaje a otra pintura** (solo si hace falta): pase en blanco (plantilla abajo) + quitar fondo
   de Higgsfield + sombra de contacto. Nunca recortar con código de una pintura cargada.
9. **Gráficos en código, en el mismo crayón** (HyperFrames): trazos con 2–3 pasadas desplazadas al azar
   (determinista) cuyo "seed" cambia a 12 fps = el boil. Rótulos de papel, nubes, reloj, partículas, tarjetas.
   **Todo lo que es información o efecto va en código; todo lo que es el personaje actuando, pintado.**
10. **Sonido sintetizado en las mismas señales** que la imagen (tono de cuarto, toques, papel que golpea por
    cada rótulo, respiración, campana final). SFX ≤ −16 dBFS, voz encima, máster −14 LUFS / −1 dBTP.
11. **Render, revisor, export** (abajo).

## Plantillas de prompt (exactas)

**Hoja de modelo** · 16:9 · sin referencias (o 2–3 de estilo)
```
Character model sheet of ONE invented <edad> <persona>, hand-painted in opaque gouache with visible wax-crayon
line work and crayon hatching on textured paper, like a children's picture-book animation: <cara>, <pelo>,
<piel con hatching>, wearing <ropa con colores exactos en hex, p. ej. (#RRGGBB)>. Three full-body views side by
side on a plain flat <color> background: <vista 1 con la prop principal>, <vista 2 en la pose que más se usará>,
three-quarter back view standing. Same character in all three views, consistent proportions (realistic young
adult proportions, head about one seventh of height), consistent colours, matte gouache, slightly wobbly
crayon outlines. No text, no labels, no logos.
```

**Base de un plano** · 9:16 o 16:9 · refs: hoja de modelo (y la base anterior si es el mismo cuarto)
```
Gouache and wax-crayon painting in exactly the technique, line work and palette of the reference model sheet,
a single animation frame, vertical composition. <hora, lugar, paleta>. <dónde está el personaje, pose, qué
mira, qué sostiene>. <La fuente de luz> is the main light: it <cómo cae: pool suave, se desvanece en los
bordes>, the way a real <lámpara / pantalla> lights a dark room. <Props y su posición>. The upper half of the
frame is a calm, mostly empty <pared> with soft crayon texture. Everything outside the light falls off
smoothly into <color> darkness. No hard-edged light shapes. No text, no clock, no logos.
```

**Paso de edición** · ref: SOLO el dibujo anterior
```
Edit this exact painting. Change ONLY <una parte>: <el cambio, concreto y pequeño>. Do not move <lo que tiende a
moverse: el teléfono, la mano, el brazo>. Do not add arrows, motion lines, symbols or marks anywhere. Keep
<cabeza, cara, ojos, pelo, cuerpo, ropa, props, muebles, luz, ventana, pared>, all colours, the crayon texture
and the framing exactly identical. Full-bleed. No text.
```

**Cambio de luz** (una lámpara que se enciende) · ref: el dibujo anterior
```
Edit this exact painting. Change ONLY the light: the small <lámpara> is now switched on, dimmed low. Its
<pantalla> glows a soft warm amber and throws a warm, soft, circular pool of light across <superficies
cercanas>, and a gentle glow on the wall around it that fades gradually at its edges; everything outside its
reach falls off smoothly into the same <color> darkness, the way a real dim lamp lights a dark room. Keep
<pose, cara, props, muebles>, crayon texture and framing exactly identical. No hard-edged light shapes, no
beams. Full-bleed. No text.
```

**Pase en blanco** (para recortar) · ref: el dibujo del personaje
```
Edit this exact painting. Change ONLY the background: it becomes a plain, clean, pure white background
(#FFFFFF), perfectly flat, no shadows, no texture. Their edges are only the painting's own crayon line work,
with no coloured halo, no glow and no sticker border. Keep <el personaje y lo que sostiene> exactly identical:
same pose, proportions, size and position in the frame, same face, hair, clothes, colours and
gouache-and-crayon style. Full-bleed. No text.
```

## Herramientas (en `scripts/pintado/`)

Python con OpenCV: el entorno aislado de edit-video ya lo trae (`~/.config/edit-video/venv-caras/bin/python`).
Sin OpenCV, las dos caen a numpy + Pillow y lo dicen (solo traslación; corte a la mitad sin flujo).

```bash
PY=~/.config/edit-video/venv-caras/bin/python
# fijar: SET_DIR con base primero (00.png, 01.png…); --chain para cadenas largas; --roi para pegar solo ahí
$PY SKILL_DIR/scripts/pintado/composite_frames.py plano1 --chain --roi 0.55,0.62,0.97,0.90
#   SET_DIR/rois.json por dibujo: {"05.png": [[x0,y0,x1,y1]], "12.png": "light"}  ("light" = solo la luz)
# intercalados: 4 entre cada par de dibujos ya fijados (+ map.json con dónde quedó cada original)
$PY SKILL_DIR/scripts/pintado/flow_inbetween.py plano1/steady plano1/flow --n 4
# pruebas
$PY SKILL_DIR/scripts/pintado/composite_frames.py --selftest
$PY SKILL_DIR/scripts/pintado/flow_inbetween.py --selftest
node SKILL_DIR/scripts/pintado/exposure_sheet.test.js
```

En la composición (HyperFrames): un `<div>` por plano con un `<img>` por dibujo apilados;
`ExposureSheet.sheetDraw("s1", HOJA, t, { boil: { seed: 3 } })` desde el `onUpdate` del reloj del timeline.
Bucles: `ExposureSheet.loop([0, 1], 0.1, t0, t1)`. Un cambio de luz con fundido propio: `[t, dibujo, 30]`.
Un "todo se congela": `{ boilT: T_CONGELA }` congela el boil sin congelar la hoja.

Arquitectura que funcionó:
- **Cámara = función pura de t** por plano (`[t, escala, x, y]` con curvas), acotada para no ver el borde
  de la pintura. Nada de leer el DOM en el `onUpdate` (el render busca cuadros fuera de orden).
- Gráficos que viven en la pintura (nube, rótulos, tarjetas): **dentro** del contenedor de la cámara, en
  coordenadas de la pintura. Gráficos que viajan entre planos (partículas): en pantalla, encima.
- Si los planos llevan `z-index` (para cruzarlos), **todo lo de encima necesita su propio `z-index`**
  (partículas, cierre, subtítulos): si no, quedan tapados sin aviso.

## Trampas (cada una salió en una pieza real)

1. **La luz se describe como una lámpara real** ("pool suave que se desvanece en los bordes", "the way a real
   lamp lights a dark room") **y "No hard-edged light shapes"**. Si la luz sale mal, **base nueva**: las
   ediciones encima de una base rota nunca la arreglan.
2. **Las ediciones derivan**: cada paso hace un poco de zoom y corre el color (tras 8 pasos, ~50 px y un tinte
   morado). Alinear cada dibujo directo con la base falla cuando cambió mucho (un brazo entero): usar
   `--chain` (cada uno con el anterior ya alineado; arranque con puntos ORB del fondo + RANSAC, afinado ECC).
   El color se iguala siempre contra la base.
3. **El modelo cambia más de lo pedido** (la cara, la lámpara, la cabecera): `--roi` pega solo el cambio que
   se pidió; lo que derivó fuera se queda de la base.
4. **"Flick upward" dibuja una flecha.** Verbos de movimiento → el modelo pone flechas o líneas de
   movimiento. Siempre: "Do not add arrows, motion lines, symbols or marks anywhere".
5. **Encender una luz no es un "cambio de zona"**: toda la imagen cambia. Modo `"light"`: se transfiere solo
   la luz (diferencia suavizada entre el dibujo nuevo y el anterior, aditiva) al cuadro fijo anterior; la
   geometría no se mueve. Multiplicar en vez de sumar deja la luz cálida verde-amarilla sobre un azul.
6. **Bordes**: alinear deja una franja inventada (reflejo) en el borde; la máscara de píxeles válidos con
   borde suave la excluye. Si se ve una costura vertical, es esa franja: revisar a tamaño completo.
7. **Halos al recortar**: nunca recortar con código de una pintura cargada; pase en blanco + quitar fondo, y
   revisar los bordes a tamaño completo (en miniatura no se ven).
8. **Saltos grandes = diapositiva.** Más dibujos por acción (un paso intermedio de "levanta el teléfono un
   cuarto") y 3–4 intercalados por par se leen como animación.
9. **JS incrustado**: HyperFrames puede incrustar los `.js` dentro del HTML; un comentario que contenga la
   etiqueta de cierre de script rompe la página entera ("Invalid or unexpected token").

## Revisor (obligatorio, además de `qa.md`)

- `bash SKILL_DIR/scripts/qa.sh final.mp4 2 <tiempos clave>` y **mirar todas** las hojas de contacto.
- **Consistencia del personaje**: una hoja con todos los dibujos fijados lado a lado; misma cara, mismo pelo,
  misma ropa, props en su sitio (un teléfono, no dos; una mano por brazo). Revisar a tamaño completo.
- **Nada parpadea**: luma media por cuadro sin componente periódica > 2 Hz (el boil mueve 1 px, no cambia
  la luz; los bucles de dibujo van en ráfagas cortas, no continuos). Un cambio de luz siempre es un fundido
  de ≥ 1 s.
- **Nada quieto**: cuadros a 0.5 s de distancia distintos en cada pausa (el boil + la cámara lo garantizan;
  comprobarlo igual).
- **Subtítulos**: cobertura N/N, fuera del 20 % inferior, un solo énfasis.
- **Sin texto pintado**: si el modelo metió letras, números o logos en una pintura, se regenera ese paso.
- Pintura generada = ficción: nunca se presenta como una persona o un hecho real.
