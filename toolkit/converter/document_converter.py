"""
document_converter.py
======================

Convertit un document Word (.docx) ou PDF (.pdf) rédigé en créole,
orthographe officielle de 1979, vers l'Alphabet Atomique Créole (ACC),
et produit un rapport statistique comparatif (voir document_stats.py).

.docx : fidélité totale. On ne touche qu'au texte à l'intérieur des
        "runs" (<w:r>) existants — styles, gras, italique, polices,
        tableaux, en-têtes/pieds de page restent strictement identiques.
        Limite connue : une séquence "ch"/"ou"/"ng" coupée pile à la
        frontière entre deux runs (rare — survient surtout après une
        correction manuelle ou un correcteur orthographique Word) n'est
        pas convertie. `document_converter.py --check` signale ces cas.

.pdf  : fidélité textuelle, pas visuelle. Un PDF n'a pas de notion de
        "texte modifiable" — remplacer du texte en conservant exactement
        la mise en page d'origine (césures, justification, polices
        embarquées) n'est pas un problème résoluble en général. Ce module
        extrait le texte paragraphe par paragraphe (pdfplumber) puis
        reconstruit un nouveau PDF (reportlab) avec la même taille de
        page et un flux de paragraphes équivalent. Pour un document dont
        la seule mise en forme est du texte courant, le résultat est
        très proche de l'original ; pour une mise en page complexe
        (colonnes, tableaux, texte superposé à des images), utiliser la
        sortie .docx si elle existe, ou valider visuellement la sortie.
"""

from __future__ import annotations

from dataclasses import dataclass
import argparse
import pathlib
import sys

import docx  # python-docx
import pdfplumber
from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer

from acc_converter import to_acc
from document_stats import build_report, build_multi_document_report

# Les polices de base (Helvetica/Times, encodage WinAnsi) n'ont pas les
# glyphes š/ŏ/ŋ (Latin Extended-A, U+014F et U+014B en particulier) :
# reportlab les affiche comme des rectangles noirs. DejaVu Sans les
# couvre. Si elle est absente du système, on retombe sur Helvetica —
# auquel cas les caractères ACC composés seront mal rendus (le texte
# reste correct en UTF-8 dans le PDF, seul le rendu visuel est affecté).
_DEJAVU_REGULAR = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
_DEJAVU_BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
_UNICODE_FONT = "Helvetica"
_UNICODE_FONT_BOLD = "Helvetica-Bold"
try:
    if pathlib.Path(_DEJAVU_REGULAR).exists():
        pdfmetrics.registerFont(TTFont("DejaVuSans", _DEJAVU_REGULAR))
        _UNICODE_FONT = "DejaVuSans"
    if pathlib.Path(_DEJAVU_BOLD).exists():
        pdfmetrics.registerFont(TTFont("DejaVuSans-Bold", _DEJAVU_BOLD))
        _UNICODE_FONT_BOLD = "DejaVuSans-Bold"
except Exception:
    pass


@dataclass
class ConversionResult:
    output_path: str
    segments: list[tuple[str, str]]  # (label, texte_original) par paragraphe
    boundary_crossing_warnings: list[str]


# ---------------------------------------------------------------------------
# DOCX
# ---------------------------------------------------------------------------

_OPAQUE_SEQUENCES = ("ch", "Ch", "CH", "ou", "Ou", "OU", "ng", "Ng", "NG", "ui", "Ui", "UI")


def _convert_paragraph_runs(paragraph, warnings: list[str], location: str) -> str:
    """Convertit chaque run en place (préserve la mise en forme du run).
    Retourne le texte ORIGINAL du paragraphe (pour les stats), et signale
    les séquences opaques qui chevauchent une frontière de run."""
    original_text = paragraph.text
    joined_before = "".join(r.text for r in paragraph.runs)

    for run in paragraph.runs:
        if run.text:
            run.text = to_acc(run.text)

    # Détection best-effort des séquences coupées entre deux runs :
    # si le texte concaténé transformé run-par-run diffère de la
    # transformation du texte concaténé en un bloc, une séquence a
    # chevauché une frontière.
    naive_full_convert = to_acc(joined_before)
    actual_full_convert = "".join(r.text for r in paragraph.runs)
    if naive_full_convert != actual_full_convert and joined_before.strip():
        warnings.append(f"{location}: possible séquence coupée entre deux runs Word — vérifier manuellement.")

    return original_text


