"""
fertilite_tokenizers.py
========================

Compare la fertilité tokenistique (#tokens / #mots, cf. formule 2.3 de
aac_complexity_analysis_.md) entre l'orthographe 1979 et l'AAC, avec TROIS
tokeniseurs de familles différentes :

    - cl100k_base   (tiktoken, BPE byte-level, GPT-3.5 / GPT-4)
    - o200k_base    (tiktoken, BPE byte-level, GPT-4o / GPT-5)
    - NLLB-200      (Hugging Face, SentencePiece/unigramme,
                      facebook/nllb-200-distilled-600M — entraîné sur 200
                      langues DONT le créole haïtien, hat_Latn)

L'intérêt de NLLB n'est pas seulement "une 3e bibliothèque" : c'est le
seul des trois dont le corpus d'entraînement a pu contenir du vrai texte
créole 1979, ce qui permet de distinguer "l'AAC tokenise mal parce que
c'est un alphabet inconnu de tout le monde" de "l'AAC tokenise mal
seulement chez les tokeniseurs anglo-centrés".

Installation :
    pip install tiktoken transformers sentencepiece

Usage :
    # un seul texte
    python3 fertilite_tokenizers.py "Chante pou chase lapli nan kò mwen."

    # texte par défaut (identique à l'ancien fertilite_tiktoken.py)
    python3 fertilite_tokenizers.py

    # les 8 textes du corpus de validation (texte par texte + agrégat)
    python3 fertilite_tokenizers.py --corpus

    # Utile si transformers/NLLB n'est pas installé car celui-ci prend 2Go
    # en installation suivit d'un systeme de cache
    python3 fertilite_tokenizers.py --corpus --tokenizers cl100k_base o200k_base

Nécessite aac_converter.py (version toolkit, to_aac) et, pour --corpus,
corpus.py (CORPUS) dans le même dossier ou sur le PYTHONPATH.
"""

from __future__ import annotations
import argparse
import statistics as stats
import sys

from aac_converter import to_aac  # remplacer par `to_acc` si vous gardez l'ancien nommage


# ---------------------------------------------------------------------------
# Chargement paresseux de chaque tokeniseur : on ne paie le coût (et le
# téléchargement) que pour ceux réellement utilisés, et un tokeniseur
# indisponible n'empêche pas les deux autres de tourner.
# ---------------------------------------------------------------------------

def _load_tiktoken(encoding_name: str):
    import tiktoken
    enc = tiktoken.get_encoding(encoding_name)
    return lambda text: enc.encode(text), lambda ids: [enc.decode([t]) for t in ids]


def _load_nllb():
    from transformers import AutoTokenizer
    tok = AutoTokenizer.from_pretrained(
        "facebook/nllb-200-distilled-600M", src_lang="hat_Latn"
    )
    # NLLB ajoute toujours un token de langue + un token de fin de séquence ;
    # on les retire pour ne compter que les tokens du texte lui-même.
    def encode(text: str):
        ids = tok.encode(text, add_special_tokens=True)
        return [i for i in ids if i not in tok.all_special_ids]
    def decode_each(ids):
        return [tok.decode([i]) for i in ids]
    return encode, decode_each


TOKENIZERS = {
    "cl100k_base": lambda: _load_tiktoken("cl100k_base"),
    "o200k_base": lambda: _load_tiktoken("o200k_base"),
    "nllb-200": _load_nllb,
}


# ---------------------------------------------------------------------------
# Mesure sur un texte
# ---------------------------------------------------------------------------

def measure(text_1979: str, encode) -> dict:
    text_aac = to_aac(text_1979)
    n_mots = len(text_1979.split())  # identique pour les deux versions
    tok_1979 = encode(text_1979)
    tok_aac = encode(text_aac)
    return {
        "n_mots": n_mots,
        "tokens_1979": len(tok_1979),
        "tokens_aac": len(tok_aac),
        "fert_1979": len(tok_1979) / n_mots,
        "fert_aac": len(tok_aac) / n_mots,
        "tok_aac_ids": tok_aac,
    }


