"""Arithmetic over a prime field GF(q), and the matrix operations UOV needs.

Chapter 24 prints every function in this module. They are collected here so the
rest of the package has one place to call, and so the ``q`` that the chapter
carries as a module-level global becomes an explicit argument.

The field is prime, so inversion is the Fermat power ``x**(q - 2) % q``. Real
UOV parameter sets work over GF(16) and GF(256), where an element is a
polynomial and inversion needs extension-field arithmetic; the toy stays prime
so that a reader can follow every step with integer arithmetic.
"""

Matrix = list[list[int]]
Vector = list[int]


def inv(x: int, q: int) -> int:
    """Return the multiplicative inverse of x in GF(q) for prime q.

    Fermat's little theorem gives x^(q-1) == 1, so x^(q-2) == x^(-1).
    """
    if x % q == 0:
        raise ZeroDivisionError("zero has no inverse in GF(q)")
    return pow(x, q - 2, q)


def matmul(A: Matrix, B: Matrix, q: int) -> Matrix:
    """Multiply two matrices over GF(q)."""
    n, k, m = len(A), len(A[0]), len(B[0])
    return [[sum(A[i][t] * B[t][j] for t in range(k)) % q for j in range(m)] for i in range(n)]


def transpose(A: Matrix) -> Matrix:
    """Return the transpose of A."""
    return [list(row) for row in zip(*A)]


def mat_vec(A: Matrix, v: Vector, q: int) -> Vector:
    """Multiply matrix A by column vector v over GF(q)."""
    return [sum(A[i][k] * v[k] for k in range(len(v))) % q for i in range(len(A))]


def quadratic_eval(Mat: Matrix, x: Vector, q: int) -> int:
    """Evaluate the quadratic form x^T . Mat . x over GF(q).

    Mat is not required to be symmetric. Every ordered pair (i, j) contributes
    ``Mat[i][j] * x[i] * x[j]``, so an asymmetric matrix and its symmetrization
    define the same form only when the field has odd characteristic.
    """
    return sum(Mat[i][j] * x[i] * x[j] for i in range(len(x)) for j in range(len(x))) % q
