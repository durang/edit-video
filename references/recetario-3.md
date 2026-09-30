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

## Por probar

Ejemplos que al director le encantaron y aún no son receta. Formato:
`- [nombre](enlace) — qué tiene de bueno — intensidad sugerida`
