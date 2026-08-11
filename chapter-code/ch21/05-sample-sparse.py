# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 21: HQC, a pedagogical implementation
# Section: "Sparse vector sampling"
# https://book.encryptorium.com/part-4-code-isogeny/ch21-hqc-from-scratch/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch21/05-sample-sparse.py

import random

def sample_sparse(n, w, rng):
    positions = rng.sample(range(n), w)
    vec = [0] * n
    for p in positions:
        vec[p] = 1
    return vec

rng = random.Random(42)
v = sample_sparse(83, 3, rng)
support = [i for i, x in enumerate(v) if x]
print("support:", support)
print("weight: ", sum(v))
# ==> support: [3, 14, 81]
# ==> weight:  3
