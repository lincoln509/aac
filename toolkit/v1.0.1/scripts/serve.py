#!/usr/bin/env python3
"""
scripts/serve.py
==================
Serveur de développement local pour tester acc-toolkit/ avant déploiement,
qui NE fait PAS ce que `python3 -m http.server` fait par défaut :

  - `http.server` nu liste le contenu de n'importe quel dossier sans
    index.html (navigation complète de l'arborescence dans le navigateur) ;
  - il sert absolument tout ce qu'il trouve, y compris `.git/` (historique
    complet, potentiellement sensible), `scripts/`, `.github/`,
    `.githooks/` — de l'outillage interne, pas du contenu destiné aux
    visiteurs du site ;
  - il écoute sur toutes les interfaces réseau par défaut (0.0.0.0),
    donc accessible depuis tout le réseau local, pas seulement votre poste.

Ce script corrige les trois points, sans dépendance externe (bibliothèque
standard uniquement), tout en continuant à servir normalement tout ce dont
web-demo/index.html a besoin (README.md, LICENSE, converter/, keyboard/,
docs/, assets/) — bloquer ces fichiers casserait la visionneuse intégrée
du site, dont c'est justement la fonction de les afficher.

Usage
-----
    python3 scripts/serve.py                # http://127.0.0.1:8000/
    python3 scripts/serve.py 8080            # port différent
    python3 scripts/serve.py --public        # accessible depuis le réseau local
    python3 scripts/serve.py 8080 --public   # les deux

Puis ouvrez http://localhost:8000/web-demo/
"""
from __future__ import annotations

import http.server
import socketserver
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Chemins bloqués (403) quel que soit le fichier demandé à l'intérieur —
# outillage interne, jamais destiné aux visiteurs du site.
BLOCKED_PREFIXES = (
    "/.git",
    "/.github",
    "/.githooks",
    "/scripts",
    "/.gitignore",
)


class SecureHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def send_head(self):
        path_only = self.path.split("?", 1)[0]
        for prefix in BLOCKED_PREFIXES:
            if path_only == prefix or path_only.startswith(prefix + "/"):
                self.send_error(403, "Aksè entèdi (dosye entèn pwojè a)")
                return None
        return super().send_head()

    def list_directory(self, path):
        # Dezaktive lis fichye yo pou nenpòt dosye ki pa gen index.html —
        # anpeche navige nan tout achitekti depo a nan navigatè a.
        self.send_error(403, "Lis dosye dezaktive")
        return None

    def log_message(self, fmt, *args):
        # Format court, plus lisible que le format par défaut
        print(f"  {self.address_string()} — {fmt % args}")


def main():
    args = sys.argv[1:]
    port = 8000
    public = "--public" in args
    for a in args:
        if a.isdigit():
            port = int(a)

    host = "" if public else "127.0.0.1"

    with socketserver.TCPServer((host, port), SecureHandler) as httpd:
        display_host = "0.0.0.0 (rezo lokal)" if public else "127.0.0.1 (sèlman machin sa a)"
        print(f"Sèvè sekirize demare — {display_host}, pò {port}")
        print(f"Ouvri : http://localhost:{port}/web-demo/")
        print("Aksè entèdi (403) pou : " + ", ".join(BLOCKED_PREFIXES))
        print("Lis dosye (navigasyon achitekti) dezaktive pou tout lòt dosye.")
        print("Ctrl+C pou sispann.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nSèvè a rete.")


if __name__ == "__main__":
    main()
