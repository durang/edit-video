# Pipeline completo — generar, iluminar, montar

`/edit-video` es el **último eslabón**. Casi todo lo que se hace en el canon de Seedance/Grok
termina aquí. Esto es lo que se combina con qué.

```
  IDEA ─┬─► Seedance / Grok ─────────────────┐     (generar escenas, personajes, TV show, vlog)
        │                                     │
  TOMA ─┼─► multiángulo (Seedance) ──────────┤     (una toma → cobertura multicámara)
  REAL  ├─► cine-grade (Seedance) ───────────┤     (la luz de una película)
        ├─► swap Genjutsu (Higgsfield) ──────┤     (cambiar mundo, ropa, persona)
        │                                     ▼
        └──────────────────────────► /edit-video   (subtítulos, cortes, gráficos, música, render)
```

## Qué aporta cada lado

| Generación (Seedance / Grok / Genjutsu) | Montaje (`/edit-video` + HyperFrames) |
|---|---|
| Personas, escenas, cámara, luz, actuación | Texto, subtítulos, gráficos, ritmo, audio |
| **No** pone texto legible (lo rompe) | **Sí** pone texto perfecto, en tu fuente |
| Clips de 4–30 s | Une clips de cualquier duración |
| Audio generado o preservado | Mezcla, ducking, música, SFX |

**Regla de oro de la combinación: el texto nunca se genera, se monta.** Seedance y Grok escriben
mal las letras; los rótulos, subtítulos, precios y logos van siempre en HyperFrames encima.

## Recetas

### 1. Asesores Aldara con multiángulo + subtítulos
1. Clip A y clip B por Seedance con los prompts de multiángulo.
2. `/edit-video`: une A + B en orden, **audio original intacto**, subtítulos en español con
   `/embedded-captions`, rótulo con el nombre de cada asesor la primera vez que habla con
   `/talking-head-recut`, logo de Aldara al cierre.

### 2. Talking head con look de película
1. `cine-grade` en Seedance: la luz de la película, mismo encuadre, misma voz.
2. `/edit-video`: subtítulos en el estilo del género (tráiler, noir…), título de apertura.

### 3. Serie de personaje (@vigilante, Figo y el Humano)
1. Episodio generado en Grok o Seedance.
2. `/edit-video`: cabecera del show (logo animado con `/motion-graphics`), subtítulos, placa
   con el nombre del episodio, música de cierre con `/hyperframes-audio`.

### 4. Vlog de una toma con cameos
1. Generado en Grok.
2. `/edit-video`: subtítulos palabra por palabra, SFX en cada cameo, reencuadre 9:16.

## Traspaso Seedance → montaje

- **Exportar siempre el MP4 del generador sin recomprimir** y dejarlo en la carpeta del montaje.
- **Si el clip se generó en varias subidas** (Seedance corta en 30 s), nombrarlos en orden
  (`A.mp4`, `B.mp4`) y decirlo en el primer prompt: *"une A y B en este orden"*.
- **El render de Genjutsu vuelve ~0.1 s más corto** por la cola. Si hay que re-sincronizar
  con el audio original, se hace aquí.
- **La transcripción se hace sobre el clip generado, no sobre el original**: si el modelo movió
  el timing, los subtítulos siguen al clip nuevo.
