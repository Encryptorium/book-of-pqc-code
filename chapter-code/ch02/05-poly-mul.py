# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 2: Mathematical preliminaries
# Section: "Polynomials over a finite field"
# https://book.encryptorium.com/part-1-foundations/ch02-mathematical-preliminaries/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch02/05-poly-mul.py

def poly_mul(f, g, p):
    result = [0] * (len(f) + len(g) - 1)
    for i, a in enumerate(f):
        for j, b in enumerate(g):
            result[i + j] = (result[i + j] + a * b) % p
    return result

# Multiply (2 + x) by (3 + x^2) in F_5[x].
f = [2, 1]
g = [3, 0, 1]
print(poly_mul(f, g, 5))
# ==> [1, 3, 2, 1]
