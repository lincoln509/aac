# Analyse fréquentielle et fonctionnelle des lettres atomiques

`converter/letter_analysis.py` mesure comment les trois lettres atomiques
de l'AAC (š, ŏ, ŋ) se comportent réellement dans un texte converti :
combien de fois elles apparaissent, dans quelle proportion des mots, et
quelle fonction syllabique (attaque / noyau / coda) elles y occupent.

Trois niveaux d'analyse, chacun avec ses définitions formelles, puis un
écart constaté (et depuis corrigé) entre le code et le résumé du mémoire.

---

## Notations préliminaires

Soit $\Sigma$ l'alphabet du texte converti en AAC, et $T = (c_1, c_2, \dots, c_N) \in \Sigma^N$
la séquence des $N$ caractères de ce texte **converti** (`to_aac(texte_1979)`),
espaces inclus — comme pour le calcul du gain scriptural dans `document_stats.py`.
On mesure la présence des lettres atomiques une fois qu'elles existent, pas
sur l'original.

Soit $\mathcal{A} = \{\text{š}, \text{ŏ}, \text{ŋ}\} \subset \Sigma$ l'ensemble
des lettres atomiques, la comparaison se faisant modulo une fonction de
normalisation de casse $\kappa$ (insensible à la casse).

Pour toute lettre $l \in \mathcal{A}$, on note l'indicatrice
$\mathbb{1}[c_i \doteq l] = 1$ si $\kappa(c_i) = \kappa(l)$, et $0$ sinon.

---

## 1. Fréquence des lettres atomiques

**Occurrences.**
$$n_l = \sum_{i=1}^{N} \mathbb{1}[c_i \doteq l], \qquad l \in \mathcal{A}$$

| Grandeur | Définition | Lecture |
|---|---|---|
| Fréquence relative | $f_l = \dfrac{n_l}{N}$ | proportion du texte occupée par $l$ |
| Pour 100 caractères | $f_{l,100} = 100\, f_l$ | usage courant en typographie/édition |
| Pour 1000 caractères | $f_{l,1000} = 1000\, f_l$ | usage courant en linguistique de corpus |
| Densité atomique totale | $D = \dfrac{1}{N}\displaystyle\sum_{l \in \mathcal{A}} n_l = \sum_{l \in \mathcal{A}} f_l$ | part du texte occupée par les 3 lettres réunies |
| Part parmi les atomiques | $p_l = \dfrac{n_l}{\sum_{l' \in \mathcal{A}} n_{l'}}$ | répartition interne, avec $\displaystyle\sum_{l \in \mathcal{A}} p_l = 1$ |

L'écriture $D = \sum_l f_l$ rend explicite que $D$ est l'agrégat additif
des trois fréquences relatives — une identité structurelle, pas une
coïncidence à vérifier empiriquement.

**Résultat mesuré sur les 8 textes de `corpus.py`** (`corpus_report()`) :

| Texte | $n_{\text{š}}$ | $n_{\text{ŏ}}$ | $n_{\text{ŋ}}$ | $D$ (densité) |
|---|---:|---:|---:|---:|
| lincoln_chant | 4 | 8 | 1 | 10,24 % |
| lincoln_dwa_travay | 3 | 2 | 0 | 8,77 % |
| konstitisyon_1987 | 0 | 2 | 3 | 2,55 % |
| dudh_atik1 | 0 | 9 | 0 | 6,72 % |
| pwoveb_lavi | 4 | 1 | 0 | 4,55 % |
| pwoveb_travay | 2 | 4 | 0 | 5,66 % |
| durand_choukoun | 11 | 29 | 1 | 6,03 % |
| sylvain_cigal_founmi | 6 | 20 | 0 | 3,88 % |

Densité atomique moyenne ($n=8$) : **6,05 %** (écart-type 2,53 %, min 2,55 %,
max 10,24 %) — cohérent avec le gain scriptural déjà mesuré (2,5 % à
9,3 %, moyenne 5,7 %, IC95 % [3,8 % ; 7,5 %], `test_corpus_diversity.py`),
puisque le gain provient presque entièrement de la fusion de
digrammes/trigrammes en une seule lettre atomique. `ŏ` domine largement
($p_{\text{ŏ}} \approx 62\,\%$ des occurrences atomiques toutes sources
confondues) : `ou` est la séquence opaque la plus fréquente du créole écrit.

---

## 2. Analyse au niveau du mot (couverture lexicale)

**Tokenisation.** Soit $\tau : T \to W$ une fonction de segmentation qui
découpe le texte en mots (lettres uniquement, ponctuation et chiffres
exclus), et $W = (w_1, \dots, w_M)$ la suite des mots obtenus, $M = |W|$.

**Compte atomique par mot.** Pour $w = (c_1, \dots, c_k)$,
$$a(w) = \sum_{j=1}^{k} \mathbb{1}[c_j \in \mathcal{A}]$$
(nombre de lettres atomiques dans $w$, avec multiplicité).

Soit $W^+ = \{w \in W : a(w) \geq 1\}$ le sous-ensemble des mots touchés
par la réforme.

