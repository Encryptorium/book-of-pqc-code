# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 31: The four-layer decomposition
# Section: "The four layers in a toy running example"
# https://book.encryptorium.com/part-6-post-quantum-zero-knowledge/ch31-four-layer-decomposition/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch31/01-dot.py

# Block 1: pedagogical slice of the R1CS format used at L1 (stdlib only).
P = 97  # small prime; a real SNARK uses a ~256-bit prime field.

# Columns of z: (one, a, b, a*b, a+b)
#   Constraint 1: (a) * (b) = (a*b)
#   Constraint 2: (a + b) * (1) = (a+b)
A = [[0, 1, 0, 0, 0], [0, 1, 1, 0, 0]]
B = [[0, 0, 1, 0, 0], [1, 0, 0, 0, 0]]
C = [[0, 0, 0, 1, 0], [0, 0, 0, 0, 1]]


def dot(row, z):
    return sum(r * v for r, v in zip(row, z)) % P


def check_r1cs(A, B, C, z):
    for i, (a_row, b_row, c_row) in enumerate(zip(A, B, C)):
        lhs = (dot(a_row, z) * dot(b_row, z)) % P
        rhs = dot(c_row, z)
        if lhs != rhs:
            raise ValueError(f"constraint {i} failed: {lhs} != {rhs}")
    return True


z = (1, 5, 7, 35, 12)  # witness for a=5, b=7
print(check_r1cs(A, B, C, z))
# ==> True