def print_single_text_report(text_1979: str, tokenizer_names: list[str]) -> None:
    text_aac = to_aac(text_1979)
    print("1979 :", text_1979)
    print("AAC  :", text_aac)
    print()
    header = f"{'tokeniseur':14s} {'Fert 1979':>10s} {'Fert AAC':>10s} {'Δ':>8s}"
    print(header)
    print("-" * len(header))
    for name in tokenizer_names:
        try:
            encode, decode_each = TOKENIZERS[name]()
        except Exception as e:  # modèle non installé / pas de réseau / etc.
            print(f"{name:14s}  (indisponible : {e})")
            continue
        m = measure(text_1979, encode)
        delta = (m["fert_aac"] - m["fert_1979"]) / m["fert_1979"] * 100
        print(f"{name:14s} {m['fert_1979']:10.3f} {m['fert_aac']:10.3f} {delta:+7.1f}%")
    print()
    # Détail des tokens AAC avec le premier tokeniseur dispo, pour inspection
    for name in tokenizer_names:
        try:
            encode, decode_each = TOKENIZERS[name]()
        except Exception:
            continue
        ids = encode(text_aac)
        print(f"--- Détail des tokens AAC ({name}) ---")
        print([decode_each([i])[0] for i in ids])
        break


def print_corpus_report(tokenizer_names: list[str]) -> None:
    from corpus import CORPUS

    texts = {k: v["texte"] for k, v in CORPUS.items()}

    for name in tokenizer_names:
        try:
            encode, _ = TOKENIZERS[name]()
        except Exception as e:
            print(f"=== {name} : indisponible ({e}) ===\n")
            continue

        print(f"=== {name} — 8 textes du corpus de validation ===")
        header = f"{'texte':24s} {'mots':>6s} {'Fert 1979':>10s} {'Fert AAC':>10s} {'Δ':>8s}"
        print(header)
        print("-" * len(header))

        fert_1979_list, fert_aac_list = [], []
        for key, texte in texts.items():
            m = measure(texte, encode)
            delta = (m["fert_aac"] - m["fert_1979"]) / m["fert_1979"] * 100
            print(f"{key:24s} {m['n_mots']:6d} {m['fert_1979']:10.3f} {m['fert_aac']:10.3f} {delta:+7.1f}%")
            fert_1979_list.append(m["fert_1979"])
            fert_aac_list.append(m["fert_aac"])

        print("-" * len(header))
        mean_1979, mean_aac = stats.mean(fert_1979_list), stats.mean(fert_aac_list)
        sd_1979 = stats.stdev(fert_1979_list) if len(fert_1979_list) > 1 else 0.0
        sd_aac = stats.stdev(fert_aac_list) if len(fert_aac_list) > 1 else 0.0
        print(
            f"{'MOYENNE (n=8)':24s} {'':6s} {mean_1979:10.3f} {mean_aac:10.3f} "
            f"{(mean_aac - mean_1979) / mean_1979 * 100:+7.1f}%"
        )
        print(f"{'écart-type':24s} {'':6s} {sd_1979:10.3f} {sd_aac:10.3f}")
        print()


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("texte", nargs="?", default=None, help="Texte unique à tester")
    parser.add_argument(
        "--corpus", action="store_true",
        help="Tester les 8 textes de corpus.py au lieu d'un texte unique",
    )
    parser.add_argument(
        "--tokenizers", nargs="+", default=list(TOKENIZERS.keys()),
        choices=list(TOKENIZERS.keys()),
        help="Sous-ensemble de tokeniseurs à utiliser (par défaut : les trois)",
    )
    args = parser.parse_args()

    if args.corpus:
        print_corpus_report(args.tokenizers)
    else:
        texte = args.texte or (
            "Chante pou chase lapli nan kò mwen. Grangou ap fè nou mache lwen, "
            "men lengis la rete la. Bekàn Jàn pwofàn, dodàn kay la, ak yon "
            "sandwich pou granmoun ki vle wè bouch li louvri."
        )
        print_single_text_report(texte, args.tokenizers)
