# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 22: Isogenies for programmers
# Section: "A first isogeny"
# https://book.encryptorium.com/part-4-code-isogeny/ch22-isogenies-for-programmers/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch22/01-point-add.py

p = 431
a, b = 1, 0  # E_0: y^2 = x^3 + x

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

# The 2-torsion point T = (0, 0): 2T = O since y_T = 0.
T = (0, 0)
print(scalar_mul(2, T, a, p))
# ==> None

# Velu evaluation formula with kernel {O, T}.
G = (13, 290)  # generator of E_0(F_431), order 432
GpT = point_add(G, T, a, p)
phi_G = ((G[0] + GpT[0] - T[0]) % p,
         (G[1] + GpT[1] - T[1]) % p)
print(phi_G)
# ==> (212, 426)

# A second image to recover the codomain y^2 = x^3 + a'x + b'.
P2 = scalar_mul(5, G, a, p)
P2pT = point_add(P2, T, a, p)
phi_P2 = ((P2[0] + P2pT[0] - T[0]) % p,
          (P2[1] + P2pT[1] - T[1]) % p)

# Two points on the codomain give two equations:
#   y_i^2 - x_i^3 = a'*x_i + b'
# Subtract to solve for a'.
x1, y1 = phi_G
x2, y2 = phi_P2
lhs1 = (y1*y1 - x1**3) % p
lhs2 = (y2*y2 - x2**3) % p
a_new = (lhs1 - lhs2) * pow(x1 - x2, -1, p) % p
b_new = (lhs1 - a_new*x1) % p

def j_inv(a, b, p):
    num = 4 * pow(a, 3, p) % p
    denom = (num + 27 * pow(b, 2, p)) % p
    return 1728 * num * pow(denom, -1, p) % p

# j = 1728 * 4a^3 / (4a^3 + 27b^2). Over F_431, 1728 mod 431 = 4.
print(f"j(E_0) = {j_inv(1, 0, p)}")
# ==> j(E_0) = 4
print(f"j(E_0/<T>) = {j_inv(a_new, b_new, p)}")
# ==> j(E_0/<T>) = 4
