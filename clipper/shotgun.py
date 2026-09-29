#!/usr/bin/env python3
"""shotgun de estilo — varias direcciones de diseño, cuadros de estilo reales, eliges, se guarda.

Inspirado en /design-shotgun de gstack, adaptado a video: en vez de imágenes generadas por IA
(que escriben mal las letras y no muestran el metraje), cada dirección se RENDERIZA sobre el
metraje real con la tipografía real, y se sacan cuadros de estilo (gancho + subtítulo).

  shotgun.py preparar T.json CLIPS.json DIRECCIONES.json --out DIR [--clip N] [--cliente SLUG]
                      [--tiempos 1.4,4.6]
  shotgun.py tablero  DIR                 # tablero de comparación (el de gstack si está); si no, rutas
  shotgun.py elegir   DIR [--elegida A] [--rechazadas B,C] [--cliente SLUG] [--nota "…"]
  shotgun.py gusto    [--cliente SLUG]    # qué ha aprobado y rechazado (con olvido del 5 % por semana)

DIRECCIONES.json:
  {"direcciones": [
     {"id": "A", "nombre": "Editorial papel", "plantilla": { …lo que cambia sobre el nivel 2… }},
     {"id": "B", …}, {"id": "C", …}]}

Regla anti-parecido (de gstack): cada dirección con OTRA fuente de titular, OTRO acento de color y
OTRA disposición (palabra activa / alineación del gancho / mayúsculas). Si dos se parecen, se avisa
y no se genera (salvo --permitir-parecidas).
"""
import argparse
import datetime as dt
import json
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import clipper as C  # noqa: E402

FFMPEG = C.FFMPEG


def area_cliente(slug):
    area = os.environ.get("EDIT_VIDEO_CLIENTS") or C._config_value("EDIT_VIDEO_CLIENTS") \
        or str(Path.home() / ".agents/edit-video-clients")
    return Path(area) / "clients" / slug


def rasgos(P):
    """Las dimensiones que se comparan y que aprende el gusto."""
    f, c = P.get("fuentes", {}), P.get("colores", {})
    st, g = P.get("subtitulo", {}), P.get("gancho", {})
    return {
        "fuente_titular": f.get("display", "Clipper Display"),
        "fuente_acento": f.get("serif", "Clipper Serif"),
        "acento": c.get("acento", "#FFD23F").upper(),
        "activa": st.get("activa", "caja"),
        "alineacion": g.get("alineacion", "izquierda"),
        "mayusculas": bool(st.get("mayusculas", False)),
    }


def demasiado_parecidas(ra, rb):
    mismo_tipo = ra["fuente_titular"] == rb["fuente_titular"]
    mismo_color = ra["acento"] == rb["acento"]
    misma_disp = (ra["activa"], ra["alineacion"], ra["mayusculas"]) == \
                 (rb["activa"], rb["alineacion"], rb["mayusculas"])
    return sum([mismo_tipo, mismo_color, misma_disp]) >= 2


