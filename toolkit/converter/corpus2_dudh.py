# -*- coding: utf-8 -*-
"""
analyse_dudh.py
================
Applique la conversion AAC (aac_converter.to_aac) et toutes les formules
de letter_analysis.py + document_stats.py + extensions (Clopper-Pearson,
chi², entropie, leave-one-out) au corpus de la DUDH (Artik 1 à 30).
"""

import re, math, random
from collections import Counter, defaultdict
import numpy as np
from scipy import stats

# CORRECTIF (revue de code) : ce module définissait sa propre fonction
# to_aac() locale, avec les 3 casses figées ("Ou"/"OU"/"ou"...) que
# aac_converter.py documente comme buguées (ne gèrent pas la casse mixte,
# ex. "oU" n'est converti par aucune des 3 règles figées). On réutilise
# maintenant l'implémentation unique et testée de aac_converter.py plutôt
# que de la dupliquer -- voir la note équivalente dans alphabet_complet.py
# et analyse_complete.py, qui font déjà `from aac_converter import to_aac`.
import sys, pathlib
sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from aac_converter import to_aac


# ------------------------------------------------------------------
# 0. Chargement du texte (collez ici le contenu du fichier ArtikAtik 1.txt)
# ------------------------------------------------------------------
TEXTE_1979 = """ArtikAtik 1
Tout moun fèt lib, egal ego pou diyite kou wè dwa. Nou gen la rezon ak la konsyans epi nou fèt pou nou aji youn ak lot ak yon lespri fwatènite.

ArtikAtik 2
Chak moun kapab itilize dwa ak tout libète pki pwoklame nan Deklarasyon sa-a, san yo pa fè okenn diferans ant you moun ak you lot, kelt ki lan swa ras li, koulè li, sex li, lang li pale-a, relijyon li, opinyon politik o swa nen pot ki lot opinyon li ka genyen, kit li soti nan orijin nasyonal o gen reapò ak la sosyete, lajan, kotel sòoti o swa nenpot ki lot sitiasyon.

Epi, yo pap fè oken diferans kel ke swa lL wa sou politik, jistis o swa Lwa entèénasyonal peyi ou byen tenritwa kote moun nan sòti, ke pèéyi o swa tenritwa sa-a li endepandan, ou byen sou lobedians yon lot, kel pa sa anji pou kol o enkeò kel gen kek règleman ki limite libète peyi-a.

ArtikAtik 3
Chak moun gen dwa as ke li gen la vi, la libeète ak sekirite pou tèt-li.

ArtikAtik 4
Yo pa gen dwa kimbe pèson nan esklavaj ni fòsel ekzekite yon travay; esklavaj avek komès esklav entèdi kèl ke swa jan yap fèl la.

ArtikAtik 5
Yo pa gen dwa maspinen you moun, ni fèl sibi mòve tretman, ni tretel kou bèt osnon fèl pèdi lonèl.

ArtikAtik 6
Chak moun gen dwa as ke yo rekònet toupatou pèsonalite jiridik-li.

ArtikAtik 7
Tou moun egal devan la lwa epi tout moun gen dwa, san pati pri, gen menm pwoteksyon ke la lwa bay. Tout moun gen dwa gen pwoteksyon-an kont tout pati pri ki ta kab anviole Deklarasyon sa-a epi tout kont tout pwovokasyon pou yo fè pati pri.

ArtikAtik 8
Chak moun gen dwa poul resevwa konkou tout bon pa devan tribinal nasyonal reskonsab yo, kont zak kap anviole dwa fondalnatal ke konstitisyon o swa la lwa rekònet kel genyen.

ArtikAtik 9
Yo pa gen dwa ak fos gro ponyet, arete, mete nan prizon o swa ekzile yon moun.

ArtikAtik 10
Chak moun gen dwa, egal ego, as ke yo koute koz li kou koz nenpòt ki lot moun, devan yon piblik, devan yon tribinal ki pa depann de pèson anpi ki baye bon pwa ak bon mezi, ki kab deside sou dwa ak devwa moun nan, o swa si akizasyon yo pote kontli la lwa konsiderel kom jis.

ArtikAtik 11
Nenpòt ki moun yo ta akize de move zak sou yon lot, sipose inosan jiskaske la lwa rekonèt kè li koupab, nan yon prose piblik, kote yo dwe bali tout garanti nesesè pou li defann tèt li.
Yo pap ka kondane pèson pou aksyon o swa manklman ke, le moman yo tap komèt yo, yo pat konsidere yo kom yon move zak, dapre dwa nasyonal oubyen ientènasyonal. Menme jan, yo pap ka mete diplius sou kondanasyon you moun ke sa la lwa te rekonèt la le moman move zak-la te komèt.

ArtikAtik 12
Yo pap ka ak la fos entre nan afè ki regade vi prive yon moun, fanmi-li, kay-li o swa lèt kel ekri o swa kel resevwa, ni sal lonè li ak repitasyon li. Tout moun gen dwa gen pwoteksyon la lwa kont zak sa yo.

ArtikAtik 13
Tout moun gen dwa sikile libreman epi tou chwazsi kote li pral rezide-a nan peyi-a.
Tout moun gen dwa kite nenpot ki peyi, menm pal tou, epi retounen nan peyi l.

ArtikAtik 14
Lò gen pèsekisyon, tout moun gen dwa chèche lazil epi benéefisie lazil nan lot peyi.
Dwa sa-a li pa ka aplike lè se pouswiv yap pouswiv yon moun pou krim dwa komen o swa
pou ajisman ki kontrè ak entanNasyon epi princip Nasyon Zini.

ArtikAtik 15
Tout moun dwe genyen yon nasyonalite.
Yo pa sa wete nasyonalite yon moun ak la fos, ni yo pa sa anpechel chanje nasyonalite.

ArtikAtik 16
DDepi yo gen laj la, yon gason ak yon fanm, kel ke swa ras yo, nasyonalite yo o swa relijyon,
gen dwa marie o swa fonde yon fanmi. Yo gen dwa egal ego devan mariaj, pandan mariaj epi lè yap divòse.
Mariaj pa sa fèt si se pa ak lib konsantman moun ki pral marie yo.
La fanmi se eleman natirel ki pi enpòtan la sosyete epi li gen dwa genyen pwoteksyon la sosyete ak leta.

ArtikAtik 17
Tout moun, kit li poukòl kit li ak moun, gen dwa posede yon byen.
Yo pa gen dwa wete byen yon moun nan men li ak la fos.

ArtikAtik 18
Tout moun gen dwa poul gen libète panse, libète konsians li ak relijyon li; dwa sa-a konpran
tou libète pou li chanje de relijyion obyen fason li pnanse, libète manifeste relijyion li o
swa fason li pnanse, poukòl osnon ak lot moun, kit li devan yon piblick kit li nan prive, pa
mwayen lanseyman, pwatik, sèvis-la ak seremoni-yo.

ArtikAtik 19
Tout moun gen dwa a libète lide yo ak lapawol yo, kidonk dwa pou yo pa enkiete yo a koz lide yo
ak dwa tou pou yo chèche, resevwa epi tou piblye, san konsiderasyon fwontiè, enfòmasyon ak lide
pa nenpot ki mwayen ki ekziste pou yo piblye yo.

ArtikAtik 20
Tout moun gen dwa gen libète fè reinyon ak asosyasyon san zam.
Yo pa ka oblije pèson manm yon asosyasyon.

ArtikAtik 21
Tout moun gen dwa patisipe nan direksyon zafè piblik peyil, swa direkteman,
swa pa lentèmediè repréesantan kel chwazi an tout libète.
Tout moun gen dwa okipe, nan kondisyon egalite, pos piblik peyi li.
Volonté yon peup se baz otorite pouvwa piblik; volonte sa-a dwe manifeste li nan
eleksyon onèt ki dwe fèt nan entèval fiks, ak patisipasyon tout sitwayen, ak
vot sekrè osnon ak yon metofd ki ta menm jan ak sa-a depi li asire libète vot-la.

ArtikAtik 22
Tout moun, kom manm la sosyete, gen dwa gen sikirite sosyal; sekirite sa-a, yo kreyel
pou moun jwen satisfaksyon dwa ekonomik, sosyal ak kiltirel ki endispansab pou diyite
ak devlopman lib pèsonalitel, gras a jeèfò nasyonal ak kooperasyon entènasyonal,
depandan de oganizasyon ak resous chak peyi.

ArtikAtik 23
Tout moun gen dwa revandike dwa travay, gen dwa chwazi libreman travay li, nan de kondisyon ki bon, ki jis, ak pwoteksyon kont chomaj.
Tout moun gen dwa, san pati pri, aske yo peyel yon salè egal pou yon travay egal ak sa yon lòt fè.
Tout moun kap travay, yo dwe bali yon salè jis epi ki satisfezan, ki kapab asirel, ansanm ak fanmi li,
yon ekzistans ki an akò avek diyite moun epi complétéetou, si gen posibilite, pou yo ta konpletel
ak tout lòt mwayen pwoteksyon sosyal.
Tout moun gen dwa fonde sendika ak lòt moun osnon entre nan sendika pou defann enterè yo.

ArtikAtik 24
Tout moun gen dwa gen repo ak amizman, ak yon limit rezonab pou dire travay-la epi, tout moun gen dwa tou a konje peye periodik.

ArtikAtik 25
Tout moun gen dwa pou yon nivo lavi ki kapab garanti lasante ak byenèt yo ansam ak pa fanmi yo,
epi tou garanti manje, abiye, kay, swen lasante avek sèvis sosyal nesesè yo; tout moun gen
dwa pou yo genyen sikirite nan ka chomaj, maladi, paralesi, epi tou si mari o swa madanm mouri,
nan ka vieyes o swa nan tout lòt ka kote yon moun ta pèdi mwayen poul viv, nan de sikonstans ke se pat volonte'l ki te vle li.
Matènité ak ti moun piti gen gen dwa a yon èd ak yon asistans espesyal. Tout ti moun, kit
yo fèt nan mariaj, kit se andeyò mariaj, gen menm pwoteksyon sosyal la.

ArtikAtik 26
Tout moun gen dwa a levasyon. Levasyon dwe gratuis, di mwens lò se anseyman elemanitè epi fondalnatal.
Anseyman elementè obligatwa. Anseyman teknik ak pwofesyonel dwe jeneralize; antre nan etid siperiè
dwe ouvè pou tout moun egal ego depandan de valè yon moun.
Vizion levasyon dwe pou fè fleri pèsonalite moun ak ranfose respè dwa de lom ak libète fondalnatal.
Li dwe tou ankouraje konesans, tolerans ak lamitye ant tout nasyon, tout gwoup ras moun o swa tout relijyon,
epi tou ankouraje devlopman aktivite Nasyon Zini pou mentni la pè.
Paran yo, en premie, gen dwa pou yo chwazi ki kalite levasyon pou yo bay pitit yo.

ArtikAtik 27
Tout moun gen dwa patisipe libreman nan aktivite sou la vi kiltirel kominote-a, jwi la vi atistik-la
epi paticipe nan pwogrè la sians ak avantaj ki soti nan pwogrè sa-a. epi aux bienfaits qui en résultent.
Tout moun gen dwa genyen pwoteksyon enterè lespri ak enterè tout bon vre ki sòti nan tout pwodiksyon
la sians, literati epi tou atistik ke moun sa-a ta pwodwi.

ArtikAtik 28
Tout moun gen dwa aske ekziste, sou plan sosyal ak sou plan entènasyonal, yon lòd kote dwa ak libète ki
pwoklame nan Deklarasyon sa a kapab aplike tout bon vre.

ArtikAtik 29
Chak moun gen devwa padevan kominote-a, kote se sèl kote devlopman lib tout bon pèsonalite li kapab realize.
Nan itilizasyon dwa li yo epi nan la jwisans libète li yo, yon moun dwe soumèt li devan limitasyon ke la
lwa sèlman tabli, pou asire rekonesans ak respe dwa ak libète lot moun epi tou pou satisfiè bon jan ekzistans
règleman la sosyete, lòd piblik ak byenèt jeneral nan yon sosyete demokratik.
Dwa ak libète sa yo, yo pap kapab, nan okenn ka, itilize yo lòt jan ke selon vizion ak pwencip Nasyon Zini.

ArtikAtik 30
Okenn nan disposisyon Deklarasyon sa-a pap ka entèpwete kom kwa yon leta, yon gwoupman o swa yon moun,
ta ka gen yon dwa kelkonk poul ta tanmen yon aktivite obyen komèt yon zak ki ta vle abouti a destriksyon
dwa ak libète ki pwoklame na Deklarasyon-an."""

