Évaluation mathématique du mémoire AAC : formules à ajouter et justification
1. Pourquoi mathématiser ce mémoire ?
   Le mémoire repose actuellement sur des arguments qualitatifs (parcimonie, transparence, opacité) et quelques mesures empiriques simples (9,3 % de gain sur un corpus unique). Pour passer d'une proposition d'ingénierie linguistique à une théorie falsifiable, il faut formaliser :

les notions clés (atomicité, opacité, bi-univocité) ;

les gains (scriptural, cognitif, tokenistique) ;

les coûts (transition, apprentissage) ;

les décisions (quel graphème choisir).

Une évaluation mathématique permet de comparer objectivement l'AAC à 1979 et à Gourdet (2022), et de prédire les effets avant expérimentation.

2. Formalisation du système graphique
   2.1 Définitions de base
   Soit :

P
=
{
p
1
,
…
,
p
N
}
P={p
1
​
,…,p
N
​
} l'ensemble des phonèmes du créole (
N
=
30
N=30, annexe phonologique).

G
=
{
g
1
,
…
,
g
M
}
G={g
1
​
,…,g
M
​
} l'ensemble des graphèmes (ou séquences graphiques) utilisés.

Une correspondance est une relation
R
⊆
P
×
G
R⊆P×G.

Fonction de transcription :
T
:
P
→
P
(
G
)
T:P→P(G) (ensemble des graphèmes pouvant encoder un phonème).

Fonction de lecture :
L
:
G
→
P
(
P
)
L:G→P(P).

2.2 Indice de bi-univocité
Le principe fondateur (« un son, un signe ») se mesure par :

B
=
1
N
∑
i
=
1
N
1
∣
T
(
p
i
)
∣
∈
[
0
,
1
]
B=
N
1
​

i=1
∑
N
​

∣T(p
i
​
)∣
1
​
∈[0,1]
B
=
1
B=1 : bi-univocité parfaite (un seul graphème par phonème).

B
=
1
/
N
B=1/N : chaos total.

Variante symétrique (ambiguïté de lecture) :

B
′
=
1
M
∑
j
=
1
M
1
∣
L
(
g
j
)
∣
B
′
=
M
1
​

j=1
∑
M
​

∣L(g
j
​
)∣
1
​

Indice global :
B
tot
=
B
⋅
B
′
B
tot
​
=
B⋅B
′

​
.

Application :

1979 :
c
h
ch et
o
u
ou ont 1 graphème pour 1 phonème, mais
/
u
/
/u/ a 2 (ou, oun) →
B
<
1
B<1.

AAC : par construction
B
=
1
B=1 pour les 24 lettres atomiques (les nasales sont des combinaisons).

2.3 Taux d'opacité
Pour une séquence
s
=
c
1
c
2
…
c
k
s=c
1
​
c
2
​
…c
k
​
(suite de caractères), on définit :

Op
(
s
)
=
1
−
H
(
L
(
s
)
)
log
⁡
2
∣
P
∣
Op(s)=1−
log
2
​
∣P∣
H(L(s))
​

où
H
H est l'entropie de Shannon de la distribution des phonèmes pouvant être lus à partir de
s
s.

Op
(
s
)
=
0
Op(s)=0 : séquence transparente (lecture unique et prévisible).

Op
(
s
)
=
1
Op(s)=1 : séquence opaque (aucune information).

Application :

a
n
an :
L
(
a
n
)
=
{
/
a
~
/
}
L(an)={/
a
~
/} →
Op
=
0
Op=0 (transparent).

c
h
ch :
L
(
c
h
)
=
{
/
ʃ
/
}
L(ch)={/ʃ/} mais
c
c et
h
h isolés ont d'autres valeurs → opacité positionnelle ; il faut une opacité conditionnelle :

Op
(
s
)
=
1
−
I
(
s
;
p
)
log
⁡
2
∣
P
∣
Op(s)=1−
log
2
​
∣P∣
I(s;p)
​

où
I
(
s
;
p
)
I(s;p) est l'information mutuelle entre la séquence et le phonème cible.

Opacité globale du système :

Ω
=
∑
s
∈
S
opaque
f
(
s
)
⋅
Op
(
s
)
Ω=
s∈S
opaque
​

∑
​
f(s)⋅Op(s)
où
f
(
s
)
f(s) est la fréquence de
s
s dans le corpus.

3. Gain scriptural : formalisation
   3.1 Définition du gain
   Pour un texte
   X
   X de
   n
   n caractères, le gain est :

