# ACC — Alphabet Atomique Créole

> Prototype technique accompagnant le mémoire *« Pour une Rationalisation Atomique de la Graphie Créole Haïtienne — De la Réforme Orthographique de 1979 à l'Alphabet Atomique Créole »*.
>
> **English:** A working prototype (bidirectional converter + interactive demo) supporting a research proposal to simplify four opaque digraphs of the 1979 official Haitian Creole orthography (`ch`, `ou`, `oun`, `ng`) into three standard Unicode monographs (`š`, `ŏ`, `ŋ`), while deliberately leaving `an`, `en`, `on` untouched. The underlying theory reclassifies the traditional 32-letter alphabet as containing only 24 truly irreducible letters — the rest being regular, predictable combinations.

Ce dépôt ne contient pas de théorie supplémentaire : il contient du **code qui vérifie que la théorie fonctionne**. Chaque chiffre cité dans le mémoire (gain de 2,5 % à 9,3 % selon le texte — moyenne 5,7 %, IC95 % [3,9–7,5 %] sur 8 textes indépendants —, 140 → 127 caractères pour l'extrait historique, réduction de l'inventaire alphabétique nominal de 32 à 24 lettres) est reproduit par une suite de tests automatisés, pas seulement affirmé dans un texte.

## L'idée en une phrase

L'orthographe créole de 1979 compte traditionnellement 32 « lettres », mais plusieurs d'entre elles (an, en, on, à, è, ò) ne sont pas des lettres irréductibles : ce sont des combinaisons régulières (voyelle + n, ou voyelle + accent). Une fois ce recomptage effectué, il ne reste que 24 lettres véritablement atomiques — et seules quatre séquences (ch, ou, oun, ng) sont de vraies anomalies orthographiques, corrigées ici par trois monogrammes déjà standardisés dans Unicode (š, ŏ, ŋ). Le détail complet de cette démonstration est dans le mémoire ; ce dépôt en est la preuve par le code.

## Pourquoi ce prototype

Un ingénieur qui propose une réforme d'écriture doit, à un moment, cesser d'en parler et la faire tourner. Ce dépôt fait exactement ça :