# ------------------------------------------------------------------
# 1. Conversion AAC — réutilise aac_converter.to_aac (voir CORRECTIF ci-dessus)
# ------------------------------------------------------------------
AAC = to_aac(TEXTE_1979)
N = len(AAC)
print(f"N (caractères AAC) = {N}")

# ------------------------------------------------------------------
# 2. Fréquences des lettres atomiques (letter_analysis.atomic_letter_frequencies)
# ------------------------------------------------------------------
ATOMIC = ("š", "ŏ", "ŋ")
lower = AAC.lower()
counts = {l: lower.count(l) for l in ATOMIC}
total_atom = sum(counts.values())
D = total_atom / N
f = {l: counts[l] / N for l in ATOMIC}
p = {l: counts[l] / total_atom for l in ATOMIC}

print("\n=== FRÉQUENCES ===")
for l in ATOMIC:
    print(f"{l}: n={counts[l]:3d}  f={f[l]*100:.3f} %  p={p[l]*100:.2f} %")
print(f"Densité D = {D*100:.3f} %")

# IC Clopper-Pearson
print("\nIC95 % Clopper-Pearson :")
for l in ATOMIC:
    n_l = counts[l]
    lo = stats.beta.ppf(0.025, n_l, N - n_l + 1)
    hi = stats.beta.ppf(0.975, n_l + 1, N - n_l)
    print(f"  {l}: [{lo*100:.3f} % ; {hi*100:.3f} %]")

