#!/usr/bin/env python3
"""
sync_corpus.py
===============

CORRECTIF (revue de code) : la section "Validasyon sou N tèks endepandan"
de web-demo/index.html affichait des chiffres codés en dur (140/127
caractères, -9,3 %, le tableau des 8 textes avec leur gain individuel, la
moyenne, l'IC95 %...), recopiés à la main depuis la sortie de
`python3 converter/corpus.py`. Toute modification de converter/corpus.py
(texte ajouté, retiré, modifié) désynchronisait silencieusement la page,
sans qu'aucun mécanisme ne le signale.

Ce script élimine la recopie manuelle : converter/corpus.py (le dict
CORPUS, y compris ses champs d'affichage `titre`/`sous_afichaj`/`note`)
reste l'UNIQUE source, et ce script exporte les données nécessaires (texte
+ libellés -- PAS les chiffres, qui sont recalculés dans le navigateur par
web-demo/index.html à partir de `texte` et de `to_aac()`, avec les mêmes
formules que converter/corpus.py et converter/document_stats.py) entre les
marqueurs

    // AAC-CORPUS:BEGIN
    // AAC-CORPUS:END

Usage :
    python3 scripts/sync_corpus.py            # régénère index.html
    python3 scripts/sync_corpus.py --check    # vérifie la synchronisation
                                                # (CI / hook pre-commit),
                                                # code de sortie != 0 si dérive.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "converter"))

from corpus import CORPUS  # noqa: E402

TARGET = ROOT / "web-demo" / "index.html"
BEGIN = "// AAC-CORPUS:BEGIN"
END = "// AAC-CORPUS:END"


def build_js_corpus() -> list[dict]:
    """Ne garde que les champs nécessaires à l'affichage web (pas `auteur`/
    `source`/`annee`, qui restent les métadonnées "papier" de corpus.py --
    `sous_afichaj` est leur équivalent condensé, en kreyòl, pour la page)."""
    out = []
    for key, entry in CORPUS.items():
        if "titre" not in entry or "sous_afichaj" not in entry:
            raise SystemExit(
                f"corpus.py: l'entrée {key!r} n'a pas de champ 'titre'/"
                "'sous_afichaj' -- requis pour l'affichage web (voir la note "
                "en tête de converter/corpus.py)."
            )
        item = {"key": key, "titre": entry["titre"], "sous": entry["sous_afichaj"], "texte": entry["texte"]}
        if entry.get("note"):
            item["note"] = entry["note"]
        out.append(item)
    return out


def build_block() -> str:
    data = build_js_corpus()
    js = json.dumps(data, ensure_ascii=False, indent=2)
    lines = [
        "  /* Données du corpus de validation -- générées automatiquement",
        "     depuis converter/corpus.py par scripts/sync_corpus.py.",
        "     NE PAS ÉDITER À LA MAIN : éditez converter/corpus.py puis",
        "     relancez `python3 scripts/sync_corpus.py`. */",
        "  const CORPUS = " + js.replace("\n", "\n  ") + ";",
    ]
    return "\n".join(lines)


def sync_file(path: Path, block: str) -> tuple[bool, str]:
    text = path.read_text(encoding="utf-8")
    if BEGIN not in text or END not in text:
        raise SystemExit(
            f"{path}: marqueurs {BEGIN!r}/{END!r} introuvables -- "
            "le fichier a-t-il été modifié en dehors de ce script ?"
        )
    before, rest = text.split(BEGIN, 1)
    _, after = rest.split(END, 1)
    new_text = before + BEGIN + "\n" + block + "\n  " + END + after
    return new_text != text, new_text


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--check", action="store_true", help="vérifier sans écrire (CI)")
    args = parser.parse_args()

    block = build_block()
    changed, new_text = sync_file(TARGET, block)

    if args.check:
        if changed:
            print("Dérive détectée (converter/corpus.py non synchronisé) :")
            print(f"  - {TARGET.relative_to(ROOT)}")
            print("Lancez `python3 scripts/sync_corpus.py` pour corriger.")
            return 1
        print("OK : web-demo/index.html est synchronisé avec converter/corpus.py.")
        return 0

    if changed:
        TARGET.write_text(new_text, encoding="utf-8")
        print(f"Synchronisé : {TARGET.relative_to(ROOT)}")
    else:
        print("Déjà synchronisé, rien à faire.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
