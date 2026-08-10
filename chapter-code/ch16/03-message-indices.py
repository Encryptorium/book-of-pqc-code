# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 16: FORS and the stateless hypertree
# Section: "FORS at teaching parameters"
# https://book.encryptorium.com/part-3-hash-based/ch16-fors-and-stateless-hypertree/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch16/03-message-indices.py

import hashlib

def message_indices(message, k, t):
    """Extract k indices from SHA-256(message), each in {0, ..., t-1}."""
    lg_t = t.bit_length() - 1            # t is a power of two; no float log
    digest = hashlib.sha256(message).digest()
    indices = []
    bit_offset = 0
    for _ in range(k):
        value = 0
        for b in range(lg_t):
            cur = bit_offset + b
            by = cur // 8
            bi = 7 - (cur % 8)
            value = (value << 1) | ((digest[by] >> bi) & 1)
        indices.append(value)
        bit_offset += lg_t
    return indices

indices = message_indices(b"FORS example", 6, 16)
print(indices)
# ==> [10, 9, 6, 9, 13, 4]
print(f"Bits used: {6 * 4} of 256")
# ==> Bits used: 24 of 256
