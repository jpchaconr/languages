# 1000 palabras más frecuentes: inglés, alemán y ruso

## Archivos

| Archivo | Contenido |
|---|---|
| `palabras.js` / `palabras.json` | **Base final** en el formato de `index.html`: `{en:{name,code,voice,words:[{r,w,ipa,pos,es,ex}]}, de:{…}, ru:{…}}` (`palabras.js` define `const DATA = …`). En alemán y ruso los sustantivos llevan además `g` (`m`, `f`, `n`, `pl`). En ruso `w` lleva el acento marcado (`молоко́`, con U+0301; la ё ya indica el acento). |
| `en_full.json`, `de_full.json`, `ru_full.json` | Igual, por idioma (lista de palabras). `palabras.js` se arma con estos tres. |
| `en_top1000.csv`, `de_top1000.csv`, `ru_top1000.csv` | Solo frecuencias (rank, word, per_million, zipf, wordfreq_pm, opensubtitles_pm). |
| `top1000.json` | Solo `{r, w}`. |
| `src/*.txt` | Texto fuente de categoría, traducción y ejemplos (`palabra\|cat\|es\|ej1\|trad1\|ej2\|trad2`). En ruso la palabra se escribe con el acento marcado (`бы́ло\|v\|…`). |
| `build_wordlists.py`, `merge.py` | Scripts que generan las listas de frecuencia y la base final. |
| `ru_ipa.py` | Transcripción IPA del ruso a partir de la palabra acentuada (la usa `merge.py`). |

Cada entrada: `r` puesto · `w` palabra · `ipa` · `pos` categoría · `es` traducciones (array) · `ex` dos ejemplos `[frase con *palabra* marcada, traducción]`.

## Fuentes

