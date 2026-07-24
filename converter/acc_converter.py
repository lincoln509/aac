"""
acc_converter.py
=================

Convertisseur bidirectionnel entre l'orthographe officielle du créole
haïtien (décret du 28 septembre 1979) et l'Alphabet Atomique Créole (ACC),
tel que défini dans le mémoire « Pour une Rationalisation Atomique de la
Graphie Créole Haïtienne ».

Règles appliquées (voir Chapitre III du mémoire) :
    ch  -> š   (U+0161)   /ʃ/
    ou  -> ŏ   (U+014F)   /u/   (et donc "oun" -> "ŏn" automatiquement)
    ng  -> ŋ   (U+014B)   /ɲ/
    ui  -> wi             /ɥi/ ~ /jw/

Séquences volontairement NON modifiées (déjà transparentes) :
    an, en, on

Ce module est volontairement dépourvu de dépendances externes.
"""

from __future__ import annotations
import re
from dataclasses import dataclass, field

# ---------------------------------------------------------------------------
# Table des règles (1979 -> ACC), appliquées dans cet ordre précis.
# L'ordre importe : "ou" doit être traité avant que "ng" ou "ch" ne
# puissent interférer sur les mêmes segments de texte.
# ---------------------------------------------------------------------------

_FORWARD_RULES: list[tuple[str, str]] = [
    (r"Ch", "Š"),
    (r"CH", "Š"),
    (r"ch", "š"),
    (r"Ou", "Ŏ"),
    (r"OU", "Ŏ"),
    (r"ou", "ŏ"),
    (r"Ng", "Ŋ"),
    (r"NG", "Ŋ"),
    (r"ng", "ŋ"),
    (r"Ui", "Wi"),
    (r"UI", "WI"),
    (r"ui", "wi"),
]

# Règles inverses simples (ACC -> 1979). Voir la limitation documentée
# plus bas concernant "wi".
_BACKWARD_RULES: list[tuple[str, str]] = [
    (r"Š", "Ch"),
    (r"š", "ch"),
    (r"Ŏ", "Ou"),
    (r"ŏ", "ou"),
    (r"Ŋ", "Ng"),
    (r"ŋ", "ng"),
]

# ---------------------------------------------------------------------------
# Exceptions lexicales pour la conversion inverse de "wi".
#
# Limitation connue et documentée (voir README, section "Limites") :
# la séquence "wi" existait déjà dans l'orthographe de 1979 pour des mots
# qui n'ont jamais été écrits "ui" (ex. "wi" = "oui"). La conversion ACC -> 1979
# ne peut donc pas restituer "ui" par simple substitution de caractères :
# elle nécessite une liste d'exceptions lexicales, complétée ici pour les
# cas les plus fréquents et destinée à être étendue par un corpus de
# référence plus large (cf. mémoire, chapitre III, feuille de route phase 2).
# ---------------------------------------------------------------------------

WI_WORDS_NEVER_FROM_UI: set[str] = {
    "wi",       # oui
    "kiwi",     # emprunt
    "sandwi",   # sandwich (déjà "sandwich"/"sandwitch" localement, variante)
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


def to_acc(text: str) -> str:
    """Convertit un texte de l'orthographe officielle 1979 vers l'ACC."""
    result = text
    for pattern, repl in _FORWARD_RULES:
        result = result.replace(pattern, repl)
    return result


def to_1979(text: str, *, use_lexicon: bool = True) -> str:
    """Convertit un texte ACC vers l'orthographe officielle 1979.

    Si use_lexicon=True (par défaut), les mots figurant dans
    WI_WORDS_NEVER_FROM_UI sont protégés et ne sont pas reconvertis en "ui".
    Sinon, la conversion est purement mécanique (wi -> ui systématique),
    ce qui est incorrect pour ces mots -- voir la section "Limites" du README.
    """
    result = text
    for pattern, repl in _BACKWARD_RULES:
        result = result.replace(pattern, repl)

    if use_lexicon:
        tokens = re.split(r"(\W+)", result)
        rebuilt = []
        for tok in tokens:
            bare = tok.strip(".,;:!?«»\"'()").lower()
            if bare in WI_WORDS_NEVER_FROM_UI:
                rebuilt.append(tok)  # on laisse "wi" tel quel
            else:
                rebuilt.append(re.sub(r"[Ww]i", lambda m: "Ui" if m.group()[0] == "W" else "ui", tok))
        result = "".join(rebuilt)
    else:
        result = result.replace("Wi", "Ui").replace("wi", "ui")

    return result


def convert(text: str, *, report: bool = False):
    """Convertit 1979 -> ACC. Si report=True, renvoie un ConversionReport
    avec les statistiques de gain scriptural au lieu du texte seul."""
    acc = to_acc(text)
    if not report:
        return acc
    return ConversionReport(original=text, converted=acc)


def diff_summary(text: str) -> dict[str, int]:
    """Compte les occurrences de chaque séquence opaque dans un texte 1979,
    utile pour reproduire l'analyse détaillée du chapitre IV du mémoire."""
    return {
        "ch": len(re.findall(r"[Cc][Hh]", text)),
        "ou": len(re.findall(r"[Oo][Uu]", text)),
        "ng": len(re.findall(r"[Nn][Gg]", text)),
        "ui": len(re.findall(r"[Uu][Ii]", text)),
    }


if __name__ == "__main__":
    import sys

    if len(sys.argv) < 3 or sys.argv[1] not in ("to-acc", "to-1979"):
        print("Usage: python acc_converter.py [to-acc|to-1979] \"texte à convertir\"")
        sys.exit(1)

    direction, text = sys.argv[1], sys.argv[2]
    if direction == "to-acc":
        rep = convert(text, report=True)
        print(rep.converted)
        print(
            f"\n[gain: {rep.gain_percent_total:.1f}% total, "
            f"{rep.gain_percent_no_space:.1f}% sans espaces]",
            file=sys.stderr,
        )
    else:
        print(to_1979(text))
