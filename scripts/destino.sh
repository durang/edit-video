#!/usr/bin/env bash
# edit-video · destino.sh — ¿se puede renderizar aquí sin llenar el disco equivocado? (Paso 1b, references/donde-renderizar.md)
#
#   destino.sh check <carpeta_proyecto> [--need-gb N]   disco montado, escribible, espacio; sale 1 si NO se debe renderizar
#   destino.sh env   <carpeta_proyecto>                 imprime los export (TMPDIR, cachés, workers): eval "$(destino.sh env DIR)"
#   destino.sh estado <cliente|carpeta_proyecto>        "¿dónde estamos editando?": tarjeta de 5–6 líneas, comprobada en vivo
#   destino.sh set <cliente|carpeta_proyecto> <vm|local|externo> [ruta]
#                                                       cambia dónde se renderiza y lo guarda (CLIENTE.md en el repo privado,
#                                                       o AGENTS.md del proyecto) — sin editar archivos a mano
#
# Regla: si la carpeta está en /Volumes/<DISCO>/… y ese disco no está montado, macOS escribiría en el disco
# interno (/Volumes es una carpeta normal). Por eso nunca se crea la carpeta si el disco no está montado.
set -uo pipefail
say(){ printf '%s\n' "$*"; }
CMD="${1:-}"; DIR="${2:-}"; shift 2 2>/dev/null || true
REST_1=""; REST_2=""
if [ "$CMD" = set ]; then REST_1="${1:-}"; REST_2="${2:-}"; shift 2 2>/dev/null || shift $# ; fi
NEED_GB=20
while [ $# -gt 0 ]; do case "$1" in --need-gb) NEED_GB="$2"; shift 2;; *) shift;; esac; done
[ -n "$CMD" ] && [ -n "$DIR" ] || { sed -n 2,12p "$0"; exit 2; }
SET_MODE=""; SET_PATH=""
if [ "$CMD" = set ]; then SET_MODE="${REST_1:-}"; SET_PATH="${REST_2:-}"; fi

vol_root(){  # /Volumes/<DISCO> si la ruta está bajo /Volumes, si no vacío
  case "$1" in /Volumes/*) printf '/Volumes/%s' "$(printf '%s' "${1#/Volumes/}" | cut -d/ -f1)";; esac
}
mount_point(){  # punto de montaje real del primer ancestro que exista
  local d="$1"; while [ ! -e "$d" ] && [ "$d" != "/" ]; do d="$(dirname "$d")"; done
  df -P "$d" 2>/dev/null | awk 'NR==2{for(i=1;i<=5;i++) $i=""; sub(/^ +/, ""); print}'   # admite espacios
}
ram_gb(){
  if [ "$(uname -s)" = Darwin ]; then echo $(( $(sysctl -n hw.memsize) / 1073741824 ))
  else awk '/MemTotal/{printf "%d", $2/1048576}' /proc/meminfo; fi
}
workers(){ local r; r=$(ram_gb); if [ "${r:-0}" -le 8 ]; then echo 2; elif [ "$r" -le 16 ]; then echo 4; else echo 6; fi; }
cache_root(){ local v; v="$(vol_root "$DIR")"; if [ -n "$v" ]; then echo "$v/.cache/edit-video"; else echo ""; fi; }

# ---------- dónde se guarda la elección: CLIENTE.md (repo privado) o AGENTS.md (proyecto) ----------
CONF="$HOME/.config/edit-video/config"; [ -f "$CONF" ] && . "$CONF"
CLIENTS="${EDIT_VIDEO_CLIENTS:-$HOME/.agents/edit-video-clients}"
resolve(){  # $1 = slug de cliente o carpeta de proyecto → TARGET_KIND, TARGET_FILE, TARGET_NAME
  if [ -d "$1" ] && [ "${1#/}" != "$1" -o -e "$1/AGENTS.md" ]; then
    TARGET_KIND=proyecto; TARGET_FILE="$(cd "$1" && pwd)/AGENTS.md"; TARGET_NAME="$(basename "$(cd "$1" && pwd)")"
  elif [ -f "$CLIENTS/clients/$1/CLIENTE.md" ]; then
    TARGET_KIND=cliente; TARGET_FILE="$CLIENTS/clients/$1/CLIENTE.md"; TARGET_NAME="$1"
  else
    say "✗ No encuentro el cliente \"$1\" ($CLIENTS/clients/$1/CLIENTE.md) ni la carpeta de proyecto."; exit 1
  fi
}
getk(){  # $1 archivo, $2 clave → valor (frontmatter "clave: v" o línea "- **clave:** v")
  [ -f "$1" ] || return 0
  sed -n -E "s/^${2}:[[:space:]]*//p; s/^- \*\*${2}:\*\*[[:space:]]*//p" "$1" | head -1 | sed -E 's/[[:space:]]+(←|#).*$//; s/^"//; s/"$//'
}
client_of_project(){ getk "$1" cliente; }
setk(){  # $1 archivo, $2 clave, $3 valor — en el frontmatter (CLIENTE.md) o en la sección Render (AGENTS.md)
  local f="$1" k="$2" v="$3" tmp; tmp="$(mktemp "${f}.XXXXXX")"
  if head -1 "$f" 2>/dev/null | grep -q '^---$'; then
    awk -v k="$k" -v v="$v" 'NR==1{print; infm=1; next}
      infm && $0 ~ "^"k":" {print k": "v; done=1; next}
      infm && /^---$/ {if(!done) print k": "v; infm=0; print; next}
      {print}' "$f" > "$tmp"
  else
    if [ -f "$f" ] && grep -qE "^- \*\*${k}:\*\*" "$f"; then
      awk -v k="$k" -v v="$v" '$0 ~ "^- \\*\\*"k":\\*\\*" {print "- **"k":** "v; next} {print}' "$f" > "$tmp"
    else
      { [ -f "$f" ] && cat "$f"; grep -q '^### Render' "$f" 2>/dev/null || printf '\n## edit-video\n\n### Render (Paso 1b)\n'; printf -- '- **%s:** %s\n' "$k" "$v"; } > "$tmp"
    fi
  fi
  mv "$tmp" "$f"
}
human_mode(){ case "$1" in vm) echo "VM / servidor del agente";; local) echo "computadora del usuario";; local-externo) echo "computadora + disco externo";; *) echo "sin elegir (Paso 1b: preguntar)";; esac; }

