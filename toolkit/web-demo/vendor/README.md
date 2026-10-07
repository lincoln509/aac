# web-demo/vendor/

Bibliothèques tierces **embarquées dans le dépôt** pour que les pages
fonctionnent hors-ligne (`file://`), sans CDN.

## `js-tiktoken-cl100k.min.js` (≈1 Mo) et `js-tiktoken-o200k.min.js` (≈2,3 Mo)

Tokeniseurs `cl100k_base` (GPT-3.5 / GPT-4) et `o200k_base` (GPT-4o) pour
`web-demo/token.html`, qui ne charge un bundle que si le tokeniseur
correspondant est coché. Chacun enregistre son encodage dans
`window.AACTiktoken` ; `window.AACTiktoken.get("cl100k_base")` renvoie un objet
`Tiktoken` de [js-tiktoken](https://github.com/dqbd/tiktoken) (licence MIT),
port JavaScript de `tiktoken` d'OpenAI. Le vocabulaire n'est analysé qu'au
premier appel de `get()`, pas au chargement du script.

- Versions utilisées : `js-tiktoken@1.0.21`, `esbuild@0.28.2`.
- Point d'entrée **unique** : [`tiktoken-entry.js`](tiktoken-entry.js) ; seul
  l'encodage change d'un bundle à l'autre.
- Ces fichiers sont **générés** : ne les éditez pas. Pour les reconstruire,
  depuis la racine du dépôt :

```bash
npm install --no-save js-tiktoken@1.0.21 esbuild@0.28.2
for enc in cl100k o200k; do
  npx esbuild web-demo/vendor/tiktoken-entry.js --bundle --minify --format=iife \
    --platform=browser --target=es2019 --legal-comments=none \
    --alias:aac-ranks=js-tiktoken/ranks/${enc}_base \
    --define:ENCODING_NAME="\"${enc}_base\"" \
    --outfile=web-demo/vendor/js-tiktoken-${enc}.min.js
done
```

(`node_modules/` n'est pas versionné.) `converter/tests/test_architecture.py`
vérifie que les bundles reproduisent les valeurs de référence de `tiktoken`
(`"hello world"` → `[15339, 1917]` en `cl100k_base`, `[24912, 2375]` en
`o200k_base`).

## NLLB-200

Le tokeniseur NLLB-200 (SentencePiece) n'est **pas** embarqué : ses fichiers ne
sont pas dans le dépôt. Il n'est disponible que dans
`converter/fertilite_tokenizers.py`, dont l'option `--export` alimente
`converter/fertilite_precomputed.json` (décomptes affichés par la page pour le
corpus seulement).
