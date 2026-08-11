# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 23: SQIsign in a toy setting
# Section: "Quaternion arithmetic"
# https://book.encryptorium.com/part-4-code-isogeny/ch23-sqisign-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch23/02-quat.py

from fractions import Fraction

p = 431

def quat(a, b, c, d):
    return (Fraction(a), Fraction(b), Fraction(c), Fraction(d))

def quat_add(x, y):
    return (x[0]+y[0], x[1]+y[1], x[2]+y[2], x[3]+y[3])

def quat_neg(x):
    return (-x[0], -x[1], -x[2], -x[3])

def quat_mul(x, y, p):
    a, b, c, d = x
    e, f, g, h = y
    r0 = a*e - b*f - p*c*g - p*d*h
    r1 = a*f + b*e + p*c*h - p*d*g
    r2 = a*g + c*e - b*h + d*f
    r3 = a*h + d*e + b*g - c*f
    return (r0, r1, r2, r3)

def quat_conj(x):
    return (x[0], -x[1], -x[2], -x[3])

def quat_norm(x, p):
    a, b, c, d = x
    return a*a + b*b + p*c*c + p*d*d

i = quat(0, 1, 0, 0)
j = quat(0, 0, 1, 0)
k = quat(0, 0, 0, 1)

print(quat_mul(i, i, p)[0])
# ==> -1
print(quat_mul(j, j, p)[0])
# ==> -431
print(quat_mul(i, j, p))
# ==> (Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(1, 1))
print(quat_mul(j, i, p))
# ==> (Fraction(0, 1), Fraction(0, 1), Fraction(0, 1), Fraction(-1, 1))
print(quat_norm(quat(2, 3, 1, 0), p))
# ==> 444
