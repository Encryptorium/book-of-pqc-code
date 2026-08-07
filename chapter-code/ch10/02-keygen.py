# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 10: Regev encryption from scratch
# Section: "Key generation, encryption, decryption"
# https://book.encryptorium.com/part-2-lattices/ch10-regev-encryption-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch10/02-keygen.py

import numpy as np

def keygen(n, q, m, B, rng):
    s = rng.integers(0, q, size=n, dtype=np.int64)
    A = rng.integers(0, q, size=(m, n), dtype=np.int64)
    e = rng.integers(-B, B + 1, size=m, dtype=np.int64)
    b = (A @ s + e) % q
    return (A, b), s

rng = np.random.default_rng(seed=0)
(A, b), s = keygen(4, 97, 8, 1, rng)

# Recompute A @ s with an explicit Python loop and verify that
# b - A s lives in the symmetric interval [-1, 1], which is the
# noise bound B = 1 set by the parameters.
As_loop = [sum(int(A[i, j]) * int(s[j]) for j in range(4)) % 97
           for i in range(8)]
residual = [(int(b[i]) - As_loop[i]) % 97 for i in range(8)]
e_sym = [v - 97 if v > 48 else v for v in residual]
print("s =", s.tolist())
print("b - A s (symmetric) =", e_sym)
# ==> s = [82, 61, 49, 26]
# ==> b - A s (symmetric) = [-1, -1, 0, 0, 0, -1, -1, -1]
