# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 8: The LWE problem
# Section: "Sampling LWE instances in Python"
# https://book.encryptorium.com/part-2-lattices/ch08-the-lwe-problem/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch08/04-sampling-lwe-instances-in-python.py

import numpy as np

q, m, B = 97, 8, 1
rng = np.random.default_rng(seed=1)
raw = rng.integers(low=-B, high=B + 1, size=m, dtype=np.int64)
e = raw % q
print("raw error       =", raw.tolist())
# ==> raw error       = [0, 0, 1, 1, -1, -1, 1, 1]
print("reduced mod q =", e.tolist())
# ==> reduced mod q = [0, 0, 1, 1, 96, 96, 1, 1]
