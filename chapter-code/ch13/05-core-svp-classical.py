# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 13: Lattice cryptanalysis
# Section: "From block size to NIST security category"
# https://book.encryptorium.com/part-2-lattices/ch13-lattice-cryptanalysis/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch13/05-core-svp-classical.py

import math


def core_svp_classical(beta):
    return int(0.292 * beta)


def core_svp_quantum(beta):
    return int(0.265 * beta)


rows = [
    ("ML-KEM-512",  406, 1),
    ("ML-KEM-768",  624, 3),
    ("ML-KEM-1024", 874, 5),
]
nist_floor_classical = {1: 143, 3: 207, 5: 272}

print(f"{'name':<12} {'beta':>5} {'classical':>10} {'NIST cat':>9} {'floor':>6}")
# ==> name          beta  classical  NIST cat  floor
for name, beta, cat in rows:
    classical = core_svp_classical(beta)
    floor = nist_floor_classical[cat]
    print(f"{name:<12} {beta:>5} {classical:>10} {cat:>9} {floor:>6}")
# ==> ML-KEM-512     406        118         1    143
# ==> ML-KEM-768     624        182         3    207
# ==> ML-KEM-1024    874        255         5    272
