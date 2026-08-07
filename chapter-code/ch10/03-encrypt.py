# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 10: Regev encryption from scratch
# Section: "Key generation, encryption, decryption"
# https://book.encryptorium.com/part-2-lattices/ch10-regev-encryption-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch10/03-encrypt.py

import numpy as np

def encrypt(A, b, bit, q, rng):
    m = b.shape[0]
    r = rng.integers(0, 2, size=m, dtype=np.int64)
    half_q = q // 2
    c1 = (A.T @ r) % q
    c2 = (int(b @ r) + half_q * bit) % q
    return c1, int(c2)

# Replay the seeded keygen so this block is self-contained.
rng = np.random.default_rng(seed=0)
n, q, m, B = 4, 97, 8, 1
s = rng.integers(0, q, size=n, dtype=np.int64)
A = rng.integers(0, q, size=(m, n), dtype=np.int64)
e = rng.integers(-B, B + 1, size=m, dtype=np.int64)
b = (A @ s + e) % q

c1_one, c2_one = encrypt(A, b, 1, q, rng)
print("mu = 1: c1 =", c1_one.tolist(), "c2 =", c2_one)
# ==> mu = 1: c1 = [44, 50, 54, 74] c2 = 21
