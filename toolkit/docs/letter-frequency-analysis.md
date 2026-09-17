# Analyse fréquentielle et fonctionnelle des lettres atomiques

`converter/letter_analysis.py` mesure comment les trois lettres atomiques
de l'AAC (š, ŏ, ŋ) se comportent réellement dans un texte converti :
combien de fois elles apparaissent, dans quelle proportion des mots, et
quelle fonction syllabique (attaque / noyau / coda) elles y occupent.

Trois niveaux d'analyse, chacun avec ses formules exactes, puis un écart
constaté entre le code et le résumé du mémoire.

---

## 1. Fréquence des lettres atomiques

Calculée sur le texte **converti en AAC** (`to_acc(texte_1979)`), pas sur
l'original — on mesure la présence des lettres une fois qu'elles existent.

Soit `N` le nombre total de caractères du texte AAC (espaces inclus, comme
pour le calcul du gain scriptural dans `document_stats.py`), et `n_l` le
nombre d'occurrences de la lettre `l` (l ∈ {š, ŏ, ŋ}, insensible à la casse).

| Grandeur | Formule | Lecture |
|---|---|---|
| Fréquence relative | `f_l = n_l / N` | proportion du texte occupée par `l` |
| Pour 100 caractères | `f_l,100 = f_l × 100` | usage courant en typographie/édition |
| Pour 1000 caractères | `f_l,1000 = f_l × 1000` | usage courant en linguistique de corpus |
| Densité atomique totale | `D = (n_š + n_ŏ + n_ŋ) / N` | part du texte occupée par les 3 lettres réunies |
| Part parmi les atomiques | `p_l = n_l / (n_š + n_ŏ + n_ŋ)` | répartition interne (Σ p_l = 1) |

**Résultat mesuré sur les 8 textes de `corpus.py`** (`corpus_report()`) :

| Texte | n_š | n_ŏ | n_ŋ | D (densité) |
|---|---:|---:|---:|---:|
| lincoln_chant | 4 | 8 | 1 | 10,24 % |
| lincoln_dwa_travay | 3 | 2 | 0 | 8,77 % |
| konstitisyon_1987 | 0 | 2 | 3 | 2,55 % |
| dudh_atik1 | 0 | 9 | 0 | 6,72 % |
| pwoveb_lavi | 4 | 1 | 0 | 4,55 % |
| pwoveb_travay | 2 | 4 | 0 | 5,66 % |
| durand_choukoun | 11 | 29 | 1 | 6,03 % |
| sylvain_cigal_founmi | 6 | 20 | 0 | 3,88 % |

Densité atomique moyenne (n=8) : **6,05 %** (écart-type 2,53 %, min 2,55 %,
max 10,24 %) — cohérent avec le gain scriptural déjà mesuré (2,5 % à
9,3 %, moyenne 5,7 %, IC95 % [3,8 % ; 7,5 %], `test_corpus_diversity.py`),
puisque le gain provient presque entièrement de la fusion de
digrammes/trigrammes en une seule lettre atomique. `ŏ` domine largement
(≈ 62 % des occurrences atomiques toutes sources confondues) : `ou` est la
séquence opaque la plus fréquente du créole écrit.

---

## 2. Analyse au niveau du mot (couverture lexicale)

Soit `W` l'ensemble des mots du texte AAC (tokenisation sur les lettres,
ponctuation et chiffres exclus), `|W|` son cardinal, et `a(w)` le nombre
de lettres atomiques présentes dans le mot `w`.

| Grandeur | Formule | Lecture |
|---|---|---|
| Couverture globale | `C = \|{w ∈ W : a(w) ≥ 1}\| / \|W\|` | proportion des mots touchés par la réforme |
| Couverture par lettre | `C_l = \|{w ∈ W : l ∈ w}\| / \|W\|` | proportion des mots contenant spécifiquement `l` |
| Moyenne (tous les mots) | `μ_all = Σ_w a(w) / \|W\|` | densité atomique moyenne par mot, mots non concernés inclus |
| Moyenne (mots concernés) | `μ_pos = Σ_w a(w) / \|{w : a(w) ≥ 1}\|` | intensité de la réforme, une fois qu'un mot est touché |

**Résultat mesuré** (8 textes concaténés, 445 mots) :

- Couverture globale `C` = **22,0 %** — environ 1 mot créole sur 4-5 contient au moins une lettre atomique.
- Couverture par lettre : š = 6,5 %, ŏ = 15,5 %, ŋ = 1,1 %.
- `μ_all` = 0,247 lettre atomique par mot (tous mots confondus).
- `μ_pos` = 1,122 — un mot touché par la réforme ne contient presque toujours qu'**une seule** lettre atomique (peu de mots cumulent plusieurs digrammes opaques).

---

## 3. Analyse fonctionnelle syllabique (attaque / noyau / coda)

### Le syllabeur

`syllabify()` est un **découpeur heuristique graphémique**, pas une analyse
phonologique validée. Principe : chaque syllabe contient exactement une
voyelle-noyau (`VOWELS = a e è i o ò u ŏ`) ; les consonnes entre deux
noyaux suivent la règle d'attaque maximale (principe standard pour les
langues à forte préférence CV comme le créole) :

