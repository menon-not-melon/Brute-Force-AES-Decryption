# Break a monoalphabetic substitution using frequency-based hill climbing.

from collections import Counter
import importlib.util
from pathlib import Path
import random
import string

HERE = Path(__file__).resolve().parent
RESOURCE_DIR = HERE.parent.parent / "Resources"
NGRAM_MODULE = RESOURCE_DIR / "ngram_score.py"
NGRAM_FILE = RESOURCE_DIR / "english_quadgrams.txt"
CIPHERTEXT_FILE = HERE / "Subst.txt"
KEY_FILE = HERE / "subst.key"
PLAINTEXT_FILE = HERE / "Subst.decoded.txt"

ALPHABET = string.ascii_uppercase
# Approximate letter frequencies in English, from most to least common. 
# (Referred from https://mathcenter.oxford.emory.edu/site/math125/englishLetterFreqs/)
ENGLISH_FREQUENCY_ORDER = "ETAOINSHRDLCUMWFGYPBVKJXQZ"

def load_scorer():
    #Load the provided n-gram scorer from the sibling Resources folder
    if not NGRAM_MODULE.exists() or not NGRAM_FILE.exists():
        raise FileNotFoundError(
            "Could not find ngram_score.py and english_quadgrams.txt in "
            f"{RESOURCE_DIR}. Keep the provided Resources folder beside Lab 01."
        )

    spec = importlib.util.spec_from_file_location("lab_ngram_score", NGRAM_MODULE)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module.ngram_score(str(NGRAM_FILE))

def init_key(cipher: str) -> list[str]:
    # Build a first decryption guess by matching letter-frequency rankings.
    # The returned list is a decryption map: its index is a ciphertext letter (A=0, B=1, ...) and its value is the guessed plaintext letter.

    counts = Counter(ch for ch in cipher.upper() if ch in ALPHABET)
    cipher_order = sorted(ALPHABET, key=lambda ch: counts[ch], reverse=True)
    decrypt_map = [""] * 26
    for cipher_letter, plain_letter in zip(cipher_order, ENGLISH_FREQUENCY_ORDER):
        decrypt_map[ord(cipher_letter) - ord("A")] = plain_letter
    return decrypt_map

def decrypt(cipher: str, decrypt_map: list[str]) -> str:
    # Apply the ciphertext-letter -> plaintext-letter lookup table
    table = str.maketrans(ALPHABET, "".join(decrypt_map))
    return cipher.upper().translate(table)

def score_text(text: str, scorer) -> float:
    # Score only letters; spaces and punctuation are not English quadgrams
    letters_only = "".join(ch for ch in text if ch in ALPHABET)
    return scorer.score(letters_only)

def randomize_map(decrypt_map: list[str], swaps: int, rng: random.Random) -> list[str]:
    # Make a nearby starting key by performing a number of random swaps
    result = decrypt_map.copy()
    for _ in range(swaps):
        a, b = rng.sample(range(26), 2)
        result[a], result[b] = result[b], result[a]
    return result
    
