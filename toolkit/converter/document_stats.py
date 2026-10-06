"""
document_stats.py
==================

Traitement statistique du gain scriptural 1979 -> AAC au niveau *document*
(par opposition au chiffre unique du chapitre IV du mémoire, "9,3 % sur
un extrait de 140 caractères" — extrait qui, en plus, avait été mal
attribué à René Depestre dans une version antérieure de ce dépôt : il
s'agit en réalité d'un texte personnel de l'auteur du mémoire. Voir
`corpus.py` pour un gain mesuré sur 8 textes indépendants et de sources
diverses : 2,5 % à 9,3 % selon le texte, moyenne 5,7 %, IC95 %
[3,9–7,5 %]).

Ici, chaque paragraphe (ou, à défaut, chaque page) du document fourni
constitue une observation indépendante. Cela permet de remplacer une
démonstration ponctuelle par une estimation avec incertitude quantifiée :

  - moyenne et écart-type du gain (%) entre paragraphes
  - erreur-type de la moyenne (SEM) et intervalle de confiance à 95 %
    (loi de Student, df = n-1)
  - test t apparié (avant vs après, en nombre de caractères) pour vérifier
    que la réduction n'est pas un artefact d'échantillonnage
  - test de normalité de Shapiro-Wilk sur la distribution des gains, pour
    juger de la validité de l'intervalle paramétrique
  - intervalle de confiance bootstrap (percentile, 10 000 ré-échantillons)
    comme vérification non-paramétrique, indépendante de l'hypothèse de
    normalité
  - taille d'effet (d de Cohen pour mesures appariées)
  - décomposition du gain par règle (ch/ou/ng contribuent chacun 1 caractère
    économisé par occurrence ; ui/wi est un renommage neutre, 0 caractère)

Dépendances : numpy, scipy (déjà présents dans l'environnement de
développement du toolkit ; à ajouter à requirements-dev.txt si absent).
"""

from __future__ import annotations

from dataclasses import dataclass, field
import math

import numpy as np
from scipy import stats as sp_stats

from aac_converter import diff_summary, to_aac


# CORRECTIF (revue de code, M4) : `to_dict()` pouvait contenir des valeurs
# `NaN` (ex. quand n=1 ou que Shapiro/corrélation ne sont pas applicables),
# ce qui rend `json.dumps(...)` INVALIDE au sens strict de la norme JSON
# (NaN n'existe pas en JSON -- json.dumps l'écrit quand même par défaut,
# produisant un fichier illisible par la plupart des autres parseurs).
# `_json_safe` remplace récursivement NaN/Inf par `None` (-> `null` en
# JSON), qui est la représentation JSON standard d'une valeur absente.
def _json_safe(obj):
    if isinstance(obj, float):
        return None if (math.isnan(obj) or math.isinf(obj)) else obj
    if isinstance(obj, dict):
        return {k: _json_safe(v) for k, v in obj.items()}
    if isinstance(obj, (list, tuple)):
        return [_json_safe(v) for v in obj]
    return obj


def leave_one_out_paired_t(before, after):
    """Robustesse du test t apparié : le recalcule en retirant tour à tour
    UNE observation. Génère (indice_retiré, t, p). Partagé par
    analyse_complete.py et corpus2_dudh.py (qui ne diffèrent que par le
    libellé affiché)."""
    before, after = np.asarray(before), np.asarray(after)
    for i in range(len(before)):
        keep = np.arange(len(before)) != i
        t, p = sp_stats.ttest_rel(before[keep], after[keep])
        yield i, t, p


@dataclass
class SegmentStat:
    """Une observation = un paragraphe (ou une page, en repli)."""

    label: str
    original: str
    converted: str

    @property
    def chars_before(self) -> int:
        return len(self.original)

    @property
    def chars_after(self) -> int:
        return len(self.converted)

    @property
    def gain_percent(self) -> float:
        if self.chars_before == 0:
            return 0.0
        return (self.chars_before - self.chars_after) / self.chars_before * 100


