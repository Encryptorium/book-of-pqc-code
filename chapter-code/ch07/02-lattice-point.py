# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 7: Lattices for programmers
# Section: "Building a lattice in Python"
# https://book.encryptorium.com/part-2-lattices/ch07-lattices-for-programmers/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch07/02-lattice-point.py

import numpy as np

# The basis B_1 from the start of the chapter, columns are b_1 and b_2.
B1 = np.array([[3, 1], [1, 2]], dtype=np.int64)

def lattice_point(B, x):
    return tuple(int(a) for a in B @ np.asarray(x, dtype=np.int64))

# A handful of lattice points in L(B_1).
print(lattice_point(B1, [ 0,  0]))
# ==> (0, 0)
print(lattice_point(B1, [ 1,  1]))
# ==> (4, 3)
print(lattice_point(B1, [ 2, -1]))
# ==> (5, 0)
print(lattice_point(B1, [-1,  2]))
# ==> (-1, 3)
