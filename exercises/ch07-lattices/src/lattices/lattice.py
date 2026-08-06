"""The Lattice class.

A full-rank integer lattice L in R^n is the set of integer
combinations of a fixed basis of n linearly independent vectors.
This module represents such a lattice by its basis matrix B,
where the columns of B are the basis vectors and every lattice
point is of the form B @ x for some x in Z^n.

No error handling on degenerate input: if the basis is not
integer or not square full-rank, downstream operations will
fail loudly. That is correct for a pedagogical package.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np


@dataclass
class Lattice:
    """A full-rank integer lattice represented by its basis matrix.

    The basis is stored as an n-by-n numpy integer array. Its columns
    are the basis vectors b_1, ..., b_n, and the lattice is the set
    { B @ x : x in Z^n }.
    """

    basis: np.ndarray

    def __post_init__(self) -> None:
        # EXERCISE: implement this function.
        #
        # Assert that every entry of the supplied basis already equals its
        # rounded value, then store the rounded array as int64. Assert that
        # it is two-dimensional, that it is square, and that its rank equals
        # its dimension, so what the class holds is a full-rank integer
        # basis rather than a degenerate one.
        #
        # Reference: Chapter 7, 'Basis over Z'
        #
        # Proved by:
        #   tests/ch07/test_lattice.py
        raise NotImplementedError("exercise: Lattice.__post_init__")

    @property
    def dimension(self) -> int:
        """The dimension n of the lattice."""
        return int(self.basis.shape[1])

    def point(self, coefficients) -> np.ndarray:
        """Compute the lattice point B @ x for the given integer coefficients."""
        x = np.asarray(coefficients, dtype=np.int64)
        return self.basis @ x

    def contains(self, vector, tol: float = 1e-9) -> bool:
        """Test whether a given real vector is a lattice point.

        A vector v lies in L(B) iff B^{-1} v has integer entries.
        """
        # EXERCISE: implement this function.
        #
        # Solve B c = v for the coordinate vector c over the reals, then
        # report whether every entry of c sits within tol of an integer. A
        # real vector lies in L(B) exactly when its coordinates in the basis
        # are integral, which is why (1, 0) is outside the lattice the
        # chapter starts from.
        #
        # Reference: Chapter 7, 'A lattice two ways'
        #
        # Proved by:
        #   tests/ch07/test_lattice.py
        #   tests/ch07/test_unimodular.py
        raise NotImplementedError("exercise: Lattice.contains")