# chi² uniformité
bar_n = total_atom / 3
chi2 = sum((counts[l] - bar_n)**2 / bar_n for l in ATOMIC)
p_chi2 = 1 - stats.chi2.cdf(chi2, df=2)
print(f"\nchi² uniformité = {chi2:.3f}  (ddl=2, p={p_chi2:.2e})")

# entropie
H = -sum(p[l] * math.log(p[l], 3) for l in ATOMIC)
print(f"Entropie H(A) = {H:.4f}")

# ------------------------------------------------------------------
# 3. Analyse au niveau du mot (letter_analysis.word_level_analysis)
# ------------------------------------------------------------------
WORD_RE = re.compile(r"[^\W\d_]+", re.UNICODE)
mots = WORD_RE.findall(AAC)
M = len(mots)
a_w = [sum(1 for c in w.lower() if c in ATOMIC) for w in mots]
W_plus = [w for w, a in zip(mots, a_w) if a >= 1]
C = len(W_plus) / M if M else 0
mu_all = sum(a_w) / M if M else 0
mu_pos = sum(a for a in a_w if a >= 1) / len(W_plus) if W_plus else 0
C_l = {l: sum(1 for w in mots if l in w.lower()) / M if M else 0 for l in ATOMIC}

print("\n=== MOTS ===")
print(f"M = {M}  |W+| = {len(W_plus)}  C = {C*100:.2f} %")
print(f"mu_all = {mu_all:.4f}  mu_pos = {mu_pos:.4f}")
print(f"Identité mu_all = C * mu_pos : {abs(mu_all - C*mu_pos) < 1e-9}")
for l in ATOMIC:
    print(f"  C_{l} = {C_l[l]*100:.2f} %")

