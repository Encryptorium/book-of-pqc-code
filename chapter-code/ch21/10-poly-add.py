# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 21: HQC, a pedagogical implementation
# Section: "HQC decryption and noise cancellation"
# https://book.encryptorium.com/part-4-code-isogeny/ch21-hqc-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch21/10-poly-add.py

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

# Reconstruct everything from seeds
rng = random.Random(0)
s = [rng.randint(0, 1) for _ in range(N)]
x = sample_sparse(N, W, rng)
y = sample_sparse(N, W, rng)
h = poly_add(x, poly_mul(s, y, N))

msg = [1, 0, 1, 1]
rng_enc = random.Random(1000)
r1 = sample_sparse(N, W_R, rng_enc)
r2 = sample_sparse(N, W_R, rng_enc)
e = sample_sparse(N, W_E, rng_enc)

u = poly_add(r1, poly_mul(r2, s, N))
codeword = rep_encode(msg, R, N)
v = poly_add(poly_add(poly_mul(r2, h, N), codeword), e)

# Decryption
noisy_code = poly_add(v, poly_mul(u, y, N))
recovered = rep_decode(noisy_code, R, N)

# Verify the noise decomposition
noise = poly_add(noisy_code, codeword)
expected_noise = poly_add(
    poly_add(poly_mul(r2, x, N), poly_mul(r1, y, N)), e
)
print("noise matches r2*x + r1*y + e:", noise == expected_noise)
print("noise weight:", sum(noise))
print("recovered:", recovered)
print("correct:", recovered == msg)
# ==> noise matches r2*x + r1*y + e: True
# ==> noise weight: 19
# ==> recovered: [1, 0, 1, 1]
# ==> correct: True
