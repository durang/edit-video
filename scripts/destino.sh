#!/usr/bin/env bash
# edit-video · destino.sh — ¿se puede renderizar aquí sin llenar el disco equivocado? (Paso 1b, references/donde-renderizar.md)
#
#   destino.sh check <carpeta_proyecto> [--need-gb N]   disco montado, escribible, espacio; sale 1 si NO se debe renderizar
#   destino.sh env   <carpeta_proyecto>                 imprime los export (TMPDIR, cachés, workers): eval "$(destino.sh env DIR)"
#
# Regla: si la carpeta está en /Volumes/<DISCO>/… y ese disco no está montado, macOS escribiría en el disco
# interno (/Volumes es una carpeta normal). Por eso nunca se crea la carpeta si el disco no está montado.
set -uo pipefail
say(){ printf '%s\n' "$*"; }
CMD="${1:-}"; DIR="${2:-}"; shift 2 2>/dev/null || true
NEED_GB=20
while [ $# -gt 0 ]; do case "$1" in --need-gb) NEED_GB="$2"; shift 2;; *) shift;; esac; done
[ -n "$CMD" ] && [ -n "$DIR" ] || { sed -n 2,8p "$0"; exit 2; }

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

case "$CMD" in
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
  *) sed -n 2,8p "$0"; exit 2;;
esac
