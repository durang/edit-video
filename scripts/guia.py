#!/usr/bin/env python3
"""guia.py — la guía de uso siempre visible y al día.

GUIA.md es la fuente. De ahí salen, sin editarlos a mano:
  - el bloque "Guía rápida" arriba del README (entre <!-- GUIA:inicio --> y <!-- GUIA:fin -->),
  - la descripción del repo en GitHub (About) con el link a GUIA.md,
  - el resumen que el agente da en el chat cuando el usuario pide "la guía".

    guia.py resumen     imprime el resumen (para el chat)
    guia.py readme      regenera el bloque del README
    guia.py github      actualiza la descripción y el link del repo (gh; solo el dueño)
    guia.py todo        readme + github
    guia.py check       sale 1 si el bloque del README no coincide con GUIA.md

sync.sh push lo corre solo. Solo librería estándar.
"""
from __future__ import annotations

import re
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GUIA = ROOT / "GUIA.md"
README = ROOT / "README.md"
SKILL = ROOT / "SKILL.md"
REPO = "durang/edit-video"
URL = f"https://github.com/{REPO}/blob/main/GUIA.md"
INI, FIN = "<!-- GUIA:inicio -->", "<!-- GUIA:fin -->"


def version() -> str:
    m = re.search(r"^\s*version:\s*([\d.]+)", SKILL.read_text("utf-8"), re.M)
    return m.group(1) if m else "?"


def mapa() -> list[tuple[str, str, str]]:
    """Filas de la tabla del §0 'Mapa rápido' de GUIA.md: (quiero, uso, tiempo)."""
    txt = GUIA.read_text("utf-8")
    sec = txt.split("## 0 ·", 1)[1].split("\n## ", 1)[0]
    filas = []
    for l in sec.splitlines():
        c = [x.strip() for x in l.strip().strip("|").split("|")]
        if len(c) >= 3 and not set(c[0]) <= set("-: ") and not c[0].startswith("Quiero"):
            filas.append((c[0], c[1], c[2]))
    return filas


def secciones() -> list[str]:
    return [re.sub(r"^##\s*", "", l).strip() for l in GUIA.read_text("utf-8").splitlines()
            if re.match(r"^## \d+ ·", l)]


def resumen(md_link: str = "GUIA.md") -> str:
    v = version()
    out = [f"## Guía rápida · v{v}", "",
           "Qué pedir y qué usar. **Guía completa** — cada nivel y herramienta con descripción, frases "
           f"de ejemplo, qué recibes, tiempo y comando: [GUIA.md]({md_link})", "",
           "| Quiero… | Uso | Tiempo |", "|---|---|---|"]
    out += [f"| {a} | {b} | {c} |" for a, b, c in mapa()]
    def corto(s):
        s = re.sub(r"\*\(.*?\)\*", "", s.split(" — ")[0]).strip()
        n, _, t = s.partition(" · ")
        return f"§{n} {t.replace(' · ', ' ')}"
    out += ["", "Contenido: " + " · ".join(corto(s) for s in secciones())]
    return "\n".join(out)


def bloque() -> str:
    return f"{INI}\n<!-- generado por scripts/guia.py desde GUIA.md: no editar a mano -->\n{resumen()}\n{FIN}"


def cmd_readme() -> int:
    r = README.read_text("utf-8")
    nuevo = bloque()
    if INI in r and FIN in r:
        r2 = re.sub(re.escape(INI) + r".*?" + re.escape(FIN), lambda _: nuevo, r, flags=re.S)
    else:  # debajo del título
        lineas = r.split("\n", 1)
        r2 = lineas[0] + "\n\n" + nuevo + "\n" + (lineas[1] if len(lineas) > 1 else "")
    if r2 != r:
        README.write_text(r2, "utf-8")
        print("✓ README: guía rápida actualizada")
    else:
        print("= README: guía rápida ya al día")
    return 0


def cmd_check() -> int:
    r = README.read_text("utf-8")
    ok = bloque() in r
    print("= guía rápida al día" if ok else "✗ el README no refleja GUIA.md: corre scripts/guia.py readme")
    return 0 if ok else 1


def descripcion() -> str:
    d = (f"edit-video v{version()} · Edita y crea video con cualquier agente. Niveles: 1 Recorte · "
         "2 Editorial · 3 Estudio (motion) · 4 Director. Desde cero: audio, guion o idea → .mp4 + .html. "
         "Clipper: mejores momentos con puntaje, lote, miniaturas, sigue al que habla. "
         "Guía de uso → GUIA.md")
    return d[:350]


def cmd_github() -> int:
    if not shutil.which("gh"):
        print("· gh no está instalado: descripción del repo sin actualizar")
        return 0
    # Con la cuenta del dueño del repo sin cambiar la cuenta activa de gh (puede ser otra, p. ej. la del trabajo)
    import os
    env = dict(os.environ)
    tok = subprocess.run(["gh", "auth", "token", "--user", REPO.split("/")[0]], capture_output=True, text=True)
    if tok.returncode == 0 and tok.stdout.strip():
        env["GH_TOKEN"] = tok.stdout.strip()
    rc = subprocess.run(["gh", "repo", "edit", REPO, "--description", descripcion(), "--homepage", URL],
                        capture_output=True, text=True, env=env)
    if rc.returncode:
        print(f"· GitHub: no pude actualizar la descripción ({(rc.stderr or '').strip()[:120]}) — "
              "solo el dueño del repo puede")
        return 0
    print(f"✓ GitHub: descripción v{version()} + link a GUIA.md")
    return 0


def main() -> int:
    cmd = sys.argv[1] if len(sys.argv) > 1 else "resumen"
    if cmd == "resumen":
        print(resumen(URL)); return 0
    if cmd == "readme":
        return cmd_readme()
    if cmd == "github":
        return cmd_github()
    if cmd == "todo":
        return cmd_readme() or cmd_github()
    if cmd == "check":
        return cmd_check()
    print(__doc__); return 2


if __name__ == "__main__":
    raise SystemExit(main())
