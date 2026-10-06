#!/usr/bin/env python3
"""
clipper — de video largo a clips verticales listos para publicar.

Diseño en fases, a propósito:

  0. `fetch`    → opcional: baja el video de YouTube o cualquier sitio soportado.
  1. `analyze`  → trabajo de máquina: transcribe con marcas de tiempo por palabra.
  2. (criterio) → un humano o un agente lee la transcripción y elige los momentos.
  3. `render`   → trabajo de máquina: corta, reencuadra, subtitula y normaliza.

La fase 2 NO se automatiza con heurísticas de silencio. Elegir qué momento vale
la pena es criterio, y el criterio se delega a quien tiene contexto.

Extras: `dict` (diccionario permanente de nombres) y `tighten` (tramos sin silencios).
El idioma se detecta o se verifica antes de transcribir; nunca se asume.

Requisitos: ffmpeg (con libass), whisper. Opcional: yt-dlp para `fetch`.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from dataclasses import dataclass, asdict, field
from pathlib import Path

WHISPER = os.environ.get("CLIPPER_WHISPER", "whisper")
def _conf(key: str) -> str | None:
    """Lee KEY="valor" de ~/.config/edit-video/config (lo escribe sync.sh / el instalador)."""
    f = Path.home() / ".config" / "edit-video" / "config"
    try:
        for line in f.read_text(encoding="utf-8").splitlines():
            if line.startswith(key + "="):
                return line.split("=", 1)[1].strip().strip('"').strip("'") or None
    except OSError:
        pass
    return None


# FFmpeg: variable de entorno → config de edit-video (p. ej. un FFmpeg con libass aparte) → PATH.
FFMPEG = os.environ.get("CLIPPER_FFMPEG") or _conf("EDIT_VIDEO_FFMPEG") or "ffmpeg"
FFPROBE = os.environ.get("CLIPPER_FFPROBE") or _conf("EDIT_VIDEO_FFPROBE") or "ffprobe"
YTDLP = os.environ.get("CLIPPER_YTDLP", "yt-dlp")

# Límites de duración por plataforma, en segundos.
PLATFORMS = {
    "reels": ("Instagram Reels", 90),
    "shorts": ("YouTube Shorts", 180),
    "tiktok": ("TikTok", 600),
    "x": ("X / Twitter", 140),
}


# ---------------------------------------------------------------- utilidades

def die(msg: str, code: int = 1):
    print(f"error: {msg}", file=sys.stderr)
    sys.exit(code)


def need(binary: str):
    if shutil.which(binary) is None:
        die(f"no encontré '{binary}' en el PATH")


def run(cmd: list[str], quiet: bool = True) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        stdout=subprocess.DEVNULL if quiet else None,
        stderr=subprocess.DEVNULL if quiet else None,
        check=False,
    )


def duration_of(path: Path) -> float:
    p = subprocess.run(
        [FFPROBE, "-v", "error", "-show_entries", "format=duration",
         "-of", "default=nw=1:nk=1", str(path)],
        capture_output=True, text=True, check=False,
    )
    try:
        return float(p.stdout.strip())
    except ValueError:
        return 0.0


def font_name() -> str:
    """Devuelve una familia de fuente que exista en el sistema."""
    for candidate in ("Noto Sans", "DejaVu Sans", "Liberation Sans", "Arial"):
        p = subprocess.run(["fc-match", candidate, "-f", "%{family}"],
                           capture_output=True, text=True, check=False)
        got = (p.stdout or "").strip()
        if got and candidate.split()[0].lower() in got.lower():
            return got.split(",")[0]
    return "sans-serif"


FONT = font_name()


def video_fingerprint(path: Path) -> str:
    """Huella rápida: tamaño + primeros y últimos 1 MB. Evita leer archivos enormes."""
    size = path.stat().st_size
    h = hashlib.sha256(str(size).encode())
    with path.open("rb") as f:
        h.update(f.read(1024 * 1024))
        if size > 2 * 1024 * 1024:
            f.seek(-1024 * 1024, os.SEEK_END)
            h.update(f.read(1024 * 1024))
    return h.hexdigest()[:16]


def ass_time(seconds: float) -> str:
    s = max(0.0, seconds)
    h, rem = divmod(int(s), 3600)
    m, sec = divmod(rem, 60)
    cs = int(round((s - int(s)) * 100))
    if cs == 100:
        cs, sec = 0, sec + 1
    return f"{h:d}:{m:02d}:{sec:02d}.{cs:02d}"


def ass_escape(text: str) -> str:
    return text.replace("\\", "\\\\").replace("{", "(").replace("}", ")").strip()


# ---------------------------------------------------------------- idioma

# Whisper acepta código o nombre; normalizamos a nombre en minúsculas para comparar.
LANG_NAMES = {
    "es": "spanish", "en": "english", "pt": "portuguese", "fr": "french",
    "it": "italian", "de": "german", "ca": "catalan", "nl": "dutch",
    "ja": "japanese", "zh": "chinese", "ko": "korean", "ru": "russian",
}


def lang_name(lang: str) -> str:
    l = (lang or "").strip().lower()
    return LANG_NAMES.get(l, l)


def detect_language(wav: Path, total: float) -> str | None:
    """Detecta el idioma con 30 s de audio y el modelo tiny.

    Se toma desde el 10 % del video (máx. 60 s) para esquivar intros y música.
    Devuelve el nombre en minúsculas ("english") o None si no se pudo — nunca adivina.
    """
    ss = min(60.0, total * 0.10)
    with tempfile.TemporaryDirectory(prefix="clipper-lang-") as td:
        sample = Path(td) / "lang.wav"
        run([FFMPEG, "-y", "-ss", f"{ss:.2f}", "-t", "30", "-i", str(wav),
             "-ar", "16000", "-ac", "1", str(sample)])
        if not sample.exists():
            return None
        p = subprocess.run([WHISPER, str(sample), "--model", "tiny",
                            "--output_format", "txt", "--output_dir", td,
                            "--fp16", "False"],
                           capture_output=True, text=True, check=False)
    m = re.search(r"Detected language:\s*([A-Za-z ]+)", (p.stdout or "") + (p.stderr or ""))
    return m.group(1).strip().lower() if m else None


# ---------------------------------------------------------------- diccionario

def _config_value(key: str) -> str | None:
    conf = Path.home() / ".config/edit-video/config"
    if conf.exists():
        m = re.search(rf'{key}="([^"]*)"', conf.read_text(encoding="utf-8"))
        if m:
            return m.group(1)
    return None


def dictionary_layers(cliente: str | None, project: Path | None) -> list[Path]:
    """Capas del diccionario permanente; la última gana.

    1. ~/clipper-studio/dictionary.json   (el que edita Clipper Studio; CLIPPER_DICT lo cambia)
    2. ~/.config/edit-video/diccionario.json   (compartido con /edit-video)
    3. <área de clientes>/clients/<cliente>/diccionario.json   (privado: marcas, nombres)
    4. <carpeta del video>/diccionario.json
    """
    layers = [Path(os.environ.get("CLIPPER_DICT",
                                  str(Path.home() / "clipper-studio" / "dictionary.json"))),
              Path.home() / ".config/edit-video/diccionario.json"]
    if cliente:
        area = os.environ.get("EDIT_VIDEO_CLIENTS") or _config_value("EDIT_VIDEO_CLIENTS") \
            or str(Path.home() / ".agents/edit-video-clients")
        layers.append(Path(area) / "clients" / cliente / "diccionario.json")
    if project:
        layers.append(project / "diccionario.json")
    return layers


def load_dictionary(cliente: str | None, project: Path | None) -> dict:
    fixes = {}
    for p in dictionary_layers(cliente, project):
        try:
            fixes.update(json.loads(p.read_text(encoding="utf-8")))
        except (OSError, json.JSONDecodeError):
            pass
    return {k: v for k, v in fixes.items() if k.strip() and k != v}


_norm = lambda t: re.sub(r"[^\w']+", "", t.lower())
_edge = re.compile(r"^(\W*)(.*?)(\W*)$", re.S)


def apply_dictionary(segs: list[dict], fixes: dict) -> int:
    """Corrige nombres en texto Y en palabras, con palabra completa.

    - "sol" nunca toca "girasol" (límite de palabra).
    - Correcciones de varias palabras ("near Turing" → "nearshoring") funden los
      tokens de `words` y conservan el inicio del primero y el final del último,
      para que el subtítulo palabra por palabra también salga bien.
    Idempotente: se puede aplicar en analyze y otra vez en render.
    """
    if not fixes:
        return 0
    rules = sorted(((k.split(), v) for k, v in fixes.items()), key=lambda r: -len(r[0]))
    n = 0
    for seg in segs:
        for bad, good in fixes.items():
            pat = re.compile(r"(?<!\w)" + r"\s+".join(map(re.escape, bad.split())) + r"(?!\w)", re.I)
            seg["text"], k = pat.subn(good, seg.get("text", ""))
            if not seg.get("words"):
                n += k
        ws, out, i = seg.get("words") or [], [], 0
        while i < len(ws):
            hit = None
            for toks, good in rules:
                k = len(toks)
                if i + k <= len(ws) and all(_norm(ws[i + j]["w"]) == _norm(toks[j]) for j in range(k)):
                    hit = (k, good)
                    break
            if not hit:
                out.append(ws[i]); i += 1
                continue
            k, good = hit
            lead = _edge.match(ws[i]["w"]).group(1)
            trail = _edge.match(ws[i + k - 1]["w"]).group(3)
            new = f"{lead}{good}{trail}"
            if new != ws[i]["w"] or k > 1:
                n += 1
            out.append({"w": new, "start": ws[i]["start"], "end": ws[i + k - 1]["end"]})
            i += k
        if ws:
            seg["words"] = out
    return n


def cmd_dict(args) -> int:
    if args.accion == "ver":
        for k, v in sorted(load_dictionary(args.cliente, Path.cwd()).items()):
            print(f"{k}  →  {v}")
        return 0
    if not (args.mal and args.bien):
        die('uso: clipper.py dict agregar "mal escrito" "Bien Escrito" [--cliente SLUG]')
    layers = dictionary_layers(args.cliente, None)
    target = layers[-1] if args.cliente else layers[0]
    target.parent.mkdir(parents=True, exist_ok=True)
    try:
        d = json.loads(target.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        d = {}
    d[args.mal] = args.bien
    target.write_text(json.dumps(dict(sorted(d.items(), key=lambda x: x[0].lower())),
                                 ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"✓ {args.mal!r} → {args.bien!r}  en {target}")
    return 0


# ---------------------------------------------------------------- fetch

def cmd_fetch(args) -> int:
    """Baja un video de YouTube, Reels, TikTok, X o cualquier sitio de yt-dlp."""
    need(YTDLP)
    outdir = Path(args.outdir).expanduser().resolve() if args.outdir else Path.cwd()
    outdir.mkdir(parents=True, exist_ok=True)

    tmpl = str(outdir / "%(title).80s-%(id)s.%(ext)s")
    cmd = [YTDLP, "--no-playlist", "--restrict-filenames",
           "--merge-output-format", "mp4", "-o", tmpl]

    if args.cookies_from_browser:
        cmd += ["--cookies-from-browser", args.cookies_from_browser]
    if args.cookies:
        cmd += ["--cookies", str(Path(args.cookies).expanduser())]

    cmd += ["-f", args.format or
            "bv*[vcodec^=avc1][height<=1080]+ba[acodec^=mp4a]/"
            "bv*[height<=1080]+ba/b[height<=1080]/b"]
    cmd += ["--print", "after_move:filepath", args.url]

    print(f"bajando {args.url}")
    p = subprocess.run(cmd, capture_output=True, text=True, check=False)

    path = None
    for line in (p.stdout or "").splitlines():
        line = line.strip()
        if line and Path(line).exists():
            path = Path(line)

    if p.returncode != 0 or path is None:
        err = (p.stderr or "").strip().splitlines()
        print("  no se pudo bajar:", file=sys.stderr)
        for l in err[-6:]:
            print(f"    {l}", file=sys.stderr)
        if any("sign in" in l.lower() or "bot" in l.lower() for l in err):
            print("\n  YouTube bloquea IPs de centro de datos. Opciones:", file=sys.stderr)
            print("    --cookies-from-browser chrome   (desde tu máquina)", file=sys.stderr)
            print("    --cookies cookies.txt           (exportadas del navegador)", file=sys.stderr)
        return 1

    print(f"  {path.name}")
    print(f"  {duration_of(path)/60:.1f} min · {path.stat().st_size/1e6:.1f} MB")

    if args.analyze:
        print()
        ns = argparse.Namespace(video=str(path), model=args.model,
                                lang=args.lang, out=None, words=True, force=False,
                                force_lang=False, cliente=getattr(args, "cliente", None))
        return cmd_analyze(ns)

    print(f"\nsigue:  clipper.py analyze '{path.name}'")
    return 0


# ---------------------------------------------------------------- analyze

@dataclass
class Segment:
    idx: int
    start: float
    end: float
    text: str
    words: list = field(default_factory=list)


def resolve_language(wav: Path, total: float, lang: str, force: bool) -> str:
    """auto → detecta. Dado → verifica. Nunca transcribe en el idioma equivocado.

    Error real que esto evita: inglés transcrito como español, 50 minutos perdidos.
    """
    if force and lang != "auto":
        return lang
    print("  detectando idioma (30 s, modelo tiny)…", flush=True)
    det = detect_language(wav, total)
    if lang == "auto":
        if not det:
            die("no pude detectar el idioma. Pásalo con --lang es|en|pt…", 2)
        print(f"  idioma detectado: {det}")
        return det
    if det and lang_name(det) != lang_name(lang):
        die(f"pediste '{lang}' pero el audio suena a '{det}'. "
            f"Repite con --lang {det}, o --force-lang si estás seguro.", 3)
    if det:
        print(f"  idioma verificado: {det}")
    return lang


def transcribe(video: Path, workdir: Path, model: str, lang: str,
               words: bool, force_lang: bool = False) -> tuple[list[Segment], str]:
    wav = workdir / "audio.wav"
    print("  extrayendo audio…", flush=True)
    rc = run([FFMPEG, "-y", "-i", str(video), "-ar", "16000", "-ac", "1",
              "-c:a", "pcm_s16le", str(wav)])
    if rc.returncode != 0 or not wav.exists():
        die("ffmpeg no pudo extraer el audio")
    lang = resolve_language(wav, duration_of(video), lang, force_lang)

    cmd = [WHISPER, str(wav), "--model", model, "--language", lang,
           "--task", "transcribe", "--output_format", "json",
           "--output_dir", str(workdir), "--fp16", "False"]
    if words:
        cmd += ["--word_timestamps", "True"]

    print(f"  transcribiendo (modelo {model}"
          f"{', palabra por palabra' if words else ''})… esto tarda", flush=True)
    run(cmd)

    js = workdir / "audio.json"
    if not js.exists():
        die("whisper no produjo transcripción")

    data = json.loads(js.read_text(encoding="utf-8"))
    segs = []
    for i, s in enumerate(data.get("segments", []), start=1):
        txt = (s.get("text") or "").strip()
        if not txt:
            continue
        ws = []
        for w in (s.get("words") or []):
            t = (w.get("word") or "").strip()
            if not t:
                continue
            try:
                ws.append({"w": t, "start": float(w["start"]), "end": float(w["end"])})
            except (KeyError, TypeError, ValueError):
                continue
        segs.append(Segment(i, float(s["start"]), float(s["end"]), txt, ws))
    return segs, lang


def cmd_analyze(args) -> int:
    need(FFMPEG); need(FFPROBE); need(WHISPER)
    video = Path(args.video).expanduser().resolve()
    if not video.exists():
        die(f"no existe {video}")

    out = Path(args.out).expanduser().resolve() if args.out else \
        video.parent / f"{video.stem}.transcript.json"
    out.parent.mkdir(parents=True, exist_ok=True)

    fp = video_fingerprint(video)

    # Caché: si ya transcribimos este mismo archivo, no repetimos whisper.
    if out.exists() and not args.force:
        try:
            prev = json.loads(out.read_text(encoding="utf-8"))
            if prev.get("fingerprint") == fp:
                n = prev.get("segment_count", 0)
                has_w = any(s.get("words") for s in prev.get("segments", []))
                if not args.words or has_w:
                    print(f"transcripción en caché ({n} segmentos)")
                    print(f"  {out}")
                    print("  usa --force para rehacerla")
                    return 0
        except (json.JSONDecodeError, OSError):
            pass

    total = duration_of(video)
    print(f"analizando {video.name}  ({total/60:.1f} min)")

    with tempfile.TemporaryDirectory(prefix="clipper-") as td:
        segs, lang = transcribe(video, Path(td), args.model, args.lang, args.words,
                                getattr(args, "force_lang", False))

    if not segs:
        die("la transcripción salió vacía")

    # Diccionario permanente: corrige nombres antes de que nadie lea la transcripción.
    segs_d = [asdict(s) for s in segs]
    fixed = apply_dictionary(segs_d, load_dictionary(getattr(args, "cliente", None), video.parent))
    if fixed:
        print(f"  diccionario: {fixed} correcciones")

    word_total = sum(len(s.words) for s in segs)
    payload = {
        "source": str(video),
        "fingerprint": fp,
        "duration_sec": round(total, 2),
        "model": args.model,
        "language": lang,
        "segment_count": len(segs),
        "word_count": sum(len(s["words"]) for s in segs_d),
        "segments": segs_d,
    }
    out.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")

    readable = out.with_suffix(".txt")
    lines = [f"# {video.name} · {total/60:.1f} min · {len(segs)} segmentos", ""]
    for s in segs_d:
        lines.append(f"[{s['start']:7.1f} → {s['end']:7.1f}]  {s['text']}")
    readable.write_text("\n".join(lines), encoding="utf-8")

    print("\nlisto:")
    print(f"  {out}")
    print(f"  {readable}   ← pásame este archivo para que elija los momentos")
    print(f"\n{len(segs)} segmentos"
          f"{f', {word_total} palabras con tiempo' if word_total else ''}"
          f", {total/60:.1f} minutos de material.")
    if getattr(args, "candidatos", True):
        escribir_candidatos(payload, out)
    return 0


# ---------------------------------------------------------------- subtítulos

ASS_HEADER = """[Script Info]
ScriptType: v4.00+
PlayResX: 1080
PlayResY: 1920
WrapStyle: 0
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Cap,{font},{cap_size},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,-1,0,0,0,100,100,0,0,1,7,0,2,60,60,{cap_margin},1
Style: Hook,{font},{hook_size},&H0000E5FF,&H0000E5FF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,6,0,8,70,70,190,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""


