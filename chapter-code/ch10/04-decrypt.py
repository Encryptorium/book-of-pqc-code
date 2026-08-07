# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 10: Regev encryption from scratch
# Section: "Key generation, encryption, decryption"
# https://book.encryptorium.com/part-2-lattices/ch10-regev-encryption-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch10/04-decrypt.py

import numpy as np

def decrypt(s, c1, c2, q):
    v = (int(c2) - int(c1 @ s)) % q
    half_q = q // 2
    return ((2 * v + half_q) // q) % 2

# Replay keygen and produce ciphertexts for both message bits with
# the same random r, so the only difference is the encoding shift.
rng = np.random.default_rng(seed=0)
n, q, m, B = 4, 97, 8, 1
s = rng.integers(0, q, size=n, dtype=np.int64)
A = rng.integers(0, q, size=(m, n), dtype=np.int64)
e = rng.integers(-B, B + 1, size=m, dtype=np.int64)
b = (A @ s + e) % q
r = rng.integers(0, 2, size=m, dtype=np.int64)
c1 = (A.T @ r) % q
c2_one = (int(b @ r) + (q // 2) * 1) % q
c2_zero = (int(b @ r) + (q // 2) * 0) % q

print("decrypt mu = 1 ->", decrypt(s, c1, c2_one, q))
print("decrypt mu = 0 ->", decrypt(s, c1, c2_zero, q))
# ==> decrypt mu = 1 -> 1
# ==> decrypt mu = 0 -> 0
