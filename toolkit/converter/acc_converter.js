/**
 * acc_converter.js
 * Port JavaScript de acc_converter.py — mêmes règles, même comportement.
 * Aucune dépendance externe. Utilisable côté navigateur ou en Node.js.
 */

const FORWARD_RULES = [
  ["Ch", "Š"], ["CH", "Š"], ["ch", "š"],
  ["Ou", "Ŏ"], ["OU", "Ŏ"], ["ou", "ŏ"],
  ["Ng", "Ŋ"], ["NG", "Ŋ"], ["ng", "ŋ"],
  ["Ui", "Wi"], ["UI", "WI"], ["ui", "wi"],
];

const BACKWARD_RULES = [
  ["Š", "Ch"], ["š", "ch"],
  ["Ŏ", "Ou"], ["ŏ", "ou"],
  ["Ŋ", "Ng"], ["ŋ", "ng"],
];

const WI_WORDS_NEVER_FROM_UI = new Set(["wi", "kiwi", "sandwi"]);

function toAcc(text) {
  let result = text;
  for (const [pattern, repl] of FORWARD_RULES) {
    result = result.split(pattern).join(repl);
  }
  return result;
}

function to1979(text, useLexicon = true) {
  let result = text;
  for (const [pattern, repl] of BACKWARD_RULES) {
    result = result.split(pattern).join(repl);
  }
  if (useLexicon) {
    result = result.replace(/[Ww]i/g, (match, offset, str) => {
      // Retrouve le "mot" autour de la correspondance pour vérifier le lexique
      const before = str.slice(0, offset).match(/[\p{L}]*$/u)[0];
      const after = str.slice(offset + match.length).match(/^[\p{L}]*/u)[0];
      const word = (before + match + after).toLowerCase();
      if (WI_WORDS_NEVER_FROM_UI.has(word)) return match; // protégé
      return match[0] === "W" ? "Ui" : "ui";
    });
  } else {
    result = result.replace(/Wi/g, "Ui").replace(/wi/g, "ui");
  }
  return result;
}

function diffSummary(text) {
  const count = (re) => (text.match(re) || []).length;
  return {
    ch: count(/[Cc][Hh]/g),
    ou: count(/[Oo][Uu]/g),
    ng: count(/[Nn][Gg]/g),
    ui: count(/[Uu][Ii]/g),
  };
}

function convertWithReport(text) {
  const converted = toAcc(text);
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
  module.exports = { toAcc, to1979, diffSummary, convertWithReport, WI_WORDS_NEVER_FROM_UI };
}
if (typeof window !== "undefined") {
  window.ACCConverter = { toAcc, to1979, diffSummary, convertWithReport };
}
