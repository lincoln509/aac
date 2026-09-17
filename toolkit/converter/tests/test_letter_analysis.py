# -*- coding: utf-8 -*-
"""Tests pour letter_analysis.py — fréquence et analyse fonctionnelle
des lettres atomiques (š, ŏ, ŋ).
"""

import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from letter_analysis import (
    ATOMIC_LETTERS,
    atomic_letter_frequencies,
    word_level_analysis,
    syllabify,
    syllable_functional_analysis,
    corpus_report,
)
from corpus import CORPUS


# ---------------------------------------------------------------------------
# 1) Fréquence des lettres atomiques
# ---------------------------------------------------------------------------

def test_frequency_counts_match_manual_count():
    text = "chante pou chase lapli"  # AAC: šante pŏ šase lapli -> š:2, ŏ:1, ŋ:0
    r = atomic_letter_frequencies(text)
    assert r.counts["š"] == 2
    assert r.counts["ŏ"] == 1
    assert r.counts["ŋ"] == 0


def test_relative_frequency_is_count_over_total_chars():
    text = "chante"  # AAC: šante (6 caractères), š compte 1 fois
    r = atomic_letter_frequencies(text)
    assert r.total_chars == len("šante")
    assert abs(r.relative_frequency["š"] - 1 / len("šante")) < 1e-9


def test_share_among_atomic_sums_to_one():
    text = "Chante pou chase lapli nan kò mwen, chante pou san mwen rete cho nan tanpèt la, pou klète lang manman nou klere sou ekran toupatou sou latè."
    r = atomic_letter_frequencies(text)
    total_share = sum(r.share_among_atomic.values())
    assert abs(total_share - 1.0) < 1e-9


def test_atomic_density_is_total_over_chars():
    text = "chante"
    r = atomic_letter_frequencies(text)
    assert abs(r.atomic_density - r.total_atomic_count / r.total_chars) < 1e-9


def test_empty_text_does_not_crash():
    r = atomic_letter_frequencies("")
    assert r.total_chars == 0
    assert all(v == 0.0 for v in r.relative_frequency.values())
    assert r.atomic_density == 0.0


# ---------------------------------------------------------------------------
# 2) Analyse au niveau du mot
# ---------------------------------------------------------------------------

def test_word_coverage_basic():
    text = "chante lapli"  # 2 mots, "chante"->šante (1 atomique), "lapli" (0)
    w = word_level_analysis(text)
    assert w.n_words == 2
    assert w.words_with_atomic == 1
    assert abs(w.coverage - 0.5) < 1e-9


def test_mean_per_word_concerned_ignores_zero_words():
    text = "chante lapli chemen"  # šante(1), lapli(0), šemen(1) -> concernés: 2 mots, 2 occurrences
    w = word_level_analysis(text)
    assert w.mean_per_word_concerned == 1.0
    assert abs(w.mean_per_word_all - 2 / 3) < 1e-9


def test_distribution_sums_to_word_count():
    text = "chante pou chase lapli nan kò mwen"
    w = word_level_analysis(text)
    assert sum(w.distribution.values()) == w.n_words


# ---------------------------------------------------------------------------
# 3) Syllabation heuristique et analyse fonctionnelle
# ---------------------------------------------------------------------------

def test_syllabify_single_vowel_word():
    assert syllabify("laŋ") == ["laŋ"]  # une seule voyelle -> une seule syllabe


def test_syllabify_single_consonant_between_vowels_goes_to_onset():
    # "šante" : š-a-n-t-e -> voyelles a(idx1) et e(idx4), 2 consonnes (n,t) entre les deux
    # règle attaque max à 2 consonnes : 1 en coda précédente, 1 en attaque suivante
    assert syllabify("šante") == ["šan", "te"]


def test_syllabify_ekran_two_consonants_split():
    assert syllabify("ekran") == ["ek", "ran"]


