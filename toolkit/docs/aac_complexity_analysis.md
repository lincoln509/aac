# Analyse de la complexité et du coût du système AAC

Ce document formalise les onze grandeurs proposées pour évaluer le système
de conversion AAC au-delà du seul gain scriptural : la qualité de la
correspondance phonème/graphème, le coût de la réforme pour l'usager
humain, sa distinctivité linguistique, son impact matériel, et la validité
statistique des mesures.

Contrairement à `letter-frequency-analysis.md`, la plupart de ces
grandeurs ne sont **pas encore implémentées** dans `converter/` : aucun
fichier de code ne calcule $B$, $\Omega$, $C_{\text{mém}}$, $C_{\text{moteur}}$,
$\text{Fert}$, $D(g)$, $J(g)$, $E_{\text{papier}}$ ou $t$ dans l'état actuel
du projet (seul $\gamma$, le gain scriptural, existe déjà dans
`acc_converter.py`/`.js` et `document_stats.py`). Ce document a donc un
double objectif : (1) fixer une définition formelle non ambiguë de chaque
grandeur, suffisamment précise pour être codée sans interprétation
différente d'un développeur à l'autre, et (2) signaler, comme pour `ng`
dans le document précédent, les points où la formule telle que donnée est
**sous-déterminée** et où un choix d'implémentation devra être fait et
documenté avant tout calcul sur corpus.

Trois résultats peuvent en revanche déjà être vérifiés sans nouveau code,
soit par dérivation directe de `acc_converter.py`, soit par un test
ponctuel : ils sont présentés avec leurs chiffres, le reste reste à l'état
de spécification.

---

## Notations préliminaires — symboles disjoints de `letter-frequency-analysis.md`

Deux symboles de la formule $B$ auraient, tels que donnés dans l'image
source, réutilisé des lettres déjà prises dans
`letter-frequency-analysis.md` avec un **sens différent** ($N$ = nombre de
caractères là-bas, $T$ = la séquence de caractères elle-même). Pour que
les deux documents restent lisibles côte à côte sans glossaire de
désambiguïsation, ils sont remplacés ici par deux symboles neufs,
définis uniquement dans ce document et ne réapparaissant nulle part
ailleurs dans le mémoire :

| Nouveau symbole | Définition | Remplace (dans la formule $B$ telle que donnée) |
|---|---|---|
| $K$ | nombre de phonèmes distincts de l'inventaire créole $P=\{p_1,\dots,p_K\}$ considéré | $N$ |
| $\mathcal{G}(p_i)$ | ensemble des graphies attestées, dans le corpus, pour le phonème $p_i$ | $T(p_i)$ |

La formule 1.1 ci-dessous est donc écrite avec $K$ et $\mathcal{G}$, pas
avec $N$ et $T$.

Les autres symboles introduits dans ce document restent, eux, des
réutilisations **volontaires et cohérentes** de `letter-frequency-analysis.md`,
à garder telles quelles :

| Symbole | Sens dans `letter-frequency-analysis.md` | Usage ici | Pourquoi ce n'est pas une collision |
|---|---|---|---|
| $\gamma$ | — (non défini là-bas) | gain scriptural, réutilisé à l'identique en §1.3 et §4.1 | même définition partout : réutilisation, pas collision |
| $f$ | $f_l = n_l/N$, une seule fonction, un seul domaine (lettres atomiques) | une **famille** de fonctions de fréquence, chacune indexée différemment : $f(s)$ (séquences, §1.2), $f_k$ (règles, §1.4), $f(g)$ (graphèmes, §2.2) | domaines disjoints et toujours indexés explicitement — mais à ne **pas** coder comme un seul dict global `f`, précisément pour ne pas recréer la collision en code |
| $g$ | — | grapheme générique (digramme/trigramme ou lettre atomique) | symbole neuf, aucun usage antérieur |

Le reste des notations ($\Sigma$, $\mathcal{A}=\{\text{š},\text{ŏ},\text{ŋ}\}$,
$\kappa$) suit `letter-frequency-analysis.md` sans changement.

---

## 1. Efficacité orthographique du système

### 1.1 Bi-univocité — $B = \dfrac{1}{K}\displaystyle\sum_{i=1}^{K} \dfrac{1}{\lVert \mathcal{G}(p_i) \rVert}$

