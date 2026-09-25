"""Une frecuencias + IPA + categoría/traducción/ejemplos (src/*.txt) y valida.
IPA: inglés y alemán de ipa-dict; ruso generada por ru_ipa.py a partir de la palabra acentuada y contrastada con WikiPron.
Uso: python merge.py [en|de|ru]   -> escribe {lang}_full.json e informa de errores. Si no hay errores, reúne todos
los {lang}_full.json en palabras.json y palabras.js (el formato de index.html)."""
import csv, glob, json, os, re, sys
import ru_ipa
sys.stdout.reconfigure(encoding='utf-8')
HERE = os.path.dirname(os.path.abspath(__file__))
POS = dict(art='artículo', pron='pronombre', v='verbo', s='sustantivo', adj='adjetivo', adv='adverbio',
           prep='preposición', conj='conjunción', det='determinante', int='interjección', num='numeral', part='partícula')
GENDER = {'sm': 'm', 'sf': 'f', 'sn': 'n', 'sp': 'pl'}
META = {'en': dict(name='Inglés', code='EN', voice='en-US', ipafile='en_US.txt'),
        'de': dict(name='Alemán', code='DE', voice='de-DE', ipafile='de.txt'),
        'ru': dict(name='Ruso', code='RU', voice='ru-RU', ipafile='rus_cyrl_narrow.tsv')}
IPA_OVERRIDE = {'de': {'darum': '/daˈʁʊm/', 'wär': '/vɛːɐ̯/', 'hause': '/tsuː ˈhaʊ̯zə/', 'band': '/bɛnt/'},
                'ru': {'сих': '/də sʲɪx ˈpor/', 'обо': '/ɐbə/', 'кое-что': '/ˌkojɪˈʂto/', 'бизнес': '/ˈbʲiznɨs/',
                       'двое': '/ˈdvoje/', 'улице': '/ˈulʲɪtsɨ/'}}
# Ruso: difieren de WikiPron pero se revisaron y se deja la transcripción generada (forma de cita, errores o
# variantes de Wiktionary: «ты» [t̪ˠɨ], «ни» átono, «об» sin ensordecer, «семья» sin [mʲ]…)
IPA_KEEP = {'ru': {'ты', 'ни', 'об', 'лучше', 'лучший', 'какие', 'отсюда', 'прежде', 'семья', 'семьи', 'каждого'}}
DISPLAY = {('de', 'hause'): 'zu Hause', ('ru', 'сих'): 'до сих пор'}   # formas que solo existen dentro de una locución

def load_ipa(fn):
    d = {}
    for l in open(os.path.join(HERE, fn), encoding='utf-8'):
        p = l.rstrip('\n').split('\t')
        if len(p) >= 2: d.setdefault(p[0], p[1].split(', ')[0])
    return d

def load_wikipron(fn, words):
    """WikiPron (Wiktionary): todas las transcripciones de cada palabra, sin espacios, ligaduras ni palatalización opcional."""
    d = {}
    for l in open(os.path.join(HERE, fn), encoding='utf-8'):
        w, p = l.rstrip('\n').split('\t')
        if w in words: d.setdefault(w, set()).add(p.replace(' ', '').replace('͡', '').replace('⁽ʲ⁾', ''))
    return d

def norm_en(ipa, word=''):
    """ipa-dict (CMUdict) -> notación de diccionario: ɫ->l, ɝ->ɜr, ɚ->ər, hw->w, ʌ tónica, sin acento en monosílabos."""
    ipa = ipa.replace('ɹ', 'r').replace('ɫ', 'l').replace('ɝ', 'ɜr').replace('ɚ', 'ər').strip('/')
    ipa = re.sub(r'^(ˈ?)hw', r'\1w', ipa)
    if word != 'the':   # ə con acento primario es en realidad ʌ (CMUdict AH1)
        ipa = re.sub(r'(ˈ[^aeiouæɑɔəɛɪʊʌɜ]*)ə', r'\1ʌ', ipa, count=1)
    if len(re.findall(r'[aeiouæɑɔəɛɪʊʌɜ]+', ipa)) <= 1: ipa = ipa.replace('ˈ', '')   # sin acento en monosílabos
    return '/' + ipa + '/'

def split_es(es):
    """Traducciones separadas por «;». Un «;» dentro de paréntesis no separa: «su (de ella; declinado)»."""
    out, cur, depth = [], '', 0
    for ch in es:
        depth += (ch == '(') - (ch == ')')
        if ch == ';' and depth == 0: out.append(cur); cur = ''
        else: cur += ch
    return [x.strip() for x in out + [cur] if x.strip()]

def norm_key(s, lang):
    s = s.lower()
    if lang == 'de': return s.replace('ß', 'ss')
    if lang == 'ru': return s.replace(ru_ipa.ACUTE, '')   # la ё se mantiene: все y всё son palabras distintas
    return s

