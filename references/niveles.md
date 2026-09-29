# Niveles — una sola máquina de edición

Todo pedido de edición cae en un nivel. **El nivel lo elige el usuario** (una pregunta al empezar
si no lo dijo); el agente recomienda. Cada nivel tiene **su motor, su línea de diseño y su puerta
de aprobación**.

| Nivel | Nombre | Motor | Línea de diseño | Tiempo | Puerta |
|---|---|---|---|---|---|
| **1** | **Recorte** | `clipper/` (FFmpeg + libass) | Blanco con contorno, palabra activa en amarillo, gancho arriba, logo | minutos | ninguna: sale |
| **2** | **Editorial** | `clipper/` (FFmpeg + libass) | Tipografía de estudio (Inter Tight · Instrument Serif · JetBrains Mono), paleta tinta/papel/acento, palabra activa sobre caja, rótulo, barra de progreso, gancho en dos líneas, grade | minutos | ninguna: sale |
| **3** | **Estudio** | HyperFrames (este skill) | Motion design de estudio: ver `nivel-3.md` — **siempre avanzado** | horas | **propuesta aprobada** antes de construir |
| **4** | **Director** *(propuesto)* | HyperFrames + generativos (Seedance, Higgsfield) | Pieza de autor: insertos generados, cámara 2.5D/3D, música a medida — ver `nivel-4.md` | días | **tratamiento aprobado** + aprobación de cada inserto |

## Cómo se elige

> ¿Nivel 1 (recorte limpio), 2 (editorial) o 3 (estudio)? ¿O combinados: todos en 1–2 y los mejores en 3?

- **Volumen** (una entrevista → 20 clips): 1 o 2.
- **Marca / cliente, sin motion**: 2.
- **Pieza que representa a alguien** (reel de marca, lanzamiento, el clip estrella): 3.
- **Pieza de autor** con escenas que no existen en el metraje: 4.

## Comandos

```bash
C=SKILL_DIR/clipper/clipper.py
python3 $C analyze largo.mp4                                     # idioma detectado, diccionario aplicado
python3 $C render largo.transcript.json clips.json --nivel 1     # Recorte
python3 $C render largo.transcript.json clips.json --nivel 2 --cliente <slug> --fit crop
python3 $C render largo.transcript.json clips.json --nivel 3 --cliente <slug>   # corte limpio + PROPUESTA.md
python3 SKILL_DIR/clipper/studio.py                              # lo mismo con interfaz web (127.0.0.1:8791)
```

`clips.json`: `start`, `end`, `slug`, y opcionales `hook` (`"serif|DISPLAY"` en nivel 2), `kicker`,
`fuente`, `fit`, `crop_x`, `tighten`, `cover_subs`, `why`. **Los momentos los elige el criterio**
(el agente propone con su `why`, decide el humano), nunca una heurística de volumen.

Nivel 3 sobre un video que ya es corto (no hay que cortar): directo al Paso 3 de `SKILL.md`, con la
propuesta de `nivel-3.md`.

## Quién puede correr cada nivel

| | Agente solo | Necesita |
|---|---|---|
| 1 y 2 | Sí, de principio a fin | Python 3, FFmpeg **con libass**, Whisper (o una transcripción ya hecha) |
| 3 | Construye solo; **el director aprueba la propuesta y revisa** | Lo de 1–2 + Node 22, HyperFrames, Chrome headless |
| 4 | Construye solo; **el director aprueba tratamiento e insertos** | Lo de 3 + acceso a Seedance / Higgsfield (créditos) |

Todos pasan por el **revisor final** (`scripts/qa.sh`) y dejan **aprendizaje** (Paso 9): lo general
aquí, lo del cliente en su carpeta privada (`edit-video-clients`, incluida su plantilla
`clipper.json` para los niveles 1–2 y su kit para el 3–4).