# ------------------------------------------------------------------
# 4. Analyse syllabique (letter_analysis.syllable_functional_analysis)
# ------------------------------------------------------------------
# CORRECTIF : alignée sur VOWELS de letter_analysis.py (ajout de 'à',
# manquant ici -- voir le bug équivalent corrigé dans alphabet_complet.py).
VOWELS = set("aeiòèouŏà")
def syllabify(word):
    w = [c.lower() for c in word]
    voy = [i for i, c in enumerate(w) if c in VOWELS]
    if not voy:
        return [{"onset": w, "nucleus": [], "coda": []}]
    sylls = [{"onset": w[:voy[0]], "nucleus": [w[voy[0]]], "coda": []}]
    for k in range(1, len(voy)):
        between = w[voy[k-1]+1:voy[k]]
        if len(between) <= 1:
            onset = between
        elif len(between) == 2:
            sylls[-1]["coda"].append(between[0]); onset = [between[1]]
        else:
            sylls[-1]["coda"].extend(between[:-1]); onset = [between[-1]]
        sylls.append({"onset": onset, "nucleus": [w[voy[k]]], "coda": []})
    sylls[-1]["coda"].extend(w[voy[-1]+1:])
    return sylls

occ = defaultdict(Counter)
for w in mots:
    for syll in syllabify(w):
        for pos in ("onset", "nucleus", "coda"):
            for c in syll[pos]:
                if c in ATOMIC:
                    occ[c][pos] += 1

