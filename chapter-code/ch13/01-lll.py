# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 13: Lattice cryptanalysis
# Section: "A toy primal attack that actually runs"
# https://book.encryptorium.com/part-2-lattices/ch13-lattice-cryptanalysis/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch13/01-lll.py

import numpy as np


def lll(basis, delta=0.75):
    """Toy educational LLL: the standard size-reduce / swap loop at parameter delta."""
    B = basis.astype(float).copy()
    dim = B.shape[0]

    def gso():
        Q = np.zeros_like(B)
        mu = np.zeros((dim, dim))
        for i in range(dim):
            Q[i] = B[i].copy()
            for j in range(i):
                mu[i, j] = B[i] @ Q[j] / (Q[j] @ Q[j])
                Q[i] = Q[i] - mu[i, j] * Q[j]
        return Q, mu

    k = 1
    while k < dim:
        Q, mu = gso()
        for j in range(k - 1, -1, -1):
            if abs(mu[k, j]) > 0.5:
                B[k] = B[k] - round(mu[k, j]) * B[j]
                Q, mu = gso()
        if Q[k] @ Q[k] >= (delta - mu[k, k - 1] ** 2) * (Q[k - 1] @ Q[k - 1]):
            k += 1
        else:
            B[[k, k - 1]] = B[[k - 1, k]]
            k = max(k - 1, 1)
    return B.astype(int)


rng = np.random.default_rng(0)
n, m, q = 4, 8, 97
A = rng.integers(0, q, size=(m, n))
s = rng.integers(-1, 2, size=n)
e = rng.integers(-1, 2, size=m)
b = (A @ s + e) % q

# Kannan primal embedding of dimension m + n + 1 = 13.
d = m + n + 1
basis = np.zeros((d, d), dtype=int)
basis[:m, :m] = q * np.eye(m, dtype=int)
basis[m:m + n, :m] = A.T
basis[m:m + n, m:m + n] = np.eye(n, dtype=int)
basis[m + n, :m] = b
basis[m + n, m + n] = 1

planted = np.concatenate([e, -s, [1]])
print(f"planted secret s = {s.tolist()}")
# ==> planted secret s = [-1, 1, -1, 0]
print(f"planted error  e = {e.tolist()}")
# ==> planted error  e = [-1, -1, 0, 0, 0, -1, -1, -1]
print(f"planted (e || -s || 1) norm = {float(np.linalg.norm(planted)):.4f}")
# ==> planted (e || -s || 1) norm = 3.0000

reduced = lll(basis)
shortest = reduced[0]
print(f"LLL shortest row norm      = {float(np.linalg.norm(shortest)):.4f}")
# ==> LLL shortest row norm      = 3.0000
print(f"equals planted vector ?    {np.array_equal(shortest, planted) or np.array_equal(shortest, -planted)}")
# ==> equals planted vector ?    True
