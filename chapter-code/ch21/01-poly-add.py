# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 21: HQC, a pedagogical implementation
# Section: "A toy HQC round-trip"
# https://book.encryptorium.com/part-4-code-isogeny/ch21-hqc-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch21/01-poly-add.py

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

def support(v):
    return [i for i, x in enumerate(v) if x]

def rep_encode(message, r, n):
    codeword = []
    for bit in message:
        codeword.extend([bit] * r)
    codeword.extend([0] * (n - len(codeword)))
    return codeword

def rep_decode(received, r, n):
    k = n // r
    message = []
    for i in range(k):
        block = received[i * r : (i + 1) * r]
        ones = sum(block)
        message.append(1 if ones > r // 2 else 0)
    return message

N, W, W_R, W_E, R = 83, 3, 3, 3, 17
K = N // R  # 4

# Key generation
rng = random.Random(0)
s = [rng.randint(0, 1) for _ in range(N)]
x = sample_sparse(N, W, rng)
y = sample_sparse(N, W, rng)
h = poly_add(x, poly_mul(s, y, N))

print("x support:", support(x))
print("y support:", support(y))
print("h weight: ", sum(h))
# ==> x support: [14, 41, 78]
# ==> y support: [62, 75, 80]
# ==> h weight:  46
