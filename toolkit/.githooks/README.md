# .githooks/

Hooks Git versionnés avec le dépôt (contrairement à `.git/hooks/`, qui
n'est jamais commité).

## Activation (une seule fois par clone)

```bash
git config core.hooksPath .githooks
```

À partir de là, `git commit` lance [`scripts/build.py`](../scripts/build.py),
qui régénère `web-demo/generated/` (règles de conversion, corpus,
instantanés hors-ligne de la visionneuse) et l'ajoute à votre commit. Les
pages `web-demo/*.html` ne sont jamais modifiées par le hook.

## Contenu

| Fichier | Rôle |
|---|---|
| `pre-commit` | Lance `scripts/build.py` avant chaque commit et ajoute uniquement `web-demo/generated/`. |

## Filet de sécurité côté serveur

Le hook est local : il ne s'exécute que si vous l'avez activé. Le workflow
[`.github/workflows/check-sync.yml`](../.github/workflows/check-sync.yml)
fait échouer le build si `web-demo/generated/` est périmé, si le
JavaScript d'une page ne compile pas, ou si les tests Python / Node
échouent. Correctif : `python3 scripts/build.py`, puis commit.
