"""Linear algebra over F_p: the third setting Chapter 2 defines.

One routine. Gaussian elimination over a field is short because every nonzero
scalar is invertible, so a pivot can always be normalized to 1. Over a ring
that is not a field it stops being short, and the lattice and code-based
chapters each return to row reduction in a more delicate form: Chapter 7 over
the integers, where the invertible scalars are only +1 and -1, and Chapter 19
over GF(2), where the arithmetic collapses to XOR.
"""


def gauss_eliminate(matrix: list[list[int]], p: int) -> tuple[list[list[int]], int]:
    """Return (reduced row echelon form, rank) of matrix over F_p.

    One column at a time: find a row at or below the current pivot row with a
    nonzero entry in this column, swap it up, scale it so the pivot is 1, then
    clear that column from every other row. A column with no available pivot is
    skipped, which is what makes the routine work on rectangular and
    rank-deficient input.

    The rank falls out of the process rather than being computed separately: it
    is the number of pivots placed, which is also the number of nonzero rows in
    the reduced form. Row operations do not change the row space, so that count
    is the dimension of the row space of the original matrix.

    The pivot inverse uses ``pow(a, p - 2, p)`` rather than the extended
    Euclidean ``mod_inv``. For prime p these agree by Fermat's little theorem,
    since a^(p-1) == 1 makes a^(p-2) the inverse of a. The Fermat form is
    shorter when the modulus is known to be prime, which it is here.
    """
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
        inv = pow(m[rank][col], p - 2, p)
        m[rank] = [(x * inv) % p for x in m[rank]]
        for r in range(rows):
            if r != rank and m[r][col] % p != 0:
                factor = m[r][col]
                m[r] = [(m[r][c] - factor * m[rank][c]) % p for c in range(cols)]
        rank += 1
    return m, rank
