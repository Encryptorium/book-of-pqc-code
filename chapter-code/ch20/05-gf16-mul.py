# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 20: McEliece: the original PQC
# Section: "Goppa code construction"
# https://book.encryptorium.com/part-4-code-isogeny/ch20-mceliece-the-original-pqc/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch20/05-gf16-mul.py

import random

def gf16_mul(a, b):
    result = 0
    for _ in range(4):
        if b & 1: result ^= a
        b >>= 1; a <<= 1
        if a & 16: a ^= 0b10011
    return result

def gf16_inv(a):
    for x in range(1, 16):
        if gf16_mul(a, x) == 1: return x

def poly_eval_gf16(coeffs, x):
    result = 0
    for c in reversed(coeffs):
        result = gf16_mul(result, x) ^ c
    return result

# Find an irreducible degree-2 polynomial over GF(16).
rng = random.Random(42)
while True:
    c0, c1 = rng.randint(0, 15), rng.randint(0, 15)
    g = [c0, c1, 1]  # monic: x^2 + c1*x + c0
    if all(poly_eval_gf16(g, a) != 0 for a in range(16)):
        break  # no roots in GF(16) => irreducible for degree 2

print(f"g(x) = {g}")

# Build the 8x16 binary parity-check matrix.
support = list(range(16))
t = 2
h = [gf16_inv(poly_eval_gf16(g, a)) for a in support]

V = []
for i in range(t):
    row = []
    for j in range(16):
        lj_pow = 1
        for _ in range(i):
            lj_pow = gf16_mul(lj_pow, support[j])
        row.append(gf16_mul(lj_pow, h[j]))
    V.append(row)

H = []
for row in V:
    for bit in range(4):
        H.append([(entry >> bit) & 1 for entry in row])

print(f"H shape: {len(H)} x {len(H[0])}")
# ==> g(x) = [8, 7, 1]
# ==> H shape: 8 x 16
