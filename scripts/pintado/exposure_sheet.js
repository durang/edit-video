/* exposure_sheet.js — hoja de exposición para planos pintados en HyperFrames
 * (receta references/pintado-a-mano.md §7).
 *
 * Una hoja dice qué dibujo se ve en cada segundo, como la carta de tiempos de un animador:
 *     [[0, 0], [2.5, 1], [2.6, 2], [2.7, 3]]   // [segundo, dibujo]
 * - Cada cambio de dibujo lleva un fundido de 1 cuadro (configurable) que suaviza el salto. Una entrada
 *   [t, dibujo, cuadros] pide un fundido más largo solo para ese cambio (una lámpara que se enciende: 36).
 * - Un "boil" a 12 fps mantiene vivo el dibujo quieto, como crayón de verdad: ±1 px y ±0.15°,
 *   determinista (misma t → mismo cuadro), sin parpadeo de luz (solo posición).
 *
 * Uso en la composición (una capa con un <img> por dibujo, apilados con position:absolute):
 *     <div id="s1">  <img src="s1/00.png"> <img src="s1/01.png"> …  </div>
 *     (y este archivo cargado con una etiqueta script src="assets/exposure_sheet.js" en el head)
 *     const S1 = [[0, 0], [1.2, 1], [1.3, 0], …];
 *     tl.to(clock, { t: DUR, duration: DUR, ease: "none", onUpdate: () => {
 *         ExposureSheet.sheetDraw("s1", S1, clock.t);          // o sheetDraw(elemento, …)
 *     }}, 0);
 *
 * Bucles (dedo que hace scroll, parpadeo de ojos): ExposureSheet.loop([0, 1], 0.1, t0, t1) genera las
 * entradas [t, dibujo] alternando cada 0.1 s (10 por segundo) entre t0 y t1.
 *
 * OJO: este comentario no lleva la etiqueta de cierre de script escrita: HyperFrames puede incrustar el
 * archivo dentro del HTML y esa etiqueta cortaría el script ("Invalid or unexpected token").
 * Sin dependencias, sin Math.random ni Date.now. Funciona en el navegador (window.ExposureSheet) y en
 * Node (module.exports) para las pruebas: `node exposure_sheet.test.js`.
 */
(function (root) {
  "use strict";

  var DEFAULTS = { fps: 30, xfade: 1, boil: { fps: 12, px: 1.0, deg: 0.15, seed: 1 } };

  function opts(o) {
    o = o || {};
    var b = o.boil === false ? false : Object.assign({}, DEFAULTS.boil, o.boil || {});
    return { fps: o.fps || DEFAULTS.fps, xfade: o.xfade == null ? DEFAULTS.xfade : o.xfade, boil: b, boilT: o.boilT };
  }

  /** Estado puro de la hoja en t: { cur, prev, mix } — mix 0→1 es el peso de cur durante el fundido. */
  function sheetState(sheet, t, o) {
    o = opts(o);
    var i = 0;
    for (var k = 0; k < sheet.length; k++) if (sheet[k][0] <= t + 1e-9) i = k;
    var cur = sheet[i][1];
    var prev = i > 0 ? sheet[i - 1][1] : cur;
    // en cuadros enteros (sin errores de coma flotante): el cuadro del cambio y los xfade-1 siguientes funden
    var xf = sheet[i].length > 2 ? sheet[i][2] : o.xfade;   // [t, dibujo, cuadros]: fundido propio (luz que cambia)
    var f = Math.round((t - sheet[i][0]) * o.fps);
    var mix = i > 0 && f < xf ? (f + 1) / (xf + 1) : 1;
    if (prev === cur) mix = 1;
    return { cur: cur, prev: prev, mix: mix, index: i };
  }

  // hash entero → [0,1) determinista (sin Math.random)
  function hash(n, seed) {
    var x = (n * 374761393 + seed * 668265263) | 0;
    x = (x ^ (x >>> 13)) * 1274126177;
    x = x ^ (x >>> 16);
    return ((x >>> 0) % 100000) / 100000;
  }

  /** Desplazamiento del boil en t: { x, y, r } (px, px, grados). Cambia 12 veces por segundo. */
  function boil(t, b) {
    if (b === false) return { x: 0, y: 0, r: 0 };
    b = Object.assign({}, DEFAULTS.boil, b || {});
    var step = Math.floor(t * b.fps + 1e-6);
    return {
      x: (hash(step, b.seed) * 2 - 1) * b.px,
      y: (hash(step, b.seed + 7) * 2 - 1) * b.px,
      r: (hash(step, b.seed + 13) * 2 - 1) * b.deg,
    };
  }

  /** Entradas [t, dibujo] alternando `draws` cada `every` segundos entre t0 y t1 (sin incluir t1). */
  function loop(draws, every, t0, t1) {
    var out = [];
    for (var k = 0; t0 + k * every < t1 - 1e-9; k++) out.push([+(t0 + k * every).toFixed(4), draws[k % draws.length]]);
    return out;
  }

  /** Pinta la hoja en la capa `el` (id o elemento): opacidades de sus hijos + boil en la capa. */
  function sheetDraw(el, sheet, t, o) {
    if (typeof el === "string") el = root.document.getElementById(el);
    if (!el) return null;
    o = opts(o);
    var st = sheetState(sheet, t, o);
    var kids = el.children;
    for (var k = 0; k < kids.length; k++) {
      var s = kids[k].style;
      if (k === st.cur) { s.opacity = st.mix; s.zIndex = 2; }
      else if (k === st.prev && st.mix < 1) { s.opacity = 1; s.zIndex = 1; }
      else { s.opacity = 0; s.zIndex = 0; }
    }
    var bo = boil(o.boilT != null ? o.boilT : t, o.boil);   // boilT: congela el boil (un "todo se detiene") sin congelar la hoja
    el.style.transform = "translate(" + bo.x.toFixed(2) + "px," + bo.y.toFixed(2) + "px) rotate(" + bo.r.toFixed(3) + "deg)";
    return st;
  }

  var api = { sheetState: sheetState, sheetDraw: sheetDraw, boil: boil, loop: loop, DEFAULTS: DEFAULTS };
  if (typeof module !== "undefined" && module.exports) module.exports = api;
  else root.ExposureSheet = api;
})(typeof window !== "undefined" ? window : this);
