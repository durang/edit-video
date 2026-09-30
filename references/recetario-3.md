# Recetario del nivel 3 — efectos probados, listos para pedir

Cada receta nace de una pieza real que el director aprobó. Se pide por su nombre
("nivel 3, cierre congelado con recorte") y el agente la construye con estos tiempos, sin
reinventarla. **Regla de entrada:** una técnica entra aquí solo cuando salió en un video
aprobado y pasó el revisor. Los ejemplos de afuera que le gusten al director entran primero en
`## Por probar` (con enlace y qué tiene de bueno) y suben a receta cuando se prueban.

Formato de cada receta: **qué es · cuándo · intensidad mínima · tiempos exactos · activos ·
fallas conocidas y su arreglo · costo.**

---

## R1 · Cierre congelado con recorte ("freeze-frame cutout")

**Qué es.** El video se congela en el último cuadro, el fondo se va y queda la persona recortada
sobre papel; detrás sube un paisaje del lugar del que habla, ella se acomoda a un lado y entra el
cierre (título, líneas, créditos, emblema). Termina con parallax lento hasta el último cuadro.

**Cuándo.** Cierre de un reel de marca personal o de empresa, cuando la persona ES el mensaje.
**Intensidad mínima:** 1.

**Tiempos (reel de ~51 s, 9:16, probados):**

| t (s) | Evento | Duración · curva |
|---|---|---|
| 47.60 | Congelado del último cuadro + SFX obturador | corte |
| 47.60 | El cuadro congelado se cierra hacia el centro (`clip-path: inset(…)` hasta el punto medio) | 0.50 s · `power2.inOut` |
| 47.62 | **El congelado se desvanece mientras se encoge** (obligatorio, ver fallas) | 0.28 s · `power2.in` |
| 48.00 | El paisaje sube por detrás (y +190 → 0) | MOVE |
| 48.40 | Ella baja a un lado: escala 1.0 → 0.8 anclada abajo, x +348 | MOVE |
| 48.80 | Barra de acento + título letra por letra (SplitText, yPercent 120 → 0) | IN · escalonado |
| 49.10–49.40 | 3 líneas de texto, +0.15 s entre cada una | IN |
| 49.30 | Emblema (contorno del país) se dibuja; punto de la ciudad al final (`back.out(2)`) | 1.2 s · `power2.inOut` |
| 49.60 | Créditos abajo | IN · escalonado 0.1 s |
| 49.25→final | Parallax: paisaje ×1.00 → 1.03, ella ×0.80 → 0.812 | 2.15 s · lineal |

**Activos.**
- Recorte **del cuadro completo** (no de un recorte del encuadre: deja un borde recto). Con
  Higgsfield `remove_background` sobre el cuadro exacto del congelado, a resolución de origen.
- Revisar el alfa a mano: manchas sueltas (p. ej. junto a la nariz) se borran poniendo alfa 0 en
  esa zona; guardar copia `.bak.png` antes.
- Paisaje en capa propia (PNG), sombra suave bajo ella.

**Fallas conocidas → arreglo.**
- Rectángulo de piel en el centro al final del `clip-path` que se encoge a un punto → desvanecer
  el congelado **durante** el encogimiento (fila 47.62). Ver `qa.md`.
- Borde recto en la silueta → recortar el cuadro completo, alineado con el encuadre del video.
- Créditos tocando el pelo → dejar ≥ 40 px entre texto y silueta; comprobar en el último cuadro.

**Costo.** El recorte, ~1 min. Con esta receta, la construcción es de una pasada; lo que tomó
tiempo la primera vez (las 3 fallas) ya está resuelto aquí.

---

## R2 · Congelado con palabra detrás ("freeze + text-behind")

**Qué es.** En la palabra clave, la imagen se congela 0.7 s como un golpe; aparece la palabra enorme
**detrás** de la persona (su pelo tapa el pie de las letras) y al soltar, corte seco al video en
movimiento y la palabra baja a su pastilla. El audio nunca se detiene.

**Cuándo.** Una o dos veces por pieza, en las palabras que resumen el mensaje. **Intensidad mínima:** 2.

**Tiempos (probados, 9:16):**

| t | Evento | Duración · curva |
|---|---|---|
| T | Congelado del cuadro (asentado: después de cualquier transición de encuadre) + golpe | corte |
| T | Header sale (la palabra ocupa esa franja) | 0.12 s · OUT |
| T+0.05 | Palabra grande entra detrás de ella (color de acento, dentro de márgenes 64 px) | IN |
| T+0.55 | Palabra grande sale hacia arriba y **termina en el cuadro del corte** | 0.15 s · OUT |
| T+0.70 | **Corte seco** al video en movimiento (nunca fundido) · header vuelve | corte · IN |
| T+0.72 | La palabra chica (pastilla) entra, por encima del video | IN |

**Activos.**
- Placa limpia del cuadro T: la composición con **todo gráfico oculto** (header, subtítulos, pie) en
  ese instante, no un cuadro del render final.
- Recorte: `npx hyperframes remove-background` (local) o Higgsfield; limpiar alfa a mano (manchas
  sueltas, borde inferior bajo el pie). Copia `.bak.png`.
- Capas: placa congelada → palabra grande → recorte → header/subtítulos/pie.

**Fallas conocidas → arreglo** (todas vistas en la primera pieza).
- La palabra choca con el header → el header sale durante el congelado.
- Palabra de borde a borde → márgenes 64 px.
- **Doble exposición al soltar** (dos cabezas) → corte seco, nunca fundido del recorte sobre el video.
- La pastilla chica asoma **detrás** de ella → entra solo después del corte, z sobre el video.
- Dos copias de la palabra a la vez → la grande termina en el cuadro del corte, la chica entra después.
- Si el pelo tapa > 30 % de las letras → subir la palabra o achicarla.

**Costo.** Placa + recorte ~5 min por congelado; construcción de una pasada con esta receta.

---

## Por probar

Ejemplos que al director le encantaron y aún no son receta. Formato:
`- [nombre](enlace) — qué tiene de bueno — intensidad sugerida`
