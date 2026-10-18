#!/usr/bin/env python3
"""Cobertura de subtítulos N/N por código (qa.md §1b) — sin mirar cuadros.

    subcov.py words.json subtitulos.json [--tol 0.05] [--salida qa/subcov.txt]

words.json: palabras dichas, con tiempos. Acepta [{"text"|"word", "start", "end"}], {"words": [...]},
            o filas [texto, start, end, ...].
subtitulos.json: lo que el motor PINTA en pantalla (exportado por el motor / la composición):
            [{"start", "end", "text"}] (un bloque de subtítulo por elemento).
Regla: en el tiempo medio de cada palabra tiene que haber un subtítulo visible que la contenga.
Escribe "N/N palabras con subtítulo" y la lista de las que faltan. Sale 1 si falta alguna.
Solo librería estándar.
"""
from __future__ import annotations
import argparse, json, re, sys, unicodedata


def norm(t: str) -> str:
    t = unicodedata.normalize("NFKD", str(t).lower().replace("’", "'"))
    return re.sub(r"[^a-z0-9']", "", "".join(c for c in t if not unicodedata.combining(c)))


def load_words(p):
    d = json.load(open(p, encoding="utf-8"))
    if isinstance(d, dict):
        d = d.get("words") or d.get("segments") or []
    out = []
    for w in d:
        if isinstance(w, dict):
            t = w.get("text") or w.get("word") or ""
            s, e = float(w.get("start", 0)), float(w.get("end", 0))
        else:
            t, s, e = w[0], float(w[1]), float(w[2])
        if norm(t):
            out.append((t, s, e))
    return out


def load_subs(p):
    d = json.load(open(p, encoding="utf-8"))
    if isinstance(d, dict):
        d = d.get("captions") or d.get("subs") or []
    return [(float(c["start"]), float(c["end"]), {norm(x) for x in str(c["text"]).split()}) for c in d]


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("words"); ap.add_argument("subs")
    ap.add_argument("--tol", type=float, default=0.05, help="segundos de tolerancia en los bordes")
    ap.add_argument("--salida")
    a = ap.parse_args()
    W, S = load_words(a.words), load_subs(a.subs)
    miss = []
    for t, s, e in W:
        mid, n = (s + e) / 2, norm(t)
        if not any(cs - a.tol <= mid <= ce + a.tol and n in toks for cs, ce, toks in S):
            miss.append(f"  {s:8.2f}s  {t}")
    res = f"{len(W) - len(miss)}/{len(W)} palabras con subtítulo"
    txt = res + ("\nFaltan:\n" + "\n".join(miss) if miss else "")
    print(txt)
    if a.salida:
        open(a.salida, "w", encoding="utf-8").write(txt + "\n")
    return 1 if miss else 0


if __name__ == "__main__":
    raise SystemExit(main())
