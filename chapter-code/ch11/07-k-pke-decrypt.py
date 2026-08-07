# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 11: ML-KEM (FIPS 203) from scratch
# Section: "K-PKE.Decrypt"
# https://book.encryptorium.com/part-2-lattices/ch11-mlkem-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch11/07-k-pke-decrypt.py

import numpy as np

q = 97
k = 2

rng = np.random.default_rng(seed=0)

# Module-Regev at k = 2, n = 1: secret and error live in Z_q^k,
# matrix lives in Z_q^{k x k}, public vector is a Z_q^k column.
s = rng.integers(-1, 2, size=k, dtype=np.int64) % q
A = rng.integers(0, q, size=(k, k), dtype=np.int64)
e = rng.integers(-1, 2, size=k, dtype=np.int64) % q
t = (A @ s + e) % q

# Encryption: r, e1 in Z_q^k, e2 scalar. mu is the message bit.
mu = 1
r = rng.integers(-1, 2, size=k, dtype=np.int64) % q
e1 = rng.integers(-1, 2, size=k, dtype=np.int64) % q
e2 = int(rng.integers(-1, 2, dtype=np.int64)) % q
u = (A.T @ r + e1) % q
v = int((t @ r + e2 + ((q + 1) // 2) * mu) % q)

# Decryption: w = v - s^T u. Round to nearer of 0 or (q+1)//2 using
# the same decode formula as Chapter 10 (midpoint -> 0).
w = (v - int(s @ u)) % q
half_q = q // 2
decoded = ((2 * w + half_q) // q) % 2
print("(q + 1) // 2 =", (q + 1) // 2)
print("w =", w)
print("decoded mu =", decoded, "expected =", mu)
# ==> (q + 1) // 2 = 49
# ==> w = 49
# ==> decoded mu = 1 expected = 1
