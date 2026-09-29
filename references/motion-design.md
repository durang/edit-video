# Motion design — cuando el montaje tiene que parecer de estudio

Lo que separa un montaje correcto de uno "de 15 000 al mes" no es meter más cosas: es que **todo
responde al mismo sistema**, que hay **profundidad**, que **suena**, y que **cierra con una firma**.
Todo esto salió de piezas reales revisadas cuadro a cuadro (un reel de entrevista 16:9 → 9:16, de v1 a v5).

## 1 · Sistema de coherencia — antes de animar nada

Declara constantes en la composición y úsalas en **todas** las animaciones. Cero valores sueltos.

```js
const IN   = { ease: "expo.out",    d: 0.55 };   // todo lo que entra
const OUT  = { ease: "power2.in",   d: 0.25 };   // todo lo que sale (más rápido que entrar)
const MOVE = { ease: "expo.inOut",  d: 0.80 };   // paneos, cambios de encuadre, reubicaciones
const STAGGER_CHAR = 0.018, STAGGER_WORD = 0.06; // escalonados
const M = 64;                                    // margen único
```

- **Una sola clase para pastillas/chips** (`.pill`): mismo papel, tinta, mono ≥ 24 px, mismo padding
  y radio. Si hay dos estilos de pastilla, parece hecho por dos personas.
- **Cada bloque del mismo tipo entra y sale igual.** Lo revisa el revisor final comparando hojas de
  contacto: si un titular entra por letras y el siguiente por palabras sin motivo, es un defecto.
- **Paleta cerrada**: papel, tinta, un acento (y como mucho uno secundario). Nada de colores nuevos a mitad.

## 2 · Mapas

Un mapa mal hecho delata al instante. Reglas:

- **Datos reales**: Natural Earth (`ne_50m_admin_0_countries`; 110 m solo para países enteros
  pequeños en pantalla). Nunca un contorno dibujado a mano ni generado por IA.
- **Precalcula a píxeles** (proyección equirectangular o la que toque, ventana lon/lat explícita) en
  un script (`tools/genmap.cjs`) y escribe los `d` finales. **Sin `transform: scale` sobre el path.**
- **Para dibujar un trazo: `pathLength="1"`** y anima `stroke-dashoffset` de 1 a 0. Con
  `getTotalLength()` sobre un path escalado el trazo termina en fragmentos sueltos (error real: el
  contorno final quedó roto y el revisor del constructor no lo vio).
- **Ciudades en coordenadas reales**, etiqueta en `.pill` con línea guía de 1 px. **Ninguna etiqueta
  se solapa** con otra, con el país resaltado ni con la cara.
- **Arcos** entre ciudades: se dibujan (`pathLength="1"`) y después un punto recorre cada arco una vez,
  escalonados. Eso cuenta la historia ("de aquí a allí") sin texto.
- **Retícula tenue** (≈6 % de tinta) y fronteras finas: el país protagonista es el único con color.
- **Tamaño contenido** (≈ un tercio del ancho en vertical) y **entra cuando el encuadre ya se movió**
  para hacerle sitio — nunca a la vez que el paneo, nunca encima de la cabeza.

## 3 · Hacer sitio — el encuadre se mueve para el gráfico

En 9:16 desde 16:9 no hay sitio para gráficos junto a una cara centrada. En vez de encoger el gráfico:
**panea el metraje** (`MOVE`) para dejar a la persona a un lado, y **después** entra el gráfico en el
hueco. Keyframes de encuadre por tramo (`txFor(t)`), cara siempre dentro de la safe zone.

## 4 · Profundidad — palabras detrás de la persona

Una palabra grande **entre el fondo y la persona** es el efecto más "de estudio" que hay.

- Mate de la persona con `npx hyperframes remove-background` sobre **ese tramo**, con **el mismo
  recorte y los mismos keyframes de encuadre** que el metraje, para que case al píxel.
- Capas: metraje → **palabra** → **persona (mate)** → resto de la interfaz. Solo la palabra grande
  va detrás; los chips secundarios, delante.
- La cabeza/pelo tapa **como máximo un 30 %** de las letras: se tiene que leer entera.
- **Si el mate parpadea o deja halo** en las hojas de contacto a 0.5 s, se quita el efecto. Mejor sin
  efecto que con un efecto sucio.

## 5 · Fondos y texturas generados

Para texturas, fondos de cierre o ilustraciones (nunca texto ni logos — ver `pipeline.md`):

- Genera con el modelo de imagen disponible (p. ej. Higgsfield `generate_image`). Pide **la mitad
  superior vacía** si va a llevar título encima, y el estilo de la pieza (tinta sobre papel, etc.).
- Como textura, **opacidad baja (≈0.10–0.15)** con degradado de desvanecimiento y deriva lenta. Nunca
  puede bajar el contraste de subtítulos ni chips (compruébalo con `npx hyperframes check`).

## 6 · El cierre con personaje — la firma

El último plano es el que se recuerda. Receta probada:

1. **Congela** el último cuadro (suena un obturador).
2. **Recorta a la persona** de ese cuadro (Higgsfield `remove_background` o
   `npx hyperframes remove-background`) y colócala **alineada al píxel** con la capa de video
   (misma escala y desplazamiento que tenía en ese instante). El fondo del cuadro se va con una
   máscara desde los bordes y queda ella sobre papel.
3. **Un fondo generado sube detrás** (`MOVE`) con **parallax**: se mueve más lento que ella.
4. **Ella se desplaza** (escala ~1 → 0.8 anclada abajo, hacia un lado) con **sombra de contacto**.
5. Titular y líneas en el hueco libre, escalonados; emblema (contorno con `pathLength="1"`).
6. Créditos pequeños **por encima de la safe zone inferior**, sin tocarla.
7. **Push lento hasta el último cuadro** (fondo 1.00→1.03, ella 1.00→1.015). Nada estático al final.

## 7 · Diseño sonoro

Cada transición y cada elemento que entra con intención tiene un sonido. Sin sonido, el motion se
siente "de plantilla".

- **Fuente**: primero `/media-use` de HyperFrames. Si no hay, **sintetiza con FFmpeg** (ruido
  filtrado para papel y whoosh, barridos de paso banda, clics de seno, golpes graves con caída) y
  guárdalos en `assets/sfx/`.
- **Higgsfield `generate_audio` solo genera voz**: no sirve para SFX ni música.
- **La voz manda**: picos de SFX nunca por encima de **−16 dBFS**; la mayoría entre −28 y −22.
- **Nunca el mismo sonido dos veces seguidas**: varía tono ±2 semitonos o la muestra.
- Mapa típico: papel (entra un marco) · pop (chip) · lápiz (flecha/trazo) · whoosh (transición grande,
  pico en el corte) · golpe grave (palabra clave) · tic (cada ítem de una lista) · sello (remate) ·
  obturador (congelado) · aire (fondo que sube) · tono grave con caída (cierre).
- **Verifícalo**: `ffmpeg -ss T -t 0.6 -i final.mp4 -af volumedetect -f null -` en cada evento.

## 8 · Reparto de trabajo con dos agentes

- **Director de arte / revisor** (el que tiene el criterio): escribe el brief con tiempos exactos,
  genera los assets, y revisa con `scripts/qa.sh` (hojas cada 0.5 s + cuadros completos + el último).
- **Constructor** (el agente con HyperFrames en la máquina): construye, hace su propia revisión y
  renderiza. **El que construye no aprueba.**
- Cada ronda de notas: un archivo `QA_RONDAn.md` con "tiempo · qué · dónde", nunca "cómo".
