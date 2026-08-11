# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 23: SQIsign in a toy setting
# Section: "Finding a path in the isogeny graph"
# https://book.encryptorium.com/part-4-code-isogeny/ch23-sqisign-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch23/01-fp2-add.py

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

# 2-torsion: roots of x^3 + ax + b = 0 in F_{p^2}.
def two_torsion(a, b, p):
    pts = []
    for x_re in range(p):
        x = (x_re, 0)
        x3 = fp2_mul(fp2_sqr(x, p), x, p)
        rhs = fp2_add(fp2_add(x3, fp2_mul(a, x, p), p), b, p)
        if rhs == (0, 0):
            pts.append((x, (0, 0)))
    if len(pts) < 3:
        for x_re in range(p):
            for x_im in range(1, p):
                x = (x_re, x_im)
                x3 = fp2_mul(fp2_sqr(x, p), x, p)
                rhs = fp2_add(fp2_add(x3, fp2_mul(a, x, p), p), b, p)
                if rhs == (0, 0):
                    pts.append((x, (0, 0)))
                    if len(pts) >= 3:
                        break
            if len(pts) >= 3:
                break
    return pts

a0, b0 = (1, 0), (0, 0)
print(len(two_torsion(a0, b0, p)))
# ==> 3