print("\n=== POSITIONS SYLLABIQUES ===")
for l in ATOMIC:
    tot = sum(occ[l].values())
    if tot:
        print(f"{l}: total {tot} — onset {occ[l]['onset']/tot*100:.1f} % / "
              f"nucleus {occ[l]['nucleus']/tot*100:.1f} % / "
              f"coda {occ[l]['coda']/tot*100:.1f} %")

# ------------------------------------------------------------------
# 5. Leave-one-out sur le test t (si vous avez plusieurs textes)
# ------------------------------------------------------------------
# Ici, un seul texte : on peut faire un leave-one-out sur les paragraphes
# (chaque paragraphe = un segment). Le script découpe le texte en paragraphes
# et applique le test t apparié.
paragraphes = [p.strip() for p in TEXTE_1979.split("\n") if p.strip()]
# On regroupe les lignes en paragraphes logiques (séparés par des lignes vides)
# Pour simplifier, on considère chaque ligne non vide comme un segment.
segments = []
current = []
for line in TEXTE_1979.split("\n"):
    if line.strip() == "":
        if current:
            segments.append(" ".join(current))
            current = []
    else:
        current.append(line.strip())
if current:
    segments.append(" ".join(current))

before = [len(s) for s in segments]
after = [len(to_aac(s)) for s in segments]
diffs = [b - a for b, a in zip(before, after)]
n_seg = len(segments)

print(f"\n=== TEST T APPARIÉ ({n_seg} segments) ===")
if n_seg >= 2:
    t_stat, p_val = stats.ttest_rel(before, after)
    print(f"t = {t_stat:.3f}, p = {p_val:.4f}")
    # Leave-one-out
    print("Leave-one-out :")
    for i in range(n_seg):
        mask = np.arange(n_seg) != i
        t_loo, p_loo = stats.ttest_rel(np.array(before)[mask],
                                       np.array(after)[mask])
        flag = "sig" if p_loo < 0.05 else "NON SIG"
        print(f"  sans seg {i+1}: t={t_loo:.3f}, p={p_loo:.4f} [{flag}]")