case "$CMD" in
  estado)
    resolve "$DIR"
    F="$TARGET_FILE"; MODE="$(getk "$F" render)"; DISK="$(getk "$F" disco_externo)"; CV="$(getk "$F" carpeta_videos)"; VENV="$(getk "$F" venv)"
    if [ "$TARGET_KIND" = proyecto ]; then
      CL="$(client_of_project "$F")"; CF="$CLIENTS/clients/$CL/CLIENTE.md"
      [ -n "$CL" ] && [ -f "$CF" ] && { [ -n "$MODE" ] || MODE="$(getk "$CF" render)"; [ -n "$DISK" ] || DISK="$(getk "$CF" disco_externo)"; [ -n "$VENV" ] || VENV="$(getk "$CF" venv)"; [ -n "$CV" ] || CV="$(getk "$CF" carpeta_videos)"; }
      PROJ="$(dirname "$F")"; [ -n "$CV" ] || CV="$(dirname "$PROJ")"
      CV="${CV/#\~/$HOME}"
    else CV="${CV/#\~/$HOME}"; PROJ="$CV/<proyecto>"; fi
    [ -n "$MODE" ] || MODE="${EDIT_VIDEO_RENDER:-}"
    HOST="$(scutil --get ComputerName 2>/dev/null || hostname)"
    say "🎬 ¿Dónde estamos editando? · $TARGET_NAME ($TARGET_KIND)"
    say "• Render: $(human_mode "$MODE")  [render: ${MODE:-—}]"
    if [ "$MODE" = vm ]; then say "• Máquina: VM del agente (esta tarjeta se generó en $HOST; la VM no se comprueba desde aquí)"
    else say "• Máquina: $HOST · $(uname -s) · RAM $(ram_gb) GB · $(workers) workers · conectada ✓ (comprobado ahora)"; fi
    say "• Proyecto: $PROJ"
    say "• Entregas: ${CV:-—}/FINALES/"
    if [ "$MODE" = local-externo ]; then
      V="$(vol_root "${DISK:-$CV}")"
      if [ -n "$V" ] && [ -d "$V" ] && [ "$(mount_point "$V/.")" = "$V" ]; then
        FR=$(df -Pk "$V" | awk 'NR==2{printf "%d", $4/1048576}'); TT=$(df -Pk "$V" | awk 'NR==2{printf "%d", $2/1048576}')
        say "• Disco: $V montado ✓ · ${FR} GB libres de ${TT} GB"
      else say "• Disco: ${V:-${DISK:-—}} ✗ NO montado — no se renderiza hasta conectarlo"; fi
    else
      D0="${CV:-$HOME}"; while [ ! -e "$D0" ] && [ "$D0" != / ]; do D0="$(dirname "$D0")"; done
      say "• Disco: $(mount_point "$D0/.") · $(df -Pk "$D0" | awk 'NR==2{printf "%d", $4/1048576}') GB libres"
    fi
    if [ -n "$VENV" ]; then
      [ -x "$VENV/bin/python" ] && say "• Motor: venv $VENV ✓" || say "• Motor: venv $VENV ✗ (no existe o el disco no está)"
    fi
    say "¿Cambio algo? mantener · VM · computadora · disco externo/ruta  →  destino.sh set $DIR <vm|local|externo> [ruta]"
    ;;
  set)
    resolve "$DIR"
    case "$SET_MODE" in vm) M=vm;; local|computadora|mac) M=local;; externo|local-externo|disco) M=local-externo;;
      *) say "uso: destino.sh set <cliente|carpeta_proyecto> <vm|local|externo> [ruta]"; exit 2;; esac
    F="$TARGET_FILE"
    if [ "$M" = local-externo ]; then
      R="${SET_PATH:-$(getk "$F" carpeta_videos)}"
      V="$(vol_root "$R")"
      [ -n "$V" ] || { say "✗ Con 'externo' la ruta tiene que estar en un disco externo (/Volumes/<DISCO>/…): destino.sh set $DIR externo /Volumes/<DISCO>/<ruta>"; exit 1; }
      [ -d "$V" ] && [ "$(mount_point "$V/.")" = "$V" ] || say "! $V no está montado ahora: lo guardo, pero no se renderizará hasta conectarlo."
      setk "$F" render local-externo; setk "$F" disco_externo "$V"; [ "$TARGET_KIND" = cliente ] && setk "$F" carpeta_videos "$R"
    else
      setk "$F" render "$M"; [ -n "$SET_PATH" ] && [ "$TARGET_KIND" = cliente ] && setk "$F" carpeta_videos "$SET_PATH"
    fi
    say "✓ $TARGET_NAME: render = $M (guardado en $F)"
    if [ "$TARGET_KIND" = cliente ] && git -C "$CLIENTS" rev-parse --git-dir >/dev/null 2>&1; then
      git -C "$CLIENTS" add -- "$F" && git -C "$CLIENTS" commit -qm "$TARGET_NAME: render = $M" -- "$F" \
        && { git -C "$CLIENTS" push -q 2>/dev/null && say "✓ repo privado: commit + push" || say "· repo privado: commit hecho; push pendiente (sync.sh push)"; }
    fi
    bash "$0" estado "$DIR"
    ;;
  check)
    ok=0; V="$(vol_root "$DIR")"
    if [ -n "$V" ]; then
      MP="$(mount_point "$V/.")"
      if [ ! -d "$V" ] || [ "$MP" != "$V" ]; then
        say "✗ El disco $V NO está montado (la ruta caería en el disco interno). Conéctalo y repite. No se renderiza."; exit 1
      fi
      say "✓ disco montado: $V"
      FS=$( (diskutil info "$V" 2>/dev/null | awk -F: '/Type \(Bundle\)|File System Personality/{gsub(/^ +/,"",$2); print $2; exit}') || true)
      case "$FS" in *exfat*|*ExFAT*|*msdos*|*FAT*)
        say "! sistema de archivos $FS: macOS crea archivos ._* — los scripts los ignoran; en tus listas usa find -name '[!.]*'. export COPYFILE_DISABLE=1";; esac
    fi
    if [ -e "$DIR" ]; then
      [ -d "$DIR" ] || { say "✗ $DIR existe y no es carpeta"; exit 1; }
    else
      mkdir -p "$DIR" || { say "✗ no pude crear $DIR"; exit 1; }
      say "✓ creada $DIR"
    fi
    PROBE="$DIR/.edit-video-probe.$$"
    if ( : > "$PROBE" ) 2>/dev/null; then rm -f "$PROBE"; say "✓ se puede escribir en $DIR"
    else say "✗ no se puede escribir en $DIR (¿solo lectura? ¿permisos?)"; exit 1; fi
    FREE_GB=$(df -Pk "$DIR" | awk 'NR==2{printf "%d", $4/1048576}')
    if [ "${FREE_GB:-0}" -lt "$NEED_GB" ]; then
      say "✗ espacio libre: ${FREE_GB} GB < ${NEED_GB} GB necesarios. Libera espacio o elige otro destino."; ok=1
    else say "✓ espacio libre: ${FREE_GB} GB (≥ ${NEED_GB} GB)"; fi
    say "· RAM $(ram_gb) GB → workers recomendados: $(workers)"
    say "· ahora: eval \"\$(bash $(cd "$(dirname "$0")" && pwd)/destino.sh env \"$DIR\")\"   (temporales y cachés al destino)"
    exit $ok
    ;;
  env)
    C="$(cache_root)"
    printf 'export TMPDIR=%q\n' "$DIR/.tmp"
    printf 'mkdir -p %q\n' "$DIR/.tmp"
    if [ -n "$C" ]; then
      printf 'mkdir -p %q\n' "$C"
      printf 'export XDG_CACHE_HOME=%q\n' "$C"
      printf 'export npm_config_cache=%q\n' "$C/npm"
      printf 'export U2NET_HOME=%q\n' "$C/u2net"          # modelos de rembg
      printf 'export HF_HOME=%q\n' "$C/huggingface"
      printf 'export PIP_CACHE_DIR=%q\n' "$C/pip"
      printf 'export PUPPETEER_CACHE_DIR=%q\n' "$C/puppeteer"
      printf 'export COPYFILE_DISABLE=1\n'
    fi
    printf 'export EDIT_VIDEO_WORKERS=%s\n' "$(workers)"
    ;;
  *) sed -n 2,12p "$0"; exit 2;;
esac
