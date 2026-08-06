# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 8: The LWE problem
# Section: "Sampling LWE instances in Python"
# https://book.encryptorium.com/part-2-lattices/ch08-the-lwe-problem/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch08/05-sampling-lwe-instances-in-python.py

import numpy as np

n, q, m, B = 4, 97, 8, 1
rng = np.random.default_rng(seed=0)

s = rng.integers(low=0, high=q, size=n, dtype=np.int64)
A = rng.integers(low=0, high=q, size=(m, n), dtype=np.int64)
e = rng.integers(low=-B, high=B + 1, size=m, dtype=np.int64)
b = (A @ s + e) % q

print("s =", s.tolist())
# ==> s = [82, 61, 49, 26]
print("e =", e.tolist())
# ==> e = [-1, -1, 0, 0, 0, -1, -1, -1]
print("b =", b.tolist())
# ==> b = [19, 31, 29, 65, 48, 86, 53, 87]
