"""The q-ary lattice Lambda_q^perp(A).

Given a matrix A in Z_q^{m x n}, the q-ary lattice

    Lambda_q^perp(A) = { x in Z^m : A^T x = 0 (mod q) }

is the integer lattice of all m-vectors that annihilate every column
of A modulo q. Chapter 8 uses it for the dual attack: a short nonzero
w in Lambda_q^perp(A) gives w^T b = w^T e (mod q) on a true LWE pair,
which has far smaller spread than uniform, while w^T u is uniform on
a uniform pair.

Search LWE embeds into the other q-ary lattice, the primal companion
Lambda_q(A) = A Z^n + q Z^m, which contains the clean vector A @ s.
The observation b = A @ s + e sits at displacement e from a point of
Lambda_q(A), so recovering s is bounded-distance decoding there, not
here. This module builds only Lambda_q^perp(A).

``qary_lattice_basis(A, q)`` returns an integer basis of
Lambda_q^perp(A) as an m x m matrix whose rows are the basis
vectors. For random A over a prime modulus, A^T has full row rank
mod q with high probability, and the construction below succeeds.
"""

from __future__ import annotations

import numpy as np


def qary_lattice_basis(A: np.ndarray, q: int) -> np.ndarray:
    """Return an integer basis of Lambda_q^perp(A) as an m x m matrix.

    The returned matrix ``B`` has rows that are lattice vectors, with
    determinant equal to plus or minus q^n. Every row ``v`` satisfies
    ``A.T @ v = 0 (mod q)``.
    """
    A = np.asarray(A, dtype=np.int64) % q
    m, n = A.shape
    assert m >= n, f"qary_lattice_basis requires m >= n (got m={m}, n={n})"

    # Row-reduce A^T (an n x m matrix) over Z_q to identify pivot columns
    # and express non-pivot columns as linear combinations of pivot ones.
    At = A.T.copy() % q
    pivot_cols: list[int] = []
    row = 0
    for col in range(m):
        if row >= n:
            break
        pivot_row = None
        for r in range(row, n):
            if int(At[r, col]) % q != 0:
                pivot_row = r
                break
        if pivot_row is None:
            continue
        if pivot_row != row:
            At[[row, pivot_row]] = At[[pivot_row, row]]
        inv = pow(int(At[row, col]), -1, q)
        At[row] = (At[row] * inv) % q
        for r in range(n):
            if r == row:
                continue
            factor = int(At[r, col]) % q
            if factor:
                At[r] = (At[r] - factor * At[row]) % q
        pivot_cols.append(col)
        row += 1

    assert row == n, (
        "qary_lattice_basis: A must have full column rank mod q "
        f"(got rank {row}, expected {n})"
    )

    pivot_set = set(pivot_cols)
    free_cols = [c for c in range(m) if c not in pivot_set]
    assert len(pivot_cols) == n and len(free_cols) == m - n

    basis = np.zeros((m, m), dtype=np.int64)

    # First n rows: q * e_{pivot_cols[i]}, putting the pivot coordinates
    # into q Z. These satisfy A^T (q e_c) = q (column c of A^T) = 0 mod q.
    for i, pc in enumerate(pivot_cols):
        basis[i, pc] = q

    # Remaining m - n rows: for each free column fc, the vector v with
    # v[fc] = 1 and v[pivot_cols[r]] = -At[r, fc] (mod q), zero elsewhere.
    # By construction A^T v = 0 mod q, and the resulting basis has
    # determinant plus or minus q^n.
    for j, fc in enumerate(free_cols):
        v = np.zeros(m, dtype=np.int64)
        v[fc] = 1
        for r, pc in enumerate(pivot_cols):
            v[pc] = (-int(At[r, fc])) % q
        basis[n + j] = v

    return basis
