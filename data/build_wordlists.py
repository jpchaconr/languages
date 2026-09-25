"""Genera las 1000 palabras más frecuentes de inglés, alemán y ruso.

Fuentes (ver README.md):
  A) wordfreq 3.x (Robyn Speer): mezcla Wikipedia, subtítulos, noticias, libros, web, Twitter, Reddit.
  B) FrequencyWords 2018 (hermitdave): corpus OpenSubtitles 2018. Archivos en_50k.txt / de_50k.txt / ru_50k.txt
     en esta misma carpeta (descargar con las URLs del README).
Método: frecuencia por millón de cada fuente -> media aritmética; una palabra debe tener >= 5 por
millón en AMBAS fuentes. Se unifican variantes ß/ss y е/ё, se filtran no-palabras y se aplican las
exclusiones manuales de abajo. Las palabras rusas con guion (что-то, из-за) solo se pueden medir en los
subtítulos (wordfreq las parte en dos): su puntuación es la de los subtítulos.
Uso:  pip install wordfreq  &&  python build_wordlists.py [en|de|ru]   (sin argumentos: los tres)
"""
import csv, json, math, os, re, sys
from wordfreq import top_n_list, word_frequency

HERE = os.path.dirname(os.path.abspath(__file__))
N, MIN_PM = 1000, 5.0
WORD = re.compile(r"[^\W\d_]+")            # solo letras: sin dígitos, apóstrofes, puntos ni guiones
WORD_RU = re.compile(r"[а-яё]+(?:-[а-яё]+)*")   # ruso: solo cirílico; el guion solo dentro de compuestos (что-то, из-за)
KEEP1 = {'en': {'a', 'i'}, 'de': set(), 'ru': set('авикосуя')}     # palabras válidas de una letra

# Fragmentos de contracciones inglesas que deja la tokenización de subtítulos (don't -> don + 't)
FRAGMENTS = set("don didn doesn isn wasn aren weren couldn wouldn shouldn haven hasn hadn ain ll ve re cause".split())
COLLOQUIAL = set("gonna wanna gotta".split())
FILLERS = set("uh um ah hm hmm huh whoa ha äh tja".split())          # muletillas sin contenido léxico
ABBREV = set("mr dr st ma em la al de tv ok non ii nen ne usa".split())
NAMES = {
 'en': set("john york david michael jack george james paul peter sam joe tom jesus london england america china".split()),
 'de': set("berlin münchen deutschland europa paris wien hamburg york john michael peter jack frank martin paul thomas max".split()),
 'ru': set("россия россии москва москве германии франции европы джон джек джо питер александр сергей".split()),
}
# Palabras inglesas que aparecen en los subtítulos alemanes (subtítulos mal etiquetados / anglicismos de guion)
LEAKS_DE = set("the of and to is he you new bad dad mom sir miss pass captain".split())
# Ruso: muletillas, siglas y trozos que deja wordfreq al partir compuestos con guion (что-нибудь -> что + нибудь, Нью-Йорк)
SKIP_RU = set("э эм мм хм".split()) | set("сша см ок го де".split()) | set("нибудь нью".split())
# е/ё: en ruso la ё se escribe a menudo como е (еще = ещё) y se unifican, salvo si las dos grafías son palabras distintas
YO_SPLIT = set("все всё всем всём чем чём чем-то чём-то".split())
EXCLUDE = {'en': COLLOQUIAL | FILLERS | ABBREV | NAMES['en'],
           'de': FILLERS | ABBREV | NAMES['de'] | LEAKS_DE | {'us'},
           'ru': SKIP_RU | NAMES['ru']}

def norm(w, lang):
    """Clave que agrupa las grafías de una misma palabra: ß -> ss (wordfreq ya lo hace), ё -> е."""
    if lang == 'de': return w.replace('ß', 'ss')
    if lang == 'ru': return w if w in YO_SPLIT else w.replace('ё', 'е')
    return w

def read_subs(lang):
    counts, total = {}, 0
    for line in open(os.path.join(HERE, f'{lang}_50k.txt'), encoding='utf-8'):
        w, c = line.split(); counts[w] = int(c); total += int(c)
    return counts, total

def build(lang):
    sub, total = read_subs(lang)
    cand = set(top_n_list(lang, 4000)) | set(list(sub)[:4000])
    word_re = WORD_RU if lang == 'ru' else WORD
    keys = {}
    for w in cand:
        if not word_re.fullmatch(w) or (len(w) == 1 and w not in KEEP1[lang]): continue
        if lang == 'en' and w in FRAGMENTS: continue
        parts = w.split('-')
        if len(parts) > 1 and (len(set(parts)) < len(parts) or min(map(len, parts)) == 1): continue   # да-да, ха-ха, н-нет
        keys.setdefault(norm(w, lang), None)
    spellings = {}
    if lang in ('de', 'ru'):   # todas las grafías de cada clave: subtítulos y (en ruso, que wordfreq no unifica) wordfreq
        pool = set(sub) | (set(top_n_list('ru', 50000)) if lang == 'ru' else set())
        for v in pool:
            if word_re.fullmatch(v): spellings.setdefault(norm(v, lang), set()).add(v)
    rows = []
    for key in keys:
        variants = {key} | spellings.get(key, set())
        counts = {v: sub.get(v, 0) for v in variants}
        if lang == 'ru':   # se muestra con ё si esa grafía supone al menos el 10 % de los usos (еще -> ещё)
            yo = max((v for v in variants if 'ё' in v), key=counts.get, default=None)
            word = yo if yo and counts[yo] >= 0.1 * sum(counts.values()) else key
        else:              # alemán: la grafía dominante en subtítulos (dass, groß, weiß…)
            word = max(counts, key=counts.get) if any(counts.values()) else key
        f_sub = sum(counts.values()) / total * 1e6
        if lang != 'ru': f_wf = word_frequency(key, lang) * 1e6
        elif '-' in key: f_wf = None                                   # wordfreq no mide compuestos con guion
        else: f_wf = sum(word_frequency(v, lang) for v in variants) * 1e6
        if min(f_sub, f_sub if f_wf is None else f_wf) < MIN_PM or key in EXCLUDE[lang] or word in EXCLUDE[lang]: continue
        rows.append((word, f_sub if f_wf is None else (f_wf + f_sub) / 2, f_wf, f_sub))
    rows.sort(key=lambda r: -r[1])
    return rows[:N]

if __name__ == '__main__':
    fn = os.path.join(HERE, 'top1000.json')
    out = json.load(open(fn, encoding='utf-8')) if os.path.exists(fn) else {}
    for lang in sys.argv[1:] or ('en', 'de', 'ru'):
        rows = build(lang)
        with open(os.path.join(HERE, f'{lang}_top1000.csv'), 'w', newline='', encoding='utf-8-sig') as f:
            wr = csv.writer(f); wr.writerow(['rank', 'word', 'per_million', 'zipf', 'wordfreq_pm', 'opensubtitles_pm'])
            for i, (w, pm, a, b) in enumerate(rows, 1):
                wr.writerow([i, w, round(pm, 2), round(math.log10(pm) + 3, 2), '' if a is None else round(a, 2), round(b, 2)])
        out[lang] = [{'r': i, 'w': w} for i, (w, *_) in enumerate(rows, 1)]
        print(lang, len(rows), 'palabras; cobertura aprox. del texto: %.1f%%' % (sum(r[1] for r in rows) / 1e4))
    json.dump(out, open(fn, 'w', encoding='utf-8'), ensure_ascii=False, indent=1)