- **Un convertisseur bidirectionnel** (Python + JavaScript, sans dépendance externe) entre l'orthographe officielle de 1979 et l'ACC.
- **Une suite de tests** qui rejoue l'exemple du chapitre IV du mémoire et échoue si les chiffres cités deviennent faux.
- **Une démo web interactive** à page unique, déployable telle quelle sur GitHub Pages, sans étape de build. Les deux panneaux (1979 / ACC) sont éditables et se convertissent automatiquement l'un l'autre, dans les deux sens, sans bouton à cliquer.
- **Une visionneuse de fichiers intégrée** à la démo : README, LICENSE et le code source (Python/JS/tests) se lisent directement sur la page, dans une fenêtre modale avec coloration syntaxique légère, sans quitter le site.
- **Une disposition clavier complète** (`keyboard/ht-t-k0-aac.xml`, format [CLDR Keyboard 3.0](https://www.unicode.org/reports/tr35/tr35-keyboards.html)) pour taper š, ŏ et ŋ directement au clavier — AltGr sur ordinateur, appui long sur mobile — plus un guide d'installation par plateforme.
- **Une conversion de documents Word/PDF entiers**, avec préservation du format d'origine, accompagnée d'un vrai traitement statistique du gain (écart-type, intervalle de confiance à 95 %, test t apparié, bootstrap) plutôt qu'un chiffre unique. Disponible en ligne de commande (`converter/document_converter.py`, fidélité maximale) **et** directement dans le navigateur (`web-demo/documents.html`, glisser-déposer, sans backend) — voir « Conversion de documents » plus bas.

## Structure du dépôt

```
acc-toolkit/
├── converter/
│   ├── acc_converter.py       # implémentation de référence (Python)
│   ├── acc_converter.js       # port JavaScript (même comportement)
│   ├── document_converter.py  # conversion .docx/.pdf avec préservation du format
│   ├── document_stats.py      # traitement statistique (écart-type, IC, test t, bootstrap)
│   ├── requirements-documents.txt
│   └── tests/
│       ├── test_converter.py           # tests de non-régression liés au mémoire
│       ├── test_document_converter.py  # fidélité de mise en forme docx
│       └── test_document_stats.py      # validité du traitement statistique
├── web-demo/
│   ├── index.html             # démo interactive, un seul fichier
│   └── documents.html         # conversion de documents entiers (docx/pdf) + rapport statistique
├── keyboard/
│   ├── ht-t-k0-aac.xml        # disposition clavier CLDR Keyboard 3.0
│   └── README.md              # guide d'installation par plateforme
├── docs/
│   └── grapheme-table.md      # table de correspondance complète
├── assets/
│   ├── aac-logo.png           # logo (en-tête du site)
│   ├── aac-logo-square.png    # favicon
│   └── aac-og.jpg             # image de partage réseaux sociaux
├── scripts/
│   └── sync_snapshots.py      # resynchronise l'instantané hors-ligne du site
├── .githooks/
│   ├── pre-commit              # relance sync_snapshots.py à chaque commit
│   └── README.md               # comment l'activer
├── .github/workflows/
│   └── sync-snapshots.yml      # même vérification, filet de sécurité côté GitHub
├── LICENSE
└── README.md
```

## Maintenance : garder la démo synchronisée avec ce dépôt

La visionneuse de fichiers intégrée à `web-demo/index.html` lit README.md,
LICENSE, le code et les fichiers clavier **en direct** (`fetch`) quand le
site est servi par un serveur web (GitHub Pages, `python3 -m http.server`,
etc.) — dans ce cas, toute modification de ces fichiers apparaît dès le
prochain rechargement de page, sans rien d'autre à faire.

Quand le site est ouvert directement depuis le disque (double-clic,
`file://`), les navigateurs interdisent `fetch()` vers d'autres fichiers
locaux : la visionneuse retombe alors sur un **instantané intégré**
directement dans `index.html` (encodé en base64), pour que la démo reste
utilisable hors-ligne. Cet instantané ne se met pas à jour tout seul —
c'est le rôle de [`scripts/sync_snapshots.py`](scripts/sync_snapshots.py).

**Automatique** : activez le hook une seule fois par clone —

```bash
git config core.hooksPath .githooks
```

— et chaque `git commit` resynchronise l'instantané si besoin, sans y
penser. Un filet de sécurité équivalent tourne aussi côté GitHub Actions
([`.github/workflows/sync-snapshots.yml`](.github/workflows/sync-snapshots.yml))
pour les modifications faites sans le hook local (éditeur web GitHub, par
exemple).

**Manuel**, si besoin :

```bash
python3 scripts/sync_snapshots.py          # met à jour
python3 scripts/sync_snapshots.py --check  # vérifie seulement (utile en CI)
```

## Essayer localement

**Python**

```bash
python3 converter/acc_converter.py to-acc "Chak moun gen dwa pou yo chèche travay san pwoblèm nan peyi a."
# -> Šak mŏn gen dwa pŏ yo šèše travay san pwoblèm nan peyi a.

python3 -m unittest converter.tests.test_converter -v
```

**JavaScript / Node**

```bash
node -e "const {toAcc} = require('./converter/acc_converter.js'); console.log(toAcc('Chante pou chase lapli.'))"
```

**Démo web**

Ouvrez `web-demo/index.html` dans un navigateur, ou servez le dépôt
localement — utilisez `scripts/serve.py` plutôt que `python3 -m
http.server` nu : ce dernier liste tout le contenu du dossier dans le
navigateur (y compris `.git/`, `scripts/`, `.github/`) et écoute sur tout
le réseau local par défaut. `scripts/serve.py` bloque ces deux points tout
en servant normalement ce dont la démo a besoin :

```bash
python3 .\toolkit\v1.0.1\scripts\serve.py #q 
python3 scripts/serve.py
# puis http://localhost:8000/web-demo/

python3 scripts/serve.py 8080 --public  # port différent, accessible depuis le réseau local
```

## Stopper le serveur 
```bash
Ctrl+C
```
Le script capte cet arrêt proprement (`KeyboardInterrupt`) et affiche `Sèvè a rete`. avant de se terminer.

Si tu as lancé le serveur en arrière-plan (avec `&` à la fin de la commande, ou dans un autre terminal que tu as fermé sans faire Ctrl+C), le port reste occupé. Deux façons de le retrouver et l'arrêter :

**1) Par le port (le plus fiable — remplace 8000 par ton port) :**

```bash
lsof -ti :8000 | xargs kill
```

**2) Par le nom du processus :**

