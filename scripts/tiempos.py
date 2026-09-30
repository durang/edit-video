#!/usr/bin/env python3
"""Tiempos reales de la máquina: registrar, estimar y ver el avance de un trabajo en curso.

Cada trabajo terminado deja una línea en el registro (JSONL). Con eso, antes de lanzar uno nuevo se
estima con los parecidos de verdad (mismo nivel y tipo, intensidad más cercana), y mientras corre se
puede decir en qué fase va, qué % lleva y a qué hora termina.

    tiempos.py estimar  --nivel 3 --intensidad 2 --tipo subida [--duracion 51]
    tiempos.py avance   --log build_v6.jsonl --nivel 3 --intensidad 2 --tipo subida
    tiempos.py registrar --log build_v6.jsonl --nivel 3 --intensidad 2 --tipo subida \\
                         --duracion 51.4 --pieza "why-colombia v6" [--cliente X] [--nota "..."]
    tiempos.py ver [--n 15]

Tipos: nuevo (pieza desde cero) · subida (añadir mucho a una pieza hecha: otra intensidad, otra
sección) · ronda (correcciones del director) · detalles (2–5 arreglos chicos) · bug (problema
técnico; no cuenta para estimar) · clipper (niveles 1–2, lo registra clipper solo).

El registro vive en el área privada de clientes (`_general/tiempos.jsonl`) si existe, o en
`~/.config/edit-video/tiempos.jsonl`. Solo librería estándar.
"""
from __future__ import annotations
import argparse, json, os, re, statistics, sys, time
from datetime import datetime, timezone, timedelta
from pathlib import Path

CONF = Path.home() / ".config" / "edit-video" / "config"


def _conf(key):
    try:
        m = re.search(rf'^{key}="?([^"\n]+)', CONF.read_text("utf-8"), re.M)
        return m.group(1) if m else None
    except OSError:
        return None


def registro() -> Path:
    c = os.environ.get("EDIT_VIDEO_CLIENTS") or _conf("EDIT_VIDEO_CLIENTS")
    if c and Path(c).is_dir():
        return Path(c) / "_general" / "tiempos.jsonl"
    return CONF.parent / "tiempos.jsonl"


def leer() -> list[dict]:
    p = registro()
    if not p.exists():
        return []
    out = []
    for l in p.read_text("utf-8").splitlines():
        try:
            out.append(json.loads(l))
        except ValueError:
            pass
    return out


def anotar(e: dict) -> Path:
    p = registro()
    p.parent.mkdir(parents=True, exist_ok=True)
    with p.open("a", encoding="utf-8") as f:
        f.write(json.dumps(e, ensure_ascii=False) + "\n")
    return p


# ------------------------------------------------------------------ log de un agente (stream-json)
FASES = [  # (nombre, % mínimo al entrar en la fase)
    ("leyendo y planeando", 0), ("activos (recortes, sonido)", 15), ("construyendo", 30),
    ("render", 65), ("revisor", 80), ("listo", 100)]


def leer_log(path: Path) -> dict:
    ini = fin = None; fase = 0; renders = 0; herramientas = 0; texto = ""; resultado = None
    for l in path.read_text("utf-8", errors="ignore").splitlines():
        try:
            d = json.loads(l)
        except ValueError:
            continue
        ts = d.get("timestamp")
        if ts:
            ini = ini or ts; fin = ts
        if d.get("type") == "assistant":
            for c in d.get("message", {}).get("content", []):
                if c.get("type") == "text":
                    texto = c["text"]
                if c.get("type") != "tool_use":
                    continue
                herramientas += 1
                s = json.dumps(c.get("input", {}))
                if "hyperframes render" in s:
                    renders += 1
                    if fase >= 2:          # un render antes de construir es un cuadro de prueba
                        fase = max(fase, 3)
                elif re.search(r"blackframe|qa\.sh|QA_", s) and renders:
                    fase = max(fase, 4)
                elif c.get("name") in ("Edit", "Write") and re.search(r"index\.html|\.js\"", s):
                    fase = max(fase, 2)
                elif re.search(r"remove-background|aevalsrc|anoisesrc|sfx|\.wav", s):
                    fase = max(fase, 1)
        if d.get("type") == "result":
            resultado = d; fase = 5
    mins = None
    if resultado and resultado.get("duration_ms"):
        mins = resultado["duration_ms"] / 60000
    t0 = datetime.fromtimestamp(path.stat().st_ctime, timezone.utc)
    err = path.with_suffix(".err")
    if err.exists():
        t0 = datetime.fromtimestamp(err.stat().st_mtime if err.stat().st_size == 0 else err.stat().st_ctime, timezone.utc)
    if ini:
        try:
            t0 = min(t0, datetime.fromisoformat(ini.replace("Z", "+00:00")))
        except ValueError:
            pass
    return {"inicio": t0, "minutos": mins, "fase": fase, "renders": renders,
            "herramientas": herramientas, "ultimo": texto.strip()[-240:]}


