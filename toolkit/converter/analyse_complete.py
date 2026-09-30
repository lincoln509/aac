# -*- coding: utf-8 -*-
"""
analyse_complete.py
===================
Développe toutes les formules statistiques sur les 8 textes de corpus.py.
"""
import re
import math
import unicodedata
from collections import defaultdict, Counter
from scipy import stats
from corpus import CORPUS
from aac_converter import to_aac

ATOMIC = {"š", "ŏ", "ŋ"}
VOWELS = set("aeèàiouòŏ")

# ---------- utilitaires ----------
def norm(c):
    return unicodedata.normalize("NFC", c).lower()

def strip_accents(s):
    return "".join(c for c in unicodedata.normalize("NFD", s)
                   if unicodedata.category(c) != "Mn")

def syllabify(word):
    w = [norm(c) for c in word]
    voy = [i for i, c in enumerate(w) if c in VOWELS]
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

# ---------- 1. statistiques de base ----------
print("=" * 78)
print("1. GAIN SCRIPTURAL PAR TEXTE")
print("=" * 78)
gains, lengths = [], []
rows = []
for key, entry in CORPUS.items():
    before = entry["texte"]
    after = to_aac(before)
    g = (len(before) - len(after)) / len(before) * 100
    gains.append(g); lengths.append(len(before))
    rows.append((key, len(before), len(after), g))
    print(f"{key:<24s} {len(before):>5d} -> {len(after):>5d}  gain={g:6.2f} %")

n = len(gains)
mean_g = sum(gains) / n
sd_g = math.sqrt(sum((g - mean_g)**2 for g in gains) / (n - 1))
se_g = sd_g / math.sqrt(n)
t_crit = stats.t.ppf(0.975, n - 1)
ic_lo, ic_hi = mean_g - t_crit * se_g, mean_g + t_crit * se_g

pooled = (sum(r[1] for r in rows) - sum(r[2] for r in rows)) / sum(r[1] for r in rows) * 100

print(f"\nn = {n}")
print(f"moyenne non pondérée  = {mean_g:.2f} %")
print(f"écart-type            = {sd_g:.2f} %")
print(f"SE                    = {se_g:.3f} %")
print(f"IC95 % (Student)      = [{ic_lo:.2f} % ; {ic_hi:.2f} %]")
print(f"gain poolé (pondéré)  = {pooled:.2f} %")

# bootstrap IC
import random
random.seed(42)
B = 10000
boot = []
for _ in range(B):
    sample = [random.choice(gains) for _ in range(n)]
    boot.append(sum(sample) / n)
boot.sort()
print(f"IC95 % (bootstrap)    = [{boot[int(0.025*B)]:.2f} % ; {boot[int(0.975*B)]:.2f} %]")

# test t apparié sur les différences
diffs = [r[1] - r[2] for r in rows]
t_stat, p_val = stats.ttest_rel([r[1] for r in rows], [r[2] for r in rows])
print(f"test t apparié        : t = {t_stat:.3f}, p = {p_val:.2e}")

# corrélation longueur / gain
r, p_r = stats.pearsonr(lengths, gains)
print(f"corrélation (long, gain) : r = {r:.3f}, p = {p_r:.3f}")

# ---------- 2. fréquences atomiques ----------
print("\n" + "=" * 78)
print("2. FRÉQUENCES DES LETTRES ATOMIQUES")
print("=" * 78)
full_aac = "".join(to_aac(e["texte"]) for e in CORPUS.values())
N = len(full_aac)
counts = Counter(c for c in full_aac if norm(c) in ATOMIC)
n_l = {l: counts[l] for l in ATOMIC}
f_l = {l: n_l[l] / N for l in ATOMIC}
total_atom = sum(n_l.values())
p_l = {l: n_l[l] / total_atom for l in ATOMIC}
D = total_atom / N

print(f"N = {N}, total atomiques = {total_atom}, densité D = {D*100:.3f} %")
print(f"{'lettre':<8s} {'n':>5s} {'f (%)':>8s} {'p (%)':>8s} {'IC95 % Clopper-Pearson':>28s}")
for l in ATOMIC:
    lo = stats.beta.ppf(0.025, n_l[l], N - n_l[l] + 1)
    hi = stats.beta.ppf(0.975, n_l[l] + 1, N - n_l[l])
    print(f"{l:<8s} {n_l[l]:>5d} {f_l[l]*100:>8.3f} {p_l[l]*100:>8.2f}   [{lo*100:.3f} % ; {hi*100:.3f} %]")

# chi² uniformité
bar_n = total_atom / 3
chi2 = sum((n_l[l] - bar_n)**2 / bar_n for l in ATOMIC)
p_chi2 = 1 - stats.chi2.cdf(chi2, df=2)
print(f"\nchi² uniformité = {chi2:.3f}, ddl = 2, p = {p_chi2:.2e}")

# entropie
H = -sum(p_l[l] * math.log(p_l[l], 3) for l in ATOMIC)
print(f"entropie H(A) = {H:.4f} (max = 1)")

# ---------- 3. analyse au niveau du mot ----------
print("\n" + "=" * 78)
print("3. ANALYSE AU NIVEAU DU MOT")
print("=" * 78)
all_words = []
for e in CORPUS.values():
    all_words.extend(re.findall(r"[^\W\d_]+", to_aac(e["texte"]), flags=re.UNICODE))
