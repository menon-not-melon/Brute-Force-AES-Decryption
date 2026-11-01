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

    # The first two key bytes range from 0000 through ffff; the remaining bytes are zero.
    for prefix in range(1 << 16):
        key = prefix.to_bytes(2, "big") + bytes(14)
        plaintext = AES.new(key, AES.MODE_CBC, iv).decrypt(encrypted)
        entropy = shannon_entropy(plaintext)

        # Wrong keys yield nearly random bytes (entropy near 8); substitution text
        # has a concentrated character distribution and therefore lower entropy.
        if entropy < best_entropy:
            best_entropy = entropy
            best_key = key
            best_plaintext = plaintext

    assert best_key is not None and best_plaintext is not None

    # Remove standard PKCS#7 padding when present; otherwise preserve all bytes.
    pad_length = best_plaintext[-1]
    if 1 <= pad_length <= AES.block_size and best_plaintext.endswith(bytes([pad_length]) * pad_length):
        best_plaintext = best_plaintext[:-pad_length]

    PLAINTEXT_FILE.write_bytes(best_plaintext)
    KEY_FILE.write_text(best_key.hex() + "\n", encoding="ascii")

    print(f"Best key:       {best_key.hex()}")
    print(f"Byte entropy:   {best_entropy:.4f} bits/byte")
    print(f"Plaintext file: {PLAINTEXT_FILE}")
    print(f"Key file:       {KEY_FILE}")

if __name__ == "__main__":
    main()
