# Disposition clavier AAC — guide d'utilisation

Ce dossier contient une disposition clavier complète et conforme à la
spécification **[CLDR Keyboard 3.0](https://www.unicode.org/reports/tr35/tr35-keyboards.html)**
(Unicode Technical Standard #35, Part 7), permettant de taper `š`, `ŏ` et `ŋ`
directement, sans logiciel de conversion, sur n'importe quelle plateforme qui
sait lire ce format.

| Fichier | Rôle |
|---|---|
| [`ht-t-k0-aac.xml`](ht-t-k0-aac.xml) | La disposition clavier elle-même (source unique, portable) |
| `README.md` | Ce guide |

## En bref

- **Identifiant clavier (BCP-47)** : `ht-t-k0-aac`
- **Conforme à** : CLDR 45 (`conformsTo="45"`)
- **Deux configurations dans un seul fichier** :
  - `formId="us"` — clavier **physique** ANSI 101/104 touches (ce que la
    plupart des ordinateurs utilisent)
  - `formId="touch"` — clavier **tactile** (mobile / tablette)
- **Aucune touche morte, aucune transformation** : `š`, `ŏ`, `ŋ` sont des
  caractères Unicode précomposés (un seul point de code chacun), donc un
  seul temps de frappe suffit pour les produire. C'est plus simple et plus
  fiable qu'une séquence de touche morte.

## Comment taper les lettres AAC

### Clavier physique — AltGr

Les trois lettres sont accessibles avec **AltGr** (la touche Alt de droite)
sur les positions physiques `S`, `O`, `N` — exactement comme `ş`/`ğ` en
turc ou `š`/`č`/`ř` en tchèque :

| Touches | Résultat |
|---|---|
| `AltGr` + `S` | š |
| `AltGr` + `Maj` + `S` | Š |
| `AltGr` + `O` | ŏ |
| `AltGr` + `Maj` + `O` | Ŏ |
| `AltGr` + `N` | ŋ |
| `AltGr` + `Maj` + `N` | Ŋ |

Le reste du clavier (chiffres, ponctuation, autres lettres) se comporte
comme un clavier QWERTY US standard, avec ou sans AltGr, avec ou sans
Verrouillage Majuscule — les 8 combinaisons de modificateurs sont définies
explicitement dans le fichier pour éviter toute touche « morte » côté
implémentation.

### Clavier tactile — appui long

Sur mobile, il n'y a pas de touche AltGr : l'accès se fait par **appui
long** (*long press*), comme `ñ` sur un clavier espagnol :

| Appui long sur | Options qui apparaissent |
|---|---|
| `s` / `S` | š / Š |
| `o` / `O` | ò, ŏ / Ò, Ŏ *(`ŏ` est proposé en premier)* |
| `n` / `N` | ŋ / Ŋ |
| `a` / `A` | à / À |
| `e` / `E` | è / È |

Les voyelles `à`, `è`, `ò` de l'orthographe 1979 sont incluses au même
endroit : un clavier créole réel en a besoin de toute façon, et cela ne
coûte rien de plus dans le fichier.

## Pourquoi ce choix de conception (AltGr + appui long, pas de touche morte)

Les notes précédentes de ce dossier envisageaient une touche morte
(`caron` + `s` → š). Ce fichier s'en écarte volontairement :

1. **Une seule frappe au lieu de deux.** `š` n'est pas une lettre de base
   plus un diacritique combiné à l'affichage — c'est un unique point de
   code Unicode précomposé (U+0161). Le taper en deux temps (touche morte
   puis lettre) ajoute une étape sans bénéfice.
2. **Pas de `<transforms>` à maintenir.** Une touche morte exige de
   définir des règles de correspondance (`<transform from= to=>`) et de
   gérer les cas où la séquence ne correspond à rien. En sortant un
   caractère précomposé directement depuis `<key output=…>`, tout le
   mécanisme de transformation devient inutile — moins de surface pour les
   bogues d'implémentation.
3. **Cohérent avec des dispositions déjà largement déployées** (tchèque,
   turc, roumain) qui utilisent AltGr pour ce type de lettre additionnelle
   plutôt qu'une touche morte.

Si une touche morte reste préférable pour un usage particulier (par
exemple, un clavier destiné à des utilisateurs habitués aux touches
mortes d'un autre clavier créole), elle peut être ajoutée plus tard via un
élément `<transforms type="simple">` sans toucher au reste du fichier —
voir la section [Étendre ce fichier](#étendre-ce-fichier) plus bas.

## Valider le fichier

Avant d'installer ou de distribuer ce fichier, vérifiez qu'il reste un XML
bien formé et que toutes les références de touches se résolvent :

```bash
python3 -c "
import xml.etree.ElementTree as ET
ET.parse('ht-t-k0-aac.xml')
print('XML bien formé : OK')
"
```

Pour une validation complète contre le schéma officiel, récupérez le DTD ou
le XSD `keyboard3` depuis le dépôt CLDR
([`unicode-org/cldr`](https://github.com/unicode-org/cldr/tree/main/keyboards/dtd))
et validez avec un outil comme `xmllint` :

```bash
xmllint --noout --dtdvalid ldmlKeyboard3.dtd ht-t-k0-aac.xml
```

## Installer et tester la disposition

Le format CLDR Keyboard 3.0 est un format d'**échange**, pas un format
directement installable par la plupart des systèmes d'exploitation — il
sert à produire un fichier natif à chaque plateforme, ou à être importé
par un outil qui sait déjà le lire.

### Option recommandée : Keyman

[Keyman](https://keyman.com) (gratuit, open source, Tavultesoft/SIL) est
aujourd'hui l'outil le plus abouti pour partir d'une disposition CLDR et
produire un clavier installable sur Windows, macOS, Linux, Android et iOS
à partir de la **même** source :

1. Installez le [Keyman Developer](https://keyman.com/developer/).
2. Créez un nouveau projet clavier et importez `ht-t-k0-aac.xml` (Keyman
   Developer sait lire le format LDML/CLDR Keyboard).
3. Compilez pour la ou les plateformes voulues (`.kmp` pour Windows/macOS/
   Linux, paquet Android/iOS pour mobile).
4. Publiez le `.kmp` généré sur le
   [Keyman Keyboard Repository](https://github.com/keymanapp/keyboards)
   ou distribuez-le directement.

C'est le chemin le plus court vers un clavier installable en une seule
étape, sur toutes les plateformes majeures, sans réécrire la disposition
plateforme par plateforme.

### Windows

- **Via Keyman** (voir ci-dessus) : le plus simple, gère AltGr nativement.
- **Via MSKLC** (Microsoft Keyboard Layout Creator) : MSKLC ne lit pas le
  format CLDR directement. Il faut recréer la disposition manuellement à
  partir du tableau ci-dessus (AltGr = colonne « clavier alternatif » dans
  MSKLC), puis compiler en `.dll`/`.msi`. Fonctionnel mais redondant avec
  Keyman — à réserver aux environnements qui interdisent les outils tiers.

### macOS

- **Via Keyman** (voir ci-dessus).
- **Via Ukelele** ([SIL Ukelele](https://software.sil.org/ukelele/)) :
  éditeur de fichiers `.keylayout` d'Apple. Ukelele ne supporte pas encore
  l'import direct de CLDR Keyboard 3.0 ; la disposition doit être recréée
  à la main dans Ukelele en suivant le tableau AltGr ci-dessus (section
  « Option » côté droit = AltGr). Une fois testée dans Ukelele, exportez en
  `.keylayout` et installez dans `~/Library/Keyboard Layouts/`.

### Linux (XKB)

Les dispositions XKB se définissent dans
`/usr/share/X11/xkb/symbols/`. Une entrée minimale correspondant à ce
fichier (variante ajoutée à la disposition `us` existante) :

```
partial alphanumeric_keys
xkb_symbols "aac" {
    include "us(basic)"
    name[Group1] = "Haitian Creole (AAC)";

    key <AC02> { [ s, S, U0161, U0160 ] }; // š Š  (touche S)
    key <AD09> { [ o, O, U014F, U014E ] }; // ŏ Ŏ  (touche O)
    key <AB06> { [ n, N, U014B, U014A ] }; // ŋ Ŋ  (touche N)
};
```

Ajoutez ce bloc à un fichier (par exemple `ht`) dans le répertoire `symbols`
ci-dessus, puis activez-le via les paramètres clavier du système
(`setxkbmap ht aac` en ligne de commande, ou via l'interface régionale de
GNOME/KDE). Les 3e/4e symboles de chaque touche (`U0161` etc.) correspondent
à AltGr et AltGr+Maj — même comportement que la disposition `us` de ce
fichier.

### Android / iOS

- **Via Keyman** : chemin le plus direct, applications Keyman disponibles
  sur les deux boutiques d'applications, la couche tactile de
  `ht-t-k0-aac.xml` (appui long) s'y importe directement.
- **Via un IME personnalisé** (Android) ou une extension clavier
  personnalisée (iOS) : possible en implémentant soi-même un moteur
  compatible CLDR Keyboard 3.0 (bibliothèques comme
  [KMEA/KMEI](https://github.com/keymanapp/keyman) de Keyman sont open
  source et réutilisables), ou en codant en dur la table `formId="touch"`
  de ce fichier dans un IME existant.

## Étendre ce fichier

Le fichier est conçu pour rester lisible et modifiable directement :

- **Ajouter une touche morte alternative** : ajoutez un élément
  `<transforms type="simple">` avec des règles `<transform from="…"
  to="…"/>`, sans toucher aux `<layers>` existants.
- **Ajouter une disposition ISO (102 touches, avec la touche
  supplémentaire près de Maj gauche)** : dupliquez le bloc
  `<layers formId="us">` en `<layers formId="iso">` — impossible d'avoir
  deux formes matérielles différentes dans le même fichier
  (voir la spécification, un seul `<layers>` non-tactile par fichier) ;
  créez alors un second fichier `ht-t-k0-aac-iso.xml` si les deux formats
  doivent coexister.
- **Ajouter d'autres langues supportées par le même clavier** : ajoutez des
  entrées dans `<locales>` (par exemple si une variante régionale du créole
  utilise la même disposition).

## Références

- Spécification complète : [UTS #35 Part 7 — Keyboards](https://www.unicode.org/reports/tr35/tr35-keyboards.html)
- Dépôt source CLDR (DTD, exemples officiels) : [github.com/unicode-org/cldr](https://github.com/unicode-org/cldr/tree/main/keyboards)
- Outil de compilation/distribution recommandé : [keyman.com](https://keyman.com)
- Table de correspondance complète des graphèmes AAC : [`../docs/grapheme-table.md`](../docs/grapheme-table.md)
