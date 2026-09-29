# Aprendizaje — cómo mejora solo, video tras video

Ningún agente se acuerda de un video al siguiente. **Aprende porque lo escribe**, en dos sitios:

| Repo | Qué guarda | Visibilidad |
|---|---|---|
| **`edit-video`** (este) | Método, referencias, errores reales, recetas — lo que sirve para **cualquier** video | Público |
| **`edit-video-clients`** | Por cliente: `CLIENTE.md` (reglas), `APRENDIZAJES.md`, `HISTORIAL.md`, `kit/` | **Privado** |

Rutas en `~/.config/edit-video/config` (las escribe `sync.sh init`). Mismas para todos los agentes
de la máquina.

## El ciclo

**1 · Al empezar** (Paso 2):
```bash
bash SKILL_DIR/scripts/sync.sh pull
```
Si el proyecto tiene cliente (`cliente: <slug>` en su `AGENTS.md`, o el usuario lo nombra), lee
**antes del beat sheet**: `clients/<slug>/CLIENTE.md`, `APRENDIZAJES.md` (lo de arriba primero) y
`kit/README.md`. Parte de `kit/plantilla.html` si existe. ¿Cliente nuevo? `sync.sh new-client <slug>`
y el onboarding llena su `CLIENTE.md`.

**2 · Durante**: cada nombre mal transcrito que se corrige va **en ese momento** al diccionario
(`scripts/diccionario.py agregar … --cliente <slug>`); cada nota del director, cada defecto que caza el revisor y cada cosa que funcionó
especialmente bien se apunta al momento en `SNAPSHOTS.md` del proyecto.

**3 · Al entregar** (Paso 9), clasifica cada aprendizaje con una pregunta:
**¿serviría en un video de otro cliente?**

- **Sí → `edit-video`**. Al archivo que toque (`qa.md` errores reales, `motion-design.md`,
  `troubleshooting.md`, `routing.md`…) + una entrada en `CHANGELOG.md` + subir versión en `SKILL.md`
  (parche si es una nota, menor si es una técnica nueva). **Sin nombres, marcas, colores ni frases
  del cliente**: se generaliza ("un reel de entrevista 16:9→9:16", no el nombre de la pieza).
- **No → `clients/<slug>/`**:
  - regla nueva o cambiada → `CLIENTE.md`
  - lo aprendido → arriba en `APRENDIZAJES.md` (`fecha · pieza · qué · por qué`; `[director]` si vino de él)
  - una línea en `HISTORIAL.md` (rondas, versión entregada, qué corrigió el director)
  - componentes, sonidos, fondos y la composición final → `kit/` (la mejor versión reemplaza a la anterior)

```bash
bash SKILL_DIR/scripts/sync.sh push "resumen en una línea"
```
Hace commit y push de los dos. **El guardia** busca en lo que va al repo público las
`palabras_privadas` de cada `CLIENTE.md`; si aparece una, no sube nada público y lo dice.
Luego reinstala el skill para que todos los agentes de la máquina lean la versión nueva.

**4 · Reporta** al usuario en una línea: qué fue a cada repo.

## Reglas

1. **Las correcciones del director mandan** sobre cualquier otra señal. Siempre se apuntan.
2. **Un aprendizaje, un sitio.** Si es general, no se duplica en el cliente.
3. **Nunca datos de cliente en el público.** Ante la duda, al privado.
4. **No se aprende de lo que no se verificó.** Solo entra lo que pasó el revisor final o lo que dijo el director.
5. **Lo viejo que se contradice se corrige**, no se apila: se edita la línea y se anota la fecha.
6. Sin permiso de escritura en `edit-video` (otra persona usando el skill), los aprendizajes
   generales van a `edit-video-clients/_general/APRENDIZAJES.md` hasta que el dueño los suba.
