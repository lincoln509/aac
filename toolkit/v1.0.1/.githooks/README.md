# .githooks/

Hooks Git versionnés avec le dépôt (contrairement à `.git/hooks/`, qui
n'est jamais commité).

## Activation (une seule fois par clone)

```bash
git config core.hooksPath .githooks
```

À partir de là, `git commit` relance automatiquement
[`scripts/sync_snapshots.py`](../scripts/sync_snapshots.py) : si vous avez
modifié `README.md`, `LICENSE`, le code du convertisseur ou les fichiers
clavier, l'instantané intégré dans `web-demo/index.html` (utilisé par la
visionneuse de fichiers du site quand elle est ouverte hors-ligne, en
`file://`) est remis à jour et ajouté à votre commit — sans étape
manuelle.

## Contenu

| Fichier | Rôle |
|---|---|
| `pre-commit` | Relance `scripts/sync_snapshots.py` avant chaque commit et ajoute `web-demo/index.html` s'il a changé. |

## Filet de sécurité côté serveur

Le hook ci-dessus est local : il ne s'exécute que si vous l'avez activé et
que vous commitez depuis votre machine (pas via l'éditeur web de GitHub,
par exemple). Pour ne jamais dépendre de ça,
[`.github/workflows/sync-snapshots.yml`](../.github/workflows/sync-snapshots.yml)
fait la même vérification côté GitHub Actions à chaque push, et corrige
automatiquement par un commit si besoin.
