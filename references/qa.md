# Revisor final — nadie entrega sin pasar esto

El agente que construye **no es el que aprueba.** Antes de decir "listo", el agente se pone en el
papel de un revisor que quiere rechazar el trabajo, y revisa **el MP4 renderizado**, no el preview.

## 1 · Sacar el video entero

```bash
bash <SKILL_DIR>/scripts/qa.sh final.mp4 2  1 3 <tiempos clave…>
```

- Hojas de contacto con un cuadro cada **0.5 s** de todo el video.
- A tamaño completo: el primer segundo, cada transición, cada entrada de texto grande, el cierre.
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

- Titular de cierre partido en dos líneas: `COLOMBI` / `A.`
- Medio logo de la fuente asomando por el borde de un recuadro
- Micro-etiquetas mono finas sobre metraje: ilegibles en el teléfono
- Un mapa "estilizado" que parecía un garabato → siempre geometría real (Natural Earth)
- Una banda negra del 20 % de la pantalla con solo una palabra: zona muerta
- Subtítulos quemados del original asomando durante un zoom
