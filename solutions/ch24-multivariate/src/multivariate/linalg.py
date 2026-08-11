"""Gaussian elimination over GF(q): invertibility, inversion, and solving.

Chapter 24 prints all three of these functions. Signing needs ``solve_linear``
(the oil-vinegar collapse is a linear solve), key generation needs
``is_invertible`` to reject a singular secret transformation, and the signer
needs ``invert_mat`` to map the central-map solution back to public
coordinates.
"""

from .gf import inv

Matrix = list[list[int]]
Vector = list[int]


def is_invertible(A: Matrix, q: int) -> bool:
    """Return True when A is invertible over GF(q).

    Forward elimination only: a pivot missing in some column means a zero
    determinant, which is all the caller needs to know.
    """
    n = len(A)
    mat = [row[:] for row in A]
    for c in range(n):
        p = next((r for r in range(c, n) if mat[r][c] != 0), None)
        if p is None:
            return False
        mat[c], mat[p] = mat[p], mat[c]
        pivot_inv = inv(mat[c][c], q)
        for r in range(c + 1, n):
            if mat[r][c]:
                f = mat[r][c] * pivot_inv % q
                for k in range(c, n):
                    mat[r][k] = (mat[r][k] - f * mat[c][k]) % q
    return True


def invert_mat(A: Matrix, q: int) -> Matrix:
    """Return the inverse of A over GF(q) by Gauss-Jordan elimination.

    Raises AssertionError on a singular matrix; callers are expected to have
    screened with ``is_invertible`` first.
    """
    n = len(A)
    mat = [row[:] + [1 if j == i else 0 for j in range(n)] for i, row in enumerate(A)]
    for c in range(n):
        p = next((r for r in range(c, n) if mat[r][c] != 0), None)
        assert p is not None, "matrix is singular over GF(q); inversion undefined"
        mat[c], mat[p] = mat[p], mat[c]
        pivot_inv = inv(mat[c][c], q)
        for k in range(2 * n):
            mat[c][k] = mat[c][k] * pivot_inv % q
        for r in range(n):
            if r != c and mat[r][c]:
                f = mat[r][c]
                for k in range(2 * n):
                    mat[r][k] = (mat[r][k] - f * mat[c][k]) % q
    return [row[n:] for row in mat]


def solve_linear(A: Matrix, b: Vector, q: int) -> Vector | None:
    """Solve A . x = b over GF(q), or return None when A is singular.

    Returning None rather than raising is what lets the signer resample: a
    singular collapse means this vinegar choice was unlucky, not that the key
    is broken.
    """
    m = len(A)
    aug = [A[i][:] + [b[i]] for i in range(m)]
    for c in range(m):
        p = next((r for r in range(c, m) if aug[r][c] != 0), None)
        if p is None:
            return None
        aug[c], aug[p] = aug[p], aug[c]
        pivot_inv = inv(aug[c][c], q)
        for k in range(m + 1):
            aug[c][k] = aug[c][k] * pivot_inv % q
        for r in range(m):
            if r != c and aug[r][c]:
                f = aug[r][c]
                for k in range(m + 1):
                    aug[r][k] = (aug[r][k] - f * aug[c][k]) % q
    return [aug[i][m] for i in range(m)]
