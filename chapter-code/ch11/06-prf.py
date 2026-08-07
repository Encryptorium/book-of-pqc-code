# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 11: ML-KEM (FIPS 203) from scratch
# Section: "K-PKE.KeyGen"
# https://book.encryptorium.com/part-2-lattices/ch11-mlkem-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch11/06-prf.py

import hashlib
import numpy as np


def PRF(eta, seed, nonce):
    shake = hashlib.shake_256()
    shake.update(seed + bytes([nonce]))
    return shake.digest(64 * eta)


def cbd_eta(byte_string, eta):
    bits = []
    for byte in byte_string:
        for j in range(8):
            bits.append((byte >> j) & 1)
    f = np.zeros(256, dtype=np.int64)
    for i in range(256):
        x = sum(bits[2 * i * eta + j] for j in range(eta))
        y = sum(bits[2 * i * eta + eta + j] for j in range(eta))
        f[i] = (x - y) % 3329
    return f


# Reconstruct sigma from the NIST tcId=26 d seed.
d = bytes.fromhex(
    "A2B4BCA315A6EA4600B4A316E09A2578AA1E8BCE919C8DF3A96C71C843F5B38B"
)
k = 3
sigma = hashlib.sha3_512(d + bytes([k])).digest()[32:]

# Sample s row 0 (nonce 0) and e row 0 (nonce k = 3) with eta_1 = 2.
s_row_0 = cbd_eta(PRF(2, sigma, 0), 2)
e_row_0 = cbd_eta(PRF(2, sigma, k), 2)

# Put the outputs into symmetric representatives for inspection.
def sym(f):
    return [int(x) - 3329 if int(x) > 1664 else int(x) for x in f]


print("s_row_0[:8] =", sym(s_row_0[:8]))
print("e_row_0[:8] =", sym(e_row_0[:8]))
print("nonce 0 vs nonce 3 independent =",
      bool(not np.array_equal(s_row_0, e_row_0)))
# ==> s_row_0[:8] = [0, 0, -1, 0, 2, 0, 1, -1]
# ==> e_row_0[:8] = [0, 0, 0, -1, 1, 0, 0, 0]
# ==> nonce 0 vs nonce 3 independent = True
