# -*- coding: utf-8 -*-
"""Tests de converter/fertilite_tokenizers.py sans télécharger aucun modèle.

- l'export JSON des décomptes (--export) : structure, empreintes, fusion ;
- le chargeur NLLB : les caractères inconnus du vocabulaire (<unk>) doivent
  rester comptés (ils ne l'étaient pas quand on filtrait all_special_ids).
  Ce test utilise un mini-tokeniseur local et exige `transformers` +
  `tokenizers` ; il est ignoré s'ils sont absents.
"""

import contextlib
import hashlib
import io
import json
import pathlib
import sys
import tempfile
import unittest
from unittest import mock

CONVERTER = pathlib.Path(__file__).resolve().parents[1]
sys.path.insert(0, str(CONVERTER))

import fertilite_tokenizers as ft  # noqa: E402
from aac_converter import to_aac  # noqa: E402
from corpus import CORPUS  # noqa: E402

try:
    from tokenizers import Tokenizer, models, pre_tokenizers
    from transformers import PreTrainedTokenizerFast
    HAVE_HF = True
except Exception:  # pragma: no cover
    HAVE_HF = False


def _one_token_per_character():
    """Faux tokeniseur : 1 jeton par caractère (suffisant pour tester l'export)."""
    return (lambda text: list(text)), (lambda ids: list(ids))


class TestExport(unittest.TestCase):
    def setUp(self):
        self._saved = dict(ft.TOKENIZERS)
        ft.TOKENIZERS["fake"] = _one_token_per_character
        ft.TOKENIZERS["fake2"] = _one_token_per_character
        self.tmp = tempfile.TemporaryDirectory()
        self.path = pathlib.Path(self.tmp.name) / "out.json"

    def tearDown(self):
        ft.TOKENIZERS.clear()
        ft.TOKENIZERS.update(self._saved)
        self.tmp.cleanup()

    def _run(self, names):
        with contextlib.redirect_stdout(io.StringIO()):
            ft.print_corpus_report(names, str(self.path))
        return json.loads(self.path.read_text(encoding="utf-8"))

    def test_export_structure_and_fingerprints(self):
        data = self._run(["fake"])
        texts = data["tokenizers"]["fake"]["texts"]
        self.assertEqual(list(texts), list(CORPUS))
        self.assertFalse(data["tokenizers"]["fake"]["provisional"])
        for key, entry in texts.items():
            with self.subTest(text=key):
                text = CORPUS[key]["texte"]
                self.assertEqual(entry["words"], len(text.split()))
                self.assertEqual(entry["tokens_1979"], len(text))        # 1 jeton par caractère
                self.assertEqual(entry["tokens_aac"], len(to_aac(text)))
                self.assertEqual(entry["sha1_1979"], hashlib.sha1(text.encode("utf-8")).hexdigest())
                self.assertEqual(entry["sha1_aac"], hashlib.sha1(to_aac(text).encode("utf-8")).hexdigest())

    def test_export_merges_instead_of_overwriting(self):
        self._run(["fake"])
        data = self._run(["fake2"])
        self.assertEqual(sorted(data["tokenizers"]), ["fake", "fake2"])

    def test_export_requires_corpus_flag(self):
        with mock.patch.object(sys, "argv", ["fertilite_tokenizers.py", "texte", "--export", "x.json"]):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                runpy_main()


def runpy_main():
    import runpy
    runpy.run_path(str(CONVERTER / "fertilite_tokenizers.py"), run_name="__main__")


@unittest.skipUnless(HAVE_HF, "transformers/tokenizers non installés")
class TestNllbUnknownCharacters(unittest.TestCase):
    """Mini-tokeniseur à vocabulaire fermé (comme un SentencePiece sans byte-fallback) :
    « ŏ » y est inconnu et devient <unk>."""

    @staticmethod
    def _mini_tokenizer():
        vocab = {"<s>": 0, "<pad>": 1, "</s>": 2, "<unk>": 3, "a": 4, "p": 5, "o": 6, "u": 7}
        tok = Tokenizer(models.WordLevel(vocab, unk_token="<unk>"))
        tok.pre_tokenizer = pre_tokenizers.Split("", "isolated")
        return PreTrainedTokenizerFast(
            tokenizer_object=tok, unk_token="<unk>", pad_token="<pad>", eos_token="</s>", bos_token="<s>")

    def _encode(self, text):
        mini = self._mini_tokenizer()
        with mock.patch("transformers.AutoTokenizer.from_pretrained", return_value=mini):
            encode, _ = ft._load_nllb()
        err = io.StringIO()
        with contextlib.redirect_stderr(err):
            ids = encode(text)
        return ids, err.getvalue()

    def test_unknown_characters_are_counted_and_reported(self):
        ids, warning = self._encode("pŏ")
        self.assertEqual(len(ids), 2)             # p + <unk> : l'<unk> compte pour 1 jeton
        self.assertIn("<unk>", warning)

    def test_known_characters_give_no_warning(self):
        ids, warning = self._encode("pou")
        self.assertEqual(len(ids), 3)
        self.assertEqual(warning, "")


if __name__ == "__main__":
    unittest.main()
