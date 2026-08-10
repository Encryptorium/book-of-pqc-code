# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 12: ML-DSA (FIPS 204) from scratch
# Section: "Sampling: SampleInBall, ExpandA, ExpandS, ExpandMask"
# https://book.encryptorium.com/part-2-lattices/ch12-mldsa-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch12/04-sample-in-ball.py

import hashlib
import numpy as np


def sample_in_ball(rho, tau):
    xof = hashlib.shake_256(rho)
    need = 8
    stream = xof.digest(need)
    signs = int.from_bytes(stream[:8], "little")
    c = np.zeros(256, dtype=np.int64)
    pos = 8
    for i in range(256 - tau, 256):
        while True:
            if pos >= len(stream):
                need += 168
                stream = xof.digest(need)
            j = stream[pos]
            pos += 1
            if j <= i:
                break
        c[i] = c[j]
        bit = (signs >> (i + tau - 256)) & 1
        c[j] = -1 if bit else 1
    return c


# ML-DSA-65: tau = 49 nonzero coefficients, challenge seed c-tilde is 48 bytes.
tau = 49
c = sample_in_ball(bytes(range(48)), tau)
print("challenge length =", int(c.shape[0]))
print("nonzero coefficients =", int(np.count_nonzero(c)))
print("values are +-1 only =", set(int(x) for x in c) == {-1, 0, 1})
print("sum of coefficients =", int(c.sum()))
# ==> challenge length = 256
# ==> nonzero coefficients = 49
# ==> values are +-1 only = True
# ==> sum of coefficients = 3
