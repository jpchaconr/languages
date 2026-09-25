"""Une frecuencias + IPA (ipa-dict) + categoría/traducción/ejemplos (src/*.txt) y valida.
Uso: python merge.py [en|de]   -> escribe {lang}_full.json y informa de errores."""
import csv, glob, json, os, re, sys
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
POS = dict(art='artículo', pron='pronombre', v='verbo', s='sustantivo', adj='adjetivo', adv='adverbio',
           prep='preposición', conj='conjunción', det='determinante', int='interjección', num='numeral')
GENDER = {'sm': 'm', 'sf': 'f', 'sn': 'n', 'sp': 'pl'}
META = {'en': dict(name='Inglés', code='EN', voice='en-US', ipafile='en_US.txt'),
        'de': dict(name='Alemán', code='DE', voice='de-DE', ipafile='de.txt')}
IPA_OVERRIDE = {'de': {'darum': '/daˈʁʊm/', 'wär': '/vɛːɐ̯/', 'hause': '/tsuː ˈhaʊ̯zə/', 'band': '/bɛnt/'}}
DISPLAY = {('de', 'hause'): 'zu Hause'}   # formas que solo existen dentro de una locución

def load_ipa(fn):
    d = {}
    for l in open(os.path.join(HERE, fn), encoding='utf-8'):
        p = l.rstrip('\n').split('\t')
        if len(p) >= 2: d.setdefault(p[0], p[1].split(', ')[0])
    return d

def norm_en(ipa, word=''):
    """ipa-dict (CMUdict) -> notación de diccionario: ɫ->l, ɝ->ɜr, ɚ->ər, hw->w, ʌ tónica, sin acento en monosílabos."""
    ipa = ipa.replace('ɹ', 'r').replace('ɫ', 'l').replace('ɝ', 'ɜr').replace('ɚ', 'ər').strip('/')
    ipa = re.sub(r'^(ˈ?)hw', r'\1w', ipa)
    if word != 'the':   # ə con acento primario es en realidad ʌ (CMUdict AH1)
        ipa = re.sub(r'(ˈ[^aeiouæɑɔəɛɪʊʌɜ]*)ə', r'\1ʌ', ipa, count=1)
    if len(re.findall(r'[aeiouæɑɔəɛɪʊʌɜ]+', ipa)) <= 1: ipa = ipa.replace('ˈ', '')   # sin acento en monosílabos
    return '/' + ipa + '/'

def norm_key(s, lang):
    s = s.lower()
    return s.replace('ß', 'ss') if lang == 'de' else s

def run(lang):
    rows = list(csv.DictReader(open(os.path.join(HERE, f'{lang}_top1000.csv'), encoding='utf-8-sig')))
    words = {int(r['rank']): r['word'] for r in rows}
    byword = {w: r for r, w in words.items()}
    ipad = load_ipa(META[lang]['ipafile'])
    src, errs = {}, []
    for fn in sorted(glob.glob(os.path.join(HERE, 'src', f'{lang}_*.txt'))):
        for n, line in enumerate(open(fn, encoding='utf-8'), 1):
            line = line.strip()
            if not line: continue
            p = line.split('|'); tag = f'{os.path.basename(fn)}:{n}'
            if len(p) != 7: errs.append(f'{tag} campos={len(p)}: {line[:60]}'); continue
            r = int(p[0]) if p[0].isdigit() else byword.get(p[0].lower())
            if r is None: errs.append(f'{tag} palabra «{p[0]}» no está en la lista'); continue
            if r in src: errs.append(f'{tag} rank {r} repetido'); continue
            src[r] = p[1:]
    out = []
    for r in sorted(src):
        pos, es, e1, t1, e2, t2 = src[r]; w = words.get(r)
        if w is None: errs.append(f'rank {r} no existe'); continue
        if pos not in POS and pos not in GENDER: errs.append(f'{r} {w}: categoría «{pos}»'); continue
        noun = pos in GENDER or pos == 's'
        disp = w.capitalize() if (lang == 'de' and noun) else ('I' if (lang == 'en' and w == 'i') else w)
        disp = DISPLAY.get((lang, w), disp)
        for e in (e1, e2):
            m = re.findall(r'\*([^*]+)\*', e)
            if len(m) != 1 or norm_key(m[0], lang) != norm_key(w, lang):
                errs.append(f'{r} {w}: marca «{m}» en «{e[:50]}»')
        if lang == 'de':
            cands = [w.capitalize(), w] if noun else [w, w.capitalize()]
            raw = IPA_OVERRIDE['de'].get(w) or next((ipad[c] for c in cands if c in ipad), None)
            ipa = raw.replace('͡', '') if raw else None   # sin ligadura de africadas (t͡s -> ts)
        else:
            raw = ipad.get(w); ipa = norm_en(raw, w) if raw else None
        if not ipa: errs.append(f'{r} {w}: sin IPA')
        item = dict(r=r, w=disp, ipa=ipa, pos=POS['s' if pos in GENDER else pos])
        if pos in GENDER: item['g'] = GENDER[pos]
        item['es'] = [x.strip() for x in es.split(';') if x.strip()]
        item['ex'] = [[e1, t1], [e2, t2]]
        out.append(item)
    missing = sorted(set(words) - set(src))
    return out, errs, missing

if __name__ == '__main__':
    langs = sys.argv[1:] or ['en', 'de']
    result = {}
    for lang in langs:
        out, errs, missing = run(lang)
        json.dump(out, open(os.path.join(HERE, f'{lang}_full.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        print(f'{lang}: {len(out)} escritas, {len(missing)} pendientes, {len(errs)} errores')
        for e in errs: print('  ', e)
        result[lang] = dict(name=META[lang]['name'], code=META[lang]['code'], voice=META[lang]['voice'], words=out)
        ok = not errs and not missing
    if set(langs) == {'en', 'de'} and all(not run(l)[1] and not run(l)[2] for l in langs):
        # formato de index.html:  const DATA = { en:{name,code,voice,words:[{r,w,ipa,pos,es,ex}]}, de:{...} }
        json.dump(result, open(os.path.join(HERE, 'palabras.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        open(os.path.join(HERE, 'palabras.js'), 'w', encoding='utf-8').write(
            '/* Generado por merge.py: 1000 palabras más frecuentes de inglés y alemán. */' + chr(10)
            + 'const DATA = ' + json.dumps(result, ensure_ascii=False, separators=(',', ':')) + ';' + chr(10))
        print('palabras.json y palabras.js escritos')