| Grandeur | Définition | Lecture |
|---|---|---|
| Couverture globale | $C = \dfrac{\lvert W^+ \rvert}{M}$ | proportion des mots touchés par la réforme |
| Couverture par lettre | $C_l = \dfrac{\lvert \{w \in W : l \in w\} \rvert}{M}$ | proportion des mots contenant spécifiquement $l$ |
| Moyenne globale | $\mu_{\text{all}} = \dfrac{1}{M} \displaystyle\sum_{w \in W} a(w)$ | densité atomique moyenne par mot, mots non concernés inclus |
| Moyenne conditionnelle | $\mu_{\text{pos}} = \dfrac{1}{\lvert W^+ \rvert} \displaystyle\sum_{w \in W^+} a(w)$ | intensité de la réforme, une fois qu'un mot est touché |

**Identité de cohérence.** Puisque les mots hors $W^+$ contribuent 0 à la
somme, $\sum_{w \in W} a(w) = \sum_{w \in W^+} a(w)$, d'où :
$$\mu_{\text{all}} = C \cdot \mu_{\text{pos}}$$

Cette identité permet de vérifier la cohérence interne des trois chiffres
sans recompter sur le corpus. Par ailleurs, pour chaque $l \in \mathcal{A}$,
$C_l \le C$, et $\sum_l C_l \ge C$ (égalité seulement si aucun mot ne
contient deux lettres atomiques distinctes).

**Résultat mesuré** (8 textes concaténés, $M = 445$ mots) :

- Couverture globale $C$ = **22,0 %** — environ 1 mot créole sur 4-5 contient au moins une lettre atomique.
- Couverture par lettre : $C_{\text{š}}$ = 6,5 %, $C_{\text{ŏ}}$ = 15,5 %, $C_{\text{ŋ}}$ = 1,1 %.
- $\mu_{\text{all}}$ = 0,247 lettre atomique par mot (tous mots confondus).
- $\mu_{\text{pos}}$ = 1,122 — un mot touché par la réforme ne contient presque toujours qu'**une seule** lettre atomique (peu de mots cumulent plusieurs digrammes opaques).

Vérification de l'identité : $C \cdot \mu_{\text{pos}} = 0{,}220 \times 1{,}122 \approx 0{,}247 = \mu_{\text{all}}$ ✓.

---

## 3. Analyse fonctionnelle syllabique (attaque / noyau / coda)

### Le syllabeur

$\text{syllabify} : W \to \mathcal{S}^*$ est un **découpeur heuristique
graphémique**, pas une analyse phonologique validée : il associe à chaque
mot $w$ une suite ordonnée de syllabes $(s_1, \dots, s_m)$, $s_j \in \mathcal{S}$.

Principe : chaque syllabe $s \in \mathcal{S}$ contient exactement une
voyelle-noyau, avec $\text{VOWELS} = \{a, e, è, i, o, ò, u, \text{ŏ}\}$ ; les
consonnes entre deux noyaux suivent la règle d'attaque maximale (principe
standard pour les langues à forte préférence CV comme le créole) :

- 0 ou 1 consonne entre deux voyelles → elle part en attaque de la syllabe suivante ;
- 2 consonnes → 1 en coda de la syllabe précédente, 1 en attaque de la suivante ;
- 3 consonnes ou plus → toutes sauf la dernière en coda, la dernière en attaque (cas rare).

Exemples vérifiés par les tests (`test_letter_analysis.py`) :
`šante` → `šan-te`, `ekran` → `ek-ran`, `laŋ` → `laŋ` (1 syllabe).

**Limite assumée** : cet outil sert à mesurer *où le convertisseur place
réellement chaque lettre*, pas à trancher un débat de phonologie créole.

### Classification onset / nucleus / coda

Soit $s = (\sigma_1, \dots, \sigma_k)$ une syllabe, c'est-à-dire la suite
ordonnée de ses $k$ caractères — pour `šan`, $s = (\sigma_1, \sigma_2, \sigma_3)
= (\text{š}, a, n)$. Soit $j^* \in \{1, \dots, k\}$ l'indice (unique, par
construction du syllabeur) du noyau vocalique de $s$ — ici $j^* = 2$, car
$\sigma_2 = a$ est la voyelle.

