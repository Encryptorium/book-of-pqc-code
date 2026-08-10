# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 15: Many-time signatures
# Section: "Base-w encoding"
# https://book.encryptorium.com/part-3-hash-based/ch15-many-time-signatures/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch15/03-base-w.py

import hashlib, math

def base_w(data, w, out_len):
    """Encode *data* as *out_len* base-*w* digits (MSB-first per byte)."""
    lg_w = int(math.log2(w))
    digits = []
    for byte in data:
        for shift in range(8 - lg_w, -1, -lg_w):
            digits.append((byte >> shift) & (w - 1))
            if len(digits) == out_len:
                return digits
    return digits[:out_len]

digest = hashlib.sha256(b"XMSS test message").digest()
msg_digits = base_w(digest, 16, 64)
print(msg_digits[:8])
# ==> [12, 1, 11, 7, 15, 0, 13, 3]
print(len(msg_digits))
# ==> 64
