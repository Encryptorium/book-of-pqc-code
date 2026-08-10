# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 19: Coding theory for cryptographers
# Section: "Goppa codes"
# https://book.encryptorium.com/part-4-code-isogeny/ch19-coding-theory-for-cryptographers/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch19/07-gf8-mul.py

def gf8_mul(a, b):
    """Multiply in GF(2^3) = GF(2)[x]/(x^3 + x + 1)."""
    p = 0
    for _ in range(3):
        if b & 1:
            p ^= a
        b >>= 1
        a <<= 1
        if a & 0b1000:
            a ^= 0b1011  # reduce mod x^3 + x + 1
    return p

def gf8_inv(a):
    """Brute-force inverse in GF(8). Crashes on zero input."""
    assert a != 0, "zero has no inverse"
    for x in range(1, 8):
        if gf8_mul(a, x) == 1:
            return x

# Goppa code with g(x) = x - 3 over GF(8), support = GF(8) \ {3}.
g_root = 3
support = [i for i in range(8) if i != g_root]
print("support:", support)
# ==> support: [0, 1, 2, 4, 5, 6, 7]

# H_j = 1 / (L_j XOR g_root), expanded to 3 binary rows.
H_goppa = [[0] * len(support) for _ in range(3)]
for j, alpha in enumerate(support):
    val = gf8_inv(alpha ^ g_root)
    for bit in range(3):
        H_goppa[2 - bit][j] = (val >> bit) & 1

print("Goppa parity-check matrix:")
for row in H_goppa:
    print(" ", row)
# ==> Goppa parity-check matrix:
# ==>   [1, 1, 0, 1, 0, 0, 1]
# ==>   [1, 0, 0, 0, 1, 1, 1]
# ==>   [0, 1, 1, 0, 1, 0, 1]
