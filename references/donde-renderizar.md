# Dónde se renderiza — Paso 1b

El render y el QA son lo que más tiempo, memoria y cuota consumen. **Se hacen donde el usuario eligió**, no
donde le quede cómodo al agente.

## Las tres opciones

| `render:` | Qué es | Cuándo | Cuidado |
|---|---|---|---|
| `vm` | El servidor / VM donde corre el agente | El usuario lo pide para este trabajo | Gasta la cuota del agente; una VM puede reiniciarse y borrar archivos grandes |
| `local` | La computadora del usuario | Por defecto si la computadora está prendida | Entregas en `carpeta_videos` del cliente |
| `local-externo` | La computadora del usuario, con **todo** en un disco externo | Poco espacio en el disco interno | Proyecto, temporales y cachés en el disco; nada en el interno |

## Dónde se recuerda

1. `render:` en el `AGENTS.md` del proyecto (manda para ese proyecto).
2. `render:` en el `CLIENTE.md` del cliente (repo privado) — **el default por cliente**.
3. `EDIT_VIDEO_RENDER` en `~/.config/edit-video/config` (`sync.sh config EDIT_VIDEO_RENDER local-externo`).
4. Si no hay ninguno: se pregunta **una** vez (texto en `SKILL.md` Paso 1b) y se guarda en 2 (o en 1 sin cliente).

Con `local-externo`, el `CLIENTE.md` lleva además:
```
render: local-externo
disco_externo: /Volumes/<DISCO>
carpeta_videos: /Volumes/<DISCO>/<ruta>/<Marca>
```

## "¿Dónde estamos editando?" — ver y cambiar en un toque

Cuándo: al dar de alta o pedir una marca, al empezar un proyecto, o cuando el usuario lo pregunta.

```bash
bash SKILL_DIR/scripts/destino.sh estado <cliente|carpeta_proyecto>
```
```
🎬 ¿Dónde estamos editando? · <cliente> (cliente)
• Render: computadora + disco externo  [render: local-externo]
• Máquina: <nombre> · Darwin · RAM 8 GB · 2 workers · conectada ✓ (comprobado ahora)
• Proyecto: /Volumes/<DISCO>/<ruta>/<Marca>/<proyecto>
• Entregas: /Volumes/<DISCO>/<ruta>/<Marca>/FINALES/
• Disco: /Volumes/<DISCO> montado ✓ · 600 GB libres de 2000 GB
¿Cambio algo? mantener · VM · computadora · disco externo/ruta
```
La tarjeta corre **en la máquina que renderiza** (así "conectada" es real). Si el agente que pregunta no llega a
esa máquina, la tarjeta dice "✗ sin conexión" en la línea de la máquina — no se inventa.

Opciones de un toque → comando (guarda en `CLIENTE.md` del privado con commit + push, o en `AGENTS.md` del proyecto):
| opción | comando |
|---|---|
| mantener | — |
| cambiar a VM | `destino.sh set <x> vm` |
| cambiar a computadora | `destino.sh set <x> local [carpeta_videos]` |
| cambiar disco externo o ruta | `destino.sh set <x> externo /Volumes/<DISCO>/<ruta>/<Marca>` |

## Antes de cada render (`local-externo`)

```bash
bash SKILL_DIR/scripts/destino.sh check "<carpeta_del_proyecto>" --need-gb <N>
eval "$(bash SKILL_DIR/scripts/destino.sh env "<carpeta_del_proyecto>")"
```

`check` falla (y **no se renderiza**) si:
- el disco no está montado — en macOS `/Volumes/<DISCO>` sin disco es una carpeta del disco interno: escribir ahí
  llena el interno sin avisar. `destino.sh` compara el punto de montaje real y nunca crea la carpeta en ese caso;
- no se puede escribir en la carpeta;
- el espacio libre es menor que `--need-gb` (regla práctica: 3 × metraje + 150 MB por minuto de pieza; 20 GB por defecto).

`env` manda al disco: `TMPDIR` (ffmpeg, Chrome), `XDG_CACHE_HOME`, `npm_config_cache` (HyperFrames vía npx),
`U2NET_HOME` (modelos de rembg), `HF_HOME`, `PIP_CACHE_DIR`, `PUPPETEER_CACHE_DIR`, y `EDIT_VIDEO_WORKERS`
según la RAM (≤ 8 GB → **2**, ≤ 16 GB → 4). Los modelos que ya estén en el interno (p. ej.
`~/.cache/hyperframes/whisper`) se pueden quedar; lo que no puede ir al interno es lo que crece por proyecto.

**Discos exFAT/FAT:** macOS crea `._archivo` al lado de cada archivo. `qa.sh` e `ingest.sh` ya los ignoran;
en tus propias listas (concat, conteos) usa `find … -name '[!.]*'`, y `COPYFILE_DISABLE=1` al empaquetar.

## Paralelismo en máquinas de 8 GB

- HyperFrames: con ≤ 8 GB activa solo `--low-memory-mode` (1 worker, captura por screenshot); si la pieza es ligera y no hay swap, `--workers 2` (o `EDIT_VIDEO_WORKERS`). La "placa única pre-renderizada" (`recetario-3.md`) ayuda.
- Motores propios por trozos: 2 procesos a la vez. El swap de macOS escribe en el disco interno: si la memoria
  se acaba, baja a 1 worker en lugar de subir trozos.
- Render **reanudable** por trozos (un `.ok` por trozo terminado) y en primer plano (`qa.md`, render cancelado).

## Plan B — la máquina elegida no está

Si el agente que orquesta no puede llegar a la máquina que renderiza (apagada, sin conexión, disco desmontado):
1. **No se renderiza en otro lado** "mientras tanto" — salvo que el usuario lo pida para ese trabajo.
2. **No se borra nada** de donde esté el trabajo hasta que esté copiado y verificado en su destino
   (mismo tamaño y `shasum`).
3. Se deja todo preparado (guion, beat sheet aprobado, voz, clips, `PEDIDO.md`) y se reintenta la copia.
4. Se le dice al usuario en una línea qué está esperando y qué falta de su lado.

## Orquestador y renderizador

Cuando un agente prepara y otro renderiza (p. ej. un agente en la nube y Claude Code en la computadora del
usuario), el trabajo se pasa con `PEDIDO.md` en la carpeta del proyecto: `references/pedido.md`.
