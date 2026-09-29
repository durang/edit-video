# Mejora continua — cuándo se investiga y cuándo no

Investigar siempre gasta tokens y casi nunca cambia nada. No investigar nunca deja la máquina vieja
en seis meses. La regla: **se investiga cuando hay una razón, y se vigila con calendario.**

## Tres ritmos

| Ritmo | Cuándo | Qué | Costo |
|---|---|---|---|
| **Retro** | Al entregar **cada** video (Paso 9) | Sin buscar en internet. 3 preguntas sobre lo que acaba de pasar | casi nada |
| **Búsqueda dirigida** | Solo si pasó algo de la lista de abajo | 2–4 búsquedas sobre **ese** problema | bajo |
| **Radar** | **Cada 2 semanas** (tarea programada) | Novedades de las herramientas + revisar cada limitación abierta | ≤ 12 búsquedas, informe de 1 página |
| **Estado del arte** | **Cada 3 meses** (el radar de ese mes) | Revisar el contrato del nivel 3 y las líneas de diseño contra lo que se hace ahora | ≤ 25 búsquedas |

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
4. **No cambia el skill por su cuenta.** Lo que sea solo documentación se puede dejar listo en una
   rama; lo que cambie herramientas, versiones o el diseño, se le propone a Sergio. Él aprueba.
5. Si no hay nada que valga la pena: una línea "sin novedades relevantes" y se acaba. Eso también es
   un resultado.

### Fuentes vigiladas

| Qué | Dónde |
|---|---|
| HyperFrames (motor del nivel 3) | changelog en hyperframes.heygen.com · releases de `heygen-com/hyperframes` · `npx hyperframes skills update` |
| Animación | blog de GSAP · skills de motion de LottieFiles |
| Transcripción | releases de `whisper.cpp` y `openai-whisper` |
| Generativos (nivel 4 y fondos) | modelos nuevos en Higgsfield (`models_explore`) · Seedance · el canon de `seedance2_5` |
| FFmpeg / libass | notas de versión, y si Homebrew vuelve a traer libass |
| Estilo y retención | análisis de edición de video corto del último trimestre (solo en el radar trimestral) |

## Reglas

- **Nada entra al skill sin probarse** en un video o en una prueba real.
- **Una novedad sin una limitación que resuelva es un "quizá"**: se apunta en `radar.md`, no se adopta.
- **Las decisiones de diseño y de herramientas las toma Sergio.** El radar propone.
- Todo radar deja rastro en `radar.md`, aunque sea "sin novedades".
