# /edit-video

<!-- GUIA:inicio -->
<!-- generado por scripts/guia.py desde GUIA.md: no editar a mano -->
## Guía rápida · v3.11.1

Qué pedir y qué usar. **Guía completa** — cada nivel y herramienta con descripción, frases de ejemplo, qué recibes, tiempo y comando: [GUIA.md](GUIA.md)

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

Contenido: §0 Mapa rápido · §1 Nivel 1 Recorte · §2 Nivel 2 Editorial · §3 Nivel 3 Estudio · §4 Nivel 4 Director · §5 Desde cero · §6 Herramientas de clipper · §7 Shotgun de estilo · §8 Tiempos · §9 Corregir · §10 Problemas comunes
<!-- GUIA:fin -->

**Una máquina de edición profesional, con cualquier agente.** Cuatro niveles:

| Nivel | Qué sale | Cuánto tarda |
|---|---|---|
| **1 · Recorte** | Clips limpios de un video largo: subtítulo palabra por palabra, gancho, logo | minutos |
| **2 · Editorial** | Lo mismo con tipografía de estudio, paleta, caja en la palabra activa, rótulo, barra de progreso y grade | minutos |
| **3 · Estudio** | Motion design avanzado (mapas, profundidad, datos, cierre con personaje, diseño sonoro), con propuesta aprobada antes. **Tres intensidades**: 1 Profesional · 2 Dinámico · 3 Extremo | horas |
| **4 · Director** *(propuesto)* | Lo del 3 + planos generados con IA, 3D y música a la imagen | días |

**¿Qué pido y cómo?** → [`GUIA.md`](GUIA.md): cada nivel con descripción, frases de ejemplo, comandos y qué recibes — incluido el modo **desde cero** (sin video: desde un audio, un guion o una idea).

Los niveles 1–2 los hace `clipper/` (FFmpeg, sin dependencias); el 3–4, HyperFrames. Detalle:
[`references/niveles.md`](references/niveles.md) · contrato del nivel 3: [`references/nivel-3.md`](references/nivel-3.md).

### Cómo pedirlo

| Dices… | Pasa esto |
|---|---|
| *"sácame clips de esta entrevista, nivel 1"* | clipper puntúa los momentos (rúbrica de clipeabilidad), te propone los mejores con su motivo y, con tu OK, los corta con subtítulo, logo y **miniatura** |
| *"con este audio hazme un video de 20 s, 9:16, estilo editorial"* | **Desde cero**: beat sheet → tu OK → cuadros de prueba → `.mp4` + `.html` editable ([GUIA §5](GUIA.md)) |
| *"sácale clips a toda esta carpeta"* | **Modo lote**: una propuesta por video, apruebas, y renderiza solo lo aprobado |
| *"hazlo vertical y que siga al que habla"* | `--fit auto`: detecta las caras y corta al hablante activo (MediaPipe, instalado aparte en un entorno aislado) |
| *"nivel 2"* | Lo mismo con la línea editorial del cliente (su plantilla) |
| *"nivel 3"* | Propuesta de motion design → **tu OK** → construcción → revisor cuadro a cuadro. Sin decir intensidad, es la **1** |
| *"nivel 3 · intensidad 2"* | Más cargado: un cambio visual cada 2–4 s, sonido en cada evento, 2–4 recortes de la persona, profundidad 2.5D |
| *"nivel 3 · intensidad 3"* | Extremo, el de *"¿qué es eso?"*: cambio cada 1–2 s, diseño sonoro denso, recorte en movimiento, 3D. Primero una prueba de 5–10 s para aprobar |
| *"… · énfasis recortes"* (o `efectos`, o `datos`) | Dónde se gasta la carga extra |
| *"con el cierre congelado con recorte"* | Usa una receta probada del [recetario](references/recetario-3.md), con sus tiempos exactos |
| *"otro igual para este cliente"* | Parte de su kit y su plantilla, sin preguntas |
| *"cambio de diseño"* / cliente nuevo | **Shotgun de estilo**: 3 direcciones reales sobre tu metraje, eliges en un tablero ([`shotgun.md`](references/shotgun.md)) |

| Intensidad del 3 | Cambio visual | Sonido | Recortes de la persona | Tiempo |
|---|---|---|---|---|
| **1 · Profesional** | cada 3–8 s | uno por transición o gráfico clave | 1 (cierre) | base |
| **2 · Dinámico** | cada 2–4 s | cada evento + subidas antes de los cambios | 2–4 + texto detrás de ella | ×1.5–2 |
| **3 · Extremo** | cada 1–2 s | capas densas al cuadro | en movimiento, gráficos delante y detrás | ×3 |

