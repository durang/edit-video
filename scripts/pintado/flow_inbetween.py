#!/usr/bin/env python3
"""flow_inbetween.py — intercalados por flujo óptico entre dibujos fijos (receta references/pintado-a-mano.md §8).

Para transformaciones lentas (algo que se derrite, un brazo que baja despacio, una luz que crece) se genera
una cadena corta de dibujos y se rellenan los huecos: el flujo óptico (Farneback) deforma cada dibujo hacia
el siguiente, así la pintura se DESLIZA en vez de fundirse. Donde la forma cambia demasiado para que el
flujo la siga (una mano que se abre, un ojo que se cierra), ese trozo cambia de golpe a la MITAD del
intervalo en lugar de dejar un fantasma de doble exposición.

Uso:
    flow_inbetween.py IN_DIR OUT_DIR [--n 4] [--ghost 28]
    flow_inbetween.py --pair a.png b.png OUT_DIR [--n 4]
    flow_inbetween.py --selftest

IN_DIR: dibujos ya fijados con composite_frames.py (ordenados por nombre). OUT_DIR: secuencia 000.png,
001.png… con los originales y N intercalados entre cada par, y `map.json` con el índice de salida de cada
original (para la hoja de exposición: el original k está en map["keys"][k]).

Motor: OpenCV (entorno aislado de edit-video: ~/.config/edit-video/venv-caras/bin/python). Sin OpenCV no
hay flujo: cae a "corte a la mitad" (sin fantasmas, sin deslizamiento) y lo dice.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image

try:
    import cv2  # type: ignore
except Exception:  # pragma: no cover
    cv2 = None

EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def load(p: Path, size=None) -> np.ndarray:
    im = Image.open(p).convert("RGB")
    if size and im.size != size:
        im = im.resize(size, Image.LANCZOS)
    return np.asarray(im).astype(np.float32)


def save(a: np.ndarray, p: Path) -> None:
    Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8)).save(p)


def flow(a: np.ndarray, b: np.ndarray, work: int = 960) -> np.ndarray:
    """Flujo denso a→b (en px de tamaño completo): b(x + F(x)) ≈ a(x)."""
    h, w = a.shape[:2]
    s = min(1.0, work / max(h, w))
    sz = (int(w * s), int(h * s))
    ga = cv2.cvtColor(cv2.resize(a, sz, interpolation=cv2.INTER_AREA).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    gb = cv2.cvtColor(cv2.resize(b, sz, interpolation=cv2.INTER_AREA).astype(np.uint8), cv2.COLOR_RGB2GRAY)
    f = cv2.calcOpticalFlowFarneback(ga, gb, None, 0.5, 5, 25, 5, 7, 1.5, cv2.OPTFLOW_FARNEBACK_GAUSSIAN)
    return cv2.resize(f, (w, h), interpolation=cv2.INTER_LINEAR) / s


def remap(img: np.ndarray, f: np.ndarray, t: float) -> np.ndarray:
    h, w = img.shape[:2]
    gx, gy = np.meshgrid(np.arange(w, dtype=np.float32), np.arange(h, dtype=np.float32))
    return cv2.remap(img, gx + t * f[..., 0], gy + t * f[..., 1], cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)


def inbetweens(a: np.ndarray, b: np.ndarray, n: int, ghost: float = 28.0) -> list[np.ndarray]:
    ts = [(k + 1) / (n + 1) for k in range(n)]
    if cv2 is None:
        return [a if t < 0.5 else b for t in ts]
    fab = flow(a, b)  # a(x) ≈ b(x + fab)
    fba = flow(b, a)  # b(x) ≈ a(x + fba)
    # ¿dónde falla el flujo? a deformado del todo hacia b vs b real
    err = np.abs(remap(a, fba, 1.0) - b).max(-1)
    err = cv2.GaussianBlur(err, (0, 0), 4)
    bad = np.clip((err - ghost) / ghost, 0, 1)[..., None]  # 0 = el flujo sirve, 1 = corte a la mitad
    out = []
    for t in ts:
        wa = remap(a, fba, t)        # a avanzando hacia b
        wb = remap(b, fab, 1.0 - t)  # b retrocediendo hacia a
        mix = wa * (1 - t) + wb * t
        hard = wa if t < 0.5 else wb
        out.append(mix * (1 - bad) + hard * bad)
    return out


def run(files: list[Path], out: Path, n: int, ghost: float) -> dict:
    out.mkdir(parents=True, exist_ok=True)
    size = Image.open(files[0]).size
    imgs = [load(p, size) for p in files]
    k = 0
    keys = []
    for i, im in enumerate(imgs):
        keys.append(k)
        save(im, out / f"{k:03d}.png")
        k += 1
        if i + 1 < len(imgs):
            for mid in inbetweens(im, imgs[i + 1], n, ghost):
                save(mid, out / f"{k:03d}.png")
                k += 1
    m = {"sources": [p.name for p in files], "n": n, "keys": keys, "count": k,
         "engine": "farneback" if cv2 is not None else "midpoint-switch"}
    (out / "map.json").write_text(json.dumps(m, indent=1))
    print(f"  {len(files)} dibujos → {k} cuadros ({m['engine']}) en {out}")
    return m


def selftest() -> int:
    import tempfile
    h, w = 240, 320
    yy, xx = np.mgrid[0:h, 0:w]
    bg = np.zeros((h, w, 3), np.float32) + [20, 30, 90]
    bg[..., 2] += 20 * np.sin(xx / 9.0) * np.cos(yy / 11.0)

    def disc(cx):
        im = bg.copy()
        m = ((xx - cx) ** 2 + (yy - 120) ** 2) < 30 ** 2
        # pintura con textura que viaja con la forma (una mancha plana no tiene flujo que seguir)
        tex = 25 * np.sin((xx - cx) / 4.0) * np.cos((yy - 120) / 5.0)
        im[m] = np.stack([240 + tex * 0.5, 190 + tex, 60 + tex * 0.4], -1)[m]
        return im

    tmp = Path(tempfile.mkdtemp())
    save(disc(120), tmp / "a.png")
    save(disc(150), tmp / "b.png")
    m = run([tmp / "a.png", tmp / "b.png"], tmp / "out", 3, 28.0)
    mid = load(tmp / "out" / f"{m['keys'][0] + 2:03d}.png")  # t = 0.5
    yel = (mid[..., 0] > 160) & (mid[..., 2] < 140)
    cx = float(xx[yel].mean()) if yel.any() else -1
    area = int(yel.sum())
    full = int((((xx - 120) ** 2 + (yy - 120) ** 2) < 30 ** 2).sum())
    if cv2 is None:
        ok = m["count"] == 5
        print(f"selftest flow_inbetween (sin OpenCV, corte a la mitad): {m['count']} cuadros → {'OK' if ok else 'FALLA'}")
    else:
        # un solo disco en el centro (≈135), con el área de un disco (no dos medios discos fantasma)
        ok = abs(cx - 135) < 6 and 0.75 * full < area < 1.25 * full
        print(f"selftest flow_inbetween (farneback): centro t=0.5 x={cx:.1f} (esperado 135) "
              f"área {area}/{full} → {'OK' if ok else 'FALLA'}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("args", nargs="*")
    ap.add_argument("--pair", action="store_true", help="args = a.png b.png OUT_DIR")
    ap.add_argument("--n", type=int, default=4, help="intercalados por par")
    ap.add_argument("--ghost", type=float, default=28.0, help="error (0-255) desde el que se corta a la mitad")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    if cv2 is None:
        print("  · sin OpenCV: corte a la mitad, sin flujo (usa ~/.config/edit-video/venv-caras/bin/python)",
              file=sys.stderr)
    if a.pair:
        if len(a.args) != 3:
            ap.error("--pair a.png b.png OUT_DIR")
        files, out = [Path(a.args[0]), Path(a.args[1])], Path(a.args[2])
    else:
        if len(a.args) != 2:
            ap.error("IN_DIR OUT_DIR")
        d = Path(a.args[0])
        files = sorted(p for p in d.iterdir() if p.suffix.lower() in EXTS and ".mask" not in p.name)
        out = Path(a.args[1])
    run(files, out, a.n, a.ghost)
    return 0


if __name__ == "__main__":
    sys.exit(main())
