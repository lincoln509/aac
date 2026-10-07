/* GÉNÉRÉ par scripts/build.py depuis converter/rules.json.
   NE PAS ÉDITER À LA MAIN : modifiez la source, puis relancez
   `python3 scripts/build.py` (le hook pre-commit le fait pour vous). */
window.AAC_RULES = {
  "ng": {
    "pattern": "(Ng|NG|ng|nG)(?![aeiouàèòAEIOUÀÈÒ])",
    "to": {
      "Ng": "Ŋ",
      "NG": "Ŋ",
      "ng": "ŋ",
      "nG": "ŋ"
    }
  },
  "forward": [
    {
      "name": "ou",
      "from": "ou",
      "to": "ŏ"
    },
    {
      "name": "ch",
      "from": "ch",
      "to": "š"
    },
    {
      "name": "ui",
      "from": "ui",
      "to": "wi"
    }
  ],
  "backward": {
    "š": "ch",
    "ŏ": "ou",
    "ŋ": "ng"
  },
  "wi_from_ui": [
    "uit",
    "uitèn",
    "dizuit",
    "vennsuit",
    "tousuit",
    "zuit"
  ],
  "atomic_letters": [
    "š",
    "ŏ",
    "ŋ"
  ],
  "vowels": "aeiòèouŏà"
};