```bash
pkill -f "scripts/serve.py"
```

Pour vérifier qu'il ne tourne vraiment plus :
```bash
lsof -i :8000
```
Si cette commande n'affiche rien, le port est libre.

Si jamais `kill` seul ne suffit pas (rare, processus bloqué), ajoute `-9` pour forcer :

```bash
lsof -ti :8000 | xargs kill -9
```


Voir [Sécurisation du serveur local](#sécurisation-du-serveur-local)
ci-dessous pour le détail de ce qui est bloqué et pourquoi.

Pour l'héberger sur GitHub Pages : Settings → Pages → Source = branche `main`, dossier `/ (root)`, puis partagez le lien vers `web-demo/index.html`.

## Sécurisation du serveur local

`python3 -m http.server` (sans argument) sert **tout** ce qui se trouve
dans le dossier où vous le lancez, et **liste le contenu de n'importe quel
dossier** qui n'a pas de `index.html` — y compris, si vous le lancez
depuis la racine ou un dossier parent, l'historique Git complet
(`.git/`), les scripts internes (`scripts/`), et les workflows CI
(`.github/`). Rien de tout ça n'est censé être navigable par un visiteur.

`scripts/serve.py` corrige ça (bibliothèque standard uniquement, aucune
dépendance) :

| Comportement | `python3 -m http.server` | `scripts/serve.py` |
|---|---|---|
| Liste le contenu d'un dossier sans `index.html` | Oui | Non — `403 Forbidden` |
| Sert `.git/`, `scripts/`, `.github/`, `.githooks/` | Oui | Non — `403 Forbidden`, même en tapant l'URL exacte |
| Sert `README.md`, `converter/*`, `keyboard/*`, `assets/*` (nécessaires à la démo) | Oui | Oui, normalement |
| Interfaces réseau écoutées | Toutes (0.0.0.0) | `127.0.0.1` seulement, sauf avec `--public` |

```bash
python3 scripts/serve.py            # 127.0.0.1:8000, dossiers internes bloqués
python3 scripts/serve.py 8080       # port différent
python3 scripts/serve.py --public   # ouvre aussi au réseau local (utile pour tester sur téléphone)
```

Si vous ajoutez d'autres fichiers ou dossiers internes à ne jamais
exposer, ajoutez-les à `BLOCKED_PREFIXES` en haut de
[`scripts/serve.py`](scripts/serve.py).

## Les règles implémentées

| Son (API) | 1979    | ACC | Codepoint | Statut        |
|-----------|---------|-----|-----------|---------------|
| /ʃ/       | ch      | š   | U+0161    | Remplacé      |
| /u/, /ũ/  | ou, oun | ŏ   | U+014F    | Remplacé      |
| /ɲ/       | ng      | ŋ   | U+014B    | Remplacé      |
| /ã/       | an      | an  | —         | **Inchangé**  |
| /ɛ̃/       | en      | en  | —         | **Inchangé**  |
| /õ/       | on      | on  | —         | **Inchangé**  |
| /ɥi/      | ui      | wi  | —         | Séquence déjà existante |

Détail complet et justification linguistique : [`docs/grapheme-table.md`](docs/grapheme-table.md) et chapitre III du mémoire.

## Limite connue et documentée

La conversion ACC → 1979 n'est **pas parfaitement réversible** pour la séquence `wi` : ce groupe existait déjà dans l'orthographe de 1979 pour des mots qui n'ont jamais été écrits `ui` (l'exemple le plus fréquent est `wi`, « oui »). Le convertisseur inclut une petite liste d'exceptions lexicales (`WI_WORDS_NEVER_FROM_UI`) pour gérer les cas les plus courants, mais une fidélité totale demanderait un lexique complet — c'est justement l'un des livrables prévus en phase 2 de la feuille de route du mémoire (constitution d'un corpus de référence bilingue). Ce n'est pas caché : c'est testé explicitement dans `test_converter.py`.

