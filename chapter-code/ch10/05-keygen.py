# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 10: Regev encryption from scratch
# Section: "Key generation, encryption, decryption"
# https://book.encryptorium.com/part-2-lattices/ch10-regev-encryption-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch10/05-keygen.py

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

def decrypt(s, c1, c2, q):
    v = (int(c2) - int(c1 @ s)) % q
    half_q = q // 2
    return ((2 * v + half_q) // q) % 2

def failure_rate(n, q, m, B, num_seeds):
    failures = 0
    for seed in range(num_seeds):
        rng = np.random.default_rng(seed=seed)
        (A, b), s = keygen(n, q, m, B, rng)
        for bit in (0, 1):
            c1, c2 = encrypt(A, b, bit, q, rng)
            if decrypt(s, c1, c2, q) != bit:
                failures += 1
    return failures / (2 * num_seeds)

print("feasible   (n=4, q=97, m=8, B=1):", failure_rate(4, 97, 8, 1, 200))
print("infeasible (n=4, q=13, m=8, B=1):", failure_rate(4, 13, 8, 1, 200))
# ==> feasible   (n=4, q=97, m=8, B=1): 0.0
# ==> infeasible (n=4, q=13, m=8, B=1): 0.0675
