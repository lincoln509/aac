# Table de correspondance complète

Référence complète des sept séquences plurigraphiques de l'orthographe officielle de 1979, telles que traitées par l'ACC. Justification linguistique détaillée : chapitre III du mémoire.

| API | Pressoir (avant 1979) | Officiel 1979 | ACC | Codepoint Unicode | Modifié ? |
|-----|------------------------|----------------|-----|--------------------|-----------|
| /ʃ/ | ch | ch | **š** | U+0161 | Oui |
| /u/ | ou | ou | **ŏ** | U+014F | Oui |
| /ũ/ | oun | oun | **ŏ** + n (automatique) | U+014F | Oui (dérivé) |
| /ã/ | an | an | an | — | Non |
| /ɛ̃/ | en | en | en | — | Non |
| /õ/ | on | on | on | — | Non |
| /ɲ/ | gn / ng | ng | **ŋ** | U+014B | Oui |
| /ɥi/ ~ /jw/ | ui | ui | wi | — | Oui (séquence, pas de nouveau graphème) |
| — | w, y | w, y | w, y | — | Non |

## Comparaison avec les propositions post-1979

| Son (API) | Officiel 1979 / AKA 2017 | Gourdet (2022, linéarisme) | ACC |
|-----------|---------------------------|------------------------------|-----|
| /ʃ/ | ch | c | š |
| /u/ | ou | u | ŏ |
| /ũ/ | oun | ü | ŏ + n (automatique) |
| /ã/ | an | ä | an (inchangé) |
| /ɛ̃/ | en | ë | en (inchangé) |
| /õ/ | on | ö | on (inchangé) |
| /ɲ/ | ng | ng (non traité) | ŋ |
| /ɥi/ | ui | yw | wi |

**Différence de fond** : Gourdet applique la logique monogrammatique aux sept séquences, y compris les trois nasales. L'ACC s'en distingue en jugeant `an`, `en`, `on` déjà phonotactiquement transparentes (voir mémoire, section 3.2), et les laisse donc inchangées — une intervention volontairement plus restreinte, ciblant exclusivement les quatre séquences réellement opaques.

## Pourquoi pas de symbole distinct pour /ũ/

`oun` n'a pas de graphème ACC dédié. Il découle automatiquement de deux règles déjà posées ailleurs :

1. `ou` → `ŏ` (règle générale du son /u/)
2. `n` en fin de syllabe nasalise la voyelle qui précède (règle déjà en vigueur et non modifiée, cf. `an`, `en`, `on`)

`oun` devient donc `ŏn` sans qu'aucune règle supplémentaire ne soit nécessaire — voir `converter/tests/test_converter.py::test_oun_becomes_o_breve_plus_n_automatically` pour la vérification automatisée de cette propriété.
