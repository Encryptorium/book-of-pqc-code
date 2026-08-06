# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 8: The LWE problem
# Section: "A simple linear system, with a catch"
# https://book.encryptorium.com/part-2-lattices/ch08-the-lwe-problem/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch08/02-solve-2x2-mod-q.py

import numpy as np

q = 17
A = np.array([[3, 5], [2, 1], [7, 4]], dtype=np.int64)
s_true = np.array([4, 7], dtype=np.int64)
b_clean = (A @ s_true) % q
e = np.array([1, 0, -2], dtype=np.int64)
b_noisy = (b_clean + e) % q

def solve_2x2_mod_q(A_top, b_top, q):
    a, b, c, d = (
        int(A_top[0, 0]), int(A_top[0, 1]),
        int(A_top[1, 0]), int(A_top[1, 1]),
    )
    det = (a * d - b * c) % q
    det_inv = pow(det, -1, q)
    adj = np.array([[d, -b], [-c, a]], dtype=np.int64)
    return (det_inv * (adj @ b_top)) % q

s_recovered = solve_2x2_mod_q(A[:2], b_noisy[:2], q)
row3_residual = int((A[2] @ s_recovered - b_noisy[2]) % q)

print("b_noisy =", b_noisy.tolist())
# ==> b_noisy = [14, 15, 3]
print("s_recovered (noisy) =", s_recovered.tolist())
# ==> s_recovered (noisy) = [16, 0]
print("row 3 residual =", row3_residual)
# ==> row 3 residual = 7