## Conversion de documents (Word / PDF) et traitement statistique

Le chiffre initial du mémoire — « gain de 9,3 % » — reposait sur **un seul extrait de 140 caractères**, et cet extrait avait en plus été mal attribué à René Depestre dans une version antérieure de ce dépôt : il s'agit en réalité d'un texte personnel de l'auteur, rédigé dans le cadre du document AAC/AKI (corrigé dans `converter/tests/test_converter.py`, classe `TestCorpusLincoln`). Un seul extrait, quelle que soit son attribution, reste une démonstration ponctuelle, pas une estimation : ni écart-type, ni intervalle de confiance, rien n'indique si elle se généralise.

`converter/corpus.py` répond à ça avec **8 textes indépendants de sources délibérément diverses** : 2 textes personnels de l'auteur, un extrait légal (Constitution de 1987), un extrait international (Déclaration universelle des droits de l'homme, traduction officielle OHCHR), 2 lots de pwovèb kreyòl (tradition orale, domaine public), et 2 extraits littéraires du domaine public — Oswald Durand (« Choukoun », 1883 ; mort en 1906) et Georges Sylvain (« Cric? Crac! », 1901 ; mort en 1925). Volontairement absents : des auteurs dont l'œuvre reste sous droits (Frankétienne, mort en 2025 ; René Depestre ; Georges Castera, mort en 2020) — les reproduire ici serait une violation de copyright, pas une question de citation en passant.

Sur ces 8 textes (`converter/tests/test_corpus_diversity.py`), le gain varie de **2,5 % à 9,3 %** selon le texte, moyenne **5,7 %** (IC95 % [3,9–7,5 %]). Ce n'est pas un échantillon aléatoire représentatif du créole écrit en général — c'est un échantillon de convenance choisi pour sa diversité de registres (personnel, légal, international, oral, littéraire ancien) — mais il montre que le gain n'est pas un artefact d'un seul extrait choisi.

`converter/document_converter.py` et `converter/document_stats.py` vont plus loin encore : ils permettent de mesurer ce même gain, avec le même appareil statistique, sur **n'importe quel document fourni par l'utilisateur** plutôt que sur un corpus fixe.

```bash
pip install -r converter/requirements-documents.txt
python converter/document_converter.py memoire.docx memoire_acc.docx --report rapport.md
python converter/document_converter.py chapitre.pdf chapitre_acc.pdf --report rapport.json
```

- **`.docx` → `.docx`** : fidélité totale. Seul le texte à l'intérieur des runs Word existants est modifié (`run.text = to_acc(run.text)`) — gras, italique, polices, styles de titre et tableaux restent identiques à l'original. Limite documentée : une séquence `ch`/`ou`/`ng` coupée exactement à la frontière entre deux runs (rare, généralement après une correction manuelle) n'est pas convertie ; le script le signale sur stderr.
- **`.pdf` → `.pdf`** : fidélité textuelle, pas visuelle. Un PDF n'a pas de « texte modifiable » — le texte est extrait paragraphe par paragraphe (`pdfplumber`) puis un nouveau PDF est reconstruit (`reportlab`, police DejaVu Sans pour que š/ŏ/ŋ s'affichent correctement) avec la même taille de page. Pour un document essentiellement textuel le résultat est très proche de l'original ; pour une mise en page complexe (colonnes, texte sur image), le contenu reste correct mais la mise en page ne l'est pas — vérifier visuellement, ou repartir du `.docx` source s'il existe.

