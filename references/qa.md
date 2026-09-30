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
  `ffmpeg -i in.mp4 -c:v copy -af "highpass=f=70,equalizer=f=3000:t=q:w=1.2:g=2.5,acompressor=threshold=-22dB:ratio=2.5:attack=8:release=120:makeup=2,loudnorm=I=-14:TP=-1:LRA=7" -c:a aac -b:a 256k out.mp4`
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
