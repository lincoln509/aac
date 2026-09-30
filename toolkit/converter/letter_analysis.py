# -*- coding: utf-8 -*-
"""
letter_analysis.py
===================

Analyse fréquentielle et fonctionnelle des trois lettres atomiques de
l'AAC (š, ŏ, ŋ) sur un texte ou un corpus de textes en orthographe 1979.

Trois niveaux d'analyse, chacun avec ses formules :

  1. Fréquence des lettres atomiques (sur le texte converti en AAC)
  2. Analyse au niveau du mot (couverture lexicale)
  3. Analyse fonctionnelle au niveau de la syllabe (onset / noyau / coda),
     via un syllabeur heuristique CV documenté en bas de fichier.

Toutes les formules sont documentées dans docs/letter-frequency-analysis.md ;
ce module n'en est que l'implémentation.

Note historique : une version antérieure de ce module documentait un écart
entre le comportement de aac_converter.py et le résumé du mémoire (la règle
positionnelle "ng -> ŋ seulement en fin de syllabe" n'était pas appliquée
par le code). Cet écart a été corrigé dans aac_converter.py (voir son
en-tête de fichier) : la fonction syllable_functional_analysis() ci-dessous
sert maintenant aussi de test de non-régression pour cette règle -- voir
test_corpus_wide_ng_is_always_coda dans test_letter_analysis.py.
"""

from __future__ import annotations

import re
import statistics
from dataclasses import dataclass, field

from aac_converter import to_aac

# ---------------------------------------------------------------------------
# 1) Fréquence des lettres atomiques
# ---------------------------------------------------------------------------

ATOMIC_LETTERS = ("š", "ŏ", "ŋ")

# Voyelles reconnues comme noyau syllabique dans le texte AAC (voir
# syllabify() plus bas) : les voyelles orales du 1979 (a à e è i o ò u),
# la voyelle atomique ŏ, et les nasales an/en/on qui restent des digrammes
# à 2 lettres en AAC (non touchées par la réforme) -- leur second membre
# (n) N'EST PAS une voyelle, donc seule la première lettre (a/e/o) compte
# comme noyau ; "an" occupe alors noyau+coda sur un seul phonème nasal.
# NOTE : doit rester synchronisé avec la classe de voyelles utilisée par
# NG_RULE dans aac_converter.py/.js (aeiouàèò, + majuscules) -- "à" a été
# ajouté ici pour lever une incohérence où syllabify() ne reconnaissait
# pas "à" comme noyau et retombait sur une classification "onset" par
# défaut pour tout le mot (y compris pour les lettres atomiques qu'il
# contenait).
VOWELS = set("aeiòèouŏà")


@dataclass
class AtomicFrequencyReport:
    """Fréquences des 3 lettres atomiques sur le texte converti en AAC.

    Formules (N = nombre total de caractères du texte AAC, espaces inclus,
    pour rester cohérent avec le calcul du gain scriptural déjà utilisé
    dans document_stats.py) :

        n_l            = nombre d'occurrences de la lettre l dans le texte AAC
        f_l             = n_l / N                    (fréquence relative)
        f_l_per_100     = f_l * 100                   (pour 100 caractères)
        f_l_per_1000    = f_l * 1000                  (pour 1000 caractères, usage courant en linguistique de corpus)
        D               = (n_š + n_ŏ + n_ŋ) / N       (densité atomique totale)
        p_l             = n_l / (n_š + n_ŏ + n_ŋ)     (part de l parmi les 3 lettres atomiques, somme des p_l = 1)
    """

    text_aac: str
    counts: dict[str, int]
    total_chars: int

    @property
    def relative_frequency(self) -> dict[str, float]:
        if self.total_chars == 0:
            return {l: 0.0 for l in ATOMIC_LETTERS}
        return {l: self.counts[l] / self.total_chars for l in ATOMIC_LETTERS}

    @property
    def per_100_chars(self) -> dict[str, float]:
        return {l: f * 100 for l, f in self.relative_frequency.items()}

    @property
    def per_1000_chars(self) -> dict[str, float]:
        return {l: f * 1000 for l, f in self.relative_frequency.items()}

    @property
    def total_atomic_count(self) -> int:
        return sum(self.counts.values())

    @property
    def atomic_density(self) -> float:
        """D = proportion du texte AAC occupée par une lettre atomique."""
        if self.total_chars == 0:
            return 0.0
        return self.total_atomic_count / self.total_chars

    @property
    def share_among_atomic(self) -> dict[str, float]:
        """p_l : part de chaque lettre parmi les occurrences atomiques (somme = 1)."""
        total = self.total_atomic_count
        if total == 0:
            return {l: 0.0 for l in ATOMIC_LETTERS}
        return {l: self.counts[l] / total for l in ATOMIC_LETTERS}


