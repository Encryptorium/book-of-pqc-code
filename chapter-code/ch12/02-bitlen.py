# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 12: ML-DSA (FIPS 204) from scratch
# Section: "Serialization: SimpleBitPack and BitPack"
# https://book.encryptorium.com/part-2-lattices/ch12-mldsa-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch12/02-bitlen.py

import numpy as np


def bitlen(m):
    return m.bit_length()


def bit_pack(w, a, b):
    width = bitlen(a + b)
    mask = (1 << width) - 1
    big = 0
    for i in range(256):
        big |= ((b - int(w[i])) & mask) << (i * width)
    return big.to_bytes(32 * width, "little")


def bit_unpack(v, a, b):
    width = bitlen(a + b)
    big = int.from_bytes(v, "little")
    mask = (1 << width) - 1
    return np.array([b - ((big >> (i * width)) & mask) for i in range(256)],
                    dtype=np.int64)


# The response z packs at (a, b) = (gamma_1 - 1, gamma_1) for ML-DSA-65,
# so each coefficient uses bitlen(2*gamma_1 - 1) = 20 bits.
gamma_1 = 1 << 19
rng = np.random.default_rng(seed=20260723)
z = rng.integers(-(gamma_1 - 1), gamma_1 + 1, size=256, dtype=np.int64)
packed = bit_pack(z, gamma_1 - 1, gamma_1)
recovered = bit_unpack(packed, gamma_1 - 1, gamma_1)
print("bits per coefficient =", bitlen(2 * gamma_1 - 1))
print("packed length =", len(packed))
print("round trip equal =", bool(np.array_equal(recovered, z)))
# ==> bits per coefficient = 20
# ==> packed length = 640
# ==> round trip equal = True
