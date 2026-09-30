# Guía de uso — qué pedir, con qué comando, y qué recibes

Esta guía es para **usar** la máquina, no para entenderla por dentro (eso está en `SKILL.md` y
`references/`). Cada apartado sigue el mismo orden:

1. **Qué es** — una descripción corta.
2. **Cómo se pide** — frases de ejemplo, tal cual se las dices al agente.
3. **Qué recibes, cuánto tarda y qué comando corre** — el detalle.

No hace falta nombrar el skill: el agente reconoce el pedido. Si quieres forzarlo, empieza con
`/edit-video`.

---

## 0 · Mapa rápido — "quiero…" → "uso…"

| Quiero… | Uso | Tiempo |
|---|---|---|
| Muchos clips rápidos de una entrevista o podcast | **Nivel 1** (clipper) | minutos |
| Esos clips con la línea gráfica de una marca | **Nivel 2** (clipper) | minutos |
| Una pieza de estudio con motion design sobre mi video | **Nivel 3** (HyperFrames) | horas |
| Lo del 3 + planos generados con IA, 3D, música | **Nivel 4** (propuesto) | días |
| Un video **sin grabar nada**: desde un audio, un guion o una idea | **Desde cero** (§5) | 10–60 min |
| Clips de una **carpeta entera** de grabaciones | **Modo lote** (§6.3) | minutos por video |
| Pasar una entrevista horizontal a vertical siguiendo al que habla | **`--fit auto`** (§6.4) | + segundos |
| Que me proponga los mejores momentos con puntaje | **Rúbrica** (§6.1) | segundos |
| Cambiar el diseño / cliente nuevo sin línea gráfica | **Shotgun de estilo** (§7) | 15–30 min |
| Saber cuánto va a tardar o cómo va | **Tiempos** (§8) | al momento |

Si no dices el nivel, el agente pregunta **una** vez: *"¿Nivel 1, 2 o 3? ¿O todos en 1–2 y los
mejores en 3?"*

---

## 1 · Nivel 1 · Recorte

**Qué es.** Clips limpios y rápidos de un video largo, para volumen: subtítulo palabra por palabra
(la palabra que se dice, en amarillo), gancho grande arriba los primeros 3 s, logo, audio
normalizado, vertical 9:16. Sale directo, sin aprobación de diseño.

**Cómo se pide.**
- *"Sácame clips de esta entrevista, nivel 1."*
- *"De este podcast dame los 8 mejores momentos en vertical, con subtítulos."*
- *"Nivel 1, y que siga al que habla."* (añade `--fit auto`)
- *"Córtale los silencios y tapa los subtítulos que ya trae el video."*

**Qué recibes.**
- Primero, la **propuesta de momentos** con puntaje y motivo (rúbrica, §6.1). Tú apruebas o ajustas.
- Luego, por clip: `NN-slug.mp4` (1080×1920, H.264, −16 LUFS) + `NN-slug-thumb.jpg` (miniatura).
- Aviso si un clip excede el límite de Reels (90 s), X (140 s), Shorts (180 s) o TikTok (600 s).

**Tiempo.** Transcribir ≈ 1/5 de la duración del video; render ≈ tiempo real del clip.

**Comandos** (`C=SKILL_DIR/clipper/clipper.py`):
```bash
python3 $C analyze entrevista.mp4                       # transcribe + candidatos con puntaje
python3 $C render entrevista.transcript.json clips.json --nivel 1
#   opciones: --fit auto | crop | blur   --tighten 0.35   --cover-subs 0.2   --no-thumbs
```

---

## 2 · Nivel 2 · Editorial

**Qué es.** Lo mismo que el 1, pero con **tipografía de estudio** (Inter Tight, Instrument Serif,
JetBrains Mono), paleta tinta/papel/acento, la palabra activa sobre una caja de color medida al
píxel, rótulo superior, barra de progreso, gancho en dos líneas y un grade suave. Es el nivel para
**marcas y clientes** que no necesitan motion. Sale directo.

