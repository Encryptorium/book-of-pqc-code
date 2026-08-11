"""GF(2) matrix and vector arithmetic using plain Python lists.

Matrices are list[list[int]] (row-major), vectors are list[int].
All arithmetic is mod 2: addition is XOR, multiplication is AND.

Extends the Chapter 19 foundation with Gaussian elimination, matrix
inversion, and random matrix generation for McEliece key generation.
"""

import random


def vec_add(a: list[int], b: list[int]) -> list[int]:
    """Componentwise XOR of two binary vectors."""
    return [(x ^ y) for x, y in zip(a, b)]


def weight(v: list[int]) -> int:
    """Hamming weight: number of nonzero entries."""
    return sum(v)


def transpose(A: list[list[int]]) -> list[list[int]]:
    """Transpose a matrix."""
    if not A:
        return []
    cols = len(A[0])
    return [[A[r][c] for r in range(len(A))] for c in range(cols)]


def identity(n: int) -> list[list[int]]:
    """n-by-n identity matrix over GF(2)."""
    return [[1 if i == j else 0 for j in range(n)] for i in range(n)]


def mat_vec_mul(A: list[list[int]], v: list[int]) -> list[int]:
    """Matrix-vector product A * v over GF(2).

    A is m-by-n, v has length n, result has length m.
    """
    return [sum(a * x for a, x in zip(row, v)) % 2 for row in A]


def mat_mul(A: list[list[int]], B: list[list[int]]) -> list[list[int]]:
    """Matrix product A * B over GF(2).

    A is m-by-p, B is p-by-n, result is m-by-n.
    """
    Bt = transpose(B)
    return [[sum(a * b for a, b in zip(row_a, col_b)) % 2
             for col_b in Bt]
            for row_a in A]


# ── extensions for McEliece ──────────────────────────────────────────

def gauss_systematic(H: list[list[int]]) -> tuple[list[list[int]], list[int]]:
    """Row-reduce H into systematic form [A | I_{n-k}].

    Returns (H_sys, col_perm) where col_perm records the column
    permutation applied.  Raises ValueError if H is not full rank.
    """
    rows = len(H)
    cols = len(H[0])
    M = [list(row) for row in H]
    col_perm = list(range(cols))

    for i in range(rows):
        # find pivot in row i, columns i..cols-1
        pivot = None
        for j in range(i, cols):
            if M[i][j] == 1:
                pivot = j
                break
            for r in range(i + 1, rows):
                if M[r][j] == 1:
                    M[i], M[r] = M[r], M[i]
                    pivot = j
                    break
            if pivot is not None:
                break
        if pivot is None:
            raise ValueError("matrix is not full rank")
        # swap columns i and pivot
        if pivot != i:
            for r in range(rows):
                M[r][i], M[r][pivot] = M[r][pivot], M[r][i]
            col_perm[i], col_perm[pivot] = col_perm[pivot], col_perm[i]
        # eliminate column i in all other rows
        for r in range(rows):
            if r != i and M[r][i] == 1:
                for c in range(cols):
                    M[r][c] ^= M[i][c]

    return M, col_perm


def generator_from_parity(H: list[list[int]]) -> tuple[list[list[int]], list[int]]:
    """Compute generator matrix G from parity-check matrix H.

    Row-reduces H to systematic form [I_{n-k} | B], then
    G = [B^T | I_k] in the permuted coordinate system.
    H_sys * G^T = B + B = 0 over GF(2).

    Returns (G, col_perm).
    """
    H_sys, col_perm = gauss_systematic(H)
    nk = len(H_sys)       # n - k = number of rows
    n = len(H_sys[0])     # code length
    k = n - nk

    # H_sys = [I_{n-k} | B], extract B (nk-by-k) from last k columns
    B = [[H_sys[r][nk + c] for c in range(k)] for r in range(nk)]
    Bt = transpose(B)

    # G = [B^T | I_k], dimensions k-by-n
    Ik = identity(k)
    G = [Bt[r] + Ik[r] for r in range(k)]
    return G, col_perm


def gf2_mat_inv(M: list[list[int]]) -> list[list[int]]:
    """Invert a square GF(2) matrix via Gaussian elimination.

    Raises ValueError if M is singular.
    """
    # EXERCISE: implement this function.
    #
    # Augment M with the identity to width 2n, run Gauss-Jordan on the left
    # half, and return the right half of each row. Pivot selection is the
    # first row at or below i with a 1 in column i; raise ValueError when
    # there is none, because a singular matrix has no inverse. Over GF(2)
    # there is no row-scaling step at all, since the only nonzero value is
    # 1, so elimination reduces to XORing the pivot row into every other row
    # that has a 1 in that column.
    #
    # Reference: Chapter 20, 'The three algorithms: original McEliece-style PKE'
    #
    # Proved by:
    #   tests/ch20/test_mceliece_keygen.py
    #   tests/ch20/test_mceliece_roundtrip.py
    raise NotImplementedError("exercise: gf2_mat_inv")


def random_invertible_matrix(n: int, rng: random.Random) -> list[list[int]]:
    """Sample a random invertible n-by-n matrix over GF(2)."""
    # EXERCISE: implement this function.
    #
    # Sample a random n-by-n matrix of 0s and 1s from the caller's rng, keep
    # it if gf2_mat_inv accepts it, and retry otherwise, giving up with
    # RuntimeError after a bounded number of attempts rather than looping
    # forever. Rejection sampling is enough because a uniform binary matrix
    # is invertible with probability around 0.29 at any sizeable n, so the
    # expected number of attempts is a small constant. This is McEliece's S:
    # multiplying G on the left by an invertible matrix changes the
    # generator basis without changing the code at all.
    #
    # Reference: Chapter 20, 'The three algorithms: original McEliece-style PKE'
    #
    # Proved by:
    #   tests/ch20/test_mceliece_keygen.py
    #   tests/ch20/test_mceliece_roundtrip.py
    raise NotImplementedError("exercise: random_invertible_matrix")


def random_permutation_matrix(n: int, rng: random.Random) -> list[list[int]]:
    """Random n-by-n permutation matrix and its inverse permutation.

    Returns (P, perm) where P is the matrix and perm is the permutation
    as a list: perm[i] = j means column i of the input becomes column j
    of the output.
    """
    # EXERCISE: implement this function.
    #
    # Shuffle list(range(n)) with the caller's rng, then build P with
    # P[i][perm[i]] = 1 and return both the matrix and the permutation.
    # Handing back the permutation as well saves every caller from reading
    # it out of the matrix, and decryption needs to invert it. This is
    # McEliece's P: permuting coordinates produces a permutation-equivalent
    # code that corrects exactly as many errors, while destroying the
    # coordinate ordering Patterson's algorithm depends on.
    #
    # Reference: Chapter 20, 'The three algorithms: original McEliece-style PKE'
    #
    # Proved by:
    #   tests/ch20/test_mceliece_keygen.py
    #   tests/ch20/test_mceliece_roundtrip.py
    raise NotImplementedError("exercise: random_permutation_matrix")