M = len(all_words)
a_w = [sum(1 for c in w if norm(c) in ATOMIC) for w in all_words]
W_plus = [w for w, a in zip(all_words, a_w) if a >= 1]
C = len(W_plus) / M
mu_all = sum(a_w) / M
mu_pos = sum(a for a in a_w if a >= 1) / len(W_plus)

print(f"M = {M} mots, |W+| = {len(W_plus)}, C = {C*100:.2f} %")
print(f"mu_all = {mu_all:.4f}, mu_pos = {mu_pos:.4f}")
print(f"identité mu_all = C * mu_pos : {mu_all:.4f} = {C * mu_pos:.4f}  ->  {abs(mu_all - C*mu_pos) < 1e-9}")

for l in ATOMIC:
    C_l = sum(1 for w in all_words if norm(l) in [norm(c) for c in w]) / M
    print(f"  C_{l} = {C_l*100:.2f} %")

# TTR atomique
ttr_A = len(set(W_plus)) / len(W_plus) if W_plus else 0
print(f"TTR atomique = {ttr_A:.3f}")

# ---------- 4. positions syllabiques ----------
print("\n" + "=" * 78)
print("4. POSITIONS SYLLABIQUES (onset / nucleus / coda)")
print("=" * 78)
occ = defaultdict(Counter)
for w in all_words:
    for syll in syllabify(w):
        for pos in ("onset", "nucleus", "coda"):
            for c in syll[pos]:
                if c in ATOMIC:
                    occ[c][pos] += 1

for l in ATOMIC:
    tot = sum(occ[l].values())
    if tot:
        print(f"{l} : total {tot} — "
              f"onset {occ[l]['onset']/tot*100:.1f} % / "
              f"nucleus {occ[l]['nucleus']/tot*100:.1f} % / "
              f"coda {occ[l]['coda']/tot*100:.1f} %")

# ---------- 5. bigrammes et PMI ----------
print("\n" + "=" * 78)
print("5. BIGRAMMES ATOMIQUES ET PMI")
print("=" * 78)
bigrams = Counter()
unigrams = Counter()
for i in range(len(full_aac) - 1):
    a, b = norm(full_aac[i]), norm(full_aac[i+1])
    if a in ATOMIC and b in ATOMIC:
        bigrams[(a, b)] += 1
for c in full_aac:
    if norm(c) in ATOMIC:
        unigrams[norm(c)] += 1

total_bg = sum(bigrams.values())
print(f"total bigrammes atomiques = {total_bg}")
for (a, b), k in bigrams.most_common():
    p_ab = k / max(total_bg, 1)
    p_a = unigrams[a] / N
    p_b = unigrams[b] / N
    pmi = math.log2(p_ab / (p_a * p_b)) if p_ab > 0 else float("nan")
    print(f"  ({a},{b}) : n={k}, PMI={pmi:.3f}")

# ---------- 6. position relative dans le mot ----------
print("\n" + "=" * 78)
print("6. POSITION RELATIVE DANS LE MOT")
print("=" * 78)
rel = defaultdict(list)
for w in all_words:
    nw = [norm(c) for c in w]
    L = len(nw)
    for i, c in enumerate(nw):
        if c in ATOMIC:
            rel[c].append((i + 1) / L)

for l in ATOMIC:
    if rel[l]:
        vals = rel[l]
        mean_r = sum(vals) / len(vals)
        p_debut = sum(1 for r in vals if r <= 0.25) / len(vals)
        p_fin = sum(1 for r in vals if r > 0.75) / len(vals)
        print(f"{l} : r moyen = {mean_r:.3f} | P(r<=0.25) = {p_debut*100:.1f} % | P(r>0.75) = {p_fin*100:.1f} %")



# ---------- 7. leave-one-out : robustesse du test t apparié ----------
# CORRECTIF (revue de code) : ce bloc était un second script complet
# ("leave_one_out.py") collé ici avec ses propres imports et des tableaux
# `before`/`after` CODÉS EN DUR (recopiés à la main depuis la sortie de la
# section 1 au moment où elle a été écrite). Si corpus.py change un texte,
# ces tableaux restent faux silencieusement, sans aucun mécanisme pour les
# garder synchronisés. On les recalcule maintenant depuis `rows` (déjà
# construit en section 1), qui reflète toujours l'état réel de CORPUS.
print("\n" + "=" * 78)
print("7. LEAVE-ONE-OUT (ROBUSTESSE DU TEST T APPARIÉ)")
print("=" * 78)
names_loo = [r[0] for r in rows]
before_loo = np.array([r[1] for r in rows])
after_loo = np.array([r[2] for r in rows])

t, p = stats.ttest_rel(before_loo, after_loo)
print(f"{'—':<26s} t={t:6.3f}  p={p:.4f}  [{'sig' if p < 0.05 else 'NON SIG'}]")

print("\nLeave-one-out :")
for i, name in enumerate(names_loo):
    m = np.arange(len(names_loo)) != i
    t, p = stats.ttest_rel(before_loo[m], after_loo[m])
    status = "sig" if p < 0.05 else "NON SIG"
    print(f"sans {name:<22s} t={t:6.3f}  p={p:.4f}  [{status}]")
