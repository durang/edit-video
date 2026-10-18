#!/usr/bin/env bash
# edit-video · sync.sh — el ciclo de aprendizaje entre los dos repos.
#
#   sync.sh init --clients <git-url> [--src <ruta-clon-edit-video>]   una vez por máquina
#   sync.sh status                         dónde está cada repo y qué hay sin subir
#   sync.sh pull                           al EMPEZAR un video: trae lo último de los dos
#   sync.sh new-client <slug>              crea clients/<slug>/ desde la plantilla
#   sync.sh push "qué aprendimos"          al ENTREGAR: commit + push de los dos (con guardia)
#   sync.sh config KEY VALOR               guarda una clave en ~/.config/edit-video/config sin borrar las demás
#
# El push NO sube cualquier cosa: antes de commit revisa los archivos. Video, secretos (.env, llaves, tokens),
# __pycache__, .DS_Store, ._* de macOS, o cualquier archivo > 5 MB (y audio en el repo público) → aborta y
# dice cuáles. Arreglo: muévelos, añádelos al .gitignore, o haz el commit a mano si de verdad van.
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

set_conf(){  # $1 clave, $2 valor — reemplaza o añade esa clave y CONSERVA las demás (p. ej. EDIT_VIDEO_FFMPEG)
  local k="$1" v="$2" tmp
  mkdir -p "$(dirname "$CONF")"; touch "$CONF"
  tmp="$(mktemp "${CONF}.XXXXXX")" || return 1
  grep -v "^${k}=" "$CONF" > "$tmp" || true
  printf '%s="%s"\n' "$k" "$v" >> "$tmp"
  mv "$tmp" "$CONF"
}

save_conf(){
  set_conf EDIT_VIDEO_CLIENTS "$CLIENTS"
  set_conf EDIT_VIDEO_SRC "$SRC"
}

check_files(){  # $1 repo, $2 público?(1/0). Sale 1 si hay archivos que no deben versionarse.
  local r="$1" pub="$2" f sz bad=""
  while IFS= read -r f; do
    [ -n "$f" ] || continue
    case "$f" in
      *.mp4|*.MP4|*.mov|*.MOV|*.webm|*.mkv|*.mxf|*.avi|*.zip|*.tgz|*.tar|*.gz|*.7z)
        bad="$bad"$'\n'"    $f  (video o archivo comprimido)"; continue;;
      *__pycache__*|*.pyc|.DS_Store|*/.DS_Store|._*|*/._*|.env|*/.env|*.env|*.pem|*.key|*.p12|*credentials*|*secret*|*token*.json)
        bad="$bad"$'\n'"    $f  (no se versiona: caché, basura de macOS o secreto)"; continue;;
    esac
    if [ "$pub" = 1 ]; then
      case "$f" in *.wav|*.mp3|*.m4a|*.aif|*.aiff|*.flac) bad="$bad"$'\n'"    $f  (audio en el repo público)"; continue;; esac
    fi
    if [ -f "$r/$f" ]; then
      sz=$(wc -c < "$r/$f" | tr -d ' ')
      [ "${sz:-0}" -gt 5242880 ] && bad="$bad"$'\n'"    $f  ($((sz / 1048576)) MB > 5 MB)"
    fi
  done < <(git -C "$r" ls-files --others --exclude-standard; git -C "$r" diff --name-only)
  if [ -n "$bad" ]; then
    say "  ✗ $(basename "$r"): archivos que no deben subirse:$bad"
    say "    Muévelos o añádelos al .gitignore (o commit a mano si de verdad van). No se subió nada de este repo."
    return 1
  fi
  return 0
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
  check_files "$r" "$pub" || return 1
  git -C "$r" add -A
  if git -C "$r" diff --cached --quiet; then say "  = $(basename "$r"): nada nuevo"; return 0; fi
  say "  · $(basename "$r") — lo que se va a subir:"; git -C "$r" diff --cached --stat | sed 's/^/      /'
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
      [ -n "$(git -C "$r" status --porcelain --untracked-files=no)" ] && say "  ! $(basename "$r"): hay cambios sin commit (git -C \"$r\" status); el pull puede fallar"
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
  config)
    k="${2:?uso: sync.sh config KEY VALOR}"; v="${3-}"
    case "$k" in EDIT_VIDEO_[A-Z_]*) ;; *) say "Solo claves EDIT_VIDEO_*"; exit 1;; esac
    set_conf "$k" "$v" && say "✓ $k=\"$v\" en $CONF (las demás claves se conservan)"
    ;;
  *) sed -n 2,20p "$0";;
esac
