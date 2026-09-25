# 1000 palabras más frecuentes: inglés y alemán

## Archivos

| Archivo | Contenido |
|---|---|
| `palabras.js` / `palabras.json` | **Base final** en el formato de `index.html`: `{en:{name,code,voice,words:[{r,w,ipa,pos,es,ex}]}, de:{…}}` (`palabras.js` define `const DATA = …`). En alemán los sustantivos llevan además `g` (`m`, `f`, `n`, `pl`). |
| `en_full.json`, `de_full.json` | Igual, por idioma (lista de palabras). |
| `en_top1000.csv`, `de_top1000.csv` | Solo frecuencias (rank, word, per_million, zipf, wordfreq_pm, opensubtitles_pm). |
| `top1000.json` | Solo `{r, w}`. |
| `src/*.txt` | Texto fuente de categoría, traducción y ejemplos (`palabra\|cat\|es\|ej1\|trad1\|ej2\|trad2`). |
| `build_wordlists.py`, `merge.py` | Scripts que generan las listas de frecuencia y la base final. |

Cada entrada: `r` puesto · `w` palabra · `ipa` · `pos` categoría · `es` traducciones (array) · `ex` dos ejemplos `[frase con *palabra* marcada, traducción]`.

## Fuentes

**Frecuencia (qué palabras)**
1. [wordfreq 3.x](https://github.com/rspeer/wordfreq) (Robyn Speer): Wikipedia, subtítulos, noticias, libros, web, Twitter y Reddit.
2. [FrequencyWords 2018](https://github.com/hermitdave/FrequencyWords) (hermitdave), sobre OpenSubtitles 2018: `en_50k.txt` y `de_50k.txt`.

**Pronunciación (IPA)**: [ipa-dict](https://github.com/open-dict-data/ipa-dict) (open-dict-data). Inglés `en_US.txt`, derivado de CMUdict (inglés general americano); alemán `de.txt`, derivado de Wiktionary. Normalizado en `merge.py` (`ɹ→r`, `ɝ→ɜr`, `ʌ` tónica, sin acento en monosílabos, sin ligadura de africadas). Solo `darum`, `wär`, `zu Hause` y `Band` se fijaron a mano.

**Categoría, traducción al español y ejemplos**: redactados por Claude (no proceden de un diccionario publicado).

Descargas necesarias para regenerar (`merge.py` las lee de esta carpeta; se retiraron por tamaño):
```
curl -LO https://raw.githubusercontent.com/open-dict-data/ipa-dict/master/data/en_US.txt
curl -LO https://raw.githubusercontent.com/open-dict-data/ipa-dict/master/data/de.txt
```

## Método de frecuencia
- Frecuencia por millón de cada fuente; puntuación = media. `zipf` = log10(por millón) + 3.
- Entra solo si tiene ≥ 5 por millón en **ambas** fuentes.
- Solo formas alfabéticas en minúscula: sin dígitos, contracciones ni abreviaturas.
- Alemán: `wordfreq` convierte `ß`→`ss`; se unificaron variantes y se eligió la grafía dominante en subtítulos (`weiß`, `groß`, `dass`).
- Exclusiones manuales (listadas en `build_wordlists.py`): nombres propios, muletillas (`uh`, `äh`), siglas (`mr`, `usa`), formas coloquiales (`gonna`, `wanna`, `gotta`) y palabras inglesas filtradas en subtítulos alemanes (`the`, `dad`, `you`…).

## Validación
`merge.py` comprueba que las 1000 palabras de cada idioma tengan entrada, que cada ejemplo marque **exactamente** la palabra de la lista (con su forma flexionada), que haya IPA y una categoría válida. Además se releyeron a mano las frases alemanas y se corrigieron las mal formadas.

## Limitaciones
- **Formas, no lemas**: `go`, `goes`, `went` y `habe`, `hast`, `hat` cuentan por separado. En las formas flexionadas la traducción indica de qué verbo/lema vienen («fue, fui (pasado de «go»)»).
- **Categoría gramatical única**: se da la más frecuente y las otras se anotan en la traducción (`v: …`, `s: …`).
- **Traducciones y ejemplos no revisados por un hablante nativo**. Es aconsejable una revisión puntual, sobre todo del alemán coloquial y de las glosas de partículas (`doch`, `halt`, `mal`, `eben`).
- **IPA**: la inglesa es americana y viene de un diccionario de pronunciación (sin marcas de longitud `ː`); en palabras funcionales (`the`, `to`…) es la forma de cita, no la reducida.
- **Sesgo de subtítulos**: hay lenguaje hablado y vulgar (`shit`, `scheiße`, `fuck`); se conservó porque es frecuente de verdad.
- Las dos fuentes de frecuencia no son independientes (wordfreq incluye subtítulos) y solo coinciden ~68 % antes de filtrar: las palabras cerca del puesto 1000 son intercambiables.
- 43 frases inglesas se reutilizan en dos entradas (con la palabra marcada distinta).
