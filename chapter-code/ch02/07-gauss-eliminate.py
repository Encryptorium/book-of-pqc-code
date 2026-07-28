# The Encryptorium Book of Post-Quantum Cryptography
# Chapter 2: Mathematical preliminaries
# Section: "Gaussian elimination over a finite field"
# https://book.encryptorium.com/part-1-foundations/ch02-mathematical-preliminaries/
#
# Generated from the chapter text. Edits here do not reach the book.
# Run: python3 chapter-code/ch02/07-gauss-eliminate.py

def gauss_eliminate(matrix, p):
    assert p > 1, "p must be prime; this helper does not test primality"
    m = [row[:] for row in matrix]
    rows = len(m)
    cols = len(m[0]) if m else 0
    rank = 0
    for col in range(cols):
        pivot = None
        for r in range(rank, rows):
            if m[r][col] % p != 0:
                pivot = r
                break
        if pivot is None:
            continue
        m[rank], m[pivot] = m[pivot], m[rank]
        # Fermat: for prime p, the inverse of a nonzero element is a^(p-2).
        inv = pow(m[rank][col], p - 2, p)
        m[rank] = [(x * inv) % p for x in m[rank]]
        for r in range(rows):
            if r != rank and m[r][col] % p != 0:
                factor = m[r][col]
                m[r] = [(m[r][c] - factor * m[rank][c]) % p for c in range(cols)]
        rank += 1
    return m, rank

matrix = [
    [1, 2, 3],
    [0, 1, 4],
    [2, 0, 0],
]
reduced, rank = gauss_eliminate(matrix, 5)
for row in reduced:
    print(row)
print("rank =", rank)
# ==> [1, 0, 0]
# ==> [0, 1, 4]
# ==> [0, 0, 0]
# ==> rank = 2