def cmd_preparar(a):
    C.need_libass()          # sin libass no hay cuadros de estilo del nivel 2 (lo explica y sale)
    out = Path(a.out).expanduser().resolve()
    out.mkdir(parents=True, exist_ok=True)
    tdata = json.loads(Path(a.transcript).read_text(encoding="utf-8"))
    segs = tdata["segments"]
    video = Path(tdata["source"])
    clips = json.loads(Path(a.clips).read_text(encoding="utf-8"))
    clips = clips.get("clips", clips) if isinstance(clips, dict) else clips
    clip = dict(clips[a.clip - 1])
    dirs = json.loads(Path(a.direcciones).read_text(encoding="utf-8"))["direcciones"]
    tiempos = [float(x) for x in a.tiempos.split(",")]

    base = C.load_plantilla(2, None, a.cliente)
    Ps = {d["id"]: C._merge(base, d.get("plantilla", {})) for d in dirs}
    R = {k: rasgos(v) for k, v in Ps.items()}
    ids = list(Ps)
    malos = [(x, y) for i, x in enumerate(ids) for y in ids[i + 1:] if demasiado_parecidas(R[x], R[y])]
    if malos and not a.permitir_parecidas:
        for x, y in malos:
            print(f"✗ {x} y {y} se parecen demasiado (comparten 2 de: fuente de titular, acento, disposición)")
        print("  Cambia una de las dos o usa --permitir-parecidas.")
        return 2

    C.apply_dictionary(segs, C.load_dictionary(a.cliente, video.parent))
    clip["end"] = min(float(clip["end"]), float(clip["start"]) + max(tiempos) + 0.6)
    imgs = []
    for d in dirs:
        k = d["id"]
        rd = out / f"render-{k}"
        rd.mkdir(exist_ok=True)
        print(f"· {k} — {d.get('nombre', '')}")
        mp4 = C.render_clip(video, segs, dict(clip, slug=f"dir-{k}"), rd, True, 1, 3, False,
                            None, "top-right", 0.22, True, 1.0, 23, "ultrafast", 0,
                            clip.get("fit", "blur"), float(clip.get("crop_x", 0.5)),
                            float(clip.get("cover_subs", 0)), 0.0, True, True, 2, Ps[k])
        if not mp4:
            print(f"  ✗ {k}: no se pudo renderizar"); continue
        frames = []
        for i, t in enumerate(tiempos):
            f = rd / f"cuadro{i + 1}.png"
            C.run([FFMPEG, "-y", "-ss", f"{t:.2f}", "-i", str(mp4), "-frames:v", "1",
                   "-vf", "scale=540:-2", str(f)])
            if f.exists():
                frames.append(f)
        img = out / f"direccion-{k}.png"
        if len(frames) > 1:
            cmd = [FFMPEG, "-y"]
            for f in frames:
                cmd += ["-i", str(f)]
            cmd += ["-filter_complex", f"hstack=inputs={len(frames)}", str(img)]
            C.run(cmd)
        elif frames:
            shutil.copy(frames[0], img)
        if img.exists():
            imgs.append(str(img))
            print(f"  ✓ {img.name}")
    (out / "direcciones.json").write_text(json.dumps({"direcciones": dirs, "rasgos": R,
                                                      "cliente": a.cliente, "clip": clip},
                                                     ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"\n{len(imgs)}/{len(dirs)} direcciones listas en {out}")
    print("Siguiente: enséñalas (Read de cada PNG) y abre el tablero:  shotgun.py tablero", out)
    return 0 if imgs else 1


def gstack_design():
    for p in (os.environ.get("GSTACK_DESIGN"),
              str(Path.home() / ".claude/skills/gstack/design/dist/design")):
        if p and Path(p).exists() and os.access(p, os.X_OK):
            return p
    return None


def cmd_tablero(a):
    out = Path(a.dir).expanduser().resolve()
    imgs = sorted(str(p) for p in out.glob("direccion-*.png"))
    if not imgs:
        print("No hay direccion-*.png en", out); return 1
    D = gstack_design()
    if not D:
        print("Sin tablero de gstack en esta máquina. Enséñale al usuario estas imágenes y pregunta cuál:")
        for i in imgs:
            print("  ", i)
        return 0
    log = out / "tablero.log"
    with open(log, "w") as lf:
        subprocess.Popen([D, "compare", "--images", ",".join(imgs), "--output",
                          str(out / "tablero.html"), "--serve", "--title", "Shotgun de estilo"],
                         stdout=lf, stderr=lf, start_new_session=True)
    for _ in range(40):
        time.sleep(0.5)
        txt = log.read_text(errors="ignore") if log.exists() else ""
        for line in txt.splitlines():
            if "BOARD_URL:" in line or "SERVE_BROWSER_OPENED" in line:
                print(line.strip())
                print(f"Cuando el usuario pulse Submit, la elección queda en {out}/feedback.json "
                      f"(Regenerate/Remix → feedback-pending.json).")
                return 0
    print("El tablero no arrancó (ver", log, "). Enseña las imágenes en el chat:")
    for i in imgs:
        print("  ", i)
    return 0


def gusto_path(cliente):
    return (area_cliente(cliente) / "gusto.json") if cliente else \
        (Path.home() / ".config/edit-video/gusto.json")


def cmd_elegir(a):
    out = Path(a.dir).expanduser().resolve()
    meta = json.loads((out / "direcciones.json").read_text(encoding="utf-8"))
    cliente = a.cliente or meta.get("cliente")
    fb = {}
    if (out / "feedback.json").exists():
        fb = json.loads((out / "feedback.json").read_text(encoding="utf-8"))
    elegida = (a.elegida or fb.get("preferred") or "").strip().upper()
    ids = [d["id"] for d in meta["direcciones"]]
    if elegida not in ids:
        print(f"Falta la elegida (una de {ids}). Usa --elegida o el tablero."); return 1
    rech = [x.strip().upper() for x in (a.rechazadas or "").split(",") if x.strip()] or \
           [i for i in ids if i != elegida]
    d = next(x for x in meta["direcciones"] if x["id"] == elegida)

    # 1) la plantilla elegida pasa a ser la del cliente (la anterior se guarda con fecha)
    hoy = dt.date.today().isoformat()
    if cliente:
        cf = area_cliente(cliente) / "clipper.json"
        prev = json.loads(cf.read_text(encoding="utf-8")) if cf.exists() else {}
        if cf.exists():
            shutil.copy(cf, cf.with_name(f"clipper.{hoy}.json"))
        nueva = C._merge(prev, d.get("plantilla", {}))
        nueva["_direccion"] = f"{hoy} · shotgun {elegida} · {d.get('nombre', '')}"
        cf.write_text(json.dumps(nueva, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        print(f"✓ plantilla del cliente actualizada: {cf}  (anterior: clipper.{hoy}.json)")
    else:
        (out / "plantilla-elegida.json").write_text(json.dumps(d.get("plantilla", {}), ensure_ascii=False,
                                                                indent=2), encoding="utf-8")
        print(f"✓ {out / 'plantilla-elegida.json'}")

    # 2) memoria de gusto: aprobado / rechazado por dimensión
    gp = gusto_path(cliente)
    gp.parent.mkdir(parents=True, exist_ok=True)
    G = json.loads(gp.read_text(encoding="utf-8")) if gp.exists() else {"version": 1, "dimensiones": {}, "sesiones": []}
    def marca(rs, campo):
        for dim, val in rs.items():
            e = G["dimensiones"].setdefault(dim, {}).setdefault(str(val), {"aprobado": 0, "rechazado": 0})
            e[campo] += 1
            e["ultimo"] = hoy
    marca(meta["rasgos"][elegida], "aprobado")
    for r in rech:
        if r in meta["rasgos"] and r != elegida:
            marca(meta["rasgos"][r], "rechazado")
    G["sesiones"].append({"fecha": hoy, "elegida": elegida, "rechazadas": rech,
                          "nota": a.nota or fb.get("overall", ""), "comentarios": fb.get("comments", {})})
    gp.write_text(json.dumps(G, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    (out / "aprobado.json").write_text(json.dumps({"elegida": elegida, "fecha": hoy, "feedback": fb,
                                                   "nota": a.nota}, ensure_ascii=False, indent=2),
                                       encoding="utf-8")
    print(f"✓ gusto actualizado: {gp}")
    return 0


def cmd_gusto(a):
    gp = gusto_path(a.cliente)
    if not gp.exists():
        print("Sin gusto registrado todavía."); return 0
    G = json.loads(gp.read_text(encoding="utf-8"))
    hoy = dt.date.today()
    print(f"Gusto — {a.cliente or 'general'}  ({len(G.get('sesiones', []))} sesiones)")
    for dim, vals in G.get("dimensiones", {}).items():
        filas = []
        for v, e in vals.items():
            sem = max(0, (hoy - dt.date.fromisoformat(e.get("ultimo", hoy.isoformat()))).days / 7)
            peso = (e["aprobado"] - e["rechazado"]) * (0.95 ** sem)
            filas.append((peso, v, e))
        filas.sort(reverse=True)
        txt = " · ".join(f"{v} ({'+' if p >= 0 else ''}{p:.1f})" for p, v, _ in filas[:4])
        print(f"  {dim:15} {txt}")
    return 0


def main():
    ap = argparse.ArgumentParser(prog="shotgun", description="Shotgun de estilo para video.")
    sp = ap.add_subparsers(dest="cmd", required=True)
    p = sp.add_parser("preparar"); p.add_argument("transcript"); p.add_argument("clips")
    p.add_argument("direcciones"); p.add_argument("--out", required=True)
    p.add_argument("--clip", type=int, default=1); p.add_argument("--cliente")
    p.add_argument("--tiempos", default="1.4,4.6")
    p.add_argument("--permitir-parecidas", action="store_true")
    p.set_defaults(f=cmd_preparar)
    p = sp.add_parser("tablero"); p.add_argument("dir"); p.set_defaults(f=cmd_tablero)
    p = sp.add_parser("elegir"); p.add_argument("dir"); p.add_argument("--elegida")
    p.add_argument("--rechazadas"); p.add_argument("--cliente"); p.add_argument("--nota")
    p.set_defaults(f=cmd_elegir)
    p = sp.add_parser("gusto"); p.add_argument("--cliente"); p.set_defaults(f=cmd_gusto)
    a = ap.parse_args()
    return a.f(a)


if __name__ == "__main__":
    sys.exit(main())
