# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 9: Ring-LWE and Module-LWE
# Section: "Sampling Ring-LWE and Module-LWE in Python"
# https://book.encryptorium.com/part-2-lattices/ch09-ring-lwe-and-module-lwe/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch09/04-ring-mul.py

import numpy as np

n, q, B, m = 4, 17, 1, 16
rng = np.random.default_rng(seed=0)

def ring_mul(f, g, q, wrap):
    # wrap = +1: the cyclic ring, x^n = 1. wrap = -1: R_q, x^n = -1.
    n = len(f)
    h = np.zeros(n, dtype=np.int64)
    for i in range(n):
        for j in range(n):
            if i + j < n:
                h[i + j] += f[i] * g[j]
            else:
                h[i + j - n] += wrap * f[i] * g[j]
    return h % q

def draw(wrap, uniform):
    # The sampler knows s. The attacker sees only the m pairs (a, b).
    s = rng.integers(low=0, high=q, size=n, dtype=np.int64)
    pairs = []
    for _ in range(m):
        a = rng.integers(low=0, high=q, size=n, dtype=np.int64)
        if uniform:
            b = rng.integers(low=0, high=q, size=n, dtype=np.int64)
        else:
            e = rng.integers(low=-B, high=B + 1, size=n, dtype=np.int64)
            b = (ring_mul(a, s, q, wrap) + e) % q
        pairs.append((a, b))
    return pairs, int(s.sum()) % q

def survivors(pairs):
    # Evaluating at x = 1 sums coefficients. Keep each guess t for s(1)
    # whose residual b(1) - a(1) t lies within n * B of 0 on every pair.
    def short(r):
        r %= q
        return min(r, q - r) <= n * B
    return [t for t in range(q)
            if all(short(int(b.sum()) - int(a.sum()) * t)
                   for a, b in pairs)]

pairs, s1 = draw(wrap=+1, uniform=False)
print("cyclic, Ring-LWE:", survivors(pairs), "and s(1) =", s1)
# ==> cyclic, Ring-LWE: [2] and s(1) = 2
pairs, _ = draw(wrap=+1, uniform=True)
print("cyclic, uniform:", survivors(pairs))
# ==> cyclic, uniform: []
pairs, s1 = draw(wrap=-1, uniform=False)
print("R_q, Ring-LWE:", survivors(pairs), "and s(1) =", s1)
# ==> R_q, Ring-LWE: [] and s(1) = 1
