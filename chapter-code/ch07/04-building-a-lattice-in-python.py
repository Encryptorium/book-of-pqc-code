# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 7: Lattices for programmers
# Section: "Building a lattice in Python"
# https://book.encryptorium.com/part-2-lattices/ch07-lattices-for-programmers/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch07/04-building-a-lattice-in-python.py

import numpy as np

B1 = np.array([[3, 1], [1, 2]], dtype=np.int64)
U  = np.array([[1, 1], [0, 1]], dtype=np.int64)
B2 = B1 @ U

det_B1 = abs(int(round(np.linalg.det(B1.astype(float)))))
det_B2 = abs(int(round(np.linalg.det(B2.astype(float)))))
print("|det B1| =", det_B1)
# ==> |det B1| = 5
print("|det B2| =", det_B2)
# ==> |det B2| = 5
