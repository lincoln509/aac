#!/usr/bin/env python3
"""
sync_converter.py
==================

CORRECTIF (revue de code, C3 — "quatre copies du convertisseur, déjà
divergentes") : avant ce correctif, le code JavaScript du convertisseur
(converter/aac_converter.js) était recopié À LA MAIN dans trois pages HTML
(web-demo/index.html, web-demo/jwet.html, web-demo/documents.html), avec
pour résultat des copies déjà différentes du fichier source (lexique
périmé, comptage de "ng" incohérent...).

Ce script élimine la copie manuelle : converter/aac_converter.js reste
l'UNIQUE source, et ce script l'injecte tel quel entre les marqueurs

    // AAC-CONVERTER:BEGIN
    // AAC-CONVERTER:END

présents dans chacune des pages HTML ci-dessus. Le code reste inliné
(plutôt que chargé via <script src="...">) pour continuer à fonctionner
à l'ouverture directe des fichiers HTML dans un navigateur, sans serveur
local.

Usage :
    python3 scripts/sync_converter.py            # régénère les 3 pages
    python3 scripts/sync_converter.py --check    # vérifie la synchronisation
                                                  # (utilisé par la CI et le
                                                  # hook pre-commit), code de
                                                  # sortie != 0 si dérive.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
SOURCE = ROOT / "converter" / "aac_converter.js"

TARGETS = [
    ROOT / "web-demo" / "index.html",
    ROOT / "web-demo" / "jwet.html",
    ROOT / "web-demo" / "documents.html",
]

BEGIN = "// AAC-CONVERTER:BEGIN"
END = "// AAC-CONVERTER:END"


def build_block(source_code: str) -> str:
    # Indentation à 2 espaces pour rester lisible dans les <script> des
    # pages HTML (qui utilisent déjà cette convention).
    lines = source_code.rstrip("\n").split("\n")
    return "\n".join("  " + line if line else line for line in lines)


def sync_file(path: Path, block: str) -> tuple[bool, str]:
    """Renvoie (a_changé, nouveau_contenu)."""
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

    source_code = SOURCE.read_text(encoding="utf-8")
    block = build_block(source_code)

    drift = []
    for target in TARGETS:
        changed, new_text = sync_file(target, block)
        if changed:
            drift.append(target)
            if not args.check:
                target.write_text(new_text, encoding="utf-8")

    if args.check:
        if drift:
            print("Dérive détectée (converter/aac_converter.js non synchronisé) :")
            for t in drift:
                print(f"  - {t.relative_to(ROOT)}")
            print("Lancez `python3 scripts/sync_converter.py` pour corriger.")
            return 1
        print("OK : les 3 pages web-demo sont synchronisées avec aac_converter.js.")
        return 0

    if drift:
        print("Synchronisé :")
        for t in drift:
            print(f"  - {t.relative_to(ROOT)}")
    else:
        print("Déjà synchronisé, rien à faire.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
