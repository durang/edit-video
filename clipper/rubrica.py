"""Rúbrica de clipeabilidad — pre-filtro con puntaje 0–10 y motivo.

No elige: ordena candidatos para que el humano o el agente lean primero lo que más promete.
Los cinco ejes (detalle y ejemplos en references/clipeabilidad.md):

    gancho     0–3   los primeros ~3 s detienen el scroll (pregunta, dato, contradicción, "tú")
    dato       0–2   historia con número o hecho concreto
    remate     0–2   cierra: conclusión, giro o frase final redonda
    autonomía  0–2   se entiende sin contexto (no empieza con "y", "pero", "eso"…)
    emoción    0–1   énfasis, exclamación, palabras cargadas

Solo librería estándar. Español e inglés.
"""
from __future__ import annotations

import re
import unicodedata

_W = r"(?<![\wáéíóúñü])({})(?![\wáéíóúñü])"


def _rx(words: str) -> re.Pattern:
    return re.compile(_W.format(words), re.I)


HOOK = _rx("nadie|nunca|jamás|secreto|error|errores|verdad|mentira|problema|por qué|cómo|"
           "deja de|dejen de|imagina|sabías|lo que|la razón|el truco|la clave|peor|mejor|"
           "no hagas|no te|tienes que|necesitas|te voy a|te digo|ojo|cuidado|mientras|cada segundo|"
           "otros ya|pierdes|perder|antes de que|si estás|si eres|deja de|"
           "nobody|never|secret|mistake|truth|lie|problem|why|how|stop|imagine|"
           "did you know|the reason|the trick|the key|worst|best|you need|here's|don't|while you|"
           "every second|you're losing|before you|if you")
YOU = _rx("tú|tu|te|ti|usted|ustedes|tus|you|your|you're")
NUM_WORDS = _rx("uno|dos|tres|cuatro|cinco|seis|siete|ocho|nueve|diez|cien|mil|millón|millones|"
                "mitad|doble|triple|por ciento|porciento|"
                "one|two|three|four|five|ten|hundred|thousand|million|billion|half|double|percent")
DIGIT = re.compile(r"\d|[$€%]")
PAYOFF = _rx("por eso|así que|entonces|la clave|al final|en resumen|lo importante|la lección|"
             "y eso es|eso es lo que|resultado|por lo tanto|moraleja|tú puedes|puedes ser|no puedes|"
             "el primero|lo único|nunca más|"
             "that's why|so that's|the point|in the end|bottom line|the lesson|which means|"
             "that's what|the result|you can be|you can't|the only|never again")
CONTRAST = _rx("pero|sin embargo|en realidad|la verdad es|resulta que|"
               "but|actually|turns out|the truth is|instead")
DANGLING = _rx("y|pero|entonces|eso|esto|esa|ese|aquello|también|además|o sea|porque|"
               "and|but|so|that|this|also|because|which|it")
EMOTION = _rx("increíble|brutal|loco|locura|miedo|amo|odio|feliz|triste|enojo|impresionante|"
              "wow|neta|literal|en serio|horrible|perfecto|frustr\\w*|tranquil\\w*|harto|urge|"
              "crazy|insane|amazing|love|hate|scared|fear|incredible|terrible|perfect|seriously")


def _sentences(segs: list[dict]) -> list[dict]:
    """Frases con tiempos: de las palabras si hay, si no del segmento."""
    out = []
    for s in segs:
        ws = s.get("words") or []
        if not ws:
            out.append({"start": float(s["start"]), "end": float(s["end"]), "text": s["text"].strip()})
            continue
        cur = []
        for j, w in enumerate(ws):
            cur.append(w)
            nxt = ws[j + 1] if j + 1 < len(ws) else None
            if w["w"][-1:] in ".?!" or nxt is None or nxt["start"] - w["end"] > 0.9:
                out.append({"start": cur[0]["start"], "end": cur[-1]["end"],
                            "text": " ".join(x["w"] for x in cur), "words": cur})
                cur = []
    return [x for x in out if x["text"]]