**Lecture.** Mesure si chaque phonème du créole correspond à une seule
graphie (principe fondateur de l'orthographe phonologique de 1979, et
objectif revendiqué de l'AAC). Soit $P=\{p_1,\dots,p_K\}$ l'inventaire des
phonèmes du créole et $\mathcal{G}(p_i) \subseteq \Sigma^+$ l'ensemble des
graphies différentes attestées dans le corpus pour $p_i$. Si $p_i$
s'écrit toujours de la même façon, $\lVert \mathcal{G}(p_i)\rVert = 1$ et
sa contribution vaut $1$ ; s'il a $k$ graphies concurrentes, sa
contribution tombe à $1/k$. $B \in (0, 1]$, avec $B=1$ ssi la
correspondance est parfaitement biunivoque phonème → graphie.

**Point sous-déterminé.** La formule ne précise pas le sens de la
correspondance. $B$ telle qu'écrite mesure l'univocité **phonème → graphies**
(« le phonème /ʃ/ a-t-il toujours la même écriture ? »), ce qui est la
question pertinente pour un *scripteur*. La question symétrique
**graphie → phonèmes** (« la lettre `g` se lit-elle toujours pareil ? »,
pertinente pour un *lecteur*) donnerait une formule différente,
$B' = \frac{1}{\lVert\Sigma\rVert}\sum_g \frac{1}{\lVert \mathcal{G}^{-1}(g)\rVert}$,
avec potentiellement une valeur différente. Les deux sont utiles mais ne
sont pas interchangeables ; le mémoire doit préciser laquelle est visée
avant implémentation. Avec les graphies 1979 (`ch`, `ou`, `ng`, `ui`) et
leur unique lecture phonémique assumée par le mémoire, l'AAC ne change
*a priori* pas $B$ côté phonème → graphie (un phonème gardait déjà une
seule graphie en 1979, l'AAC ne fait qu'en raccourcir l'écriture) — sauf
si l'inventaire $P$ inclut des cas de variation dialectale ou
d'homographie non couverts ici.

### 1.2 Opacité — $\Omega = \displaystyle\sum_{s} f(s)\,\text{Op}(s)$

**Lecture.** $s$ parcourt les séquences graphémiques candidates (`ch`,
`ou`, `ng`, `ui`, mais aussi, en 1979, toute séquence qui *pourrait* être
lue lettre à lettre), $f(s)$ leur fréquence dans le texte 1979, et
$\text{Op}(s) \in \{0,1\}$ (ou $[0,1]$ si graduée) indique si $s$ est
« opaque » — c'est-à-dire si sa lecture ne se déduit pas de la simple
concaténation des valeurs de ses lettres. $\Omega$ est la masse totale
d'opacité du texte, pondérée par la fréquence d'usage.

**Lien avec les données déjà disponibles.** Avec $\text{Op}(s)=1$ pour
$s \in \{\text{ch, ou, ng, ui}\}$ et $0$ sinon, $\Omega$ compté en
occurrences brutes (sans normaliser par la longueur du texte) coïncide
avec la somme des quatre compteurs déjà renvoyés par `diff_summary()` /
`diffSummary()` dans `acc_converter.py`/`.js` — aucune nouvelle mesure
n'est nécessaire pour cette version simple, seulement une somme
pondérée des champs `ch`, `ou`, `ng`, `ui` du dictionnaire déjà renvoyé.

**Point à ne pas confondre avec $\gamma$.** `ui` compte comme opaque
($\text{Op}(\text{ui})=1$, digramme non lu lettre à lettre) mais ne
contribue **pas** au gain scriptural $\gamma$ : `ui → wi` ne fusionne pas
deux caractères en un seul atome, donc $\Delta_{\text{ui}} = 0$ dans la
formule 1.4 ci-dessous alors que $\text{Op}(\text{ui})=1$ ici. $\Omega$ et
$\gamma$ ne doivent donc pas être présentés comme deux mesures d'une même
chose à un facteur près : $\Omega$ mesure l'opacité *de lecture*, $\gamma$
le gain *d'écriture*, et elles divergent précisément sur `ui`.

### 1.3 Gain scriptural — $\gamma = 1 - \dfrac{n_{\text{AAC}}}{n_{1979}}$

**Déjà implémenté.** Cette formule est exactement
`gainPercentTotal / 100` dans `acc_converter.py`/`.js`
(`(before - after) / before`, avec `before = n_1979`, `after = n_AAC`) —
aucun nouveau code n'est nécessaire, seul le nom diffère. C'est la
grandeur déjà mesurée dans `letter-frequency-analysis.md` et
`document_stats.py` : moyenne 5,7 %, IC95 % [3,8 % ; 7,5 %] sur le corpus
de 8 textes (voir §4.2 pour une vérification de cohérence de cet
intervalle avec la formule $t$ de validation statistique).

### 1.4 Décomposition du gain — $\mathbb{E}[\gamma] = \displaystyle\sum_k f_k\,\Delta_k$

**Lecture.** $k$ parcourt les règles de conversion (`ch→š`, `ou→ŏ`,
`ng→ŋ`, `ui→wi`), $\Delta_k$ le nombre de caractères économisés par
application de la règle $k$ ($\Delta_{\text{ch}}=\Delta_{\text{ou}}=\Delta_{\text{ng}}=1$,
$\Delta_{\text{ui}}=0$), et $f_k$ la fréquence de la règle $k$.

**Ce n'est pas une approximation : c'est une identité exacte, à condition
de bien normaliser $f_k$.** Si l'on pose $f_k = n_k / n_{1979}$ (le
nombre d'applications de la règle $k$ rapporté à la longueur du texte
**1979**, pas au nombre de mots ni au nombre d'occurrences d'opacité), on
a directement $\sum_k n_k \Delta_k = n_{1979} - n_{\text{AAC}}$ par
construction (chaque application de $k$ retire exactement $\Delta_k$
caractères), d'où $\sum_k f_k \Delta_k = \frac{n_{1979}-n_{\text{AAC}}}{n_{1979}} = \gamma$
— l'espérance $\mathbb{E}[\cdot]$ de la notation est donc trompeuse : ce
n'est pas une espérance statistique approchée mais une décomposition
additive exacte de $\gamma$ en contributions par règle, au même titre que
l'identité $\mu_{\text{all}} = C \cdot \mu_{\text{pos}}$ déjà établie dans
`letter-frequency-analysis.md` §2. Cette précision doit être ajoutée au
mémoire : telle quelle, la notation $\mathbb{E}[\gamma]$ suggère une
approximation probabiliste alors qu'il s'agit d'une égalité stricte sous
la bonne normalisation.

---

## 2. Charge pour l'usager humain

### 2.1 Charge cognitive — $C_{\text{mém}} = \alpha \lVert U \rVert + \beta \lVert R \rVert$

**Lecture.** $U$ = ensemble des nouveaux symboles à mémoriser (š, ŏ, ŋ :
$\lVert U \rVert = 3$), $R$ = ensemble des règles à mémoriser pour les
utiliser correctement, $\alpha, \beta$ = coûts unitaires (un nouveau
symbole coûte-t-il plus ou moins cher à apprendre qu'une règle de
position ?).

**Point sous-déterminé : que compte-t-on dans $R$ ?** Ce n'est pas
seulement « 4 règles » (une par digramme). Le travail déjà fait sur ce
projet montre que $R$ doit au minimum inclure, séparément :
1. la règle positionnelle de `ng` (ng → ŋ seulement en fin de syllabe) ;
2. la règle, plus simple, « toujours » pour `ch` et `ou` ;
3. la règle *lexicale* `ui/wi`, qui n'est pas une règle de conversion
   simple mais une liste d'exceptions à retenir par cœur
   (`WI_WORDS_NEVER_FROM_UI = {wi, kiwi, sandwich, sandwitch}` dans
   `acc_converter.py`/`.js`) — chaque mot de cette liste est, du point de
   vue de la charge cognitive, un item de mémorisation supplémentaire
   distinct, pas une sous-partie négligeable d'« une » règle `ui`.

Si $R$ est compté au niveau des règles seulement, $\lVert R \rVert = 3$
(ng, ch/ou, ui) ; si l'on compte aussi les exceptions lexicales comme des
items de $R$ (plus honnête vis-à-vis de l'usager qui doit réellement les
retenir), $\lVert R \rVert = 3 + 4 = 7$ avec le lexique actuel — et cette
valeur grandit mécaniquement si le lexique d'exceptions est étendu. Le
mémoire doit choisir et documenter l'une des deux conventions avant de
publier une valeur numérique de $C_{\text{mém}}$, sans quoi le chiffre
n'est pas reproductible.

### 2.2 Coût du tracé — $C_{\text{moteur}} = \displaystyle\sum_g f(g)\,m(g)\,\tau$

**Lecture.** $g$ parcourt les graphèmes, $f(g)$ leur fréquence, $m(g)$ le
nombre de mouvements/traits nécessaires pour les tracer à la main, $\tau$
le temps (ou coût) moyen par trait.

**Mise en garde : ne pas confondre économie de caractères et économie de
traits.** $\gamma > 0$ ne garantit *pas* $C_{\text{moteur}}$ plus faible.
Une lettre atomique accentuée comme š ou ŏ s'écrit à la main en au moins
deux traits distincts (le corps de la lettre + le diacritique, souvent
tracé après coup comme pour un `i` pointé), soit potentiellement **autant
ou plus** de traits que les deux lettres latines non accentuées `c`+`h`
ou `o`+`u` qu'elle remplace, selon la convention retenue pour $m(\cdot)$.
$\gamma$ compte des *caractères informatiques* (code points), pas des
*gestes manuscrits* : les deux grandeurs peuvent diverger, et $C_{\text{moteur}}$
mérite d'être calculée séparément plutôt que déduite de $\gamma$ par
analogie. Ceci est cohérent avec l'avertissement déjà formulé en 1.2 à
propos de $\Omega$ vs $\gamma$ : ce document distingue systématiquement
ce qui se compte en caractères de ce qui se compte en efforts réels
(lecture, écriture manuscrite, mémorisation).

### 2.3 Fertilité tokenistique — $\text{Fert} = \dfrac{\#\text{tokens}}{\#\text{mots}}$

**Lecture.** Mesure, pour un tokeniseur donné (typiquement un tokeniseur
de type BPE utilisé par un modèle de langue), en combien de sous-unités
("tokens") un texte est découpé en moyenne par mot — pertinent si le
mémoire veut évaluer le coût de l'AAC pour un traitement automatique
(LLM, NLP) plutôt que pour un humain.

**Vérification par la longueur en octets.** Avant toute mesure avec un
vrai tokeniseur, la longueur en octets UTF-8 — qui conditionne le
comportement de tout tokeniseur byte-level — donne déjà une indication.
Résultat mesuré sur quelques mots :

| Mot 1979 | caractères | octets UTF-8 | Mot AAC | caractères | octets UTF-8 |
|---|---:|---:|---|---:|---:|
| chante | 6 | 6 | šante | 5 | 6 |
| grangou | 7 | 7 | grangŏ | 6 | 7 |
| bouch | 5 | 5 | bŏš | 3 | 5 |
| sandwich | 8 | 8 | sandwiš | 7 | 8 |
| gourdet | 7 | 7 | gŏrdet | 6 | 7 |

Dans tous les cas, **le nombre d'octets UTF-8 reste identique**, alors
que le nombre de caractères diminue : š, ŏ et ŋ sont des caractères
« Latin étendu-A » codés sur 2 octets en UTF-8, exactement comme les deux
lettres ASCII (`ch`, `ou`, `ng`) qu'ils remplacent. Le gain scriptural
$\gamma$ (mesuré en caractères) **ne se traduit donc par aucun gain en
octets**.

**Confirmation avec trois tokeniseurs réels, sur les 8 textes complets du
corpus de validation** (`fertilite_tokenizers.py`, fourni avec ce
document). Trois familles délibérément différentes, pas trois variantes
d'une même bibliothèque : `cl100k_base` et `o200k_base` sont deux BPE
byte-level d'OpenAI (GPT-3.5/4 et GPT-4o/GPT-5 respectivement), tandis
que NLLB-200 (`facebook/nllb-200-distilled-600M`, Meta) est un tokeniseur
SentencePiece/unigramme entraîné sur 200 langues **dont le créole
haïtien** (`hat_Latn`) — le seul des trois dont le vocabulaire a pu voir
du vrai texte créole 1979 pendant son entraînement.

| Tokeniseur | $\overline{\text{Fert}}_{1979}$ (n=8) | $\overline{\text{Fert}}_{\text{AAC}}$ (n=8) | $\Delta$ moyen | $\Delta$ min–max sur les 8 textes |
|---|---:|---:|---:|---:|
| `cl100k_base` | 2,066 (σ=0,272) | 2,448 (σ=0,199) | **+18,4 %** | +5,5 % à +42,6 % |
| `o200k_base` | 1,667 (σ=0,267) | 2,072 (σ=0,160) | **+24,3 %** | +6,8 % à +51,2 % |
| NLLB-200 | 1,486 (σ=0,270) | 1,751 (σ=0,174) | **+17,8 %** | +4,8 % à +42,9 % |

**Résultat net : $\text{Fert}_{\text{AAC}} > \text{Fert}_{1979}$ sur les
24 observations (8 textes × 3 tokeniseurs), sans une seule exception.**
Sous l'hypothèse nulle « pas d'effet systématique » (chaque observation
aurait 50 % de chances d'aller dans un sens ou l'autre), la probabilité
d'obtenir 24 résultats positifs sur 24 par hasard est $0{,}5^{24} \approx 6\times10^{-8}$,
soit environ 1 chance sur 16,8 millions — ce n'est donc pas un artefact
d'un tokeniseur particulier ni d'un texte particulier. Fait notable :
même **NLLB-200**, le tokeniseur le plus susceptible d'avoir "vu" du
créole authentique à l'entraînement, montre le même effet (+17,8 %) que
les deux tokeniseurs anglo-centrés — ce qui pointe vers une cause
structurelle (š/ŏ/ŋ sont des points de code rares dans *tous* les corpus
d'entraînement, créole inclus, faute de textes déjà écrits en AAC) plutôt
que vers un simple biais anglo-centré corrigible en changeant de
tokeniseur.

Le détail token par token (disponible via le script) confirme le
mécanisme déjà identifié sur l'échantillon pilote : `š` forme souvent un
seul token, `ŏ` se décompose plus systématiquement — cohérent avec le
fait que `ŏ` porte, à lui seul, environ 62 % des occurrences de lettres
atomiques du corpus (`letter-frequency-analysis.md` §1), donc l'essentiel
de la perte de fertilité mesurée ici.

**Ce résultat remplace désormais l'estimation par octets comme preuve
principale** : $\text{Fert}$ est mesuré, pas hypothétique, sur le corpus
de validation complet, avec trois tokeniseurs indépendants, un effet
parfaitement consistant en signe, et une ampleur (+18 % à +24 % de
tokens en moyenne) à mettre en regard du gain scriptural $\gamma$
(moyenne 5,7 %, §1.3) : l'AAC économise des caractères mais coûte
nettement plus de tokens — à peu près un ordre de grandeur de plus que
ce qu'il économise en caractères.

---

## 3. Positionnement linguistique et décision

### 3.1 Distinctivité — $D(g) = \log_2 \dfrac{P(g \mid \text{créole})}{P(g \mid \text{fr})}$

**Lecture.** Rapport de vraisemblance (en bits) entre la probabilité
d'observer le graphème $g$ dans un corpus créole vs. un corpus français
de référence. $D(g) > 0$ signifie que $g$ est plus caractéristique du
créole que du français (argument visuel/identitaire en faveur de l'AAC :
un texte truffé de š/ŏ/ŋ ne peut pas être confondu avec du français, alors
que `ch`/`ou`/`ng` seuls le peuvent).

**Points à documenter avant calcul.** (1) Nécessite deux corpus de
référence comparables en taille et en registre — le corpus de 8 textes de
`corpus.py` est probablement trop petit et trop spécifique (citations,
proverbes) pour estimer $P(\cdot\mid\text{créole})$ de façon fiable ; (2)
pour $g \notin$ corpus français (cas de š, ŏ, ŋ, qui n'existent
simplement pas en français), $P(g\mid\text{fr}) = 0$ et $D(g)$ diverge
vers $+\infty$ — un lissage (Laplace/add-one, ou plancher minimal) est
indispensable et doit être choisi et documenté, sinon la valeur n'a pas
de sens comparatif.

### 3.2 Décision multicritère — $J(g) = \displaystyle\sum_i w_i C_i - w_4 D$

**Lecture.** Combine linéairement plusieurs coûts $C_i$ (candidats
naturels : $C_{\text{mém}}$, $C_{\text{moteur}}$, éventuellement $\Omega$)
avec des poids $w_i$, moins un terme de bénéfice $w_4 D$ (la
distinctivité réduit le score global, qu'on cherche vraisemblablement à
minimiser pour choisir entre plusieurs réformes graphiques candidates).

**C'est la formule la moins spécifiée du lot, par nature.** Contrairement
aux dix autres, $J(g)$ n'est pas une mesure empirique mais un **choix
normatif** : rien dans les données ne dicte quels $C_i$ entrer dans la
somme, ni la valeur des poids $w_i$. Avant tout calcul, le mémoire doit
fixer explicitement (a) la liste des $C_i$ retenus parmi les grandeurs
ci-dessus, (b) leurs poids, et (c) une justification de ces poids
(enquête auprès d'usagers, jugement d'expert, ou poids égaux par défaut).
Sans cela, $J(g)$ ne peut être présenté comme un résultat objectif du
mémoire, seulement comme un exemple illustratif d'agrégation possible.

---

## 4. Impact et validation

### 4.1 Impact écologique — $E_{\text{papier}} = \gamma V \rho$

**Lecture.** $\gamma$ = gain scriptural (§1.3, déjà défini et mesuré), $V$
= volume de documents produits dans le domaine visé (ex. pages de manuels
scolaires imprimées par an), $\rho$ = facteur de conversion
caractères économisés → impact physique.

**$\rho$ n'est pas une seule constante empirique : c'est un produit de
plusieurs hypothèses qui doivent être déballées séparément**, soit
$\rho = \rho_a \cdot \rho_b \cdot \rho_c$ :

**$\rho_a$ — caractères économisés → pages économisées.** Dépend de la
densité de caractères par page (variable selon la mise en page du
document visé par le mémoire : manuel scolaire, roman, presse...). Aucune
source externe ne peut fixer cette valeur à la place du mémoire : c'est
un paramètre du corpus cible, à documenter explicitement (nombre moyen de
caractères par page des documents réellement concernés par la réforme),
pas une constante physique comme les deux suivantes.

**$\rho_b$ — pages économisées → grammes de papier.** Pour une page A4 à
80 g/m² (grammage de bureau standard), $\rho_b = 5\,\text{g/feuille}$,
exactement : $0{,}21\,\text{m} \times 0{,}297\,\text{m} = 0{,}06237\,\text{m}^2$,
soit $1/16$ d'un A0 (1 m²), donc $0{,}06237 \times 80 \approx 4{,}99 \approx 5\,\text{g}$
— un résultat d'arithmétique pure de la norme ISO 216, pas une
approximation.

**$\rho_c$ — grammes de papier → impact écologique.** Contrairement à
$\rho_a$ et $\rho_b$, il n'y a pas une seule bonne unité de sortie ; selon
l'impact que le mémoire veut communiquer, $\rho_c$ prend l'une des
valeurs sourcées suivantes (toutes ramenées ici au gramme de papier pour
rester comparables, mais voir les limites plus bas) :

| Sortie visée | Source | Valeur rapportée | Ramenée au gramme de papier |
|---|---|---|---:|
| CO₂e (méthode directe, par feuille) | Dias & Arroja (2012), ISO 14040/14044, berceau-client | 4,64 g CO₂e / feuille A4 | $4{,}64 / 4{,}99 \approx 0{,}930\ \text{g CO}_2\text{e/g}$ |
| CO₂e (méthode par tonne) | Sun, Wang, Shi & Klemeš (2018), *Renewable and Sustainable Energy Reviews* 92, 828-833, berceau-usine — chiffre rapporté par Furszyfer Del Rio *et al.* (2022), *Renewable and Sustainable Energy Reviews* 167, 112706, qui le cite sans en être la source primaire | ≈ 951 kg CO₂e / tonne de papier | $951\,000 / 1\,000\,000 \approx 0{,}951\ \text{g CO}_2\text{e/g}$ |
| Masse de bois (principal) | IEA (2007), *Tracking industrial Energy Efficiency and CO2 Emissions* — cité dans Furszyfer Del Rio *et al.* (2022) | 2,2 t bois / t papier kraft blanchi | $2{,}2 \times 10^{-6}\ \text{t bois/g}$ |
| Volume de bois (recoupement) | FAO, ≈ 4,25 m³ bois rond / tonne de pâte chimique | — | $4{,}25 \times 10^{-6}\ \text{m}^3\text{/g}$ *(de pâte, pas de papier fini — voir limite ci-dessous)* |
| Nombre d'arbres | Conservatree (calcul des années 1970) | 24 arbres / tonne (papier impression/écriture, procédé kraft) | $2{,}4 \times 10^{-5}\ \text{arbre/g}$ |

**La masse de bois a désormais deux sources indépendantes qui se recoupent.**
Contrairement au facteur FAO (pâte, pas papier fini — voir limite ci-dessous),
le ratio IEA de 2,2 t bois/t papier est un rapport **direct** bois → papier
kraft, sans étape intermédiaire ni hypothèse sur le taux de charges
minérales : c'est donc la valeur principale à retenir pour la masse de
bois, d'autant qu'elle porte sur le même procédé (kraft) que la ligne
« arbres » de Conservatree juste en dessous — cohérence interne entre les
deux lignes. Le facteur FAO reste utile comme recoupement en *volume*
(m³), mais nécessite une densité du bois pour être comparé à la valeur
IEA (en masse) :

| Densité de bois supposée | FAO → t bois / t pâte | IEA → t bois / t papier | Écart |
|---|---:|---:|---:|
| 0,40 t/m³ | 1,70 | 2,2 | −23 % |
| 0,50 t/m³ | 2,12 | 2,2 | −3 % |
| 0,55 t/m³ | 2,34 | 2,2 | +6 % |

Pour une densité plausible de bois rond résineux (0,50–0,55 t/m³), les
deux sources indépendantes se recoupent à quelques % près — une
corroboration raisonnable, mais qui repose sur une densité choisie par
nous plutôt que sourcée, donc à présenter comme un recoupement
illustratif et non comme une preuve.

**Deux sources indépendantes de CO₂e se recoupent, c'est une bonne
nouvelle pour la robustesse de $\rho_c$** : $0{,}930$ et $0{,}951\ \text{g CO}_2\text{e/g}$
ne s'écartent que d'environ 2 %, malgré des méthodologies et des
périmètres différents (une LCA précise du papier de bureau portugais vs.
une moyenne mondiale « tous types de papier confondus », rapportée par
une revue de littérature plutôt que mesurée directement par ses auteurs).
Ce n'est toutefois pas une identité à prendre pour acquise dans une
future version de ce document : les deux valeurs restent deux mesures
différentes qui se corroborent, pas une seule mesure vérifiée deux fois.

**Limites qui restent, propres à chaque ligne du tableau :**
- La ligne « volume de bois » convertit des **grammes de pâte chimique**,
  pas des grammes de papier fini — un papier contenant des charges
  minérales (carbonate de calcium, kaolin...) demande moins de pâte par
  tonne de papier produit que ce facteur ne le suggère. C'est
  explicitement une valeur haute/conservatrice, pas une estimation
  centrale.
- La ligne « nombre d'arbres » mélange des sources dont l'ancrage précis
  diffère : 24 arbres/tonne est bien documenté pour le papier
  impression/écriture par procédé kraft chimique (Conservatree, calcul
  des années 1970 attribué à un travail universitaire repris par
  Conservatree), mais le chiffre de 17 arbres parfois cité en complément
  est une **moyenne tous grades de papier confondus**, pas une valeur
  spécifique au papier journal — le papier journal a sa propre valeur
  publiée (12 arbres/tonne, procédé mécanique, plus économe en bois). Le
  mémoire doit choisir la valeur correspondant au type de document
  réellement visé par la réforme (manuel scolaire ≈ papier
  impression/écriture ≈ 24 arbres/tonne est probablement le bon choix),
  pas prendre 17 par défaut sans vérifier qu'il s'applique au bon type de
  papier.
- La valeur FAO de 4,25 m³/tonne n'a pas pu être retracée jusqu'à une
  publication FAO 2024 précise lors de cette vérification — elle est
  cohérente avec la fourchette de facteurs FAO/UNECE publiés pour la pâte
  chimique (3,35 à 5,22 m³/tonne selon l'année et la méthode), donc
  numériquement plausible, mais la référence exacte reste à confirmer
  avant publication dans le mémoire.

Avec ces chiffres, $\rho$ cesse d'être un facteur noir opaque : seul
$\rho_a$ reste un paramètre à fournir par le mémoire (densité de
caractères par page du corpus cible), $\rho_b$ est une constante exacte
de la norme ISO 216, et $\rho_c$ est un choix documenté parmi quatre
sorties possibles, chacune sourcée et accompagnée de sa limite propre —
plutôt que de présenter $E_{\text{papier}}$ comme découlant directement
et simplement de $\gamma$.

### 4.2 Validation statistique — $t = \dfrac{\hat{\gamma}}{\hat{\sigma}/\sqrt{n}}$

**Lecture.** Statistique de test (Student, $n-1$ degrés de liberté) pour
l'hypothèse nulle $H_0 : \gamma = 0$ (« la réforme ne produit aucun gain
en moyenne »), à partir de la moyenne $\hat\gamma$ et de l'écart-type
$\hat\sigma$ du gain mesurés sur $n$ textes.

**Vérification de cohérence avec les chiffres déjà publiés.** Les valeurs
brutes par texte de $\gamma$ ne sont pas dans les documents disponibles
ici (seules les densités $D$ par texte le sont, dans
`letter-frequency-analysis.md` §1 — $D$ et $\gamma$ sont deux grandeurs
différentes, qui ne doivent pas être interverties), mais
`letter-frequency-analysis.md` rapporte déjà $\hat\gamma = 5{,}7\,\%$ avec
un IC95 % $[3{,}8\,\%\,;\,7{,}5\,\%]$ sur $n=8$ textes. On peut vérifier
que ces deux chiffres sont mutuellement cohérents en reconstruisant
$\hat\sigma$ à partir de la largeur de l'intervalle
($\text{IC95\%} = \hat\gamma \pm t_{0{,}975,\,7}\cdot\hat\sigma/\sqrt n$,
avec $t_{0{,}975,\,7} \approx 2{,}365$) :

$$\hat\sigma \approx \frac{(7{,}5-3{,}8)/2}{2{,}365}\sqrt{8} \approx 2{,}21\,\%
\quad\Longrightarrow\quad
t = \frac{5{,}7}{2{,}21/\sqrt 8} \approx 7{,}29 \;(\text{df}=7,\; p \approx 0{,}0002)$$

C'est cohérent avec un IC95 % qui exclut largement 0, et confirme que le
gain mesuré est statistiquement significatif — mais c'est une
**reconstruction à partir de l'intervalle déjà publié**, pas un calcul
indépendant sur les $n=8$ valeurs brutes de $\gamma$. Si ces valeurs
brutes par texte sont disponibles dans `test_corpus_diversity.py`, $t$
devrait être recalculé directement dessus plutôt que déduit de l'IC95 %,
qui n'est lui-même qu'un intervalle *dérivé* de $t$ — utiliser l'un pour
retrouver l'autre est un test de cohérence utile mais circulaire si c'est
la seule vérification faite.

---

## Récapitulatif : ce qui est prêt, ce qui reste à faire

| Grandeur | Déjà calculable avec le code existant ? | Principal point à trancher avant implémentation |
|---|---|---|
| $\gamma$ | Oui — `acc_converter.py`/`.js` | — |
| $\Omega$ (version simple) | Oui — via `diff_summary()` | choix de $\text{Op}(s)$ binaire vs gradué |
| $t$ | Partiellement — par reconstruction depuis l'IC95 % déjà publié | obtenir les $n=8$ valeurs brutes de $\gamma$ |
| $\text{Fert}$ | **Oui** — mesuré sur les 8 textes du corpus avec 3 tokeniseurs (`cl100k_base`, `o200k_base`, NLLB-200) ; AAC plus fertile que 1979 dans 24/24 cas (+17,8 % à +24,3 % selon le tokeniseur, §2.3) | tester aussi sur le tokeniseur précis visé par le mémoire s'il diffère des trois ci-dessus |
| $B$ | Non | sens de $T$ : phonème→graphies ou l'inverse |
| $E[\gamma]$ | Non (mais démontré ci-dessus comme une identité exacte de $\gamma$) | normaliser $f_k$ par $n_{1979}$, pas par mot |
| $C_{\text{mém}}$ | Non | granularité de $R$ (règles seules ou + exceptions lexicales) |
| $C_{\text{moteur}}$ | Non | définir $m(g)$ (convention de tracé manuscrit) |
| $D(g)$ | Non | corpus français de référence + lissage |
| $J(g)$ | Non | normatif par nature — liste et poids des $C_i$ à fixer |
| $E_{\text{papier}}$ | Partiellement — $\rho_b$ (exact, ISO 216) et $\rho_c$ (4 sorties sourcées, CO₂e recoupé à 2 % par deux sources indépendantes) décomposés et vérifiés en §4.1 | fournir $\rho_a$ (densité caractères/page du corpus cible) ; confirmer la référence FAO 2024 exacte pour le facteur bois ; choisir la bonne valeur « arbres » selon le type de papier visé |
