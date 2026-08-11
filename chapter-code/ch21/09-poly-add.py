# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 21: HQC, a pedagogical implementation
# Section: "HQC encryption"
# https://book.encryptorium.com/part-4-code-isogeny/ch21-hqc-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch21/09-poly-add.py

import random

def poly_add(a, b):
    return [ai ^ bi for ai, bi in zip(a, b)]

def poly_mul(a, b, n):
    c = [0] * n
    for i in range(n):
        if a[i] == 0:
            continue
        for j in range(n):
            if b[j]:
                c[(i + j) % n] ^= 1
    return c

def sample_sparse(n, w, rng):
    positions = rng.sample(range(n), w)
    vec = [0] * n
    for p in positions:
        vec[p] = 1
    return vec

def rep_encode(message, r, n):
    codeword = []
    for bit in message:
        codeword.extend([bit] * r)
    codeword.extend([0] * (n - len(codeword)))
    return codeword

N, W, W_R, W_E, R = 83, 3, 3, 3, 17

# Reconstruct public key from seed 0
rng = random.Random(0)
s = [rng.randint(0, 1) for _ in range(N)]
x = sample_sparse(N, W, rng)
y = sample_sparse(N, W, rng)
h = poly_add(x, poly_mul(s, y, N))

# Encrypt message [1, 0, 1, 1]
msg = [1, 0, 1, 1]
rng_enc = random.Random(1000)
r1 = sample_sparse(N, W_R, rng_enc)
r2 = sample_sparse(N, W_R, rng_enc)
e = sample_sparse(N, W_E, rng_enc)

u = poly_add(r1, poly_mul(r2, s, N))
codeword = rep_encode(msg, R, N)
v = poly_add(poly_add(poly_mul(r2, h, N), codeword), e)

r1_pos = [i for i, v in enumerate(r1) if v]
r2_pos = [i for i, v in enumerate(r2) if v]
e_pos = [i for i, v in enumerate(e) if v]
print("r1 support:", r1_pos)
print("r2 support:", r2_pos)
print("e support: ", e_pos)
print("ciphertext size: 2 *", N, "=", 2 * N, "bits")
# ==> r1 support: [12, 50, 54]
# ==> r2 support: [8, 45, 59]
# ==> e support:  [21, 55, 68]
# ==> ciphertext size: 2 * 83 = 166 bits
