# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 21: HQC, a pedagogical implementation
# Section: "HQC key generation"
# https://book.encryptorium.com/part-4-code-isogeny/ch21-hqc-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch21/08-poly-add.py

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

N, W = 83, 3
rng = random.Random(0)
s = [rng.randint(0, 1) for _ in range(N)]
x = sample_sparse(N, W, rng)
y = sample_sparse(N, W, rng)
h = poly_add(x, poly_mul(s, y, N))

x_pos = [i for i, v in enumerate(x) if v]
y_pos = [i for i, v in enumerate(y) if v]
print("x support:", x_pos)
print("y support:", y_pos)
print("h weight: ", sum(h))
print("public key size: 2 *", N, "=", 2 * N, "bits")
# ==> x support: [14, 41, 78]
# ==> y support: [62, 75, 80]
# ==> h weight:  46
# ==> public key size: 2 * 83 = 166 bits
