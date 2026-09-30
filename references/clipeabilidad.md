# Rúbrica de clipeabilidad — qué momento merece ser clip

`clipper` no elige los momentos: **propone**. La rúbrica tiene dos capas:

1. **Pre-filtro automático** (`clipper/rubrica.py`): `analyze` la corre al terminar y `candidatos` la
   corre sobre cualquier transcripción (la de `analyze` o la `transcript.json` de `ingest.sh`). Puntúa
   ventanas de frases completas (15–60 s por defecto) de 0 a 10, quita las que se solapan y deja
   `<video>.candidatos.json` en el formato de `clips.json`, con `why` = puntaje + motivo.
2. **Criterio del agente** (esta hoja): el agente lee los mejores candidatos **y la transcripción
   completa**, aplica los mismos cinco ejes con juicio, ajusta los cortes, escribe el `hook` y
   propone. **Decide el humano.** El pre-filtro solo cuenta palabras: no entiende ironía, contexto
   ni si el dato es falso.

```bash
python3 clipper/clipper.py analyze entrevista.mp4             # transcribe + candidatos
python3 clipper/clipper.py candidatos entrevista.edit/transcript.json --min 20 --max 45 --top 8
```

## Los cinco ejes (0–10)

| Eje | Puntos | Qué mira | Señales (ES / EN) |
|---|---|---|---|
| **Gancho** | 0–3 | Los primeros ~3.5 s paran el scroll | pregunta · negación directa ("no te…", "deja de…") · dato en la apertura · "nadie / nunca / error / secreto / por qué" · hablarle a *tú* |
| **Dato** | 0–2 | Historia con número o hecho concreto | cifras, %, $, "tres", "la mitad", "el doble" |
| **Remate** | 0–2 | Cierra: conclusión, giro o frase redonda | termina en punto · "por eso / así que / la clave / al final" · "pero / en realidad / resulta que" en la segunda mitad |
| **Autonomía** | 0–2 | Se entiende sin lo de antes | resta si arranca con "y / pero / eso / entonces / porque" o a media frase |
| **Emoción** | 0–1 | Hay algo en juego | exclamación, "increíble / brutal / miedo / frustra…" |

Lectura rápida: **7+** candidato fuerte · **5–6** vale si el agente le arregla el arranque o el
remate · **≤4** solo si el tema lo pide.

## Lo que el agente hace encima del pre-filtro

- **Mover los bordes**, no aceptar los del pre-filtro: empezar en la frase que plantea la tensión,
  terminar un beat después del remate. Nunca a media palabra.
- **Escribir el `hook`** (texto grande de los primeros 3 s): máximo 5–6 palabras, la promesa del
  clip, no la primera frase copiada.
- **Descartar** lo que puntúa alto por ruido: publicidad leída, saludos, una pregunta retórica sin
  respuesta dentro del clip.
- **Buscar lo que la máquina no ve**: una historia con personaje, un contraste entre dos momentos
  lejanos, una frase citable. Si vale, proponerla aunque no esté en la lista.
- **Duración por destino**: 20–45 s rinde en Reels/TikTok/Shorts; >60 s solo si la historia lo
  aguanta (avisos de plataforma en `render`).

Formato de la propuesta al humano: tabla `puntaje · inicio → fin · apertura · motivo`, y los 3
mejores con `hook` sugerido. Con su OK, se copian a `clips.json` y se renderizan.

## Opcional: segunda opinión con Higgsfield

Con los 3 mejores ya renderizados (nivel 1, en borrador), el `virality_predictor` de Higgsfield
puede dar retención/gancho estimados. Gasta créditos: solo si el director lo pide, y nunca en lugar
del criterio.
