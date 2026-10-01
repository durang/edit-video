# Revisor final — nadie entrega sin pasar esto

El agente que construye **no es el que aprueba.** Antes de decir "listo", el agente se pone en el
papel de un revisor que quiere rechazar el trabajo, y revisa **el MP4 renderizado**, no el preview.

## 1 · Sacar el video entero

```bash
bash <SKILL_DIR>/scripts/qa.sh final.mp4 2  1 3 <tiempos clave…>
```

- Hojas de contacto con un cuadro cada **0.5 s** de todo el video.
- A tamaño completo: el primer segundo, cada transición, cada entrada de texto grande, el cierre, y
  **siempre el último cuadro del video** — es el que se queda en pantalla y donde más se esconden fallos.
- **Se miran TODAS.** Mirar solo unas cuantas es no revisar.

Si el entorno permite subagentes, la revisión la hace **otro agente** con este archivo y las hojas,
sin ver el código: solo el video. Es lo que más errores caza.

## 2 · Checklist, cuadro por cuadro

**Texto**
- [ ] **Ninguna palabra partida** entre dos líneas (`COLOMBI` / `A.` = rechazo)
- [ ] Ninguna palabra cortada por un borde del cuadro o por una máscara
- [ ] Ningún glifo suelto durante las entradas y salidas (revisar las transiciones cuadro a cuadro)
- [ ] Ortografía de nombres, marcas, cifras = la del `AGENTS.md`; ningún nombre inventado
- [ ] Todo legible a tamaño de teléfono: **nada por debajo de 26 px sobre metraje**; las etiquetas
      secundarias van en pastilla sólida, nunca finas sobre video

**Logo motion — lockup contra el original (BLOQUEANTE)**
- [ ] **El lockup final de cualquier logo motion se valida contra el archivo original del logo**
      (overlay/diff del cuadro final del lockup sobre el PNG oficial escalado): mismo espaciado,
      mismas proporciones, **cero encimados** (el wordmark nunca toca el isotipo). Si el isotipo se
      arma por piezas, haz crossfade a la imagen real en el *snap* para que el lockup sea pixel-idéntico.
- [ ] Hojas de contacto cada **0.25 s** en el tramo del lockup y del destejido: en ningún cuadro
      se cruzan texto y pieza/logo. Receta completa: `logo-motion-tejido.md`.

**Subtítulos (BLOQUEANTE — el director los considera lo más importante)**
- [ ] **Cobertura N/N**: por CADA palabra de `transcript.json`/`words.json` se extrae el cuadro en su tiempo
      medio y el subtítulo está visible y legible. El QA escribe "N/N palabras con subtítulo". Menos de N/N = rechazo.
- [ ] Al reconstruir o ampliar una prueba a pieza completa, el subtítulo se extiende a **toda** la pieza
      (error real: la prueba de 10 s tenía subtítulo y la pieza completa no, de 10 s al final)
- [ ] Ningún gráfico tapa el subtítulo; si chocan, se mueve el gráfico

**Recortes de la persona (cierre R1 y congelados)**
- [ ] La silueta solo puede cortarla el **borde inferior** del cuadro; nunca un lado a media altura
      (brazo o mano cortados en seco = rechazo). Revisar cada 0.1 s todo el cierre a tamaño completo
- [ ] **Ojos abiertos en todo congelado/recorte**: el cuadro del congelado se elige midiendo `eyeBlink` con
      FaceLandmarker (venv de caras) en los últimos 3–5 s y tomando el de ojos abiertos (blink < 0.2) más cercano al
      final — nunca "el último cuadro" a ciegas (error real: cierre congelado a mitad de parpadeo)
- [ ] Texto "detrás de la persona" (R2 o recorte en movimiento): **todas** sus letras, también las etiquetas
      pequeñas, se leen; si la persona tapa algo que no sea la palabra grande (≤ 30 %), el bloque va delante
- [ ] Si una versión anterior de la misma pieza ya tiene un cierre aprobado, se **reutiliza ese recorte y
      esa posición** en lugar de rehacerlo

**Composición**
- [ ] Nada encima de la cara
- [ ] Nada de texto fuera de la safe zone
- [ ] Márgenes iguales en todos los bloques
- [ ] Un solo acento dominante por pantalla
- [ ] Ninguna zona muerta: si un área existe (pie, banda), está diseñada

**Fuente**
- [ ] Ningún subtítulo quemado del original asomando
- [ ] Ningún logo o marca de agua del original cortado a medias (o entero o fuera)

**Trazos y gráficos**
- [ ] Todo trazo que se dibuja (contornos, flechas, arcos, checks) termina **completo y cerrado**;
      a mitad del trazo se ve **una sola línea continua** avanzando, nunca trozos sueltos
- [ ] Mapas con geometría real (Natural Earth), puntos en sus coordenadas reales
- [ ] Ningún gráfico entra mientras la cámara todavía se está moviendo hacia su hueco

**Movimiento y coherencia**
- [ ] Mismas curvas y duraciones de entrada/salida en todos los bloques del mismo tipo
- [ ] Cada efecto cae en su palabra (comparar con `transcript.json`)
- [ ] Transiciones sin saltos, sin cuadros negros, sin parpadeos

**Técnico**
- [ ] Duración, resolución y fps correctos · audio presente y en sincronía

## 3 · Si falla algo

Se anota en `SNAPSHOTS.md` (tiempo · defecto · arreglo), **se arregla, se vuelve a renderizar y se
vuelve a revisar entero.** Solo una pasada completa limpia autoriza decir "listo".

