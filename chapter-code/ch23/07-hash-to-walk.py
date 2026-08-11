# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 23: SQIsign in a toy setting
# Section: "Toy SQIsign: sign"
# https://book.encryptorium.com/part-4-code-isogeny/ch23-sqisign-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch23/07-hash-to-walk.py

# Pedagogical sketch of the signing routine.
# The runnable sign lives in the ch23-sqisign package under solutions/
# and is exercised by tests/ch23/test_sqisign_roundtrip.py.

import hashlib

CHALLENGE_WALK_LENGTH = 3

def hash_to_walk(message, pk_a, pk_b, length):
    h = hashlib.sha256()
    h.update(message)
    for fp2 in (pk_a, pk_b):
        h.update(fp2[0].to_bytes(2, "big"))
        h.update(fp2[1].to_bytes(2, "big"))
    digest = h.digest()
    while len(digest) < length:
        digest = digest + hashlib.sha256(digest).digest()
    out = []
    for i in range(length):
        byte = digest[i]
        degree = 2 if (byte & 0x80) == 0 else 3
        out.append((degree, byte & 0x7F))
    return out

# Use the actual public-key coefficients (a, b) for the alice keypair
# computed by sqisign.keygen(b"alice"): a = (137, 0), b = (0, 375).
# The j-invariant of this curve is (143, 0).
walk = hash_to_walk(b"hello", (137, 0), (0, 375), CHALLENGE_WALK_LENGTH)
print(walk)
# ==> [(3, 60), (2, 60), (3, 30)]
