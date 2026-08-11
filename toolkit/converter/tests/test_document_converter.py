"""Tests du module document_converter — vérifie la fidélité de mise en
forme du docx et le bon fonctionnement du pipeline pdf."""

import sys
import pathlib
import tempfile

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import docx as docx_lib
from document_converter import convert_docx


def _make_sample_docx(path):
    d = docx_lib.Document()
    p = d.add_paragraph()
    p.add_run("Chak moun gen dwa pou chèche travay. ").bold = True
    p.add_run("Nou vle yon peyi san pwoblèm.").italic = True
    d.save(path)


def test_docx_conversion_preserves_run_formatting():
    with tempfile.TemporaryDirectory() as tmp:
        src = pathlib.Path(tmp) / "in.docx"
        dst = pathlib.Path(tmp) / "out.docx"
        _make_sample_docx(src)

        convert_docx(str(src), str(dst))

        out = docx_lib.Document(str(dst))
        runs = out.paragraphs[0].runs
        assert runs[0].bold is True
        assert runs[1].italic is True
        # le texte doit être converti (ch->š, ou->ŏ)
        assert "š" in runs[0].text
        assert "ŏ" in runs[1].text
        # aucune séquence 1979 résiduelle dans un run entièrement converti
        assert "ch" not in runs[0].text
        assert "ou" not in runs[1].text


def test_docx_conversion_returns_segments_for_stats():
    with tempfile.TemporaryDirectory() as tmp:
        src = pathlib.Path(tmp) / "in.docx"
        dst = pathlib.Path(tmp) / "out.docx"
        _make_sample_docx(src)

        result = convert_docx(str(src), str(dst))

        assert len(result.segments) == 1
        label, original = result.segments[0]
        # le texte ORIGINAL (pas converti) doit être renvoyé pour les stats
        assert "chèche" in original
        assert "pwoblèm" in original


if __name__ == "__main__":
    test_docx_conversion_preserves_run_formatting()
    test_docx_conversion_returns_segments_for_stats()
    print("ok")