## Errores reales que este checklist ya cazó

- **El video del recuadro salió NEGRO 18 segundos** y el constructor dijo "verificado": un cambio en
  el encuadre sacó el metraje del recuadro y solo quedó el fondo `#000`. El revisor independiente lo
  vio en la primera hoja de contacto. Desde entonces `qa.sh` avisa solo de cuadros con ≥10 % en negro.
- **Recorte de persona hecho sobre un cuadro ya recortado** → en el cierre se veía un corte recto
  vertical en su hombro y su moño. Los recortes se sacan **del cuadro completo del original**, y
  ningún borde recto de la silueta puede verse (solo el borde inferior del lienzo).
- **Artefacto de máscara**: un rectángulo color piel en la mandíbula del recorte, un solo cuadro.
  Por eso se miran también los cuadros de transición, no solo los de reposo.
- **Créditos encima de la persona** en el cierre, y sobre un fondo dibujado donde no se leían.
  Texto pequeño solo sobre papel limpio o con placa sólida.
- **Tarjeta vacía**: el marco del mapa entraba medio segundo antes que el mapa. Contenedor y
  contenido entran juntos.
- **`clip-path` que se encoge a un punto sin fade**: al final del cierre quedaba un rectángulo color
  piel en el centro, un cuadro. La capa se desvanece mientras se encoge (`recetario-3.md` R1).
- **Borde recto arriba de un fondo recortado** (paisaje que sube): línea horizontal visible →
  degradado de 120 px con `mask-image` en el borde superior.
- **La voz se oía bajita** (−16 LUFS): en el teléfono todo se oye más bajo que en el editor. Entrega
  siempre a **−14 LUFS integrados, −1 dBTP**, con la voz al frente. Master sin re-renderizar el video:
  `ffmpeg -i in.mp4 -c:v copy -af "highpass=f=70,equalizer=f=3000:t=q:w=1.2:g=2.5,acompressor=threshold=-22dB:ratio=2.5:attack=8:release=120:makeup=2,loudnorm=I=-14:TP=-1.5:LRA=7,aresample=48000" -ar 48000 -c:a aac -b:a 256k out.mp4`
- **Cambios encimados al agrupar**: al juntar varios cambios en un solo tiempo, la etiqueta vieja y la
  nueva quedaron visibles a la vez ¼ s. Agrupar = la vieja sale (0.1 s) y la nueva entra justo después.
- **Demasiados cambios en poco tiempo**: 12 en 8 s se leyó como "destellos". Contar cambios por frase
  en la hoja de contacto (≤ 1 por frase salvo que la frase lo pida).
- **Final en silencio digital** (−91 dB): el último sonido tiene que llegar al último cuadro con fade.

- Titular de cierre partido en dos líneas: `COLOMBI` / `A.`
- Medio logo de la fuente asomando por el borde de un recuadro
- Micro-etiquetas mono finas sobre metraje: ilegibles en el teléfono
- Un mapa "estilizado" que parecía un garabato → siempre geometría real (Natural Earth)
- Una banda negra del 20 % de la pantalla con solo una palabra: zona muerta
- Subtítulos quemados del original asomando durante un zoom
- Un contorno de país "dibujándose" que al final eran 7 trozos sueltos (dasharray medido en otra
  escala). Arreglo: `pathLength="1"` y animar de 1 a 0
- El revisor del propio agente lo dio por bueno: **por eso la revisión la hace otro**

### Errores reales (2026-09-30)
- **Audio a 96 kHz = "no se escucha" en el celular.** `loudnorm` sube la frecuencia interna; sin `aresample=48000`
  el AAC sale a 96 kHz y varios reproductores móviles lo dejan mudo. Entrega SIEMPRE a 48 kHz (`qa.sh` avisa).
- **Subtítulos perdidos en un tramo heredado.** Al subir de intensidad se reconstruyó un tramo y el subtítulo de
  0–17 s desapareció; el revisor miraba efectos, no subtítulos. Regla: al hacer una versión nueva, comparar cada
  0.5 s contra la versión aprobada — donde antes había subtítulo, ahora también.
- **Pieza completa sin subtítulos después de la prueba**: la prueba aprobada (0–10 s) llevaba subtítulo; al
  construir el resto, el constructor no lo extendió y el revisor no lo buscó. → check de cobertura N/N.
- **Cierre con el brazo cortado por el lado**: el recorte se escaló grande y el borde derecho le cortó el brazo
  en seco. La versión hermana (otra intensidad) ya tenía un cierre aprobado → reutilizarlo.
- **Render cancelado al terminar el turno del constructor**: lanzar el render en segundo plano y cerrar el turno
  mata el render (`render_cancelled_parent_exited`). El render va en **primer plano** dentro del turno.

### Errores reales (2026-10-01, radar)
- **clipper entregaba a 96 kHz**: los clips de niveles 1–2 salían con el AAC a 96 kHz (el mismo fallo de
  `loudnorm` de arriba). Arreglado en clipper (3.11.1); `qa.sh` ahora avisa de **cualquier** frecuencia ≠ 48 kHz.
- **Pico real por encima de −1 dBTP** en una pieza de nivel 3 masterizada con `TP=-1` (medido −0.7 dBTP): el
  AAC sube el pico 0.3–0.5 dB al codificar. Masterizar con `TP=-1.5`; `qa.sh` avisa del pico y del volumen alto (> −12.5 LUFS).
- **Arranque quieto**: `qa.sh` avisa si los primeros ≥ 0.4 s no se mueven (`freezedetect`), contrato del nivel 3 §1.

