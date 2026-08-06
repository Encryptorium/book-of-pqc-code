# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 8: The LWE problem
# Section: "Sampling LWE instances in Python"
# https://book.encryptorium.com/part-2-lattices/ch08-the-lwe-problem/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch08/06-sampling-lwe-instances-in-python.py

import numpy as np

n, q, m, B = 4, 97, 8, 1

# Search instance with secret s and small error e.
rng = np.random.default_rng(seed=0)
s = rng.integers(low=0, high=q, size=n, dtype=np.int64)
A = rng.integers(low=0, high=q, size=(m, n), dtype=np.int64)
e = rng.integers(low=-B, high=B + 1, size=m, dtype=np.int64)
b_lwe = (A @ s + e) % q

# Decisional "uniform" side: same A, random u.
rng2 = np.random.default_rng(seed=7)
u_rand = rng2.integers(low=0, high=q, size=m, dtype=np.int64)

print("b_lwe  =", b_lwe.tolist())
# ==> b_lwe  = [19, 31, 29, 65, 48, 86, 53, 87]
print("u_rand =", u_rand.tolist())
# ==> u_rand = [91, 60, 66, 87, 56, 75, 80, 21]
