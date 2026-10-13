# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 10: Regev encryption from scratch
# Section: "IND-CPA from decisional LWE"
# https://book.encryptorium.com/part-2-lattices/ch10-regev-encryption-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch10/06-keygen.py

import itertools
import numpy as np

def keygen(n, q, m, B, rng):
    s = rng.integers(0, q, size=n, dtype=np.int64)
    A = rng.integers(0, q, size=(m, n), dtype=np.int64)
    e = rng.integers(-B, B + 1, size=m, dtype=np.int64)
    return (A, (A @ s + e) % q), s

def encrypt(A, b, bit, q, rng):
    m = b.shape[0]
    r = rng.integers(0, 2, size=m, dtype=np.int64)
    half_q = q // 2
    return (A.T @ r) % q, (int(b @ r) + half_q * bit) % q

# The eavesdropper holds the public key (A, b) and a ciphertext
# (c1, c2), never s. It tabulates A^T r for all 2^m choices of r.
n, q, m, B = 4, 97, 8, 1
cube = np.array(list(itertools.product((0, 1), repeat=m)), dtype=np.int64)
one_to_one, recovered, shifts = 0, 0, set()
for seed in range(200):
    rng = np.random.default_rng(seed=seed)
    (A, b), _ = keygen(n, q, m, B, rng)
    table = {tuple(((A.T @ r) % q).tolist()): r for r in cube}
    one_to_one += len(table) == len(cube)
    for bit in (0, 1):
        c1, c2 = encrypt(A, b, bit, q, rng)
        r = table[tuple(c1.tolist())]
        shift = (c2 - int(b @ r)) % q
        shifts.add(shift)
        recovered += int(shift == q // 2) == bit

print("keys where r -> A^T r is one to one:", one_to_one, "of 200")
print("values of c2 - b^T r:", sorted(shifts))
print("bits recovered without s:", recovered, "of 400")
# ==> keys where r -> A^T r is one to one: 200 of 200
# ==> values of c2 - b^T r: [0, 48]
# ==> bits recovered without s: 400 of 400
