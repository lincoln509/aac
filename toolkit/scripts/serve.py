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
    `.githooks/`, `.idea/` -- de l'outillage interne, pas du contenu
    destiné aux visiteurs du site ;
  - il écoute sur toutes les interfaces réseau par défaut (0.0.0.0),
    donc accessible depuis tout le réseau local, pas seulement votre poste.

Ce script corrige les trois points, sans dépendance externe (bibliothèque
standard uniquement), tout en continuant à servir normalement tout ce dont
web-demo/index.html a besoin (README.md, LICENSE, converter/, keyboard/,
docs/, assets/) -- bloquer ces fichiers casserait la visionneuse intégrée
du site, dont c'est justement la fonction de les afficher.

CORRECTIF CRITIQUE (revue de code, C2) — la version précédente comparait
le chemin d'URL BRUT (`self.path`, ex. "/.git/config") à une liste de
préfixes interdits, AVANT tout décodage/normalisation. Elle était donc
contournable de plusieurs façons, toutes vérifiées et corrigées ici :
  - encodage pourcent du point :        /%2egit/config
  - composants "." /  ".." :            /./.git/config , /web-demo/../.git/config
  - casse différente (Windows/macOS) :  /.GIT/config
  - fichiers internes non listés :      /.idea/workspace.xml
Le blocage porte désormais sur le CHEMIN DE FICHIER RÉSOLU (après décodage
et normalisation par `translate_path`, puis `Path.resolve()`), comparé de
façon insensible à la casse au premier composant sous la racine du dépôt --
et non plus sur le texte brut de l'URL. Toute requête qui sort de la racine
du dépôt (traversée de répertoire) est également rejetée explicitement.

Ce script utilise aussi désormais `ThreadingHTTPServer` (un client lent ne
bloque plus les autres) et `allow_reuse_address = True` (redémarrage
immédiat possible après un arrêt, sans "Address already in use").

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
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent

# Noms de dossiers/fichiers internes bloqués (403), quel que soit le
# chemin exact utilisé pour y accéder dans l'URL. Comparaison insensible
# à la casse, sur le PREMIER composant du chemin résolu sous ROOT (voir
# SecureHandler.send_head).
BLOCKED_TOP_LEVEL_NAMES = {
    ".git",
    ".github",
    ".githooks",
    ".idea",
    "scripts",
    ".gitignore",
    ".gitattributes",
}


class SecureHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(ROOT), **kwargs)

    def send_head(self):
        # `translate_path` décode déjà l'URL (%XX) et neutralise les
        # composants "." / ".." de la façon standard de la bibliothèque --
        # mais ce n'est pas suffisant à soi seul : on résout ensuite le
        # chemin obtenu pour retrouver le chemin réel sur le disque, et on
        # vérifie qu'il reste bien SOUS la racine du dépôt.
        try:
            fs_path = Path(self.translate_path(self.path)).resolve()
        except (OSError, ValueError):
            self.send_error(400, "Requête invalide")
            return None

        try:
            rel = fs_path.relative_to(ROOT)
        except ValueError:
            # Le chemin résolu sort de la racine du dépôt (traversée de
            # répertoire) : toujours refusé, quelle que soit la manière
            # dont l'URL l'a exprimé (../, symlink, etc.).
            self.send_error(403, "Aksè entèdi (deyò rasin pwojè a)")
            return None

        if rel.parts and rel.parts[0].lower() in BLOCKED_TOP_LEVEL_NAMES:
            self.send_error(403, "Aksè entèdi (dosye entèn pwojè a)")
            return None

        return super().send_head()

    def list_directory(self, path):
        # Dezaktive lis fichye yo pou nenpòt dosye ki pa gen index.html --
        # anpeche navige nan tout achitekti depo a nan navigatè a.
        self.send_error(403, "Lis dosye dezaktive")
        return None

    def log_message(self, fmt, *args):
        # Format court, plus lisible que le format par défaut
        print(f"  {self.address_string()} — {fmt % args}")


class SecureServer(http.server.ThreadingHTTPServer):
    # CORRECTIF (revue de code, C2, remarque annexe) : évite l'erreur
    # "Address already in use" lors d'un redémarrage rapide du serveur.
    allow_reuse_address = True


def main():
    args = sys.argv[1:]
    port = 8000
    public = "--public" in args
    for a in args:
        if a.isdigit():
            port = int(a)

    host = "" if public else "127.0.0.1"

    with SecureServer((host, port), SecureHandler) as httpd:
        display_host = "0.0.0.0 (rezo lokal)" if public else "127.0.0.1 (sèlman machin sa a)"
        print(f"Sèvè sekirize demare — {display_host}, pò {port}")
        print(f"Ouvri : http://localhost:{port}/web-demo/")
        print("Aksè entèdi (403) pou : " + ", ".join(sorted(BLOCKED_TOP_LEVEL_NAMES)))
        print("Lis dosye (navigasyon achitekti) dezaktive pou tout lòt dosye.")
        print("Ctrl+C pou sispann.\n")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print("\nSèvè a rete.")


if __name__ == "__main__":
    main()