γ
=
n
1979
−
n
AAC
n
1979
=
1
−
n
AAC
n
1979
γ=
n
1979
​

n
1979
​
−n
AAC
​

​
=1−
n
1979
​

n
AAC
​

​

Décomposition par substitution :

γ
=
∑
k
∈
{
ch, ou, oun, ng
}
f
k
⋅
Δ
k
γ=
k∈{ch, ou, oun, ng}
∑
​
f
k
​
⋅Δ
k
​

où :

f
k
f
k
​
= fréquence du digramme/trigramme
k
k dans le corpus (occurrences par caractère).

Δ
k
Δ
k
​
= économie par occurrence (
Δ
c
h
=
1
Δ
ch
​
=1,
Δ
o
u
=
1
Δ
ou
​
=1,
Δ
o
u
n
=
2
Δ
oun
​
=2,
Δ
n
g
=
1
Δ
ng
​
=1).

Application au corpus Depestre :

f
c
h
=
4
/
114
f
ch
​
=4/114,
f
o
u
=
8
/
114
f
ou
​
=8/114,
f
n
g
=
1
/
114
f
ng
​
=1/114.

γ
=
(
4
+
8
+
1
)
/
114
=
13
/
114
≈
11
,
4
%
γ=(4+8+1)/114=13/114≈11,4% (théorique).

Mesuré : 9,3 % (écart dû aux espaces et à la ponctuation).

3.2 Gain attendu sur un corpus de taille
n
n
E
[
γ
]
=
∑
k
E
[
f
k
]
⋅
Δ
k
E[γ]=
k
∑
​
E[f
k
​
]⋅Δ
k
​

Avec un intervalle de confiance :

IC
95
%
(
γ
)
=
γ
^
±
1
,
96
⋅
σ
γ
n
IC
95%
​
(γ)=
γ
^
​
±1,96⋅
n
​

σ
γ
​

​

Recommandation : calculer
σ
γ
σ
γ
​
sur plusieurs textes (littéraire, journalistique, administratif) pour valider les 9–13 %.

4. Charge cognitive : modèle quantitatif
   4.1 Charge mnémotechnique
   Soit
   U
   U l'ensemble des unités à mémoriser (lettres + règles).

C
m
e
ˊ
m
=
α
∣
U
∣
+
β
∣
R
∣
C
m
e
ˊ
m
​
=α∣U∣+β∣R∣
où :

∣
U
∣
∣U∣ = nombre d'unités atomiques.

∣
R
∣
∣R∣ = nombre de règles de composition.

α
,
β
α,β = poids cognitifs (à calibrer expérimentalement).

Application :

1979 :
∣
U
∣
=
32
∣U∣=32,
∣
R
∣
≈
0
∣R∣≈0 →
C
≈
32
α
C≈32α.

AAC :
∣
U
∣
=
24
∣U∣=24,
∣
R
∣
=
3
∣R∣=3 (nasalisation, accent, semi-voyelles) →
C
≈
24
α
+
3
β
C≈24α+3β.

Gain :
Δ
C
=
8
α
−
3
β
ΔC=8α−3β. Si
α
>
0
,
375
β
α>0,375β, l'AAC est plus économique.

4.2 Coût du tracé manuscrit
Pour un graphème
g
g tracé en
m
(
g
)
m(g) gestes moteurs :

C
moteur
=
∑
g
f
(
g
)
⋅
m
(
g
)
⋅
τ
C
moteur
​
=
g
∑
​
f(g)⋅m(g)⋅τ
où
τ
≈
80
–
120
τ≈80–120 ms par geste (section 4.2.2).

Application :

c
h
ch :
m
=
5
–
7
m=5–7 gestes.

s
ˇ
s
ˇ
:
m
=
2
m=2 gestes (corps du s + caron).

Gain par occurrence :
Δ
m
≈
3
–
5
Δm≈3–5 gestes →
Δ
C
≈
240
–
600
ΔC≈240–600 ms.

5. Tokenisation : modèle informationnel
   5.1 Fertilité tokenistique
   Pour une langue
   ℓ
   ℓ et un tokeniseur
   T
   T :

Fert
(
ℓ
)
=
#
tokens
(
T
,
X
ℓ
)
#
mots
(
X
ℓ
)
Fert(ℓ)=
#mots(X
ℓ
​
)
#tokens(T,X
ℓ
​
)
​

Objectif : minimiser
Fert
Fert.

Lien avec l'orthographe : plus une séquence est partagée avec une langue dominante (français), plus le tokeniseur la fusionne selon les statistiques de cette langue.

5.2 Indice de distinctivité
Pour un graphème
g
g :