def puntuar(frases: list[dict]) -> dict:
    """Puntúa una ventana de frases consecutivas. Devuelve ejes, total y motivo."""
    texto = " ".join(f["text"] for f in frases)
    t0 = frases[0]["start"]
    ws = [w for f in frases for w in (f.get("words") or [])]
    if ws:   # la apertura son las palabras de los primeros ~3.5 s, no la frase entera
        apertura = " ".join(w["w"] for w in ws if w["start"] < t0 + 3.5)
    else:
        apertura = " ".join(f["text"] for f in frases if f["start"] < t0 + 3.5) or frases[0]["text"]
    final = frases[-1]["text"]
    motivos = []

    g = 0
    if "?" in apertura:
        g += 1; motivos.append("abre con pregunta")
    if HOOK.search(apertura):
        g += 1; motivos.append(f"gancho «{HOOK.search(apertura).group(0)}»")
    if DIGIT.search(apertura) or NUM_WORDS.search(apertura):
        g += 1; motivos.append("dato en la apertura")
    elif YOU.search(apertura) and g < 3:
        g += 1; motivos.append("habla a «tú»")
    g = min(g, 3)

    nums = len(DIGIT.findall(texto)) + len(NUM_WORDS.findall(texto))
    d = 2 if nums >= 2 else 1 if nums == 1 else 0
    if d:
        motivos.append(f"{nums} dato(s) concreto(s)")

    r = 0
    if final.rstrip()[-1:] in ".!?":
        r += 1
    if PAYOFF.search(final) or CONTRAST.search(texto[len(texto) // 2:]):
        r += 1; motivos.append("remate/giro al final")
    r = min(r, 2)

    primera = frases[0]["text"].split()[0] if frases[0]["text"].split() else ""
    a = 2
    if DANGLING.fullmatch(primera.strip(",.¿¡").lower() or "-"):
        a -= 1; motivos.append(f"arranca con «{primera}» (necesita contexto)")
    if frases[0]["text"][:1].islower():
        a -= 1
    a = max(a, 0)

    e = 1 if ("!" in texto or EMOTION.search(texto)) else 0
    if e:
        motivos.append("carga emocional")

    total = g + d + r + a + e
    return {"total": total, "gancho": g, "dato": d, "remate": r, "autonomia": a, "emocion": e,
            "motivo": "; ".join(motivos) or "sin señales fuertes"}


def candidatos(segs: list[dict], min_s: float = 15, max_s: float = 60, top: int = 10) -> list[dict]:
    """Ventanas de frases completas entre min_s y max_s, puntuadas y sin solaparse."""
    fr = _sentences(segs)
    cands = []
    for i in range(len(fr)):
        for j in range(i, len(fr)):
            dur = fr[j]["end"] - fr[i]["start"]
            if dur > max_s:
                break
            if dur < min_s:
                continue
            p = puntuar(fr[i:j + 1])
            # a igual puntaje, mejor más corto (retiene más)
            cands.append({**p, "start": round(fr[i]["start"], 2), "end": round(fr[j]["end"], 2),
                          "apertura": fr[i]["text"][:80], "_k": (p["total"], -dur)})
    cands.sort(key=lambda c: c["_k"], reverse=True)
    elegidos = []
    for c in cands:
        if all(c["end"] <= x["start"] or c["start"] >= x["end"] for x in elegidos):
            elegidos.append(c)
        if len(elegidos) >= top:
            break
    for n, c in enumerate(elegidos, 1):
        c.pop("_k")
        c["slug"] = f"cand{n:02d}-" + re.sub(r"[^a-z0-9]+", "-", unicodedata.normalize("NFKD", c["apertura"].lower()).encode("ascii", "ignore").decode())[:30].strip("-")
        c["why"] = f"{c['total']}/10 · {c['motivo']}"
    return elegidos