def atomic_letter_frequencies(text_1979: str) -> AtomicFrequencyReport:
    """Calcule les fréquences des lettres atomiques sur la conversion AAC de text_1979."""
    aac = to_aac(text_1979)
    lower = aac.lower()
    counts = {l: lower.count(l) for l in ATOMIC_LETTERS}
    return AtomicFrequencyReport(text_aac=aac, counts=counts, total_chars=len(aac))


# ---------------------------------------------------------------------------
# 2) Analyse au niveau du mot
# ---------------------------------------------------------------------------

_WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)


def _tokenize_words(text_aac: str) -> list[str]:
    """Découpe un texte AAC en mots (lettres uniquement, ponctuation/chiffres
    exclus). Insensible à la casse pour le comptage des lettres atomiques."""
    return _WORD_RE.findall(text_aac)


@dataclass
class WordLevelReport:
    """Couverture lexicale des lettres atomiques.

    Soit W l'ensemble des mots du texte AAC, |W| son cardinal, et a(w) le
    nombre de lettres atomiques (š/ŏ/ŋ) dans le mot w. Formules :

        C       = |{w in W : a(w) >= 1}| / |W|           (couverture globale)
        C_l     = |{w in W : l apparaît dans w}| / |W|    (couverture par lettre l)
        mu_all  = somme(a(w) pour w in W) / |W|           (moyenne sur TOUS les mots)
        mu_pos  = somme(a(w) pour w in W) / |{w : a(w)>=1}|  (moyenne sur les mots concernés seulement)
    """

    n_words: int
    words_with_atomic: int
    per_letter_word_count: dict[str, int]
    distribution: dict[int, int]  # {nombre de lettres atomiques dans le mot: nombre de mots}
    total_atomic_occurrences: int

    @property
    def coverage(self) -> float:
        if self.n_words == 0:
            return 0.0
        return self.words_with_atomic / self.n_words

    @property
    def per_letter_coverage(self) -> dict[str, float]:
        if self.n_words == 0:
            return {l: 0.0 for l in ATOMIC_LETTERS}
        return {l: c / self.n_words for l, c in self.per_letter_word_count.items()}

    @property
    def mean_per_word_all(self) -> float:
        if self.n_words == 0:
            return 0.0
        return self.total_atomic_occurrences / self.n_words

    @property
    def mean_per_word_concerned(self) -> float:
        if self.words_with_atomic == 0:
            return 0.0
        return self.total_atomic_occurrences / self.words_with_atomic


def word_level_analysis(text_1979: str) -> WordLevelReport:
    aac = to_aac(text_1979)
    words = _tokenize_words(aac)
    per_letter_word_count = {l: 0 for l in ATOMIC_LETTERS}
    distribution: dict[int, int] = {}
    words_with_atomic = 0
    total_occ = 0

    for w in words:
        wl = w.lower()
        a_w = sum(wl.count(l) for l in ATOMIC_LETTERS)
        total_occ += a_w
        distribution[a_w] = distribution.get(a_w, 0) + 1
        if a_w >= 1:
            words_with_atomic += 1
        for l in ATOMIC_LETTERS:
            if l in wl:
                per_letter_word_count[l] += 1

    return WordLevelReport(
        n_words=len(words),
        words_with_atomic=words_with_atomic,
        per_letter_word_count=per_letter_word_count,
        distribution=distribution,
        total_atomic_occurrences=total_occ,
    )