@dataclass
class DocumentStatisticalReport:
    segments: list[SegmentStat]
    confidence_level: float = 0.95
    bootstrap_resamples: int = 10_000
    bootstrap_seed: int = 42

    # ---- agrégats simples -------------------------------------------------

    @property
    def n(self) -> int:
        return len(self.segments)

    @property
    def chars_before_total(self) -> int:
        return sum(s.chars_before for s in self.segments)

    @property
    def chars_after_total(self) -> int:
        return sum(s.chars_after for s in self.segments)

    @property
    def gain_percent_global(self) -> float:
        """Gain calculé sur le total (équivalent au chiffre du mémoire,
        mais sur l'ensemble du document plutôt qu'un seul extrait)."""
        if self.chars_before_total == 0:
            return 0.0
        return (self.chars_before_total - self.chars_after_total) / self.chars_before_total * 100

    @property
    def _gains(self) -> np.ndarray:
        return np.array([s.gain_percent for s in self.segments], dtype=float)

    @property
    def _before(self) -> np.ndarray:
        return np.array([s.chars_before for s in self.segments], dtype=float)

    @property
    def _after(self) -> np.ndarray:
        return np.array([s.chars_after for s in self.segments], dtype=float)

    # ---- statistiques descriptives ----------------------------------------

    @property
    def mean_gain_percent(self) -> float:
        return float(np.mean(self._gains))

    @property
    def stdev_gain_percent(self) -> float:
        """Écart-type d'échantillon (ddof=1) — non défini (nan) si n<2."""
        if self.n < 2:
            return float("nan")
        return float(np.std(self._gains, ddof=1))

    @property
    def sem_gain_percent(self) -> float:
        if self.n < 2:
            return float("nan")
        return self.stdev_gain_percent / math.sqrt(self.n)

    @property
    def ci95_gain_percent(self) -> tuple[float, float]:
        """Intervalle de confiance paramétrique (Student, df=n-1) sur la
        moyenne du gain par paragraphe."""
        if self.n < 2:
            return (float("nan"), float("nan"))
        alpha = 1 - self.confidence_level
        t_crit = sp_stats.t.ppf(1 - alpha / 2, df=self.n - 1)
        margin = t_crit * self.sem_gain_percent
        return (self.mean_gain_percent - margin, self.mean_gain_percent + margin)

    # ---- test d'hypothèse : le gain est-il réel ou dû au hasard ? --------

    @property
    def paired_ttest(self) -> dict:
        """H0 : pas de différence entre nb de caractères avant/après.
        H1 (unilatérale) : le texte 1979 a plus de caractères que l'AAC.
        """
        if self.n < 2:
            return {"t_stat": float("nan"), "p_value": float("nan"), "df": 0, "applicable": False}
        t_stat, p_value = sp_stats.ttest_rel(self._before, self._after, alternative="greater")
        return {"t_stat": float(t_stat), "p_value": float(p_value), "df": self.n - 1, "applicable": True}

    @property
    def shapiro_normality(self) -> dict:
        """Teste si la distribution des gains par paragraphe est
        raisonnablement normale (nécessaire pour se fier à l'IC de Student
        plutôt qu'au seul IC bootstrap). Nécessite n >= 3."""
        if self.n < 3:
            return {"w_stat": float("nan"), "p_value": float("nan"), "applicable": False}
        w_stat, p_value = sp_stats.shapiro(self._gains)
        return {"w_stat": float(w_stat), "p_value": float(p_value), "applicable": True}

    @property
    def cohens_d_paired(self) -> float:
        """Taille d'effet pour mesures appariées : d = moyenne(diff) / écart-type(diff).
        Repères usuels (Cohen 1988) : 0.2 petit, 0.5 moyen, 0.8 grand."""
        if self.n < 2:
            return float("nan")
        diff = self._before - self._after
        sd = np.std(diff, ddof=1)
        if sd == 0:
            return float("inf") if np.mean(diff) != 0 else 0.0
        return float(np.mean(diff) / sd)

    @property
    def bootstrap_ci95_gain_percent(self) -> tuple[float, float]:
        """IC non-paramétrique par ré-échantillonnage (percentile method).
        Ne suppose pas la normalité — sert de contrôle de robustesse
        vis-à-vis de l'IC de Student, utile quand n est petit ou que
        Shapiro-Wilk rejette la normalité."""
        if self.n < 2:
            return (float("nan"), float("nan"))
        rng = np.random.default_rng(self.bootstrap_seed)
        gains = self._gains
        means = np.empty(self.bootstrap_resamples)
        for i in range(self.bootstrap_resamples):
            sample = rng.choice(gains, size=self.n, replace=True)
            means[i] = sample.mean()
        alpha = 1 - self.confidence_level
        lo, hi = np.percentile(means, [100 * alpha / 2, 100 * (1 - alpha / 2)])
        return (float(lo), float(hi))

    @property
    def bootstrap_ci95_cohens_d(self) -> tuple[float, float]:
        """Même principe que l'IC bootstrap du gain, appliqué au d de Cohen :
        à quel point la taille d'effet elle-même est-elle stable si on
        avait eu un tirage différent de paragraphes ?"""
        if self.n < 2:
            return (float("nan"), float("nan"))
        rng = np.random.default_rng(self.bootstrap_seed + 1)
        before, after = self._before, self._after
        ds = np.empty(self.bootstrap_resamples)
        for i in range(self.bootstrap_resamples):
            idx = rng.integers(0, self.n, size=self.n)
            diff = before[idx] - after[idx]
            sd = np.std(diff, ddof=1)
            ds[i] = 0.0 if (sd == 0 and np.mean(diff) == 0) else (np.inf if sd == 0 else np.mean(diff) / sd)
        finite = ds[np.isfinite(ds)]
        if len(finite) < self.bootstrap_resamples * 0.5:
            return (float("nan"), float("nan"))
        alpha = 1 - self.confidence_level
        lo, hi = np.percentile(finite, [100 * alpha / 2, 100 * (1 - alpha / 2)])
        return (float(lo), float(hi))

    @property
    def permutation_test(self) -> dict:
        """Test de permutation (Monte Carlo, par retournement de signe) sur
        la différence appariée avant-après. N'a AUCUNE hypothèse de
        normalité ni de forme de distribution — troisième vérification
        indépendante du gain, à côté du test t (paramétrique) et de l'IC
        bootstrap. Principe : sous H0 (aucun effet directionnel), le signe
        de chaque différence par-paragraphe serait aussi bien + que -.
        On retire ce signe au hasard `n_permutations` fois et on regarde
        combien de fois la moyenne obtenue dépasse la moyenne observée."""
        if self.n < 2:
            return {"observed_mean_diff": float("nan"), "p_value": float("nan"), "n_permutations": 0, "applicable": False}
        diffs = self._before - self._after
        observed = float(np.mean(diffs))
        rng = np.random.default_rng(self.bootstrap_seed + 2)
        n_perm = self.bootstrap_resamples
        signs = rng.choice([-1.0, 1.0], size=(n_perm, self.n))
        perm_means = (signs * diffs).mean(axis=1)
        # p unilatérale : H1 = l'effet observé est positif (before > after)
        p_value = float((np.sum(perm_means >= observed) + 1) / (n_perm + 1))
        return {"observed_mean_diff": observed, "p_value": p_value, "n_permutations": n_perm, "applicable": True}

    @property
    def length_gain_correlation(self) -> dict:
        """Le gain % dépend-il artificiellement de la longueur du segment ?
        Une corrélation forte indiquerait un biais (p.ex. les longs
        paragraphes gagnent systématiquement plus/moins) plutôt qu'un
        effet homogène des règles de conversion. On s'attend à une
        corrélation faible : la densité de ch/ou/ng ne dépend pas de la
        longueur du paragraphe, seulement du contenu."""
        if self.n < 3:
            return {"r": float("nan"), "p_value": float("nan"), "applicable": False}
        r, p = sp_stats.pearsonr(self._before, self._gains)
        return {"r": float(r), "p_value": float(p), "applicable": True}

    def power_analysis(self, target_n_values=(10, 20, 30, 50, 100), alpha=0.05, n_simulations=2000, seed=None) -> dict:
        """Puissance statistique estimée par simulation : pour chaque taille
        d'échantillon candidate, on tire `n_simulations` échantillons par
        ré-échantillonnage bootstrap (avec remise) des différences
        par-paragraphe RÉELLEMENT observées -- pas d'hypothèse de forme de
        distribution sur les données d'origine -- puis on applique un test t
        classique à chaque tirage simulé et on compte la proportion de fois
        où p < alpha. Répond à « combien de paragraphes faut-il pour un
        résultat robuste ? ».

        Note (CORRECTIF, revue de code, M4) : `n_simulations` (2000 par
        défaut) est INDÉPENDANT de `bootstrap_resamples` (10 000, utilisé
        pour les IC bootstrap ailleurs dans cette classe) -- ce sont deux
        simulations distinctes. Le nombre de tirages réellement utilisé est
        inclus dans le résultat (clé "n_simulations") pour que le rapport
        Markdown l'affiche correctement plutôt que de supposer qu'il vaut
        `bootstrap_resamples`.
        """
        if self.n < 2:
            return {"achieved_power_at_n": float("nan"), "by_n": {}, "required_n_80pct": None, "n_simulations": n_simulations}
        rng = np.random.default_rng(seed if seed is not None else self.bootstrap_seed + 3)
        diffs = (self._before - self._after)

        def power_at(n_target):
            rejections = 0
            for _ in range(n_simulations):
                sample = rng.choice(diffs, size=n_target, replace=True)
                sd = np.std(sample, ddof=1)
                if sd == 0:
                    rejected = np.mean(sample) > 0
                else:
                    t_stat = (np.mean(sample) / sd) * math.sqrt(n_target)
                    p = 1 - sp_stats.t.cdf(t_stat, df=n_target - 1)
                    rejected = p < alpha
                rejections += int(rejected)
            return rejections / n_simulations

        by_n = {n_target: round(power_at(n_target), 3) for n_target in sorted(set(target_n_values))}
        achieved_at_current_n = round(power_at(self.n), 3)

        required_n_80pct = None
        for n_target in range(max(2, self.n), 501):
            if power_at(n_target) >= 0.80:
                required_n_80pct = n_target
                break

        return {
            "achieved_power_at_n": achieved_at_current_n,
            "current_n": self.n,
            "by_n": by_n,
            "required_n_80pct": required_n_80pct,
            "n_simulations": n_simulations,
        }

    # ---- décomposition par règle -------------------------------------------

    @property
    def rule_contribution(self) -> dict:
        """Combien de caractères chaque règle a réellement économisés,
        agrégé sur tout le document. ch/ou/ng économisent 1 caractère par
        occurrence (digramme -> monogramme) ; ui->wi est un renommage
        neutre (0 caractère). La somme prédite est comparée au gain réel
        pour détecter toute interaction inattendue entre règles."""
        totals = {"ch": 0, "ou": 0, "ng": 0, "ui": 0}
        for s in self.segments:
            counts = diff_summary(s.original)
            for k in totals:
                totals[k] += counts[k]
        predicted_savings = totals["ch"] + totals["ou"] + totals["ng"]
        actual_savings = self.chars_before_total - self.chars_after_total
        return {
            "occurrences": totals,
            "predicted_savings": predicted_savings,
            "actual_savings": actual_savings,
            "matches": predicted_savings == actual_savings,
        }

    # ---- rendu -------------------------------------------------------------

    def to_dict(self, include_power_analysis: bool = False) -> dict:
        ci_lo, ci_hi = self.ci95_gain_percent
        boot_lo, boot_hi = self.bootstrap_ci95_gain_percent
        d_boot_lo, d_boot_hi = self.bootstrap_ci95_cohens_d
        ttest = self.paired_ttest
        shapiro = self.shapiro_normality
        perm = self.permutation_test
        corr = self.length_gain_correlation
        out = {
            "n_segments": self.n,
            "chars_before_total": self.chars_before_total,
            "chars_after_total": self.chars_after_total,
            "gain_percent_global": round(self.gain_percent_global, 2),
            "mean_gain_percent_per_segment": round(self.mean_gain_percent, 2),
            "stdev_gain_percent": round(self.stdev_gain_percent, 2) if self.n > 1 else None,
            "sem_gain_percent": round(self.sem_gain_percent, 3) if self.n > 1 else None,
            "ci95_student": [round(ci_lo, 2), round(ci_hi, 2)],
            "ci95_bootstrap": [round(boot_lo, 2), round(boot_hi, 2)],
            "paired_ttest_before_gt_after": {
                "t": round(ttest["t_stat"], 3),
                "p_value": ttest["p_value"],
                "df": ttest["df"],
                "applicable": ttest["applicable"],
            },
            "permutation_test_before_gt_after": {
                "observed_mean_diff_chars": round(perm["observed_mean_diff"], 3) if self.n > 1 else None,
                "p_value": perm["p_value"],
                "n_permutations": perm["n_permutations"],
                "applicable": perm["applicable"],
            },
            "shapiro_normality_on_gains": {
                "W": round(shapiro["w_stat"], 3) if shapiro["applicable"] else None,
                "p_value": shapiro["p_value"] if shapiro["applicable"] else None,
                "applicable": shapiro["applicable"],
            },
            "cohens_d_paired": round(self.cohens_d_paired, 3) if self.n > 1 else None,
            "cohens_d_ci95_bootstrap": [round(d_boot_lo, 3), round(d_boot_hi, 3)] if self.n > 1 else None,
            "length_gain_correlation": {
                "r": round(corr["r"], 3) if corr["applicable"] else None,
                "p_value": round(corr["p_value"], 4) if corr["applicable"] else None,
                "applicable": corr["applicable"],
            },
            "rule_contribution": self.rule_contribution,
        }
        if include_power_analysis:
            out["power_analysis"] = self.power_analysis()
        return _json_safe(out)

    def to_markdown(self, title: str = "Rapport statistique de conversion 1979 -> AAC", include_power_analysis: bool = False) -> str:
        d = self.to_dict(include_power_analysis=include_power_analysis)
        ci = d["ci95_student"]
        boot = d["ci95_bootstrap"]
        tt = d["paired_ttest_before_gt_after"]
        pm = d["permutation_test_before_gt_after"]
        sh = d["shapiro_normality_on_gains"]
        rc = d["rule_contribution"]
        corr = d["length_gain_correlation"]
        d_ci = d["cohens_d_ci95_bootstrap"]

        # CORRECTIF (revue de code, M4) : auparavant, quand le test n'était
        # pas applicable (n<2), p_value valait NaN et `nan < 0.05` est
        # toujours faux en Python -- le rapport affichait donc à tort
        # "NON significatif" pour un test qui n'avait tout simplement pas
        # eu lieu. On distingue maintenant explicitement les deux cas via
        # le champ "applicable".
        if tt["applicable"]:
            p_str = "< 0.001" if tt["p_value"] < 0.001 else f"{tt['p_value']:.4f}"
            sig = "significatif" if tt["p_value"] < 0.05 else "NON significatif"
        else:
            p_str = "n/a"
            sig = "non applicable (n<2)"
        pm_p_str = "n/a"
        pm_sig = "non applicable (n<2)"
        if pm["applicable"]:
            pm_p_str = "< 0.001" if pm["p_value"] < 0.001 else f"{pm['p_value']:.4f}"
            pm_sig = "significatif" if pm["p_value"] < 0.05 else "NON significatif"

        t_str = f"t({tt['df']}) = {tt['t']}" if tt["applicable"] else "test t"
        lines = [
            f"# {title}",
            "",
            f"- Segments analysés (paragraphes) : **{d['n_segments']}**",
            f"- Caractères avant -> après (total) : **{d['chars_before_total']} -> {d['chars_after_total']}**",
            f"- Gain global : **{d['gain_percent_global']} %**",
            "",
            "## Gain par paragraphe (échantillon)",
            "",
            f"- Moyenne : **{d['mean_gain_percent_per_segment']} %**",
            f"- Écart-type (n-1) : {d['stdev_gain_percent']} points",
            f"- Erreur-type (SEM) : {d['sem_gain_percent']}",
            f"- IC 95 % (Student, df={tt['df']}) : [{ci[0]} %, {ci[1]} %]",
            f"- IC 95 % (bootstrap, {self.bootstrap_resamples} ré-échantillons) : [{boot[0]} %, {boot[1]} %]",
            "",
            "## Le gain est-il réel, ou un artefact d'échantillonnage ? (trois tests indépendants)",
            "",
            f"1. Test t apparié (paramétrique) : {t_str}, p = {p_str} → **{sig}** au seuil 5 %.",
            f"2. Test de permutation (Monte Carlo, {pm['n_permutations']} tirages, sans hypothèse de distribution) : "
            f"p = {pm_p_str} → **{pm_sig}**.",
        ]
        if sh["applicable"]:
            normal = "compatible avec une distribution normale" if (sh["p_value"] or 0) > 0.05 else "s'écarte d'une distribution normale"
            lines.append(f"3. Shapiro-Wilk sur les gains par paragraphe : W = {sh['W']}, p = {sh['p_value']:.4f} → {normal}.")
        else:
            lines.append("3. Shapiro-Wilk non applicable (n<3) ; se fier au test de permutation et à l'IC bootstrap plutôt qu'aux tests paramétriques.")
        lines += [
            "",
            f"Taille d'effet (d de Cohen, apparié) : **{d['cohens_d_paired']}**"
            + (f", IC 95 % bootstrap : [{d_ci[0]}, {d_ci[1]}]." if d_ci else "."),
        ]
        if corr["applicable"]:
            corr_note = (
                "aucune corrélation notable — le gain ne dépend pas artificiellement de la longueur du segment."
                if corr["p_value"] is not None and corr["p_value"] > 0.05
                else "corrélation détectée entre longueur de segment et gain % — à examiner (voir tableau par segment)."
            )
            lines.append(f"Corrélation longueur-du-segment / gain % : r = {corr['r']}, p = {corr['p_value']} → {corr_note}")
        lines += [
            "",
            "## D'où vient le gain (décomposition par règle)",
            "",
            f"| Règle | Occurrences | Caractères économisés / occurrence |",
            f"|---|---|---|",
            f"| ch -> š | {rc['occurrences']['ch']} | 1 |",
            f"| ou -> ŏ | {rc['occurrences']['ou']} | 1 |",
            f"| ng -> ŋ | {rc['occurrences']['ng']} | 1 |",
            f"| ui -> wi | {rc['occurrences']['ui']} | 0 (renommage, pas de compression) |",
            "",
            f"Gain prédit à partir des règles : **{rc['predicted_savings']} caractères**. "
            f"Gain réellement mesuré : **{rc['actual_savings']} caractères**. "
            + ("Les deux coïncident exactement — aucune interaction non-modélisée entre règles."
               if rc["matches"] else
               "⚠️ Écart détecté — vérifier une interaction entre règles non prise en compte (voir tests)."),
        ]
        if include_power_analysis and "power_analysis" in d:
            pa = d["power_analysis"]
            lines += [
                "",
                "## Combien de paragraphes faut-il pour un résultat robuste ?",
                "",
                f"Puissance estimée par simulation (ré-échantillonnage bootstrap des écarts observés, {pa['n_simulations']} tirages "
                f"par taille testée) à l'échantillon actuel (n={pa['current_n']}) : **{pa['achieved_power_at_n']}**"
                f" (probabilité de détecter l'effet observé si l'expérience était répétée).",
                f"Taille d'échantillon nécessaire pour une puissance de 80 % : "
                + (f"**{pa['required_n_80pct']} segments**." if pa['required_n_80pct'] else "non atteinte avant n=500 — l'effet est trop faible ou trop variable pour être détecté de façon fiable, indépendamment de la taille de l'échantillon."),
                f"Puissance par taille d'échantillon : " + ", ".join(f"n={k} → {v}" for k, v in pa["by_n"].items()),
            ]
        return "\n".join(lines)


