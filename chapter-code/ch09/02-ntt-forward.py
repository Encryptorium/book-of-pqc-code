# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 9: Ring-LWE and Module-LWE
# Section: "The number theoretic transform"
# https://book.encryptorium.com/part-2-lattices/ch09-ring-lwe-and-module-lwe/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch09/02-ntt-forward.py

import numpy as np

n, q, psi = 4, 17, 2
psi_inv = pow(psi, -1, q)
n_inv = pow(n, -1, q)

def ntt_forward(f):
    fhat = np.zeros(n, dtype=np.int64)
    for k in range(n):
        acc = 0
        for i in range(n):
            acc += int(f[i]) * pow(psi, i * (2 * k + 1), q)
        fhat[k] = acc % q
    return fhat

def ntt_inverse(fhat):
    f = np.zeros(n, dtype=np.int64)
    for j in range(n):
        acc = 0
        for k in range(n):
            acc += int(fhat[k]) * pow(psi_inv, j * (2 * k + 1), q)
        f[j] = (n_inv * acc) % q
    return f

f = np.array([1, 2, 3, 4], dtype=np.int64)
g = np.array([5, 6, 0, 0], dtype=np.int64)
fhat = ntt_forward(f)
ghat = ntt_forward(g)
hhat = (fhat * ghat) % q
h = ntt_inverse(hhat)
print("fhat =", fhat.tolist())
# ==> fhat = [15, 13, 11, 16]
print("ghat =", ghat.tolist())
# ==> ghat = [0, 2, 10, 8]
print("f * g in R_17 via NTT =", h.tolist())
# ==> f * g in R_17 via NTT = [15, 16, 10, 4]
