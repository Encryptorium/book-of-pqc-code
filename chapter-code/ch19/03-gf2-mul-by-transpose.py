# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 19: Coding theory for cryptographers
# Section: "The [7,4,3] Hamming code"
# https://book.encryptorium.com/part-4-code-isogeny/ch19-coding-theory-for-cryptographers/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch19/03-gf2-mul-by-transpose.py

# GF(2) matrix product A * B^T where B_rows holds the rows of B.
# Each row of B is a column of B^T, so the (i,j) entry of the product
# is the dot product of A's row i with B's row j, reduced mod 2.
def gf2_mul_by_transpose(A, B_rows):
    return [[sum(a * b for a, b in zip(row_a, row_b)) % 2
             for row_b in B_rows]
            for row_a in A]

G = [
    [1, 0, 0, 0, 1, 1, 0],
    [0, 1, 0, 0, 1, 0, 1],
    [0, 0, 1, 0, 0, 1, 1],
    [0, 0, 0, 1, 1, 1, 1],
]
H = [
    [1, 1, 0, 1, 1, 0, 0],
    [1, 0, 1, 1, 0, 1, 0],
    [0, 1, 1, 1, 0, 0, 1],
]

# Verify the defining relationship: G * H^T = 0.
# Pass H directly: each row of H is a column of H^T.
product = gf2_mul_by_transpose(G, H)
print("G * H^T =", product)
# ==> G * H^T = [[0, 0, 0], [0, 0, 0], [0, 0, 0], [0, 0, 0]]
