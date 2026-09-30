#!/usr/bin/env python3
"""caras — dónde está la cara y quién habla, para el recorte vertical automático (`--fit auto`).

Corre en un entorno AISLADO (nunca el python del sistema): MediaPipe (detector de rango
completo + Face Landmarker) + OpenCV. Probado con mediapipe 0.10.21 (la 1.0.x falla en macOS con
"graph_service: Service is unavailable").
clipper.py (solo librería estándar) lo llama por subproceso y usa el JSON que devuelve.

    python -m venv ~/.config/edit-video/venv-caras
    ~/.config/edit-video/venv-caras/bin/pip install mediapipe==0.10.21
    ~/.config/edit-video/venv-caras/bin/python caras.py VIDEO --start 12 --end 40 --out cam.json

Qué hace:
  1. Muestrea el tramo a ~6 fps y detecta hasta 4 caras (landmarks + blendshape `jawOpen`).
  2. Sigue cada cara en el tiempo (pistas por posición).
  3. Hablante activo = la cara cuya boca más se mueve en una ventana de 1.5 s. Con histéresis:
     solo cambia si el otro lleva ≥ 0.8 s moviendo más la boca (evita saltos por un "ajá").
  4. Si todas las caras caben en el recorte 9:16, encuadra al grupo en vez de cortar entre ellas.
  5. Cámara virtual: zona muerta + suavizado dentro de cada hablante; CORTE seco al cambiar de
     hablante (como un editor, no un paneo).
  6. Cuadro para la miniatura: en los primeros 4 s, la cara del hablante más grande y más expresiva.

Salida (JSON): {w, h, modo, camino: [[t, cx], …], cortes: [t, …], hablantes, thumb_t, muestras}
t en segundos absolutos del video fuente; cx = centro horizontal del encuadre (0–1).
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path

MODEL_URL = ("https://storage.googleapis.com/mediapipe-models/face_landmarker/"
             "face_landmarker/float16/1/face_landmarker.task")
MODEL = Path(os.environ.get("EDIT_VIDEO_FACE_MODEL",
                            Path.home() / ".config" / "edit-video" / "modelos" / "face_landmarker.task"))


def modelo() -> Path:
    if not MODEL.exists():
        MODEL.parent.mkdir(parents=True, exist_ok=True)
        print(f"caras: bajando el modelo de MediaPipe a {MODEL}…", file=sys.stderr)
        urllib.request.urlretrieve(MODEL_URL, MODEL)
    return MODEL


def detectar(video: str, start: float, end: float, fps: float, max_caras: int) -> tuple[list, int, int]:
    """Detector de rango completo (caras chicas de plano abierto, hasta ~5 m) sobre el cuadro, y
    Face Landmarker sobre el recorte de cada cara para medir la boca (`jawOpen`)."""
    import cv2
    import mediapipe as mp
    from mediapipe.tasks.python import BaseOptions, vision

    cap = cv2.VideoCapture(video)
    if not cap.isOpened():
        sys.exit(f"caras: no pude abrir {video}")
    W = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH)); H = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
    det = mp.solutions.face_detection.FaceDetection(model_selection=1, min_detection_confidence=0.5)
    lm = vision.FaceLandmarker.create_from_options(vision.FaceLandmarkerOptions(
        base_options=BaseOptions(model_asset_path=str(modelo())),
        running_mode=vision.RunningMode.IMAGE, num_faces=1, output_face_blendshapes=True,
        min_face_detection_confidence=0.3, min_face_presence_confidence=0.3))
    vfps = cap.get(cv2.CAP_PROP_FPS) or 30.0
    idx = int(max(start, 0) * vfps)
    cap.set(cv2.CAP_PROP_POS_FRAMES, idx)     # por cuadro, no por ms: el seek por ms falla en .mov/.mp4 de iPhone
    muestras, sig = [], start
    escala = 960 / W if W > 960 else 1.0
    while True:
        t = idx / vfps; idx += 1
        ok, frame = cap.read()
        if not ok or t > end:
            break
        if t + 1e-3 < sig:
            continue
        sig = t + 1 / fps
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        chico = cv2.resize(rgb, None, fx=escala, fy=escala, interpolation=cv2.INTER_AREA) if escala != 1 else rgb
        r = det.process(chico)
        caras = []
        for d in (r.detections or [])[:max_caras]:
            bb = d.location_data.relative_bounding_box
            cx, cy, w, h = bb.xmin + bb.width / 2, bb.ymin + bb.height / 2, bb.width, bb.height
            if w < 0.03:
                continue
            # boca: landmarker sobre el recorte ampliado de la cara, a resolución completa
            x0 = int(max(0, (cx - w) * W)); x1 = int(min(W, (cx + w) * W))
            y0 = int(max(0, (cy - h) * H)); y1 = int(min(H, (cy + h) * H))
            jaw = 0.0
            if x1 - x0 > 16 and y1 - y0 > 16:
                crop = cv2.resize(rgb[y0:y1, x0:x1], (256, 256), interpolation=cv2.INTER_LINEAR)
                res = lm.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=crop))
                if res.face_blendshapes:
                    jaw = next((c.score for c in res.face_blendshapes[0] if c.category_name == "jawOpen"), 0.0)
            caras.append({"cx": round(cx, 4), "cy": round(cy, 4), "w": round(w, 4), "jaw": round(float(jaw), 4)})
        muestras.append({"t": round(t, 3), "caras": caras})
    cap.release(); lm.close(); det.close()
    return muestras, W, H


def pistas(muestras: list) -> int:
    """Asigna un id estable a cada cara por cercanía horizontal. Devuelve cuántas pistas hubo."""
    tr, n = [], 0
    for m in muestras:
        libres = [p for p in tr if m["t"] - p["t"] < 3.0]   # solo pistas vivas (bug real: una pista
        # vieja en la misma x ganaba el "más cercano" y cada muestra abría una pista nueva)
        for c in sorted(m["caras"], key=lambda c: -c["w"]):
            best = min(libres, key=lambda p: abs(p["x"] - c["cx"]), default=None)
            lim = max(0.12, 0.5 * c["w"] + 0.05)          # una cara grande (primer plano) se mueve más
            if best and abs(best["x"] - c["cx"]) < lim:
                c["id"] = best["id"]; best["x"] = c["cx"]; best["t"] = m["t"]; libres.remove(best)
            else:
                c["id"] = n; tr.append({"id": n, "x": c["cx"], "t": m["t"]}); n += 1
    return n


def actividad(muestras: list, i: int, pid: int, ventana: float = 0.75) -> float:
    t0 = muestras[i]["t"]; prev = None; acc = 0.0; k = 0
    for m in muestras:
        if abs(m["t"] - t0) > ventana:
            continue
        c = next((c for c in m["caras"] if c.get("id") == pid), None)
        if c is None:
            prev = None; continue
        if prev is not None:
            acc += abs(c["jaw"] - prev); k += 1
        prev = c["jaw"]
    return acc / k if k else 0.0


def camara(muestras: list, W: int, H: int, retener: float = 0.8) -> dict:
    ancho = min(1.0, (H * 9 / 16) / W)          # fracción del ancho que ocupa el recorte 9:16
    n_pistas = pistas(muestras)
    def objetivo(caras, sujeto):
        if sujeto == "grupo":
            if len(caras) < 2:
                return None
            lo = min(c["cx"] - c["w"] / 2 for c in caras); hi = max(c["cx"] + c["w"] / 2 for c in caras)
            return (lo + hi) / 2 if hi - lo <= ancho * 0.9 else None
        c = next((c for c in caras if c["id"] == sujeto), None)
        return c["cx"] if c else None

    actual, pendiente, desde, visto, ult_obj, ult_cambio = None, None, 0.0, -1e9, None, -1e9
    objetivos, quien = [], []
    for i, m in enumerate(muestras):
        caras, t = m["caras"], m["t"]
        cand = None
        if caras:
            if objetivo(caras, "grupo") is not None:          # caben todas: encuadre de grupo
                cand = "grupo"
            else:
                act = {c["id"]: actividad(muestras, i, c["id"]) for c in caras}
                cand = max(act, key=act.get)
                if actual in act and act[cand] < act[actual] * 1.3 + 0.0008:
                    cand = actual
                # una cara con la boca quieta (o de perfil: el landmarker no ve su boca) no le roba
                # el plano a quien estaba hablando y el detector perdió un momento
                if act[cand] < 0.001 and actual not in (None, "grupo", cand) and t - visto < 3.0:
                    cand = None
        o_act = objetivo(caras, actual) if actual is not None else None
        if o_act is not None:
            visto = t
        antes = actual
        if actual is None and cand is not None:
            actual, pendiente = cand, None
        elif t - ult_cambio < 1.0:
            pass                                            # 1 s mínimo entre cortes: nunca un parpadeo
        elif cand is not None and cand != actual:
            if o_act is None and t - visto > 1.5:          # el sujeto se fue (cambio de plano)
                actual, pendiente = cand, None
            elif o_act is not None:
                if pendiente != cand:
                    pendiente, desde = cand, t
                elif t - desde >= retener:                  # el otro lleva rato hablando
                    actual, pendiente = cand, None
        else:
            pendiente = None
        if actual != antes:
            ult_cambio = t
        o = objetivo(caras, actual) if actual is not None else None
        if o is not None:
            ult_obj = o
        objetivos.append(ult_obj); quien.append(actual)
    # cámara virtual: corte seco al cambiar de sujeto; dentro, zona muerta + suavizado
    camino, cortes, cam, antes = [], [], None, object()
    ult = next((o for o in objetivos if o is not None), 0.5)
    for m, o, q in zip(muestras, objetivos, quien):
        o = ult if o is None else o; ult = o
        if cam is None or q != antes:
            if cam is not None and abs(o - cam) > 0.02:
                cortes.append(m["t"])
            cam = o
        elif abs(o - cam) > 0.035:
            cam += 0.25 * (o - cam)
        antes = q
        camino.append([m["t"], round(min(max(cam, ancho / 2), 1 - ancho / 2), 4)])
    # miniatura: primeros 4 s, cara grande con la boca abierta (expresiva)
    t_ini = muestras[0]["t"] if muestras else 0
    mejor, thumb_t = -1.0, None
    for m in muestras:
        if m["t"] > t_ini + 4:
            break
        for c in m["caras"]:
            s = c["w"] * (0.35 + c["jaw"])
            if s > mejor:
                mejor, thumb_t = s, m["t"]
    con_caras = sum(1 for m in muestras if m["caras"])
    modo = "sin_caras" if not con_caras else ("hablante" if cortes else "cara")
    linea = []
    for m, q in zip(muestras, quien):
        if not linea or linea[-1][1] != q:
            linea.append([m["t"], q])
    return {"w": W, "h": H, "modo": modo, "camino": camino, "cortes": cortes, "sujetos": linea,
            "hablantes": n_pistas, "thumb_t": thumb_t, "muestras": len(muestras),
            "con_caras": con_caras}


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("video"); ap.add_argument("--start", type=float, default=0.0)
    ap.add_argument("--end", type=float, default=1e9); ap.add_argument("--out")
    ap.add_argument("--fps", type=float, default=6.0); ap.add_argument("--max-caras", type=int, default=4)
    a = ap.parse_args()
    muestras, W, H = detectar(a.video, a.start, a.end, a.fps, a.max_caras)
    res = camara(muestras, W, H)
    txt = json.dumps(res, ensure_ascii=False)
    if a.out:
        Path(a.out).write_text(txt, encoding="utf-8")
    else:
        print(txt)
    print(f"caras: {res['muestras']} muestras · {res['con_caras']} con cara · {res['hablantes']} pistas · "
          f"modo {res['modo']} · {len(res['cortes'])} cortes de hablante", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
