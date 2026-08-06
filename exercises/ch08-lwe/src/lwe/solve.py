"""Noise-free Gaussian elimination over Z_q.

``gaussian_eliminate_mod_q(A, b, q)`` solves the linear system
``A @ s = b (mod q)`` for s in Z_q^n, given an m x n matrix A with
m >= n and a right-hand side b of length m.

The algorithm is textbook Gauss with two changes:

- division is multiplication by a modular inverse, computed via the
  extended Euclidean algorithm (pow(x, -1, q) in Python 3.8+)
- after forward elimination on the first n rows we also check that
  the remaining m - n rows of the reduced system are consistent
  (zero = zero); if not, the function returns None

When the system is exact (the target b equals A @ s with no added
error), the function recovers s exactly. When b = A @ s + e with a
nonzero error e and m > n, the consistency check on the remaining
m - n rows almost always fails and the function returns None. When
m == n there are no consistency rows, so on a noisy square system
the function returns a plausible-looking wrong secret with no
signal of failure. That is the point of Chapter 8's
noise-makes-LWE-hard demonstration: the same algorithm that
trivially solves the clean system breaks on the noisy one, loudly
when m > n and silently when m == n.

For modular inversion to work, q must be such that every pivot element
encountered is a unit in Z_q. When q is prime every nonzero element is
a unit, so the function is guaranteed to make progress. For composite
q it can fail on a bad pivot; the test suite uses q = 97 (prime) so
the guarantee holds.
"""

from __future__ import annotations

import numpy as np


def _mod_inv(a: int, q: int) -> int:
    """Modular inverse of a mod q, via Python's built-in pow."""
    return pow(int(a) % q, -1, q)


def gaussian_eliminate_mod_q(
    A: np.ndarray,
    b: np.ndarray,
    q: int,
) -> np.ndarray | None:
    """Solve A @ s = b (mod q) for s in Z_q^n, or return None on failure.

    Returns the unique s in Z_q^n when the noise-free system has a
    solution, and None when the system is inconsistent (which is what
    happens once noise is added to a clean LWE instance).
    """
    A = np.asarray(A, dtype=np.int64).copy() % q
    b = np.asarray(b, dtype=np.int64).copy() % q
    m, n = A.shape
    assert b.shape == (m,), (
        f"gaussian_eliminate_mod_q: b has shape {b.shape}, expected ({m},)"
    )
    assert m >= n, (
        f"gaussian_eliminate_mod_q: need m >= n "
        f"(got m={m}, n={n})"
    )

    # Forward elimination on columns 0 .. n-1 using the first n rows.
    row = 0
    for col in range(n):
        # Find a pivot row at or below ``row`` whose entry in this column
        # is a unit mod q. Because q is assumed prime in the test suite,
        # "unit" here means "nonzero".
        pivot = None
        for r in range(row, m):
            if A[r, col] % q != 0:
                pivot = r
                break
        if pivot is None:
            # The column is zero in every remaining row. The system is
            # rank-deficient; the noise-free LWE recovery story assumes
            # a uniform A with m >= n, which is full-rank with high
            # probability. Return None rather than guessing.
            return None

        # Swap the pivot row into position.
        if pivot != row:
            A[[row, pivot]] = A[[pivot, row]]
            b[row], b[pivot] = int(b[pivot]), int(b[row])

        # Normalize the pivot row so the leading entry is 1.
        inv = _mod_inv(int(A[row, col]), q)
        A[row] = (A[row] * inv) % q
        b[row] = (int(b[row]) * inv) % q

        # Eliminate the pivot column in every other row.
        for r in range(m):
            if r == row:
                continue
            factor = int(A[r, col]) % q
            if factor == 0:
                continue
            A[r] = (A[r] - factor * A[row]) % q
            b[r] = (int(b[r]) - factor * int(b[row])) % q

        row += 1

    # Consistency check: rows n .. m-1 of the reduced A are now zero, so
    # the corresponding entries of b must also be zero for a solution to
    # exist. This is the test that noise breaks.
    for r in range(n, m):
        if int(b[r]) % q != 0:
            return None

    # The first n rows of A are the identity on the first n columns, so
    # the first n entries of b are the recovered secret.
    s = b[:n].copy() % q
    return s
