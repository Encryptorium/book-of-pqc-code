# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 10: Regev encryption from scratch
# Section: "IND-CPA from decisional LWE"
# https://book.encryptorium.com/part-2-lattices/ch10-regev-encryption-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch10/07-keygen.py

import numpy as np

def keygen(n, q, m, B, rng):
    s = rng.integers(0, q, size=n, dtype=np.int64)
    A = rng.integers(0, q, size=(m, n), dtype=np.int64)
    e = rng.integers(-B, B + 1, size=m, dtype=np.int64)
    return (A, (A @ s + e) % q), s

def encrypt(A, b, bit, q, rng):
    m = b.shape[0]
    r = rng.integers(0, 2, size=m, dtype=np.int64)
    half_q = q // 2
    return (A.T @ r) % q, (int(b @ r) + half_q * bit) % q

def decode(v, q):
    half_q = q // 2
    return ((2 * (v % q) + half_q) // q) % 2

def decrypt(s, c1, c2, q):
    return decode(int(c2) - int(c1 @ s), q)

# The challenger holds s and decrypts any ciphertext except the
# challenge. The adversary sends one query and flips the answer.
n, q, m, B = 4, 97, 8, 1
half_q = q // 2
wins = 0
for seed in range(200):
    rng = np.random.default_rng(seed=seed)
    (A, b), s = keygen(n, q, m, B, rng)
    for bit in (0, 1):
        c1, c2 = encrypt(A, b, bit, q, rng)
        answer = decrypt(s, c1, (c2 + half_q) % q, q)
        wins += (1 - answer) == bit
print("challenge bits found with one query:", wins, "of 400")

# Every honest noise value E = e^T r has |E| <= m B = 8.
flips = sum(decode(half_q * bit + E + half_q, q) == 1 - bit
            for bit in (0, 1) for E in range(-m * B, m * B + 1))
stuck = [v for v in range(q) if decode(v + half_q, q) == decode(v, q)]
print("pairs (bit, E) where the shift flips the bit:", flips, "of 34")
print("decrypted values the shift does not flip:", stuck)
# ==> challenge bits found with one query: 400 of 400
# ==> pairs (bit, E) where the shift flips the bit: 34 of 34
# ==> decrypted values the shift does not flip: [73]
