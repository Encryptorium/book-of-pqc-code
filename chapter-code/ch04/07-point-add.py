# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 4: From classical to post-quantum
# Section: "Building ECDSA on secp256k1"
# https://book.encryptorium.com/part-1-foundations/ch04-from-classical-to-post-quantum/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch04/07-point-add.py

# Toy curve y^2 = x^3 + 7 over F_97.
P = 97

def point_add(x1, y1, x2, y2):
    lam = (y2 - y1) * pow(x2 - x1, -1, P) % P
    x3 = (lam * lam - x1 - x2) % P
    y3 = (lam * (x1 - x3) - y1) % P
    return (x3, y3)

# Two points on y^2 = x^3 + 7 mod 97: (1, 28) and (5, 36).
# Check they are on the curve.
for (x, y) in [(1, 28), (5, 36)]:
    assert (y * y - x * x * x - 7) % P == 0

x3, y3 = point_add(1, 28, 5, 36)
print(x3, y3)
print((y3 * y3 - x3 * x3 * x3 - 7) % P)
# ==> 95 75
# ==> 0
