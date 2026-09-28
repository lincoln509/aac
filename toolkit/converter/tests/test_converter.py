"""
Tests de non-régression pour acc_converter.

Le test `test_corpus_lincoln_matches_memoire` reproduit exactement
l'analyse du chapitre IV, section 4.1.2 du mémoire : si ce test échoue,
les chiffres cités dans le mémoire (140 -> 127 caractères, gain de 9,3 %)
ne sont plus reproductibles et doivent être corrigés dans le document.

Note d'attribution (corrigée) : ce texte de 140 caractères est un texte
personnel de l'auteur du mémoire (H. Lincoln Compère), rédigé dans le cadre
du document AAC/AKI — il avait été mal étiqueté "Depestre" dans une
version antérieure de ce dépôt (variable/classe portant ce nom). Pour un
gain mesuré sur plusieurs textes indépendants et de sources diverses
(personnel, légal, international, oral, littéraire du domaine public),
voir `corpus.py` et `test_corpus_diversity.py` : le gain varie de 2,5 %
à 9,3 % selon le texte (moyenne 5,7 %, IC95 % [2,9–9,25 %] sur 8 textes).
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from acc_converter import to_acc, to_1979, convert, diff_summary, WI_WORDS_FROM_UI


class TestForwardConversion(unittest.TestCase):
    def test_ch_becomes_s_caron(self):
        self.assertEqual(to_acc("chante"), "šante")
        self.assertEqual(to_acc("Chante"), "Šante")

    def test_ou_becomes_o_breve(self):
        self.assertEqual(to_acc("pou"), "pŏ")
        self.assertEqual(to_acc("nou"), "nŏ")

    def test_oun_becomes_o_breve_plus_n_automatically(self):
        # Aucune règle dédiée à "oun" : elle doit émerger naturellement
        # de la règle "ou" -> "ŏ", conformément au principe du mémoire
        # (section 3.5 : pas de symbole distinct pour /ũ/).
        self.assertEqual(to_acc("moun"), "mŏn")
        self.assertEqual(to_acc("oun"), "ŏn")

    def test_ng_becomes_eng(self):
        self.assertEqual(to_acc("lang"), "laŋ")

    def test_ui_becomes_wi(self):
        # CORRECTIF (revue de code) : le mot testé était "tousuit" (sans le
        # second "t"), qui n'existe pas dans le corpus -- le vrai mot du
        # corpus (converter/corpus.py, texte de Choukoun) est "toutsuit".
        # Le test passait quand même (le mot inventé contient "ui" comme
        # le vrai), mais ne vérifiait pas ce qu'il prétendait vérifier.
        self.assertEqual(to_acc("toutsuit"), "tŏtswit")
        # "tousuit" est le mot correct existant du créole haitien avec une
        # occurrence de "ui", mais dans le corpus de référence (converter/corpus.py)
        # -- on utilise avec un "t" c'est un probleme de grammaire/conversion.
        self.assertEqual(to_acc("tousuit"), "tŏswit")

    def test_case_insensitive_and_case_preserving(self):
        # CORRECTIF (revue de code, M5) : les règles doivent reconnaître
        # toutes les combinaisons de casse ("cH", "oU"...), pas seulement
        # les 3 casses figées d'origine, et préserver la casse du résultat.
        self.assertEqual(to_acc("cHak"), "šak")
        self.assertEqual(to_acc("oU"), "ŏ")
        self.assertEqual(to_acc("CHAK"), "ŠAK")

    def test_an_en_on_unchanged(self):
        # Coeur de la révision du mémoire : ces séquences ne doivent
        # JAMAIS être modifiées par le convertisseur.
        for word in ["manman", "san", "tanpèt", "gen", "pwoblèm", "on", "mont"]:
            self.assertEqual(to_acc(word), word)

    def test_w_y_unchanged(self):
        self.assertEqual(to_acc("wozo"), "wozo")
        self.assertEqual(to_acc("yo"), "yo")


class TestCorpusLincoln(unittest.TestCase):
    """Reproduit l'exemple du chapitre IV, section 4.1.2 du mémoire.

    Ce texte de 140 caractères est un texte personnel de l'auteur
    (Lincoln Compère, document AAC/AKI) — PAS un extrait de René
    Depestre, contrairement à l'étiquette utilisée dans une version
    antérieure de ce dépôt (classe et variables renommées en
    conséquence : TestCorpusDepestre -> TestCorpusLincoln)."""

    ORIGINAL = (
        "Chante pou chase lapli nan kò mwen, chante pou san mwen rete cho "
        "nan tanpèt la, pou klète lang manman nou klere sou ekran toupatou "
        "sou latè."
    )

    EXPECTED_ACC = (
        "Šante pŏ šase lapli nan kò mwen, šante pŏ san mwen rete šo "
        "nan tanpèt la, pŏ klète laŋ manman nŏ klere sŏ ekran tŏpatŏ "
        "sŏ latè."
    )

    def test_conversion_matches_memoire_text(self):
        self.assertEqual(to_acc(self.ORIGINAL), self.EXPECTED_ACC)

    def test_character_counts_match_memoire_table(self):
        report = convert(self.ORIGINAL, report=True)
        self.assertEqual(report.chars_total_before, 140)
        self.assertEqual(report.chars_total_after, 127)
        self.assertEqual(report.chars_no_space_before, 114)
        self.assertEqual(report.chars_no_space_after, 101)

    def test_gain_percentages_match_memoire(self):
        report = convert(self.ORIGINAL, report=True)
        self.assertAlmostEqual(report.gain_percent_total, 9.3, places=1)
        self.assertAlmostEqual(report.gain_percent_no_space, 11.4, places=1)

    def test_substitution_breakdown_matches_memoire(self):
        # 4 ch, 8 ou, 1 ng -- exactement les chiffres cités en 4.1.2
        counts = diff_summary(self.ORIGINAL)
        self.assertEqual(counts["ch"], 4)
        self.assertEqual(counts["ou"], 8)
        self.assertEqual(counts["ng"], 1)


class TestBackwardConversion(unittest.TestCase):
    def test_simple_roundtrip(self):
        original = "Chak moun gen dwa pou yo chèche travay san pwoblèm nan peyi a."
        acc = to_acc(original)
        back = to_1979(acc)
        self.assertEqual(back, original)

    def test_roundtrip_case(self):
        # CORRECTIF (revue de code, M5) : MOUN -> MŎN -> MOUN (auparavant
        # "MOuN", casse incohérente au retour).
        self.assertEqual(to_1979(to_acc("MOUN")), "MOUN")
        self.assertEqual(to_1979(to_acc("Chak")), "Chak")

    def test_wi_never_converted_to_ui_by_default(self):
        # CORRECTIF CRITIQUE (revue de code, C1) : l'ancienne version
        # convertissait TOUT "wi" en "ui" sauf 4 exceptions, ce qui
        # corrompait des mots courants et bien réels de 1979 ("swiv",
        # "lwil", "kwit", "nwit", "pwi", "fwi"...). Par défaut, "wi" n'est
        # plus jamais reconverti en "ui" : aucune preuve de corpus ne
        # justifie cette conversion (voir la note dans acc_converter.py).
        for word in ["swiv", "lwil", "kwit", "pwi", "nwit", "fwi", "wi", "kiwi", "sandwich"]:
            with self.subTest(word=word):
                self.assertEqual(to_1979(to_acc(word)), word)

    def test_wi_lexicon_whitelist_is_empty_by_default(self):
        # La liste blanche des mots à reconvertir en "ui" doit rester vide
        # tant qu'aucun mot n'est confirmé par un linguiste ou un corpus de
        # référence (voir la note dans acc_converter.py) : c'est ce qui
        # garantit que convert_wi="lexicon" ne fait rien de plus que "none"
        # tant qu'elle n'a pas été complétée sciemment.
        self.assertEqual(WI_WORDS_FROM_UI, set())
        self.assertEqual(
            to_1979(to_acc("kwit"), convert_wi="lexicon"),
            to_1979(to_acc("kwit"), convert_wi="none"),
        )

    def test_always_mode_shows_the_old_incorrect_behavior(self):
        # Documente volontairement l'ancien comportement mécanique et
        # incorrect ("ancienne version" du convertisseur), conservé pour
        # compatibilité mais déconseillé sur du texte réel.
        naive = to_1979(to_acc("swiv"), convert_wi="always")
        self.assertEqual(naive, "suiv")  # incorrect, à dessein
        self.assertEqual(to_1979("Wi, mwen dakò.", convert_wi="always"), "Ui, mwen dakò.")


if __name__ == "__main__":
    unittest.main(verbosity=2)
