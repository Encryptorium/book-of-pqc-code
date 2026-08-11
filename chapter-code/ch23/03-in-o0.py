# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 23: SQIsign in a toy setting
# Section: "The maximal order $\mathcal{O}_0$"
# https://book.encryptorium.com/part-4-code-isogeny/ch23-sqisign-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch23/03-in-o0.py

from fractions import Fraction

def in_O0(x):
    a, b, c, d = x
    u0 = a - c
    u1 = b - d
    u2 = 2 * c
    u3 = 2 * d
    return all(u.denominator == 1 for u in (u0, u1, u2, u3))

# (1 + j) / 2 lies in O_0; j/2 alone does not.
half_one_plus_j = (Fraction(1, 2), Fraction(0), Fraction(1, 2), Fraction(0))
half_j = (Fraction(0), Fraction(0), Fraction(1, 2), Fraction(0))
print(in_O0(half_one_plus_j))
# ==> True
print(in_O0(half_j))
# ==> False

# i and j are also in O_0 (j = 2*(1+j)/2 - 1).
print(in_O0((Fraction(0), Fraction(1), Fraction(0), Fraction(0))))
# ==> True
print(in_O0((Fraction(0), Fraction(0), Fraction(1), Fraction(0))))
# ==> True
