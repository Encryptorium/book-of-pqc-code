# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 12: ML-DSA (FIPS 204) from scratch
# Section: "KeyGen"
# https://book.encryptorium.com/part-2-lattices/ch12-mldsa-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch12/07-mod-pm.py

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


# The ML-DSA key equation t = A s1 + s2, shown at ring degree n = 1 so each
# ring element is a single integer in Z_q. Module shape (k, l) = (2, 2), secret
# coefficients drawn from [-eta, eta] with eta = 4. The real scheme runs the
# same equation over degree-255 polynomials with A expanded from rho.
rng = np.random.default_rng(seed=204)
A = rng.integers(0, Q, size=(2, 2), dtype=np.int64)
s1 = rng.integers(-4, 5, size=2, dtype=np.int64)
s2 = rng.integers(-4, 5, size=2, dtype=np.int64)
t = (A @ s1 + s2) % Q

# Power2Round drops the low d = 13 bits of t; the public key ships t1 only.
t1 = np.empty(2, dtype=np.int64)
t0 = np.empty(2, dtype=np.int64)
for i in range(2):
    t1[i], t0[i] = power2round(int(t[i]))

print("t  =", [int(x) for x in t])
print("t1 =", [int(x) for x in t1])
print("reconstructs t :",
      all(int(t1[i]) * (1 << D) + int(t0[i]) == int(t[i]) for i in range(2)))
print("t0 within (-2^12, 2^12] :",
      bool(np.all((t0 > -(1 << (D - 1))) & (t0 <= (1 << (D - 1))))))
# ==> t  = [2613718, 1033595]
# ==> t1 = [319, 126]
# ==> reconstructs t : True
# ==> t0 within (-2^12, 2^12] : True
