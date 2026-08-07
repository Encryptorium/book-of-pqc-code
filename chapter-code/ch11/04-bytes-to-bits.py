# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 11: ML-KEM (FIPS 203) from scratch
# Section: "Sampling: CBD_eta and rejection-sampled uniform"
# https://book.encryptorium.com/part-2-lattices/ch11-mlkem-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch11/04-bytes-to-bits.py

import hashlib
import numpy as np

Q = 3329
N = 256


def _bytes_to_bits(b):
    bits = []
    for byte in b:
        for j in range(8):
            bits.append((byte >> j) & 1)
    return bits


def cbd_eta(byte_string, eta):
    assert len(byte_string) == 64 * eta
    bits = _bytes_to_bits(byte_string)
    f = np.zeros(N, dtype=np.int64)
    for i in range(N):
        x = sum(bits[2 * i * eta + j] for j in range(eta))
        y = sum(bits[2 * i * eta + eta + j] for j in range(eta))
        f[i] = (x - y) % Q
    return f


def sample_ntt(shake_input):
    shake = hashlib.shake_128()
    shake.update(shake_input)
    bytes_requested = 168 * 5
    raw = shake.digest(bytes_requested)
    idx = 0
    out = np.zeros(N, dtype=np.int64)
    j = 0
    while j < N:
        if idx + 3 > len(raw):
            bytes_requested += 168
            raw = shake.digest(bytes_requested)
        b0, b1, b2 = raw[idx], raw[idx + 1], raw[idx + 2]
        idx += 3
        d1 = b0 | ((b1 & 0x0F) << 8)
        d2 = (b1 >> 4) | (b2 << 4)
        if d1 < Q:
            out[j] = d1
            j += 1
        if j < N and d2 < Q:
            out[j] = d2
            j += 1
    return out


# All-zero PRF input at eta=2 produces the zero polynomial because
# every paired-bit x = y = 0 gives f[i] = 0. Non-zero inputs produce
# coefficients in {-2, -1, 0, 1, 2} represented in Z_q.
f_zero = cbd_eta(b"\x00" * 128, 2)
print("CBD(0 bytes, eta=2) sums =", int(f_zero.sum()))

# The rejection sampler consumes bytes until it has 256 valid ones.
# Two distinct seeds produce distinct polynomials with overwhelming
# probability.
a = sample_ntt(b"\x00" * 34)
b = sample_ntt(b"\x01" * 34)
print("sample_ntt output length =", int(a.shape[0]))
print("distinct seeds distinct output =", bool(not np.array_equal(a, b)))
# ==> CBD(0 bytes, eta=2) sums = 0
# ==> sample_ntt output length = 256
# ==> distinct seeds distinct output = True
