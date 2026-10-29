# Brute-force the 16-bit AES key prefix used by Subst-Rijndael.crypt.

from collections import Counter
from math import log2
from pathlib import Path
import sys

from Crypto.Cipher import AES

HERE = Path(__file__).resolve().parent
INPUT_FILE = HERE / "Subst-Rijndael.crypt"
PLAINTEXT_FILE = HERE / "Subst.txt"
KEY_FILE = HERE / "aes.key"


def shannon_entropy(data: bytes) -> float:
    """Return byte entropy in bits per byte (0 to 8)."""
    counts = Counter(data)
    length = len(data)
    return -sum((count / length) * log2(count / length) for count in counts.values())

def main() -> None:
    ciphertext = INPUT_FILE.read_bytes()
    if len(ciphertext) < 32 or len(ciphertext) % AES.block_size:
        raise ValueError("Expected at least an IV and one AES block, with a multiple-of-16 file size")
    
    # The first ciphertext block is the IV; remaining bytes are CBC-encrypted data.
    iv = ciphertext[:AES.block_size]
    encrypted = ciphertext[AES.block_size:]

    best_entropy = float("inf")
    best_key = None
    best_plaintext = None
