# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 8: The LWE problem
# Section: "Sampling LWE instances in Python"
# https://book.encryptorium.com/part-2-lattices/ch08-the-lwe-problem/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch08/03-sampling-lwe-instances-in-python.py

import numpy as np

n, q = 4, 97
rng = np.random.default_rng(seed=0)
s = rng.integers(low=0, high=q, size=n, dtype=np.int64)
print("s =", s.tolist())
# ==> s = [82, 61, 49, 26]
