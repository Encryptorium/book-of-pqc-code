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
    if rng is None:
        rng = random.Random()

    n_minus_k = len(H)
    n = len(H[0])
    k = n - n_minus_k
    all_indices = list(range(n))

    for iteration in range(1, max_iters + 1):
        # Pick a random information set of size k
        I_set = set(rng.sample(all_indices, k))
        J = [j for j in all_indices if j not in I_set]

        # Extract H_J and try to solve
        H_J = _extract_columns(H, J)
        e_J = _gf2_gauss_solve(H_J, list(s))

        if e_J is None:
            continue  # H_J was singular

        if weight(e_J) != target_weight:
            continue

        # Build the full error vector (zeros at information-set positions)
        e = [0] * n
        for idx, j in enumerate(J):
            e[j] = e_J[idx]

        # Verify
        check = mat_vec_mul(H, e)
        if check == list(s):
            return e, iteration

    raise RuntimeError(f"Prange ISD did not converge in {max_iters} iterations")


def isd_cost_estimate(n: int, k: int, w: int) -> float:
    """Expected number of Prange iterations for an [n,k] code with error weight w.

    The success probability per iteration is C(n-w, k) / C(n, k),
    so the expected number of iterations is C(n, k) / C(n-w, k).
    """
    # Use log to avoid overflow for large parameters
    log_cost = (
        sum(math.log2(n - i) for i in range(k))
        - sum(math.log2(n - w - i) for i in range(k))
    )
    return 2 ** log_cost


def isd_exponent(n: int, k: int, w: int) -> float:
    """Return log2 of the expected Prange iteration count."""
    return math.log2(isd_cost_estimate(n, k, w))
