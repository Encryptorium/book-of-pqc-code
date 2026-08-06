# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 9: Ring-LWE and Module-LWE
# Section: "Sampling Ring-LWE and Module-LWE in Python"
# https://book.encryptorium.com/part-2-lattices/ch09-ring-lwe-and-module-lwe/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch09/04-ring-mul-naive.py

import numpy as np

n, q, k, m, B = 4, 17, 2, 4, 1

def ring_mul_naive(f, g, q):
    n = len(f)
    h = np.zeros(n, dtype=np.int64)
    for i in range(n):
        for j in range(n):
            kk = i + j
            if kk < n:
                h[kk] += f[i] * g[j]
            else:
                h[kk - n] -= f[i] * g[j]
    return h % q

rng = np.random.default_rng(seed=0)
A = rng.integers(low=0, high=q, size=(m, k, n), dtype=np.int64)
s = rng.integers(low=0, high=q, size=(k, n), dtype=np.int64)
raw_e = rng.integers(low=-B, high=B + 1, size=(m, n), dtype=np.int64)
e = raw_e % q

b = np.zeros((m, n), dtype=np.int64)
for i in range(m):
    row = np.zeros(n, dtype=np.int64)
    for j in range(k):
        row = (row + ring_mul_naive(A[i, j], s[j], q)) % q
    b[i] = (row + e[i]) % q

print("A shape =", A.shape)
# ==> A shape = (4, 2, 4)
print("s shape =", s.shape)
# ==> s shape = (2, 4)
print("b shape =", b.shape)
# ==> b shape = (4, 4)
print("b[0] =", b[0].tolist())
# ==> b[0] = [1, 15, 16, 9]