# Zona segura vertical: Reels/TikTok/Shorts tapan el 20 % inferior (y > 1536 en 1920) con el
# texto del post, el usuario y los botones. El subtítulo tiene que quedar por encima.
VERTICAL_CAP_MARGIN = 500
HIGHLIGHT = "&H0000E5FF&"          # amarillo (BGR de ASS), el mismo del gancho


def tighten_ranges(words: list[dict], start: float, end: float,
                   gap: float = 0.35, pad: float = 0.12) -> list[tuple[float, float]]:
    """Tramos a CONSERVAR dentro de [start, end], quitando silencios > gap.

    Solo corta ENTRE palabras (nunca dentro de una) y deja `pad` de aire a cada lado.
    Tiempos absolutos del video fuente.
    """
    inside = [w for w in words if w["end"] > start and w["start"] < end]
    if not inside:
        return [(start, end)]
    keep, a = [], start
    for w0, w1 in zip(inside, inside[1:]):
        if w1["start"] - w0["end"] > gap:
            keep.append((a, min(w0["end"] + pad, end)))
            a = max(w1["start"] - pad, start)
    keep.append((a, end))
    return [(x, y) for x, y in keep if y - x > 0.05]


def make_remap(keep: list[tuple[float, float]], start: float):
    """Tiempo absoluto del fuente → tiempo dentro del clip ya recortado."""
    def f(t: float) -> float:
        acc = 0.0
        for a, b in keep:
            if t < a:
                return acc
            if t <= b:
                return acc + (t - a)
            acc += b - a
        return acc
    return f if keep else (lambda t: t - start)


def chunk_words(words: list[dict], start: float, end: float,
                per_chunk: int, max_chars: int = 0) -> list[list[dict]]:
    """Agrupa palabras en bloques cortos — el estilo que domina en Reels.

    Además de `per_chunk` palabras, respeta `max_chars` para que el bloque QUEPA en una línea:
    un bloque largo ("Colombia, first nearshoring,") se salía por los dos lados del cuadro.
    """
    inside = [w for w in words if w["end"] > start and w["start"] < end]
    out, cur = [], []
    for w in inside:
        text_len = len(" ".join(x["w"] for x in cur + [w]))
        if cur and (len(cur) >= per_chunk or (max_chars and text_len > max_chars)):
            out.append(cur); cur = []
        cur.append(w)
    if cur:
        out.append(cur)
    return out