- 0 ou 1 consonne entre deux voyelles → elle part en attaque de la syllabe suivante ;
- 2 consonnes → 1 en coda de la syllabe précédente, 1 en attaque de la suivante ;
- 3 consonnes ou plus → toutes sauf la dernière en coda, la dernière en attaque (cas rare).

Exemples vérifiés par les tests (`test_letter_analysis.py`) :
`šante` → `šan-te`, `ekran` → `ek-ran`, `laŋ` → `laŋ` (1 syllabe).

**Limite assumée** : cet outil sert à mesurer *où le convertisseur place
réellement chaque lettre*, pas à trancher un débat de phonologie créole.

### Classification onset / nucleus / coda

Pour chaque occurrence d'une lettre atomique dans une syllabe, sa position
est son rang par rapport au noyau de cette syllabe : avant → `onset`,
au noyau → `nucleus`, après → `coda`.

**Résultat mesuré sur les 8 textes (627 syllabes, 445 mots)** :

| Lettre | Occurrences | Onset | Coda | Nucleus |
|---|---:|---:|---:|---:|
| š | 30 | 25 (83 %) | 5 (17 %) | — |
| ŏ | 75 | — | — | 75 (100 %) |
| ŋ | 5 | 0 (0 %) | 5 (100 %) | — |

`ŏ` est, par construction, **toujours** noyau (il vient toujours de `ou`,
une voyelle) — vérifié par `test_o_breve_is_always_nucleus`, qui fait
tourner cette assertion sur les 8 textes du corpus, pas seulement sur un
exemple isolé. Depuis la correction de la règle positionnelle de `ng` (voir
ci-dessous), `ŋ` est de la même façon **toujours** coda par construction —
vérifié par `test_corpus_wide_ng_is_always_coda`.

`š`, en revanche, n'est **pas** toujours en attaque : `bouch` → `bŏš` place
`š` en coda (17 % des cas mesurés sur le corpus) — attendu, et normal,
puisque `ch` note un phonème unique (/ʃ/) qui peut occuper n'importe quelle
position syllabique en créole, pas seulement l'attaque. Ce n'est pas un
bug : contrairement à `ng`, aucune règle positionnelle n'a jamais été
revendiquée pour `ch` dans le mémoire.

---

## Correction de la règle positionnelle de `ng` (historique)

Une version antérieure de cette analyse avait mis en évidence un écart
entre le code et le résumé du mémoire. Le résumé affirme :

> « Une règle positionnelle stricte encadre la substitution ng → ŋ, limitée
> aux occurrences en fin de syllabe et/ou de mot. »

Or `acc_converter.py` appliquait alors `ng → ŋ` sans aucune condition de
position. Exemple concret : `grangou` (gran-gou, "ng" à cheval sur deux
syllabes) devenait `graŋŏ`, où `ŋ` se retrouvait en **attaque** de la
syllabe `ŋŏ` — pas en fin de syllabe. Sur le corpus, cela produisait 38 %
d'occurrences de `ŋ` en onset plutôt qu'en coda.

**Ceci est maintenant corrigé.** `acc_converter.py` n'applique `ng → ŋ` que
lorsque `ng` n'est *pas* suivi d'une voyelle (donc uniquement en fin de mot,
en fin de composant d'un mot composé, ou devant une consonne) :

```text
grangou  -> grangŏ   (gran-gou : "g" commence la syllabe suivante, ng ne fusionne pas)
lingis   -> lingis   (lin-gis : idem, inchangé)
lang     -> laŋ      (ng en fin de mot : fusionne)
long     -> loŋ
Bleng-bleng -> Bleŋ-bleŋ
bling-blong -> bliŋ-bloŋ
```

La condition doit être testée **avant** la règle `ou → ŏ` : sinon la
voyelle qui suit `ng` est déjà consommée au moment du test, et la
condition « pas suivi d'une voyelle » devient toujours vraie à tort — c'est
exactement ce qui causait le bug initial. `acc_converter.py` applique donc
désormais la règle `ng` en premier, avant la boucle des autres règles.

Conséquence mesurable : la densité et le gain scriptural du texte
`sylvain_cigal_founmi` (qui contient trois fois « grangou ») ont
légèrement baissé (gain : 4,17 % → 3,74 % ; la fusion en `ŋ` économisait un
caractère à tort à chaque occurrence). L'écart type et la borne basse de
l'IC95 % du corpus en ont été très légèrement affectés (voir la table
ci-dessus et `README.md`) ; la moyenne (5,7 %) et l'écart min–max global
(2,5 %–9,3 %) restent inchangés au premier chiffre après la virgule.

Cette correction rend désormais **exacte** l'affirmation du résumé du
mémoire sur la règle positionnelle de `ng` — ce n'était pas le cas avant.

---

## Utilisation

```python
from converter.letter_analysis import full_report, corpus_report
from converter.corpus import CORPUS

# Sur un seul texte
r = full_report("Chante pou chase lapli nan kò mwen...")
r["frequency"].atomic_density        # D
r["word_level"].coverage             # C
r["syllable_functional"].summary()   # texte lisible onset/nucleus/coda

# Sur tout le corpus de validation (8 textes)
texts = {k: v["texte"] for k, v in CORPUS.items()}
agg = corpus_report(texts)
agg["mean_density_percent"], agg["min_density_percent"], agg["max_density_percent"]
```

Tests : `python3 -m pytest converter/tests/test_letter_analysis.py -v` (16 tests).