def run(lang):
    rows = list(csv.DictReader(open(os.path.join(HERE, f'{lang}_top1000.csv'), encoding='utf-8-sig')))
    words = {int(r['rank']): r['word'] for r in rows}
    byword = {norm_key(w, lang): r for r, w in words.items()}
    if lang == 'ru': ipad = load_wikipron(META[lang]['ipafile'], set(words.values()))
    else: ipad = load_ipa(META[lang]['ipafile'])
    src, errs, warns = {}, [], []
    for fn in sorted(glob.glob(os.path.join(HERE, 'src', f'{lang}_*.txt'))):
        for n, line in enumerate(open(fn, encoding='utf-8'), 1):
            line = line.strip()
            if not line: continue
            p = line.split('|'); tag = f'{os.path.basename(fn)}:{n}'
            if len(p) != 7: errs.append(f'{tag} campos={len(p)}: {line[:60]}'); continue
            r = int(p[0]) if p[0].isdigit() else byword.get(norm_key(p[0], lang))
            if r is None: errs.append(f'{tag} palabra «{p[0]}» no está en la lista'); continue
            if r in src: errs.append(f'{tag} rank {r} repetido'); continue
            src[r] = p
    out = []
    for r in sorted(src):
        head, pos, es, e1, t1, e2, t2 = src[r]; w = words.get(r)
        if w is None: errs.append(f'rank {r} no existe'); continue
        if pos not in POS and pos not in GENDER: errs.append(f'{r} {w}: categoría «{pos}»'); continue
        noun = pos in GENDER or pos == 's'
        disp = w.capitalize() if (lang == 'de' and noun) else ('I' if (lang == 'en' and w == 'i') else w)
        if lang == 'ru': disp = head.lower()   # ruso: con el acento marcado (молоко́)
        disp = DISPLAY.get((lang, w), disp)
        for e in (e1, e2):
            m = re.findall(r'\*([^*]+)\*', e)
            if len(m) != 1 or norm_key(m[0], lang) != norm_key(w, lang):
                errs.append(f'{r} {w}: marca «{m}» en «{e[:50]}»')
        if lang == 'de':
            cands = [w.capitalize(), w] if noun else [w, w.capitalize()]
            raw = IPA_OVERRIDE['de'].get(w) or next((ipad[c] for c in cands if c in ipad), None)
            ipa = raw.replace('͡', '') if raw else None   # sin ligadura de africadas (t͡s -> ts)
        elif lang == 'ru':
            try: ipa = IPA_OVERRIDE['ru'].get(w) or ru_ipa.transcribe(head.lower())
            except ValueError as ex: ipa = None; errs.append(f'{r} {w}: {ex}')
            if (ipa and w in ipad and w not in IPA_OVERRIDE['ru'] and w not in IPA_KEEP['ru']
                    and ipa.strip('/').replace('ˈ', '') not in ipad[w]):
                warns.append(f'aviso {r} {head}: {ipa} ≠ Wiktionary {" | ".join(sorted(ipad[w]))}')
        else:
            raw = ipad.get(w); ipa = norm_en(raw, w) if raw else None
        if not ipa: errs.append(f'{r} {w}: sin IPA')
        item = dict(r=r, w=disp, ipa=ipa, pos=POS['s' if pos in GENDER else pos])
        if pos in GENDER: item['g'] = GENDER[pos]
        item['es'] = split_es(es)
        item['ex'] = [[e1, t1], [e2, t2]]
        out.append(item)
    missing = sorted(set(words) - set(src))
    return out, errs, missing, warns

if __name__ == '__main__':
    langs = sys.argv[1:] or list(META)
    ok = True
    for lang in langs:
        out, errs, missing, warns = run(lang)
        json.dump(out, open(os.path.join(HERE, f'{lang}_full.json'), 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
        print(f'{lang}: {len(out)} escritas, {len(missing)} pendientes, {len(errs)} errores, {len(warns)} avisos')
        for e in errs + warns: print('  ', e)
        ok = ok and not errs and not missing
    full = {l: os.path.join(HERE, f'{l}_full.json') for l in META}
    if ok and all(os.path.exists(f) for f in full.values()):
        # formato de index.html:  const DATA = { en:{name,code,voice,words:[{r,w,ipa,pos,es,ex}]}, de:{...}, ru:{...} }
        result = {l: dict(name=m['name'], code=m['code'], voice=m['voice'], words=json.load(open(full[l], encoding='utf-8')))
                  for l, m in META.items()}
        json.dump(result, open(os.path.join(HERE, 'palabras.json'), 'w', encoding='utf-8'), ensure_ascii=False, separators=(',', ':'))
        open(os.path.join(HERE, 'palabras.js'), 'w', encoding='utf-8').write(
            '/* Generado por merge.py: 1000 palabras más frecuentes de inglés, alemán y ruso. */' + chr(10)
            + 'const DATA = ' + json.dumps(result, ensure_ascii=False, separators=(',', ':')) + ';' + chr(10))
        print('palabras.json y palabras.js escritos')