D
(
g
)
=
−
log
⁡
2
P
(
g
∣
fr
)
+
log
⁡
2
P
(
g
∣
cr
e
ˊ
ole
)
D(g)=−log
2
​
P(g∣fr)+log
2
​
P(g∣cr
e
ˊ
ole)
D
(
g
)
>
0
D(g)>0 :
g
g est marqueur de créole.

D
(
g
)
≤
0
D(g)≤0 :
g
g est ambigu (partagé avec le français).

Application :

c
h
ch : présent en français →
D
≈
0
D≈0.

s
ˇ
,
o
ˉ
,
η
s
ˇ
,
o
ˉ
,η : absents du français →
D
≫
0
D≫0.

Indice global :

D
syst
e
ˋ
me
=
∑
g
∈
G
f
(
g
)
⋅
D
(
g
)
D
syst
e
ˋ
me
​
=
g∈G
∑
​
f(g)⋅D(g)
6. Décision : quel graphème choisir ?
   6.1 Fonction de coût multicritère
   Pour chaque graphème candidat
   g
   g :

J
(
g
)
=
w
1
⋅
C
tech
(
g
)
+
w
2
⋅
C
appr
(
g
)
+
w
3
⋅
C
frappe
(
g
)
−
w
4
⋅
D
(
g
)
J(g)=w
1
​
⋅C
tech
​
(g)+w
2
​
⋅C
appr
​
(g)+w
3
​
⋅C
frappe
​
(g)−w
4
​
⋅D(g)
où :

C
tech
C
tech
​
: coût technique (Unicode, fonte, clavier).

C
appr
C
appr
​
: coût d'apprentissage.

C
frappe
C
frappe
​
: coût de frappe mobile.

D
(
g
)
D(g) : distinctivité (bénéfice).

w
i
w
i
​
: poids à fixer par l'Académie.

Choix :
g
∗
=
arg
⁡
min
⁡
g
J
(
g
)
g
∗
=argmin
g
​
J(g).

Application :

s
ˇ
s
ˇ
vs ligature
c
h
ch :
C
tech
(
s
ˇ
)
≪
C
tech
(
ligature
)
C
tech
​
(
s
ˇ
)≪C
tech
​
(ligature) →
s
ˇ
s
ˇ
gagne.

s
ˇ
s
ˇ
vs  (point souscrit) :  car le caron est en haut (section 3.4.3).

6.2 Théorie des jeux (optionnel)
Si l'on modélise l'adoption par les locuteurs comme un jeu de coordination :

Stratégies :
{
1979
,
A
A
C
}
{1979,AAC}.

Payoff :
u
(
s
i
,
s
j
)
=
−
C
(
s
i
)
+
B
⋅
1
[
s
i
=
s
j
]
u(s
i
​
,s
j
​
)=−C(s
i
​
)+B⋅1[s
i
​
=s
j
​
].

Équilibre de Nash : deux équilibres (tous 1979, tous AAC). La transition nécessite un mécanisme de coordination (Académie, école).

7. Modèle économique et écologique
   7.1 Économie de papier
   E
   papier
   =
   γ
   ⋅
   V
   ⋅
   ρ
   E
   papier
   ​
   =γ⋅V⋅ρ
   où :

γ
γ = gain scriptural (9–13 %).

V
V = volume total (pages/an).

ρ
ρ = poids papier par page.

Application :

V
=
100
V=100 M pages,
ρ
≈
5
ρ≈5 g/page →
E
≈
50
E≈50 t/an.

7.2 CO₂ évité
E
CO
2
=
E
papier
⋅
κ
E
CO
2
​

​
=E
papier
​
⋅κ
où
κ
≈
1
,
5
–
2
κ≈1,5–2 kg CO₂/kg papier.

Arbres préservés :

N
arbres
=
E
papier
μ
N
arbres
​
=
μ
E
papier
​

​

avec
μ
≈
0
,
05
μ≈0,05 t/papier/arbre.

8. Validation expérimentale : plan statistique
   8.1 Test d'hypothèse sur le gain
   H
   0
   H
   0
   ​
   :
   γ
   =
   0
   γ=0.

H
1
H
1
​
:
γ
>
0
γ>0.

Statistique :

t
=
γ
^
−
0
σ
^
γ
/
n
t=
σ
^

γ
​
/
n
​

γ
^
​
−0
​

Avec
n
n textes. Rejet de
H
0
H
0
​
si
t
>
t
1
−
α
t>t
1−α
​
.