def build_report(segments: list[tuple[str, str]], **kwargs) -> DocumentStatisticalReport:
    """segments : liste de (label, texte_original_1979). La conversion AAC
    est calculée ici pour garantir la cohérence avec aac_converter.to_aac."""
    stats_segments = [
        SegmentStat(label=label, original=text, converted=to_aac(text))
        for label, text in segments
        if text.strip()
    ]
    return DocumentStatisticalReport(segments=stats_segments, **kwargs)


_SENTENCE_SPLIT_RE = __import__("re").compile(r"(?<=[.!?])\s+(?=[A-ZÀ-Þ0-9])")


def split_into_sentences(paragraph_text: str) -> list[str]:
    """Découpe un paragraphe en phrases (augmente n : plus de segments =
    intervalles de confiance plus étroits, au prix d'une indépendance
    entre observations plus faible qu'au niveau paragraphe — voir la
    note sur l'analyse "cluster" ci-dessous). Heuristique simple : coupe
    après .!? suivi d'une majuscule ou d'un chiffre ; ne gère pas les
    abréviations (M., etc.) — pour un mémoire, une relecture rapide du
    tableau segment-par-segment suffit à repérer une coupe aberrante."""
    parts = [p.strip() for p in _SENTENCE_SPLIT_RE.split(paragraph_text) if p.strip()]
    return parts if parts else [paragraph_text]