# ------------------------------------------------------------------ estimar
def parecidos(nivel, intensidad, tipo, n=3):
    rows = [r for r in leer() if r.get("tipo") != "bug" and r.get("minutos")]
    same = [r for r in rows if r.get("nivel") == nivel and r.get("tipo") == tipo]
    if not same:  # sin historia de ese tipo: mismo nivel, cualquier tipo salvo detalles/bug
        same = [r for r in rows if r.get("nivel") == nivel and r.get("tipo") not in ("detalles",)]
    same.sort(key=lambda r: (abs((r.get("intensidad") or 1) - (intensidad or 1)), -_ts(r)))
    return same[:n]


def _ts(r):
    try:
        return datetime.fromisoformat(r["fecha"]).timestamp()
    except (KeyError, ValueError):
        return 0


def estimar(nivel, intensidad, tipo, duracion=None):
    ref = parecidos(nivel, intensidad, tipo)
    if not ref:
        return None, []
    base = []
    for r in ref:
        m = r["minutos"]
        if duracion and r.get("duracion_video_s"):  # el trabajo escala suave con la duración
            exp = 1.0 if tipo == "clipper" else 0.5   # clipper escala lineal con los segundos
            m *= (duracion / r["duracion_video_s"]) ** exp
        # cada punto de intensidad por encima de la referencia ≈ +35 % (tabla de nivel-3.md §0)
        m *= 1 + 0.35 * max(0, (intensidad or 1) - (r.get("intensidad") or 1))
        base.append(m)
    med = statistics.median(base)
    return (round(med * 0.85, 1), round(med * 1.3, 1)), ref


def _dur(m):
    return f"{m * 60:.0f} s" if m < 2 else f"{m:.0f} min"


def _fmt_ref(r):
    i = f" · int {r['intensidad']}" if r.get("intensidad") else ""
    return (f"  - {r.get('fecha','')[:10]} · {r.get('pieza','?')} · nivel {r.get('nivel')}{i} · "
            f"{r.get('tipo')} → {_dur(r['minutos'])} ({r.get('renders', '?')} renders)")


def otras(nivel, tipo, ya, n=3):
    rows = [r for r in leer() if r.get("nivel") == nivel and r.get("minutos") and r not in ya
            and r.get("tipo") not in ("bug", "investigacion", tipo)]
    rank = {"nuevo": 0, "subida": 1, "ronda": 2, "detalles": 3, "clipper": 4}
    return sorted(rows, key=lambda r: (rank.get(r.get("tipo"), 9), -_ts(r)))[: max(0, n - len(ya))]


def cmd_estimar(a):
    rng, ref = estimar(a.nivel, a.intensidad, a.tipo, a.duracion)
    if not rng:
        print("Sin historia parecida todavía: primera vez de este tipo. Se registra al terminar.")
        return 0
    print(f"Estimado: {_dur(rng[0])} – {_dur(rng[1])}  (nivel {a.nivel}, intensidad {a.intensidad or '-'}, {a.tipo})")
    print("Referencias:")
    for r in ref:
        print(_fmt_ref(r))
    mas = otras(a.nivel, a.tipo, ref)
    if mas:
        print("Para comparar (otro tipo, mismo nivel):")
        for r in mas:
            print(_fmt_ref(r))
    return 0


