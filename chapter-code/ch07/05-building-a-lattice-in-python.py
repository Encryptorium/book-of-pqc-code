# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 7: Lattices for programmers
# Section: "Building a lattice in Python"
# https://book.encryptorium.com/part-2-lattices/ch07-lattices-for-programmers/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch07/05-building-a-lattice-in-python.py

import numpy as np

B = np.array([[3, 1], [1, 2]], dtype=float)
D = np.linalg.inv(B).T

# The dual basis is rational; displaying 5 * D shows it as a small integer matrix.
print("5 * D =", np.round(5 * D).astype(np.int64).tolist())
# ==> 5 * D = [[2, -1], [-1, 3]]

# B^T @ D should equal I: every (dual, primal) pair has the right inner product.
identity = B.T @ D
print("B^T @ D rounded =", np.round(identity, 9).tolist())
# ==> B^T @ D rounded = [[1.0, 0.0], [0.0, 1.0]]