8.2 Taille d'échantillon requise
n
≥
(
z
1
−
α
+
z
1
−
β
γ
/
σ
)
2
n≥(
γ/σ
z
1−α
​
+z
1−β
​

​
)
2

Pour
γ
=
0
,
10
γ=0,10,
σ
=
0
,
03
σ=0,03,
α
=
0
,
05
α=0,05,
β
=
0
,
20
β=0,20 →
n
≈
8
n≈8 textes.

Recommandation : 30 textes (10 par registre) pour robustesse.

9. Synthèse : formules minimales à ajouter
   Section	Formule	Rôle
   2.2
   B
   =
   1
   N
   ∑
   1
   /
   ∥
   T
   (
   p
   i
   )
   ∥
   B=
   N
   1
   ​
   ∑1/∥T(p
   i
   ​
   )∥	Mesurer la bi-univocité
   2.3
   Ω
   =
   ∑
   f
   (
   s
   )
   Op
   (
   s
   )
   Ω=∑f(s)Op(s)	Quantifier l'opacité
   3.1
   γ
   =
   1
   −
   n
   AAC
   /
   n
   1979
   γ=1−n
   AAC
   ​
   /n
   1979
   ​
   Gain scriptural
   3.2
   E
   [
   γ
   ]
   =
   ∑
   f
   k
   Δ
   k
   E[γ]=∑f
   k
   ​
   Δ
   k
   ​
   Décomposition du gain
   4.1
   C
   m
   e
   ˊ
   m
   =
   α
   ∥
   U
   ∥
+
β
∥
R
∥
C
m
e
ˊ
m
​
=α∥U∥+β∥R∥	Charge cognitive
4.2
C
moteur
=
∑
f
(
g
)
m
(
g
)
τ
C
moteur
​
=∑f(g)m(g)τ	Coût du tracé
5.1
Fert
=
#
tokens
/
#
mots
Fert=#tokens/#mots	Fertilité tokenistique
5.2
D
(
g
)
=
log
⁡
2
P
(
g
∥
cr
e
ˊ
ole
)
P
(
g
∥
fr
)
D(g)=log
2
​

P(g∥fr)
P(g∥cr
e
ˊ
ole)
​
Distinctivité
6.1
J
(
g
)
=
∑
w
i
C
i
−
w
4
D
J(g)=∑w
i
​
C
i
​
−w
4
​
D	Décision multicritère
7.1
E
papier
=
γ
V
ρ
E
papier
​
=γVρ	Impact écologique
8.1
t
=
γ
^
/
(
σ
^
/
n
)
t=
γ
^
​
/(
σ
^
/
n
​
)	Validation statistique
10. Pourquoi ces formules et pas d'autres ?
    Elles sont falsifiables : chaque formule produit une prédiction testable (ex.
    γ
    ∈
    [
    9
    %
    ,
    13
    %
    ]
    γ∈[9%,13%]).

Elles sont comparables : on peut calculer
B
B,
Ω
Ω,
γ
γ pour 1979, Gourdet et AAC.

Elles sont minimales : pas de modèle inutilement complexe (pas de réseaux de neurones, pas de théorie des catégories).

Elles couvrent les 4 axes du mémoire : linguistique (
B
,
Ω
B,Ω), pédagogie (
C
m
e
ˊ
m
,
C
moteur
C
m
e
ˊ
m
​
,C
moteur
​
), TALN (
Fert
,
D
Fert,D), économie (
E
E).

Elles respectent l'esprit de parcimonie de l'AAC : peu de paramètres, interprétables, calibrés sur corpus.

11. Limites et extensions possibles
    Calibration :
    α
    ,
    β
    ,
    τ
    ,
    w
    i
    α,β,τ,w
    i
    ​
    doivent être estimés empiriquement (études pilotes).

Corpus : les formules supposent un corpus représentatif ; il faut stratifier par registre.

Dynamique : on pourrait ajouter un modèle épidémiologique d'adoption (
d
A
d
t
=
β
A
(
1
−
A
)
−
δ
A
dt
dA
​
=βA(1−A)−δA) pour la transition.

Théorie de l'information : on pourrait calculer l'entropie conditionnelle
H
(
P
∣
G
)
H(P∣G) et
H
(
G
∣
P
)
H(G∣P) pour mesurer l'efficacité informationnelle du code.

Conclusion : l'ajout de ces formules transforme le mémoire d'un essai argumenté en une proposition scientifique quantifiée, prête à être testée, comparée et éventuellement réfutée. C'est exactement ce que l'Académie du Créole Haïtien attend d'une réforme : des preuves, pas seulement des principes.