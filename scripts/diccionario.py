#!/usr/bin/env python3
"""edit-video · diccionario permanente de correcciones.

Whisper escribe los nombres como suenan ("Columbia", "near Turing"). Cada corrección que hace el
director se guarda UNA vez y se aplica sola en todos los videos siguientes, antes de que nadie vea nada.

  diccionario.py aplicar TRANSCRIPT.json [--cliente SLUG]     corrige en su sitio (tiempos por palabra)
  diccionario.py agregar "mal escrito" "Bien Escrito" [--cliente SLUG | --proyecto DIR]
  diccionario.py ver [--cliente SLUG]

Capas (la última gana):
  1. global    ~/.config/edit-video/diccionario.json         (términos generales, nada de clientes)
  2. clipper   ~/clipper-studio/dictionary.json               (si existe: mismo diccionario para los dos)
  3. cliente   <área de clientes>/clients/SLUG/diccionario.json  (PRIVADO: marcas, nombres)
  4. proyecto  ./diccionario.json en la carpeta del video

Reglas: palabra completa (nunca dentro de otra: "sol" no toca "girasol"); sin distinguir mayúsculas;
las correcciones de VARIAS palabras ("near Turing" → "nearshoring") funden los tokens y conservan el
inicio del primero y el final del último, para que los subtítulos palabra por palabra también salgan bien.
"""
import json, os, re, sys
from pathlib import Path

HOME = Path.home()
CONF = HOME / ".config/edit-video/config"

def clients_dir():
    d = os.environ.get("EDIT_VIDEO_CLIENTS")
    if not d and CONF.exists():
        m = re.search(r'EDIT_VIDEO_CLIENTS="([^"]*)"', CONF.read_text())
        d = m.group(1) if m else None
    return Path(d or HOME / ".agents/edit-video-clients")

def slug_from_agents(folder: Path):
    for name in ("AGENTS.md", "CLAUDE.md"):
        f = folder / name
        if f.exists():
            m = re.search(r"^\s*-?\s*\**cliente:?\**:?\s*`?([a-z0-9][a-z0-9_-]*)", f.read_text(), re.M | re.I)
            if m: return m.group(1)
    return os.environ.get("EDIT_VIDEO_CLIENTE")

def layers(slug, proj: Path):
    out = [("global", HOME / ".config/edit-video/diccionario.json"),
           ("clipper", HOME / "clipper-studio/dictionary.json")]
    if slug: out.append((f"cliente:{slug}", clients_dir() / "clients" / slug / "diccionario.json"))
    out.append(("proyecto", proj / "diccionario.json"))
    return out

def load(path: Path):
    try: return json.loads(path.read_text("utf-8"))
    except Exception: return {}

def merged(slug, proj):
    d = {}
    for _, p in layers(slug, proj): d.update(load(p))
    return {k: v for k, v in d.items() if k.strip() and k != v}

norm = lambda s: re.sub(r"[^\w']+", "", s.lower())
PUNCT = re.compile(r"^(\W*)(.*?)(\W*)$", re.S)

def aplicar(tj: Path, slug):
    proj = tj.resolve().parent.parent if tj.parent.name.endswith(".edit") else tj.resolve().parent
    slug = slug or slug_from_agents(proj)
    fixes = merged(slug, proj)
    data = json.loads(tj.read_text("utf-8"))
    words = data["words"] if isinstance(data, dict) and "words" in data else data
    key = "text" if words and "text" in words[0] else "word"
    rules = sorted(((k.split(), v) for k, v in fixes.items()), key=lambda r: -len(r[0]))
    out, i, log = [], 0, []
    while i < len(words):
        hit = None
        for toks, good in rules:
            k = len(toks)
            if i + k <= len(words) and all(norm(words[i + j][key]) == norm(toks[j]) for j in range(k)):
                hit = (k, good); break
        if not hit:
            out.append(words[i]); i += 1; continue
        k, good = hit
        first, last = words[i], words[i + k - 1]
        lead = PUNCT.match(first[key].strip()).group(1); trail = PUNCT.match(last[key].strip()).group(3)
        w = dict(first); w[key] = f"{lead}{good}{trail}"; w["end"] = last["end"]
        log.append(f'{first["start"]:7.2f}  {" ".join(x[key] for x in words[i:i+k])!s} → {w[key]}')
        out.append(w); i += k
    if isinstance(data, dict) and "words" in data: data["words"] = out
    else: data = out
    tj.write_text(json.dumps(data, ensure_ascii=False, indent=2), "utf-8")
    (tj.parent / "diccionario.log").write_text("\n".join(log) + "\n", "utf-8")
    capas = ", ".join(n for n, p in layers(slug, proj) if p.exists())
    print(f"   diccionario: {len(log)} correcciones ({len(fixes)} reglas; capas: {capas or 'ninguna'})")

def agregar(bad, good, slug, proj):
    if slug: p = clients_dir() / "clients" / slug / "diccionario.json"
    elif proj: p = Path(proj) / "diccionario.json"
    else: p = HOME / ".config/edit-video/diccionario.json"
    p.parent.mkdir(parents=True, exist_ok=True)
    d = load(p); d[bad] = good
    p.write_text(json.dumps(dict(sorted(d.items(), key=lambda x: x[0].lower())), ensure_ascii=False, indent=2) + "\n", "utf-8")
    print(f"✓ {bad!r} → {good!r} en {p}")

def main(a):
    opt = lambda f: a[a.index(f) + 1] if f in a else None
    if not a: print(__doc__); return 1
    if a[0] == "aplicar": aplicar(Path(a[1]), opt("--cliente")); return 0
    if a[0] == "agregar": agregar(a[1], a[2], opt("--cliente"), opt("--proyecto")); return 0
    if a[0] == "ver":
        for k, v in merged(opt("--cliente"), Path.cwd()).items(): print(f"{k}  →  {v}")
        return 0
    print(__doc__); return 1

if __name__ == "__main__": sys.exit(main(sys.argv[1:]))