def convert_docx(input_path: str, output_path: str) -> ConversionResult:
    document = docx.Document(input_path)
    segments: list[tuple[str, str]] = []
    warnings: list[str] = []

    for i, paragraph in enumerate(document.paragraphs):
        if paragraph.text.strip():
            original = _convert_paragraph_runs(paragraph, warnings, f"paragraphe {i + 1}")
            segments.append((f"paragraphe {i + 1}", original))

    for t_idx, table in enumerate(document.tables):
        for r_idx, row in enumerate(table.rows):
            for c_idx, cell in enumerate(row.cells):
                for p_idx, paragraph in enumerate(cell.paragraphs):
                    if paragraph.text.strip():
                        loc = f"tableau {t_idx + 1}, cellule ({r_idx + 1},{c_idx + 1})"
                        original = _convert_paragraph_runs(paragraph, warnings, loc)
                        segments.append((loc, original))

    document.save(output_path)
    return ConversionResult(output_path=output_path, segments=segments, boundary_crossing_warnings=warnings)


# ---------------------------------------------------------------------------
# PDF
# ---------------------------------------------------------------------------

def _extract_pdf_paragraphs(input_path: str) -> list[tuple[str, str, tuple[float, float]]]:
    """Retourne une liste de (label, texte, taille_page) par paragraphe.
    Un paragraphe = un bloc de texte séparé par une ligne vide ; si une
    page n'a aucune ligne vide détectable, la page entière devient un
    seul paragraphe (repli, pour garantir n >= 1)."""
    out = []
    with pdfplumber.open(input_path) as pdf:
        for p_idx, page in enumerate(pdf.pages):
            text = page.extract_text() or ""
            page_size = (page.width, page.height)
            blocks = [b.strip() for b in text.split("\n\n") if b.strip()]
            if len(blocks) <= 1:
                blocks = [b.strip() for b in text.split("\n") if b.strip()]
            for b_idx, block in enumerate(blocks):
                out.append((f"page {p_idx + 1}, bloc {b_idx + 1}", block, page_size))
    return out


def convert_pdf(input_path: str, output_path: str) -> ConversionResult:
    paragraphs = _extract_pdf_paragraphs(input_path)
    segments = [(label, text) for label, text, _ in paragraphs]

    page_size = paragraphs[0][2] if paragraphs else letter
    # reportlab attend des points ; pdfplumber donne déjà des points.
    doc = SimpleDocTemplate(
        output_path,
        pagesize=(page_size[0], page_size[1]),
        leftMargin=20 * mm, rightMargin=20 * mm, topMargin=20 * mm, bottomMargin=20 * mm,
    )
    styles = getSampleStyleSheet()
    body_style = ParagraphStyle("Body", parent=styles["Normal"], fontName=_UNICODE_FONT, fontSize=11, leading=15)

    story = []
    for label, text, _ in paragraphs:
        converted = to_acc(text).replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
        story.append(Paragraph(converted, body_style))
        story.append(Spacer(1, 8))
    doc.build(story)

    return ConversionResult(output_path=output_path, segments=segments, boundary_crossing_warnings=[
        "Sortie PDF reconstruite : mise en page textuelle équivalente, pas une copie visuelle exacte "
        "(colonnes, images et polices embarquées de l'original ne sont pas reproduites — voir docstring du module)."
    ])


def extract_docx_paragraphs(input_path: str) -> list[tuple[str, str]]:
    """Comme convert_docx, mais lecture seule — pour l'agrégation
    multi-documents (`analyze`), qui n'a pas besoin d'écrire de sortie."""
    document = docx.Document(input_path)
    segments: list[tuple[str, str]] = []
    for i, paragraph in enumerate(document.paragraphs):
        if paragraph.text.strip():
            segments.append((f"paragraphe {i + 1}", paragraph.text))
    for t_idx, table in enumerate(document.tables):
        for r_idx, row in enumerate(table.rows):
            for c_idx, cell in enumerate(row.cells):
                for paragraph in cell.paragraphs:
                    if paragraph.text.strip():
                        segments.append((f"tableau {t_idx + 1}, cellule ({r_idx + 1},{c_idx + 1})", paragraph.text))
    return segments


def extract_paragraphs(input_path: str) -> list[tuple[str, str]]:
    ext = pathlib.Path(input_path).suffix.lower()
    if ext == ".docx":
        return extract_docx_paragraphs(input_path)
    elif ext == ".pdf":
        return [(label, text) for label, text, _ in _extract_pdf_paragraphs(input_path)]
    else:
        raise ValueError(f"Format non supporté : {ext} (attendu : .docx ou .pdf)")


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

