"""Tests du module document_stats — s'assure que le traitement statistique
reste correct (et pas seulement que le code tourne)."""

import math
import sys
import pathlib

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

from document_stats import build_report, SegmentStat, DocumentStatisticalReport, build_multi_document_report


AUTOGRAF_LINCOLN = (
    "Chante pou chase lapli nan kò mwen, chante pou san mwen rete cho nan "
    "tanpèt la, pou klète lang manman nou klere sou ekran toupatou sou latè."
)
# Texte personnel de l'auteur (Lincoln Compère, document AAC/AKI) — anciennement
# mal étiqueté "Depestre" dans ce fichier. Voir corpus.py pour un gain mesuré
# sur 8 textes indépendants et de sources diverses (2,5 % à 9,3 %).


def test_single_segment_matches_memoire_figures():
    """Le chiffre historique du mémoire (140 -> 127, -9,3 %) doit rester
    reproductible tel quel via le pipeline statistique, pas seulement via
    acc_converter.convert()."""
    report = build_report([("lincoln", AUTOGRAF_LINCOLN)])
    assert report.chars_before_total == 140
    assert report.chars_after_total == 127
    assert round(report.gain_percent_global, 1) == 9.3


def test_stdev_and_ci_undefined_for_single_segment():
    report = build_report([("x", AUTOGRAF_LINCOLN)])
    assert math.isnan(report.stdev_gain_percent)
    lo, hi = report.ci95_gain_percent
    assert math.isnan(lo) and math.isnan(hi)


def test_multi_segment_ci_contains_mean():
    segments = [
        ("a", "Chak moun gen dwa pou yo chèche travay."),
        ("b", "Nou vle yon lekòl kote timoun ka aprann."),
        ("c", "Ki jan ou fè konnen si yon moun gen kouraj?"),
        ("d", "Timoun yo renmen jwe nan lakou lekòl la."),
    ]
    report = build_report(segments)
    lo, hi = report.ci95_gain_percent
    assert lo <= report.mean_gain_percent <= hi
    # l'IC bootstrap doit être du même ordre de grandeur que l'IC de Student
    blo, bhi = report.bootstrap_ci95_gain_percent
    assert blo <= report.mean_gain_percent <= bhi


def test_paired_ttest_significant_when_gain_consistent():
    segments = [
        ("a", "Chak moun gen chans pou chache travay nan chak vil."),
        ("b", "Chante ak dans se de bagay moun renmen anpil nan tout peyi."),
        ("c", "Chemen an long men chak moun ka rive nan bout li."),
        ("d", "Chak chapit gen anpil chanjman nan tout istwa a."),
    ]
    report = build_report(segments)
    result = report.paired_ttest
    assert result["p_value"] < 0.05
    assert result["t_stat"] > 0  # avant > après, cohérent avec la direction testée


def test_paired_ttest_not_significant_when_no_gain():
    # Aucune séquence opaque -> aucune conversion -> aucune différence.
    segments = [
        ("a", "Bèl kay la kle e lave pa gwo pwoblèm."),
        ("b", "Mwen te la e li te la tou pa gwo bri."),
        ("c", "Yo ale e yo tounen san yo pa di anyen."),
    ]
    report = build_report(segments)
    result = report.paired_ttest
    assert result["p_value"] > 0.05


def test_rule_contribution_matches_actual_savings():
    segments = [
        ("a", AUTOGRAF_LINCOLN),
        ("b", "Chak moun ka wè ou nan lakou a."),
    ]
    report = build_report(segments)
    rc = report.rule_contribution
    assert rc["matches"] is True
    assert rc["predicted_savings"] == rc["actual_savings"]


def test_cohens_d_zero_when_no_variation():
    segments = [("a", "Bèl kay la."), ("b", "Bon jan tan an.")]
    report = build_report(segments)
    assert report.cohens_d_paired == 0.0


def test_to_dict_and_to_markdown_do_not_crash():
    segments = [
        ("a", AUTOGRAF_LINCOLN),
        ("b", "Chak moun ka wè ou nan lakou a."),
        ("c", "Timoun yo renmen jwe nan lakou lekòl la."),
    ]
    report = build_report(segments)
    d = report.to_dict()
    assert d["n_segments"] == 3
    md = report.to_markdown()
    assert "Rapport statistique" in md
    assert "%" in md


def test_permutation_test_low_resolution_at_small_n():
    """Avec n petit, l'espace des permutations est trop grossier pour
    atteindre p<0,05 même si le test t paramétrique, lui, y arrive — c'est
    un avertissement honnête sur les limites d'un tout petit échantillon,
    pas un bug : avec n=4, le p unilatéral minimal possible est 1/16=0,0625."""
    segments = [
        ("a", "Chak moun gen chans pou chache travay nan chak vil."),
        ("b", "Chante ak dans se de bagay moun renmen anpil nan tout peyi."),
        ("c", "Chemen an long men chak moun ka rive nan bout li."),
        ("d", "Chak chapit gen anpil chanjman nan tout istwa a."),
    ]
    report = build_report(segments)
    perm = report.permutation_test
    assert report.n == 4
    assert perm["p_value"] >= 1 / 16 - 0.01  # jamais en dessous de la résolution du test


def test_multi_document_pooled_vs_cluster_n():
    docs = {
        "d1.docx": [("p1", "Chak moun gen chans pou chache travay.")],
        "d2.docx": [
            ("p1", "Chante ak dans se de bagay moun renmen anpil."),
            ("p2", "Chemen an long men chak moun ka rive nan bout li."),
        ],
    }
    multi = build_multi_document_report(docs)
    assert multi.pooled.n == 3          # 1 + 2 segments
    assert multi.cluster.n == 2         # 2 documents


def test_sentence_granularity_increases_n():
    docs = {
        "d1.docx": [("p1", "Chak moun gen dwa. Nou vle yon lekòl. Ki jan ou fè konnen?")],
    }
    para_level = build_multi_document_report(docs, granularity="paragraph")
    sent_level = build_multi_document_report(docs, granularity="sentence")
    assert para_level.pooled.n == 1
    assert sent_level.pooled.n == 3


def test_bootstrap_ci_cohens_d_contains_point_estimate():
    segments = [
        ("a", "Chak moun gen chans pou chache travay nan chak vil."),
        ("b", "Chante ak dans se de bagay moun renmen anpil nan tout peyi."),
        ("c", "Chemen an long men chak moun ka rive nan bout li."),
        ("d", "Chak chapit gen anpil chanjman nan tout istwa a."),
        ("e", "Timoun yo renmen jwe nan lakou lekòl la."),
    ]
    report = build_report(segments)
    lo, hi = report.bootstrap_ci95_cohens_d
    assert lo <= report.cohens_d_paired <= hi


def test_power_analysis_required_n_at_least_current_n():
    segments = [
        ("a", "Chak moun gen chans pou chache travay nan chak vil."),
        ("b", "Chante ak dans se de bagay moun renmen anpil nan tout peyi."),
        ("c", "Chemen an long men chak moun ka rive nan bout li."),
    ]
    report = build_report(segments)
    pa = report.power_analysis(n_simulations=300)
    if pa["required_n_80pct"] is not None:
        assert pa["required_n_80pct"] >= report.n


if __name__ == "__main__":
    import subprocess
    subprocess.run([sys.executable, "-m", "pytest", __file__, "-v"])