**Cómo se pide.**
- *"Nivel 2 para el cliente X."* (usa su plantilla, colores y logo, sin preguntas)
- *"Nivel 2, gancho: Lo que | nadie te dice."* (la barra parte en serif + display)
- *"Otro igual al de la semana pasada."*

**Qué recibes.** Los mismos archivos que en el nivel 1, con la línea gráfica del cliente. La
miniatura usa la misma tipografía y el acento de la marca.

**Comandos.**
```bash
python3 $C render t.json clips.json --nivel 2 --cliente <slug> --fit auto
```
Por clip, en `clips.json`: `hook` (`"serif|DISPLAY"`), `titulo` (miniatura), `kicker` y `fuente`
(rótulo), `fit`, `crop_x`, `tighten`, `thumb_t`.

---

## 3 · Nivel 3 · Estudio

**Qué es.** Motion design de estudio **sobre tu video**: mapas, datos, palabras detrás de la
persona, recortes, profundidad 2.5D, cierre con personaje, diseño sonoro. Siempre avanzado. Se
construye en HyperFrames (el video se escribe como página web y se renderiza a MP4). **Nada se
construye sin tu OK a la propuesta.**

**Cómo se pide.**
- *"Nivel 3."* (intensidad 1, la de por defecto)
- *"Nivel 3 · intensidad 2 · énfasis recortes."*
- *"Nivel 3 · intensidad 3."* (primero te enseña una prueba animada de 5–10 s)
- *"Con el cierre congelado con recorte."* (usa la receta R1 del recetario, con sus tiempos exactos)
- *"De esta entrevista, todos en nivel 1 y los 2 mejores en nivel 3."*

**Las tres intensidades** (son un techo, no una cuota: si el video no da, te lo dice):

| | 1 · Profesional | 2 · Dinámico | 3 · Extremo |
|---|---|---|---|
| Cambio visual | cada 3–8 s | cada 2–4 s | cada 1–2 s |
| Sonido | uno por transición clave | en cada evento + subidas | capas densas al cuadro |
| Recortes de la persona | 1 (cierre) | 2–4 + texto detrás | en movimiento, gráficos delante y detrás |
| Aprobación | propuesta | propuesta + 2–3 cuadros | propuesta + prueba de 5–10 s |
| Tiempo | base | ×1.5–2 | ×3 |

**Énfasis** (dónde se gasta la carga extra): `recortes`, `efectos` o `datos`.

**Qué recibes.**
1. **Propuesta** (`*-PROPUESTA.md`): concepto en una frase, estilo, beat sheet cronometrado,
   gráficos únicos, imágenes a generar, sonido. **PARADA hasta tu OK.**
2. **Construcción** → preview → tus notas (una por línea, con el segundo) → versiones v1, v2…
3. **Revisor final** cuadro por cuadro antes de decir "listo", y entrega a −14 LUFS.

**Recetario** (`references/recetario-3.md`): efectos que ya salieron en videos aprobados, con
tiempos exactos. R1 · cierre congelado con recorte. R2 · congelado con palabra detrás (uno por pieza).
Se piden por su nombre.

**Comandos.**
```bash
python3 $C render t.json clips.json --nivel 3 --intensidad 2 --enfasis recortes --cliente <slug>
#   → corte limpio + PROPUESTA.md; con el OK, el agente construye con /edit-video (HyperFrames)
```

---

## 4 · Nivel 4 · Director *(propuesto)*

**Qué es.** Lo del nivel 3 **más lo que no se grabó**: planos generados con Seedance o Higgsfield
(la fábrica, el puerto, el producto), cámara 2.5D sobre fotos, objetos 3D, música cortada a la
imagen, 2–3 versiones del gancho y másters recompuestos en 9:16, 4:5 y 16:9.

