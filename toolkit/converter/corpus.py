"""
corpus.py
=========

Corpus de validation à 8 textes indépendants pour le gain scriptural
1979 -> AAC, remplaçant l'ancien chiffre unique "9,3 % sur le corpus
Depestre" (qui reposait sur UN seul extrait de 140 caractères, et qui
en plus était mal attribué : ce texte est en réalité un texte personnel
de l'auteur du mémoire, pas un extrait de René Depestre).

Chaque entrée est un texte complet, indépendant, avec une source
vérifiable :

  - 2 textes personnels de l'auteur (Lincoln Compère), rédigés dans le
    cadre du document AAC/AKI ;
  - un extrait de la Constitution haïtienne de 1987 (Atik 1 + Atik 5) —
    texte légal officiel, domaine public ;
  - l'Article 1 de la Déclaration universelle des droits de l'homme en
    kreyòl, traduction officielle publiée par le Haut-Commissariat des
    Nations Unies aux droits de l'homme (OHCHR) ;
  - 2 lots de pwovèb kreyòl (proverbes) — tradition orale anonyme,
    domaine public ;
  - un extrait d'Oswald Durand, "Choukoun" (1883 ; l'auteur est mort en
    1906, l'œuvre est dans le domaine public) ;
  - un extrait de Georges Sylvain, "Cric? Crac!" (1901 ; l'auteur est
    mort en 1925, l'œuvre est dans le domaine public).

Volontairement absents : des extraits d'auteurs dont l'œuvre reste sous
droits (Frankétienne, mort en 2025 ; René Depestre ; Georges Castera,
mort en 2020). Les reproduire ici, dans un dépôt public, serait une
violation de copyright — voir la discussion dans README.md.

Ce module ne fait AUCUNE hypothèse de représentativité statistique du
créole écrit en général : c'est un échantillon de convenance choisi
pour sa diversité de sources (personnel, légal, international,
oral/anonyme, littéraire ancien), pas un échantillon aléatoire. Le but
est de montrer que le gain n'est pas un artefact d'un seul extrait
choisi, pas d'estimer une "vraie" moyenne de la langue.
"""

from __future__ import annotations

