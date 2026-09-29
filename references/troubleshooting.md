# Defecto → arreglo

Describe qué ves y cuándo, o pega el error.

| Síntoma | Arreglo |
|---|---|
| **Nombres mal escritos** | Dar los nombres y marcas en el primer prompt. Corrige la transcripción **y** los subtítulos |
| **El texto queda tapado por los botones de la app** | Declarar la safe zone: nada en el 20% inferior ni pegado al borde derecho |
| **El efecto llega tarde** | Nombrar **la palabra** en la que debe empezar. Claude tiene el tiempo exacto de cada una |
| **Dice que está hecho pero se ve mal** | `snapshot el frame en 0:07 y revísalo tú mismo`. Entonces ve lo que ves tú |
| **El preview o el render fallan** | `npx hyperframes doctor`, y pegarle el error |
| **Un cambio rompió algo** | Guardar versión antes de cada ronda (v1, v2...) y volver atrás |
| **Los subtítulos van demasiado rápido** | `De 0:12 a 0:14 los subtítulos van muy rápido. Muestra dos palabras a la vez` |
| **El recorte tiene bordes blandos** | Movimiento demasiado rápido o poca separación de la pared. Se vuelve a grabar, no se arregla en montaje |
| **El clean plate no existe** | Los efectos de capas no se pueden hacer. Se graban 2 s de sala vacía y se repite |

## Hábitos que evitan casi todo

- **Un cambio por mensaje.**
- **Siempre con el tiempo:** "en 0:07".
- **Decir qué se quiere ver, no cómo programarlo.**
- **Aprobar el plan antes de construir.**

## Atajos

- Rough cut primero, efectos después.
- Previsualizar secciones cortas antes de un render completo.
- Las reglas de estilo (tipografías, colores, safe zone) en un `CLAUDE.md` en la carpeta.
  Claude lo lee cada vez.
- Cuando un efecto funcione, pedir que lo guarde como plantilla.

## Racionalizaciones que hay que rechazar

| Pensamiento | Realidad |
|---|---|
| "Lo construyo y ya lo enseño luego" | El beat sheet es más barato que un render. Siempre |
| "Está hecho, seguro que se ve bien" | Si no has mirado el frame, no lo sabes. Snapshot y mirar |
| "Le meto un efecto más y queda mejor" | Más de un zoom cada cinco segundos cansa. Lo raro es lo que impacta |
| "Grabo y ya veré si hace falta el clean plate" | Sin él, la mitad de los efectos buenos quedan fuera |