**Cómo se pide.** *"Nivel 4: quiero ver la fábrica aunque no la grabamos."*

**Qué recibes.** Tres aprobaciones en lugar de una: **tratamiento**, **animatic** y **cada inserto
generado**. Gasta créditos. Detalle en `references/nivel-4.md`.

---

## 5 · Desde cero — sin video

**Qué es.** Una pieza animada **sin grabar nada**: tipografía cinética, formas, datos, collage
editorial, iconos, y figuras o fondos generados con Higgsfield. Mismo motor que el nivel 3
(HyperFrames: HTML → MP4), sin metraje. Hay tres puntos de partida:

| Partes de… | Qué pasa | Por qué es distinto |
|---|---|---|
| **Un audio** (nota de voz, locución, podcast) | Se transcribe con el tiempo de cada palabra y **cada animación cae en la palabra exacta** | Parece hecho a mano: la voz manda el ritmo |
| **Un guion** (texto) | Se corta en líneas de ≤ 5 palabras y se reparte en 4–7 beats | Tú controlas qué ideas entran |
| **Una idea** (una frase) | El agente escribe el guion, te lo enseña, y con tu OK sigue | Lo más rápido para empezar |
| **Una web** | Se lee la página y se saca el guion | Promos de producto |

**Cómo se pide.** Solo dos datos que el agente no puede adivinar: **duración** y **formato**.
- *"Con este audio hazme un video de 20 s, 9:16, estilo editorial."*
- *"Promo de 30 s, 16:9, de mi app. Guion: …"*
- *"Idea: una búsqueda del tesoro por la ciudad, 15 s vertical, que se sienta aventura."*
- *"Estilo como el del reel del hombre con tele en la cabeza: papel, círculo olivo, tipografía condensada."*

| Formato | Tamaño | Para |
|---|---|---|
| 9:16 | 1080 × 1920 | TikTok, Reels, Shorts, Stories |
| 1:1 | 1080 × 1080 | Feed, LinkedIn |
| 16:9 | 1920 × 1080 | Web, YouTube, presentaciones |

| Duración | Uso |
|---|---|
| 15–20 s | Redes (el punto dulce) |
| 30 s | Lanzamiento, portada de web |
| < 12 s | Se siente apurado |
| > 45 s | Necesita una historia de verdad |

**Qué recibes.**
1. **Beat sheet** en el chat: 4–7 beats con tiempo, tipo de plano y texto en pantalla. **Si la
   historia está mal, se dice aquí**, antes de construir.
2. **2–3 cuadros de prueba** para aprobar composición y estilo.
3. **`.mp4`** listo para publicar + **`.html`** editable (la animación como código: se puede abrir en
   el navegador, revisar cuadro a cuadro y cambiar textos y colores arriba del archivo).

**Tiempo.** 15–20 s ≈ 10–20 min de principio a fin (render cuadro por cuadro). Cada corrección
re-renderiza solo lo que cambió.

**Estilos.** Cada estilo aprobado se guarda como plantilla reutilizable (shotgun, §7). Primeros
candidatos: **editorial collage** (papel texturizado, círculo de color, condensada negra, figura en
blanco y negro recortada, marcas de registro) y **neón sobre negro** (vidrio oscuro, luz como sujeto,
espectro frío → cálido). Tu color de marca entra en el lugar principal de la paleta, no pegado encima.

**Cómo escribir un guion que anima bien** (lo que más decide si queda bueno):
- **Para el oído, no para la página.** Como se lo dirías a un amigo.
- **4–6 ideas como máximo.** 20 s aguantan unos 5 beats; si das 12, se eligen 5.
- **La primera línea es la más filosa.** El primer beat es el que la gente sí ve.
- **Fuera adjetivos.** "Potente, intuitivo, de clase mundial" no se anima. "Despliega en 9 segundos" sí.
- **Los números valen oro.** Un dato concreto tiene su propio tipo de plano (entra grande, con destello).

