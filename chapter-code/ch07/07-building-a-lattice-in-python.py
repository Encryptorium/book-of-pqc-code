# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 7: Lattices for programmers
# Section: "Building a lattice in Python"
# https://book.encryptorium.com/part-2-lattices/ch07-lattices-for-programmers/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch07/07-building-a-lattice-in-python.py

import math
import numpy as np

B = np.array([[3, 1], [1, 2]], dtype=np.int64)
n = B.shape[1]
det_L = abs(int(round(np.linalg.det(B.astype(float)))))
bound = math.sqrt(n) * (det_L ** (1.0 / n))
print("det(L) =", det_L)
# ==> det(L) = 5
print("Minkowski bound =", round(bound, 4))
# ==> Minkowski bound = 3.1623

best_len = float("inf")
best_coef = None
for i in range(-3, 4):
    for j in range(-3, 4):
        if (i, j) == (0, 0):
            continue
        v = B @ np.array([i, j], dtype=np.int64)
        length = float(np.linalg.norm(v))
        if length < best_len:
            best_len = length
            best_coef = (i, j)

v = B @ np.array(best_coef, dtype=np.int64)
print("shortest coefficients:", best_coef)
# ==> shortest coefficients: (-1, 1)
print("shortest vector:", tuple(int(x) for x in v))
# ==> shortest vector: (-2, 1)
print("length =", round(best_len, 4))
# ==> length = 2.2361
