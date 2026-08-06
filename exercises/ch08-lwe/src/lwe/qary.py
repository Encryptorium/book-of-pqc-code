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
    # EXERCISE: implement this function.
    #
    # Row-reduce A^T over Z_q and record its pivot columns; there must be
    # exactly n of them, which is the full-column-rank assumption. Build an
    # m by m integer matrix: the first n rows are q times the unit vector at
    # each pivot column, and for each of the m-n free columns fc the
    # remaining rows carry a 1 at fc and the negation of the reduced entry
    # at row r, column fc placed at pivot column r. Every row then
    # annihilates A^T modulo q, and the determinant comes out as q^n up to
    # sign.
    #
    # Reference: Chapter 8, 'LWE on a lattice'
    #
    # Proved by:
    #   tests/ch08/test_qary.py
    raise NotImplementedError("exercise: qary_lattice_basis")
