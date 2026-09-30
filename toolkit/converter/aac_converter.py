"""
aac_converter.py
=================

Convertisseur bidirectionnel entre l'orthographe officielle du créole
haïtien (décret du 28 septembre 1979) et l'Alphabet Atomique Créole (AAC),
tel que défini dans le mémoire « Pour une Rationalisation Atomique de la
Graphie Créole Haïtienne ».

Règles appliquées (voir Chapitre III du mémoire) :
    ch  -> š   (U+0161)   /ʃ/
    ou  -> ŏ   (U+014F)   /u/   (et donc "oun" -> "ŏn" automatiquement)
    ng  -> ŋ   (U+014B)   /ŋ/   -- SEULEMENT en fin de syllabe/mot (voir plus bas)
    ui  -> wi             /ɥi/ ~ /jw/

Séquences volontairement NON modifiées (déjà transparentes) :
    an, en, on

Règle positionnelle de "ng" -> "ŋ" (Chapitre III du mémoire) :
    "ng" ne représente le phonème nasal unique /ŋ/ que lorsque le "n" ferme
    une syllabe et que le "g" ne peut pas commencer la syllabe suivante --
    en pratique, quand "ng" n'est PAS suivi d'une voyelle (fin de mot, fin
    de composant dans un mot composé, ou suivi d'une consonne). Quand "ng"
    est suivi d'une voyelle, "n" et "g" sont deux consonnes distinctes
    appartenant à deux syllabes différentes (le "g" commence la syllabe
    suivante) et ne fusionnent PAS :
        laŋ, loŋ, bleŋ-bleŋ, bliŋ-bloŋ   (ng en fin de syllabe -> ŋ)
        grangŏ (gran-gou), lengis (len-gis)   (ng suivi d'une voyelle -> inchangé)
    Cette règle doit être évaluée AVANT la règle "ou" -> "ŏ" : sinon la
    voyelle qui suit "ng" est déjà consommée par "ou" au moment du test, et
    la condition "pas suivi d'une voyelle" devient toujours vraie à tort
    (c'était le bug de la version précédente : "grangou" -> "graŋŏ").

Ce module est volontairement dépourvu de dépendances externes.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Table des règles (1979 -> AAC), appliquées dans cet ordre précis.
# L'ordre importe :
#   1. "ng" doit être évaluée AVANT "ou" (voir note ci-dessus sur la règle
#      positionnelle -- sinon la voyelle qui suit "ng" est déjà remplacée).
#   2. "ou" doit être traitée avant que "ch" ne puisse interférer sur les
#      mêmes segments de texte (aucune interaction directe en pratique,
#      mais l'ordre est conservé pour rester proche de la version d'origine).
# ---------------------------------------------------------------------------

# "ng" -> "ŋ" seulement si NON suivi d'une voyelle (limite de syllabe).
# Regex plutôt que .replace() simple : c'est la seule règle qui a besoin
# de regarder le caractère suivant avant de décider.
_NG_RULE = re.compile(r"(Ng|NG|ng|nG)(?![aeiouàèòAEIOUÀÈÒ])")
_NG_REPLACEMENTS = {"Ng": "Ŋ", "NG": "Ŋ", "ng": "ŋ", "nG": "ŋ"}

# CORRECTIF (revue de code) — casse mixte non gérée ("OUI" -> "ŎI" -> "OuI").
# Les règles ne couvraient que 3 casses figées (bas de casse, Titre, MAJ) par
# séquence, alors que diff_summary() comptait, lui, toutes les combinaisons de
# casse ([Cc][Hh], [Oo][Uu]...). Les deux fonctions utilisent maintenant les
# mêmes règles insensibles à la casse, qui préservent la casse d'origine.
def _make_case_preserving_sub(pattern: str, lower_repl: str):
    """Construit une regex insensible à la casse et une fonction de
    remplacement qui choisit la casse du résultat selon celle du texte
    trouvé : MAJUSCULES -> MAJUSCULES, Titre -> Titre, minuscules -> minuscules."""
    rx = re.compile(pattern, re.IGNORECASE)

    def repl(m: re.Match) -> str:
        found = m.group(0)
        if found.isupper():
            return lower_repl.upper()
        if found[0].isupper():
            return lower_repl[0].upper() + lower_repl[1:]
        return lower_repl

    return rx, repl


_FORWARD_RULES = [
    _make_case_preserving_sub(r"ou", "ŏ"),
    _make_case_preserving_sub(r"ch", "š"),
    _make_case_preserving_sub(r"ui", "wi"),
]

# CORRECTIF (revue de code, suite de M5) — casse en conversion inverse.
#
# Un digramme 1979 de 2 lettres ("ch", "ou", "ng") est compressé en 1 seul
# codepoint AAC ("š", "ŏ", "ŋ"), qui n'a que 2 formes de casse (majuscule /
# minuscule) alors que le digramme d'origine en a 3 ("ch"/"Ch"/"CH"). Décider
# de la casse à partir du SEUL caractère trouvé (ex. Š.isupper() est toujours
# vrai) ne peut donc pas distinguer "Ch" (Titre) de "CH" (MAJUSCULES) : c'est
# ce qui causait le "MOUN -> MŎN -> MOuN" du rapport de revue.
#
# Correctif : la casse est décidée au niveau du MOT entier plutôt que du
# caractère isolé, en observant les autres lettres (normales ou spéciales)
# du même mot :
#   - mot tout en majuscules (ex. "CHAK", "MŎN")      -> digramme en MAJUSCULES
#   - mot tout en minuscules (ex. "chak", "mŏn")       -> digramme en minuscules
#   - mot à initiale majuscule seule (ex. "Šak")       -> digramme en Titre
#     (majuscule seulement si le caractère spécial est en tête de mot)
#   - casse interne réellement imprévisible (rare)     -> repli sur l'ancien
#     comportement caractère par caractère (documenté, non garanti correct)
_BACKWARD_MAP_LOWER = {"š": "ch", "ŏ": "ou", "ŋ": "ng"}
_WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)


def _word_case_mode(word: str) -> str:
    cased = [c for c in word if c.isalpha()]
    if not cased:
        return "lower"
    if all(c.isupper() for c in cased):
        return "upper"
    if all(c.islower() for c in cased):
        return "lower"
    if cased[0].isupper() and all(c.islower() for c in cased[1:]):
        return "title"
    return "mixed"  # casse interne imprévisible : repli caractère par caractère


def _decode_word(word: str) -> str:
    mode = _word_case_mode(word)
    out = []
    for i, ch in enumerate(word):
        lower_ch = ch.lower()
        digraph = _BACKWARD_MAP_LOWER.get(lower_ch)
        if digraph is None:
            out.append(ch)
            continue
        if mode == "upper":
            out.append(digraph.upper())
        elif mode == "title":
            out.append(digraph[0].upper() + digraph[1:] if i == 0 else digraph)
        elif mode == "lower":
            out.append(digraph)
        else:  # "mixed" : repli sur la casse du caractère spécial lui-même
            out.append(digraph.upper() if ch.isupper() else digraph)
    return "".join(out)


def _decode_backward_digraphs(text: str) -> str:
    return _WORD_RE.sub(lambda m: _decode_word(m.group(0)), text)

# ---------------------------------------------------------------------------
# CORRECTIF (revue de code) — "wi" -> "ui" en conversion inverse.
#
# Bug initial : la version précédente convertissait TOUT "wi" en "ui" sauf
# une poignée d'exceptions ("wi", "kiwi", "sandwich"...). Or "wi" est une
# séquence banale de l'orthographe 1979 (swiv, lwil, kwit, nwit, pwi, fwi...)
# qui n'a jamais été écrite "ui". Dans le corpus de référence du mémoire
# (converter/corpus.py), "ui" n'apparaît qu'UNE seule fois (« toutsuit ») et
# aucun mot du corpus ne dérive de "wi". Il n'existe donc aujourd'hui aucune
# preuve de corpus justifiant une conversion mécanique "wi" -> "ui" : la
# règle a été inversée de liste noire (tout convertir sauf exceptions) en
# liste blanche (ne rien convertir, sauf mots explicitement confirmés).
#
# Comportement par défaut : "wi" est laissé identique (choix sûr). Le
# paramètre `convert_wi` de to_1979() permet un usage explicite :
#   - "none"    (défaut) : "wi" n'est jamais reconverti en "ui".
#   - "lexicon" : seuls les mots de WI_WORDS_FROM_UI (liste blanche, VIDE
#                 tant qu'aucun mot n'est confirmé par un linguiste ou un
#                 corpus de référence) sont reconvertis en "ui".
#   - "always"  : ancien comportement mécanique, gardé uniquement pour
#                 compatibilité/tests -- NE PAS utiliser sur du texte réel.
# ---------------------------------------------------------------------------

# Mots confirmés comme s'écrivant "ui" en orthographe 1979 (donc à reconvertir
# depuis leur forme AAC "wi"). Vide par défaut : à compléter uniquement sur
# preuve de corpus ou validation linguistique, jamais par supposition.
WI_WORDS_FROM_UI: set[str] = set()

# Conservé pour compatibilité ascendante avec l'ancien nom ; n'est plus
# utilisé par to_1979 (qui fonctionne désormais par liste blanche).
WI_WORDS_NEVER_FROM_UI: set[str] = {
    "wi",         # oui
    "kiwi",       # emprunt
    "sandwich",   # déjà "sandwich" en 1979, jamais "sanduich"
    "sandwitch",  # variante orthographique locale, même raison
}


@dataclass
class ConversionReport:
    """Statistiques d'une conversion, utiles pour l'analyse quantitative
    du chapitre IV du mémoire (gain scriptural)."""

    original: str
    converted: str
    substitutions: dict = field(default_factory=dict)

    @property
    def chars_total_before(self) -> int:
        return len(self.original)

    @property
    def chars_total_after(self) -> int:
        return len(self.converted)

    @property
    def chars_no_space_before(self) -> int:
        return len(self.original.replace(" ", ""))

    @property
    def chars_no_space_after(self) -> int:
        return len(self.converted.replace(" ", ""))

    @property
    def gain_percent_total(self) -> float:
        if self.chars_total_before == 0:
            return 0.0
        return (self.chars_total_before - self.chars_total_after) / self.chars_total_before * 100

    @property
    def gain_percent_no_space(self) -> float:
        if self.chars_no_space_before == 0:
            return 0.0
        return (self.chars_no_space_before - self.chars_no_space_after) / self.chars_no_space_before * 100


def to_aac(text: str) -> str:
    """Convertit un texte de l'orthographe officielle 1979 vers l'AAC."""
    result = _NG_RULE.sub(lambda m: _NG_REPLACEMENTS[m.group(1)], text)
    for rx, repl in _FORWARD_RULES:
        result = rx.sub(repl, result)
    return result


def to_1979(text: str, *, convert_wi: str = "none", use_lexicon: bool | None = None) -> str:
    """Convertit un texte AAC vers l'orthographe officielle 1979.

    convert_wi contrôle le traitement de "wi" (voir la note ci-dessus) :
      - "none"    (défaut) : "wi" n'est jamais reconverti en "ui" -- c'est
                  le comportement sûr, car "wi" est une séquence banale de
                  1979 (swiv, lwil, kwit, nwit, pwi...).
      - "lexicon" : seuls les mots de WI_WORDS_FROM_UI sont reconvertis.
      - "always"  : conversion mécanique de tout "wi" en "ui" -- ancien
                  comportement, incorrect sur du texte réel, gardé pour
                  compatibilité et pour les tests de non-régression.

    use_lexicon est un ancien paramètre booléen, conservé pour compatibilité
    ascendante : use_lexicon=True équivaut à convert_wi="lexicon" (mais la
    liste blanche WI_WORDS_FROM_UI étant vide par défaut, le résultat visible
    est le même que "none" tant qu'elle n'est pas complétée), et
    use_lexicon=False équivaut à convert_wi="always". Ne pas utiliser dans du
    code neuf : préférer convert_wi explicitement.
    """
    if use_lexicon is not None:
        convert_wi = "lexicon" if use_lexicon else "always"
    if convert_wi not in ("none", "lexicon", "always"):
        raise ValueError('convert_wi doit être "none", "lexicon" ou "always"')

    result = _decode_backward_digraphs(text)

    if convert_wi == "none":
        return result

    if convert_wi == "always":
        return result.replace("Wi", "Ui").replace("wi", "ui")

    # convert_wi == "lexicon" : liste blanche uniquement.
    tokens = re.split(r"(\W+)", result)
    rebuilt = []
    for tok in tokens:
        bare = tok.strip(".,;:!?«»\"'()").lower()
        if bare in WI_WORDS_FROM_UI:
            rebuilt.append(re.sub(r"[Ww]i", lambda m: "Ui" if m.group()[0] == "W" else "ui", tok))
        else:
            rebuilt.append(tok)  # par défaut, "wi" reste "wi"
    return "".join(rebuilt)


def convert(text: str, *, report: bool = False):
    """Convertit 1979 -> AAC. Si report=True, renvoie un ConversionReport
    avec les statistiques de gain scriptural au lieu du texte seul."""
    aac = to_aac(text)
    if not report:
        return aac
    return ConversionReport(original=text, converted=aac)


def diff_summary(text: str) -> dict[str, int]:
    """Compte les occurrences de chaque séquence opaque dans un texte 1979,
    utile pour reproduire l'analyse détaillée du chapitre IV du mémoire.

    "ng" n'est compté que lorsqu'il est réellement opaque (non suivi d'une
    voyelle, voir la règle positionnelle documentée en tête de fichier) --
    les occurrences comme "grangou" (gran-gou), où "n" et "g" appartiennent
    à deux syllabes différentes, ne sont pas des séquences opaques et sont
    donc exclues de ce compte."""
    return {
        "ch": len(re.findall(r"[Cc][Hh]", text)),
        "ou": len(re.findall(r"[Oo][Uu]", text)),
        "ng": len(_NG_RULE.findall(text)),
        "ui": len(re.findall(r"[Uu][Ii]", text)),
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3 or sys.argv[1] not in ("to-aac", "to-1979"):
        print("Usage: python aac_converter.py [to-aac|to-1979] \"texte à convertir\"")
        sys.exit(1)

    direction, text = sys.argv[1], sys.argv[2]
    if direction == "to-aac":
        rep = convert(text, report=True)
        print(rep.converted)
        print(
            f"\n[gain: {rep.gain_percent_total:.1f}% total, "
            f"{rep.gain_percent_no_space:.1f}% sans espaces]",
            file=sys.stderr,
        )
    else:
        print(to_1979(text))
