"""
Tests de non-régression pour acc_converter.

Le test `test_corpus_depestre_matches_memoire` reproduit exactement
l'analyse du chapitre IV, section 4.1.2 du mémoire : si ce test échoue,
les chiffres cités dans le mémoire (140 -> 127 caractères, gain de 9,3 %)
ne sont plus reproductibles et doivent être corrigés dans le document.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from acc_converter import to_acc, to_1979, convert, diff_summary, WI_WORDS_NEVER_FROM_UI


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
        self.assertEqual(to_acc("kuit"), "kwit")

    def test_an_en_on_unchanged(self):
        # Coeur de la révision du mémoire : ces séquences ne doivent
        # JAMAIS être modifiées par le convertisseur.
        for word in ["manman", "san", "tanpèt", "gen", "pwoblèm", "on", "mont"]:
            self.assertEqual(to_acc(word), word)

    def test_w_y_unchanged(self):
        self.assertEqual(to_acc("wozo"), "wozo")
        self.assertEqual(to_acc("yo"), "yo")


class TestCorpusDepestre(unittest.TestCase):
    """Reproduit l'exemple du chapitre IV, section 4.1.2 du mémoire."""

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

    def test_wi_lexicon_exception_is_documented_and_applied(self):
        # "wi" (oui) ne doit jamais redevenir "ui" : c'est la limitation
        # documentée dans le README et dans acc_converter.py.
        self.assertIn("wi", WI_WORDS_NEVER_FROM_UI)
        self.assertEqual(to_1979("Wi, mwen dakò."), "Wi, mwen dakò.")

    def test_naive_backward_conversion_shows_the_limitation(self):
        # Documente volontairement le comportement incorrect quand on
        # désactive le lexique, pour que la limitation reste visible
        # et testée plutôt que silencieuse.
        naive = to_1979("Wi, mwen dakò.", use_lexicon=False)
        self.assertEqual(naive, "Ui, mwen dakò.")  # incorrect, à dessein


if __name__ == "__main__":
    unittest.main(verbosity=2)