El freno de todas: **la voz se entiende siempre**; si un efecto tapa lo que se dice, se quita.

**¿Cuánto va a tardar?** Antes de empezar, el agente te da un estimado con los 2–3 trabajos más
parecidos que ya hizo (*"estimado 46–71 min; la última subida de intensidad tardó 40"*), y si preguntas
*"¿cómo va?"* te dice la fase, el % y la hora estimada de fin. Cada trabajo terminado afina el
siguiente estimado (`scripts/tiempos.py`).

**El recetario** ([`references/recetario-3.md`](references/recetario-3.md)) guarda cada efecto que
salió en un video aprobado: qué es, cuándo, tiempos exactos, activos, fallas y su arreglo. Los
ejemplos que te gusten entran en "Por probar" y suben a receta cuando se prueban. Cada video lo
hace más grande.

**Monta videos que ya existen, con cualquier agente.** Subtítulos, cortar silencios, zooms,
rótulos, gráficos encima, música, reencuadre a vertical, recorte de fondo, objetos 3D, estilos con
nombre — y unir clips generados con IA en una pieza terminada.

No genera video. Monta el que ya tienes.

Funciona en **Claude Code, OpenClaw, Hermes Agent, Codex, Cursor, Gemini CLI** y cualquier agente
que lea skills en formato `SKILL.md`.

## Instalar

### Si eres una persona


```bash
git clone https://github.com/durang/edit-video && cd edit-video && bash install.sh
```

