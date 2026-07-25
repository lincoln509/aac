# ACC — Alphabet Atomique Créole

> Prototype technique accompagnant le mémoire *« Pour une Rationalisation Atomique de la Graphie Créole Haïtienne — De la Réforme Orthographique de 1979 à l'Alphabet Atomique Créole »*.
>
> **English:** A working prototype (bidirectional converter + interactive demo) supporting a research proposal to simplify four opaque digraphs of the 1979 official Haitian Creole orthography (`ch`, `ou`, `oun`, `ng`) into three standard Unicode monographs (`š`, `ŏ`, `ŋ`), while deliberately leaving `an`, `en`, `on` untouched. The underlying theory reclassifies the traditional 32-letter alphabet as containing only 24 truly irreducible letters — the rest being regular, predictable combinations.

Ce dépôt ne contient pas de théorie supplémentaire : il contient du **code qui vérifie que la théorie fonctionne**. Chaque chiffre cité dans le mémoire (gain de 9,3 % sur le corpus Depestre, 140 → 127 caractères, réduction de l'inventaire alphabétique nominal de 32 à 24 lettres) est reproduit par une suite de tests automatisés, pas seulement affirmé dans un texte.

## L'idée en une phrase

L'orthographe créole de 1979 compte traditionnellement 32 « lettres », mais plusieurs d'entre elles (an, en, on, à, è, ò) ne sont pas des lettres irréductibles : ce sont des combinaisons régulières (voyelle + n, ou voyelle + accent). Une fois ce recomptage effectué, il ne reste que 24 lettres véritablement atomiques — et seules quatre séquences (ch, ou, oun, ng) sont de vraies anomalies orthographiques, corrigées ici par trois monogrammes déjà standardisés dans Unicode (š, ŏ, ŋ). Le détail complet de cette démonstration est dans le mémoire ; ce dépôt en est la preuve par le code.

## Pourquoi ce prototype

Un ingénieur qui propose une réforme d'écriture doit, à un moment, cesser d'en parler et la faire tourner. Ce dépôt fait exactement ça :

- **Un convertisseur bidirectionnel** (Python + JavaScript, sans dépendance externe) entre l'orthographe officielle de 1979 et l'ACC.
- **Une suite de tests** qui rejoue l'exemple du chapitre IV du mémoire et échoue si les chiffres cités deviennent faux.
- **Une démo web interactive** à page unique, déployable telle quelle sur GitHub Pages, sans étape de build. Les deux panneaux (1979 / ACC) sont éditables et se convertissent automatiquement l'un l'autre, dans les deux sens, sans bouton à cliquer.
- **Une visionneuse de fichiers intégrée** à la démo : README, LICENSE et le code source (Python/JS/tests) se lisent directement sur la page, dans une fenêtre modale avec coloration syntaxique légère, sans quitter le site.
- **Une disposition clavier complète** (`keyboard/ht-t-k0-aac.xml`, format [CLDR Keyboard 3.0](https://www.unicode.org/reports/tr35/tr35-keyboards.html)) pour taper š, ŏ et ŋ directement au clavier — AltGr sur ordinateur, appui long sur mobile — plus un guide d'installation par plateforme.

## Structure du dépôt

```
acc-toolkit/
├── converter/
│   ├── acc_converter.py       # implémentation de référence (Python)
│   ├── acc_converter.js       # port JavaScript (même comportement)
│   └── tests/
│       └── test_converter.py  # tests de non-régression liés au mémoire
├── web-demo/
│   └── index.html             # démo interactive, un seul fichier
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

Ouvrez `web-demo/index.html` dans un navigateur, ou servez le dépôt localement :

```bash
python3 -m http.server 8000 -d ./toolkit/v1.0.1/
# puis http://localhost:8000/web-demo/
```

Pour l'héberger sur GitHub Pages : Settings → Pages → Source = branche `main`, dossier `/ (root)`, puis partagez le lien vers `web-demo/index.html`.

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

## Par rapport aux travaux existants

Ce prototype n'invente pas le principe d'un alphabet à monogrammes pour le créole : le linguiste Frantz Gourdet en a publié une version plus ambitieuse en 2022 (*Rechèch Etid Kreyòl*, théorie du linéarisme), qui touche également `an`, `en`, `on`. L'ACC s'en distingue délibérément en laissant ces trois séquences inchangées — voir la section 3.5 du mémoire pour la justification complète de ce choix.

## Documents associés

Ce dépôt est le complément technique d'un ensemble documentaire plus large :

- **Mémoire complet** (format Letter, ~70 pages) — la démonstration scientifique intégrale : histoire de la graphie créole, diagnostic, théorie de l'alphabet atomique, protocole d'implémentation, évaluation d'impact, chapitre dédié au traitement automatique du langage (tokenisation, GPT/Claude), annexes phonologique et Unicode complètes.
- **Édition livre** (format 6×9 po, page de titre, ISBN à obtenir, dépôt légal) — la même démonstration scientifique, mise en forme pour une diffusion en dehors du cadre strictement académique.
- **Document de préparation à la soutenance** — 36 questions-réponses anticipant les objections d'un jury ou de l'Académie, y compris les questions les plus inconfortables.

Ces documents ne sont pas inclus dans ce dépôt (ce sont des fichiers Word volumineux, peu adaptés à un suivi git) mais définissent l'intégralité du raisonnement dont ce code n'est que la vérification.

## Licence

Le code de ce dépôt est publié sous licence [MIT](LICENSE). Le texte du mémoire associé suit sa propre licence (voir le document lui-même).

## Statut du projet

Prototype de recherche indépendant, soumis pour discussion à l'Akademi Kreyòl Ayisyen. Contributions, corrections et signalements d'erreurs linguistiques bienvenus via les *issues* de ce dépôt.
