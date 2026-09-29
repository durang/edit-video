# Prompts listos para pegar

Se manda **uno cada vez**. Los `[corchetes]` se cambian.

---

## El primero de todos — oídos y ojos

> Mi video es `take.mp4` en esta carpeta. Transcríbelo con `npx hyperframes transcribe` y el
> modelo multilingüe `small` (hablo en español, nunca un modelo `.en`), con un timestamp para
> cada palabra, y guarda las palabras y los tiempos en `take.words.json`. Luego usa FFmpeg para sacar
> un fotograma por segundo y mira los fotogramas. Dime qué digo, cuándo lo digo y qué hay en el
> plano en cada momento. Estos nombres tienen que estar bien escritos: `[tu nombre, marca, producto]`.

## El segundo — el plan, antes de construir nada

> Antes de construir nada, escribe el beat sheet de este montaje como tabla: inicio y fin, mis
> palabras exactas, qué aparece en pantalla, dónde se coloca el texto, y el sonido.
> Formato: vertical 9:16 para Reels. Nada de texto en el 20% inferior de la pantalla ni pegado
> al borde derecho, donde van los botones de la app. Espera mi OK antes de construir.

---

## Montajes de diario

Estos suelen salir a la primera.

**Subtítulos** — por donde se empieza
> Añade subtítulos palabra por palabra, sincronizados con la transcripción. Dos o tres palabras
> en pantalla a la vez, en negrita y blanco, con la palabra clave de cada frase en `[color]`.
> Colócalos a la altura del 65% de la pantalla.

**Cortar el aire muerto** — después de la transcripción
> Corta cada pausa de más de 0.3 segundos y cada respiración, usando los tiempos de las palabras.
> Nunca cortes dentro de una palabra, y deja un beat corto antes de cada remate.
> Dime la duración nueva.

**Punch-in zooms** — pocos
> Acércate 1.2x en la palabra clave de cada frase, mantén dos segundos y sal suavemente.
> No más de un zoom cada cinco segundos.

**Título de apertura + placa de nombre**
> Abre con un título en tipografía grande y gruesa: "`[tu gancho]`". Mantenlo dos segundos y corta
> a mí. Añade un rótulo inferior con mi nombre y `[@handle]` la primera vez que hablo.

**Pop-ups** — la imagen en la carpeta
> Cuando diga "`[palabra]`", saca `[imagen.png]` a mi lado durante dos segundos con un rebote
> pequeño. Nunca debe taparme la cara.

**Música y efectos** — los archivos en la carpeta
> Pon `[musica.mp3]` bajo mi voz a volumen bajo, y bájala más mientras hablo. Pon un whoosh en
> cada zoom y un pop en cada pop-up, usando los archivos de la carpeta `sfx`.
> Nunca el mismo sonido dos veces seguidas.

**Reencuadrar para Reels** — para tomas horizontales
> Reencuadra este video de 16:9 a 9:16 para Reels y mantén mi cara centrada todo el tiempo.

**Lotes** — un montaje, tres idiomas
> Haz tres versiones de este montaje con el mismo timing y el mismo estilo: subtítulos en español,
> en inglés y en portugués. Traduce solo los subtítulos, conserva mi voz, y renderiza las tres.

---

## Montajes para lucirse

Piden más preparación y son los que se comparten. Cada línea entrecomillada se dice **en cámara**,
tal cual. El agente la encuentra en la transcripción y construye el efecto en esa palabra exacta.

**Objeto 3D en la mano**
> *"Haz zoom en mi mano y pon el logo aquí, en 3D."* → *"¡Ahora lánzalo a la cámara!"*
Construye: punch-in en la mano, el logo como objeto 3D real apoyado en la palma, y luego volando
hacia la lente con un cristal que se rompe.
**Necesitas:** el logo (SVG o PNG) en la carpeta, y la mano abierta quieta un segundo.

**Separar la escena en capas**
> *"Ahora separa la escena en capas: la pared, yo, y el texto."* → *"Ahora esconde mi capa."* →
> *"Vale, tráeme de vuelta."*
Construye: un recorte tuyo (`npx hyperframes remove-background`) separado de la sala vacía, con el
texto en medio. Escondes tu capa y la sala vacía sigue hablando con tu voz.
**Necesitas:** los 2 segundos de clean plate, y distancia a la pared.

**Marco + explicativo al lado**
> *"Ponme en un marco a la derecha, y a la izquierda enseña cómo un reel se hace viral."*
Construye: tú encoges dentro de un marco mientras a la izquierda se construye un explicativo
animado —títulos, iconos y una gráfica— sincronizado con lo que dices después.
**Necesitas:** un tema claro y 2 o 3 puntos cortos que digas justo después.

**Tus videos flotando detrás**
> *"Vuelve a pantalla completa. Ahora haz flotar mis mejores reels detrás de mí, en 3D."*
Construye: tu recorte delante, tus videos reproduciéndose en pantallas 3D flotando detrás.
**Necesitas:** los videos en una carpeta. El agente elige los 3 o 4 segundos más visuales de cada uno.

**Un objeto real que cobra vida**
> *"La última: coge la cámara de mi estante y ábrela."* → *"Ahora devuélvela... ¡y hazme una foto!"*
Construye: el objeto real recortado del plano, volando del estante, reconstruido en 3D y abierto
en sus piezas. Luego un flash, y una foto hecha con un fotograma real tuyo.
**Necesitas:** un segundo clean plate sin el objeto, y una pose en "foto".

---

## Por qué funcionan

Dos cosas: **cada efecto cae en la palabra exacta**, y **cada efecto tiene un giro** — el logo se
lanza, tú desapareces, la cámara te hace una foto. **Pide un giro para cada efecto que añadas.**