CORPUS: dict[str, dict[str, str]] = {
    "lincoln_chant": {
        "auteur": "Lincoln Compère",
        "source": "Texte personnel, document AAC/AKI",
        "annee": "2025",
        "texte": (
            "Chante pou chase lapli nan kò mwen, chante pou san mwen rete cho nan "
            "tanpèt la, pou klète lang manman nou klere sou ekran toupatou sou latè."
        ),
    },
    "lincoln_dwa_travay": {
        "auteur": "Lincoln Compère",
        "source": "Texte personnel, document AAC/AKI",
        "annee": "2025",
        "texte": "Chak moun gen dwa pou yo chèche travay san pwoblèm nan peyi a.",
    },

    # "lincoln_lang_manmanm": {
    #     "auteur": "Lincoln Compère",
    #     "source": "Texte personnel, document AAC/AKI",
    #     "annee": "2025",
    #     "texte": (
    #         "Mwen pa nan tete lang ak movezè, move lanyon, moun san zantray"
    #         "Mwen se yon natif natal, nèg lakay ki pap janmen manje zong devan lennmi."
    #         "Tankou Kapwa lanmò, tankou Desalin, tankou Mari Jàn, mwen ap goumen pou nansyon sa."
    #         "mwen ap goumen pou lang manman m. M’ap kontinye pale lang manman m ak fyète"
    #         "san m pa bliye grangou ki blayi nan peyi an mwen."
    #     ),
    # },

    "konstitisyon_1987": {
        "auteur": "Assemblée constituante haïtienne",
        "source": "Constitution de la République d'Haïti, 1987 (Atik 1 + Atik 5) — domaine public",
        "annee": "1987",
        "texte": (
            "Ayiti se yon Repiblik, endivizib, souvren, endepandan, koperatif, lib, "
            "demokratik ak sosyal. Sèl lang ki simante tout Ayisyen ansanm, se lang "
            "kreyòl. Kreyòl ak Franse, se lang ofisyèl Repiblik d Ayiti."
        ),
    },
    "dudh_atik1": {
        "auteur": "Nations Unies (OHCHR)",
        "source": "Déclaration universelle des droits de l'homme, Atik 1, traduction officielle",
        "annee": "1948",
        "texte": (
            "Tout moun fèt lib, egal ego pou diyite kou wè dwa. Nou gen la rezon ak "
            "la konsyans epi nou fèt pou nou aji youn ak lot ak yon lespri fwatènite."
        ),
    },
    "pwoveb_lavi": {
        "auteur": "Tradition orale (anonyme)",
        "source": "Pwovèb kreyòl — lot A, domaine public",
        "annee": None,
        "texte": (
            "Piti piti, zwazo fè nich li. Dèyè mòn, gen mòn. Men anpil, chay pa lou. "
            "Wòch nan dlo pa konnen mizè wòch nan solèy."
        ),
    },
    "pwoveb_travay": {
        "auteur": "Tradition orale (anonyme)",
        "source": "Pwovèb kreyòl — lot B, domaine public",
        "annee": None,
        "texte": (
            "Tout otan ou gen tèt, ou ka mete chapo. Kreyòl pale, kreyòl konprann. "
            "Se lave men siye atè. Santi bon koute chè."
        ),
    },
    "durand_choukoun": {
        "auteur": "Oswald Durand (1840–1906)",
        "source": '"Choukoun" (1883) — domaine public (auteur mort en 1906)',
        "annee": "1883",
        "texte": (
            "Dèyè yon gwo touf pengwen\n"
            "Lòt jou mwen kontre Choukoun\n"
            "Li souri lè li wè mwen\n"
            "Mwen di: O! a la yon bèl moun!\n"
            "Li di: Ou trouve sa, chè?\n"
            "Ti zwezo t ap koute nou an lè,\n"
            "Kan m sonje sa, mwen genyen lapenn\n"
            "Kar depi jou la, de pye mwen lan chenn!\n"
            "Choukoun se yon marabou\n"
            "Zye li klere kon chandèl\n"
            "Li genyen tete doubout...\n"
            "A! si Choukoun te fidèl!\n"
            "Nou rete koze lontan\n"
            "Jouk zwezo lan bwa te parèt kontan!...\n"
            "Pito bliye sa, se twò gran lapenn,\n"
            "Kar depi jou là de pye mwen lan chenn!\n"
            "Ti dan Choukoun blanch kou lèt.\n"
            "Bouch li koulè kayimit:\n"
            "Li pa gwo fanm, li grasèt:\n"
            "Fanm kon sa plè mwen toutsuit...\n"
            "Tan pase pa tan jodi!...\n"
            "Zwezo te tande tou sa li te di\n"
            "Si yo sonje sa, yo dwe lan lapenn,\n"
            "Kar depi jou la, de pye mwen lan chenn!"
        ),
    },
    "sylvain_cigal_founmi": {
        "auteur": "Georges Sylvain (1866–1925)",
        "source": '"Cric? Crac!" (1901) — domaine public (auteur mort en 1925)',
        "annee": "1901",
        "texte": (
            "Chante, fò kwè se bagay ki\n"
            "Dou nan lavi!\n"
            "Mwen konnen moun sa deja fè\n"
            "Bliye manje.\n"
            "Atò, se sa menm ki rive\n"
            "Kòmè Lasigal, mwa pase:\n"
            "Kòmè te san manje, san bwè,\n"
            "Depi de jou;\n"
            "Sou dènye swè la, yon grangou\n"
            "Mete dife nan kò kòmè.\n"
            "Way! Li kouri kay Sò Fourni,\n"
            "Yon vwazin li.\n"
            "Frape: Ch! Kòw! Ki moun ki la?\n"
            "Se mwen, vwazin! Adye kòmè,\n"
            "M ape mouri grangou!\n"
            "Ou pa ganyen moso manje, fèy, flè,\n"
            "Sa li ye, ban mwen?... Tan pri, chè!\n"
            "Lò mache samdi va vini,\n"
            "M a rann ou li.\n"
            "Fourni, se yon bon kamarad:\n"
            "Li pa pe janmen refize\n"
            "Bwè avèk ou, ri, banboche,\n"
            "Fè lapwomnad;\n"
            "Men, kanta pou lonje lan men,\n"
            "Se yon sistèm li pa renmen.\n"
            "San louvri pòt li, li di: Chè,\n"
            "Kòman w fè kont ou, non, pou\n"
            "Alè sa la, ou nan grangou?"
        ),
    },
}


def as_documents() -> dict[str, list[tuple[str, str]]]:
    """Convertit CORPUS au format attendu par
    document_stats.build_multi_document_report : {nom_fichier: [(label, texte)]}."""
    return {key: [("texte_complet", entry["texte"])] for key, entry in CORPUS.items()}


if __name__ == "__main__":
    # python3 corpus.py : évalue et affiche le gain scriptural de chaque
    # texte du corpus, individuellement, sans passer par pytest.
    from acc_converter import to_acc
    from document_stats import build_multi_document_report

    print(f"{'Texte':<24s} {'Auteur / source':<45s} {'1979':>6s} {'AAC':>6s}  {'Gain':>7s}")
    print("-" * 92)
    for key, entry in CORPUS.items():
        before = entry["texte"]
        after = to_acc(before)
        gain = (len(before) - len(after)) / len(before) * 100
        print(f"{key:<24s} {entry['auteur']:<45s} {len(before):>6d} {len(after):>6d}  {gain:>6.2f} %")

    multi = build_multi_document_report(as_documents())
    gains = [r.gain_percent_global for r in multi.per_document.values()]
    lo, hi = multi.pooled.ci95_gain_percent
    print("-" * 92)
    print(
        f"n={len(gains)}  min={min(gains):.2f} %  max={max(gains):.2f} %  "
        f"moyenne={multi.pooled.mean_gain_percent:.2f} %  "
        f"IC95 %=[{lo:.2f} % ; {hi:.2f} %]"
    )
