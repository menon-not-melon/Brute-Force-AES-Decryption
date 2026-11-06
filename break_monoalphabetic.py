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
