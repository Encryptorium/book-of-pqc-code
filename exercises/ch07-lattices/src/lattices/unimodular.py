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
    # EXERCISE: implement this function.
    #
    # Reject anything that is not a square two-dimensional matrix, and
    # reject any matrix whose entries are not all within tol of an integer.
    # Round it and accept only when the absolute value of its determinant is
    # within tol of one.
    #
    # Reference: Chapter 7, 'Unimodular change of basis'
    #
    # Proved by:
    #   tests/ch07/test_unimodular.py
    raise NotImplementedError("exercise: is_unimodular")


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
    # EXERCISE: implement this function.
    #
    # Solve B_1 U = B_2 for U over the reals, letting a singular B_1 raise
    # LinAlgError rather than catching it. Return None when U is not within
    # tol of an integer matrix, and None again when the rounded U fails
    # is_unimodular; otherwise return the rounded integer U. A None answer
    # means the two bases generate different lattices.
    #
    # Reference: Chapter 7, 'Unimodular change of basis'
    #
    # Proved by:
    #   tests/ch07/test_unimodular.py
    raise NotImplementedError("exercise: change_of_basis")
