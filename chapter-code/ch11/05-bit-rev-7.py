# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 11: ML-KEM (FIPS 203) from scratch
# Section: "The specialized partial NTT at (256, 3329)"
# https://book.encryptorium.com/part-2-lattices/ch11-mlkem-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch11/05-bit-rev-7.py

import numpy as np

Q = 3329
N = 256
ZETA = 17
INV_128 = pow(128, -1, Q)  # 3303


def bit_rev_7(i):
    out = 0
    for _ in range(7):
        out = (out << 1) | (i & 1)
        i >>= 1
    return out


ZETAS_NTT = [pow(ZETA, bit_rev_7(k), Q) for k in range(128)]
ZETAS_MUL = [pow(ZETA, 2 * bit_rev_7(k) + 1, Q) for k in range(128)]


def ntt(f):
    f_hat = np.asarray(f, dtype=np.int64).copy() % Q
    i = 1
    length = 128
    while length >= 2:
        start = 0
        while start < N:
            zeta = ZETAS_NTT[i]
            i += 1
            for j in range(start, start + length):
                t = (zeta * int(f_hat[j + length])) % Q
                f_hat[j + length] = (int(f_hat[j]) - t) % Q
                f_hat[j] = (int(f_hat[j]) + t) % Q
            start += 2 * length
        length //= 2
    return f_hat


def inverse_ntt(f_hat):
    f = np.asarray(f_hat, dtype=np.int64).copy() % Q
    i = 127
    length = 2
    while length <= 128:
        start = 0
        while start < N:
            zeta = ZETAS_NTT[i]
            i -= 1
            for j in range(start, start + length):
                t = int(f[j])
                f[j] = (t + int(f[j + length])) % Q
                f[j + length] = (zeta * (int(f[j + length]) - t)) % Q
            start += 2 * length
        length *= 2
    return (f * INV_128) % Q


def multiply_ntts(f_hat, g_hat):
    out = np.zeros(N, dtype=np.int64)
    for i in range(128):
        gamma = ZETAS_MUL[i]
        a0, a1 = int(f_hat[2 * i]), int(f_hat[2 * i + 1])
        b0, b1 = int(g_hat[2 * i]), int(g_hat[2 * i + 1])
        out[2 * i] = (a0 * b0 + a1 * b1 * gamma) % Q
        out[2 * i + 1] = (a0 * b1 + a1 * b0) % Q
    return out


# Self-consistency check: the NTT product equals schoolbook convolution
# in R_q, for a random polynomial pair.
def schoolbook(f, g):
    h = np.zeros(N, dtype=np.int64)
    for i in range(N):
        fi = int(f[i])
        for j in range(N):
            k = i + j
            term = (fi * int(g[j])) % Q
            if k < N:
                h[k] = (int(h[k]) + term) % Q
            else:
                h[k - N] = (int(h[k - N]) - term) % Q
    return h


rng = np.random.default_rng(seed=20260411)
f = rng.integers(0, Q, size=N, dtype=np.int64)
g = rng.integers(0, Q, size=N, dtype=np.int64)
h_ntt = inverse_ntt(multiply_ntts(ntt(f), ntt(g)))
h_school = schoolbook(f, g)
print("NTT product equals schoolbook =", bool(np.array_equal(h_ntt, h_school)))
print("ZETAS_NTT[1] =", ZETAS_NTT[1])
# ==> NTT product equals schoolbook = True
# ==> ZETAS_NTT[1] = 1729
