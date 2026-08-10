"""GF(2) matrix and vector arithmetic using plain Python lists.

Matrices are list[list[int]] (row-major), vectors are list[int].
All arithmetic is mod 2: addition is XOR, multiplication is AND.
"""


def vec_add(a: list[int], b: list[int]) -> list[int]:
    """Componentwise XOR of two binary vectors."""
    return [(x ^ y) for x, y in zip(a, b)]


def weight(v: list[int]) -> int:
    """Hamming weight: number of nonzero entries."""
    # EXERCISE: implement this function.
    #
    # The Hamming weight is the number of nonzero coordinates. Entries here
    # are always 0 or 1, so summing the list counts them; on a vector over a
    # larger alphabet you would have to count nonzeros instead. Weight
    # rather than distance is what pins down d for a linear code: the
    # difference of two codewords is itself a codeword, so the minimum
    # distance equals the minimum weight over the nonzero codewords.
    #
    # Reference: Chapter 19, 'Linear codes over GF(2)'
    #
    # Proved by:
    #   tests/ch19/test_gf2_matmul.py
    raise NotImplementedError("exercise: weight")


def transpose(A: list[list[int]]) -> list[list[int]]:
    """Transpose a matrix."""
    # EXERCISE: implement this function.
    #
    # Return a matrix whose entry (c, r) is the input's entry (r, c). Return
    # an empty list for an empty input rather than indexing A[0] for the
    # column count. Transposition is what lets the chapter's defining
    # relationship G * H^T = 0 be written as a plain matrix product, and it
    # is also how the systematic forms line up: H = [A | I] and G = [I |
    # A^T] use the same block twice.
    #
    # Reference: Chapter 19, 'Linear codes over GF(2)'
    #
    # Proved by:
    #   tests/ch19/test_gf2_matmul.py
    raise NotImplementedError("exercise: transpose")


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
    # EXERCISE: implement this function.
    #
    # Transpose B once so its columns become rows, then the (i, j) entry is
    # the dot product of row i of A with row j of the transpose, mod 2.
    # Doing the transpose up front rather than indexing B[p][j] inside the
    # inner loop keeps the access pattern in row order. The product this
    # package cares about is G * H^T, which is zero for a valid generator
    # and parity-check pair.
    #
    # Reference: Chapter 19, 'Linear codes over GF(2)'
    #
    # Proved by:
    #   tests/ch19/test_gf2_matmul.py
    raise NotImplementedError("exercise: mat_mul")
