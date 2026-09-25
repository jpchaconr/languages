"""Transcripción IPA del ruso estándar a partir de la forma con el acento marcado (молоко́, ещё, что́-то).

Sigue las convenciones del módulo de pronunciación de Wiktionary (ru-pron), simplificadas: reducción vocálica
(акание/иканье), consonantes blandas ante е, ё, и, ю, я, ь; ж, ш, ц siempre duras y ч, щ siempre blandas;
ensordecimiento final y asimilación de sonoridad; с/з blandas ante т, д, н blandas; grupos simplificados
(здра́вствуйте, се́рдце, че́стно); -ого/-его con [v]; -тся/-ться como [tsə] ([tsːə] tras la tónica). Sin ligaduras en africadas (ts, tɕ).
merge.py compara el resultado con WikiPron (Wiktionary) y avisa de las diferencias.
"""
import re

ACUTE = '\u0301'
VOWELS = 'аеёиоуыэюя'
IOTATED = 'еёюя'                 # /j/ + vocal a principio de palabra y tras vocal, ь o ъ
SOFTENING = 'еёиюяь'             # ablandan la consonante anterior
CONS = dict(б='b', в='v', г='ɡ', д='d', ж='ʐ', з='z', к='k', л='ɫ', м='m', н='n', п='p', р='r', с='s', т='t',
            ф='f', х='x', ц='ts', ч='tɕ', ш='ʂ', щ='ɕː', й='j')
PAIRED = set('бвгдзклмнпрстфх')  # tienen versión blanda; ж ш ц son siempre duras, ч щ й siempre blandas
DEVOICE = dict(b='p', v='f', ɡ='k', d='t', z='s', ʐ='ʂ', ɣ='x', dz='ts', dʑ='tɕ', ʑː='ɕː')
VOICE = {v: k for k, v in DEVOICE.items()}
LIQUID, STOP, SIBILANT = set('rɫlv'), set('pbtdkɡ'), {'s', 'z', 'ʂ', 'ʐ'}
OGO_EXCEPT = {'много', 'немного', 'строго', 'дорого', 'убого', 'ого', 'итого'}

def base(p): return p.rstrip('ʲ')
def soft(p): return p.rstrip('ː').endswith('ʲ') or p.rstrip('ː') in ('tɕ', 'ɕ', 'j', 'dʑ', 'ʑ')
def obstruent(p): return base(p) in DEVOICE or base(p) in VOICE

def respell(w):
    """Grafías que no se leen letra a letra (el acento, U+0301, se conserva en su vocal)."""
    plain = w.replace(ACUTE, '')
    w = re.sub(r'(^|-|ни|не)чт(?=о)', r'\1шт', w)                       # что [ʂto], что́-то, ничто́
    if plain.split('-')[0] not in OGO_EXCEPT:
        w = re.sub(r'(?<=[ое])(\u0301?)г(?=о\u0301?(?:$|-))', r'\1в', w)   # его́, э́того, кого́-то: [v]
    w = re.sub(r'^сего(\u0301?)дн', r'сево\1дн', w)                  # сего́дня
    if plain == 'конечно': w = w.replace('ч', 'ш')
    if plain == 'бог': w = 'бох'
    for a, b in (('гк', 'хк'), ('гч', 'хч'), ('вств', 'ств'), ('стн', 'сн'), ('здн', 'зн'), ('рдц', 'рц'),
                 ('лнц', 'нц'), ('стл', 'сл'), ('чш', 'тш'), ('сч', 'щ'), ('зч', 'щ'), ('жч', 'щ')):
        w = w.replace(a, b)
    w = re.sub(r'(?<=[\u0301ё])ть?ся$', 'тца', w)                   # -тся, -ться tras la tónica: [tsːə]
    w = re.sub(r'ть?ся$', 'ца', w)                                    # -тся, -ться: [tsə]
    return re.sub(r'лся$', 'лса', w)                                  # верну́лся: [ɫsə]