@dataclass
class MultiDocumentReport:
    """Regroupe plusieurs documents pour augmenter n. Deux niveaux de
    lecture sont fournis, car les combiner à tort donnerait un intervalle
    de confiance trop optimiste :

      - `pooled`  : chaque paragraphe (ou phrase) de chaque document comme
                    une observation indépendante -> IC le plus étroit,
                    mais un peu optimiste (des paragraphes du même
                    document se ressemblent souvent plus qu'entre
                    documents : même auteur, même sujet).
      - `cluster` : chaque DOCUMENT résumé par sa moyenne -> n = nombre de
                    documents, IC plus large mais plus honnête, car il ne
                    traite plus les paragraphes d'un même texte comme
                    interchangeables avec ceux d'un autre.

    En pratique : le `cluster` est la borne prudente à citer dans un
    mémoire ; le `pooled` montre ce qu'on gagnerait avec un corpus plus
    large et plus varié.
    """

    per_document: dict[str, DocumentStatisticalReport]
    pooled: DocumentStatisticalReport
    cluster: DocumentStatisticalReport  # n = nb documents, "segment" = 1 doc

    def to_markdown(self) -> str:
        lines = [f"# Rapport consolidé — {len(self.per_document)} document(s)", ""]
        lines.append("## Par document")
        lines.append("")
        lines.append("| Document | Segments | Gain global | Gain moyen/segment |")
        lines.append("|---|---|---|---|")
        for name, r in self.per_document.items():
            lines.append(f"| {name} | {r.n} | {r.gain_percent_global:.1f} % | {r.mean_gain_percent:.1f} % |")
        lines.append("")
        lines.append(f"## Vue regroupée (pooled, n={self.pooled.n} segments — optimiste)")
        lines.append("")
        lines.append(self.pooled.to_markdown(title="Regroupé (segment = paragraphe/phrase, tous documents confondus)"))
        lines.append("")
        lines.append(f"## Vue par grappe (cluster, n={self.cluster.n} documents — prudente)")
        lines.append("")
        lines.append(self.cluster.to_markdown(title="Par grappe (segment = document entier)"))
        return "\n".join(lines)


