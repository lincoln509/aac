/**
 * aac_converter.js
 * Port JavaScript de aac_converter.py — mêmes règles, même comportement.
 * Aucune dépendance externe. Utilisable côté navigateur ou en Node.js.
 *
 * IMPORTANT : ce fichier est la SEULE copie exécutable du convertisseur JS
 * (CORRECTIF, revue de code, C3). Il ne doit plus être recopié à la main
 * dans web-demo/*.html : ces pages l'incluent via scripts/sync_converter.py,
 * qui injecte ce fichier tel quel entre des marqueurs AAC-CONVERTER:BEGIN /
 * AAC-CONVERTER:END. Toute divergence entre une page web et ce fichier est
 * un bug — ne jamais modifier le code entre ces marqueurs à la main.
 */

// "ng" -> "ŋ" seulement si NON suivi d'une voyelle (limite de syllabe) :
// évalué AVANT les règles de FORWARD_RULES (voir aac_converter.py).
const NG_RULE = /(Ng|NG|ng|nG)(?![aeiouàèòAEIOUÀÈÒ])/g;
const NG_REPLACEMENTS = { "Ng": "Ŋ", "NG": "Ŋ", "ng": "ŋ", "nG": "ŋ" };

// CORRECTIF (revue de code, M5) : règles insensibles à la casse et
// préservant la casse trouvée (MAJUSCULES -> MAJUSCULES, Titre -> Titre,
// minuscules -> minuscules), au lieu des 3 casses figées d'origine
// (qui ne géraient pas "cH", "oU"...). Miroir exact de
// `_make_case_preserving_sub` dans aac_converter.py.
function caseAwareRepl(lowerRepl) {
  return (m) => {
    if (m === m.toUpperCase() && m !== m.toLowerCase()) return lowerRepl.toUpperCase();
    if (m[0] === m[0].toUpperCase() && m[0] !== m[0].toLowerCase()) {
      return lowerRepl[0].toUpperCase() + lowerRepl.slice(1);
    }
    return lowerRepl;
  };
}

const FORWARD_RULES = [
  [/ou/gi, caseAwareRepl("ŏ")],
  [/ch/gi, caseAwareRepl("š")],
  [/ui/gi, caseAwareRepl("wi")],
];

function toAac(text) {
  let result = text.replace(NG_RULE, (m) => NG_REPLACEMENTS[m]);
  for (const [rx, repl] of FORWARD_RULES) {
    result = result.replace(rx, repl);
  }
  return result;
}

// ---------------------------------------------------------------------
// CORRECTIF CRITIQUE (revue de code, C1) — voir aac_converter.py pour le
// détail : "wi" n'est plus jamais reconverti en "ui" par défaut, car
// aucune preuve de corpus ne le justifie et cela corrompait des mots
// courants de 1979 (swiv, lwil, kwit, nwit, pwi, fwi...).
// ---------------------------------------------------------------------
const WI_WORDS_FROM_UI = new Set([]); // liste blanche, vide tant que non confirmée
// Conservé pour compatibilité ascendante uniquement (plus utilisé ci-dessous).
const WI_WORDS_NEVER_FROM_UI = new Set(["wi", "kiwi", "sandwich", "sandwitch"]);

// CORRECTIF (revue de code, suite de M5) — décision de casse au niveau du
// mot entier plutôt que du caractère isolé (miroir de `_decode_word` /
// `_word_case_mode` dans aac_converter.py). Un caractère spécial isolé
// (Š/Ŏ/Ŋ) est toujours "majuscule" au sens de la casse Unicode : on ne
// peut pas savoir, à partir de lui seul, s'il vient d'un digramme "Ch"
// (Titre) ou "CH" (MAJUSCULES) sans regarder le reste du mot.
const BACKWARD_MAP_LOWER = { "š": "ch", "ŏ": "ou", "ŋ": "ng" };

function isAlpha(ch) {
  return /\p{L}/u.test(ch);
}

