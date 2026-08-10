# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 12: ML-DSA (FIPS 204) from scratch
# Section: "Power2Round, Decompose, and the hint"
# https://book.encryptorium.com/part-2-lattices/ch12-mldsa-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch12/06-mod-pm.py

import numpy as np

Q = 8380417
D = 13


def mod_pm(r, alpha):
    m = r % alpha
    return m - alpha if m > alpha // 2 else m


def power2round(r):
    r %= Q
    r0 = mod_pm(r, 1 << D)
    return (r - r0) >> D, r0


def decompose(r, gamma2):
    r %= Q
    r0 = mod_pm(r, 2 * gamma2)
    if r - r0 == Q - 1:
        return 0, r0 - 1
    return (r - r0) // (2 * gamma2), r0


def high_bits(r, gamma2):
    return decompose(r, gamma2)[0]


def make_hint(z, r, gamma2):
    return 1 if high_bits(r, gamma2) != high_bits((r + z) % Q, gamma2) else 0


def use_hint(h, r, gamma2):
    m = (Q - 1) // (2 * gamma2)
    r1, r0 = decompose(r, gamma2)
    if h == 1:
        return (r1 + 1) % m if r0 > 0 else (r1 - 1) % m
    return r1


gamma_2 = (Q - 1) // 32     # ML-DSA-65/87 low-order window

# Power2Round splits a public coefficient into a top part and the dropped d bits.
t = 4211255
t1, t0 = power2round(t)
print("power2round(t) = (t1, t0) =", (t1, t0))
print("t1 * 2^d + t0 == t :", t1 * (1 << D) + t0 == t)

# The hint lets a verifier that only knows HighBits recover HighBits(r + z)
# whenever the perturbation z stays within the low-order window gamma_2.
rng = np.random.default_rng(seed=7)
ok = True
for _ in range(20000):
    r = int(rng.integers(0, Q))
    z = int(rng.integers(-gamma_2, gamma_2 + 1))
    if use_hint(make_hint(z, r, gamma_2), r, gamma_2) != high_bits((r + z) % Q, gamma_2):
        ok = False
        break
print("UseHint(MakeHint(z, r), r) == HighBits(r + z) for |z| <= gamma_2 :", ok)
# ==> power2round(t) = (t1, t0) = (514, 567)
# ==> t1 * 2^d + t0 == t : True
# ==> UseHint(MakeHint(z, r), r) == HighBits(r + z) for |z| <= gamma_2 : True
