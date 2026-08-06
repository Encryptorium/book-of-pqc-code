# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 9: Ring-LWE and Module-LWE
# Section: "The ring $R_q$ and its negacyclic multiplication"
# https://book.encryptorium.com/part-2-lattices/ch09-ring-lwe-and-module-lwe/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch09/01-ring-mul-naive.py

import numpy as np

def ring_mul_naive(f, g, q):
    n = len(f)
    h = np.zeros(n, dtype=np.int64)
    for i in range(n):
        for j in range(n):
            k = i + j
            if k < n:
                h[k] += f[i] * g[j]
            else:
                # x^n = -1 wraps the tail into the head with a sign flip
                h[k - n] -= f[i] * g[j]
    return h % q

f = np.array([1, 2, 3, 4], dtype=np.int64)
g = np.array([5, 6, 0, 0], dtype=np.int64)
h = ring_mul_naive(f, g, 17)
print("f * g in R_17 =", h.tolist())
# ==> f * g in R_17 = [15, 16, 10, 4]
