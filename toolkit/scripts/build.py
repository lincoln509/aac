#!/usr/bin/env python3
"""
scripts/build.py
=================

Générateur UNIQUE des fichiers que le navigateur ne peut pas lire lui-même.
Il remplace les anciens sync_converter.py, sync_corpus.py et
sync_snapshots.py, qui recopiaient du code et des données DANS les pages
HTML (entre des marqueurs) et dont les trois copies ont fini par diverger.

Principe : chaque donnée a UNE source ; ce script la convertit, sans rien y
ajouter, en un petit fichier JavaScript que les pages chargent avec une
simple balise <script src>. Les pages web-demo/*.html ne sont jamais
modifiées par ce script.

    SOURCE                               ->  GÉNÉRÉ (web-demo/generated/)
    converter/rules.json                 ->  rules.js     window.AAC_RULES
    converter/corpus.py (CORPUS)         ->  corpus.js    window.AAC_CORPUS
    converter/fertilite_precomputed.json ->  fertilite_precomputed.js  window.AAC_PRECOMPUTED
    README, code, clavier... (FILES)     ->  snapshots.js window.AAC_FILES

Le convertisseur lui-même n'est PAS généré : converter/aac_converter.js est
chargé tel quel par les pages (<script src="../converter/aac_converter.js">).

Pourquoi des fichiers générés plutôt que fetch() ? Parce que les navigateurs
interdisent fetch() vers des fichiers locaux quand la page est ouverte par
double-clic (file://), alors qu'une balise <script src> y fonctionne : la démo
reste donc utilisable hors-ligne, sans serveur et sans étape de build côté
visiteur. Les fichiers générés sont versionnés (GitHub Pages les sert tels
quels).

Usage :
    python3 scripts/build.py           # régénère (ne réécrit que ce qui change)
    python3 scripts/build.py --check   # ne modifie rien ; code de sortie 1
                                       # s'il y a dérive (CI)

Automatisation : le hook .githooks/pre-commit lance ce script avant chaque
commit ; les workflows .github/workflows/ le relancent côté GitHub.
Bibliothèque standard uniquement.
"""
from __future__ import annotations

import argparse
import base64
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GENERATED = ROOT / "web-demo" / "generated"

# Fichiers affichés par la visionneuse de web-demo/index.html, dans l'ordre
# des onglets : (clé, nom affiché, chemin depuis la racine, langage).
# C'est l'UNIQUE liste : la page lit window.AAC_FILES, elle n'en recopie rien.
VIEWER_FILES = [
    ("license", "LICENSE", "LICENSE", "text"),
    ("readme", "README.md", "README.md", "markdown"),
    ("kbguide", "keyboard/README.md", "keyboard/README.md", "markdown"),
    ("kbxml", "ht-t-k0-aac.xml", "keyboard/ht-t-k0-aac.xml", "xml"),
    ("freq", "letter-frequency-analysis.md", "docs/letter-frequency-analysis.md", "markdown"),
    ("analysis", "complexity_analysis.md", "docs/aac_complexity_analysis.md", "markdown"),
    ("rules", "rules.json", "converter/rules.json", "json"),
    ("py", "aac_converter.py", "converter/aac_converter.py", "python"),
    ("js", "aac_converter.js", "converter/aac_converter.js", "javascript"),
    ("test", "test_converter.py", "converter/tests/test_converter.py", "python"),
]

HEADER = (
    "/* GÉNÉRÉ par scripts/build.py depuis {source}.\n"
    "   NE PAS ÉDITER À LA MAIN : modifiez la source, puis relancez\n"
    "   `python3 scripts/build.py` (le hook pre-commit le fait pour vous). */\n"
)


def _js(var: str, source: str, data) -> str:
    body = json.dumps(data, ensure_ascii=False, indent=2)
    return HEADER.format(source=source) + f"window.{var} = {body};\n"


def build_rules() -> str:
    rules = json.loads((ROOT / "converter" / "rules.json").read_text(encoding="utf-8"))
    public = {k: v for k, v in rules.items() if not k.startswith("_")}  # sans les notes
    return _js("AAC_RULES", "converter/rules.json", public)


def build_corpus() -> str:
    sys.path.insert(0, str(ROOT / "converter"))
    from corpus import CORPUS  # noqa: E402

    items = []
    for key, entry in CORPUS.items():
        if "titre" not in entry or "sous_afichaj" not in entry:
            raise SystemExit(
                f"corpus.py : l'entrée {key!r} n'a pas de champ 'titre'/'sous_afichaj' "
                "-- requis pour l'affichage web (voir la note en tête de converter/corpus.py)."
            )
        # Texte + libellés seulement : les chiffres sont recalculés dans le
        # navigateur avec toAac(), jamais recopiés.
        item = {"key": key, "titre": entry["titre"], "sous": entry["sous_afichaj"], "texte": entry["texte"]}
        if entry.get("note"):
            item["note"] = entry["note"]
        items.append(item)
    return _js("AAC_CORPUS", "converter/corpus.py", items)


def build_precomputed() -> str:
    """Décomptes de jetons pré-calculés par converter/fertilite_tokenizers.py --export
    (pour les tokeniseurs que la page ne peut pas exécuter, comme NLLB-200)."""
    path = ROOT / "converter" / "fertilite_precomputed.json"
    data = json.loads(path.read_text(encoding="utf-8")) if path.exists() else {"tokenizers": {}}
    public = {k: v for k, v in data.items() if not k.startswith("_")}
    return _js("AAC_PRECOMPUTED", "converter/fertilite_precomputed.json", public)


def build_snapshots() -> str:
    files = {}
    for key, name, rel, lang in VIEWER_FILES:
        raw = (ROOT / rel).read_bytes().replace(b"\r\n", b"\n")  # stable quel que soit autocrlf
        files[key] = {"name": name, "path": rel, "lang": lang, "b64": base64.b64encode(raw).decode("ascii")}
    return _js("AAC_FILES", "README.md, LICENSE, converter/, keyboard/, docs/ (instantané hors-ligne)", files)


def outputs() -> dict[Path, str]:
    return {
        GENERATED / "rules.js": build_rules(),
        GENERATED / "corpus.js": build_corpus(),
        GENERATED / "fertilite_precomputed.js": build_precomputed(),
        GENERATED / "snapshots.js": build_snapshots(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    parser.add_argument("--check", action="store_true", help="vérifier sans écrire (CI)")
    args = parser.parse_args()

    drift = []
    for path, content in outputs().items():
        data = content.encode("utf-8")
        if not path.exists() or path.read_bytes() != data:
            drift.append(path)
            if not args.check:
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_bytes(data)  # écriture binaire : toujours des fins de ligne LF

    names = [p.relative_to(ROOT).as_posix() for p in drift]
    if args.check:
        if drift:
            print("✗ Dérive détectée, fichiers générés périmés :")
            for n in names:
                print(f"  - {n}")
            print("Lancez `python3 scripts/build.py`, puis commitez le résultat.")
            return 1
        print("✓ web-demo/generated/ est à jour.")
        return 0

    if drift:
        print("Régénéré :")
        for n in names:
            print(f"  - {n}")
    else:
        print("✓ Déjà à jour, rien à faire.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
