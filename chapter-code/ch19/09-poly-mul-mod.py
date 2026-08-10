# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 19: Coding theory for cryptographers
# Section: "Quasi-cyclic codes"
# https://book.encryptorium.com/part-4-code-isogeny/ch19-coding-theory-for-cryptographers/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch19/09-poly-mul-mod.py

def poly_mul_mod(a, b, n):
    """Multiply polynomials a and b in GF(2)[x]/(x^n - 1)."""
    result = [0] * n
    for i, ai in enumerate(a):
        if ai == 0:
            continue
        for j, bj in enumerate(b):
            if bj:
                result[(i + j) % n] ^= 1
    return result

# Small example: n=5, multiply (1 + x) by (1 + x^3) mod x^5 - 1.
a = [1, 1, 0, 0, 0]
b = [1, 0, 0, 1, 0]
c = poly_mul_mod(a, b, 5)
print("product mod x^5-1:", c)
# ==> product mod x^5-1: [1, 1, 0, 1, 1]