# ---------------------------------------------------------------------------
# 3) Analyse fonctionnelle syllabique (onset / noyau / coda)
# ---------------------------------------------------------------------------
#
# Syllabeur heuristique graphémique (PAS une analyse phonologique complète) :
#
#   - Chaque syllabe contient EXACTEMENT une voyelle-noyau (cf. VOWELS).
#   - Les consonnes entre deux noyaux sont réparties selon la règle
#     d'attaque maximale (principe cross-linguistique standard, adapté aux
#     langues à forte préférence CV comme le créole) :
#       * 1 consonne entre deux voyelles -> attaque (onset) de la syllabe suivante
#       * 2 consonnes entre deux voyelles -> 1 en coda de la syllabe qui
#         précède, 1 en attaque de la syllabe qui suit
#       * 3 consonnes ou plus -> toutes sauf la dernière en coda de la
#         syllabe qui précède, la dernière en attaque de la suivante
#         (cas rare, simplification documentée)
#   - Consonnes avant la première voyelle -> attaque de la 1re syllabe.
#   - Consonnes après la dernière voyelle -> coda de la dernière syllabe.
#
# Limite assumée : ceci est un heuristique orthographique, pas une analyse
# phonologique validée par un linguiste. Il sert à mesurer, de façon
# reproductible, la position structurelle (onset/noyau/coda) où le
# convertisseur PLACE RÉELLEMENT chaque lettre atomique -- pas à trancher
# un débat phonologique.

CONSONANTS_PATTERN = re.compile(r"[^aeiòèouŏà]", re.IGNORECASE)


def syllabify(word: str) -> list[str]:
    """Découpe un mot AAC en syllabes selon l'heuristique CV à attaque maximale."""
    wl = word
    vowel_positions = [i for i, ch in enumerate(wl.lower()) if ch in VOWELS]
    if not vowel_positions:
        return [wl] if wl else []

    # bornes de chaque syllabe : (début, fin_exclusive)
    bounds = []
    start = 0
    for idx, v in enumerate(vowel_positions):
        if idx == len(vowel_positions) - 1:
            end = len(wl)  # dernière syllabe : va jusqu'à la fin du mot
        else:
            next_v = vowel_positions[idx + 1]
            n_consonants = next_v - v - 1
            if n_consonants <= 1:
                cut = v + 1  # 0 ou 1 consonne -> tout part en attaque de la suivante
            else:
                cut = v + 1 + (n_consonants - 1)  # attaque max = 1 seule consonne devant la voyelle suivante
            end = cut
        bounds.append((start, end))
        start = end

    return [wl[a:b] for a, b in bounds if b > a]


def _classify_position(syllable: str, letter_index: int) -> str:
    """onset (avant le noyau), nucleus (le noyau lui-même), ou coda (après)."""
    vowel_positions = [i for i, ch in enumerate(syllable.lower()) if ch in VOWELS]
    if not vowel_positions:
        return "onset"  # syllabe dégénérée (rare) : tout est attaque par convention
    nucleus = vowel_positions[0]
    if letter_index < nucleus:
        return "onset"
    if letter_index == nucleus:
        return "nucleus"
    return "coda"


@dataclass
class SyllableFunctionalReport:
    """Répartition onset/nucleus/coda de chaque lettre atomique, mesurée sur
    le texte AAC syllabé mot par mot avec syllabify()."""

    positions: dict[str, dict[str, int]]  # {lettre: {"onset":n, "nucleus":n, "coda":n}}
    n_words: int
    n_syllables: int

    def summary(self) -> str:
        lines = []
        for l in ATOMIC_LETTERS:
            p = self.positions[l]
            total = sum(p.values())
            if total == 0:
                lines.append(f"{l}: aucune occurrence")
                continue
            parts = ", ".join(f"{k}={v} ({v/total*100:.0f}%)" for k, v in p.items() if v)
            lines.append(f"{l}: {total} occurrence(s) — {parts}")
        return "\n".join(lines)


def syllable_functional_analysis(text_1979: str) -> SyllableFunctionalReport:
    aac = to_aac(text_1979)
    words = _tokenize_words(aac)
    positions = {l: {"onset": 0, "nucleus": 0, "coda": 0} for l in ATOMIC_LETTERS}
    n_syllables = 0

    for w in words:
        syllables = syllabify(w)
        n_syllables += len(syllables)
        for syl in syllables:
            for i, ch in enumerate(syl.lower()):
                if ch in ATOMIC_LETTERS:
                    pos = _classify_position(syl, i)
                    positions[ch][pos] += 1

    return SyllableFunctionalReport(positions=positions, n_words=len(words), n_syllables=n_syllables)