def _cmd_convert(args):
    in_path = pathlib.Path(args.input)
    ext = in_path.suffix.lower()
    if ext == ".docx":
        result = convert_docx(args.input, args.output)
    elif ext == ".pdf":
        result = convert_pdf(args.input, args.output)
    else:
        print(f"Format non supporté : {ext} (attendu : .docx ou .pdf)", file=sys.stderr)
        sys.exit(1)

    report = build_report(result.segments)
    print(f"Converti : {args.input} -> {result.output_path}", file=sys.stderr)
    print(f"{report.n} segment(s), gain global {report.gain_percent_global:.1f} %", file=sys.stderr)
    for w in result.boundary_crossing_warnings:
        print(f"[avertissement] {w}", file=sys.stderr)

    if args.report:
        _write_report(args.report, report.to_dict(include_power_analysis=args.power_analysis), report.to_markdown(include_power_analysis=args.power_analysis))


def _cmd_analyze(args):
    documents = {}
    for input_path in args.inputs:
        try:
            documents[pathlib.Path(input_path).name] = extract_paragraphs(input_path)
        except Exception as e:
            print(f"[erreur] {input_path}: {e}", file=sys.stderr)
    if not documents:
        print("Aucun document exploitable.", file=sys.stderr)
        sys.exit(1)

    multi = build_multi_document_report(documents, granularity=args.granularity)
    print(f"{len(documents)} document(s) — {multi.pooled.n} segment(s) au total (granularité: {args.granularity})", file=sys.stderr)
    print(f"Vue groupée (pooled)  : gain moyen {multi.pooled.mean_gain_percent:.1f} %, IC95 Student "
          f"[{multi.pooled.ci95_gain_percent[0]:.1f} %, {multi.pooled.ci95_gain_percent[1]:.1f} %]", file=sys.stderr)
    print(f"Vue par grappe (n={multi.cluster.n} documents) : IC95 Student "
          f"[{multi.cluster.ci95_gain_percent[0]:.1f} %, {multi.cluster.ci95_gain_percent[1]:.1f} %] (plus prudent)", file=sys.stderr)

    if args.report:
        report_path = pathlib.Path(args.report)
        if report_path.suffix.lower() == ".json":
            import json
            payload = {
                "per_document": {k: v.to_dict() for k, v in multi.per_document.items()},
                "pooled": multi.pooled.to_dict(include_power_analysis=args.power_analysis),
                "cluster": multi.cluster.to_dict(include_power_analysis=args.power_analysis),
            }
            report_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        else:
            report_path.write_text(multi.to_markdown(), encoding="utf-8")
        print(f"Rapport : {report_path}", file=sys.stderr)


def _write_report(report_path_str, dict_payload, markdown_payload):
    report_path = pathlib.Path(report_path_str)
    if report_path.suffix.lower() == ".json":
        import json
        report_path.write_text(json.dumps(dict_payload, ensure_ascii=False, indent=2), encoding="utf-8")
    else:
        report_path.write_text(markdown_payload, encoding="utf-8")
    print(f"Rapport statistique : {report_path}", file=sys.stderr)


def main(argv=None):
    parser = argparse.ArgumentParser(description="Convertit un/des document(s) (.docx/.pdf) en ACC avec rapport statistique.")
    sub = parser.add_subparsers(dest="command", required=True)

    p_convert = sub.add_parser("convert", help="Convertit UN document et écrit le fichier converti (fidélité de format).")
    p_convert.add_argument("input", help="Fichier .docx ou .pdf en orthographe 1979")
    p_convert.add_argument("output", help="Fichier de sortie (même extension que l'entrée)")
    p_convert.add_argument("--report", help="Chemin du rapport statistique (.md ou .json)", default=None)
    p_convert.add_argument("--power-analysis", action="store_true", help="Inclure l'analyse de puissance (calcul plus long).")
    p_convert.set_defaults(func=_cmd_convert)

    p_analyze = sub.add_parser("analyze", help="Regroupe PLUSIEURS documents pour augmenter n (pas de fichier converti en sortie).")
    p_analyze.add_argument("inputs", nargs="+", help="Fichiers .docx/.pdf à regrouper")
    p_analyze.add_argument("--granularity", choices=["paragraph", "sentence"], default="paragraph",
                            help="Unité d'observation : paragraphe (défaut) ou phrase (plus de segments, n plus grand).")
    p_analyze.add_argument("--report", help="Chemin du rapport consolidé (.md ou .json)", default=None)
    p_analyze.add_argument("--power-analysis", action="store_true", help="Inclure l'analyse de puissance dans le JSON (calcul plus long).")
    p_analyze.set_defaults(func=_cmd_analyze)

    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
