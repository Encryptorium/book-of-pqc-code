"""GF(2) matrix and vector arithmetic using plain Python lists.

Matrices are list[list[int]] (row-major), vectors are list[int].
All arithmetic is mod 2: addition is XOR, multiplication is AND.
"""


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
