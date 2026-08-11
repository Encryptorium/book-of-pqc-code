# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 21: HQC, a pedagogical implementation
# Section: "Polynomial arithmetic in $\text{GF}(2)[x]/(x^n - 1)$"
# https://book.encryptorium.com/part-4-code-isogeny/ch21-hqc-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch21/04-poly-add.py

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

# Worked example: (1 + x^2 + x^5) * (1 + x + x^3) mod x^83 - 1
N = 83
a = [0] * N
b = [0] * N
a[0], a[2], a[5] = 1, 1, 1
b[0], b[1], b[3] = 1, 1, 1
c = poly_mul(a, b, N)
support = [i for i, v in enumerate(c) if v]
print("product support:", support)
# ==> product support: [0, 1, 2, 6, 8]
