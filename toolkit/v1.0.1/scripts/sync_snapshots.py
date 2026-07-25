#!/usr/bin/env python3
"""
scripts/sync_snapshots.py
==========================
Remet à jour les instantanés (base64) intégrés dans web-demo/index.html à
partir du contenu RÉEL des fichiers sources sur disque.

Pourquoi ce script existe
--------------------------
La visionneuse de fichiers du site (README, LICENSE, code, clavier) essaie
d'abord de lire les fichiers en direct via fetch() — ça marche quand le
site est servi par un serveur web (GitHub Pages, `python3 -m http.server`,
etc.). Mais quand quelqu'un ouvre index.html directement depuis son disque
(double-clic, `file://`), les navigateurs interdisent fetch() vers d'autres
fichiers locaux : le site retombe alors sur un instantané intégré
directement dans le HTML (encodé en base64), pour que la démo reste
utilisable hors-ligne.

Ce script est ce qui maintient cet instantané synchronisé avec les vrais
fichiers. Sans lui, éditer README.md (ou LICENSE, ou le code) ne change
RIEN à ce que montre la visionneuse en mode hors-ligne, jusqu'à ce que
quelqu'un relance ce script.

Usage
-----
    python3 scripts/sync_snapshots.py

Automatisation
---------------
Ce script tourne automatiquement :
  - à chaque commit, via le hook .githooks/pre-commit (voir
    .githooks/README.md pour l'activer une seule fois) ;
  - à chaque push, via .github/workflows/sync-snapshots.yml (si le dépôt
    est hébergé sur GitHub).

Il est idempotent (ne réécrit le fichier que si quelque chose a réellement
changé) et ne dépend d'aucun paquet externe — seulement la bibliothèque
standard Python.
"""
from __future__ import annotations

import base64
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
INDEX_HTML = ROOT / "web-demo" / "index.html"

# Doit rester synchronisé avec l'objet FILES défini dans web-demo/index.html
FILES: dict[str, str] = {
    "readme": "README.md",
    "license": "LICENSE",
    "py": "converter/acc_converter.py",
    "js": "converter/acc_converter.js",
    "test": "converter/tests/test_converter.py",
    "kbxml": "keyboard/ht-t-k0-aac.xml",
    "kbguide": "keyboard/README.md",
}


def sync(check_only: bool = False) -> tuple[int, list[str]]:
    """Synchronise les instantanés. Retourne (nombre de fichiers modifiés,
    liste des chemins modifiés). Retourne (-1, []) en cas d'erreur fatale.

    check_only=True : ne modifie rien, sert juste à détecter une dérive
    (utile en CI pour vérifier qu'un commit n'a pas oublié de relancer le
    script).
    """
    if not INDEX_HTML.exists():
        print(f"Erreur : {INDEX_HTML} introuvable.", file=sys.stderr)
        return -1, []

    html = INDEX_HTML.read_text(encoding="utf-8")
    changed: list[str] = []
    missing: list[str] = []

    for key, rel_path in FILES.items():
        path = ROOT / rel_path
        if not path.exists():
            missing.append(rel_path)
            continue

        b64 = base64.b64encode(path.read_bytes()).decode("ascii")

        pattern = re.compile(
            r"("
            + re.escape(key)
            + r": \{ name: '[^']*', path: '"
            + re.escape(rel_path).replace("/", r"\/")
            + r"', lang: '[^']*', b64: \")([^\"]*)(\" \})"
        )
        m = pattern.search(html)
        if not m:
            print(
                f"Avètisman : entrée '{key}' ({rel_path}) pa jwenn nan "
                f"index.html, li ignore.",
                file=sys.stderr,
            )
            continue

        if m.group(2) != b64:
            changed.append(rel_path)
            if not check_only:
                html = html[: m.start(2)] + b64 + html[m.end(2) :]

    if missing:
        print("Avètisman : fichye sa yo pa egziste, yo ignore :", file=sys.stderr)
        for m_path in missing:
            print(f"  - {m_path}", file=sys.stderr)

    if changed and not check_only:
        INDEX_HTML.write_text(html, encoding="utf-8")

    return len(changed), changed


def main() -> int:
    check_only = "--check" in sys.argv
    count, changed = sync(check_only=check_only)

    if count < 0:
        return 1

    if count == 0:
        print("✓ Enstantane yo ajou — pa gen chanjman.")
        return 0

    verb = "ta dwe mete ajou" if check_only else "mete ajou"
    print(f"Enstantane {verb} pou {count} fichye :")
    for c in changed:
        print(f"  - {c}")

    if check_only:
        print(
            "\n✗ Dérive détectée : lance `python3 scripts/sync_snapshots.py` "
            "(sans --check) epi komite rezilta a."
        )
        return 1

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
