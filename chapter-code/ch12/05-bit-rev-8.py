# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 12: ML-DSA (FIPS 204) from scratch
# Section: "The full NTT at (256, 8380417)"
# https://book.encryptorium.com/part-2-lattices/ch12-mldsa-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch12/05-bit-rev-8.py

import numpy as np

Q = 8380417
N = 256
ZETA = 1753
N_INV = pow(N, -1, Q)


def bit_rev_8(k):
    r = 0
    for _ in range(8):
        r = (r << 1) | (k & 1)
        k >>= 1
    return r


ZETAS = [pow(ZETA, bit_rev_8(k), Q) for k in range(256)]


def ntt(w):
    w_hat = (np.asarray(w, dtype=np.int64) % Q).copy()
    m = 0
    length = 128
    while length >= 1:
        start = 0
        while start < N:
            m += 1
            zeta = ZETAS[m]
            for j in range(start, start + length):
                t = (zeta * int(w_hat[j + length])) % Q
                w_hat[j + length] = (int(w_hat[j]) - t) % Q
                w_hat[j] = (int(w_hat[j]) + t) % Q
            start += 2 * length
        length //= 2
    return w_hat


def ntt_inverse(w_hat):
    w = (np.asarray(w_hat, dtype=np.int64) % Q).copy()
    m = 256
    length = 1
    while length < N:
        start = 0
        while start < N:
            m -= 1
            zeta = (-ZETAS[m]) % Q
            for j in range(start, start + length):
                t = int(w[j])
                w[j] = (t + int(w[j + length])) % Q
                w[j + length] = (zeta * (t - int(w[j + length]))) % Q
            start += 2 * length
        length *= 2
    return np.array([(N_INV * int(w[j])) % Q for j in range(N)], dtype=np.int64)


def multiply_ntts(a_hat, b_hat):
    return np.array([(int(a_hat[i]) * int(b_hat[i])) % Q for i in range(N)],
                    dtype=np.int64)


def schoolbook(a, b):
    out = [0] * N
    for i in range(N):
        ai = int(a[i])
        for j in range(N):
            k = i + j
            prod = ai * int(b[j])
            if k < N:
                out[k] = (out[k] + prod) % Q
            else:                      # X^256 = -1: wrap with a sign flip
                out[k - N] = (out[k - N] - prod) % Q
    return np.array(out, dtype=np.int64)


rng = np.random.default_rng(seed=20260723)
f = rng.integers(0, Q, size=N, dtype=np.int64)
g = rng.integers(0, Q, size=N, dtype=np.int64)
prod_ntt = ntt_inverse(multiply_ntts(ntt(f), ntt(g)))
prod_school = schoolbook(f, g)
print("N_INV =", N_INV)
print("ZETAS[1] =", ZETAS[1])
print("NTT product equals schoolbook =", bool(np.array_equal(prod_ntt, prod_school)))
# ==> N_INV = 8347681
# ==> ZETAS[1] = 4808194
# ==> NTT product equals schoolbook = True
