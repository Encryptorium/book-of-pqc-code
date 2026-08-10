"""Prange information-set decoding and ISD cost estimation.

Prange's algorithm (1962) is the simplest ISD variant.  Given an
(n-k)-by-n parity-check matrix H and a target syndrome s, it repeatedly:

  1. Pick a random set I of k column indices (the "information set").
  2. Let J = {0, ..., n-1} \\ I be the remaining n-k indices.
  3. Extract H_J (the (n-k)-by-(n-k) submatrix of columns in J).
  4. If H_J is invertible over GF(2), solve H_J * e_J = s.
  5. If wt(e_J) equals the target weight w, output e (with zeros at I).

Expected iterations: C(n, k) / C(n-w, k).
"""

import math
import random

from coding_theory.gf2 import mat_vec_mul, weight


def _extract_columns(H: list[list[int]], cols: list[int]) -> list[list[int]]:
    """Extract a submatrix of H consisting of the given columns."""
    return [[H[r][c] for c in cols] for r in range(len(H))]


def _gf2_gauss_solve(A: list[list[int]], b: list[int]) -> list[int] | None:
    """Solve A * x = b over GF(2) by Gaussian elimination.

    Returns x if A is invertible, None otherwise.  Modifies copies of A and b.
    """
    n = len(A)
    # Augmented matrix
    aug = [row[:] + [b[i]] for i, row in enumerate(A)]

    # Forward elimination
    for col in range(n):
        pivot = None
        for row in range(col, n):
            if aug[row][col] == 1:
                pivot = row
                break
        if pivot is None:
            return None
        aug[col], aug[pivot] = aug[pivot], aug[col]
        for row in range(n):
            if row != col and aug[row][col] == 1:
                aug[row] = [(a ^ b_) for a, b_ in zip(aug[row], aug[col])]

    return [aug[i][n] for i in range(n)]


def prange_isd(
    H: list[list[int]],
    s: list[int],
    target_weight: int,
    max_iters: int = 100_000,
    rng: random.Random | None = None,
) -> tuple[list[int], int]:
    """Run Prange ISD to find e with H * e^T = s and wt(e) = target_weight.

    Returns (error_vector, iterations_used).
    Raises RuntimeError if max_iters is exceeded.
    """
    # EXERCISE: implement this function.
    #
    # Loop up to max_iters times. Each iteration samples k column indices as
    # the information set I, takes the remaining n - k indices as J in
    # ascending order, extracts the square submatrix H_J with
    # _extract_columns, and asks _gf2_gauss_solve for e_J. Skip the
    # iteration when the solve returns None, meaning H_J was singular, and
    # skip it when the weight of e_J is not the target. Otherwise scatter
    # e_J back into a length-n zero vector at the positions of J, leaving
    # zeros on I, verify H * e^T equals s, and return the vector with the
    # iteration count. Raise RuntimeError if the loop runs out. The
    # algorithm wins only when the sampled information set happens to miss
    # all w error positions, which is where the C(n, k) / C(n - w, k)
    # expected iteration count comes from.
    #
    # Reference: Chapter 19, 'Prange information-set decoding'
    #
    # Proved by:
    #   tests/ch19/test_isd_prange.py
    raise NotImplementedError("exercise: prange_isd")


def isd_cost_estimate(n: int, k: int, w: int) -> float:
    """Expected number of Prange iterations for an [n,k] code with error weight w.

    The success probability per iteration is C(n-w, k) / C(n, k),
    so the expected number of iterations is C(n, k) / C(n-w, k).
    """
    # EXERCISE: implement this function.
    #
    # Return C(n, k) / C(n - w, k), the reciprocal of the per-iteration
    # success probability. Compute it in the log domain and exponentiate at
    # the end: the falling factorials cancel the factorials, so the log is
    # sum(log2(n - i) for i in range(k)) minus sum(log2(n - w - i) for i in
    # range(k)). Going through math.comb directly would build integers with
    # hundreds of thousands of digits at Classic McEliece parameters. At n =
    # 3488, k = 2720, w = 64 the answer is about 2^142.8.
    #
    # Reference: Chapter 19, 'Prange information-set decoding'
    #
    # Proved by:
    #   tests/ch19/test_isd_prange.py
    raise NotImplementedError("exercise: isd_cost_estimate")


def isd_exponent(n: int, k: int, w: int) -> float:
    """Return log2 of the expected Prange iteration count."""
    return math.log2(isd_cost_estimate(n, k, w))