Chaque **paragraphe** du document devient une observation indépendante, ce qui permet un vrai traitement statistique plutôt qu'un chiffre unique :

- moyenne et écart-type (échantillon, ddof=1) du gain (%) entre paragraphes ;
- intervalle de confiance à 95 % par loi de Student (df = n−1) **et** par bootstrap (10 000 ré-échantillons, percentile) — le second ne suppose pas la normalité et sert de vérification croisée ;
- test de Shapiro-Wilk sur la distribution des gains, pour juger si l'IC de Student est fiable ou s'il faut privilégier le bootstrap ;
- test t apparié (nombre de caractères avant vs après) contre l'hypothèse nulle « aucune différence », pour vérifier que la réduction n'est pas un artefact du choix des paragraphes ;
- **test de permutation** (Monte Carlo, retournement de signe) : une troisième vérification indépendante, sans aucune hypothèse de distribution — utile en particulier pour révéler qu'avec un tout petit échantillon, l'espace des permutations est trop grossier pour jamais atteindre p<0,05, même quand le test t (paramétrique) y arrive. Un signal honnête plutôt qu'un artefact caché ;
- taille d'effet (d de Cohen, mesures appariées), avec son propre **intervalle de confiance bootstrap** ;
- **corrélation longueur du segment / gain %** (Pearson) : diagnostic de validité — un gain qui dépendrait artificiellement de la longueur du paragraphe serait suspect ;
- **analyse de puissance par simulation** : combien de paragraphes faudrait-il pour détecter l'effet observé avec 80 % de certitude, si on répétait l'expérience ? Répond directement à « combien de texte faut-il pour un résultat solide » ;
- décomposition du gain par règle (`ch`/`ou`/`ng` économisent chacun 1 caractère par occurrence, `ui→wi` est un renommage neutre à 0 caractère) avec vérification croisée : la somme des économies prédites par règle doit égaler le gain réellement mesuré.

### Augmenter la taille de l'échantillon

Deux leviers, cumulables, pour resserrer les intervalles de confiance :

