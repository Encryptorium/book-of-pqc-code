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
    """The support-avoidance estimate of Prange iterations for an [n,k] code.

    Counts only whether the chosen information set avoids the error
    support: that happens with probability C(n-w, k) / C(n, k), so the
    estimate is its reciprocal, C(n, k) / C(n-w, k).

    It is an estimate and not the exact expectation of the implemented
    experiment, because it prices every draw as usable. ``prange_isd``
    also spends an iteration on a singular column choice, and singular
    choices are not rare at small n: of the 35 three-column selections
    for the [7,4,3] Hamming code, seven are singular, so a planted
    weight-one error is recovered by 12 of the 35 rather than by the 15
    this formula counts. The exact mean there is 35/12 = 2.92 against
    this estimate's 35/15 = 2.33. The gap does not close at cryptographic
    parameters: for a uniform square binary matrix the probability of
    invertibility tends to prod_{i>=1} (1 - 2^-i) = 0.288788..., so the
    omitted factor tends to about 3.46, or about 1.79 bits. The Classic
    McEliece security guide (section 3.2) states that 0.29 and applies
    the corresponding correction. It is a constant factor, which is why
    the asymptotic exponent can still be quoted from this estimate; it
    is not a vanishing one.
    """
    # EXERCISE: implement this function.
    #
    # Return C(n, k) / C(n - w, k), the reciprocal of the per-iteration
    # success probability. Compute it in the log domain and exponentiate at
    # the end: the falling factorials cancel the factorials, so the log is
    # sum(log2(n - i) for i in range(k)) minus sum(log2(n - w - i) for i in
    # range(k)). Work in logs not because math.comb cannot cope, since
    # C(3488, 2720) has only 797 decimal digits, but because the falling
    # factorials cancel term by term there, the arithmetic happens in the
    # bits the answer is quoted in, and no large intermediate is built at
    # any parameter set. At n = 3488, k = 2720, w = 64 the answer is about
    # 2^142.8.
    #
    # Reference: Chapter 19, 'Prange information-set decoding'
    #
    # Proved by:
    #   tests/ch19/test_isd_prange.py
    raise NotImplementedError("exercise: isd_cost_estimate")


def isd_exponent(n: int, k: int, w: int) -> float:
    """Return log2 of the expected Prange iteration count."""
    return math.log2(isd_cost_estimate(n, k, w))
