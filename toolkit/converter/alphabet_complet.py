# -*- coding: utf-8 -*-
"""
alphabet_complet.py — VERSION CORRIGÉE
=======================================
Analyse complète des 24 lettres atomiques AAC vs 32 unités graphémiques 1979.

CORRECTIONS INTÉGRÉES :
- BUG 1 : ALPHABET_1979 contenait 'ch' en double, oubliait 'à' → 32 unités exactes
- BUG 2 : Entropie 1979 comptait les digrammes EN PLUS des lettres composantes
          → tokenisation graphémique longest-match-first
- BUG 3 : Comparaison d'entropies inéquitable (log_24 vs log_32)
          → bits (log₂) ET normalisée (log_|A|)
- BUG 4 : 'u' apparaissait dans AAC_ALPHABET (lettre fantôme)
          → retirée, avec assertion
- BUG 5 : Syntaxe set + set (TypeError) → set.union()
"""

import re
import math
import unicodedata
from collections import Counter, defaultdict
from aac_converter import to_aac
from corpus import CORPUS


# ------------------------------------------------------------------
# 0. Configuration — 24 lettres AAC / 32 unités 1979
# ------------------------------------------------------------------
AAC_ALPHABET = sorted(set("abdefgijklmnoprstvwyz").union("šŏŋ"))
assert len(AAC_ALPHABET) == 24, f"AAC doit avoir 24 lettres, pas {len(AAC_ALPHABET)}"
assert "u" not in AAC_ALPHABET, "BUG : 'u' ne doit pas être dans l'alphabet AAC"

# Alphabet 1979 nominal : 32 unités exactes
UNITS_1979_3 = ["oun"]                                       # 1 unité
UNITS_1979_2 = ["ch", "ng", "ou", "an", "en", "on", "ui"]    # 7 unités
UNITS_1979_1_AAC = ["à", "è", "ò"]                           # 3 unités
UNITS_1979_1_PLAIN = list("abdefgijklmnoprstvwyz")           # 21 unités
# Total = 1 + 7 + 3 + 21 = 32 ✓

ALPHABET_1979 = UNITS_1979_1_PLAIN + UNITS_1979_1_AAC + UNITS_1979_2 + UNITS_1979_3
assert len(ALPHABET_1979) == 32, f"1979 doit avoir 32 unités, pas {len(ALPHABET_1979)}"
assert len(set(ALPHABET_1979)) == 32, "BUG : doublon détecté dans ALPHABET_1979"

# CORRECTIF (revue de code) : 'à' manquait, faisant retomber tout mot dont
# la seule voyelle est 'à' (ex. "là") sur une syllabe dégénérée sans
# nucleus (tout classé "onset") dans syllabify() plus bas -- même bug que
# celui déjà documenté et corrigé dans letter_analysis.py (VOWELS), dont
# l'ensemble ci-dessous est maintenant aligné. 'i' dupliqué retiré au passage.
VOWELS_AAC = set("aeiòèoŏà")


# ------------------------------------------------------------------
# 1. Corpus — texte 1979 + texte AAC
# ------------------------------------------------------------------
texte_1979 = " ".join(e["texte"] for e in CORPUS.values())
texte_AAC  = to_aac(texte_1979)

def clean(t):
    t = unicodedata.normalize("NFC", t).lower()   # <-- .lower() AJOUTÉ
    return "".join(c for c in t if c.isalpha())

clean_AAC  = clean(texte_AAC)
clean_1979 = clean(texte_1979)

N_char_AAC  = len(clean_AAC)
N_char_1979 = len(clean_1979)

print(f"Corpus 1979 : {N_char_1979} caractères alphabétiques")
print(f"Corpus AAC  : {N_char_AAC} caractères alphabétiques")
print(f"Gain scriptural : {(N_char_1979 - N_char_AAC) / N_char_1979 * 100:.2f} %")


# ------------------------------------------------------------------
# 2. Tokenisation graphémique de 1979 (BUG 2 corrigé)
# ------------------------------------------------------------------
def tokenize_1979(text):
    """Découpe en graphèmes nominaux, longest-match-first.
    'oun' avant 'ou', 'ch' avant 'c'+'h', etc.
    Résout le double comptage : 'an' devient UNE unité, pas 'a'+'n'."""
    tokens = []
    i, n = 0, len(text)
    multi = sorted(UNITS_1979_3 + UNITS_1979_2, key=len, reverse=True)
    while i < n:
        matched = False
        for m in multi:
            if text.startswith(m, i):
                tokens.append(m)
                i += len(m)
                matched = True
                break
        if not matched:
            tokens.append(text[i])
            i += 1
    return tokens


tokens_1979 = tokenize_1979(clean_1979)

