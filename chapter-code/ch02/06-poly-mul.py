# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 2: Mathematical preliminaries
# Section: "Polynomial reduction"
# https://book.encryptorium.com/part-1-foundations/ch02-mathematical-preliminaries/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch02/06-poly-mul.py

def poly_mul(f, g, p):
    result = [0] * (len(f) + len(g) - 1)
    for i, a in enumerate(f):
        for j, b in enumerate(g):
            result[i + j] = (result[i + j] + a * b) % p
    return result

def poly_mod(a, f, p):
    assert f[-1] == 1, "poly_mod requires f to be monic"
    a = [c % p for c in a]
    deg_f = len(f) - 1
    while len(a) - 1 >= deg_f:
        lead = a[-1]
        if lead != 0:
            for i in range(deg_f + 1):
                a[-1 - i] = (a[-1 - i] - lead * f[deg_f - i]) % p
        a.pop()
    return a

# In F_7[x], reduce (1 + x + x^3) * (2 + x^2) modulo x^3 + x + 1.
# Any multiple of the modulus reduces to the zero polynomial.
f_mod = [1, 1, 0, 1]
g = [2, 0, 1]
product = poly_mul(f_mod, g, 7)
print(poly_mod(product, f_mod, 7))
# ==> [0, 0, 0]
