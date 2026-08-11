# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 21: HQC, a pedagogical implementation
# Section: "Multi-seed round-trip"
# https://book.encryptorium.com/part-4-code-isogeny/ch21-hqc-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch21/11-poly-add.py

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

def rep_decode(received, r, n):
    k = n // r
    message = []
    for i in range(k):
        block = received[i * r : (i + 1) * r]
        ones = sum(block)
        message.append(1 if ones > r // 2 else 0)
    return message

N, W, W_R, W_E, R = 83, 3, 3, 3, 17
K = N // R
successes = 0
total = 0

for seed in range(20):
    rng_k = random.Random(seed)
    s = [rng_k.randint(0, 1) for _ in range(N)]
    x = sample_sparse(N, W, rng_k)
    y = sample_sparse(N, W, rng_k)
    h = poly_add(x, poly_mul(s, y, N))

    for mi in range(2**K):
        m = [(mi >> b) & 1 for b in range(K)]
        rng_e = random.Random(seed * 1000 + mi + 5000)
        r1 = sample_sparse(N, W_R, rng_e)
        r2 = sample_sparse(N, W_R, rng_e)
        e = sample_sparse(N, W_E, rng_e)
        u = poly_add(r1, poly_mul(r2, s, N))
        cw = rep_encode(m, R, N)
        v = poly_add(poly_add(poly_mul(r2, h, N), cw), e)
        noisy = poly_add(v, poly_mul(u, y, N))
        rec = rep_decode(noisy, R, N)
        total += 1
        if rec == m:
            successes += 1

print(f"{successes}/{total} round-trips succeeded")
# ==> 318/320 round-trips succeeded
