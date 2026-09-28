# Entropie, structure positionnelle, bigrammes et ambiguïté résiduelle

Analyse complémentaire à `letter-frequency-analysis.md`, sur le même principe
(mesures reproductibles à partir du code du dépôt), mais centrée sur quatre
questions supplémentaires : la comparaison d'entropie entre les deux
alphabets, la répartition onset/nucleus/coda des 24 lettres AAC, la matrice
de bigrammes 24×24, et une mesure chiffrée de l'ambiguïté résiduelle
(bi-univocité) du système — plutôt que l'affirmation non calculée
« Bi-univocité totale = 0 » que contenait une version antérieure de
`alphabet_complet.py` (voir la revue de code jointe, point M7).

## 0. Méthodologie et échantillon

**Échantillon** : corpus 1 (`converter/corpus.py`, 8 textes indépendants,
2197 caractères) **+** corpus 2 (`converter/corpus2_dudh.py`,
Déclaration universelle des droits de l'homme en créole, 30 articles).

**Nettoyage du corpus 2** : ce texte contient, tel qu'il est stocké dans le
dépôt, un petit nombre de mots corrompus ou francisés lors d'une
transcription antérieure (déjà signalé dans la revue de code, point M10) :
`aux`, `qui`, `résultent`, `sex`, `entèénasyonal`, `complétéetou`, `piblick`,
`pwencip`, `princip`, `paticipe`, `diplius`, `peup`, `pèéyi`, `benéefisie`,
`repréesantan`, `matènité`, `volonté` — 17 mots sur 1586 (1,07 %), repérés
par la présence de `x`, `q`, `é` (absent de l'orthographe créole) ou d'un
`c`/`u` isolé hors des séquences `ch`/`ou`/`oun`/`ui`. Ils sont retirés avant
tokenisation : les inclure aurait mélangé du bruit de transcription avec de
vraies statistiques de langue.

**Alphabet 1979 (32 lettres)** : liste officielle vérifiée par recherche
(`howtocreole.com`, cohérente avec les résultats de l'Akademi Kreyòl
Ayisyen) : a, an, b, ch, d, e, è, en, f, g, h, i, j, k, l, m, n, ng, o, ò,
on, ou, oun, p, r, s, t, ui, v, w, y, z. Le texte est segmenté en 32 unités
par plus-longue-correspondance, avec la **même règle positionnelle** que
`acc_converter.NG_RULE` pour « ng » (nasale uniquement si non suivie d'une
voyelle — sinon « n » et « g » comptent comme deux consonnes séparées, ex.
*gran-gou*). `à` est traité comme allophone accentué de `a` (non listé comme
lettre distincte dans l'alphabet officiel).

**Alphabet AAC (24 lettres)** : celui codé dans `alphabet_complet.py`
(`abdefgijklmnoprstvwyz` + `š,ŏ,ŋ`). **Limite déjà signalée (revue de code,
M7), reconfirmée ici avec des chiffres exacts** : ce jeu de 24 caractères
ne couvre que **7674 des 7883 caractères** du texte ACC réel
(97,35 %) — les **209 caractères restants (2,65 %)**
sont `è`, `ò` et `à`, qui existent dans le texte converti mais n'appartiennent
pas à l'ensemble déclaré. Les tableaux ci-dessous respectent la demande
« 24 lettres AAC » à la lettre (alphabet code, sans `è/ò/à`) ; le tableau
« hors alphabet » qui suit chiffre précisément ce qui est ainsi laissé de
côté, pour que le lecteur puisse juger lui-même si ce choix lui convient.

---

## 1. Table de fréquence — 32 lettres (1979) vs 24 lettres (AAC)

### 1979 (32 unités)

| Lettre 1979 | Occurrences | Fréquence |
|---|---:|---:|
| a | 741 | 10.31 % |
| i | 614 | 8.54 % |
| e | 558 | 7.76 % |
| t | 518 | 7.21 % |
| k | 455 | 6.33 % |
| l | 424 | 5.90 % |
| s | 393 | 5.47 % |
| p | 300 | 4.17 % |
| y | 297 | 4.13 % |
| o | 247 | 3.44 % |
| m | 237 | 3.30 % |
| an | 231 | 3.21 % |
| r | 212 | 2.95 % |
| on | 209 | 2.91 % |
| d | 201 | 2.80 % |
| w | 199 | 2.77 % |
| ou | 197 | 2.74 % |
| en | 178 | 2.48 % |
| è | 157 | 2.18 % |
| n | 139 | 1.93 % |
| g | 111 | 1.54 % |
| b | 102 | 1.42 % |
| v | 87 | 1.21 % |
| f | 75 | 1.04 % |
| oun | 75 | 1.04 % |
| j | 62 | 0.86 % |
| z | 60 | 0.83 % |
| ò | 51 | 0.71 % |
| ch | 50 | 0.70 % |
| ng | 6 | 0.08 % |
| ui | 2 | 0.03 % |
| h | 0 | 0.00 % |
| **Total** | **7188** | **100.00 %** |

### AAC (24 lettres codées)

| Lettre AAC | Occurrences | Fréquence (sur les 24) |
|---|---:|---:|
| a | 971 | 12.65 % |
| n | 832 | 10.84 % |
| e | 736 | 9.59 % |
| i | 616 | 8.03 % |
| t | 518 | 6.75 % |
| o | 456 | 5.94 % |
| k | 455 | 5.93 % |
| l | 424 | 5.53 % |
| s | 393 | 5.12 % |
| p | 300 | 3.91 % |
| y | 297 | 3.87 % |
| ŏ | 272 | 3.54 % |
| m | 237 | 3.09 % |
| r | 212 | 2.76 % |
| d | 201 | 2.62 % |
| w | 201 | 2.62 % |
| g | 111 | 1.45 % |
| b | 102 | 1.33 % |
| v | 87 | 1.13 % |
| f | 75 | 0.98 % |
| j | 62 | 0.81 % |
| z | 60 | 0.78 % |
| š | 50 | 0.65 % |
| ŋ | 6 | 0.08 % |
| **Total** | **7674** | **100.00 %** |

### Caractères ACC hors des 24 lettres codées (è, ò, à)

| Caractère | Occurrences | % du total ACC |
|---|---:|---:|
| è | 157 | 1.99 % |
| ò | 51 | 0.65 % |
| à | 1 | 0.01 % |

**Lecture** : à eux seuls, `a`, `n`, `e`, `i`, `t` couvrent déjà
47.9 %
des caractères ACC — la distribution reste très inégale dans les deux
systèmes (c'est justement ce que l'entropie normalisée, section 2, permet
de quantifier plutôt que de constater à l'œil).

---

## 2. Entropie des deux alphabets

Formule utilisée (celle de l'énoncé), avec un **log dans la base de la
taille de l'alphabet** — ce qui rend les deux entropies directement
comparables sur l'échelle [0, 1] malgré la différence de taille (32 vs 24),
sans qu'il soit nécessaire de trancher au préalable le débat sur la bonne
façon de compter les lettres (§0) :

```
H_1979 = - Σ p_l · log_32(p_l)      (l parcourt les 32 lettres 1979)
H_AAC  = - Σ p_l · log_24(p_l)      (l parcourt les 24 lettres AAC codées)
```

| Système | Entropie normalisée | N (occurrences) |
|---|---:|---:|
| 1979 (32 lettres) | **0.9015** | 7188 |
| AAC (24 lettres codées) | **0.8991** | 7674 |
| AAC (27 caractères réellement observés, log base 27) | 0.8858 | 7883 |

**Hypothèse testée : H_AAC > H_1979 (l'alphabet AAC serait plus équilibré).**

**Résultat : l'hypothèse n'est pas confirmée par les données.** Sur cet
échantillon, `H_AAC` (0,899) est très légèrement **inférieure** à
`H_1979` (0,901), et l'écart se creuse encore (dans le même sens)
si l'on inclut `è`/`ò`/`à` dans l'alphabet AAC (colonne du bas). Autrement
dit, retirer les trois digrammes `ch`/`ou`/`ng` de la liste des lettres ne
rend pas la distribution des lettres restantes plus uniforme — ce qui est
cohérent avec le fait que ces trois lettres sont peu fréquentes
(3.5 % du texte 1979 à elles trois) : leur fusion en un seul
caractère chacune ne redistribue quasiment aucune masse de probabilité vers
les lettres sous-représentées (`j`, `z`, `h`...). L'argument « alphabet plus
équilibré » ne tient donc pas empiriquement sur cet échantillon ; l'écart
mesuré (0.0024) est de toute façon trop faible, sur un
corpus de cette taille (n=7188), pour être présenté comme une différence
robuste plutôt qu'un artefact d'échantillonnage — un test formel
nécessiterait un rééchantillonnage (bootstrap) sur des sous-corpus, non fait
ici. **Le vrai gain quantifiable de l'AAC n'est donc pas une meilleure
entropie de l'alphabet, mais le gain scriptural (nombre de caractères) déjà
mesuré ailleurs dans le dépôt** (`corpus.py`, `document_stats.py`) — ce sont
deux arguments différents, et il serait incorrect de présenter l'un comme
preuve de l'autre.

---

## 3. Analyse positionnelle complète (onset / nucleus / coda)

Chaque voyelle (`a,e,è,i,o,ò,ŏ`) est comptée comme noyau (`nucleus`) de sa
propre syllabe (règle de l'hiatus : deux voyelles adjacentes = deux
syllabes, pas de diphtongue) ; entre deux noyaux, une consonne unique est
l'attaque (`onset`) de la syllabe suivante, et un groupe de consonnes se
partage règle de l'attaque maximale (tout sauf la dernière = coda de la
syllabe précédente). `w`/`y` sont traités comme consonnes (simplification
déjà documentée dans le dépôt, cf. revue de code m5) : ce choix est
linguistiquement défendable pour le créole (semi-consonnes en attaque de
groupe), mais reste une simplification, pas une vérité universelle.

| Lettre | Occurrences | Onset | Nucleus | Coda |
|---|---:|---:|---:|---:|
| a | 971 | 0.0 % | 100.0 % | 0.0 % |
| b | 102 | 61.8 % | 0.0 % | 38.2 % |
| d | 201 | 95.5 % | 0.0 % | 4.5 % |
| e | 736 | 0.0 % | 100.0 % | 0.0 % |
| f | 75 | 96.0 % | 0.0 % | 4.0 % |
| g | 111 | 96.4 % | 0.0 % | 3.6 % |
| i | 616 | 0.0 % | 100.0 % | 0.0 % |
| j | 62 | 72.6 % | 0.0 % | 27.4 % |
| k | 455 | 60.9 % | 0.0 % | 39.1 % |
| l | 424 | 77.6 % | 0.0 % | 22.4 % |
| m | 237 | 89.0 % | 0.0 % | 11.0 % |
| n | 832 | 18.4 % | 0.0 % | 81.6 % |
| o | 456 | 0.0 % | 100.0 % | 0.0 % |
| p | 300 | 90.0 % | 0.0 % | 10.0 % |
| r | 212 | 83.5 % | 0.0 % | 16.5 % |
| s | 393 | 58.8 % | 0.0 % | 41.2 % |
| t | 518 | 72.2 % | 0.0 % | 27.8 % |
| v | 87 | 82.8 % | 0.0 % | 17.2 % |
| w | 201 | 99.5 % | 0.0 % | 0.5 % |
| y | 297 | 92.9 % | 0.0 % | 7.1 % |
| z | 60 | 90.0 % | 0.0 % | 10.0 % |
| ŋ | 6 | 0.0 % | 0.0 % | 100.0 % |
| ŏ | 272 | 0.0 % | 100.0 % | 0.0 % |
| š | 50 | 90.0 % | 0.0 % | 10.0 % |

**Lecture** :
- Les 7 voyelles (`a,e,i,o,è,ò,ŏ`) sont à **100 % en position nucléaire**,
  comme attendu — aucune ambiguïté positionnelle pour les voyelles.
- `ŋ` est à **100 % en coda**, ce qui est cohérent avec la règle même qui le
  produit (« ng » n'est converti que quand il N'EST PAS suivi d'une
  voyelle, donc jamais en attaque de la syllabe suivante). Ceci confirme
  empiriquement que la règle actuelle ne peut pas, par construction,
  produire un `ŋ` en onset — mais voir la mise en garde de la section 4 :
  cette même règle peut, sur certains mots, placer à tort en coda un `n`
  qui devrait rester séparé d'un `g` d'attaque (ex. *pengwen*).
- `n` est majoritairement en coda (81,6 %) — cohérent avec son rôle
  dominant dans les nasales `an/en/on` (toujours en coda de la voyelle qui
  précède).
- Les autres consonnes se répartissent très majoritairement en onset (`d`,
  `f`, `g`, `š`... > 90 %), à l'exception de `b`, `k`, `s`, qui apparaissent
  aussi comme coda dans 38–41 % des cas (finales de mots comme *bagay*,
  *dwa[k]*... à vérifier au cas par cas, hors du périmètre de ce script).

---

## 4. Bigrammes complets (24 × 24)

Comptés à l'intérieur des mots uniquement (jamais à cheval sur un espace ou
une apostrophe), sur les 7883 caractères ACC du corpus combiné. Une
paire est exclue de la matrice dès que l'un de ses deux caractères tombe
hors des 24 lettres codées (`è`, `ò`, `à` — voir §0) : 338 paires sur
5839 (≈ 5,8 %) sont dans ce cas et n'apparaissent pas ci-dessous.

| ↓1er \ 2e→ | a | b | d | e | f | g | i | j | k | l | m | n | o | p | r | s | t | v | w | y | z | ŋ | ŏ | š |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **a** | 0 | 16 | 7 | 0 | 2 | 1 | 1 | 17 | 86 | 60 | 9 | 231 | 0 | 32 | 55 | 66 | 62 | 18 | 1 | 25 | 10 | 5 | 0 | 1 |
| **b** | 9 | 0 | 0 | 3 | 0 | 0 | 6 | 0 | 0 | 17 | 0 | 0 | 11 | 0 | 3 | 0 | 0 | 0 | 3 | 9 | 0 | 0 | 4 | 0 |
| **d** | 13 | 0 | 1 | 62 | 0 | 0 | 35 | 0 | 0 | 1 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 72 | 1 | 0 | 0 | 2 | 0 |
| **e** | 2 | 0 | 3 | 0 | 3 | 15 | 1 | 1 | 40 | 35 | 13 | 178 | 0 | 39 | 20 | 28 | 29 | 21 | 0 | 23 | 9 | 1 | 0 | 1 |
| **f** | 14 | 0 | 1 | 7 | 0 | 0 | 5 | 0 | 0 | 2 | 0 | 0 | 10 | 0 | 2 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 2 | 0 |
| **g** | 19 | 0 | 0 | 68 | 0 | 0 | 0 | 0 | 0 | 2 | 0 | 0 | 5 | 0 | 10 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 3 | 0 |
| **i** | 10 | 41 | 12 | 7 | 6 | 2 | 0 | 8 | 91 | 12 | 7 | 16 | 7 | 6 | 14 | 34 | 62 | 12 | 0 | 8 | 15 | 0 | 0 | 1 |
| **j** | 8 | 0 | 0 | 16 | 0 | 0 | 11 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 | 3 | 6 | 0 | 0 | 6 | 0 |
| **k** | 68 | 0 | 0 | 37 | 0 | 0 | 62 | 0 | 0 | 15 | 0 | 1 | 65 | 0 | 11 | 15 | 4 | 0 | 2 | 0 | 6 | 0 | 19 | 0 |
| **l** | 91 | 0 | 0 | 32 | 0 | 0 | 138 | 0 | 1 | 1 | 2 | 3 | 24 | 0 | 0 | 0 | 3 | 0 | 9 | 2 | 0 | 0 | 2 | 0 |
| **m** | 54 | 1 | 1 | 28 | 0 | 0 | 16 | 0 | 0 | 0 | 0 | 1 | 9 | 0 | 0 | 0 | 0 | 0 | 19 | 0 | 0 | 0 | 70 | 0 |
| **n** | 86 | 1 | 24 | 20 | 3 | 3 | 22 | 11 | 8 | 0 | 23 | 17 | 9 | 13 | 2 | 39 | 45 | 2 | 0 | 14 | 0 | 0 | 9 | 1 |
| **o** | 0 | 6 | 4 | 0 | 3 | 3 | 0 | 0 | 11 | 10 | 18 | 209 | 1 | 7 | 2 | 32 | 41 | 4 | 0 | 0 | 4 | 0 | 0 | 1 |
| **p** | 69 | 0 | 0 | 29 | 0 | 0 | 52 | 0 | 1 | 7 | 4 | 2 | 15 | 0 | 18 | 0 | 0 | 0 | 22 | 3 | 0 | 0 | 45 | 0 |
| **r** | 51 | 0 | 0 | 70 | 0 | 0 | 43 | 0 | 0 | 0 | 0 | 2 | 2 | 0 | 0 | 0 | 30 | 0 | 0 | 0 | 0 | 0 | 1 | 0 |
| **s** | 60 | 0 | 0 | 49 | 3 | 0 | 37 | 0 | 8 | 0 | 1 | 4 | 32 | 9 | 0 | 0 | 14 | 0 | 29 | 79 | 0 | 0 | 15 | 0 |
| **t** | 35 | 0 | 0 | 117 | 0 | 0 | 116 | 0 | 0 | 1 | 2 | 1 | 4 | 0 | 18 | 2 | 0 | 0 | 6 | 1 | 0 | 0 | 70 | 0 |
| **v** | 26 | 0 | 0 | 12 | 0 | 0 | 19 | 0 | 0 | 5 | 0 | 0 | 6 | 0 | 4 | 0 | 0 | 0 | 8 | 0 | 0 | 0 | 0 | 0 |
| **w** | 122 | 0 | 0 | 35 | 0 | 0 | 7 | 0 | 0 | 0 | 0 | 0 | 23 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 2 | 0 |
| **y** | 15 | 0 | 0 | 50 | 0 | 0 | 20 | 0 | 0 | 0 | 4 | 0 | 177 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 6 | 0 |
| **z** | 12 | 0 | 0 | 8 | 0 | 0 | 20 | 0 | 0 | 0 | 1 | 0 | 8 | 0 | 0 | 1 | 0 | 0 | 4 | 1 | 0 | 0 | 0 | 0 |
| **ŋ** | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 1 | 0 | 0 | 0 | 0 | 0 |
| **ŏ** | 0 | 2 | 0 | 0 | 1 | 0 | 0 | 0 | 7 | 6 | 1 | 75 | 0 | 5 | 8 | 3 | 55 | 5 | 0 | 0 | 0 | 0 | 0 | 1 |
| **š** | 17 | 0 | 0 | 9 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 0 | 3 | 0 | 0 | 0 | 0 | 0 | 4 | 0 | 0 | 0 | 4 | 0 |

**Bigrammes les plus fréquents** : `an` (231), `on` (209), `en` (178) —
les trois nasales, qui restent des séquences de deux caractères en AAC
(non fusionnées, cf. §0) — suivies de `yo` (177, pronom pluriel), `li`
(138), `wa` (122), `te`/`ti` (117/116). La prédominance des nasales en tête
de classement illustre concrètement pourquoi la section 3 de
`docs/grapheme-table.md` explique le choix de NE PAS fusionner `an/en/on` :
ce sont déjà, de très loin, les bigrammes les plus fréquents du texte —
les fusionner en un caractère unique aurait un impact sur le gain
scriptural bien supérieur à celui de `ch`/`ou`/`ng` réunis, ce qui n'est
pas anodin pour qui voudrait un jour rouvrir ce débat (cf. la note de
`grapheme-table.md` sur la proposition Gourdet 2022).

---

## 5. Mesure de l'ambiguïté résiduelle (bi-univocité)

Formule de l'énoncé : `B = (1/N) · Σ 1/‖T(p_i)‖`, où `T(p_i)` est
l'ensemble des séquences 1979 pouvant produire la lettre/unité AAC `p_i`
(bijection parfaite ⟺ `‖T‖ = 1` pour toutes les lettres ⟺ `B = 1`).

**Correctif méthodologique** (par rapport à `alphabet_complet.py`) : la
version précédente affichait `Bi-univocité totale : Amb(...) = 0`,
**codé en dur**, sans être calculé à partir d'une quelconque définition de
`T`. `B` est ici réellement calculé à partir des règles de conversion
documentées (`acc_converter.py`, `docs/grapheme-table.md`), pas seulement
observé sur le corpus (un cas rare mais réel n'apparaîtrait pas forcément
dans un échantillon de 7188 lettres).

| Lettre AAC | ‖T(l)‖ | Source(s) 1979 possibles |
|---|---:|---|
| 22 lettres inchangées (a,b,d,e,f,g,i,j,k,l,m,n,o,p,r,s,t,v,w,y,z) + š, ŏ | 1 | bijection parfaite (š ← ch, ŏ ← ou, seules sources) |
| **ŋ** | **2** | `ng` en coda réelle (*lang*, *long* — cas normal) **OU** `n`+`g` à cheval sur une frontière syllabique mal détectée par la même règle positionnelle (*pengwen* = pe(n)-gwen, prononcé avec deux syllabes distinctes, mais la règle fusionne quand même `ng` car il n'est pas suivi d'une voyelle — cf. revue de code, point M6) |

**B (sur les 24 lettres) = 0.9792**
(23 lettres bi-univoques sur 24 ; seule `ŋ` porte une ambiguïté structurelle
documentée). Dans le corpus étudié, cette ambiguïté ne s'est *pas*
matérialisée : les 6 occurrences réelles de `ŋ` proviennent toutes
de vraies codas (`lang` notamment), pas d'un cas type *pengwen* — mais
`B < 1` reste correct pour signaler un **risque structurel** de la règle,
indépendant de sa fréquence d'occurrence dans tel ou tel échantillon.

**Ambiguïté supplémentaire, hors alphabet des 24 lettres — la séquence
« wi »** (déjà quantifiée en pratique lors de la revue de code, correctif
C1) : en ACC, la séquence `wi` a **deux** origines 1979 possibles —
`wi` (*wi* = oui, *kiwi*...) ou `ui` (converti). `T(wi) = 2`, donc
`1/T(wi) = 0,5` — c'est précisément pour cette raison que la conversion
inverse ACC → 1979 ne peut **pas**, par défaut, reconvertir `wi` en `ui` :
aucune règle mécanique ne peut discriminer les deux cas sans un lexique.
Cette ambiguïté n'est pas comptée dans le `B` ci-dessus (elle porte sur une
séquence de deux caractères, pas sur une lettre unique de l'alphabet à 24),
mais c'est en pratique la source d'imprécision la plus conséquente du
système : contrairement à `ŋ`, elle concerne des mots réellement fréquents
(*wi*, *kiwi*) et non un cas de figure rare (mot d'emprunt).

---

## 6. Résumé

| Question | Réponse chiffrée |
|---|---|
| H_AAC > H_1979 ? | **Non** — 0.8991 < 0.9015 (écart 0.0024, non robuste à ce n) |
| Bi-univocité des 24 lettres (B) | **0,9792** (1 lettre à risque structurel : ŋ) |
| Ambiguïté résiduelle la plus concrète | `wi` (T=2), hors des 24 lettres, déjà gérée par `convert_wi="none"` |
| Couverture réelle des « 24 lettres AAC » | **97.35 %** du texte ACC (reste : è, ò, à) |
| Bigrammes dominants | `an`, `on`, `en` (nasales, non fusionnées par choix) |

**À retenir pour la suite du mémoire** : l'argument le plus solide en
faveur de l'AAC reste le **gain scriptural mesuré** (`corpus.py`,
`document_stats.py`), pas un gain d'entropie de l'alphabet — cette dernière
hypothèse, testée ici pour la première fois avec un vrai calcul plutôt
qu'une affirmation, ne se vérifie pas sur l'échantillon disponible.
