// node exposure_sheet.test.js — pruebas de la hoja de exposición (sin dependencias)
const assert = require("assert");
const X = require("./exposure_sheet.js");
const S = [[0, 0], [2.5, 1], [2.6, 2], [2.7, 3]];
assert.deepStrictEqual(X.sheetState(S, 0).cur, 0);
assert.strictEqual(X.sheetState(S, 2.49).cur, 0);
// cuadro del cambio: fundido 50 % entre el anterior y el nuevo; el siguiente cuadro ya es 100 %
let s = X.sheetState(S, 2.5);
assert.strictEqual(s.cur, 1); assert.strictEqual(s.prev, 0); assert.ok(Math.abs(s.mix - 0.5) < 1e-6);
assert.strictEqual(X.sheetState(S, 2.5 + 1 / 30).mix, 1);
assert.strictEqual(X.sheetState(S, 9).cur, 3);
// sin fundido
assert.strictEqual(X.sheetState(S, 2.5, { xfade: 0 }).mix, 1);
// boil: determinista, cambia 12 veces por segundo, acotado
const a = X.boil(1.0), b = X.boil(1.0), c = X.boil(1.0 + 1 / 30), d = X.boil(1.0 + 1 / 12);
assert.deepStrictEqual(a, b);
assert.deepStrictEqual(a, c);          // mismo paso de 1/12 s
assert.notDeepStrictEqual(a, d);       // paso siguiente
for (let t = 0; t < 5; t += 1 / 30) { const q = X.boil(t); assert.ok(Math.abs(q.x) <= 1 && Math.abs(q.y) <= 1 && Math.abs(q.r) <= 0.15); }
// bucle a 10 por segundo
const L = X.loop([0, 1], 0.1, 1, 1.5);
assert.deepStrictEqual(L.map((e) => e[1]), [0, 1, 0, 1, 0]);
assert.strictEqual(L.length, 5);
// fundido propio de una entrada: 4 cuadros → 1/5, 2/5 … y 100 % al 4º cuadro
const S2 = [[0, 0], [1, 1, 4]];
assert.ok(Math.abs(X.sheetState(S2, 1).mix - 0.2) < 1e-9);
assert.ok(Math.abs(X.sheetState(S2, 1 + 3 / 30).mix - 0.8) < 1e-9);
assert.strictEqual(X.sheetState(S2, 1 + 4 / 30).mix, 1);
console.log("selftest exposure_sheet: OK");