def test_o_breve_is_always_nucleus():
    """ŏ vient toujours de 'ou' (voyelle) : il doit toujours être noyau,
    quel que soit le mot testé du corpus."""
    for entry in CORPUS.values():
        rep = syllable_functional_analysis(entry["texte"])
        if rep.positions["ŏ"]["onset"] or rep.positions["ŏ"]["coda"]:
            raise AssertionError(f"ŏ trouvé hors noyau dans : {entry['texte'][:60]}")


def test_ng_positional_rule_is_now_correctly_enforced():
    """La règle positionnelle décrite dans le mémoire ("ng" -> "ŋ"
    seulement en fin de syllabe/mot) est maintenant réellement appliquée
    par acc_converter.py (corrigé -- voir acc_converter.py, en-tête de
    fichier, et l'historique git pour le commit correspondant).

    'grangou' (gran-gou) : le "g" commence la syllabe suivante -> "ng" ne
    fusionne PAS, contrairement à 'lang'/'long' (ng en fin de mot)."""
    from acc_converter import to_acc

    assert to_acc("grangou") == "grangŏ"
    assert to_acc("lingis") == "lingis"
    assert to_acc("lang") == "laŋ"
    assert to_acc("long") == "loŋ"
    assert to_acc("Bleng-bleng") == "Bleŋ-bleŋ"
    assert to_acc("bling-blong") == "bliŋ-bloŋ"

    syllables = syllabify(to_acc("grangou"))
    assert not any(syl.startswith("ŋ") for syl in syllables), (
        "ŋ ne doit plus jamais apparaître en attaque de syllabe : la règle "
        "positionnelle garantit qu'il n'existe qu'en fin de syllabe (coda)."
    )


def test_ch_final_word_is_coda_not_onset():
    """'bouch' (mouth) se termine par 'ch' -> š doit être classé coda, pas onset."""
    rep = syllable_functional_analysis("bouch")
    assert rep.positions["š"]["coda"] == 1
    assert rep.positions["š"]["onset"] == 0


# ---------------------------------------------------------------------------
# 4) Rapport agrégé sur le corpus (corpus.py)
# ---------------------------------------------------------------------------

def test_corpus_report_covers_all_eight_texts():
    texts = {k: v["texte"] for k, v in CORPUS.items()}
    agg = corpus_report(texts)
    assert agg["n_documents"] == 8
    assert agg["min_density_percent"] <= agg["mean_density_percent"] <= agg["max_density_percent"]


def test_corpus_wide_sh_is_not_always_onset():
    """Fige la mesure réelle sur les 8 textes : š n'est pas 100% onset
    (contrairement à une hypothèse naïve), car 'ch' final existe (ex. 'bouch')."""
    texts = {k: v["texte"] for k, v in CORPUS.items()}
    tout = " ".join(texts.values())
    rep = syllable_functional_analysis(tout)
    total_sh = sum(rep.positions["š"].values())
    assert total_sh > 0
    assert rep.positions["š"]["coda"] > 0, "aucune occurrence coda de š trouvée sur le corpus"
    assert rep.positions["š"]["onset"] > 0


def test_corpus_wide_ng_is_always_coda():
    """Conséquence directe de la règle positionnelle (maintenant appliquée
    par acc_converter.py, voir test_ng_positional_rule_is_now_correctly_
    enforced) : sur les 8 textes du corpus, ŋ n'apparaît plus jamais qu'en
    coda. S'il apparaissait en onset, ce serait la preuve d'une régression
    de la règle positionnelle."""
    texts = {k: v["texte"] for k, v in CORPUS.items()}
    tout = " ".join(texts.values())
    rep = syllable_functional_analysis(tout)
    total_ng = sum(rep.positions["ŋ"].values())
    assert total_ng > 0
    assert rep.positions["ŋ"]["onset"] == 0
    assert rep.positions["ŋ"]["coda"] == total_ng


if __name__ == "__main__":
    import subprocess

    subprocess.run([sys.executable, "-m", "pytest", __file__, "-v"])