Detecta tus agentes, instala el skill, **y el skill instala todo lo demás** que le falte:
[HyperFrames](https://github.com/heygen-com/hyperframes), FFmpeg, Node, whisper-cpp y el modelo de
Whisper. Te enseña el plan y te pide permiso antes de instalar nada.

### Si eres un agente (o se lo pasas a uno)

Pégale esto a Claude Code, OpenClaw, Hermes o el que uses:

> Instala el skill de https://github.com/durang/edit-video con
> `npx skills add durang/edit-video -g -y`. Luego corre
> `bash ~/.agents/skills/edit-video/scripts/setup.sh`, enséñame el plan que imprima y pídeme
> permiso antes de instalar. Cuando esté en verde, usa el skill edit-video para editar mi video.

Eso es todo: el skill trae su propio instalador y su propia comprobación. Detalle y Windows: [`references/setup.md`](references/setup.md).

## Usar

Abre tu agente en la carpeta de tu video y di:

```
/edit-video mi-video.mp4 — subtítulos, córtale los silencios y hazlo vertical para Reels
```

o en lenguaje normal: *"edita mi-video.mp4, ponle subtítulos y quítale las pausas"*.

La primera vez te hace **seis preguntas** (idioma, cómo se escribe tu nombre, dónde publicas,
colores, tipografía, logo) y guarda tus reglas en `AGENTS.md`. Nunca más las repites.

Luego, siempre igual:

1. **Escucha y mira** — transcripción con el tiempo de cada palabra, y fotogramas
2. **Te enseña el plan** (beat sheet) y **espera tu OK**
3. **Rough cut** — fuera silencios y respiraciones
4. **Construye** — cada efecto anclado a una palabra
5. **Preview** — le das notas con el tiempo: *"en 0:07 el logo me tapa la cara"*
6. **Render** — MP4 final, local o en la nube
7. **Revisor final** — el video entero, cuadro cada 0.5 s: ninguna palabra partida, nada tapado, nada ilegible

## Cómo se mantiene al día

Cada entrega cierra con una **retro** de tres preguntas (sin gastar en búsquedas). Lo que no sale bien
va a [`LIMITACIONES.md`](LIMITACIONES.md). **Cada 2 semanas un radar** revisa si algo nuevo resuelve
esas limitaciones, qué cambió en las herramientas, y el estado del arte de los niveles 2 y 3.
Implementa lo obvio (probado); lo demás lo propone para aprobación. Detalle: [`references/mejora-continua.md`](references/mejora-continua.md).

## Área de clientes y autoaprendizaje

Son **dos repos**:

| | Qué guarda | |
|---|---|---|
| **`edit-video`** (este) | El método y todo lo aprendido que sirve para **cualquier** video | público |
| **`edit-video-clients`** | Por cliente: reglas (`CLIENTE.md`), kit de diseño, aprendizajes, historial | **privado** |

```bash
bash install.sh --clients git@github.com:TU_USUARIO/edit-video-clients.git
```

El agente lo hace solo: **al empezar** (`sync.sh pull`) trae lo último de los dos y lee al cliente
antes del beat sheet; **al entregar** (`sync.sh push`) guarda lo general aquí y lo del cliente en el
privado. Un guardia impide que un dato de cliente llegue al repo público. Así cada video sale mejor
que el anterior, y el segundo de un mismo cliente parte de su kit. Detalle: `references/aprendizaje.md`.

## ¿Tiene que estar prendido mi ordenador?

Corre **donde corre el agente**:

| Tu agente está… | ¿Ordenador prendido? |
|---|---|
| En tu Mac o PC (Claude Code, OpenClaw o Hermes local) | **Sí** |
| En un servidor (OpenClaw o Hermes en un VPS, por Telegram o WhatsApp) | **No** — corre en el servidor |
| En una app de chat sin terminal | No puede correrlo |

El render pesado también puede irse a la nube de HeyGen: `npx hyperframes cloud render`.

## Por qué funciona

Un agente no puede ver un video. Así que se le dan **oídos** (Whisper: cada palabra con su tiempo)
y **ojos** (FFmpeg: fotogramas). Con eso **cada efecto cae en una palabra exacta**, no en un segundo
adivinado. Es lo que separa un montaje hecho a mano de una plantilla.

## Contenido

| | |
|---|---|
| `SKILL.md` | El método, los pasos y las reglas duras |
| `install.sh` | Instala en todos tus agentes |
| `scripts/setup.sh` | **El skill se instala lo que le falta**: plan, permiso, instalación, comprobación |
| `scripts/check.sh` | Comprueba que no falte nada |
| `scripts/ingest.sh` | Oídos y ojos en un comando, con el idioma bien puesto |
| `scripts/qa.sh` + `references/qa.md` | **Revisor final**: el video entero cuadro a cuadro antes de entregar |
| `templates/AGENTS.md.template` | Tus reglas de marca |
| `references/onboarding.md` | Las seis preguntas de la primera vez |
| `references/setup.md` | Instalación en detalle |
| `references/routing.md` | Qué skill de HyperFrames construye cada cosa |
| `references/pipeline.md` | Combinar con Seedance, Grok, Veo, Kling: generar → montar |
| `references/film-it-right.md` | **Cómo grabar una toma editable — léelo antes de grabar** |
| `references/prompts.md` | Pedidos listos, de diario y para lucirse |
| `references/styles.md` | Copiar un estilo |
| `references/clipper.md` | Video largo → muchos clips: clipper para volumen, aquí para los mejores |
| `scripts/tiempos.py` | Estimados con trabajos parecidos, avance en %, registro de tiempos reales |
| `scripts/diccionario.py` | Diccionario permanente de nombres: una corrección, para siempre |
| `references/aprendizaje.md` + `scripts/sync.sh` | Área privada de clientes y autoaprendizaje en dos repos |
| `references/niveles.md` | Los 4 niveles: qué es cada uno, comandos, quién lo corre |
| `references/nivel-3.md` | **Contrato del nivel 3**, intensidades, tiempos y curvas, técnicas, lo que ya no se hace |
| `references/recetario-3.md` | **Recetario**: efectos probados con tiempos exactos, y ejemplos por probar |
| `references/shotgun.md` | Shotgun de estilo: 3 direcciones, tablero, la elegida se vuelve plantilla |
| `references/nivel-4.md` | Nivel 4 · Director (propuesto) |
| `LIMITACIONES.md` | Lo que aún no sale bien, con su arreglo provisional y qué lo resolvería |
| `references/motion-design.md` | Nivel estudio: coherencia, mapas, profundidad, cierre con personaje, sonido |
| `references/troubleshooting.md` | Defecto → arreglo |

## Si hablas español (o cualquier idioma que no sea inglés)

El modelo de Whisper por defecto de HyperFrames es **solo inglés** (`small.en`). Prueba real, el
mismo audio en español:

| | Resultado |
|---|---|
| `hyperframes transcribe audio.wav` | *"We are going to do this for you, for you to do what you want, for you to do what you want…"* |
| `hyperframes transcribe audio.wav -l es` | *"Trabajamos para que tú estés seguro, para que duermas tranquilo, para que tengas la seguridad de que tu propiedad va a estar en buenas manos."* |

Sin el idioma, **inventa**. Este skill siempre le pasa el idioma. A mano: `-l es`.

## English

`/edit-video` edits footage that already exists — captions, dead-air cuts, zooms, overlays, music,
reframing, background removal — in any agent that reads `SKILL.md` skills, on top of HyperFrames.
Install with `bash install.sh`. Docs are in Spanish; the skill works in any language.

## Crédito

Método: **"Let Claude Edit Your Videos"**, [@pauloshimas](https://github.com/aipauloshimas) · The
Creator Stack (2026). Motor: **HyperFrames**, de HeyGen. Skill: Sergio Duran. MIT.
