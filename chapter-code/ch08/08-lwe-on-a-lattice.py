# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 8: The LWE problem
# Section: "LWE on a lattice"
# https://book.encryptorium.com/part-2-lattices/ch08-the-lwe-problem/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch08/08-lwe-on-a-lattice.py

import numpy as np

q = 11
A = np.array([[3], [5], [2]], dtype=np.int64)
m, n = A.shape

# With n = 1, A is a column vector and A[0] = 3 is a unit mod 11.
# Use row 0 as the pivot and construct a basis directly.
inv = pow(int(A[0, 0]), -1, q)
B = np.array([
    [q,                                 0, 0],
    [(-int(A[1, 0]) * inv) % q,         1, 0],
    [(-int(A[2, 0]) * inv) % q,         0, 1],
], dtype=np.int64)

print("basis B =")
# ==> basis B =
print(B)
# ==> [[11  0  0]
# ==>  [ 2  1  0]
# ==>  [ 3  0  1]]

det_B = int(round(np.linalg.det(B.astype(float))))
print("|det B| =", abs(det_B))
# ==> |det B| = 11
print("q^n     =", q ** n)
# ==> q^n     = 11

for i, row in enumerate(B):
    r = (A.T @ row) % q
    print(f"A^T @ B[{i}] mod q = {int(r[0])}")
# ==> A^T @ B[0] mod q = 0
# ==> A^T @ B[1] mod q = 0
# ==> A^T @ B[2] mod q = 0