- **Granularité plus fine** : au lieu du paragraphe, découper en phrases (`--granularity sentence` en CLI, ou le sélecteur « fraz » dans `documents.html`). Plus de segments, IC plus étroit — au prix d'une indépendance un peu plus faible entre observations (deux phrases du même paragraphe se ressemblent plus que deux paragraphes de documents différents).
- **Plusieurs documents à la fois** : `python converter/document_converter.py analyze fichier1.docx fichier2.pdf ... --report rapport.md` (ou glisser plusieurs fichiers dans `documents.html`) regroupe tous les segments. Le rapport distingue alors deux lectures :
  - **pooled** — chaque paragraphe de chaque document compte comme une observation indépendante (IC le plus étroit, un peu optimiste) ;
  - **cluster** — chaque document résumé par sa propre moyenne, n = nombre de documents (IC plus large, plus honnête — c'est celui à citer dans un mémoire). Avec seulement 1-2 documents, cet IC "cluster" est volontairement très large : c'est le signal qu'il faut plus de documents, pas plus de paragraphes du même texte.

`converter/tests/test_document_stats.py` vérifie entre autres que le chiffre historique du mémoire (140 → 127 caractères, −9,3 %, texte personnel de l'auteur) reste reproductible tel quel via ce pipeline, et que le test t détecte correctement un gain nul quand le texte ne contient aucune séquence opaque. `converter/tests/test_corpus_diversity.py` vérifie que l'écart mesuré sur les 8 textes de `corpus.py` (2,5 % à 9,3 %) reste stable, et qu'aucun auteur encore sous droits n'y est jamais réintroduit. `converter/tests/test_document_converter.py` vérifie la préservation du gras/italique sur un docx converti.

### Version navigateur (`web-demo/documents.html`)

Même traitement statistique, mais glisser-déposer direct dans le navigateur, sans backend — `converter/document_converter.py` est le même calcul, en Python, pour qui préfère la ligne de commande ou traiter un lot de fichiers.

- **.docx → .docx** : fidélité totale. Implémenté avec [JSZip](https://stuk.github.io/jszip/) : le `.docx` est ouvert comme l'archive ZIP qu'il est, seul le texte à l'intérieur des balises `<w:t>` de `word/document.xml` est modifié, puis l'archive est réécrite telle quelle — gras, italique, tableaux, styles restent identiques à l'original (vérifié en rendant le fichier de sortie et en inspectant runs et mise en page).
- **.pdf → texte/.docx** : le texte est extrait paragraphe par paragraphe avec [pdf.js](https://mozilla.github.io/pdf.js/) (regroupement des lignes par position verticale, détection du saut de paragraphe par écart de ligne), puis proposé en téléchargement `.txt` (fidélité de contenu garantie) et `.docx` (mise en page simple, un paragraphe par `<w:p>`). Reconstruire un `.pdf` visuellement fidèle sans backend n'est pas fait ici — utiliser `document_converter.py` pour ça.
- Les fonctions statistiques (bêta incomplète, CDF/PPF de Student, bootstrap, test t apparié, d de Cohen) sont un port JavaScript direct de `document_stats.py`, validées ligne à ligne contre `scipy.stats.t` avant portage, puis testées de bout en bout dans un vrai navigateur (Playwright) sur les mêmes documents que les tests Python — les deux implémentations produisent des résultats identiques au dixième de point près.
- Dépendances chargées par CDN (JSZip, pdf.js) : seule cette page en a besoin, `index.html` reste sans dépendance externe.

## Par rapport aux travaux existants

Ce prototype n'invente pas le principe d'un alphabet à monogrammes pour le créole : le linguiste Frantz Gourdet en a publié une version plus ambitieuse en 2022 (*Rechèch Etid Kreyòl*, théorie du linéarisme), qui touche également `an`, `en`, `on`. L'ACC s'en distingue délibérément en laissant ces trois séquences inchangées — voir la section 3.5 du mémoire pour la justification complète de ce choix.

## Documents associés

Ce dépôt est le complément technique d'un ensemble documentaire plus large :

- **Édition livre** (format 6×9 po, page de titre, avec ISBN en d'obtention depuis la BNH, dépôt légal) — la même démonstration scientifique, mise en forme pour une diffusion en dehors du cadre strictement académique.
- **Mémoire complet** (format Letter, ~70 pages) — la démonstration scientifique intégrale : histoire de la graphie créole, diagnostic, théorie de l'alphabet atomique, protocole d'implémentation, évaluation d'impact, chapitre dédié au traitement automatique du langage (tokenisation, GPT/deepseek/Claude etc.), annexes phonologique et Unicode complètes.
- **ht-t-k0-aac.xml** — Disposition clavier CLDR (Keyboard 3.0, UTS #35 Part 7) pour l'Alphabet Atomique Créole (AAC).
- **Un manuel de transition technique vers l'AAC** — Qui contient les spécifications des dispositions clavier (physique/virtuelle), Guide de conversion pour éditeurs et des protocoles de la phase pilote.


Ces documents ne sont pas inclus, à l'exception de ht-t-k0-aac.xml, qui s'y trouve dans le dossier : [keyboard/ht-t-k0-aac.xml](keyboard/ht-t-k0-aac.xml), dans ce dépôt (ce sont des fichiers Word volumineux, peu adaptés à un suivi git), mais définissent l'intégralité du raisonnement dont ce code n'est que la vérification.

## Licence

Le code de ce dépôt est publié sous licence [MIT](LICENSE). Le texte du mémoire associé suit sa propre licence (voir le document lui-même).

## Statut du projet

Prototype de recherche indépendant, soumis pour discussion à l'Akademi Kreyòl Ayisyen. Contributions, corrections et signalements d'erreurs linguistiques bienvenus via les *issues* de ce dépôt.