def word_ipa(w):
    letters, stress = [], []            # letras sin guion; stress: índice de la vocal acentuada
    for ch in respell(w.lower()):
        if ch == ACUTE: stress.append(len(letters) - 1)
        elif ch == '-': letters.append('-')
        else: letters.append(ch)
    vowels = [i for i, c in enumerate(letters) if c in VOWELS]
    if not stress: stress = [i for i in vowels if letters[i] == 'ё'] or (vowels if len(vowels) == 1 else [])
    if len(stress) != 1 and len(vowels) > 1: raise ValueError(f'acento no marcado en «{w}»')
    st = stress[0] if stress else None
    # 1) segmentos: consonantes con su dureza; vocales con su letra (la calidad se decide al final)
    seg, gem = [], False   # seg: [tipo, fonema (o letra, en las vocales), índice de la letra]
    for i, c in enumerate(letters):
        if c in '-ьъ': continue
        nxt = letters[i + 1] if i + 1 < len(letters) else ''
        if c in CONS:
            if nxt == c:      # consonante doble: una sola (ру́сский), salvo -нн- entre vocales (соверше́нно [nː])
                gem = c == 'н' and 0 < i < len(letters) - 2 and letters[i - 1] in VOWELS + ACUTE and letters[i + 2] in VOWELS
                continue
            p = CONS[c]
            if c in PAIRED and nxt and nxt in SOFTENING: p = 'lʲ' if c == 'л' else p + 'ʲ'
            seg.append(['C', p + ('ː' if gem else ''), i]); gem = False; continue
        before = letters[i - 1] if i and letters[i - 1] != '-' else (letters[i - 2] if i > 1 else None)
        if (c in IOTATED and (before is None or before in VOWELS or before in 'ьъ')) or (c == 'и' and before == 'ь'):
            seg.append(['C', 'j', i])
        seg.append(['V', c, i])
    # 2) asimilaciones, de derecha a izquierda
    cons_word = not any(s[0] == 'V' for s in seg)
    if seg and seg[-1][0] == 'C' and obstruent(seg[-1][1]) and not cons_word:   # ensordecimiento final
        seg[-1][1] = DEVOICE.get(base(seg[-1][1]), base(seg[-1][1])) + ('ʲ' if seg[-1][1].endswith('ʲ') else '')
    for k in range(len(seg) - 2, -1, -1):
        a, b = seg[k], seg[k + 1]
        if a[0] != 'C' or b[0] != 'C': continue
        pa, pb, mark = base(a[1]), base(b[1]), 'ʲ' if a[1].endswith('ʲ') else ''
        if pa in ('s', 'z') and base(pb) in ('ʂ', 'ʐ'): a[1] = pa = VOICE[pb] if pb in VOICE and pa == 'z' else pb   # сж, зж: [ʐː]
        if obstruent(a[1]) and obstruent(b[1]):
            if pb in VOICE: a[1] = DEVOICE.get(pa, pa) + mark                  # ante sorda: sorda
            elif pb != 'v': a[1] = VOICE.get(pa, pa) + mark                   # ante sonora (salvo в): sonora
        if not mark and ((base(a[1]) in ('s', 'z') and b[1] in ('tʲ', 'dʲ', 'nʲ', 'sʲ', 'zʲ'))
                         or (base(a[1]) in ('t', 'd') and b[1] in ('tʲ', 'dʲ', 'nʲ'))
                         or (a[1] == 'n' and b[1] in ('tʲ', 'dʲ', 'sʲ', 'zʲ', 'tɕ', 'ɕː'))): a[1] += 'ʲ'   # есть, идти́, же́нщина
    for k in range(len(seg) - 2, -1, -1):     # dos consonantes iguales tras asimilar: una larga (бу́дто [ˈbutːə])
        if seg[k][0] != 'C' or seg[k + 1][0] != 'C': continue
        a, b = seg[k][1], seg[k + 1][1]
        if a == b and not a.endswith('ː'): seg[k][1] += 'ː'; del seg[k + 1]
        elif base(a) == 't' and b in ('ts', 'tɕ'): seg[k][1] = b + 'ː'; del seg[k + 1]     # отца́ [ɐˈtsːa]
    # 3) calidad de las vocales
    vpos = [k for k, s in enumerate(seg) if s[0] == 'V']
    out = []
    for n, k in enumerate(vpos):
        c, i = seg[k][1], seg[k][2]
        left = seg[k - 1][1] if k and seg[k - 1][0] == 'C' else None
        right = seg[k + 1][1] if k + 1 < len(seg) and seg[k + 1][0] == 'C' else None
        after_soft = left is not None and soft(left)
        hard_sib = left is not None and left.rstrip('ː') in ('ʐ', 'ʂ', 'ts')
        final = k == len(seg) - 1
        if i == st or st is None:
            if c in 'ая': q = 'æ' if after_soft and right and soft(right) else 'a'
            elif c in 'оё': q = 'ɵ' if after_soft else 'o'
            elif c in 'ую': q = 'ʉ' if after_soft and right and soft(right) else 'u'
            elif c == 'ы': q = 'ɨ'
            elif c == 'и': q = 'ɨ' if hard_sib else 'i'
            elif c == 'э': q = 'ɛ'
            else: q = 'ɛ' if hard_sib else 'e'
        else:
            pre = st is not None and n + 1 < len(vpos) and seg[vpos[n + 1]][2] == st
            if c in 'ао' and not after_soft:          # [ɐ] al inicio, antes de la tónica y en «оо» (вообще́, сообще́ние)
                q = 'ɐ' if (k == 0 or pre or (c == 'о' and k + 1 < len(seg) and seg[k + 1][1] == 'о')) else 'ə'
            elif c in 'аяо': q = 'ə' if final or ''.join(letters[i:]) in ('ям', 'ях', 'ями') else 'ɪ'   # лю́дям [ˈlʲʉdʲəm]
            elif c == 'е':
                if hard_sib: q = 'ə' if final and left.startswith('ts') else 'ɨ'
                elif final: q = 'ə' if n and seg[vpos[n - 1]][1] == 'о' and seg[k - 1][1] == 'j' else 'e'
                else: q = 'ɪ'
            elif c in 'иэ': q = 'ɨ' if hard_sib or (c == 'э' and k) else 'ɪ'
            elif c == 'ы': q = 'ɨ'
            else: q = 'ʉ' if after_soft and right and soft(right) else 'ʊ'
        out.append((k, q))
    for k, q in out: seg[k][1] = q
    # 4) acento: antes del ataque de la sílaba tónica (se deja en la coda lo que no puede iniciar sílaba)
    ph = [s[1] for s in seg]
    if st is not None and len(vpos) > 1:
        k = next(k for k in vpos if seg[k][2] == st)
        j = k
        while j and seg[j - 1][0] == 'C': j -= 1
        cl = ph[j:k]
        if cl and cl[-1] != 'j':
            o = 1
            if len(cl) > 1 and base(cl[-1]) in LIQUID and obstruent(cl[-2]): o = 2
            if len(cl) > o and base(cl[-o]) in STOP and base(cl[-o - 1]) in SIBILANT: o += 1
            j = k - o
        elif cl: j = k - 1
        ph.insert(j if any(s[0] == 'V' for s in seg[:j]) else 0, 'ˈ')
    return ''.join(ph)

def transcribe(w):
    """'молоко́' -> '/məɫɐˈko/'. Varias palabras separadas por espacios se transcriben por separado."""
    return '/' + ' '.join(word_ipa(x) for x in w.split()) + '/'

if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    for x in sys.argv[1:]: print(x, transcribe(x))
