# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 9: Ring-LWE and Module-LWE
# Section: "Sampling Ring-LWE and Module-LWE in Python"
# https://book.encryptorium.com/part-2-lattices/ch09-ring-lwe-and-module-lwe/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch09/03-ring-mul-naive.py

import numpy as np

n, q, B = 4, 17, 1
rng = np.random.default_rng(seed=0)

def ring_mul_naive(f, g, q):
    n = len(f)
    h = np.zeros(n, dtype=np.int64)
    for i in range(n):
        for j in range(n):
            k = i + j
            if k < n:
                h[k] += f[i] * g[j]
            else:
                h[k - n] -= f[i] * g[j]
    return h % q

a = rng.integers(low=0, high=q, size=n, dtype=np.int64)
s = rng.integers(low=0, high=q, size=n, dtype=np.int64)
raw_e = rng.integers(low=-B, high=B + 1, size=n, dtype=np.int64)
e = raw_e % q
b = (ring_mul_naive(a, s, q) + e) % q

print("a =", a.tolist())
# ==> a = [14, 10, 8, 4]
print("s =", s.tolist())
# ==> s = [5, 0, 1, 0]
print("raw e =", raw_e.tolist())
# ==> raw e = [-1, 1, 0, 1]
print("b =", b.tolist())
# ==> b = [10, 13, 3, 14]

# Independent identity check. Compute the Z[x] product via numpy.convolve
# and fold the tail into the head with a sign flip (x^n = -1), yielding
# a second path to a * s in R_q that does not call ring_mul_naive.
raw_prod = np.convolve(a, s).astype(np.int64)  # length 2n - 1 = 7
folded = raw_prod[:n].copy()
# raw_prod[n:] has n-1 entries at positions n..2n-2; each subtracts into
# folded[0..n-2] under x^n = -1. The head term at position n-1 (degree
# x^{n-1}) does not wrap and stays in folded[n-1] untouched.
folded[:n - 1] -= raw_prod[n:]
expected_b = (folded + e) % q
print("independent expected b =", expected_b.tolist())
# ==> independent expected b = [10, 13, 3, 14]
print("b == expected :", (b == expected_b).all())
# ==> b == expected : True
