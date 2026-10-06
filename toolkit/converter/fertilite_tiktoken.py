"""
fertilite_tiktoken.py
======================

Compare la fertilité tokenistique (#tokens / #mots, cf. formule 2.3 de
aac_complexity_analysis.md) entre l'orthographe 1979 et l'AAC, avec le
tokeniseur cl100k_base d'OpenAI (celui de GPT-4 / GPT-3.5).

Installation :
    pip install tiktoken
    python3 -m pip install tiktoken #windows

Usage :
    python3 fertilite_tiktoken.py
    python3 fertilite_tiktoken.py "Chante pou chase lapli nan kò mwen."

Nécessite aac_converter.py (version toolkit, to_aac) dans le même dossier
ou sur le PYTHONPATH.
"""

from __future__ import annotations
import sys
import tiktoken

from aac_converter import to_aac  # remplacer par `to_acc` si vous gardez l'ancien nommage


def fertility_report(text_1979: str, encoding_name: str = "cl100k_base") -> None:
    enc = tiktoken.get_encoding(encoding_name)
    text_aac = to_aac(text_1979)

    tok_1979 = enc.encode(text_1979)
    tok_aac = enc.encode(text_aac)
    n_mots_1979 = len(text_1979.split())
    n_mots_aac = len(text_aac.split())  # identique en nombre de mots, juste au cas où

    print(f"Tokeniseur : {encoding_name}\n")
    print("1979 :", text_1979)
    print("AAC  :", text_aac)
    print()
    print(f"{'':10s} {'mots':>6s} {'tokens':>8s} {'Fert = tokens/mots':>20s} {'octets UTF-8':>14s}")
    print(f"{'1979':10s} {n_mots_1979:6d} {len(tok_1979):8d} {len(tok_1979)/n_mots_1979:20.3f} {len(text_1979.encode('utf-8')):14d}")
    print(f"{'AAC':10s} {n_mots_aac:6d} {len(tok_aac):8d} {len(tok_aac)/n_mots_aac:20.3f} {len(text_aac.encode('utf-8')):14d}")
    print()

    # Détail token par token pour visualiser où les lettres atomiques
    # "coûtent" plus ou moins de tokens que leur digramme d'origine.
    print("--- Détail des tokens AAC (decode de chaque id) ---")
    print([enc.decode([t]) for t in tok_aac])


if __name__ == "__main__":
    texte = sys.argv[1] if len(sys.argv) > 1 else (
        "Chante pou chase lapli nan kò mwen. Grangou ap fè nou mache lwen, "
        "men lengis la rete la. Bekàn Jàn pwofàn, dodàn kay la, ak yon "
        "sandwich pou granmoun ki vle wè bouch li louvri."
    )
    fertility_report(texte)
