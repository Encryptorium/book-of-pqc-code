# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 7: Lattices for programmers
# Section: "Building a lattice in Python"
# https://book.encryptorium.com/part-2-lattices/ch07-lattices-for-programmers/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch07/03-building-a-lattice-in-python.py

import numpy as np

B1 = np.array([[3, 1], [1, 2]], dtype=np.int64)
B2 = np.array([[3, 4], [1, 3]], dtype=np.int64)

# Solve B_1 U = B_2 for U over the rationals; unimodular iff integer and det +/-1.
U = np.linalg.solve(B1.astype(float), B2.astype(float))
U_int = np.round(U).astype(np.int64)

print("U =", U_int.tolist())
# ==> U = [[1, 1], [0, 1]]
print("U is integer?", bool(np.allclose(U, U_int)))
# ==> U is integer? True
print("det U =", int(round(np.linalg.det(U_int.astype(float)))))
# ==> det U = 1
