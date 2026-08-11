# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 22: Isogenies for programmers
# Section: "A first isogeny"
# https://book.encryptorium.com/part-4-code-isogeny/ch22-isogenies-for-programmers/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch22/02-point-add.py

p = 431
a, b = 1, 0

def point_add(P, Q, a, p):
    if P is None: return Q
    if Q is None: return P
    x1, y1 = P; x2, y2 = Q
    if x1 == x2:
        if (y1 + y2) % p == 0: return None
        lam = (3*x1*x1 + a) * pow(2*y1, -1, p) % p
    else:
        lam = (y2 - y1) * pow(x2 - x1, -1, p) % p
    x3 = (lam*lam - x1 - x2) % p
    y3 = (lam*(x1 - x3) - y1) % p
    return (x3, y3)

def scalar_mul(k, P, a, p):
    R = None
    while k:
        if k & 1: R = point_add(R, P, a, p)
        P = point_add(P, P, a, p)
        k >>= 1
    return R

def j_inv(a, b, p):
    num = 4 * pow(a, 3, p) % p
    denom = (num + 27 * pow(b, 2, p)) % p
    return 1728 * num * pow(denom, -1, p) % p

G = (13, 290)

# 3-torsion point: 144*G has order 3 (since 432/3 = 144).
P3 = scalar_mul(144, G, a, p)
print(f"P3 = {P3}")
# ==> P3 = (261, 309)
print(f"3*P3 = {scalar_mul(3, P3, a, p)}")
# ==> 3*P3 = None

# Degree-3 isogeny via the Velu evaluation formula.
kernel_3 = [None, P3, scalar_mul(2, P3, a, p)]
x_new, y_new = G[0], G[1]
for R in kernel_3:
    if R is None: continue
    GpR = point_add(G, R, a, p)
    x_new = (x_new + GpR[0] - R[0]) % p
    y_new = (y_new + GpR[1] - R[1]) % p
phi3_G = (x_new, y_new)
print(f"phi_3(G) = {phi3_G}")
# ==> phi_3(G) = (412, 94)

# Recover the codomain's j-invariant.
P2 = scalar_mul(7, G, a, p)
x2n, y2n = P2[0], P2[1]
for R in kernel_3:
    if R is None: continue
    P2R = point_add(P2, R, a, p)
    x2n = (x2n + P2R[0] - R[0]) % p
    y2n = (y2n + P2R[1] - R[1]) % p
x1, y1 = phi3_G; x2, y2 = x2n, y2n
lhs1 = (y1*y1 - x1**3) % p
lhs2 = (y2*y2 - x2**3) % p
a3 = (lhs1 - lhs2) * pow(x1 - x2, -1, p) % p
b3 = (lhs1 - a3*x1) % p
print(f"j(E_0/<P3>) = {j_inv(a3, b3, p)}")
# ==> j(E_0/<P3>) = 319
