# Évaluation mathématique du mémoire AAC — Formules à ajouter et justification

## 1. Pourquoi mathématiser ce mémoire ?

Le mémoire repose actuellement sur des **arguments qualitatifs** (parcimonie, transparence, opacité) et quelques **mesures empiriques simples** (9,3 % de gain sur un corpus unique). Pour passer d'une **proposition d'ingénierie linguistique** à une **théorie falsifiable**, il faut formaliser :

- les **notions clés** (atomicité, opacité, bi-univocité) ;
- les **gains** (scriptural, cognitif, tokenistique) ;
- les **coûts** (transition, apprentissage) ;
- les **décisions** (quel graphème choisir).

Une évaluation mathématique permet de **comparer objectivement** l'AAC à 1979 et à Gourdet (2022), et de **prédire** les effets avant expérimentation.

---

## 2. Formalisation du système graphique

### 2.1 Définitions de base

Soit :
- \( P = \{p_1, \dots, p_N\} \) l'ensemble des **phonèmes** du créole (\( N = 30 \), annexe phonologique).
- \( G = \{g_1, \dots, g_M\} \) l'ensemble des **graphèmes** (ou séquences graphiques) utilisés.
- Une **correspondance** est une relation \( R \subseteq P \times G \).

**Fonction de transcription** : \( T : P \to \mathcal{P}(G) \) (ensemble des graphèmes pouvant encoder un phonème).

**Fonction de lecture** : \( L : G \to \mathcal{P}(P) \).

### 2.2 Indice de bi-univocité

Le principe fondateur (« un son, un signe ») se mesure par :

\[
B = \frac{1}{N} \sum_{i=1}^{N} \frac{1}{|T(p_i)|} \quad \in [0,1]
\]

- \( B = 1 \) : bi-univocité parfaite (un seul graphème par phonème).
- \( B = 1/N \) : chaos total.

**Variante symétrique** (ambiguïté de lecture) :

\[
B' = \frac{1}{M} \sum_{j=1}^{M} \frac{1}{|L(g_j)|}
\]