Pour chaque indice $j$ tel que $\sigma_j \in \mathcal{A}$ (c'est-à-dire pour
chaque occurrence d'une lettre atomique dans $s$), on définit la fonction
de position, qui compare le rang $j$ de cette occurrence au rang $j^*$ du
noyau :

$$
\text{pos}(\sigma_j, s) =
\begin{cases}
\text{onset} & \text{si } j < j^* \\
\text{nucleus} & \text{si } j = j^* \\
\text{coda} & \text{si } j > j^*
\end{cases}
$$

c'est-à-dire le rang de l'occurrence par rapport au noyau de sa syllabe :
avant → attaque, au noyau → noyau, après → coda.

Dans l'exemple `šan` : $\text{pos}(\sigma_1, s) = \text{pos}(\text{š}, s) = \text{onset}$
(car $1 < 2$), et si la syllabe contenait un `ŋ` en position 3, on aurait
$\text{pos}(\sigma_3, s) = \text{coda}$ (car $3 > 2$). C'est une fonction
définie *par occurrence*, pas par lettre : il faut l'agréger sur tout le
corpus pour obtenir un résultat par lettre atomique.

**Distribution conditionnelle empirique.** En notant $\text{Occ}(l)$
l'ensemble des occurrences de $l$ dans le corpus syllabifié, on définit,
pour chaque lettre $l \in \mathcal{A}$ et chaque position $c \in
\{\text{onset}, \text{nucleus}, \text{coda}\}$, l'estimateur du maximum de
vraisemblance sous un modèle multinomial :

$$\hat{\Pr}[\text{pos} = c \mid l] = \frac{\bigl|\{\sigma \in \text{Occ}(l) : \text{pos}(\sigma, s_\sigma) = c\}\bigr|}{|\text{Occ}(l)|}$$

avec, pour chaque lettre, $\displaystyle\sum_{c} \hat{\Pr}[\text{pos} = c \mid l] = 1$.

**Résultat mesuré sur les 8 textes (627 syllabes, 445 mots)** :

| Lettre | $\lvert\text{Occ}(l)\rvert$ | $\hat{\Pr}[\text{onset}\mid l]$ | $\hat{\Pr}[\text{coda}\mid l]$ | $\hat{\Pr}[\text{nucleus}\mid l]$ |
|---|---:|---:|---:|---:|
| š | 30 | 0,83 | 0,17 | 0 |
| ŏ | 75 | 0 | 0 | 1,00 |
| ŋ | 5 | 0 | 1,00 | 0 |

`ŏ` est, par construction, **toujours** noyau : $\hat{\Pr}[\text{nucleus} \mid \text{ŏ}] = 1$
(il vient toujours de `ou`, une voyelle) — vérifié par
`test_o_breve_is_always_nucleus`, qui fait tourner cette assertion sur les
8 textes du corpus, pas seulement sur un exemple isolé. Depuis la
correction de la règle positionnelle de `ng` (voir ci-dessous), `ŋ` est de
la même façon **toujours** coda par construction, $\hat{\Pr}[\text{coda} \mid \text{ŋ}] = 1$
— vérifié par `test_corpus_wide_ng_is_always_coda`.

`š`, en revanche, n'est **pas** toujours en attaque :
$\hat{\Pr}[\text{coda} \mid \text{š}] \approx 0{,}17$. Exemple : `bouch` →
`bŏš` place `š` en coda — attendu, et normal, puisque `ch` note un phonème
unique (/ʃ/) qui peut occuper n'importe quelle position syllabique en
créole, pas seulement l'attaque. Ce n'est pas un bug : contrairement à
`ng`, aucune règle positionnelle n'a jamais été revendiquée pour `ch` dans
le mémoire.

Notez que les deux distributions dégénérées ($\hat{\Pr}[\cdot \mid \text{ŏ}]$
et $\hat{\Pr}[\cdot \mid \text{ŋ}]$, concentrées sur un seul point) ne sont
pas des artefacts de mesure : ce sont des conséquences directes des règles
de conversion (`ou` est toujours une voyelle, `ng → ŋ` n'est appliqué que
sans voyelle suivante). Seule la distribution de `š` est une véritable
distribution empirique non triviale, reflet du comportement réel de `ch`
en créole.

---

## Correction de la règle positionnelle de `ng` (historique)

Une version antérieure de cette analyse avait mis en évidence un écart
entre le code et le résumé du mémoire. Le résumé affirme :

> « Une règle positionnelle stricte encadre la substitution ng → ŋ, limitée
> aux occurrences en fin de syllabe et/ou de mot. »

Or `aac_converter.py` appliquait alors `ng → ŋ` sans aucune condition de
position. Exemple concret : `grangou` (gran-gou, "ng" à cheval sur deux
syllabes) devenait `graŋŏ`, où `ŋ` se retrouvait en **attaque** de la
syllabe `ŋŏ` — pas en fin de syllabe. Sur le corpus, cela produisait 38 %
d'occurrences de `ŋ` en onset plutôt qu'en coda.

**Ceci est maintenant corrigé.** `aac_converter.py` n'applique `ng → ŋ` que
lorsque `ng` n'est *pas* suivi d'une voyelle (donc uniquement en fin de mot,
en fin de composant d'un mot composé, ou devant une consonne) :

```text
grangou  -> grangŏ   (gran-gou : "g" commence la syllabe suivante, ng ne fusionne pas)
lengis   -> lengis   (lin-gis : idem, inchangé)
lang     -> laŋ      (ng en fin de mot : fusionne)
long     -> loŋ
Bleng-bleng -> Bleŋ-bleŋ
bling-bleng -> bliŋ-bleŋ
```

La condition doit être testée **avant** la règle `ou → ŏ` : sinon la
voyelle qui suit `ng` est déjà consommée au moment du test, et la
condition « pas suivi d'une voyelle » devient toujours vraie à tort — c'est
exactement ce qui causait le bug initial. `aac_converter.py` applique donc
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
