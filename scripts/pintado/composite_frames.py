#!/usr/bin/env python3
"""composite_frames.py — fija los dibujos de un plano pintado (receta references/pintado-a-mano.md §6).

Cada dibujo editado ("Edit this exact painting. Change ONLY …") vuelve movido unos píxeles y con el
color un poco corrido. Puestos en fila, parpadean. Este script toma SOLO lo que cambió de cada dibujo
y lo pega sobre la base, así el fondo queda idéntico al píxel en todo el plano:

  1. alinea cada dibujo con la base usando solo el fondo (correlación de fase + ECC afín con máscara),
  2. iguala el color con la base, medido en la zona que no cambió (ganancia + desplazamiento por canal),
  3. calcula la máscara de cambio (diferencia, limpieza morfológica, sin islas pequeñas, borde suave),
  4. pega solo la zona cambiada sobre la base.

Uso:
    composite_frames.py SET_DIR [--out SET_DIR/steady] [--thresh 16] [--feather 9] [--min-area 0.0004]
    composite_frames.py --base base.png a.png b.png … --out dir
    composite_frames.py SET_DIR --roi 0.55,0.65,0.95,0.9     # solo pega cambios dentro de esa caja
    composite_frames.py --selftest

SET_DIR: PNG/JPG ordenados por nombre; el PRIMERO es la base (00.png, 01.png…). Salida: mismos nombres en
--out, más `<nombre>.mask.png` (rojo = lo que se tomó del dibujo) y `report.json` (desplazamiento,
ganancias, % cambiado). Con `--roi` (o `SET_DIR/rois.json` por dibujo) solo se toma el cambio dentro de la zona
que se pidió editar: lo que el modelo movió fuera (una lámpara, la cabecera) se queda como en la base. Un dibujo con > 35 % cambiado o desplazamiento > 3 % del ancho se marca "REVISAR":
casi siempre es un encuadre que se movió → se vuelve a generar ese paso, no se parchea.

Motor: OpenCV si está (el entorno aislado de edit-video lo trae: ~/.config/edit-video/venv-caras/bin/python);
si no, cae a numpy + Pillow (solo traslación, sin ECC) y lo dice.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageFilter

try:
    import cv2  # type: ignore
except Exception:  # pragma: no cover - depende del entorno
    cv2 = None

EXTS = {".png", ".jpg", ".jpeg", ".webp"}


def load(p: Path, size=None) -> np.ndarray:
    im = Image.open(p).convert("RGB")
    if size and im.size != size:
        im = im.resize(size, Image.LANCZOS)
    return np.asarray(im).astype(np.float32)


def save(a: np.ndarray, p: Path) -> None:
    Image.fromarray(np.clip(a + 0.5, 0, 255).astype(np.uint8)).save(p)


def gray(a: np.ndarray) -> np.ndarray:
    return a @ np.array([0.299, 0.587, 0.114], np.float32)


def blur(a: np.ndarray, r: float) -> np.ndarray:
    if r <= 0:
        return a
    if cv2 is not None:
        k = int(r * 3) | 1
        return cv2.GaussianBlur(a, (k, k), r)
    # numpy puro: gaussiana separable
    x = np.arange(-int(r * 3), int(r * 3) + 1, dtype=np.float32)
    k = np.exp(-x * x / (2 * r * r))
    k /= k.sum()
    pad = len(k) // 2
    def conv(v, ax):
        v = np.pad(v, [(pad, pad) if i == ax else (0, 0) for i in range(v.ndim)], mode="reflect")
        return np.apply_along_axis(lambda s: np.convolve(s, k, "valid"), ax, v)
    return conv(conv(a.astype(np.float32), 0), 1).astype(np.float32)


def phase_shift(a: np.ndarray, b: np.ndarray) -> tuple[float, float]:
    """Traslación (dx, dy) que lleva b sobre a (numpy puro, con ventana de Hann)."""
    h, w = a.shape
    win = np.outer(np.hanning(h), np.hanning(w)).astype(np.float32)
    A = np.fft.fft2((a - a.mean()) * win)
    B = np.fft.fft2((b - b.mean()) * win)
    R = A * np.conj(B)
    R /= np.abs(R) + 1e-9
    r = np.fft.ifft2(R).real
    y, x = np.unravel_index(np.argmax(r), r.shape)
    # sub-píxel por parábola en cada eje
    def sub(c, n, get):
        l, m, rr = get((c - 1) % n), get(c), get((c + 1) % n)
        d = l - 2 * m + rr
        return c + (0.5 * (l - rr) / d if abs(d) > 1e-12 else 0.0)
    xs = sub(x, w, lambda i: r[y, i])
    ys = sub(y, h, lambda i: r[i, x])
    if xs > w / 2:
        xs -= w
    if ys > h / 2:
        ys -= h
    return float(xs), float(ys)


def warp(img: np.ndarray, M: np.ndarray) -> np.ndarray:
    """Aplica la afín 2x3 M (coordenadas de la base → del dibujo) al dibujo."""
    h, w = img.shape[:2]
    if cv2 is not None:
        return cv2.warpAffine(img, M, (w, h), flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                              borderMode=cv2.BORDER_REFLECT)
    # solo traslación en el modo sin OpenCV
    dx, dy = M[0, 2], M[1, 2]
    pil = [Image.fromarray(img[..., c]) for c in range(3)]
    out = [np.asarray(p.transform(p.size, Image.AFFINE, (1, 0, dx, 0, 1, dy), Image.BILINEAR), np.float32)
           for p in pil]
    return np.stack(out, -1)


def valid_mask(shape, M: np.ndarray) -> np.ndarray:
    """1 donde el dibujo alineado tiene píxeles reales; 0 donde la alineación dejó borde inventado (reflejo)."""
    h, w = shape[:2]
    if cv2 is None:
        m = np.ones((h, w), np.float32)
        e = int(np.ceil(np.abs(M[:, 2]).max())) + 2
        m[:e], m[-e:], m[:, :e], m[:, -e:] = 0, 0, 0, 0
        return m
    ones = np.ones((h, w), np.float32)
    m = cv2.warpAffine(ones, M, (w, h), flags=cv2.INTER_NEAREST | cv2.WARP_INVERSE_MAP,
                       borderMode=cv2.BORDER_CONSTANT, borderValue=0)
    m = cv2.erode(m, np.ones((31, 31), np.uint8))   # margen + borde suave: sin costura visible
    return np.clip(blur(m, 12.0), 0, 1)


def align(base: np.ndarray, draw: np.ndarray, work: int = 900) -> tuple[np.ndarray, np.ndarray]:
    """Devuelve (dibujo alineado, M). Alinea con el FONDO: el primer cálculo de cambio se excluye del ECC."""
    h, w = base.shape[:2]
    s = min(1.0, work / max(h, w))
    sz = (max(8, int(w * s)), max(8, int(h * s)))
    gb = np.asarray(Image.fromarray(gray(base)).resize(sz, Image.BILINEAR), np.float32)
    gd = np.asarray(Image.fromarray(gray(draw)).resize(sz, Image.BILINEAR), np.float32)
    dx, dy = phase_shift(gb, gd)
    M = np.array([[1, 0, -dx], [0, 1, -dy]], np.float32)  # base → dibujo (inverse map)
    if cv2 is not None:
        # Arranque robusto: puntos ORB + RANSAC (similaridad). Con un brazo o un cuerpo entero que cambió, la
        # correlación de fase se va al cambio; los puntos del fondo (ventana, mueble, textura) mandan aquí.
        try:
            orb = cv2.ORB_create(6000)
            ka, da = orb.detectAndCompute(gb.astype(np.uint8), None)
            kb, db_ = orb.detectAndCompute(gd.astype(np.uint8), None)
            if da is not None and db_ is not None and len(ka) > 50 and len(kb) > 50:
                mt = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(da, db_)
                if len(mt) >= 30:
                    pa = np.float32([ka[m.queryIdx].pt for m in mt])
                    pb = np.float32([kb[m.trainIdx].pt for m in mt])
                    A, inl = cv2.estimateAffinePartial2D(pa, pb, method=cv2.RANSAC, ransacReprojThreshold=2.0,
                                                         maxIters=5000, confidence=0.999)
                    if A is not None and inl is not None and inl.sum() >= 25:
                        M = A.astype(np.float32)  # base → dibujo, igual que WARP_INVERSE_MAP
        except cv2.error:
            pass
        # máscara de fondo: lo que ya coincide tras la traslación
        moved = cv2.warpAffine(gd, M, sz, flags=cv2.INTER_LINEAR | cv2.WARP_INVERSE_MAP,
                               borderMode=cv2.BORDER_REFLECT)
        diff = blur(np.abs(moved - gb), 2.0)
        bg = (diff < np.percentile(diff, 70)).astype(np.uint8) * 255
        try:
            crit = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 200, 1e-6)
            M0 = M.copy()
            _, M = cv2.findTransformECC(blur(gb, 1.2), blur(gd, 1.2), M.copy(), cv2.MOTION_AFFINE, crit, bg, 5)
            if np.abs(M[:, 2] - M0[:, 2]).max() > 0.02 * max(sz) or np.abs(M[:, :2] - M0[:, :2]).max() > 0.03:
                M = M0  # el ECC se fue lejos del arranque: no se le cree
        except cv2.error:
            pass  # se queda con el arranque
    M = M.astype(np.float32).copy()
    M[:, 2] /= s
    return warp(draw, M), M


def color_match(base: np.ndarray, draw: np.ndarray, keep: np.ndarray) -> tuple[np.ndarray, list]:
    """Ganancia + desplazamiento por canal medidos en `keep` (zona sin cambio)."""
    out = draw.copy()
    coef = []
    idx = keep > 0
    if idx.sum() < 500:
        return out, [[1.0, 0.0]] * 3
    for c in range(3):
        x = draw[..., c][idx]
        y = base[..., c][idx]
        vx = float(x.var())
        g = float(((x - x.mean()) * (y - y.mean())).mean() / vx) if vx > 1e-6 else 1.0
        g = float(np.clip(g, 0.8, 1.25))
        o = float(np.clip(y.mean() - g * x.mean(), -40, 40))
        out[..., c] = draw[..., c] * g + o
        coef.append([round(g, 4), round(o, 2)])
    return out, coef


def morph(m: np.ndarray, r: int, op: str) -> np.ndarray:
    if r <= 0:
        return m
    if cv2 is not None:
        k = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2 * r + 1, 2 * r + 1))
        return (cv2.dilate if op == "dilate" else cv2.erode)(m, k)
    f = ImageFilter.MaxFilter if op == "dilate" else ImageFilter.MinFilter
    return np.asarray(Image.fromarray(m).filter(f(2 * r + 1)))


def drop_small(m: np.ndarray, min_px: int) -> np.ndarray:
    if cv2 is None or min_px <= 0:
        return m
    n, lab, st, _ = cv2.connectedComponentsWithStats(m, 8)
    keep = np.zeros(n, bool)
    keep[1:] = st[1:, cv2.CC_STAT_AREA] >= min_px
    return (keep[lab] * 255).astype(np.uint8)


def change_mask(base: np.ndarray, draw: np.ndarray, thresh: float, feather: float, min_area: float):
    """Máscara de lo que cambió. La diferencia se SUAVIZA antes del umbral (no se abre después): así el
    ruido de textura del crayón (cada edición re-pinta el grano) se promedia y desaparece, pero un cambio
    fino de alto contraste (una pupila, una línea de párpado) sigue pasando. Luego se cierran los huecos
    para que una zona cambiada (una cara) se tome entera, nunca mitad vieja, mitad nueva."""
    h, w = base.shape[:2]
    r = max(1, int(round(min(h, w) * 0.004)))
    d = np.abs(blur(base, 1.0) - blur(draw, 1.0)).max(-1)
    d = blur(d, r * 1.5)
    m = (d > thresh).astype(np.uint8) * 255
    m = morph(morph(m, 5 * r, "dilate"), 5 * r, "erode")  # cerrar: une trozos de un mismo cambio
    m = drop_small(m, int(min_area * h * w))
    m = morph(m, 2 * r, "dilate")                          # margen para que no se vea el corte
    alpha = blur(m.astype(np.float32) / 255.0, feather)
    return np.clip(alpha, 0, 1), m


def roi_mask(shape, boxes, feather: float) -> np.ndarray:
    """1 dentro de las cajas (fracciones x0,y0,x1,y1), borde suave; sin cajas, todo 1."""
    h, w = shape[:2]
    if not boxes:
        return np.ones((h, w), np.float32)
    m = np.zeros((h, w), np.float32)
    for x0, y0, x1, y1 in boxes:
        m[int(y0 * h):int(y1 * h), int(x0 * w):int(x1 * w)] = 1
    return np.clip(blur(m, feather * 3), 0, 1)


def composite(base_p: Path, draws: list[Path], out: Path, thresh=16.0, feather=9.0, min_area=0.0004,
              rois: dict | None = None, chain: bool = False) -> list:
    """rois: {"nombre.png": [[x0,y0,x1,y1], …] | "light" | "full", "*": …}.
    "light" = cambio de LUZ (una lámpara que se enciende): solo la luz pasa al cuadro fijo anterior.
    "full"  = el cuadro entero viene del dibujo alineado (sin igualar color ni máscara).
    chain=True: cada dibujo se alinea con el ANTERIOR ya alineado (para cadenas largas de ediciones, donde el
    encuadre deriva poco a poco y el salto hasta la base ya es demasiado grande para alinear directo)."""
    out.mkdir(parents=True, exist_ok=True)
    bim = Image.open(base_p)
    base = load(base_p)
    save(base, out / f"{base_p.stem}.png")
    rep = [{"file": base_p.name, "base": True}]
    ref, prev_res = base, base
    for p in draws:
        d = load(p, bim.size)
        prev_al = ref
        al, M = align(ref, d)
        if chain:
            ref = al
        boxes = (rois or {}).get(p.name, (rois or {}).get("*"))
        if boxes == "light":
            # cambio de LUZ sobre el cuadro anterior: se transfiere solo la luz (cociente muy suavizado entre el
            # dibujo nuevo y el anterior, ambos alineados) al cuadro fijo anterior. La geometría no se mueve nada.
            # Aditivo (no multiplicativo): una luz cálida sobre un azul oscuro SUMA color; multiplicar el azul
            # da amarillo verdoso. Diferencia suavizada (1 % del lado) entre el dibujo nuevo y el anterior.
            r = max(4.0, min(base.shape[:2]) * 0.01)
            # sin máscara de válidos: los dos dibujos están alineados casi igual, así que en el borde reflejado la
            # diferencia sigue siendo luz; cortarla dejaba una costura brillante si la lámpara toca el borde
            light = blur(al, r) - blur(prev_al, r)
            al = np.clip(prev_res + light, 0, 255)
            alpha = np.ones(base.shape[:2], np.float32)
            m = np.full(base.shape[:2], 255, np.uint8)
            coef = None
        elif boxes == "full":
            alpha = np.ones(base.shape[:2], np.float32)
            m = np.full(base.shape[:2], 255, np.uint8)
            coef = None
        else:
            # primera máscara (sin igualar) → zona estable → igualar color → máscara final
            _, m0 = change_mask(base, al, thresh * 1.4, 0, min_area)
            keep = (morph(m0, 6, "dilate") == 0).astype(np.uint8)
            al, coef = color_match(base, al, keep)
            alpha, m = change_mask(base, al, thresh, feather, min_area)
            if boxes:  # solo se toma el cambio que se PIDIÓ: lo que derivó fuera (lámpara, cabecera) se queda de la base
                alpha = alpha * roi_mask(base.shape, boxes, feather)
            # borde: lo que entró por el reflejo de la alineación no es un cambio real
            alpha = alpha * valid_mask(base.shape, M)
            m = m.copy(); m[alpha < 0.02] = 0
        res = base * (1 - alpha[..., None]) + al * alpha[..., None]
        prev_res = res
        save(res, out / f"{p.stem}.png")
        vis = base * 0.55
        vis[..., 0] = np.maximum(vis[..., 0], alpha * 255)
        save(vis, out / f"{p.stem}.mask.png")
        pct = float((m > 0).mean() * 100)
        shift = float(np.hypot(M[0, 2], M[1, 2]))
        flag = (pct > 35 and boxes not in ("full", "light")) or shift > 0.03 * base.shape[1]
        rep.append({"file": p.name, "dx": round(float(M[0, 2]), 2), "dy": round(float(M[1, 2]), 2),
                    "affine": np.round(M, 4).tolist(), "color": coef, "changed_pct": round(pct, 2),
                    "status": "REVISAR" if flag else "ok"})
        print(f"  {p.name}: shift ({M[0, 2]:+.1f}, {M[1, 2]:+.1f}) px · cambió {pct:.1f}% · "
              f"{'REVISAR' if flag else 'ok'}")
    (out / "report.json").write_text(json.dumps(rep, indent=1))
    return rep


def selftest() -> int:
    import tempfile
    rng = np.random.default_rng(7)
    h, w = 480, 300
    tex = blur(rng.normal(128, 50, (h, w, 3)).astype(np.float32), 3)
    yy, xx = np.mgrid[0:h, 0:w]
    tex[..., 2] += 40 * np.sin(xx / 17.0) + 30 * np.cos(yy / 23.0)  # estructura para alinear
    base = np.clip(tex, 0, 255)
    # dibujo = base movida (+3, -2), color corrido, + un "brazo" nuevo
    M = np.float32([[1, 0, 3], [0, 1, -2]])
    shifted = np.roll(np.roll(base, -2, 0), 3, 1)
    draw = np.clip(shifted * 1.04 + 5, 0, 255)
    draw[200:260, 120:200] = [230, 120, 60]
    tmp = Path(tempfile.mkdtemp())
    save(base, tmp / "00.png")
    save(draw, tmp / "01.png")
    rep = composite(tmp / "00.png", [tmp / "01.png"], tmp / "steady")
    res = load(tmp / "steady" / "01.png")
    outside = np.ones((h, w), bool)
    outside[180:280, 100:220] = False
    err_out = float(np.abs(res - base)[outside].mean())
    err_in = float(np.abs(res[210:250, 130:190] - np.array([230, 120, 60])).mean())
    ok = err_out < 1.5 and err_in < 12 and rep[1]["status"] == "ok"
    print(f"selftest composite_frames ({'opencv' if cv2 is not None else 'numpy'}): fondo Δ={err_out:.2f} "
          f"cambio Δ={err_in:.2f} shift=({rep[1]['dx']}, {rep[1]['dy']}) → {'OK' if ok else 'FALLA'}")
    return 0 if ok else 1


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("set_dir", nargs="?")
    ap.add_argument("files", nargs="*")
    ap.add_argument("--base")
    ap.add_argument("--out")
    ap.add_argument("--thresh", type=float, default=16.0, help="diferencia (0-255) que cuenta como cambio")
    ap.add_argument("--feather", type=float, default=9.0, help="suavizado del borde de la máscara (px)")
    ap.add_argument("--min-area", type=float, default=0.0004, help="isla mínima, fracción del cuadro")
    ap.add_argument("--roi", action="append", default=[],
                    help="x0,y0,x1,y1 en fracciones: solo se pega el cambio dentro (repetible). "
                         "Por dibujo: SET_DIR/rois.json {\"01.png\": [[x0,y0,x1,y1]], \"*\": [...]}")
    ap.add_argument("--chain", action="store_true", help="alinear cada dibujo con el anterior (cadenas largas)")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    if a.selftest:
        return selftest()
    rois = {}
    if a.roi:
        rois["*"] = [[float(v) for v in r.split(",")] for r in a.roi]
    if cv2 is None:
        print("  · sin OpenCV: solo traslación (usa ~/.config/edit-video/venv-caras/bin/python)", file=sys.stderr)
    if a.base:
        base = Path(a.base)
        draws = [Path(x) for x in ([a.set_dir] if a.set_dir else []) + a.files]
        out = Path(a.out or base.parent / "steady")
    else:
        if not a.set_dir:
            ap.error("falta SET_DIR o --base")
        d = Path(a.set_dir)
        files = sorted(p for p in d.iterdir() if p.suffix.lower() in EXTS and ".mask" not in p.name)
        base, draws = files[0], files[1:]
        out = Path(a.out or d / "steady")
        if (d / "rois.json").exists():
            rois.update(json.loads((d / "rois.json").read_text()))
    composite(base, draws, out, a.thresh, a.feather, a.min_area, rois, a.chain)
    return 0


if __name__ == "__main__":
    sys.exit(main())