# ---------------------------------------------------------------------------
# Rapport combiné
# ---------------------------------------------------------------------------

def full_report(text_1979: str) -> dict:
    freq = atomic_letter_frequencies(text_1979)
    word = word_level_analysis(text_1979)
    syl = syllable_functional_analysis(text_1979)
    return {"frequency": freq, "word_level": word, "syllable_functional": syl}


def corpus_report(texts: dict[str, str]) -> dict:
    """Agrège l'analyse sur plusieurs textes (ex. converter/corpus.py) et
    calcule mean/stdev/min/max de la densité atomique (D) entre documents,
    même méthodologie que build_multi_document_report() dans document_stats.py."""
    per_doc = {name: atomic_letter_frequencies(t) for name, t in texts.items()}
    densities = [r.atomic_density * 100 for r in per_doc.values()]
    agg = {
        "per_document": per_doc,
        "n_documents": len(densities),
        "mean_density_percent": statistics.mean(densities) if densities else 0.0,
        "stdev_density_percent": statistics.stdev(densities) if len(densities) > 1 else 0.0,
        "min_density_percent": min(densities) if densities else 0.0,
        "max_density_percent": max(densities) if densities else 0.0,
    }
    return agg


if __name__ == "__main__":
    import sys

    if "--corpus" in sys.argv:
        # python3 letter_analysis.py --corpus : fréquence + fonction
        # syllabique agrégées sur les 8 textes de corpus.py.
        from corpus import CORPUS

        texts = {k: v["texte"] for k, v in CORPUS.items()}
        agg = corpus_report(texts)
        print("=== Densité atomique par texte ===")
        for name, r in agg["per_document"].items():
            print(f"  {name:22s} n_š={r.counts['š']:3d} n_ŏ={r.counts['ŏ']:3d} n_ŋ={r.counts['ŋ']:2d}  D={r.atomic_density*100:5.2f}%")
        print(
            f"  moyenne={agg['mean_density_percent']:.2f}%  "
            f"min={agg['min_density_percent']:.2f}%  max={agg['max_density_percent']:.2f}%  "
            f"écart-type={agg['stdev_density_percent']:.2f}%"
        )
        print()
        tout = " ".join(texts.values())
        w = word_level_analysis(tout)
        print("=== Analyse lexicale agrégée (8 textes) ===")
        print(f"  {w.n_words} mots, couverture globale C = {w.coverage*100:.1f}%")
        print(f"  Couverture par lettre : {[(l, f'{c*100:.1f}%') for l, c in w.per_letter_coverage.items()]}")
        print(f"  Moyenne/mot (tous) = {w.mean_per_word_all:.3f} ; moyenne/mot (concernés) = {w.mean_per_word_concerned:.3f}")
        print()
        print("=== Analyse fonctionnelle syllabique agrégée (8 textes) ===")
        print(syllable_functional_analysis(tout).summary())
        sys.exit(0)

    text = sys.argv[1] if len(sys.argv) > 1 else (
        "Chante pou chase lapli nan kò mwen, chante pou san mwen rete cho nan "
        "tanpèt la, pou klète lang manman nou klere sou ekran toupatou sou latè."
    )
    r = full_report(text)
    print("=== Fréquence des lettres atomiques ===")
    for l in ATOMIC_LETTERS:
        f = r["frequency"]
        print(f"  {l}: n={f.counts[l]:3d}  f={f.relative_frequency[l]*100:.2f}/100car  part={f.share_among_atomic[l]*100:.1f}%")
    print(f"  Densité atomique totale D = {r['frequency'].atomic_density*100:.2f}%")
    print()
    print("=== Analyse lexicale ===")
    w = r["word_level"]
    print(f"  {w.n_words} mots, couverture globale C = {w.coverage*100:.1f}%")
    print(f"  Couverture par lettre : {[(l, f'{c*100:.1f}%') for l, c in w.per_letter_coverage.items()]}")
    print(f"  Moyenne/mot (tous) = {w.mean_per_word_all:.3f} ; moyenne/mot (concernés) = {w.mean_per_word_concerned:.3f}")
    print()
    print("=== Analyse fonctionnelle syllabique ===")
    print(r["syllable_functional"].summary())
    print()
    print("Astuce : python3 letter_analysis.py --corpus pour l'agrégat sur les 8 textes de corpus.py.")
