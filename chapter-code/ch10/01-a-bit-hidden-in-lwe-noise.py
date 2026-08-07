# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 10: Regev encryption from scratch
# Section: "A bit hidden in LWE noise"
# https://book.encryptorium.com/part-2-lattices/ch10-regev-encryption-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch10/01-a-bit-hidden-in-lwe-noise.py

import numpy as np

n, q, m, B = 4, 97, 8, 1
rng = np.random.default_rng(seed=0)
s = rng.integers(0, q, size=n, dtype=np.int64)
A = rng.integers(0, q, size=(m, n), dtype=np.int64)
e = rng.integers(-B, B + 1, size=m, dtype=np.int64)
b = (A @ s + e) % q
r = rng.integers(0, 2, size=m, dtype=np.int64)
half_q = q // 2

c1 = (A.T @ r) % q
c2_one = (int(b @ r) + half_q * 1) % q
c2_zero = (int(b @ r) + half_q * 0) % q
v_one = (c2_one - int(c1 @ s)) % q
v_zero = (c2_zero - int(c1 @ s)) % q

print("s =", s.tolist())
print("r =", r.tolist())
print("c1 =", c1.tolist())
print("c2 for mu=1:", c2_one, "c2 for mu=0:", c2_zero)
print("v for mu=1:", v_one, "v for mu=0:", v_zero)
# ==> s = [82, 61, 49, 26]
# ==> r = [0, 1, 1, 1, 0, 1, 1, 0]
# ==> c1 = [44, 50, 54, 74]
# ==> c2 for mu=1: 21 c2 for mu=0: 70
# ==> v for mu=1: 45 v for mu=0: 94
