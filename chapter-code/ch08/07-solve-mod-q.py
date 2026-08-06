# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 8: The LWE problem
# Section: "Why noise makes it hard"
# https://book.encryptorium.com/part-2-lattices/ch08-the-lwe-problem/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch08/07-solve-mod-q.py

import numpy as np

def solve_mod_q(A, b, q):
    A = np.array(A, dtype=np.int64) % q
    b = np.array(b, dtype=np.int64) % q
    m, n = A.shape
    for c in range(n):
        pivot = next((r for r in range(c, m) if A[r, c] != 0), None)
        assert pivot is not None, "rank deficient"
        A[[c, pivot]] = A[[pivot, c]]
        b[c], b[pivot] = int(b[pivot]), int(b[c])
        inv = pow(int(A[c, c]), -1, q)
        A[c] = (A[c] * inv) % q
        b[c] = (int(b[c]) * inv) % q
        for r in range(m):
            if r != c and A[r, c] != 0:
                f = int(A[r, c])
                A[r] = (A[r] - f * A[c]) % q
                b[r] = (int(b[r]) - f * int(b[c])) % q
    for r in range(n, m):
        if int(b[r]) % q != 0:
            return None
    return b[:n].copy()

n, q, m, B = 4, 97, 8, 1
rng = np.random.default_rng(seed=0)
s_true = rng.integers(0, q, size=n, dtype=np.int64)
A = rng.integers(0, q, size=(m, n), dtype=np.int64)
e = rng.integers(-B, B + 1, size=m, dtype=np.int64)
b_clean = (A @ s_true) % q
b_noisy = (A @ s_true + e) % q

s_clean = solve_mod_q(A, b_clean, q)
s_noisy = solve_mod_q(A, b_noisy, q)

print("s_true          =", s_true.tolist())
# ==> s_true          = [82, 61, 49, 26]
print("recovered clean =", s_clean.tolist())
# ==> recovered clean = [82, 61, 49, 26]
print("recovered noisy =", s_noisy)
# ==> recovered noisy = None
