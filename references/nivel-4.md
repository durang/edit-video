# Nivel 4 · Director — propuesto

> **Estado: propuesto.** Se activa cuando el director lo apruebe. Hasta entonces, lo más alto es el 3.

El nivel 3 lo hace todo con el metraje que existe. El 4 **añade lo que no se grabó**: planos
generados, cámara en espacios que no existían, luz nueva, música cortada a la imagen, y varias
versiones del gancho. Es donde se juntan los dos repos: `seedance2_5` (generar) y este (montar).

## Qué añade sobre el nivel 3

| Capa | Cómo | Herramienta |
|---|---|---|
| **Insertos generados** (B-roll que no existe: la fábrica, el puerto, el producto) | Prompts del canon de `seedance2_5`; 3–4 s por plano; **nunca texto dentro del plano** | Seedance 2.5 / Higgsfield video |
| **Multiángulo y re-iluminado** de la persona | Habilidades del canon (multiángulo, copiar la luz) | Seedance / Higgsfield |
| **Cámara 2.5D sobre fotos** | Mapa de profundidad → parallax con 2–3 capas | HyperFrames (`three`, capas CSS 3D) |
| **Objetos 3D** (producto, logo, globo) | Imagen → GLB → escena | Higgsfield `generate_3d` + adaptador `three` de HyperFrames |
| **Música a la imagen** | Pista con licencia; cortes y golpes gráficos en el beat | `music-to-video`, `hyperframes-audio` |
| **Versiones del gancho** | 2–3 aperturas distintas del mismo cuerpo, para probar | la misma composición, otra escena inicial |
| **Másters por formato** | 9:16, 4:5 y 16:9 **recompuestos**, no recortados | la misma composición con tres lienzos |

## Puertas de aprobación (tres, no una)

1. **Tratamiento**: concepto, referencias, guion visual por beats, lista de insertos a generar,
   música propuesta, presupuesto de créditos.
2. **Animatic**: render borrador (`--quality draft`) con los insertos como placa y el timing real.
3. **Cada inserto generado** se aprueba antes de entrar al montaje (se genera en variantes).

Después: construcción, revisor final (el contrato del nivel 3 + coherencia de luz y color entre
metraje real e insertos) y aprendizaje.

## Por qué es otro nivel y no un nivel 3 "más grande"

Cambian tres cosas: **cuesta créditos**, **mete material que no existía** (hay que cuidar que no
engañe: nada de hacer pasar un plano generado por un hecho real), y **necesita más de una
aprobación**. Mezclarlo con el 3 haría el 3 lento y caro por defecto.
