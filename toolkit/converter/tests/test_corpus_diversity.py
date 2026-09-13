"""Tests du corpus multi-auteurs (corpus.py).

Remplace l'ancienne validation à un seul extrait ("9,3 % sur le corpus
Depestre", qui en plus était mal attribué — voir test_converter.py) par
une validation sur 8 textes indépendants et de sources diverses :
2 textes personnels de l'auteur, un texte légal (Constitution 1987), un
texte international (DUDH, traduction officielle OHCHR), 2 lots de
pwovèb kreyòl (tradition orale), et 2 extraits littéraires du domaine
public (Oswald Durand 1883, Georges Sylvain 1901 — tous deux morts il
y a un siècle ou plus).

Ce test fige l'écart réellement mesuré : si quelqu'un modifie corpus.py
ou acc_converter.py d'une façon qui change sensiblement ces chiffres,
ce test doit échouer et la documentation (README.md) doit être mise à
jour en conséquence — pas l'inverse.
"""

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from corpus import CORPUS, as_documents
from document_stats import build_multi_document_report


def test_corpus_has_at_least_four_distinct_authors():
    """L'objectif de départ ('plus de 4 auteurs différents') doit être
    tenu : on compte les catégories d'auteurs/sources distinctes, pas
    seulement le nombre de textes."""
    auteurs = {entry["auteur"] for entry in CORPUS.values()}
    assert len(CORPUS) >= 5
    assert len(auteurs) >= 5


def test_no_copyrighted_living_or_recent_author():
    """Garde-fou explicite : aucun texte d'un auteur dont l'œuvre reste
    sous droits ne doit être réintroduit ici (Frankétienne, René
    Depestre, Georges Castera — voir la discussion dans README.md)."""
    noms_interdits = ("frankétienne", "franketienne", "depestre", "castera")
    for entry in CORPUS.values():
        auteur_lower = entry["auteur"].lower()
        assert not any(nom in auteur_lower for nom in noms_interdits), (
            f"Auteur potentiellement encore sous droits détecté : {entry['auteur']}"
        )


def test_per_document_gain_range_matches_measured_values():
    """Fige l'écart réellement mesuré (2,5 % à 9,3 %) sur les 8 textes.
    Si ce test échoue, corriger le README avant de corriger le test."""
    multi = build_multi_document_report(as_documents())
    gains = [r.gain_percent_global for r in multi.per_document.values()]

    assert len(gains) == len(CORPUS)
    assert round(min(gains), 1) == 2.5
    assert round(max(gains), 1) == 9.3


def test_pooled_mean_and_ci_match_measured_values():
    multi = build_multi_document_report(as_documents())
    assert round(multi.pooled.mean_gain_percent, 1) == 5.7
    lo, hi = multi.pooled.ci95_gain_percent
    assert round(lo, 1) == 3.9
    assert round(hi, 1) == 7.5


def test_gain_is_never_negative_and_never_absurdly_high():
    """Garde-fou de bon sens : le gain doit toujours être dans [0, 25] %
    pour un texte créole ordinaire — au-delà, c'est le signe d'un bug
    (ex. double conversion) ou d'un texte non représentatif."""
    multi = build_multi_document_report(as_documents())
    for name, r in multi.per_document.items():
        assert 0 <= r.gain_percent_global <= 25, f"{name}: {r.gain_percent_global}"


if __name__ == "__main__":
    import subprocess

    subprocess.run([sys.executable, "-m", "pytest", __file__, "-v"])
