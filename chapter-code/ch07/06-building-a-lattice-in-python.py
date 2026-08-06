# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 7: Lattices for programmers
# Section: "Building a lattice in Python"
# https://book.encryptorium.com/part-2-lattices/ch07-lattices-for-programmers/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch07/06-building-a-lattice-in-python.py

import numpy as np

B = np.array([[3, 1], [1, 2]], dtype=float)
D  = np.linalg.inv(B).T
DD = np.linalg.inv(D).T
print("dual-of-dual equals B?", bool(np.allclose(DD, B)))
# ==> dual-of-dual equals B? True
