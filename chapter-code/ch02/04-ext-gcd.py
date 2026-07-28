# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 2: Mathematical preliminaries
# Section: "The extended Euclidean algorithm"
# https://book.encryptorium.com/part-1-foundations/ch02-mathematical-preliminaries/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch02/04-ext-gcd.py

def ext_gcd(a, b):
    if b == 0:
        return a, 1, 0
    g, x1, y1 = ext_gcd(b, a % b)
    return g, y1, x1 - (a // b) * y1

def mod_inv(a, modulus):
    assert modulus > 1, "modulus must be greater than 1"
    g, x, _ = ext_gcd(a % modulus, modulus)
    assert g == 1, "inverse does not exist: a and modulus share a factor"
    return x % modulus

# Compute 17^-1 modulo 43 and verify the inverse.
inverse = mod_inv(17, 43)
product = (17 * inverse) % 43
print(inverse)
print(product)
# ==> 38
# ==> 1
