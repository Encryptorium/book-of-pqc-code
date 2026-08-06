# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 7: Lattices for programmers
# Section: "A lattice two ways"
# https://book.encryptorium.com/part-2-lattices/ch07-lattices-for-programmers/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch07/01-lattice-point.py

import numpy as np

# A lattice in Z^2, stored as its basis B with columns b_1, b_2.
B1 = np.array([[3, 1], [1, 2]], dtype=np.int64)
B2 = np.array([[3, 4], [1, 3]], dtype=np.int64)

def lattice_point(B, x):
    return tuple(int(a) for a in B @ np.asarray(x, dtype=np.int64))

print("b_1  =", lattice_point(B1, [1, 0]))
# ==> b_1  = (3, 1)
print("b_2  =", lattice_point(B1, [0, 1]))
# ==> b_2  = (1, 2)
print("b'_2 =", lattice_point(B2, [0, 1]))
# ==> b'_2 = (4, 3)
print("b_1 + b_2 (in L(B1)) =", lattice_point(B1, [1, 1]))
# ==> b_1 + b_2 (in L(B1)) = (4, 3)
