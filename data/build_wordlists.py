"""Genera las 1000 palabras más frecuentes de inglés y alemán.

Fuentes (ver README.md):
  A) wordfreq 3.x (Robyn Speer): mezcla Wikipedia, subtítulos, noticias, libros, web, Twitter, Reddit.
  B) FrequencyWords 2018 (hermitdave): corpus OpenSubtitles 2018. Archivos en_50k.txt / de_50k.txt
     en esta misma carpeta (descargar con las URLs del README).
Método: frecuencia por millón de cada fuente -> media aritmética; una palabra debe tener >= 5 por
millón en AMBAS fuentes. Se unifican variantes ß/ss, se filtran no-palabras y se aplican las
exclusiones manuales de abajo. Uso:  pip install wordfreq  &&  python build_wordlists.py
"""
import csv, json, math, os, re
from wordfreq import top_n_list, word_frequency

HERE = os.path.dirname(os.path.abspath(__file__))
N, MIN_PM = 1000, 5.0
WORD = re.compile(r"[^\W\d_]+")            # solo letras: sin dígitos, apóstrofes, puntos ni guiones
KEEP1 = {'en': {'a', 'i'}, 'de': set()}     # palabras válidas de una letra

# Fragmentos de contracciones inglesas que deja la tokenización de subtítulos (don't -> don + 't)
FRAGMENTS = set("don didn doesn isn wasn aren weren couldn wouldn shouldn haven hasn hadn ain ll ve re cause".split())
COLLOQUIAL = set("gonna wanna gotta".split())
FILLERS = set("uh um ah hm hmm huh whoa ha äh tja".split())          # muletillas sin contenido léxico
ABBREV = set("mr dr st ma em la al de tv ok non ii nen ne usa".split())
NAMES = {
 'en': set("john york david michael jack george james paul peter sam joe tom jesus london england america china".split()),
 'de': set("berlin münchen deutschland europa paris wien hamburg york john michael peter jack frank martin paul thomas max".split()),
}
# Palabras inglesas que aparecen en los subtítulos alemanes (subtítulos mal etiquetados / anglicismos de guion)
LEAKS_DE = set("the of and to is he you new bad dad mom sir miss pass captain".split())
EXCLUDE = {'en': COLLOQUIAL | FILLERS | ABBREV | NAMES['en'],
           'de': FILLERS | ABBREV | NAMES['de'] | LEAKS_DE | {'us'}}

def read_subs(lang):
    counts, total = {}, 0
    for line in open(os.path.join(HERE, f'{lang}_50k.txt'), encoding='utf-8'):
        w, c = line.split(); counts[w] = int(c); total += int(c)
    return counts, total

def build(lang):
    sub, total = read_subs(lang)
    cand = set(top_n_list(lang, 4000)) | set(list(sub)[:4000])
    keys = {}
    for w in cand:
        if not WORD.fullmatch(w) or (len(w) == 1 and w not in KEEP1[lang]): continue
        if lang == 'en' and w in FRAGMENTS: continue
        keys.setdefault(w.replace('ß', 'ss') if lang == 'de' else w, None)
    rows = []
    for key in keys:
        if lang == 'de':   # wordfreq normaliza ß->ss: elegir la grafía dominante en subtítulos (dass, groß, weiß…)
            variants = {key} | {v for v in sub if v.replace('ß', 'ss') == key}
        else:
            variants = {key}
        counts = {v: sub.get(v, 0) for v in variants}
        word = max(counts, key=counts.get) if any(counts.values()) else key
        f_sub = sum(counts.values()) / total * 1e6
        f_wf = word_frequency(key, lang) * 1e6
        if min(f_wf, f_sub) < MIN_PM or word in EXCLUDE[lang]: continue
        rows.append((word, (f_wf + f_sub) / 2, f_wf, f_sub))
    rows.sort(key=lambda r: -r[1])
    return rows[:N]

if __name__ == '__main__':
    out = {}
    for lang in ('en', 'de'):
        rows = build(lang)
        with open(os.path.join(HERE, f'{lang}_top1000.csv'), 'w', newline='', encoding='utf-8-sig') as f:
            wr = csv.writer(f); wr.writerow(['rank', 'word', 'per_million', 'zipf', 'wordfreq_pm', 'opensubtitles_pm'])
            for i, (w, pm, a, b) in enumerate(rows, 1):
                wr.writerow([i, w, round(pm, 2), round(math.log10(pm) + 3, 2), round(a, 2), round(b, 2)])
        out[lang] = [{'r': i, 'w': w} for i, (w, *_) in enumerate(rows, 1)]
        print(lang, len(rows), 'palabras; cobertura aprox. del texto: %.1f%%' % (sum(r[1] for r in rows) / 1e4))
    json.dump(out, open(os.path.join(HERE, 'top1000.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