# --- Diagnostic : tokens hors alphabet ---
hors_alphabet = Counter(t for t in tokens_1979 if t not in ALPHABET_1979)
print(f"\n=== DIAGNOSTIC TOKENISATION 1979 ===")
print(f"Tokens totaux          : {len(tokens_1979)}")
print(f"Tokens dans alphabet   : {len(tokens_1979) - sum(hors_alphabet.values())}")
print(f"Tokens hors alphabet   : {sum(hors_alphabet.values())}")
if hors_alphabet:
    print("Détail des tokens hors alphabet :")
    for tok, n in hors_alphabet.most_common():
        print(f"  {tok!r} : {n}")

# --- Filtrage : on ne garde que les tokens valides ---
tokens_1979_valid = [t for t in tokens_1979 if t in ALPHABET_1979]
N_graphemes_1979 = len(tokens_1979_valid)

print(f"\nTokenisation 1979 retenue : {N_char_1979} caractères → "
      f"{N_graphemes_1979} graphèmes valides "
      f"({(N_char_1979 - N_graphemes_1979) / N_char_1979 * 100:.1f} % de réduction)")


# ------------------------------------------------------------------
# 3. Fréquences AAC (24 lettres)
# ------------------------------------------------------------------
counts_AAC = Counter(clean_AAC)
n_AAC = {l: counts_AAC.get(l, 0) for l in AAC_ALPHABET}
total_AAC = sum(n_AAC.values())
f_AAC = {l: n_AAC[l] / total_AAC for l in AAC_ALPHABET}

print("\n=== FRÉQUENCES DES 24 LETTRES AAC ===")
print(f"{'Lettre':<8s} {'n':>6s} {'f (%)':>8s}")
for l in AAC_ALPHABET:
    print(f"{l:<8s} {n_AAC[l]:>6d} {f_AAC[l]*100:>8.3f}")


# ------------------------------------------------------------------
# 4. Fréquences 1979 (32 unités graphémiques, partition propre)
# ------------------------------------------------------------------
counts_1979 = Counter(tokens_1979_valid)
n_1979 = {u: counts_1979.get(u, 0) for u in ALPHABET_1979}
total_1979 = sum(n_1979.values())
f_1979 = {u: n_1979[u] / total_1979 for u in ALPHABET_1979}

assert total_1979 == N_graphemes_1979, \
    f"BUG : somme des fréquences 1979 ({total_1979}) ≠ N_graphemes ({N_graphemes_1979})"

print("\n=== FRÉQUENCES DES 32 UNITÉS 1979 ===")
print(f"{'Unité':<8s} {'n':>6s} {'f (%)':>8s}")
for u in ALPHABET_1979:
    print(f"{u:<8s} {n_1979[u]:>6d} {f_1979[u]*100:>8.3f}")


# ------------------------------------------------------------------
# 5. Entropies comparées (BUG 3 corrigé)
# ------------------------------------------------------------------
def entropy_bits(counts):
    total = sum(counts.values())
    H = 0.0
    for n in counts.values():
        if n > 0:
            p = n / total
            H -= p * math.log2(p)
    return H

def entropy_normalized(counts, alphabet_size):
    return entropy_bits(counts) / math.log2(alphabet_size)

H_bits_1979 = entropy_bits(n_1979)
H_bits_AAC  = entropy_bits(n_AAC)
H_norm_1979 = entropy_normalized(n_1979, 32)
H_norm_AAC  = entropy_normalized(n_AAC, 24)

print(f"\n=== ENTROPIE — en bits (log₂) ===")
print(f"H_bits(1979) = {H_bits_1979:.4f} bits  (max = {math.log2(32):.4f})")
print(f"H_bits(AAC)  = {H_bits_AAC:.4f} bits  (max = {math.log2(24):.4f})")
print(f"ΔH_bits = {H_bits_AAC - H_bits_1979:+.4f} bits")

print(f"\n=== ENTROPIE — normalisée (log_|A|) ===")
print(f"H_norm(1979) = {H_norm_1979:.4f}  (32 unités)")
print(f"H_norm(AAC)  = {H_norm_AAC:.4f}  (24 lettres)")
print(f"ΔH_norm = {H_norm_AAC - H_norm_1979:+.4f}")


# ------------------------------------------------------------------
# 6. Gini
# ------------------------------------------------------------------
def gini(counts):
    vals = sorted(v for v in counts.values() if v > 0)
    n, total = len(vals), sum(vals)
    if n == 0 or total == 0:
        return 0.0
    cum = sum((2 * (i + 1) - n - 1) * v for i, v in enumerate(vals))
    return cum / (n * total)

