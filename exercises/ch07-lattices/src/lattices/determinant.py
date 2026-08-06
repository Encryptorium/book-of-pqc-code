"""Lattice determinant.

The determinant of a full-rank lattice L is |det B| for any basis B
of L. The value is basis-invariant because two bases B_1 and B_2 of
the same lattice are related by a unimodular integer matrix U with
det U = +/-1, so det B_2 = det B_1 * det U and |det B_2| = |det B_1|.

This module computes the determinant as an integer for small
pedagogical examples. For larger matrices the numpy float
determinant is rounded to the nearest integer; Ch 7 stays well
inside the range where that rounding is harmless.
"""

from __future__ import annotations

import numpy as np

from .lattice import Lattice


def _basis_matrix(lattice_or_basis) -> np.ndarray:
    if isinstance(lattice_or_basis, Lattice):
        return lattice_or_basis.basis
    return np.asarray(lattice_or_basis, dtype=np.int64)


def det(lattice_or_basis) -> int:
    """Return |det B| as a non-negative Python int.

    Accepts either a Lattice instance or a raw numpy/array-like basis.
    """
    # EXERCISE: implement this function.
    #
    # Take the numpy determinant of the basis as a float, round to the
    # nearest integer, and return the absolute value as a Python int. The
    # absolute value is what makes the answer a property of the lattice: a
    # unimodular change of basis multiplies the determinant by one or by
    # minus one.
    #
    # Reference: Chapter 7, 'The determinant and the fundamental parallelepiped'
    #
    # Proved by:
    #   tests/ch07/test_determinant.py
    raise NotImplementedError("exercise: det")
