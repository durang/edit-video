#!/usr/bin/env bash
# edit-video · sync.sh — el ciclo de aprendizaje entre los dos repos.
#
#   sync.sh init --clients <git-url> [--src <ruta-clon-edit-video>]   una vez por máquina
#   sync.sh status                         dónde está cada repo y qué hay sin subir
#   sync.sh pull                           al EMPEZAR un video: trae lo último de los dos
#   sync.sh new-client <slug>              crea clients/<slug>/ desde la plantilla
#   sync.sh push "qué aprendimos"          al ENTREGAR: commit + push de los dos (con guardia)
#
# Dos repos:
#   edit-video (público)          método + aprendizajes que sirven para CUALQUIER video
#   edit-video-clients (privado)  reglas, kit, aprendizajes e historial de CADA cliente
# El guardia bloquea el push público si aparece alguna palabra_privada de un CLIENTE.md.
set -uo pipefail
CONF="$HOME/.config/edit-video/config"
[ -f "$CONF" ] && . "$CONF"
CLIENTS="${EDIT_VIDEO_CLIENTS:-$HOME/.agents/edit-video-clients}"
SRC="${EDIT_VIDEO_SRC:-}"
SKILL_DIR="$(cd "$(dirname "$0")/.." && pwd)"

say(){ printf '%s\n' "$*"; }
isrepo(){ [ -n "$1" ] && git -C "$1" rev-parse --git-dir >/dev/null 2>&1; }

save_conf(){
  mkdir -p "$(dirname "$CONF")"
  printf 'EDIT_VIDEO_CLIENTS="%s"\nEDIT_VIDEO_SRC="%s"\n' "$CLIENTS" "$SRC" > "$CONF"
}

guard(){  # $1 = repo público, $2 = mensaje del commit. Sale 1 si se cuela algo privado.
  isrepo "$CLIENTS" || return 0
  local words w hits=0
  words=$(for f in "$CLIENTS"/clients/*/CLIENTE.md; do
      [[ "$f" == */_plantilla/* ]] && continue
      sed -n 's/^palabras_privadas:[[:space:]]*\[\(.*\)\].*/\1/p' "$f" | tr ',' '\n'
    done | sed 's/^[[:space:]"]*//; s/[[:space:]"]*$//' | grep -v '^<' | grep -v '^$' | sort -u)
  [ -z "$words" ] && return 0
  local added; added=$(git -C "$1" diff --cached -U0 | grep '^+' | grep -v '^+++')
  added="$added"$'\n'"${2:-}"   # el mensaje del commit también es público
  while IFS= read -r w; do
    if printf '%s' "$added" | grep -qiw -- "$w"; then say "  ✗ guardia: \"$w\" es privado de un cliente y va al repo público"; hits=1; fi
  done <<< "$words"
  return $hits
}

commit_push(){  # $1 repo, $2 mensaje, $3 público?(1/0)
  local r="$1" m="$2" pub="$3"
  isrepo "$r" || return 0
  git -C "$r" add -A
  if git -C "$r" diff --cached --quiet; then say "  = $(basename "$r"): nada nuevo"; return 0; fi
  if [ "$pub" = 1 ] && ! guard "$r" "$m"; then
    git -C "$r" reset -q; say "  ✗ $(basename "$r"): NO se subió. Mueve eso al repo de clientes."; return 1
  fi
  git -C "$r" commit -qm "$m" && git -C "$r" push -q && say "  ✓ $(basename "$r"): $(git -C "$r" log --oneline -1)"
}

case "${1:-status}" in
  init)
    shift; URL=""
    while [ $# -gt 0 ]; do case "$1" in
      --clients) URL="$2"; shift 2;; --src) SRC="$2"; shift 2;; *) shift;; esac; done
    if ! isrepo "$CLIENTS"; then
      [ -n "$URL" ] || { say "Falta --clients <git-url> del repo privado de clientes"; exit 1; }
      git clone -q "$URL" "$CLIENTS" || { say "No pude clonar $URL (¿tienes acceso?)"; exit 1; }
    fi
    save_conf; say "✓ clientes: $CLIENTS"; [ -n "$SRC" ] && say "✓ edit-video (fuente): $SRC" \
      || say "· sin clon de edit-video: los aprendizajes generales irán a $CLIENTS/_general/APRENDIZAJES.md"
    ;;
  status)
    say "clientes : $CLIENTS $(isrepo "$CLIENTS" && echo '✓' || echo '✗ (sync.sh init --clients <url>)')"
    say "fuente   : ${SRC:-—} $(isrepo "$SRC" && echo '✓' || echo '(sin clon con permiso de escritura)')"
    for r in "$SRC" "$CLIENTS"; do isrepo "$r" && git -C "$r" status -s | sed "s#^#  $(basename "$r"): #"; done
    isrepo "$CLIENTS" && say "clientes: $(ls "$CLIENTS/clients" | grep -v '^_' | tr '\n' ' ')"
    ;;
  pull)
    changed=0
    for r in "$SRC" "$CLIENTS"; do
      isrepo "$r" || continue
      before=$(git -C "$r" rev-parse HEAD); git -C "$r" pull -q --ff-only || say "  ! $(basename "$r"): no pude hacer pull"
      [ "$before" != "$(git -C "$r" rev-parse HEAD)" ] && { say "  ↓ $(basename "$r") actualizado"; [ "$r" = "$SRC" ] && changed=1; }
    done
    [ "$changed" = 1 ] && npx -y skills update edit-video -g -y >/dev/null 2>&1 && say "  ↻ skill edit-video reinstalado"
    say "✓ al día"
    ;;
  new-client)
    s="${2:?uso: sync.sh new-client <slug>}"; d="$CLIENTS/clients/$s"
    [ -e "$d" ] && { say "Ya existe: $d"; exit 0; }
    cp -R "$CLIENTS/clients/_plantilla" "$d" && sed -i.bak "s/<slug-en-minusculas>/$s/" "$d/CLIENTE.md" && rm -f "$d/CLIENTE.md.bak"
    say "✓ $d — llena CLIENTE.md con el onboarding"
    ;;
  push)
    m="${2:?uso: sync.sh push \"qué aprendimos\"}"; rc=0
    commit_push "$CLIENTS" "aprendizaje: $m" 0 || rc=1
    if isrepo "$SRC"; then
      # El instalador (npx skills) descarta el skill si el frontmatter no es YAML válido:
      # un ": " suelto en la descripción basta para que "no encuentre" el skill.
      if sed -n '2,/^---$/p' "$SRC/SKILL.md" | grep -E '^description: ' | grep -vE '^description: ["'"'"']' | sed 's/^description: //' | grep -q ': '; then
        say "  ✗ SKILL.md: la descripción tiene ': ' sin comillas → el instalador no verá el skill. No subo."; exit 1
      fi
      python3 "$SRC/scripts/guia.py" readme    # la guía rápida del README sale de GUIA.md
      commit_push "$SRC" "aprendizaje: $m" 1 || rc=1
      python3 "$SRC/scripts/guia.py" github    # descripción del repo (About) + link a GUIA.md
      git -C "$SRC" log -1 --format=%s | grep -q "^aprendizaje: $m" && npx -y skills update edit-video -g -y >/dev/null 2>&1 && say "  ↻ skill edit-video reinstalado"
    fi
    exit $rc
    ;;
  *) sed -n 2,14p "$0";;
esac