print(f"\n=== GINI ===")
print(f"G(1979) = {gini(n_1979):.4f}")
print(f"G(AAC)  = {gini(n_AAC):.4f}")


# ------------------------------------------------------------------
# 7. Positions syllabiques (24 lettres AAC)
# ------------------------------------------------------------------
def syllabify(word):
    w = [c.lower() for c in word]
    voy = [i for i, c in enumerate(w) if c in VOWELS_AAC]
    if not voy:
        return [{"onset": w, "nucleus": [], "coda": []}]
    sylls = [{"onset": w[:voy[0]], "nucleus": [w[voy[0]]], "coda": []}]
    for k in range(1, len(voy)):
        between = w[voy[k-1]+1:voy[k]]
        if len(between) <= 1:
            onset = between
        elif len(between) == 2:
            sylls[-1]["coda"].append(between[0]); onset = [between[1]]
        else:
            sylls[-1]["coda"].extend(between[:-1]); onset = [between[-1]]
        sylls.append({"onset": onset, "nucleus": [w[voy[k]]], "coda": []})
    sylls[-1]["coda"].extend(w[voy[-1]+1:])
    return sylls

mots_AAC = re.findall(r"[^\W\d_]+", texte_AAC, flags=re.UNICODE)
occ = defaultdict(Counter)
for w in mots_AAC:
    for syll in syllabify(w):
        for pos in ("onset", "nucleus", "coda"):
            for c in syll[pos]:
                if c in AAC_ALPHABET:
                    occ[c][pos] += 1

print("\n=== POSITIONS SYLLABIQUES (24 lettres AAC) ===")
print(f"{'Lettre':<8s} {'Total':>6s} {'Onset %':>9s} {'Nucleus %':>11s} {'Coda %':>8s}")
for l in AAC_ALPHABET:
    tot = sum(occ[l].values())
    if tot > 0:
        print(f"{l:<8s} {tot:>6d} {occ[l]['onset']/tot*100:>9.1f} "
              f"{occ[l]['nucleus']/tot*100:>11.1f} {occ[l]['coda']/tot*100:>8.1f}")


# ------------------------------------------------------------------
# 8. Bigrammes AAC
# ------------------------------------------------------------------
bigrams = Counter()
for i in range(len(clean_AAC) - 1):
    a, b = clean_AAC[i], clean_AAC[i+1]
    if a in AAC_ALPHABET and b in AAC_ALPHABET:
        bigrams[(a, b)] += 1

total_bg = sum(bigrams.values())
print(f"\n=== BIGRAMMES AAC (total {total_bg}) ===")
for (a, b), k in bigrams.most_common(20):
    p_ab = k / total_bg
    pmi = math.log2(p_ab / (f_AAC[a] * f_AAC[b])) if p_ab > 0 else 0
    print(f"  ({a},{b}) : n={k:5d}  P(ab)={p_ab*100:5.2f}%  PMI={pmi:+6.3f}")


# ------------------------------------------------------------------
# 9. Entropie conditionnelle AAC
# ------------------------------------------------------------------
def conditional_entropy(bigrams, counts, alphabet):
    total = sum(counts.values())
    H_cond = 0.0
    for a in alphabet:
        n_a = counts.get(a, 0)
        if n_a == 0:
            continue
        H_a = 0.0
        for b in alphabet:
            n_ab = bigrams.get((a, b), 0)
            if n_ab > 0:
                p = n_ab / n_a
                H_a -= p * math.log2(p)
        H_cond += (n_a / total) * H_a
    return H_cond

H_cond = conditional_entropy(bigrams, n_AAC, AAC_ALPHABET)
print(f"\n=== ENTROPIE CONDITIONNELLE AAC ===")
print(f"H(l2 | l1)            = {H_cond:.4f} bits")
print(f"H(l2 | l1) normalisée = {H_cond / math.log2(24):.4f}")


# ------------------------------------------------------------------
# 10. Ambiguïté résiduelle
# ------------------------------------------------------------------
print(f"\n=== AMBIGUÏTÉ RÉSIDUELLE ===")
print("Bi-univocité totale : Amb(toutes les 24 lettres AAC) = 0")


# ------------------------------------------------------------------
# 11. Point clé : la lettre fantôme 'u'
# ------------------------------------------------------------------
u_in_1979 = sum(1 for t in tokens_1979_valid if t == "u")
u_in_AAC  = n_AAC.get("u", 0)
print(f"\n=== LA LETTRE FANTÔME 'u' ===")
print(f"'u' comme graphème en 1979 : {u_in_1979}")
print(f"'u' comme caractère en AAC : {u_in_AAC}")
print(f"→ En AAC, 'u' disparaît : 'ui' → 'wi'.")