| Débil | Fuerte |
|---|---|
| *"Plataforma integral de nivel empresarial que optimiza la gestión."* | *"Encuentra la hora de junta que nadie odia. Lee todos los calendarios. 40 % menos juntas. Gratis hasta 10 personas."* |

**Qué skill construye cada caso** (el agente lo elige; los puedes pedir por nombre):

| Pedido | Skill de HyperFrames |
|---|---|
| Pieza corta de motion: titular cinético, contador, dato, mapa, logo | `/motion-graphics` |
| Explicativo sin cara, con voz | `/faceless-explainer` |
| Promo de producto / lanzamiento | `/product-launch-video` |
| Animado al ritmo de una canción | `/music-to-video` |
| Pieza larga o de varias escenas, montaje libre | `/general-video` |
| Presentación navegable (no MP4) | `/slideshow` |

**Estado:** el motor y los skills ya están instalados; la primera pieza desde cero con el estilo
editorial es la prueba que sigue. Al aprobarla, su estilo entra a la biblioteca.

---

## 6 · Herramientas de clipper

### 6.1 · Rúbrica de clipeabilidad
**Qué es.** Puntúa cada tramo del video de 0 a 10: gancho (0–3), dato concreto (0–2), remate (0–2),
se entiende solo (0–2), emoción (0–1). Es un pre-filtro: el agente lee, ajusta y propone; **decides tú**.

**Cómo se pide.** *"¿Cuáles son los mejores momentos?"* · *"Dame 8 candidatos de 20 a 45 s."*

**Qué recibes.** Tabla `puntaje · inicio → fin · primeras palabras · motivo` y `*.candidatos.json`.
```bash
python3 $C candidatos entrevista.transcript.json --min 20 --max 45 --top 8
```
Criterio completo: `references/clipeabilidad.md`.

### 6.2 · Miniaturas
**Qué es.** Una portada por clip: el cuadro más expresivo cerca del gancho + titular con la
tipografía de la plantilla.

**Cómo se pide.** Salen solas. *"Titular de la portada: Tres generaciones | haciendo ropa."*

**Qué recibes.** `NN-slug-thumb.jpg` (1080×1920; 1280×720 si es horizontal), ~1.3 s cada una.
`titulo` o `thumb_t` en el clip para fijarlas; `--no-thumbs` para no hacerlas.

### 6.3 · Modo lote
**Qué es.** Una carpeta de grabaciones → una propuesta por video → **tu OK** → render de lo aprobado.

**Cómo se pide.** *"Sácale clips a toda esta carpeta."*

**Qué recibes.** `LOTE.md` (resumen) y `<video>.clips.json` por video. Marca `"aprobado": true` en
los que quieras y el agente renderiza. Los videos casi sin voz (música, b-roll) salen como "poca voz".
```bash
python3 $C lote ~/grabaciones                                  # paso 1: propuestas
python3 $C lote ~/grabaciones --render --nivel 2 --fit auto    # paso 2: solo lo aprobado
```

### 6.4 · Recorte por cara / hablante activo
**Qué es.** Pasa un video horizontal a vertical **siguiendo la cara**; con dos personas, sigue al que
habla (por el movimiento de la boca) y corta seco al cambiar, como un editor.

**Cómo se pide.** *"Hazlo vertical y que siga al que habla."*

**Qué recibes.** El clip encuadrado solo. Si no hay caras o falta el entorno, cae a fondo difuminado
y lo dice. Límite: una cara **de perfil** no deja ver la boca y no gana el plano; el cambio de
hablante llega con 1–5 s de retraso.
```bash
python3 $C render t.json clips.json --fit auto
```
Instalación una vez (entorno aislado): ver `references/clipper.md` § Recorte por cara.