def build_multi_document_report(
    documents: dict[str, list[tuple[str, str]]], granularity: str = "paragraph", **kwargs
) -> MultiDocumentReport:
    """documents : {nom_du_fichier: [(label, texte_original), ...]}.
    granularity : 'paragraph' (défaut) ou 'sentence' (augmente n en
    subdivisant chaque paragraphe en phrases avant de construire les
    segments)."""
    per_document: dict[str, DocumentStatisticalReport] = {}
    pooled_segments: list[tuple[str, str]] = []
    cluster_segments: list[tuple[str, str]] = []

    for doc_name, paragraphs in documents.items():
        if granularity == "sentence":
            expanded = []
            for label, text in paragraphs:
                for i, sentence in enumerate(split_into_sentences(text)):
                    expanded.append((f"{label} · phrase {i + 1}", sentence))
            paragraphs = expanded

        report = build_report(paragraphs, **kwargs)
        per_document[doc_name] = report

        for s in report.segments:
            pooled_segments.append((f"{doc_name} · {s.label}", s.original))
        # niveau grappe : un document = une seule "observation" (son texte concaténé)
        doc_full_text = " ".join(s.original for s in report.segments)
        if doc_full_text.strip():
            cluster_segments.append((doc_name, doc_full_text))

    pooled = build_report(pooled_segments, **kwargs)
    cluster = build_report(cluster_segments, **kwargs)
    return MultiDocumentReport(per_document=per_document, pooled=pooled, cluster=cluster)
