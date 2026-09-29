# Pipeline — generar, montar

`/edit-video` es **el último eslabón**. Lo que sale de un modelo generativo casi nunca está
terminado: le faltan texto, subtítulos, ritmo, música y un cierre. Eso se hace aquí.

```
  IDEA ──► modelo generativo (Seedance, Grok, Veo, Kling, Runway…) ──┐
                                                                     │   escenas, personas,
  TOMA REAL ──► re-filmado / re-iluminado / swap (Seedance, Genjutsu)─┤   cámara, luz, actuación
                                                                     ▼
                                                              /edit-video   texto, subtítulos,
                                                                            gráficos, ritmo,
                                                                            audio, render final
```

## Qué pone cada lado

| Generativo | `/edit-video` + HyperFrames |
|---|---|
| Personas, escenas, cámara, luz, actuación | Texto, subtítulos, gráficos, ritmo, audio |
| **Escribe mal las letras** | **Texto perfecto**, en tu tipografía |
| Clips de 4 a 30 segundos | Une clips de cualquier duración |
| Audio generado o preservado | Mezcla, ducking, música, efectos |

**Regla de oro: el texto nunca se genera, se monta.** Los modelos generativos rompen letras,
rótulos, precios y logos. Todo eso va encima, en HyperFrames.

## Recetas

### Varias personas, cada una grabada por separado
1. Si hace falta, cobertura multicámara de cada toma con el generativo.
2. `/edit-video`: une en orden con el **audio original intacto**, subtítulos, y el nombre de cada
   persona en un rótulo la primera vez que habla.

### Talking head con el look de una película
1. Re-iluminado con el generativo (misma cara, misma voz, luz nueva).
2. `/edit-video`: subtítulos en el estilo del género, título de apertura.

### Serie o personaje recurrente
1. Episodio generado.
2. `/edit-video`: cabecera del show (logo animado con `motion-graphics`), subtítulos, placa con el
   nombre del episodio, música de cierre con `hyperframes-audio`.

### Video de una toma generado (vlog, POV)
1. Generado de una pieza.
2. `/edit-video`: subtítulos palabra por palabra, SFX en los momentos clave, reencuadre 9:16.

## Traspaso generativo → montaje

- **Exporta el MP4 del generador sin recomprimir** y déjalo en la carpeta del montaje.
- **Si se generó en varias subidas** (muchos modelos cortan en 15 o 30 s), nómbralas en orden
  (`A.mp4`, `B.mp4`…) y dilo en el primer pedido: *"une A y B en este orden"*.
- **Algunos generadores devuelven el clip unas décimas más corto**, recortado por la cola. Si hay
  que re-sincronizar con el audio original, se hace aquí.
- **Transcribe el clip generado, no el original.** Si el modelo movió el timing, los subtítulos
  tienen que seguir al clip nuevo.
