# -*- coding: utf-8 -*-
"""Garde-fous de l'architecture « une donnée = une source ».

Ils empêchent le retour des copies qui avaient fini par diverger :
  - fichiers générés (web-demo/generated/) périmés ;
  - convertisseur ou règles recopiés dans les pages HTML ;
  - pages dont le JavaScript ne compile plus ;
  - port JS qui s'écarte du Python (parité sur tout le corpus) ;
  - nouvelle copie locale du syllabeur ou des alphabets.

Les tests qui ont besoin de Node sont ignorés si `node` est absent.
"""

import importlib.util
import json
import pathlib
import re
import shutil
import subprocess
import sys
import tempfile
import unittest

CONVERTER = pathlib.Path(__file__).resolve().parents[1]
ROOT = CONVERTER.parent
PAGES = sorted((ROOT / "web-demo").glob("*.html"))
NODE = shutil.which("node")

sys.path.insert(0, str(CONVERTER))
from aac_converter import to_1979, to_aac  # noqa: E402
from corpus import CORPUS  # noqa: E402


def _load_build():
    spec = importlib.util.spec_from_file_location("aac_build", ROOT / "scripts" / "build.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class TestGeneratedFiles(unittest.TestCase):
    def test_generated_files_are_up_to_date(self):
        build = _load_build()
        for path, content in build.outputs().items():
            with self.subTest(file=path.name):
                self.assertTrue(path.exists(), f"{path} manquant : lancez python3 scripts/build.py")
                self.assertEqual(
                    path.read_bytes(), content.encode("utf-8"),
                    f"{path.name} périmé : lancez python3 scripts/build.py",
                )


class TestPagesUseSharedSources(unittest.TestCase):
    def test_pages_found(self):
        self.assertGreaterEqual(len(PAGES), 3)

    def test_pages_load_shared_converter_and_rules(self):
        for page in PAGES:
            text = page.read_text(encoding="utf-8")
            if "AACConverter" not in text and "toAac(" not in text:
                continue
            with self.subTest(page=page.name):
                self.assertIn('src="generated/rules.js"', text)
                self.assertIn('src="../converter/aac_converter.js"', text)
                self.assertLess(text.index('src="generated/rules.js"'), text.index('src="../converter/aac_converter.js"'))

    def test_pages_do_not_embed_a_converter_copy(self):
        for page in PAGES:
            text = page.read_text(encoding="utf-8")
            with self.subTest(page=page.name):
                for forbidden in ("function toAac", "function to1979", "AAC-CONVERTER:BEGIN",
                                  "AAC-CORPUS:BEGIN", "const NG_RULE", "const FORWARD_RULES"):
                    self.assertNotIn(forbidden, text)


@unittest.skipUnless(NODE, "node introuvable")
class TestNode(unittest.TestCase):
    def test_inline_page_scripts_compile(self):
        script_re = re.compile(r"<script(?![^>]*\bsrc=)[^>]*>(.*?)</script>", re.S)
        for page in PAGES:
            text = re.sub(r"<!--.*?-->", "", page.read_text(encoding="utf-8"), flags=re.S)  # commentaires HTML
            for i, body in enumerate(script_re.findall(text)):
                if not body.strip():
                    continue
                with self.subTest(page=page.name, script=i):
                    with tempfile.TemporaryDirectory() as tmp:
                        js = pathlib.Path(tmp) / "inline.js"
                        js.write_text(body, encoding="utf-8")
                        result = subprocess.run([NODE, "--check", str(js)], capture_output=True, text=True)
                        self.assertEqual(result.returncode, 0, result.stderr[:400])

    def test_js_matches_python_on_corpus_and_edge_cases(self):
        samples = [e["texte"] for e in CORPUS.values()] + [
            "OUI Chante CHAK", "bleng-bleng ng", "grangou ak lengis", "toutswit lwil swiv",
            "Ng nG NG", "kiwi sandwich wi", "",
            # liste blanche wi_from_ui : forme, casse, ponctuation, accents et mots voisins non listés
            "uit", "uitèn", "dizuit", "vennsuit", "Uit", "UIT", "UITÈN", "Dizuit.", "(uit)",
            "uit nwit kwit swiv wi dizuit", "kiwi uit", "toutsuit",
        ]
        samples += [to_aac(s) for s in samples]  # on teste aussi AAC -> 1979
        script = (
            "const c=require(process.argv[1]);"
            "const S=JSON.parse(require('fs').readFileSync(0,'utf8'));"
            "process.stdout.write(JSON.stringify(S.map(s=>[c.toAac(s),c.to1979(s)])));"
        )
        result = subprocess.run(
            [NODE, "-e", script, str(CONVERTER / "aac_converter.js")],
            input=json.dumps(samples), capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stderr[:400])
        for sample, (js_aac, js_1979) in zip(samples, json.loads(result.stdout)):
            with self.subTest(sample=sample[:40]):
                self.assertEqual(js_aac, to_aac(sample))
                self.assertEqual(js_1979, to_1979(sample))


VENDOR = ROOT / "web-demo" / "vendor"


class TestTokenizerBundle(unittest.TestCase):
    """web-demo/token.html : le tokeniseur embarqué doit rester celui de tiktoken."""

    def test_page_references_existing_vendor_files(self):
        text = (ROOT / "web-demo" / "token.html").read_text(encoding="utf-8")
        for name in ("cl100k", "o200k"):
            with self.subTest(bundle=name):
                self.assertIn(f'"vendor/js-tiktoken-{name}.min.js"', text)
                self.assertTrue((VENDOR / f"js-tiktoken-{name}.min.js").exists())

    def test_python_script_uses_same_converter_and_encoding(self):
        text = (CONVERTER / "fertilite_tokenizers.py").read_text(encoding="utf-8")
        self.assertIn("from aac_converter import to_aac", text)
        self.assertIn('"cl100k_base"', text)
        # tous les encodages tiktoken de la page existent aussi dans le script
        page = (ROOT / "web-demo" / "token.html").read_text(encoding="utf-8")
        for encoding in re.findall(r'\{ id: "(\w+_base)"', page):
            with self.subTest(encoding=encoding):
                self.assertIn(f'"{encoding}"', text)

    def test_old_script_name_is_gone_everywhere(self):
        # fertilite_tiktoken.py a été remplacé par fertilite_tokenizers.py
        self.assertFalse((CONVERTER / "fertilite_tiktoken.py").exists())
        for path in [ROOT / "README.md", ROOT / "web-demo" / "token.html"]:
            self.assertNotIn("fertilite_tiktoken", path.read_text(encoding="utf-8"), path.name)

    def test_measure_with_a_fake_encoder(self):
        # measure() ne dépend d'aucun tokeniseur réel : on lui passe un encodeur factice (1 jeton = 1 caractère).
        import fertilite_tokenizers as ft
        m = ft.measure("Chante pou chase", lambda text: list(text))
        self.assertEqual(m["n_mots"], 3)
        self.assertEqual(m["tokens_1979"], len("Chante pou chase"))
        self.assertEqual(m["tokens_aac"], len(to_aac("Chante pou chase")))
        self.assertAlmostEqual(m["fert_1979"], len("Chante pou chase") / 3)

    # Valeurs de référence publiées par OpenAI (tiktoken) pour chaque encodage.
    REFERENCE = {
        "cl100k": ("cl100k_base", [15339, 1917], [83, 1609, 5963, 374, 2294, 0]),
        "o200k": ("o200k_base", [24912, 2375], [83, 8251, 2488, 382, 2212, 0]),
    }

    @unittest.skipUnless(NODE, "node introuvable")
    def test_bundles_match_tiktoken_reference_vectors(self):
        for bundle, (encoding, hello_ref, great_ref) in self.REFERENCE.items():
            script = (
                "global.window={};"
                "require('vm').runInThisContext(require('fs').readFileSync(process.argv[1],'utf8'));"
                f"const e=window.AACTiktoken.get('{encoding}');"
                "process.stdout.write(JSON.stringify([e.encode('hello world',[],[]),"
                "e.encode('tiktoken is great!',[],[]),e.encode('<|endoftext|>',[],[]).length,"
                "e.decode(e.encode('Šak mŏn gen dwa',[],[]))]));"
            )
            with self.subTest(encoding=encoding):
                result = subprocess.run(
                    [NODE, "-e", script, str(VENDOR / f"js-tiktoken-{bundle}.min.js")],
                    capture_output=True, text=True, encoding="utf-8",
                )
                self.assertEqual(result.returncode, 0, result.stderr[:400])
                hello, great, special_len, roundtrip = json.loads(result.stdout)
                self.assertEqual(hello, hello_ref)
                self.assertEqual(great, great_ref)
                self.assertGreater(special_len, 1)               # pas un jeton spécial unique
                self.assertEqual(roundtrip, "Šak mŏn gen dwa")   # aller-retour sans perte sur les lettres atomiques

    @unittest.skipUnless(NODE, "node introuvable")
    def test_both_bundles_share_one_registry(self):
        # Charger les deux bundles dans la même page : les deux encodages doivent coexister.
        script = (
            "global.window={};const fs=require('fs'),vm=require('vm');"
            "for(const f of process.argv.slice(1)) vm.runInThisContext(fs.readFileSync(f,'utf8'));"
            "process.stdout.write(JSON.stringify(Object.keys(window.AACTiktoken.factories).sort()));"
        )
        result = subprocess.run(
            [NODE, "-e", script, str(VENDOR / "js-tiktoken-cl100k.min.js"), str(VENDOR / "js-tiktoken-o200k.min.js")],
            capture_output=True, text=True, encoding="utf-8",
        )
        self.assertEqual(result.returncode, 0, result.stderr[:400])
        self.assertEqual(json.loads(result.stdout), ["cl100k_base", "o200k_base"])


@unittest.skipUnless(NODE, "node introuvable")
class TestExtraUiWordsParity(unittest.TestCase):
    """La mémoire des mots en « ui » (extra_ui_words / extraUiWords) doit être identique en JS et en Python."""

    def test_js_matches_python(self):
        from aac_converter import ui_words
        sources = [
            "uit dizuit tousuit toutsuit fuit uitt Tousuit",
            "nwit kwit fuit swiv", "FUIT Fuit fuit", "Chak moun tousuit lwil, uit.", "sen-uit (tousuit) wi", "",
        ]
        script = (
            "const c=require(process.argv[1]);"
            "const S=JSON.parse(require('fs').readFileSync(0,'utf8'));"
            "process.stdout.write(JSON.stringify(S.map(s=>{const w=c.uiWords(s);const a=c.toAac(s);"
            "return [w,a,c.to1979(a,'lexicon',w),c.to1979(a)];})));"
        )
        result = subprocess.run([NODE, "-e", script, str(CONVERTER / "aac_converter.js")],
                                input=json.dumps(sources), capture_output=True, text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr[:400])
        for src, (js_words, js_aac, js_with, js_without) in zip(sources, json.loads(result.stdout)):
            with self.subTest(src=src[:40]):
                py_words = ui_words(src)
                self.assertEqual(js_words, py_words)
                self.assertEqual(js_aac, to_aac(src))
                self.assertEqual(js_with, to_1979(to_aac(src), extra_ui_words=py_words))
                self.assertEqual(js_without, to_1979(to_aac(src)))


class TestPrecomputedTokenCounts(unittest.TestCase):
    """converter/fertilite_precomputed.json (affiché par la page pour NLLB-200) doit rester
    lié au corpus ET aux règles de conversion actuels : sinon ses chiffres sont périmés."""

    HINT = ("valeurs pré-calculées périmées : relancez "
            "python3 converter/fertilite_tokenizers.py --corpus --tokenizers <nom> --export converter/fertilite_precomputed.json")

    def test_precomputed_matches_current_corpus_and_rules(self):
        import hashlib
        sha = lambda t: hashlib.sha1(t.encode("utf-8")).hexdigest()  # noqa: E731
        data = json.loads((CONVERTER / "fertilite_precomputed.json").read_text(encoding="utf-8"))
        self.assertTrue(data["tokenizers"])
        for name, entry in data["tokenizers"].items():
            self.assertIsInstance(entry["provisional"], bool)
            self.assertEqual(list(entry["texts"]), list(CORPUS), name)
            for key, d in entry["texts"].items():
                with self.subTest(tokenizer=name, text=key):
                    text = CORPUS[key]["texte"]
                    self.assertEqual(d["sha1_1979"], sha(text), self.HINT)
                    self.assertEqual(d["sha1_aac"], sha(to_aac(text)), self.HINT)
                    self.assertEqual(d["words"], len(text.split()), self.HINT)
                    self.assertGreater(d["tokens_1979"], 0)
                    self.assertGreater(d["tokens_aac"], 0)


class TestNoLocalCopies(unittest.TestCase):
    """Une seule définition de chaque brique partagée."""

    def _sources(self):
        return [p for p in CONVERTER.glob("*.py")]

    def test_single_syllabifier(self):
        defs = [p.name for p in self._sources() if re.search(r"^def syllabify\w*\(", p.read_text(encoding="utf-8"), re.M)]
        self.assertEqual(defs, ["letter_analysis.py"], defs)

    def test_alphabets_defined_only_in_rules_json(self):
        pattern = re.compile(r"""^(ATOMIC_LETTERS|VOWELS|ATOMIC)\s*=\s*(\(\s*["']|set\(\s*["']|\{\s*["']|["'])""", re.M)
        offenders = [p.name for p in self._sources() if pattern.search(p.read_text(encoding="utf-8"))]
        self.assertEqual(offenders, [], offenders)

    def test_single_word_regex(self):
        offenders = [p.name for p in self._sources()
                     if p.name != "aac_converter.py" and r"[^\W\d_]" in p.read_text(encoding="utf-8")]
        self.assertEqual(offenders, [], offenders)


if __name__ == "__main__":
    unittest.main()
