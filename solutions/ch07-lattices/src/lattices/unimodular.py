"""Unimodular change of basis.

Two bases B_1 and B_2 generate the same lattice L iff there is an
integer matrix U with det U = +/-1 (a unimodular matrix) such that
B_2 = B_1 @ U. The proof: any lattice vector B_1 x must also equal
B_2 y for some integer y, so x = U y with U = B_1^{-1} B_2; for U
to map every integer tuple to an integer tuple and back, U and
U^{-1} must both be integer matrices, which happens iff det U is
a unit in Z, namely +/-1.

This module checks whether a given matrix is unimodular and, given
two candidate bases, reports the integer change-of-basis matrix if
the bases generate the same lattice, or None if they do not.
"""

from __future__ import annotations

from typing import Optional

import numpy as np


def is_unimodular(matrix, tol: float = 1e-9) -> bool:
    """True when the input is an integer square matrix with det = +/-1."""
    U = np.asarray(matrix, dtype=float)
    if U.ndim != 2 or U.shape[0] != U.shape[1]:
        return False
    rounded = np.round(U)
    if not np.allclose(U, rounded, atol=tol):
        return False
    d = float(np.linalg.det(rounded))
    return abs(abs(d) - 1.0) < tol


def change_of_basis(b1, b2, tol: float = 1e-9) -> Optional[np.ndarray]:
    """Return the integer matrix U with B_2 = B_1 @ U, or None if no U exists.

    Two bases B_1 and B_2 generate the same lattice iff the returned
    matrix is unimodular, which this function also verifies before
    returning. Callers should treat a None return as "the two bases
    do not generate the same lattice".

    This function assumes both inputs are valid full-rank square bases.
    Passing a singular B_1 is a programming error and will raise
    numpy.linalg.LinAlgError from np.linalg.solve.
    """
    B1 = np.asarray(b1, dtype=float)
    B2 = np.asarray(b2, dtype=float)
    assert B1.shape == B2.shape, "change_of_basis requires same-shape bases"
    assert B1.shape[0] == B1.shape[1], "change_of_basis requires square bases"
    # np.linalg.solve raises LinAlgError on singular B1; we let it propagate.
    U = np.linalg.solve(B1, B2)
    U_int = np.round(U).astype(np.int64)
    if not np.allclose(U, U_int, atol=tol):
        return None
    if not is_unimodular(U_int, tol=tol):
        return None
    return U_int
