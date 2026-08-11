# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 23: SQIsign in a toy setting
# Section: "BFS over the isogeny graph"
# https://book.encryptorium.com/part-4-code-isogeny/ch23-sqisign-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch23/05-fp2-add.py

from collections import deque

p = 431

def fp2_add(x, y, p):
    return ((x[0]+y[0]) % p, (x[1]+y[1]) % p)
def fp2_sub(x, y, p):
    return ((x[0]-y[0]) % p, (x[1]-y[1]) % p)
def fp2_mul(x, y, p):
    return ((x[0]*y[0]-x[1]*y[1]) % p, (x[0]*y[1]+x[1]*y[0]) % p)
def fp2_inv(x, p):
    n = (x[0]*x[0]+x[1]*x[1]) % p
    inv = pow(n, -1, p)
    return ((x[0]*inv) % p, ((-x[1])*inv) % p)
def fp2_sqr(x, p):
    return ((x[0]*x[0]-x[1]*x[1]) % p, (2*x[0]*x[1]) % p)
def fp2_neg(x, p):
    return ((-x[0]) % p, (-x[1]) % p)

def j_invariant(a, b, p):
    a3 = fp2_mul(fp2_sqr(a, p), a, p)
    four_a3 = ((4*a3[0]) % p, (4*a3[1]) % p)
    b2 = fp2_sqr(b, p)
    den = fp2_add(four_a3, ((27*b2[0]) % p, (27*b2[1]) % p), p)
    return fp2_mul(((1728*four_a3[0]) % p, (1728*four_a3[1]) % p), fp2_inv(den, p), p)

a0, b0 = (1, 0), (0, 0)
print(j_invariant(a0, b0, p))
# ==> (4, 0)