def cmd_avance(a):
    L = leer_log(Path(a.log))
    ahora = datetime.now(timezone.utc)
    trans = (ahora - L["inicio"]).total_seconds() / 60 if L["fase"] < 5 else (L["minutos"] or 0)
    rng, ref = estimar(a.nivel, a.intensidad, a.tipo, a.duracion)
    fase_nom, piso = FASES[L["fase"]]
    if L["fase"] == 5:
        pct = 100
    elif rng:
        mid = (rng[0] + rng[1]) / 2
        pct = min(95, round(100 * trans / mid))
    else:
        pct = piso
    if L["fase"] < 5:          # el % por tiempo no se sale de la fase en la que va
        techo = FASES[L["fase"] + 1][1] - 1
        pct = min(max(pct, piso), techo)
    print(f"Fase: {fase_nom} · {pct} % · {trans:.0f} min transcurridos · {L['renders']} renders")
    if rng and L["fase"] < 5:
        f0 = L["inicio"] + timedelta(minutes=rng[0]); f1 = L["inicio"] + timedelta(minutes=rng[1])
        extra = " (va más largo de lo normal)" if trans > rng[1] else ""
        print(f"Estimado total {_dur(rng[0])} – {_dur(rng[1])} → termina ~{f0:%H:%M}–{f1:%H:%M} UTC{extra}")
        print("Referencias:"); [print(_fmt_ref(r)) for r in ref]
        mas = otras(a.nivel, a.tipo, ref)
        if mas:
            print("Para comparar:"); [print(_fmt_ref(r)) for r in mas]
    if L["ultimo"]:
        print(f"Último paso: {L['ultimo']}")
    return 0


def cmd_registrar(a):
    L = leer_log(Path(a.log)) if a.log else {"minutos": a.minutos, "renders": a.renders, "inicio": datetime.now(timezone.utc)}
    mins = a.minutos or L.get("minutos")
    if not mins:
        sys.exit("no sé cuánto tardó: el log no tiene resultado; pasa --minutos")
    e = {"fecha": L["inicio"].isoformat(timespec="minutes"), "pieza": a.pieza, "cliente": a.cliente,
         "nivel": a.nivel, "intensidad": a.intensidad, "tipo": a.tipo, "duracion_video_s": a.duracion,
         "minutos": round(mins, 1), "renders": L.get("renders"), "nota": a.nota}
    p = anotar({k: v for k, v in e.items() if v is not None})
    print(f"✓ {mins:.0f} min registrados en {p}")
    return 0


def cmd_ver(a):
    for r in leer()[-a.n:]:
        print(_fmt_ref(r))
    return 0


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    sp = ap.add_subparsers(dest="cmd", required=True)
    for name in ("estimar", "avance", "registrar"):
        p = sp.add_parser(name)
        p.add_argument("--nivel", type=int, required=True)
        p.add_argument("--intensidad", type=int)
        p.add_argument("--tipo", required=True,
                       choices=["nuevo", "subida", "ronda", "detalles", "bug", "clipper", "investigacion"])
        p.add_argument("--duracion", type=float, help="segundos del video")
        if name in ("avance", "registrar"):
            p.add_argument("--log", required=(name == "avance"), help="stream-json del agente constructor")
        if name == "registrar":
            p.add_argument("--pieza", required=True); p.add_argument("--cliente")
            p.add_argument("--nota"); p.add_argument("--minutos", type=float)
            p.add_argument("--renders", type=int)
    v = sp.add_parser("ver"); v.add_argument("--n", type=int, default=15)
    a = ap.parse_args()
    return {"estimar": cmd_estimar, "avance": cmd_avance, "registrar": cmd_registrar, "ver": cmd_ver}[a.cmd](a)


if __name__ == "__main__":
    raise SystemExit(main())
