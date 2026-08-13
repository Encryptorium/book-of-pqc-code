# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 32: PQ-secure commitment schemes
# Section: "Lattice PCS: SIS binding, recent literature"
# https://book.encryptorium.com/part-6-post-quantum-zero-knowledge/ch32-commitment-schemes/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch32/05-sample-matrix.py

# Block 5: pedagogical slice of commitment_schemes.lattice_pcs.commit (stdlib only).

import hashlib

MODULUS = 257
DIMENSION = 8
COMMIT_SIZE = 4

def sample_matrix(seed):
    rows, counter, buf = [], 0, b""
    for _ in range(COMMIT_SIZE):
        row = []
        for _ in range(DIMENSION):
            while len(buf) < 4:
                buf += hashlib.sha256(seed + counter.to_bytes(8, "big")).digest()
                counter += 1
            word = int.from_bytes(buf[:4], "big")
            buf = buf[4:]
            row.append(word % MODULUS)
        rows.append(row)
    return rows

def commit_sis(A, m, e):
    C = []
    for row, err in zip(A, e):
        acc = sum(a * mi for a, mi in zip(row, m)) + err
        C.append(acc % MODULUS)
    return C

A = sample_matrix(b"ch32-demo-seed")
m = [3, -2, 1, 0, -4, 2, -1, 5]
e = [1, -1, 0, 2]
C = commit_sis(A, m, e)
print(f"C = {C}")
# ==> C = [67, 146, 188, 205]