def build_ass(segs: list[dict], start: float, end: float, vertical: bool,
              hook: str | None, per_chunk: int, cap_scale: float = 1.0,
              out_h: int = 0, highlight: bool = True, remap=None) -> str:
    # El tamano base se define contra 720p horizontal / 1920 vertical.
    # Si el lienzo crece, la letra crece en proporcion para verse igual.
    prop = (out_h / 720.0) if (out_h and not vertical) else 1.0
    cap_size = int((96 if vertical else 54) * cap_scale * prop)
    hook_size = int((76 if vertical else 44) * cap_scale * prop)
    body = ASS_HEADER.format(font=FONT, cap_size=cap_size, hook_size=hook_size,
                             cap_margin=VERTICAL_CAP_MARGIN if vertical else int(90 * prop))
    T = remap or (lambda t: t - start)
    events = []

    all_words = []
    for s in segs:
        all_words.extend(s.get("words") or [])

    if all_words:
        # Caracteres que caben en una línea al tamaño actual (letra negrita ≈ 0.6 em de ancho).
        usable = (1080 - 2 * 60) if vertical else ((out_h * 16 // 9 if out_h else 1280) - 120)
        max_chars = max(8, int(usable / (cap_size * 0.6)))
        for grp in chunk_words(all_words, start, end, per_chunk, max_chars):
            a = T(max(grp[0]["start"], start))
            b = T(min(grp[-1]["end"], end))
            if b - a < 0.08:
                b = a + 0.08
            if not highlight:
                text = " ".join(ass_escape(w["w"]) for w in grp)
                events.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Cap,,0,0,0,,{text}")
                continue
            # Palabra activa resaltada: un evento por palabra, el bloque entero visible.
            for j, w in enumerate(grp):
                wa = a if j == 0 else T(w["start"])
                wb = b if j == len(grp) - 1 else T(grp[j + 1]["start"])
                if wb - wa < 0.02:
                    continue
                parts = [(f"{{\\1c{HIGHLIGHT}}}{ass_escape(x['w'])}{{\\1c&H00FFFFFF&}}"
                          if k == j else ass_escape(x["w"])) for k, x in enumerate(grp)]
                events.append(f"Dialogue: 0,{ass_time(wa)},{ass_time(wb)},Cap,,0,0,0,,"
                              f"{' '.join(parts)}")
    else:
        # Sin tiempos por palabra: caemos a subtítulo por segmento.
        for s in segs:
            s0, s1 = float(s["start"]), float(s["end"])
            if s1 <= start or s0 >= end:
                continue
            a = T(max(s0, start))
            b = T(min(s1, end))
            if b - a < 0.05:
                continue
            events.append(f"Dialogue: 0,{ass_time(a)},{ass_time(b)},Cap,,0,0,0,,"
                          f"{ass_escape(s['text'])}")

    if hook:
        h = ass_escape(hook.replace("|", " ")).replace("  ", " ")   # "serif|DISPLAY" es para el nivel 2
        events.insert(0, f"Dialogue: 1,{ass_time(0)},{ass_time(3.0)},Hook,,0,0,0,,{h}")

    return body + "\n".join(events) + "\n"


# ---------------------------------------------------------------- plantillas (niveles)
#
# Nivel 1 · Recorte    → build_ass() de arriba. Rápido, seguro.
# Nivel 2 · Editorial  → build_ass_editorial(): tipografía de estudio, paleta, caja en la palabra
#                        activa, rótulo, barra de progreso, gancho en dos líneas, grade suave.
# Nivel 3 · Estudio    → no se quema nada: corte limpio + propuesta para /edit-video (ver cmd_render).

HERE = Path(__file__).resolve().parent
FONTS_DIR = HERE / "fonts"
PLANTILLAS_DIR = HERE / "plantillas"
_METRICS = None


def metrics() -> dict:
    global _METRICS
    if _METRICS is None:
        try:
            _METRICS = json.loads((FONTS_DIR / "metrics.json").read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            _METRICS = {}
    return _METRICS


def text_w(text: str, fam: str, size: float, spacing: float = 0.0) -> float:
    """Ancho en píxeles tal como lo pinta libass (em = tamaño / (winAscent + winDescent))."""
    m = metrics().get(fam)
    if not m:
        return len(text) * size * 0.42
    em = size / m["win"]
    return sum(m["adv"].get(c, m["avg"]) for c in text) * em + spacing * max(len(text) - 1, 0)


def cell_top(fam: str, size: float, baseline: float) -> float:
    """y de \\pos con \\an7 para que la línea base caiga en `baseline`."""
    m = metrics().get(fam, {"win": 1.2, "winAscent": 0.95})
    return baseline - m["winAscent"] * size / m["win"]


def cap_h(fam: str, size: float) -> float:
    m = metrics().get(fam, {"win": 1.2, "cap": 0.72})
    return m["cap"] * size / m["win"]


def ass_color(hex_rgb: str, alpha: int = 0) -> str:
    h = hex_rgb.lstrip("#")
    r, g, b = h[0:2], h[2:4], h[4:6]
    return f"&H{alpha:02X}{b}{g}{r}".upper()


def _merge(a: dict, b: dict) -> dict:
    out = dict(a)
    for k, v in (b or {}).items():
        out[k] = _merge(out[k], v) if isinstance(v, dict) and isinstance(out.get(k), dict) else v
    return out


def load_plantilla(nivel: int, path: str | None, cliente: str | None) -> dict:
    """Plantilla del nivel → encima la del cliente (clients/<slug>/clipper.json) → encima --plantilla."""
    base = {}
    for f in sorted(PLANTILLAS_DIR.glob(f"{nivel}-*.json")):
        base = json.loads(f.read_text(encoding="utf-8"))
        break
    if cliente:
        area = os.environ.get("EDIT_VIDEO_CLIENTS") or _config_value("EDIT_VIDEO_CLIENTS") \
            or str(Path.home() / ".agents/edit-video-clients")
        cf = Path(area) / "clients" / cliente / "clipper.json"
        if cf.exists():
            extra = json.loads(cf.read_text(encoding="utf-8"))
            if extra.get("logo"):
                extra["logo"] = str((cf.parent / extra["logo"]).resolve())
            base = _merge(base, extra)
    if path:
        base = _merge(base, json.loads(Path(path).expanduser().read_text(encoding="utf-8")))
    base.setdefault("nivel", nivel)
    return base


def _rect(w: float, h: float) -> str:
    w, h = round(w), round(h)
    return f"m 0 0 l {w} 0 l {w} {h} l 0 {h}"


def build_ass_editorial(segs: list[dict], start: float, end: float, W: int, H: int,
                        clip: dict, P: dict, per_chunk: int, captions: bool,
                        remap=None, dur: float | None = None) -> str:
    """Nivel 2. Todo posicionado a mano con las métricas reales de las fuentes."""
    vertical = H > W
    k = (H / 1920) if vertical else (H / 1080)       # escala respecto al diseño base
    M = P.get("margen", 64) * (W / 1080 if vertical else W / 1920)
    C = P.get("colores", {})
    ink, acc, txt = C.get("tinta", "#111111"), C.get("acento", "#FFD23F"), C.get("texto", "#FFFFFF")
    T = remap or (lambda t: t - start)
    dur = dur if dur is not None else end - start
    FU = P.get("fuentes", {})
    D = FU.get("display", "Clipper Display")      # titulares y subtítulos
    S = FU.get("serif", "Clipper Serif")          # acento editorial (primera línea del gancho)
    MO = FU.get("mono", "Clipper Mono")           # rótulos
    X = "Clipper Text"
    for fam in (D, S, MO):
        if fam not in metrics():
            print(f"  aviso: la fuente '{fam}' no está en fonts/metrics.json; las medidas serán aproximadas")

    ev = []
    def add(layer, a, b, style, body):
        if b - a > 0.01:
            ev.append(f"Dialogue: {layer},{ass_time(a)},{ass_time(b)},{style},,0,0,0,,{body}")

    # Degradados de legibilidad (bandas de tinta con alfa creciente)
    if P.get("degradados", True):
        # Muchas bandas finas con curva suave (ease) y sin solaparse: sin escalones visibles.
        n = 48
        top_h, bot_y = (640 if vertical else 330) * k, (1150 if vertical else 700) * k
        ease = lambda u: u * u * (3 - 2 * u)
        for i in range(n):
            u = (i + 0.5) / n
            a_top = int(0x50 + (0xFF - 0x50) * ease(u))
            y0, y1 = round(top_h * i / n), round(top_h * (i + 1) / n)
            add(0, 0, dur, "Fx", f"{{\\an7\\pos(0,{y0})\\1c{ass_color(ink)}\\1a&H{a_top:02X}&\\p1}}{_rect(W, y1 - y0)}")
            a_bot = int(0xFF - (0xFF - 0x40) * ease(u))
            y0, y1 = round(bot_y + (H - bot_y) * i / n), round(bot_y + (H - bot_y) * (i + 1) / n)
            add(0, 0, dur, "Fx", f"{{\\an7\\pos(0,{y0})\\1c{ass_color(ink)}\\1a&H{a_bot:02X}&\\p1}}{_rect(W, y1 - y0)}")

    # Rótulo superior: raya de acento + texto mono; a la derecha, marca o fuente
    rot = P.get("rotulo", {})
    kick = (clip.get("kicker") or rot.get("izquierda") or "").upper()
    right = (clip.get("fuente") or rot.get("derecha") or "")
    ks = 30 * k
    kb = (200 if vertical else 92) * k
    if kick:
        add(3, 0, dur, "Fx", f"{{\\an7\\pos({M:.0f},{kb - cap_h(MO, ks) / 2 - 2 * k:.0f})\\1c{ass_color(acc)}\\p1}}{_rect(28 * k, 4 * k)}")
        add(3, 0, dur, "Fx", f"{{\\an7\\pos({M + 44 * k:.0f},{cell_top(MO, ks, kb):.0f})\\fn{MO}\\fs{ks:.0f}\\fsp{3 * k:.1f}\\1c{ass_color(txt)}\\bord{4 * k:.1f}\\3c{ass_color(ink)}\\3a&H90&\\blur{8 * k:.1f}\\shad0}}{ass_escape(kick)}")
    if right and not P.get("_logo"):
        rw = text_w(right, MO, ks * 0.92, 1.5 * k)
        add(3, 0, dur, "Fx", f"{{\\an7\\pos({W - M - rw:.0f},{cell_top(MO, ks * 0.92, kb):.0f})\\fn{MO}\\fs{ks * 0.92:.0f}\\fsp{1.5 * k:.1f}\\1c{ass_color(txt)}\\1a&H30&\\bord0\\shad0}}{ass_escape(right)}")

    # Barra de progreso (dentro de la zona segura)
    if P.get("barra_progreso", True):
        by, bw, bh = (1512 if vertical else 1040) * k, W - 2 * M, 4 * k
        add(1, 0, dur, "Fx", f"{{\\an7\\pos({M:.0f},{by:.0f})\\1c{ass_color(txt)}\\1a&HB0&\\p1}}{_rect(bw, bh)}")
        add(2, 0, dur, "Fx", f"{{\\an7\\pos({M:.0f},{by:.0f})\\1c{ass_color(acc)}\\fscx0\\t(0,{int(dur * 1000)},\\fscx100)\\p1}}{_rect(bw, bh)}")

    # Gancho: "serif|DISPLAY" — dos líneas arriba a la izquierda, entra subiendo
    hook = clip.get("hook")
    if hook:
        g = P.get("gancho", {})
        hd = float(g.get("duracion", 3.2))
        serif_t, disp_t = (hook.split("|", 1) + [""])[:2] if "|" in hook else ("", hook)
        disp_t = disp_t.strip().upper()
        ss, ds = g.get("serif", 96) * k, g.get("display", 150) * k
        while ds > 40 and text_w(disp_t, D, ds) > W - 2 * M:
            ds -= 4
        y = g.get("y", 300 if vertical else 170) * k   # gancho.y: subirlo/bajarlo si choca con la cabeza
        fade = "\\fad(200,250)"
        centro = g.get("alineacion", "izquierda") == "centro"
        hx = lambda w_: (W - w_) / 2 if centro else M
        if serif_t.strip():
            b1 = y + cap_h(S, ss)
            t1 = cell_top(S, ss, b1)
            sx = hx(text_w(serif_t.strip(), S, ss))
            add(4, 0, hd, "Fx", f"{{\\an7\\move({sx:.0f},{t1 + 24 * k:.0f},{sx:.0f},{t1:.0f},0,380){fade}\\fn{S}\\fs{ss:.0f}\\1c{ass_color(txt)}\\bord{4 * k:.1f}\\3c{ass_color(ink)}\\3a&H90&\\blur{8 * k:.1f}\\shad0}}{ass_escape(serif_t.strip())}")
            y = b1 + 22 * k
        b2 = y + cap_h(D, ds)
        t2 = cell_top(D, ds, b2)
        dx = hx(text_w(disp_t, D, ds))
        add(4, 0.08, hd, "Fx", f"{{\\an7\\move({dx:.0f},{t2 + 28 * k:.0f},{dx:.0f},{t2:.0f},0,420){fade}\\fn{D}\\fs{ds:.0f}\\1c{ass_color(txt)}\\bord{4 * k:.1f}\\3c{ass_color(ink)}\\3a&H90&\\blur{8 * k:.1f}\\shad0}}{ass_escape(disp_t)}")
        uw = max(text_w(disp_t, D, ds) * 0.45, 120 * k)
        ux = (W - uw) / 2 if centro else M
        add(4, 0.35, hd, "Fx", f"{{\\an7\\pos({ux:.0f},{b2 + 18 * k:.0f})\\1c{ass_color(acc)}\\fscx0\\t(0,350,\\fscx100){fade}\\p1}}{_rect(uw, 12 * k)}")

    # Subtítulos: bloque centrado, palabra activa sobre caja de acento con tinta
    all_words = [w for s in segs for w in (s.get("words") or [])]
    if captions and all_words:
        st = P.get("subtitulo", {})
        fs = st.get("tamano", 70) * k
        # vertical: por encima del 20 % inferior (Reels/TikTok); horizontal: 86 % del alto
        base = st.get("linea_base", 1400) * k if vertical else H * 0.86
        modo = st.get("activa", "caja")               # caja | color | subrayado
        box_on = modo == "caja"
        fam_sub = FU.get(st.get("fuente", "display"), st.get("fuente")) if st.get("fuente") else D
        if fam_sub not in metrics():
            fam_sub = D
        upper = bool(st.get("mayusculas", False))
        maxw = W - 2 * M - 24 * k
        per = int(st.get("palabras", per_chunk))
        # bloques: por palabras y por ancho real
        blocks, cur = [], []
        for w in [w for w in all_words if w["end"] > start and w["start"] < end]:
            test = cur + [w]
            if cur and (len(cur) >= per or text_w(" ".join(x["w"] for x in test), fam_sub, fs) > maxw):
                blocks.append(cur); cur = []
            cur.append(w)
        if cur:
            blocks.append(cur)
        sp = text_w(" ", fam_sub, fs)
        top = cell_top(fam_sub, fs, base)
        ch = cap_h(fam_sub, fs)
        cw = (lambda t_: t_.upper()) if upper else (lambda t_: t_)
        for grp in blocks:
            a = T(max(grp[0]["start"], start))
            b = T(min(grp[-1]["end"], end))
            if b - a < 0.08:
                b = a + 0.08
            widths = [text_w(cw(w["w"]), fam_sub, fs) for w in grp]
            total = sum(widths) + sp * (len(grp) - 1)
            x0 = W / 2 - total / 2
            xs, x = [], x0
            for wd in widths:
                xs.append(x); x += wd + sp
            for j, w in enumerate(grp):
                wa = a if j == 0 else T(w["start"])
                wb = b if j == len(grp) - 1 else T(grp[j + 1]["start"])
                if wb - wa < 0.02:
                    continue
                fin = "\\fad(90,0)" if j == 0 else ""
                if box_on:
                    px, py = 12 * k, 14 * k
                    bw_, bh_ = widths[j] + 2 * px, ch + 2 * py
                    cx, cy = xs[j] + widths[j] / 2, base - ch / 2
                    add(5, wa, wb, "Fx", f"{{\\an5\\pos({cx:.0f},{cy:.0f})\\1c{ass_color(acc)}\\fscx90\\fscy90\\t(0,90,\\fscx100\\fscy100){fin}\\p1}}{_rect(bw_, bh_)}")
                if modo == "subrayado":
                    add(5, wa, wb, "Fx", f"{{\\an7\\pos({xs[j]:.0f},{base + 12 * k:.0f})\\1c{ass_color(acc)}\\fscx0\\t(0,120,\\fscx100)\\p1}}{_rect(widths[j], 8 * k)}")
                parts = []
                for i2, x2 in enumerate(grp):
                    col = ass_color(ink) if (i2 == j and box_on) else (ass_color(acc) if (i2 == j and modo == "color") else ass_color(txt))
                    shadow = "\\bord0\\shad0\\blur0" if (i2 == j and box_on) else f"\\bord{3.5 * k:.1f}\\3c{ass_color(ink)}\\3a&H60&\\blur{3 * k:.1f}"
                    parts.append(f"{{\\1c{col}{shadow}}}{ass_escape(cw(x2['w']))}")
                add(6, wa, wb, "Fx", f"{{\\an7\\pos({x0:.0f},{top:.0f})\\fn{fam_sub}\\fs{fs:.0f}{fin}}}" + " ".join(parts))

    header = f"""[Script Info]
ScriptType: v4.00+
PlayResX: {W}
PlayResY: {H}
WrapStyle: 2
ScaledBorderAndShadow: yes

[V4+ Styles]
Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding
Style: Fx,{D},{int(70 * k)},&H00FFFFFF,&H00FFFFFF,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1

[Events]
Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text
"""
    return header + "\n".join(ev) + "\n"


def write_propuesta(clip: dict, segs: list[dict], start: float, end: float, video: Path,
                    out_mp4: Path, P: dict, cliente: str | None) -> Path:
    """Nivel 3: propuesta para aprobar ANTES de construir con /edit-video."""
    words = [w for s in segs for w in (s.get("words") or []) if w["end"] > start and w["start"] < end]
    lines, cur, c0 = [], [], None
    for w in words:
        if c0 is None:
            c0 = w["start"]
        cur.append(w["w"])
        if w["w"][-1:] in ".?!,;:" or len(cur) >= 8:
            lines.append((c0 - start, w["end"] - start, " ".join(cur))); cur, c0 = [], None
    if cur:
        lines.append((c0 - start, words[-1]["end"] - start, " ".join(cur)))
    stills = []
    for i, frac in enumerate((0.1, 0.5, 0.9), start=1):
        t = start + (end - start) * frac
        img = out_mp4.with_name(f"{out_mp4.stem}-cuadro{i}.jpg")
        run([FFMPEG, "-y", "-ss", f"{t:.2f}", "-i", str(video), "-frames:v", "1", "-q:v", "3", str(img)])
        if img.exists():
            stills.append((t - start, img.name))
    beat = "\n".join(f"| {a:5.2f} | {b:5.2f} | {txt} | | | |" for a, b, txt in lines)
    md = f"""# Propuesta · {clip.get('slug') or out_mp4.stem}  —  PENDIENTE DE APROBACIÓN

> Nivel 3 · Estudio. clipper cortó el tramo limpio (`{out_mp4.name}`, {end - start:.1f} s, sin subtítulos).
> El agente completa esta propuesta, la enseña con 2–3 cuadros de muestra y **espera el OK del
> director** antes de construir con `/edit-video` (HyperFrames). Nada se construye sin aprobación.

- **Fuente:** `{video.name}` · {start:.2f} → {end:.2f} s
- **Cliente:** {cliente or '—'} (reglas y kit en el área de clientes)
- **Intensidad:** {P.get('intensidad', 1)} · {(P.get('intensidades') or {}).get(str(P.get('intensidad', 1)), '')}{(' · énfasis ' + P['enfasis']) if P.get('enfasis') else ''} (tabla en `nivel-3.md` §0; recetas en `recetario-3.md`)
- **Por qué este momento:** {clip.get('why', '')}
- **Gancho:** {clip.get('hook', '')}

## 1 · Concepto (una frase)

## 2 · Estilo
Parte del kit del cliente si existe; si no, de la plantilla Editorial (tipografía, paleta papel /
tinta / acento, tokens de movimiento IN/OUT/MOVE). Nombra la referencia visual.

## 3 · Beat sheet (tiempos del clip)
| inicio | fin | palabras | qué aparece | dónde | sonido |
|---|---|---|---|---|---|
{beat}

## 4 · Gráficos únicos
Mapa, datos, lista, palabra detrás de la persona, cierre con personaje… (ver `motion-design.md`).

## 5 · Imágenes a generar (Higgsfield)
| para qué | prompt | formato |
|---|---|---|
| fondo / textura | | |

## 6 · Sonido
SFX por evento (niveles ≤ −16 dBFS, la voz manda). Música: ¿sí/no, cuál?

## 7 · Cuadros de referencia del metraje
""" + "\n".join(f"- {t:.1f} s → `{n}`" for t, n in stills) + """

---
**APROBACIÓN:** ☐ aprobado · ☐ cambios: ______________________
"""
    p = out_mp4.with_name(f"{out_mp4.stem}-PROPUESTA.md")
    p.write_text(md, encoding="utf-8")
    return p


# ---------------------------------------------------------------- recorte por cara / hablante activo

def caras_python() -> str | None:
    """El python del entorno aislado con MediaPipe (nunca el del sistema)."""
    c = os.environ.get("EDIT_VIDEO_CARAS_PY") or _conf("EDIT_VIDEO_CARAS_PY")
    for p in (c, str(Path.home() / ".config" / "edit-video" / "venv-caras" / "bin" / "python")):
        if p and Path(p).exists():
            return p
    return None


def camara_auto(video: Path, start: float, end: float) -> dict | None:
    """Corre caras.py (MediaPipe) sobre el tramo. None = no hay entorno o no hay caras → blur."""
    py = caras_python()
    if not py:
        print("  --fit auto: falta el entorno de caras (references/clipper.md § Recorte por cara); "
              "uso fondo difuminado")
        return None
    fd, out = tempfile.mkstemp(suffix=".json", prefix="clipper-cam-"); os.close(fd)
    try:
        rc = subprocess.run([py, str(HERE / "caras.py"), str(video), "--start", f"{start:.3f}",
                             "--end", f"{end:.3f}", "--out", out], stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE, text=True, check=False)
        d = json.loads(Path(out).read_text(encoding="utf-8")) if rc.returncode == 0 else None
    except (OSError, json.JSONDecodeError):
        d = None
    finally:
        Path(out).unlink(missing_ok=True)
    if not d:
        err = [l for l in (rc.stderr or "").splitlines() if l.strip() and not l.startswith(("W0", "I0", "INFO"))]
        print(f"  --fit auto: caras.py falló ({err[-1] if err else '?'}); uso fondo difuminado")
        return None
    if d.get("modo") == "sin_caras":
        return None
    return d


def cam_cx(d: dict, ts: float) -> float:
    """Centro del encuadre en el segundo `ts` (absoluto): lineal entre muestras, escalón en cortes."""
    cam, cortes = d["camino"], set(d.get("cortes") or [])
    if ts <= cam[0][0]:
        return cam[0][1]
    for (t0, c0), (t1, c1) in zip(cam, cam[1:]):
        if t0 <= ts < t1:
            return c0 if t1 in cortes else c0 + (c1 - c0) * (ts - t0) / max(t1 - t0, 1e-6)
    return cam[-1][1]


def cam_px(cx: float, sw: int) -> int:
    return int(min(max(round(cx * sw - 540), 0), sw - 1080))


def cam_sendcmd(d: dict, start: float, end: float, T, sw: int) -> str:
    """Comandos de sendcmd para mover crop@cam en el tiempo del clip (respeta --tighten vía T)."""
    lines, prev, k = [], None, 0
    while True:
        ts = start + k / 30.0
        if ts > end:
            break
        x = cam_px(cam_cx(d, ts), sw)
        if x != prev:
            lines.append(f"{max(T(ts), 0):.3f} crop@cam x {x};")
            prev = x
        k += 1
    return "\n".join(lines) + "\n"


# ---------------------------------------------------------------- miniaturas

def thumb_title(clip: dict, segs: list[dict]) -> str:
    """Titular de la miniatura: `titulo` > `hook` > las primeras palabras del clip."""
    t = (clip.get("titulo") or clip.get("hook") or "").strip()
    if t:
        return t
    s0 = float(clip["start"])
    ws = [w["w"] for sg in segs for w in (sg.get("words") or []) if w["start"] >= s0 - 0.05][:7]
    if not ws:
        ws = next((sg["text"] for sg in segs if float(sg["end"]) > s0), "").split()[:7]
    return " ".join(ws).rstrip(",;:")


def make_thumb(video: Path, clip: dict, segs: list[dict], out_mp4: Path, vertical: bool,
               fit: str, crop_x: float, nivel: int, P: dict) -> Path | None:
    """Miniatura por clip: el cuadro más representativo cerca del gancho + titular con la tipografía
    de la plantilla → `NN-slug-thumb.jpg` (1080×1920 vertical, 1280×720 horizontal).

    Cuadro: `thumb_t` (segundo absoluto) si el clip lo trae; si hay caras (`caras.py`, mejora del
    recorte), el de boca más abierta y cara más grande en los primeros 4 s; si no, el filtro
    `thumbnail` de FFmpeg sobre 16 cuadros de los primeros 4 s (evita parpadeos y transiciones)."""
    start, end = float(clip["start"]), float(clip["end"])
    fit = clip.get("fit", fit)
    crop_x = float(clip.get("crop_x", crop_x))
    W, H = (1080, 1920) if vertical else (1280, 720)
    out = out_mp4.with_name(f"{out_mp4.stem}-thumb.jpg")
    title = thumb_title(clip, segs)
    win = min(4.0, max(end - start, 0.5))
    t_at = clip.get("thumb_t")
    if t_at is None and clip.get("_thumb_t") is not None:
        t_at = clip["_thumb_t"]
    with tempfile.TemporaryDirectory(prefix="clipper-t-") as td:
        td = Path(td)
        frame = td / "f.png"
        if t_at is not None:
            cmd = [FFMPEG, "-y", "-ss", f"{float(t_at):.3f}", "-i", str(video), "-frames:v", "1", str(frame)]
        else:
            cmd = [FFMPEG, "-y", "-ss", f"{start:.3f}", "-t", f"{win:.3f}", "-i", str(video),
                   "-vf", "fps=4,thumbnail=16", "-frames:v", "1", str(frame)]
        run(cmd)
        if not frame.exists():
            return None
        # encuadre = el del clip
        if vertical and fit == "auto" and clip.get("_crop_px") is not None:
            vf = f"scale=-2:1920,crop=1080:1920:{clip['_crop_px']}:0"
        elif vertical and fit == "crop":
            cx = min(max(crop_x, 0.0), 1.0)
            vf = f"scale=-2:1920,crop=1080:1920:(iw-1080)*{cx:.3f}:0"
        elif vertical:
            vf = ("split=2[bg][fg];[bg]scale=1080:1920:force_original_aspect_ratio=increase,"
                  "crop=1080:1920,gblur=sigma=22[bgb];[fg]scale=1080:1920:"
                  "force_original_aspect_ratio=decrease[fgs];[bgb][fgs]overlay=(W-w)/2:(H-h)/2")
        else:
            vf = f"scale={W}:{H}:force_original_aspect_ratio=increase,crop={W}:{H}"
        if nivel == 2 and P.get("grade"):
            vf += "," + P["grade"]
        # legibilidad: sombra arriba, donde va el titular (abajo lo tapa la app)
        # degradado suave (12 bandas; sin bordes duros) de negro 45 % arriba a 0 en el 55 %
        vf += "".join(f",drawbox=x=0:y=0:w=iw:h=ih*{0.55 * (k + 1) / 12:.4f}:color=black@0.05:t=fill"
                      for k in range(12))
        (td / "t.ass").write_text(thumb_ass(title, W, H, nivel, P), encoding="utf-8")
        fdir = str(FONTS_DIR).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
        vf += f",ass=t.ass:fontsdir={fdir}"
        rc = subprocess.run([FFMPEG, "-y", "-i", str(frame), "-vf", vf, "-frames:v", "1",
                             "-q:v", "2", str(out)], cwd=td, stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE, text=True, check=False)
    if rc.returncode != 0 or not out.exists():
        print(f"      miniatura: FALLÓ ({(rc.stderr or '').strip().splitlines()[-1:] or ''})")
        return None
    return out


def thumb_ass(title: str, W: int, H: int, nivel: int, P: dict) -> str:
    """Titular grande en el tercio superior. Nivel 2: serif + display en acento ("Lo que|nadie te
    dice"); nivel 1: la fuente del sistema en negrita, blanco con contorno y la última línea amarilla."""
    vertical = H > W
    m = int(W * 0.07)
    top = int(H * (0.12 if vertical else 0.10))
    if nivel == 2:
        F = P.get("fuentes") or {}
        C = P.get("colores") or {}
        disp, serif = F.get("display", "Clipper Display"), F.get("serif", "Clipper Serif")
        acc = ass_color(C.get("acento", "#FFD23F"))
        txt = ass_color(C.get("texto", "#FFFFFF"))
        big = int((180 if vertical else 120) * (0.82 if len(title) > 24 else 1))
        small = int(big * 0.62)
        styles = (f"Style: A,{serif},{small},{txt},{txt},&H00000000,&H64000000,0,0,0,0,100,100,0,0,1,0,3,7,{m},{m},{top},1\n"
                  f"Style: B,{disp},{big},{acc},{acc},&H00000000,&H64000000,-1,0,0,0,100,100,-1,0,1,0,4,7,{m},{m},{top},1\n")
        if "|" in title:
            a, b = title.split("|", 1)
            text = f"{{\\rA}}{ass_escape(a.strip())}\\N{{\\rB}}{ass_escape(b.strip())}"
        else:
            text = f"{{\\rB}}{ass_escape(title)}"
    else:
        big = int((118 if vertical else 84) * (0.82 if len(title) > 30 else 1))
        styles = (f"Style: B,{FONT},{big},&H00FFFFFF,&H00FFFFFF,&H00000000,&H80000000,-1,0,0,0,100,100,0,0,1,9,3,8,{m},{m},{top},1\n")
        words = title.replace("|", " ").split()
        cut = max(1, len(words) * 2 // 3) if len(words) > 3 else len(words)
        head, tail = " ".join(words[:cut]), " ".join(words[cut:])
        text = ass_escape(head.upper()) + (f"\\N{{\\1c{HIGHLIGHT}}}{ass_escape(tail.upper())}" if tail else "")
    return (f"[Script Info]\nScriptType: v4.00+\nPlayResX: {W}\nPlayResY: {H}\nWrapStyle: 0\n"
            "ScaledBorderAndShadow: yes\n\n[V4+ Styles]\nFormat: Name, Fontname, Fontsize, PrimaryColour, "
            "SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, "
            "Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding\n"
            f"{styles}\n[Events]\nFormat: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text\n"
            f"Dialogue: 0,0:00:00.00,0:00:05.00,B,,0,0,0,,{text}\n")


# ---------------------------------------------------------------- render

def check_platform(dur: float) -> list[str]:
    warns = []
    for _, (label, limit) in PLATFORMS.items():
        if dur > limit:
            warns.append(f"{label} (máx {limit}s)")
    return warns


def watermark_chain(inlabel: str, vertical: bool, pos: str, scale: float,
                    shadow: bool, frame_w: int = 0) -> str:
    """Compone el logo sobre el video.

    Un logo blanco sobre fondo claro desaparece. Por eso, si `shadow` está
    activo, primero se pinta una copia ennegrecida y desenfocada del propio
    logo, desplazada unos pixeles. Da contorno sin ensuciar la marca.
    """
    fw = frame_w or (1080 if vertical else 1280)
    w = int(fw * scale)
    m = int(fw * 0.045)          # margen proporcional al cuadro

    xy = {
        "top-right": (f"W-w-{m}", f"{m}"),
        "top-left": (f"{m}", f"{m}"),
        "bottom-right": (f"W-w-{m}", f"H-h-{m}"),
        "bottom-left": (f"{m}", f"H-h-{m}"),
    }.get(pos, (f"W-w-{m}", f"{m}"))
    x, y = xy

    if not shadow:
        return (f";[1:v]scale={w}:-1[wm];"
                f"[{inlabel}][wm]overlay={x}:{y}[vo]")

    off = max(2, w // 90)
    return (
        f";[1:v]scale={w}:-1,split=2[wmf][wms];"
        f"[wms]colorchannelmixer=rr=0:rg=0:rb=0:gr=0:gg=0:gb=0:br=0:bg=0:bb=0,"
        f"boxblur=4:1[wsh];"
        f"[{inlabel}][wsh]overlay={x}+{off}:{y}+{off}[wbg];"
        f"[wbg][wmf]overlay={x}:{y}[vo]"
    )


def render_clip(video: Path, segs: list[dict], clip: dict, outdir: Path,
                vertical: bool, idx: int, per_chunk: int,
                normalize: bool, watermark: Path | None = None,
                wm_pos: str = "top-right", wm_scale: float = 0.22,
                wm_shadow: bool = True, cap_scale: float = 1.0,
                crf: int = 21, preset: str = "medium",
                out_h: int = 0, fit: str = "blur", crop_x: float = 0.5,
                cover_subs: float = 0.0, tighten: float = 0.0,
                captions: bool = True, highlight: bool = True,
                nivel: int = 1, P: dict | None = None) -> Path | None:
    start, end = float(clip["start"]), float(clip["end"])
    if end <= start:
        print(f"  clip {idx}: rango inválido, lo salto")
        return None

    slug = (clip.get("slug") or f"clip{idx:02d}").strip().replace(" ", "-")[:48]
    out = outdir / f"{idx:02d}-{slug}.mp4"
    hook = clip.get("hook")
    # Por clip se puede sobreescribir: el agente mira los frames y decide el encuadre.
    fit = clip.get("fit", fit)
    crop_x = float(clip.get("crop_x", crop_x))
    cover_subs = float(clip.get("cover_subs", cover_subs))
    tighten = float(clip.get("tighten", tighten))

    all_words = [w for sg in segs for w in (sg.get("words") or [])]
    keep = tighten_ranges(all_words, start, end, tighten) if tighten > 0 else []
    remap = make_remap(keep, start) if keep else None
    dur = sum(b - a for a, b in keep) if keep else end - start
    cut_note = f", {len(keep) - 1} silencios fuera ({end - start:.1f}→{dur:.1f}s)" \
        if keep and len(keep) > 1 else ""

    P = P or {}
    src_w = src_h = 0
    if vertical and fit == "auto":
        pr = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries",
                             "stream=width,height:stream_side_data=rotation", "-of", "csv=p=0:s=x",
                             str(video)], capture_output=True, text=True, check=False)
        try:
            src_w, src_h = (int(x) for x in pr.stdout.strip().splitlines()[0].split("x")[:2])
        except (ValueError, IndexError):
            src_w = src_h = 0
    if vertical:
        W, H = 1080, 1920
    elif out_h:
        W, H = int(out_h * 16 / 9) // 2 * 2, out_h
    else:
        pr = subprocess.run([FFPROBE, "-v", "error", "-select_streams", "v:0", "-show_entries",
                             "stream=width,height", "-of", "csv=p=0:s=x", str(video)],
                            capture_output=True, text=True, check=False)
        try:
            W, H = (int(x) for x in pr.stdout.strip().splitlines()[0].split("x"))
        except (ValueError, IndexError):
            W, H = 1920, 1080

    with tempfile.TemporaryDirectory(prefix="clipper-r-") as td:
        td = Path(td)
        ass = td / "s.ass"
        if nivel == 2:
            body = build_ass_editorial(segs, start, end, W, H, clip, P, per_chunk, captions,
                                       remap, dur)
        else:
            body = build_ass(segs if captions else [], start, end, vertical, hook,
                             per_chunk, cap_scale, out_h, highlight, remap)
        ass.write_text(body, encoding="utf-8")

        # Cadena de video: [src] → (silencios fuera) → (tapar subtítulos quemados) → encuadre → ass
        pre = "[0:v]"
        chain = []
        if keep and len(keep) > 1:
            sel = "+".join(f"between(t,{a - start:.3f},{b - start:.3f})" for a, b in keep)
            chain.append(f"{pre}select='{sel}',setpts=N/FRAME_RATE/TB[vt]")
            pre = "[vt]"
        if nivel == 2 and P.get("grade"):
            chain.append(f"{pre}{P['grade']}[vg]")
            pre = "[vg]"
        if cover_subs > 0:
            f = min(max(cover_subs, 0.02), 0.5)
            chain.append(f"{pre}split=2[cs0][cs1];[cs1]crop=iw:ih*{f:.3f}:0:ih*{1 - f:.3f},"
                         f"boxblur=24:3[band];[cs0][band]overlay=0:main_h*{1 - f:.3f}[vc]")
            pre = "[vc]"

        tail = "vo" if not watermark else "vsub"
        cam = None
        if vertical and fit == "auto":
            sw = int(round(src_w * 1920 / src_h / 2)) * 2 if src_h else 0
            if sw > 1100:
                cam = camara_auto(video, start, end)
            if cam:
                (td / "cam.cmd").write_text(cam_sendcmd(cam, start, end, remap or (lambda t: t - start), sw),
                                            encoding="utf-8")
                x0 = cam_px(cam_cx(cam, start), sw)
                chain.append(f"{pre}scale=-2:1920,sendcmd=f=cam.cmd,crop@cam=1080:1920:{x0}:0[v]")
                tt = cam.get("thumb_t") if cam.get("thumb_t") is not None else start + min(1.0, (end - start) / 2)
                clip["_thumb_t"], clip["_crop_px"] = tt, cam_px(cam_cx(cam, tt), sw)
                cut_note += (f", encuadre auto: {cam['modo']}"
                             f"{', ' + str(len(cam['cortes'])) + ' cortes de hablante' if cam['cortes'] else ''}")
            else:
                fit = "crop" if sw and sw <= 1100 else "blur"   # ya vertical: centro; sin caras: blur
                crop_x = 0.5
        if cam:
            pass
        elif vertical and fit == "crop":
            # Recorte 9:16 centrado en crop_x (0 = izquierda, 1 = derecha): sin franjas ni borroso.
            cx = min(max(crop_x, 0.0), 1.0)
            chain.append(f"{pre}scale=-2:1920,crop=1080:1920:(iw-1080)*{cx:.3f}:0[v]")
        elif vertical:
            chain.append(
                f"{pre}split=2[bg][fg];"
                "[bg]scale=1080:1920:force_original_aspect_ratio=increase,"
                "crop=1080:1920,gblur=sigma=22[bgb];"
                "[fg]scale=1080:1920:force_original_aspect_ratio=decrease[fgs];"
                "[bgb][fgs]overlay=(W-w)/2:(H-h)/2[v]")
        elif out_h:
            ow = int(out_h * 16 / 9) // 2 * 2
            chain.append(f"{pre}scale={ow}:{out_h}:flags=lanczos[v]")
        else:
            chain.append(f"{pre}null[v]")
        fdir = str(FONTS_DIR).replace("\\", "/").replace(":", "\\:").replace("'", "\\'")
        chain.append(f"[v]ass={ass.name}:fontsdir={fdir}[{tail}]")
        vf = ";".join(chain)

        if watermark:
            fw = 0 if vertical or not out_h else int(out_h * 16 / 9) // 2 * 2
            vf += watermark_chain(tail, vertical, wm_pos, wm_scale, wm_shadow, fw)

        cmd = [FFMPEG, "-y", "-ss", f"{start:.3f}", "-t", f"{end - start:.3f}",
               "-i", str(video)]
        if watermark:
            cmd += ["-i", str(watermark)]
        cmd += ["-filter_complex", vf, "-map", "[vo]", "-map", "0:a?"]
        af = []
        if keep and len(keep) > 1:
            asel = "+".join(f"between(t,{a - start:.3f},{b - start:.3f})" for a, b in keep)
            af.append(f"aselect='{asel}',asetpts=N/SR/TB")
        if normalize:
            af.append("loudnorm=I=-16:TP=-1.5:LRA=11")
        # loudnorm sube la frecuencia interna a 192 kHz y el AAC salía a 96 kHz: en varios
        # reproductores del celular no suena. Siempre se entrega a 48 kHz (qa.md, qa.sh avisa).
        af.append("aresample=48000")
        cmd += ["-af", ",".join(af)]
        cmd += ["-c:v", "libx264", "-preset", preset, "-crf", str(crf),
                "-pix_fmt", "yuv420p", "-c:a", "aac", "-ar", "48000", "-b:a", "192k",
                "-movflags", "+faststart", str(out)]

        rc = subprocess.run(cmd, cwd=td, stdout=subprocess.DEVNULL,
                            stderr=subprocess.PIPE, text=True, check=False)

    if rc.returncode != 0 or not out.exists():
        print(f"  clip {idx}: FALLÓ")
        for l in (rc.stderr or "").strip().splitlines()[-3:]:
            print(f"      {l}")
        return None

    note = ""
    warns = check_platform(dur)
    if warns:
        note = f"  ⚠ excede {', '.join(warns)}"
    print(f"  clip {idx}: {out.name}  ({dur:.1f}s, {out.stat().st_size/1e6:.1f} MB{cut_note}){note}")
    return out


def read_transcript(path) -> dict:
    """Acepta la transcripción de clipper (`analyze`), la de /edit-video (`ingest.sh` / HyperFrames:
    lista de palabras {text,start,end}) o un JSON de Whisper con segments. Devuelve siempre el formato
    de clipper: {"segments": [{id,start,end,text,words:[{w,start,end}]}], "source"?: …}."""
    data = json.loads(Path(path).expanduser().read_text(encoding="utf-8"))
    if isinstance(data, dict) and data.get("segments") and any(
            "w" in w for sg in data["segments"] for w in (sg.get("words") or [])[:1]):
        return data
    if isinstance(data, dict) and data.get("segments"):          # Whisper: words con "word"
        segs = []
        for i, sg in enumerate(data["segments"], start=1):
            ws = [{"w": (w.get("word") or w.get("text") or "").strip(), "start": float(w["start"]),
                   "end": float(w["end"])} for w in (sg.get("words") or [])
                  if (w.get("word") or w.get("text") or "").strip()]
            segs.append({"id": i, "start": float(sg["start"]), "end": float(sg["end"]),
                         "text": (sg.get("text") or "").strip(), "words": ws})
        return {**{k: v for k, v in data.items() if k != "segments"}, "segments": segs}
    words = data.get("words", []) if isinstance(data, dict) else data   # lista de palabras
    ws = [{"w": (w.get("text") or w.get("word") or w.get("w") or "").strip(),
           "start": float(w["start"]), "end": float(w["end"])} for w in words
          if (w.get("text") or w.get("word") or w.get("w") or "").strip()]
    if not ws:
        die(f"no entiendo la transcripción {path}: ni segments ni lista de palabras")
    segs, cur = [], []
    for j, w in enumerate(ws):                  # frase = hasta . ? ! o una pausa de 0.8 s
        cur.append(w)
        nxt = ws[j + 1] if j + 1 < len(ws) else None
        if w["w"][-1:] in ".?!" or nxt is None or nxt["start"] - w["end"] > 0.8:
            segs.append({"id": len(segs) + 1, "start": cur[0]["start"], "end": cur[-1]["end"],
                         "text": " ".join(x["w"] for x in cur), "words": cur})
            cur = []
    out = {"segments": segs, "duration_sec": ws[-1]["end"]}
    if isinstance(data, dict) and data.get("source"):
        out["source"] = data["source"]
    return out


def need_libass():
    """Sin libass no hay subtítulos quemados. Mejor decirlo antes que fallar en cada clip."""
    p = subprocess.run([FFMPEG, "-hide_banner", "-filters"], capture_output=True, text=True, check=False)
    if " ass " in (p.stdout or ""):
        return
    msg = ("tu ffmpeg no trae libass (filtro 'ass'): no puede quemar subtítulos ni gráficos.\n"
           "  macOS: el ffmpeg de Homebrew core ya no lo incluye. Lo más limpio (no toca tu ffmpeg):\n"
           "    conda create -y -n edit-video-ffmpeg -c conda-forge ffmpeg\n"
           "    y en ~/.config/edit-video/config: EDIT_VIDEO_FFMPEG=\"<env>/bin/ffmpeg\" (+ EDIT_VIDEO_FFPROBE)\n"
           "  O reemplazarlo: brew uninstall ffmpeg && brew tap homebrew-ffmpeg/ffmpeg && "
           "brew install homebrew-ffmpeg/ffmpeg/ffmpeg\n"
           "  Linux: el paquete ffmpeg de la distro suele traerlo (apt install ffmpeg).\n"
           "  Sin libass solo funciona --nivel 3 (corte limpio, sin quemar nada).")
    die(msg)


def _log_tiempo(nivel: int, clips: int, segundos: float, t0: float, cliente: str | None) -> None:
    """Cada render de clipper deja su tiempo real para que scripts/tiempos.py estime los próximos."""
    import time as _t
    c = os.environ.get("EDIT_VIDEO_CLIENTS") or _conf("EDIT_VIDEO_CLIENTS")
    p = (Path(c) / "_general" / "tiempos.jsonl") if c and Path(c).is_dir() \
        else Path.home() / ".config" / "edit-video" / "tiempos.jsonl"
    e = {"fecha": _t.strftime("%Y-%m-%dT%H:%M+00:00", _t.gmtime(t0)), "pieza": f"clipper {clips} clips",
         "nivel": nivel, "tipo": "clipper", "duracion_video_s": round(segundos, 1),
         "minutos": round((_t.time() - t0) / 60, 1), "renders": clips}
    if cliente:
        e["cliente"] = cliente
    try:
        p.parent.mkdir(parents=True, exist_ok=True)
        with p.open("a", encoding="utf-8") as f:
            f.write(json.dumps(e, ensure_ascii=False) + "\n")
    except OSError:
        pass


def cmd_render(args) -> int:
    import time as _t
    _t0 = _t.time()
    need(FFMPEG)
    if str(getattr(args, "nivel", "1")) != "3":
        need_libass()
    tpath = Path(args.transcript).expanduser().resolve()
    if not tpath.exists():
        die(f"no existe {tpath}")
    tdata = read_transcript(tpath)
    segs = tdata["segments"]
    if not args.video and not tdata.get("source"):
        die("esta transcripción no dice de qué video sale: pasa --video")

    video = Path(args.video).expanduser().resolve() if args.video \
        else Path(tdata["source"])
    if not video.exists():
        die(f"no existe el video {video}")

    cpath = Path(args.clips).expanduser().resolve()
    if not cpath.exists():
        die(f"no existe {cpath}")
    clips = json.loads(cpath.read_text(encoding="utf-8"))
    if isinstance(clips, dict):
        clips = clips.get("clips", [])
    if not clips:
        die("el archivo de clips está vacío")

    outdir = Path(args.outdir).expanduser().resolve() if args.outdir \
        else video.parent / f"{video.stem}-clips"
    outdir.mkdir(parents=True, exist_ok=True)

    nivel = int(args.nivel)
    P = load_plantilla(nivel, args.plantilla, args.cliente)
    if args.intensidad:
        P["intensidad"] = int(args.intensidad)
    if args.enfasis:
        P["enfasis"] = args.enfasis
    if nivel == 3:
        # Estudio: aquí no se quema nada. Corte limpio en el encuadre original, voz intacta,
        # y una PROPUESTA por clip que el director aprueba antes de construir con /edit-video.
        args.horizontal, args.no_captions, args.no_normalize = True, True, True
        args.cover_subs, args.watermark = 0.0, None

    wm = None
    if args.watermark:
        wm = Path(args.watermark).expanduser().resolve()
        if not wm.exists():
            die(f"no existe la marca de agua {wm}")
    elif P.get("logo") and nivel < 3:
        wm = Path(P["logo"])
        if not wm.exists():
            print(f"  aviso: el logo del cliente no existe ({wm}); sigo sin logo")
            wm = None
    if wm:
        P["_logo"] = True

    fixed = apply_dictionary(segs, load_dictionary(args.cliente, video.parent))
    has_words = any(s.get("words") for s in segs)
    print(f"renderizando {len(clips)} clip(s) de {video.name}")
    print(f"  nivel {nivel} · {P.get('nombre', '')}"
          f"{' · cliente ' + args.cliente if args.cliente else ''}")
    print(f"  formato: {'vertical 1080x1920' if not args.horizontal else 'original'}")
    print(f"  subtítulos: {'palabra por palabra' if has_words else 'por segmento'}"
          f" · fuente {FONT} · escala {args.caption_scale}x")
    if args.no_captions:
        print("  subtítulos: NO (solo cortar — para montar después con /edit-video)")
    elif fixed:
        print(f"  diccionario: {fixed} correcciones aplicadas")
    if not args.horizontal:
        enc = {"crop": f"recorte 9:16 en x={args.crop_x}", "blur": "fondo difuminado",
               "auto": "auto: sigue la cara / hablante activo (caras.py)"}[args.fit]
        print(f"  encuadre: {enc}")
    if args.tighten:
        print(f"  silencios: fuera los > {args.tighten}s (nunca dentro de una palabra)")
    if args.cover_subs:
        print(f"  subtítulos del original: tapados ({int(args.cover_subs*100)}% inferior)")
    print(f"  audio: {'normalizado EBU R128' if not args.no_normalize else 'sin tocar'} · 192k")
    print(f"  calidad: CRF {args.crf} · preset {args.preset}")
    if wm:
        print(f"  marca de agua: {wm.name} · {args.watermark_pos} · "
              f"{int(args.watermark_scale*100)}% del ancho"
              f"{' con sombra' if not args.no_watermark_shadow else ''}")
    print()

    made = []
    for i, c in enumerate(clips, start=1):
        r = render_clip(video, segs, c, outdir, not args.horizontal, i,
                        args.words_per_caption, not args.no_normalize,
                        wm, args.watermark_pos, args.watermark_scale,
                        not args.no_watermark_shadow, args.caption_scale,
                        args.crf, args.preset, args.out_height, args.fit, args.crop_x,
                        args.cover_subs, args.tighten, not args.no_captions,
                        not args.no_highlight, nivel, P)
        if r:
            made.append(r)
            if nivel == 3:
                prop = write_propuesta(c, segs, float(c["start"]), float(c["end"]), video,
                                       r, P, args.cliente)
                print(f"      propuesta: {prop.name}")
            if not args.no_thumbs:
                th = make_thumb(video, c, segs, r, not args.horizontal, args.fit, args.crop_x,
                                min(nivel, 2), P)
                if th:
                    print(f"      miniatura: {th.name}")

    print(f"\n{len(made)}/{len(clips)} listos en:\n  {outdir}")
    if made:
        _log_tiempo(nivel, len(made), sum(float(c["end"]) - float(c["start"]) for c in clips), _t0, args.cliente)
    if nivel == 3 and made:
        print("\nNivel 3: completa cada *-PROPUESTA.md (concepto, gráficos, imágenes de Higgsfield,"
              "\nsonido), enséñala con 2–3 cuadros de muestra y ESPERA el OK del director."
              "\nCon el OK, se construye con /edit-video a partir del corte limpio.")
    return 0 if made else 1


def escribir_candidatos(tdata: dict, tpath: Path, min_s: float = 15, max_s: float = 60,
                        top: int = 10, quiet: bool = False) -> Path | None:
    """Rúbrica de clipeabilidad (rubrica.py, references/clipeabilidad.md) → *.candidatos.json.

    Es un pre-filtro: ordena y explica. El humano o el agente leen, ajustan y eligen; nada se
    renderiza desde aquí."""
    sys.path.insert(0, str(Path(__file__).resolve().parent))
    import rubrica
    cands = rubrica.candidatos(tdata["segments"], min_s, max_s, top)
    if not cands:
        if not quiet:
            print("  rúbrica: ningún tramo entre "
                  f"{min_s:.0f} y {max_s:.0f} s (¿video demasiado corto? prueba --min menor)")
        return None
    stem = tpath.name.replace(".transcript.json", "").replace(".json", "")
    out = tpath.with_name(f"{stem}.candidatos.json")
    out.write_text(json.dumps({"fuente": tdata.get("source"), "rubrica": "references/clipeabilidad.md",
                               "clips": cands}, ensure_ascii=False, indent=2), encoding="utf-8")
    if not quiet:
        print(f"\nrúbrica de clipeabilidad — {len(cands)} candidatos (0–10; G gancho · D dato · "
              "R remate · A autonomía · E emoción)")
        for c in cands:
            print(f"  {c['total']:>2}/10  [{c['start']:7.1f} → {c['end']:7.1f}]  "
                  f"G{c['gancho']} D{c['dato']} R{c['remate']} A{c['autonomia']} E{c['emocion']}  "
                  f"«{c['apertura'][:48]}»")
            print(f"          {c['motivo']}")
        print(f"\n  {out}\n  Pre-filtro, no decisión: lee los mejores, ajusta cortes y 'hook', y "
              "copia los elegidos a clips.json.")
    return out


def cmd_candidatos(args) -> int:
    tpath = Path(args.transcript).expanduser().resolve()
    if not tpath.exists():
        die(f"no existe {tpath}")
    tdata = read_transcript(tpath)
    return 0 if escribir_candidatos(tdata, tpath, args.min, args.max, args.top) else 1


VIDEO_EXT = {".mp4", ".mov", ".m4v", ".mkv", ".webm"}


def _transcribir_lote(v: Path, args) -> Path | None:
    """Transcripción de un video del lote, con caché. Whisper de OpenAI si está (analyze);
    si no, ingest.sh del skill (whisper.cpp vía HyperFrames, también saca los fotogramas)."""
    t_clip = v.with_name(f"{v.stem}.transcript.json")
    t_ing = v.with_suffix(".edit") / "transcript.json"
    for t in (t_clip, t_ing):
        if t.exists() and not args.force:
            return t
    if shutil.which(WHISPER):
        ns = argparse.Namespace(video=str(v), out=None, model=args.model, lang=args.lang,
                                force_lang=False, words=True, force=args.force,
                                cliente=args.cliente, candidatos=False)
        cmd_analyze(ns)
        return t_clip if t_clip.exists() else None
    ingest = HERE.parent / "scripts" / "ingest.sh"
    if not ingest.exists():
        die("no hay whisper ni scripts/ingest.sh para transcribir")
    rc = subprocess.run(["bash", str(ingest), str(v), args.lang], check=False)
    return t_ing if rc.returncode == 0 and t_ing.exists() else None


def cmd_lote(args) -> int:
    """Una carpeta de grabaciones → propuestas por video → (OK) → clips + miniaturas.

    Paso 1 (sin --render): transcribe cada video (con caché), corre la rúbrica y deja
      <video>.clips.json con los candidatos y "aprobado": false, más LOTE.md con el resumen.
    Paso 2 (--render): renderiza SOLO los videos cuyo .clips.json dice "aprobado": true.
    El OK del humano entre los dos pasos no se salta: es la regla de clipper."""
    import time as _t
    carpeta = Path(args.carpeta).expanduser().resolve()
    if not carpeta.is_dir():
        die(f"no es una carpeta: {carpeta}")
    videos = sorted(p for p in carpeta.iterdir() if p.suffix.lower() in VIDEO_EXT
                    and not p.name.startswith(".") and p.is_file())
    if not videos:
        die(f"no hay videos en {carpeta}")
    filas, t0 = [], _t.time()

    if not args.render:
        print(f"lote · {len(videos)} video(s) en {carpeta.name} · paso 1: transcribir y proponer\n")
        for v in videos:
            tv = _t.time()
            print(f"── {v.name}")
            prop = v.with_name(f"{v.stem}.clips.json")
            if prop.exists() and not args.force:
                d = json.loads(prop.read_text(encoding="utf-8"))
                filas.append((v.name, len(d.get("clips", [])), d.get("aprobado", False), "ya propuesto", 0))
                print("   propuesta ya existe (--force para rehacer)\n")
                continue
            tpath = _transcribir_lote(v, args)
            if not tpath:
                filas.append((v.name, 0, False, "FALLÓ la transcripción", _t.time() - tv))
                continue
            tdata = read_transcript(tpath)
            nw = sum(len(sg.get("words") or []) or len(sg["text"].split()) for sg in tdata["segments"])
            if nw < 40:   # música, b-roll, casi sin voz: no es material de clipper
                filas.append((v.name, 0, False, f"poca voz ({nw} palabras): no es material de clipper",
                              _t.time() - tv))
                print(f"   poca voz ({nw} palabras): sin propuesta\n")
                continue
            cpath = escribir_candidatos(tdata, tpath, args.min, args.max, args.top, quiet=True)
            clips = json.loads(cpath.read_text(encoding="utf-8"))["clips"] if cpath else []
            prop.write_text(json.dumps({
                "video": v.name, "transcript": str(tpath.relative_to(carpeta)), "aprobado": False,
                "nota": "Revisa: quita los que no, ajusta start/end, escribe 'hook' y 'titulo'. "
                        "Luego \"aprobado\": true y `clipper.py lote <carpeta> --render`.",
                "clips": clips}, ensure_ascii=False, indent=2), encoding="utf-8")
            mejor = f"{clips[0]['total']}/10" if clips else "—"
            filas.append((v.name, len(clips), False, f"mejor {mejor}", _t.time() - tv))
            print(f"   {len(clips)} candidatos · mejor {mejor} · {_t.time() - tv:.0f} s\n")
        md = [f"# Lote · {carpeta.name}", "",
              f"{len(videos)} video(s) · paso 1 en {(_t.time() - t0) / 60:.1f} min", "",
              "| video | candidatos | aprobado | nota | s |", "|---|---|---|---|---|"]
        md += [f"| {a} | {b} | {'sí' if c else 'no'} | {d} | {e:.0f} |" for a, b, c, d, e in filas]
        md += ["", "**Siguiente:** revisar cada `<video>.clips.json` (candidatos de la rúbrica, "
               "`references/clipeabilidad.md`), poner `\"aprobado\": true` y correr "
               f"`clipper.py lote {carpeta} --render`."]
        (carpeta / "LOTE.md").write_text("\n".join(md) + "\n", encoding="utf-8")
        print(f"listo: {carpeta / 'LOTE.md'}\nNada se renderiza sin aprobación: edita los "
              "*.clips.json, marca \"aprobado\": true y vuelve con --render.")
        return 0

    print(f"lote · {len(videos)} video(s) en {carpeta.name} · paso 2: renderizar lo aprobado\n")
    hechos = 0
    for v in videos:
        prop = v.with_name(f"{v.stem}.clips.json")
        if not prop.exists():
            print(f"── {v.name}: sin propuesta (corre primero sin --render)")
            continue
        d = json.loads(prop.read_text(encoding="utf-8"))
        if not d.get("aprobado"):
            print(f"── {v.name}: sin aprobar, lo salto")
            continue
        tpath = carpeta / d["transcript"]
        cmd = [sys.executable, str(Path(__file__).resolve()), "render", str(tpath), str(prop),
               "--video", str(v), "--outdir", str(carpeta / f"{v.stem}-clips"),
               "--nivel", str(args.nivel), "--fit", args.fit, "--preset", args.preset]
        if args.cliente:
            cmd += ["--cliente", args.cliente]
        print(f"── {v.name}")
        rc = subprocess.run(cmd, check=False)
        hechos += rc.returncode == 0
    print(f"\n{hechos} video(s) renderizados en {(_t.time() - t0) / 60:.1f} min "
          "(cada render queda en tiempos.py)")
    return 0 if hechos else 1


def cmd_tighten(args) -> int:
    """Imprime los tramos a conservar sin silencios (JSON). Lo consume /edit-video para su rough cut."""
    tdata = read_transcript(args.transcript)
    words = [w for s in tdata["segments"] for w in (s.get("words") or [])]
    if not words:
        die("la transcripción no tiene tiempos por palabra (analyze sin --no-words)")
    start = args.start if args.start is not None else 0.0
    end = args.end if args.end is not None else float(tdata.get("duration_sec") or words[-1]["end"])
    keep = tighten_ranges(words, start, end, args.gap, args.pad)
    kept = sum(b - a for a, b in keep)
    json.dump({"source": tdata.get("source"), "gap": args.gap, "pad": args.pad,
               "original_sec": round(end - start, 2), "kept_sec": round(kept, 2),
               "cuts": len(keep) - 1,
               "keep": [{"start": round(a, 3), "end": round(b, 3)} for a, b in keep]},
              sys.stdout, ensure_ascii=False, indent=2)
    print(f"\n{end - start:.1f}s → {kept:.1f}s, {len(keep) - 1} cortes", file=sys.stderr)
    return 0


# ---------------------------------------------------------------- cli

def main() -> int:
    ap = argparse.ArgumentParser(
        prog="clipper",
        description="Video largo → clips verticales listos para publicar.",
    )
    sub = ap.add_subparsers(dest="cmd", required=True)

    f = sub.add_parser("fetch", help="baja video de YouTube y otros sitios")
    f.add_argument("url")
    f.add_argument("--outdir")
    f.add_argument("--format", help="selector de formato de yt-dlp")
    f.add_argument("--cookies", help="archivo cookies.txt")
    f.add_argument("--cookies-from-browser", dest="cookies_from_browser",
                   help="chrome|firefox|safari|edge")
    f.add_argument("--analyze", action="store_true",
                   help="transcribir inmediatamente después de bajar")
    f.add_argument("--model", default="base")
    f.add_argument("--lang", default="auto", help="auto (detecta) | es | en | …")
    f.add_argument("--cliente", help="slug del cliente: aplica su diccionario privado")
    f.set_defaults(func=cmd_fetch)

    a = sub.add_parser("analyze", help="transcribe con marcas de tiempo")
    a.add_argument("video")
    a.add_argument("--model", default="base",
                   help="tiny|base|small|medium (default: base)")
    a.add_argument("--lang", default="auto",
                   help="auto = detecta (default). Si lo pasas, se verifica contra el audio")
    a.add_argument("--force-lang", action="store_true",
                   help="no verificar el idioma pasado con --lang")
    a.add_argument("--cliente", help="slug del cliente: aplica su diccionario privado")
    a.add_argument("--out", help="ruta del .transcript.json")
    a.add_argument("--no-words", dest="words", action="store_false",
                   help="sin tiempos por palabra (más rápido)")
    a.add_argument("--force", action="store_true",
                   help="ignorar la caché y rehacer la transcripción")
    a.add_argument("--no-candidatos", dest="candidatos", action="store_false",
                   help="no correr la rúbrica de clipeabilidad al terminar")
    a.set_defaults(func=cmd_analyze, words=True)

    r = sub.add_parser("render", help="corta, subtitula y normaliza")
    r.add_argument("transcript", help="el .transcript.json de analyze")
    r.add_argument("clips", help="JSON con los momentos elegidos")
    r.add_argument("--video", help="override del video fuente")
    r.add_argument("--outdir")
    r.add_argument("--horizontal", action="store_true",
                   help="no reencuadrar a vertical")
    r.add_argument("--words-per-caption", type=int, default=3,
                   help="palabras por bloque de subtítulo (default: 3)")
    r.add_argument("--no-normalize", action="store_true",
                   help="no normalizar el audio")
    r.add_argument("--watermark", help="PNG de marca de agua (ideal con alfa)")
    r.add_argument("--watermark-pos", default="top-right",
                   choices=["top-right", "top-left", "bottom-right", "bottom-left"])
    r.add_argument("--watermark-scale", type=float, default=0.22,
                   help="ancho del logo como fracción del cuadro (default 0.22)")
    r.add_argument("--out-height", type=int, default=0,
                   help="alto de salida en modo horizontal (1080 escala 720p a FHD)")
    r.add_argument("--crf", type=int, default=21,
                   help="calidad x264: 18 casi sin perdida, 23 estandar")
    r.add_argument("--preset", default="medium",
                   help="veryfast|fast|medium|slow — mas lento = mejor compresion")
    r.add_argument("--caption-scale", type=float, default=1.0,
                   help="multiplicador del tamano de subtitulo (1.4 = 40%% mas grande)")
    r.add_argument("--no-watermark-shadow", action="store_true",
                   help="sin sombra bajo el logo (logos oscuros no la necesitan)")
    r.add_argument("--fit", default="blur", choices=["blur", "crop", "auto"],
                   help="vertical: blur = fondo difuminado; crop = recorte 9:16 sin franjas en --crop-x; "
                        "auto = sigue la cara y al hablante activo (MediaPipe, entorno aislado)")
    r.add_argument("--crop-x", type=float, default=0.5,
                   help="con --fit crop: centro horizontal del recorte, 0..1 (por clip: crop_x)")
    r.add_argument("--tighten", type=float, default=0.0, metavar="SEG",
                   help="quita silencios mayores a SEG segundos (0.35 recomendado)")
    r.add_argument("--cover-subs", type=float, default=0.0, metavar="FRAC",
                   help="difumina la franja inferior del original (subtítulos quemados), 0.15–0.25")
    r.add_argument("--no-captions", action="store_true",
                   help="sin subtítulos: solo cortar (para montar después con /edit-video)")
    r.add_argument("--no-highlight", action="store_true",
                   help="sin resaltar la palabra que se está diciendo")
    r.add_argument("--cliente", help="slug del cliente: su diccionario y su plantilla (clipper.json)")
    r.add_argument("--nivel", default="1", choices=["1", "2", "3"],
                   help="1 recorte · 2 editorial (tipografía, paleta, detalles) · "
                        "3 estudio (corte limpio + propuesta para /edit-video)")
    r.add_argument("--plantilla", help="JSON que se superpone a la plantilla del nivel")
    r.add_argument("--intensidad", choices=["1", "2", "3"],
                   help="solo nivel 3: 1 profesional · 2 dinámico · 3 extremo (por defecto 1)")
    r.add_argument("--enfasis", choices=["recortes", "efectos", "datos"],
                   help="solo nivel 3: dónde se gasta la carga extra")
    r.add_argument("--no-thumbs", action="store_true",
                   help="no generar la miniatura NN-slug-thumb.jpg de cada clip")
    r.set_defaults(func=cmd_render)

    c = sub.add_parser("candidatos", help="rúbrica de clipeabilidad: tramos puntuados 0–10 con motivo")
    c.add_argument("transcript", help="*.transcript.json de analyze o transcript.json de ingest.sh")
    c.add_argument("--min", type=float, default=15, help="duración mínima del clip (s)")
    c.add_argument("--max", type=float, default=60, help="duración máxima del clip (s)")
    c.add_argument("--top", type=int, default=10, help="cuántos candidatos")
    c.set_defaults(func=cmd_candidatos)

    L = sub.add_parser("lote", help="carpeta de videos → propuestas → (OK) → clips + miniaturas")
    L.add_argument("carpeta")
    L.add_argument("--render", action="store_true",
                   help="paso 2: renderizar los videos cuyo .clips.json dice \"aprobado\": true")
    L.add_argument("--top", type=int, default=6, help="candidatos por video")
    L.add_argument("--min", type=float, default=15)
    L.add_argument("--max", type=float, default=60)
    L.add_argument("--model", default="base", help="modelo de whisper (si se usa analyze)")
    L.add_argument("--lang", default="auto")
    L.add_argument("--cliente")
    L.add_argument("--nivel", default="1", choices=["1", "2", "3"])
    L.add_argument("--fit", default="blur", choices=["blur", "crop", "auto"])
    L.add_argument("--preset", default="veryfast")
    L.add_argument("--force", action="store_true", help="rehacer transcripciones y propuestas")
    L.set_defaults(func=cmd_lote)

    t = sub.add_parser("tighten", help="tramos sin silencios (JSON) para montar")
    t.add_argument("transcript")
    t.add_argument("--start", type=float)
    t.add_argument("--end", type=float)
    t.add_argument("--gap", type=float, default=0.35, help="silencio mínimo a quitar (s)")
    t.add_argument("--pad", type=float, default=0.12, help="aire que se deja a cada lado (s)")
    t.set_defaults(func=cmd_tighten)

    d = sub.add_parser("dict", help="diccionario permanente de correcciones")
    d.add_argument("accion", choices=["agregar", "ver"])
    d.add_argument("mal", nargs="?")
    d.add_argument("bien", nargs="?")
    d.add_argument("--cliente", help="guardar en el diccionario privado del cliente")
    d.set_defaults(func=cmd_dict)

    args = ap.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
