# Mejora continua — cuándo se investiga y cuándo no

Investigar siempre gasta tokens y casi nunca cambia nada. No investigar nunca deja la máquina vieja
en seis meses. La regla: **se investiga cuando hay una razón, y se vigila con calendario.**

## Tres ritmos

| Ritmo | Cuándo | Qué | Costo |
|---|---|---|---|
| **Retro** | Al entregar **cada** video (Paso 9) | Sin buscar en internet. 3 preguntas sobre lo que acaba de pasar | casi nada |
| **Búsqueda dirigida** | Solo si pasó algo de la lista de abajo | 2–4 búsquedas sobre **ese** problema | bajo |
| **Radar** | **Cada 2 semanas**, días 1 y 15 (tarea programada, decisión de Sergio) | Limitaciones abiertas + novedades de herramientas + **revisión profunda de los niveles 2 y 3** (técnicas, estilo, retención) | ≤ 25 búsquedas, informe de 1 página |

## 1 · Retro (cada video, obligatoria)

Al terminar el Paso 9, tres preguntas, respuestas de una línea:

1. **¿Qué corrigió el director?** → aprendizaje (general o del cliente).
2. **¿Qué defecto cazó el revisor que el constructor no vio?** → `qa.md` y, si se puede, una alarma
   automática en `qa.sh` (así nació la alarma de negro).
3. **¿Qué no pudimos hacer, o hicimos a mano, o salió peor de lo que queríamos?** → si no tiene
   arreglo hoy, **una línea en `LIMITACIONES.md`**. Eso es lo que el radar vigila.

## 2 · Búsqueda dirigida (solo con razón)

Se busca en el momento **solo** si:

- una herramienta falla de una forma que no está en `troubleshooting.md` ni en `LIMITACIONES.md`;
- el mismo defecto aparece **dos veces**;
- el director pide algo que el skill no sabe hacer;
- una herramienta avisa de versión nueva o de algo obsoleto.

Máximo 4 búsquedas, sobre ese problema. Lo que se encuentre se prueba antes de escribirlo como regla.

## 3 · Radar (cada 2 semanas)

Una tarea programada abre una sesión y hace esto, en este orden:

1. **Lee `LIMITACIONES.md`** y, para cada limitación abierta, busca si algo nuevo la resuelve.
   *Esto es lo más valioso del radar: busca soluciones a problemas reales, no novedades por novedad.*
2. **Mira las fuentes vigiladas** (abajo) desde la fecha del último radar en `radar.md`.
3. Escribe en `radar.md` una entrada: fecha, qué hay nuevo, **qué limitación resolvería**, y una
   propuesta concreta (qué archivo cambia, cómo se prueba).
4. **Mejora obvia → se implementa.** Obvia = no cambia herramientas ni instala nada, no cambia la
   línea de diseño de ningún nivel, y se puede probar ahí mismo: una regla nueva en `qa.md`, una
   alarma en `qa.sh`, un dato corregido, una técnica documentada con su fuente, un arreglo de un
   script con su prueba. Se prueba, se sube versión (parche/menor), `CHANGELOG`, `sync.sh push`.
5. **Lo demás se propone** (herramienta nueva, instalar algo, cambiar una línea de diseño o el
   contrato de un nivel, activar el nivel 4). Sergio aprueba.
6. Si no hay nada que valga la pena: una línea "sin novedades relevantes" y se acaba. Eso también es
   un resultado.

El radar también **revisa los issues y pull requests abiertos** de `durang/edit-video`: los resume,
prueba lo que se pueda y propone aceptar o no. **Nunca fusiona un PR de otra persona por su cuenta.**

### Fuentes vigiladas

| Qué | Dónde |
|---|---|
| HyperFrames (motor del nivel 3) | changelog en hyperframes.heygen.com · releases de `heygen-com/hyperframes` · `npx hyperframes skills update` |
| Animación | blog de GSAP · skills de motion de LottieFiles |
| Transcripción | releases de `whisper.cpp` y `openai-whisper` |
| Generativos (nivel 4 y fondos) | modelos nuevos en Higgsfield (`models_explore`) · Seedance · el canon de `seedance2_5` |
| FFmpeg / libass | notas de versión, y si Homebrew vuelve a traer libass |
| Estilo y retención (niveles 2 y 3) | análisis recientes de edición de video corto, motion design y tipografía cinética |

## Reglas

- **Nada entra al skill sin probarse** en un video o en una prueba real.
- **Una novedad sin una limitación que resuelva es un "quizá"**: se apunta en `radar.md`, no se adopta.
- **Las decisiones de diseño y de herramientas las toma Sergio.** El radar implementa lo obvio y propone lo demás.
- Todo radar deja rastro en `radar.md`, aunque sea "sin novedades".

## Si descargaste el skill (no eres el dueño del repo)

El radar programado es **del dueño**: es el único que cambia el repo. Tú recibes sus mejoras así:

1. **Cada sesión**, `check.sh` compara tu versión con la de GitHub y, si hay una nueva, te lo dice con
   el comando para actualizar (`npx skills update edit-video -g -y`). Tu agente te pide permiso.
2. **Tu retro** (las 3 preguntas) funciona igual. Lo de tus clientes va a **tu** área privada.
3. **Lo que serviría a todos** se propone con un issue o un PR (`CONTRIBUTING.md`), nunca con datos
   de clientes. El dueño lo revisa en su radar.

Si quieres tu propio radar, prográmalo en **modo informe**: investiga y te deja propuestas, pero no
sube nada al repo público (no tienes permiso) — solo a tu área privada o como issue.