### 6.5 · Otras
| Qué | Cómo se pide | Comando |
|---|---|---|
| Bajar de YouTube, TikTok, X… | *"Baja este link y sácale clips"* | `$C fetch "<url>" --analyze` |
| Quitar silencios | *"Córtale los silencios"* | `--tighten 0.35` · `$C tighten t.json` |
| Nombres bien escritos para siempre | *"Es Hermosillo, no Ermosillo"* | `$C dict agregar "Ermosillo" "Hermosillo"` |
| Sin terminal | *"Ábreme el Studio"* | `python3 clipper/studio.py` (127.0.0.1:8791) |

---

## 7 · Shotgun de estilo — cambiar el diseño

**Qué es.** En vez de adivinar un diseño, se hacen **3 direcciones de verdad distintas** sobre tu
metraje real, las ves en un tablero y eliges. La elegida se vuelve la plantilla del cliente.

**Cómo se pide.** *"Cambio de diseño."* · *"Explora direcciones."* · *"Solo cambia la tipografía."*
(**"Otro igual"** no pasa por aquí: usa el kit del cliente tal cual.)

**Qué recibes.** 3 cuadros de estilo reales → eliges → plantilla guardada, y el sistema aprende tu
gusto. Detalle: `references/shotgun.md`.

---

## 8 · Tiempos — cuánto tarda y cómo va

**Qué es.** Cada trabajo terminado deja su tiempo real; con eso se estima el siguiente.

**Cómo se pide.** *"¿Cuánto va a tardar?"* · *"¿Cómo va?"*

**Qué recibes.** *"Estimado 46–71 min; referencias: …"* (los 2–3 trabajos más parecidos) y, en curso,
fase, % y hora estimada de fin.
```bash
python3 scripts/tiempos.py estimar --nivel 3 --intensidad 2 --tipo nuevo --duracion 51
python3 scripts/tiempos.py avance --log build.jsonl --nivel 3 --intensidad 2 --tipo nuevo
python3 scripts/tiempos.py ver
```

---

## 9 · Corregir — notas en lenguaje normal

**Regla:** una nota = un cambio, con el segundo. Qué, dónde, cuándo; nunca cómo.

| Dices | Qué cambia |
|---|---|
| *"El beat 3 va muy rápido"* | Ese beat se alarga; el resto se sostiene |
| *"Que resalte más"* | Más brillo y movimiento de color |
| *"Muy cargado"* | Menos objetos por beat, pausas más largas |
| *"Más frío" / "más cálido"* | Se mueve la paleta |
| *"Se ve trabado"* | Se corrige la curva de movimiento |
| *"Usa nuestro morado #6633EE"* | La paleta se rearma alrededor de tu color |
| *"Quita la escena del buscador"* | Se corta ese beat y se reparte el tiempo |
| *"Otra apertura"* | Cambia el primer plano |
| *"En el 0:12 el texto tapa la cara"* | Se mueve ese elemento, se revisa ese cuadro |

Cada ronda se versiona (v1, v2…) y se re-renderiza solo lo que cambió.

---

## 10 · Problemas comunes

| Pasa | Qué hacer |
|---|---|
| No arrancó el skill | Di *"usa /edit-video para…"* |
| Salió plano comparado con los ejemplos | Casi siempre es el modelo: usa el más fuerte (Opus). Luego, afila el guion (§5) |
| Solo llegó el `.html` | Es la animación completa; ábrelo en el navegador. Pide *"ahora renderízalo a MP4"* |
| Lleva 10 minutos | Normal en nivel 3 y desde cero: se pintan cientos de cuadros. Pregunta *"¿cómo va?"* |
| Eligió las partes equivocadas | Dile cuáles querías, o dale un guion más corto |
| Colores que no son de la marca | Pasa los hex: *"usa #6633EE y #00D4A0"* |
| Subtítulos con nombres mal escritos | Corrígelo una vez; queda en el diccionario para siempre |
| El vertical no sigue a la persona | `--fit auto`; si está de perfil, `crop_x` a mano |

Más: `references/troubleshooting.md`.