**Indice global** : \( B_{\text{tot}} = \sqrt{B \cdot B'} \).

**Application** :
- 1979 : \( ch \) et \( ou \) ont 1 graphème pour 1 phonème, mais \( /u/ \) a 2 (ou, oun) → \( B < 1 \).
- AAC : par construction \( B = 1 \) pour les 24 lettres atomiques (les nasales sont des combinaisons).

### 2.3 Taux d'opacité

Pour une séquence \( s = c_1 c_2 \dots c_k \) (suite de caractères), on définit :

\[
\text{Op}(s) = 1 - \frac{H(L(s))}{\log_2 |P|}
\]

où \( H \) est l'entropie de Shannon de la distribution des phonèmes pouvant être lus à partir de \( s \).

- \( \text{Op}(s) = 0 \) : séquence **transparente** (lecture unique et prévisible).
- \( \text{Op}(s) = 1 \) : séquence **opaque** (aucune information).

**Application** :
- \( an \) : \( L(an) = \{/ã/\} \) → \( \text{Op} = 0 \) (transparent).
- \( ch \) : \( L(ch) = \{/ʃ/\} \) mais \( c \) et \( h \) isolés ont d'autres valeurs → opacité **positionnelle** ; il faut une **opacité conditionnelle** :

\[
\text{Op}(s) = 1 - \frac{I(s ; p)}{\log_2 |P|}
\]

où \( I(s ; p) \) est l'information mutuelle entre la séquence et le phonème cible.

**Opacité globale du système** :

\[
\Omega = \sum_{s \in \mathcal{S}_{\text{opaque}}} f(s) \cdot \text{Op}(s)
\]

où \( f(s) \) est la fréquence de \( s \) dans le corpus.

---

## 3. Gain scriptural : formalisation

### 3.1 Définition du gain

Pour un texte \( X \) de \( n \) caractères, le gain est :

\[
\gamma = \frac{n_{1979} - n_{\text{AAC}}}{n_{1979}} = 1 - \frac{n_{\text{AAC}}}{n_{1979}}
\]

**Décomposition par substitution** :

\[
\gamma = \sum_{k \in \{\text{ch, ou, oun, ng}\}} f_k \cdot \Delta_k
\]

où :
- \( f_k \) = fréquence du digramme/trigramme \( k \) dans le corpus (occurrences par caractère).
- \( \Delta_k \) = économie par occurrence (\( \Delta_{ch} = 1 \), \( \Delta_{ou} = 1 \), \( \Delta_{oun} = 2 \), \( \Delta_{ng} = 1 \)).

**Application au corpus Depestre** :
- \( f_{ch} = 4/114 \), \( f_{ou} = 8/114 \), \( f_{ng} = 1/114 \).
- \( \gamma = (4 + 8 + 1)/114 = 13/114 \approx 11,4\% \) (théorique).
- Mesuré : 9,3 % (écart dû aux espaces et à la ponctuation).

### 3.2 Gain attendu sur un corpus de taille \( n \)

\[
\mathbb{E}[\gamma] = \sum_k \mathbb{E}[f_k] \cdot \Delta_k
\]

Avec un intervalle de confiance :

\[
\text{IC}_{95\%}(\gamma) = \hat{\gamma} \pm 1,96 \cdot \frac{\sigma_\gamma}{\sqrt{n}}
\]

**Recommandation** : calculer \( \sigma_\gamma \) sur plusieurs textes (littéraire, journalistique, administratif) pour valider les 9–13 %.

---

## 4. Charge cognitive : modèle quantitatif

### 4.1 Charge mnémotechnique

Soit \( U \) l'ensemble des **unités à mémoriser** (lettres + règles).

\[
C_{\text{mém}} = \alpha |U| + \beta |R|
\]

où :
- \( |U| \) = nombre d'unités atomiques.
- \( |R| \) = nombre de règles de composition.
- \( \alpha, \beta \) = poids cognitifs (à calibrer expérimentalement).

**Application** :
- 1979 : \( |U| = 32 \), \( |R| \approx 0 \) → \( C \approx 32\alpha \).
- AAC : \( |U| = 24 \), \( |R| = 3 \) (nasalisation, accent, semi-voyelles) → \( C \approx 24\alpha + 3\beta \).

**Gain** : \( \Delta C = 8\alpha - 3\beta \). Si \( \alpha > 0,375\beta \), l'AAC est plus économique.

### 4.2 Coût du tracé manuscrit

Pour un graphème \( g \) tracé en \( m(g) \) gestes moteurs :

\[
C_{\text{moteur}} = \sum_{g} f(g) \cdot m(g) \cdot \tau
\]

où \( \tau \approx 80\text{–}120 \) ms par geste (section 4.2.2).

**Application** :
- \( ch \) : \( m = 5\text{–}7 \) gestes.
- \( š \) : \( m = 2 \) gestes (corps du s + caron).
- Gain par occurrence : \( \Delta m \approx 3\text{–}5 \) gestes → \( \Delta C \approx 240\text{–}600 \) ms.

---

## 5. Tokenisation : modèle informationnel

### 5.1 Fertilité tokenistique

Pour une langue \( \ell \) et un tokeniseur \( \mathcal{T} \) :

\[
\text{Fert}(\ell) = \frac{\#\text{tokens}(\mathcal{T}, X_\ell)}{\#\text{mots}(X_\ell)}
\]

**Objectif** : minimiser \( \text{Fert} \).

**Lien avec l'orthographe** : plus une séquence est **partagée** avec une langue dominante (français), plus le tokeniseur la fusionne selon les statistiques de cette langue.

### 5.2 Indice de distinctivité

Pour un graphème \( g \) :

\[
D(g) = -\log_2 P(g \mid \text{fr}) + \log_2 P(g \mid \text{créole})
\]

- \( D(g) > 0 \) : \( g \) est **marqueur de créole**.
- \( D(g) \leq 0 \) : \( g \) est ambigu (partagé avec le français).

**Application** :
- \( ch \) : présent en français → \( D \approx 0 \).
- \( š, \bar{o}, \eta \) : absents du français → \( D \gg 0 \).

**Indice global** :

\[
D_{\text{système}} = \sum_{g \in G} f(g) \cdot D(g)
\]

---

## 6. Décision : quel graphème choisir ?

### 6.1 Fonction de coût multicritère

Pour chaque graphème candidat \( g \) :

\[
J(g) = w_1 \cdot C_{\text{tech}}(g) + w_2 \cdot C_{\text{appr}}(g) + w_3 \cdot C_{\text{frappe}}(g) - w_4 \cdot D(g)
\]

où :
- \( C_{\text{tech}} \) : coût technique (Unicode, fonte, clavier).
- \( C_{\text{appr}} \) : coût d'apprentissage.
- \( C_{\text{frappe}} \) : coût de frappe mobile.
- \( D(g) \) : distinctivité (bénéfice).
- \( w_i \) : poids à fixer par l'Académie.

**Choix** : \( g^* = \arg\min_g J(g) \).

**Application** :
- \( \check{s} \) vs ligature \( ch \) : \( C_{\text{tech}}(\check{s}) \ll C_{\text{tech}}(\text{ligature}) \) → \( \check{s} \) gagne.
- \( \check{s} \) vs \( \d{s} \) (point souscrit) : \( C_{\text{frappe}}(\check{s}) < C_{\text{frappe}}(\d{s}) \) car le caron est en haut (section 3.4.3).

### 6.2 Théorie des jeux (optionnel)

Si l'on modélise l'adoption par les locuteurs comme un jeu de coordination :

- Stratégies : \( \{1979, AAC\} \).
- Payoff : \( u(s_i, s_j) = -C(s_i) + B \cdot \mathbb{1}[s_i = s_j] \).

**Équilibre de Nash** : deux équilibres (tous 1979, tous AAC). La transition nécessite un **mécanisme de coordination** (Académie, école).

---

## 7. Modèle économique et écologique

### 7.1 Économie de papier

\[
E_{\text{papier}} = \gamma \cdot V \cdot \rho
\]

où :
- \( \gamma \) = gain scriptural (9–13 %).
- \( V \) = volume total (pages/an).
- \( \rho \) = poids papier par page.

**Application** :
- \( V = 100 \) M pages, \( \rho \approx 5 \) g/page → \( E \approx 50 \) t/an.

### 7.2 CO₂ évité

\[
E_{\text{CO}_2} = E_{\text{papier}} \cdot \kappa
\]

où \( \kappa \approx 1,5\text{–}2 \) kg CO₂/kg papier.

**Arbres préservés** :

\[
N_{\text{arbres}} = \frac{E_{\text{papier}}}{\mu}
\]

avec \( \mu \approx 0,05 \) t/papier/arbre.

---

## 8. Validation expérimentale : plan statistique

### 8.1 Test d'hypothèse sur le gain

- \( H_0 \) : \( \gamma = 0 \).
- \( H_1 \) : \( \gamma > 0 \).

Statistique :

\[
t = \frac{\hat{\gamma} - 0}{\hat{\sigma}_\gamma / \sqrt{n}}
\]

Avec \( n \) textes. Rejet de \( H_0 \) si \( t > t_{1-\alpha} \).

### 8.2 Taille d'échantillon requise

\[
n \geq \left( \frac{z_{1-\alpha} + z_{1-\beta}}{\gamma / \sigma} \right)^2
\]

Pour \( \gamma = 0,10 \), \( \sigma = 0,03 \), \( \alpha = 0,05 \), \( \beta = 0,20 \) → \( n \approx 8 \) textes.

**Recommandation** : 30 textes (10 par registre) pour robustesse.

---

## 9. Synthèse : formules minimales à ajouter

| Section | Formule | Rôle |
|---------|---------|------|
| 2.2 | \( B = \frac{1}{N}\sum 1/\|T(p_i)\| \) | Mesurer la bi-univocité |
| 2.3 | \( \Omega = \sum f(s)\text{Op}(s) \) | Quantifier l'opacité |
| 3.1 | \( \gamma = 1 - n_{\text{AAC}}/n_{1979} \) | Gain scriptural |
| 3.2 | \( \mathbb{E}[\gamma] = \sum f_k \Delta_k \) | Décomposition du gain |
| 4.1 | \( C_{\text{mém}} = \alpha\|U\| + \beta\|R\| \) | Charge cognitive |
| 4.2 | \( C_{\text{moteur}} = \sum f(g)m(g)\tau \) | Coût du tracé |
| 5.1 | \( \text{Fert} = \#\text{tokens}/\#\text{mots} \) | Fertilité tokenistique |
| 5.2 | \( D(g) = \log_2 \frac{P(g\|\text{créole})}{P(g\|\text{fr})} \) | Distinctivité |
| 6.1 | \( J(g) = \sum w_i C_i - w_4 D \) | Décision multicritère |
| 7.1 | \( E_{\text{papier}} = \gamma V \rho \) | Impact écologique |
| 8.1 | \( t = \hat{\gamma}/(\hat{\sigma}/\sqrt{n}) \) | Validation statistique |

---

## 10. Pourquoi ces formules et pas d'autres ?

1. **Elles sont falsifiables** : chaque formule produit une prédiction testable (ex. \( \gamma \in [9\%, 13\%] \)).
2. **Elles sont comparables** : on peut calculer \( B \), \( \Omega \), \( \gamma \) pour 1979, Gourdet et AAC.
3. **Elles sont minimales** : pas de modèle inutilement complexe (pas de réseaux de neurones, pas de théorie des catégories).
4. **Elles couvrent les 4 axes du mémoire** : linguistique (\( B, \Omega \)), pédagogie (\( C_{\text{mém}}, C_{\text{moteur}} \)), TALN (\( \text{Fert}, D \)), économie (\( E \)).
5. **Elles respectent l'esprit de parcimonie** de l'AAC : peu de paramètres, interprétables, calibrés sur corpus.

---

## 11. Limites et extensions possibles

- **Calibration** : \( \alpha, \beta, \tau, w_i \) doivent être estimés empiriquement (études pilotes).
- **Corpus** : les formules supposent un corpus représentatif ; il faut stratifier par registre.
- **Dynamique** : on pourrait ajouter un modèle épidémiologique d'adoption (\( \frac{dA}{dt} = \beta A (1-A) - \delta A \)) pour la transition.
- **Théorie de l'information** : on pourrait calculer l'entropie conditionnelle \( H(P|G) \) et \( H(G|P) \) pour mesurer l'efficacité informationnelle du code.

---

**Conclusion** : l'ajout de ces formules transforme le mémoire d'un **essai argumenté** en une **proposition scientifique quantifiée**, prête à être testée, comparée et éventuellement réfutée. C'est exactement ce que l'Académie du Créole Haïtien attend d'une réforme : des preuves, pas seulement des principes.