**Frecuencia (qué palabras)**
1. [wordfreq 3.x](https://github.com/rspeer/wordfreq) (Robyn Speer): Wikipedia, subtítulos, noticias, libros, web, Twitter y Reddit.
2. [FrequencyWords 2018](https://github.com/hermitdave/FrequencyWords) (hermitdave), sobre OpenSubtitles 2018: `en_50k.txt`, `de_50k.txt` y `ru_50k.txt`.

**Pronunciación (IPA)**
- Inglés y alemán: [ipa-dict](https://github.com/open-dict-data/ipa-dict) (open-dict-data). Inglés `en_US.txt`, derivado de CMUdict (inglés general americano); alemán `de.txt`, derivado de Wiktionary. Normalizado en `merge.py` (`ɹ→r`, `ɝ→ɜr`, `ʌ` tónica, sin acento en monosílabos, sin ligadura de africadas). Solo `darum`, `wär`, `zu Hause` y `Band` se fijaron a mano.
- Ruso: ipa-dict no tiene ruso, y la transcripción rusa de Wiktionary que recoge [WikiPron](https://github.com/CUNY-CL/wikipron) (`rus_cyrl_narrow.tsv`) viene sin marcas de acento y mezcla variantes dialectales. Por eso `ru_ipa.py` genera la IPA a partir de la palabra acentuada, con las reglas del módulo de pronunciación de Wiktionary (reducción vocálica, consonantes blandas, ensordecimiento y asimilación, grupos como `здра́вствуйте` o `се́рдце`, `-ого` con [v], `-тся` como [tsə]). `merge.py` la compara con WikiPron: **959** de las 1000 coinciden exactamente con alguna transcripción de Wiktionary, 24 no están en Wiktionary (casi todas con guion: `что́-то`, `из-за́`…) y se revisaron a mano, 6 se fijaron a mano (`до сих пор`, `обо`, `кое-что́`, `би́знес`, `дво́е`, `у́лице`) y en 11 se mantuvo la transcripción generada frente a la de Wiktionary (`ты`, `ни` y `об` en forma de cita, `семья́` con [mʲ]…; lista `IPA_KEEP` en `merge.py`). Es una transcripción fonética estrecha, al estilo de Wiktionary (`/məɫɐˈko/`), aunque va entre barras como la de los otros idiomas.

**Acento del ruso**: marcado en cada palabra al redactar `src/ru_*.txt` y verificado de forma indirecta al comparar la IPA con Wiktionary (la reducción vocálica delata una sílaba tónica equivocada).

**Categoría, traducción al español y ejemplos**: redactados por Claude (no proceden de un diccionario publicado).

Descargas necesarias para regenerar (`merge.py` las lee de esta carpeta; se retiraron por tamaño):
```
curl -LO https://raw.githubusercontent.com/open-dict-data/ipa-dict/master/data/en_US.txt
curl -LO https://raw.githubusercontent.com/open-dict-data/ipa-dict/master/data/de.txt
curl -LO https://raw.githubusercontent.com/CUNY-CL/wikipron/master/data/scrape/tsv/rus_cyrl_narrow.tsv
```
`python merge.py ru` regenera solo el ruso y vuelve a armar `palabras.js` con los `*_full.json` existentes, así que basta con descargar el archivo del idioma que se regenere.

## Método de frecuencia
- Frecuencia por millón de cada fuente; puntuación = media. `zipf` = log10(por millón) + 3.
- Entra solo si tiene ≥ 5 por millón en **ambas** fuentes.
- Solo formas alfabéticas en minúscula: sin dígitos, contracciones ni abreviaturas.
- Alemán: `wordfreq` convierte `ß`→`ss`; se unificaron variantes y se eligió la grafía dominante en subtítulos (`weiß`, `groß`, `dass`).
- Ruso:
  - Solo cirílico. Se admiten las palabras con guion (`что-то`, `из-за`, `по-моему`), que son unidades léxicas. Como wordfreq las parte en dos, solo se pueden medir en los subtítulos, así que su puntuación es la de los subtítulos.
  - La ё se escribe a menudo como е (`еще` = `ещё`): se suman las dos grafías y se muestra la de ё (la del diccionario) si supone al menos el 10 % de los usos. `все`/`всё`, `чем`/`чём`, `всем`/`всём` y `чем-то`/`чём-то` son palabras distintas y se cuentan por separado.
  - Las 8 palabras de una letra (`в`, `и`, `с`, `к`, `у`, `о`, `а`, `я`) son válidas; el resto de letras sueltas no.
- Exclusiones manuales (listadas en `build_wordlists.py`): nombres propios (`джон`, `россии`, `москве`), muletillas (`uh`, `äh`, `э`, `хм`), siglas (`mr`, `usa`, `сша`), formas coloquiales (`gonna`, `wanna`, `gotta`), palabras inglesas filtradas en subtítulos alemanes (`the`, `dad`, `you`…) y trozos que deja wordfreq al partir palabras con guion (`нибудь`, `нью`).

## Validación
`merge.py` comprueba que las 1000 palabras de cada idioma tengan entrada, que cada ejemplo marque **exactamente** la palabra de la lista (con su forma flexionada), que haya IPA y una categoría válida, y en ruso que toda palabra de más de una sílaba tenga el acento marcado. También avisa si la IPA rusa no coincide con Wiktionary. Además se releyeron a mano las frases alemanas y rusas y se corrigieron las mal formadas.

## Limitaciones
- **Formas, no lemas**: `go`, `goes`, `went`, `habe`, `hast`, `hat` y `знаю`, `знаешь`, `знает` cuentan por separado. En las formas flexionadas la traducción indica de qué verbo/lema vienen («fue, fui (pasado de «go»)», «vida (genitivo, dativo y preposicional de «жизнь»)»). El ruso, muy flexivo, llena la lista de formas: las 1000 cubren ~59 % del texto frente a ~71 % en inglés y alemán.
- **Categoría gramatical única**: se da la más frecuente y las otras se anotan en la traducción (`v: …`, `s: …`). En ruso se añadió la categoría `partícula` (`не`, `же`, `ли`, `бы`, `вот`…).
- **Homógrafos rusos con distinto acento** (`пра́ва`/`права́`, `нача́ла`/`начала́`, `игры́`/`и́гры`, `дру́гом`/`друго́м`, `ме́ста`/`места́`): se eligió el más frecuente, y el otro se anota en la traducción con su acento.
- **El acento solo se marca en la palabra de la tarjeta**, no en los ejemplos, que van en ruso normal (con ё siempre). La voz del navegador recibe el texto sin la marca de acento; para oír ruso hace falta una voz rusa en el dispositivo.
- **Traducciones y ejemplos no revisados por un hablante nativo**. Es aconsejable una revisión puntual, sobre todo del alemán coloquial, de las glosas de partículas (`doch`, `halt`, `mal`, `eben`, `же`, `ведь`, `уж`) y de los ejemplos rusos.
- **IPA**: la inglesa es americana y viene de un diccionario de pronunciación (sin marcas de longitud `ː`); en palabras funcionales (`the`, `to`…) es la forma de cita, no la reducida. La rusa también da la forma de cita de las preposiciones y partículas (`не` /nʲe/, `в` /v/), que en la frase suelen ser átonas.
- **Sesgo de subtítulos**: hay lenguaje hablado y vulgar (`shit`, `scheiße`, `fuck`, `чёрт`) y tratamientos de películas traducidas (`sir`, `сэр`, `мистер`, `мисс`); se conservaron porque son frecuentes de verdad.
- Las dos fuentes de frecuencia no son independientes (wordfreq incluye subtítulos) y solo coinciden ~68 % antes de filtrar: las palabras cerca del puesto 1000 son intercambiables. En ruso, las palabras con guion (medidas solo en subtítulos) tienden a quedar algo más arriba, y las grafías con е de `все` y `чем` incluyen algunos usos de `всё` y `чём` escritos sin diéresis.
- 43 frases inglesas y 52 rusas se reutilizan en dos entradas (con la palabra marcada distinta).
