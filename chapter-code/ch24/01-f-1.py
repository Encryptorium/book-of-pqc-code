# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 24: Multivariate signature schemes
# Section: "A worked Oil-Vinegar at GF(7)"
# https://book.encryptorium.com/part-4-code-isogeny/ch24-the-other-families/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch24/01-f-1.py

Q = 7

def F_1(v, o1, o2): return (v*v + v*o1 + 2*v*o2 + 3) % Q
def F_2(v, o1, o2): return (4*v*v + 2*v*o1 + v*o2 + 5) % Q

target = [2, 5]

# Signer picks a vinegar value.
v = 3

# With v fixed, each F_i is linear in (o1, o2). Build the 2x2 coefficient matrix
# and the right-hand side, then solve over GF(7) by Cramer's rule.
A = [[v, 2*v], [2*v, v]]
c = [(v*v + 3) % Q, (4*v*v + 5) % Q]
b = [(target[i] - c[i]) % Q for i in range(2)]

det = (A[0][0]*A[1][1] - A[0][1]*A[1][0]) % Q
assert det != 0, f"singular system for v={v}; pick a different vinegar value"
det_inv = pow(det, Q - 2, Q)   # Fermat inversion: x^(Q-2) == x^(-1) in GF(Q)
o1 = (A[1][1]*b[0] - A[0][1]*b[1]) * det_inv % Q
o2 = (-A[1][0]*b[0] + A[0][0]*b[1]) * det_inv % Q

print("vinegar v =", v)
print("oil (o1, o2) =", (o1, o2))
print("F(v, o1, o2) =", [F_1(v, o1, o2), F_2(v, o1, o2)])
print("target       =", target)
# ==> vinegar v = 3
# ==> oil (o1, o2) = (4, 1)
# ==> F(v, o1, o2) = [2, 5]
# ==> target       = [2, 5]