function wordCaseMode(word) {
  const cased = [...word].filter(isAlpha);
  if (cased.length === 0) return "lower";
  const isUp = (c) => c === c.toUpperCase() && c !== c.toLowerCase();
  const isLo = (c) => c === c.toLowerCase() && c !== c.toUpperCase();
  if (cased.every(isUp)) return "upper";
  if (cased.every(isLo)) return "lower";
  if (isUp(cased[0]) && cased.slice(1).every(isLo)) return "title";
  return "mixed";
}

function decodeWord(word) {
  const mode = wordCaseMode(word);
  const chars = [...word];
  return chars
    .map((ch, i) => {
      const lower = ch.toLowerCase();
      const digraph = BACKWARD_MAP_LOWER[lower];
      if (digraph === undefined) return ch;
      if (mode === "upper") return digraph.toUpperCase();
      if (mode === "title") return i === 0 ? digraph[0].toUpperCase() + digraph.slice(1) : digraph;
      if (mode === "lower") return digraph;
      // "mixed" (rare) : repli sur la casse du caractère lui-même
      return ch === ch.toUpperCase() && ch !== ch.toLowerCase() ? digraph.toUpperCase() : digraph;
    })
    .join("");
}

function decodeBackwardDigraphs(text) {
  return text.replace(/[\p{L}]+/gu, (word) => decodeWord(word));
}

/**
 * convertWi contrôle le traitement de "wi" (voir la note dans
 * aac_converter.py) :
 *   - "none"    (défaut) : "wi" n'est jamais reconverti en "ui".
 *   - "lexicon" : seuls les mots de WI_WORDS_FROM_UI sont reconvertis.
 *   - "always"  : ancien comportement mécanique, incorrect sur du texte
 *                 réel, gardé pour compatibilité et les tests.
 * `useLexicon` (ancien paramètre booléen) reste accepté pour compatibilité
 * ascendante : true -> "lexicon", false -> "always".
 */
function to1979(text, convertWi = "none") {
  if (convertWi === true) convertWi = "lexicon";
  if (convertWi === false) convertWi = "always";

  let result = decodeBackwardDigraphs(text);

  if (convertWi === "none") return result;

  if (convertWi === "always") {
    return result.replace(/Wi/g, "Ui").replace(/wi/g, "ui");
  }

  // "lexicon" : liste blanche uniquement.
  return result.replace(/[\p{L}]+/gu, (word) => {
    const bare = word.toLowerCase();
    if (!WI_WORDS_FROM_UI.has(bare)) return word;
    return word.replace(/[Ww]i/g, (m) => (m[0] === "W" ? "Ui" : "ui"));
  });
}

function diffSummary(text) {
  const count = (re) => (text.match(re) || []).length;
  return {
    ch: count(/[Cc][Hh]/g),
    ou: count(/[Oo][Uu]/g),
    ng: (text.match(NG_RULE) || []).length,
    ui: count(/[Uu][Ii]/g),
  };
}

function convertWithReport(text) {
  const converted = toAac(text);
  const noSpace = (s) => s.replace(/ /g, "");
  const before = text.length;
  const after = converted.length;
  const beforeNS = noSpace(text).length;
  const afterNS = noSpace(converted).length;
  return {
    original: text,
    converted,
    charsTotalBefore: before,
    charsTotalAfter: after,
    charsNoSpaceBefore: beforeNS,
    charsNoSpaceAfter: afterNS,
    gainPercentTotal: before === 0 ? 0 : ((before - after) / before) * 100,
    gainPercentNoSpace: beforeNS === 0 ? 0 : ((beforeNS - afterNS) / beforeNS) * 100,
  };
}

// Export pour Node.js / bundlers, tout en restant utilisable directement
// via <script> dans le navigateur (attache à window si présent).
if (typeof module !== "undefined" && module.exports) {
  module.exports = { toAac, to1979, diffSummary, convertWithReport, WI_WORDS_FROM_UI, WI_WORDS_NEVER_FROM_UI };
}
if (typeof window !== "undefined") {
  window.AACConverter = { toAac, to1979, diffSummary, convertWithReport };
}
