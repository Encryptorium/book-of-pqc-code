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
        raw = np.asarray(self.basis)
        rounded = np.round(raw)
        assert np.array_equal(raw, rounded), (
            "Lattice basis must have integer entries (got non-integer values)"
        )
        self.basis = rounded.astype(np.int64)
        assert self.basis.ndim == 2, "Lattice basis must be a 2D matrix"
        n, m = self.basis.shape
        assert n == m, "Lattice requires a square full-rank basis"
        rank = int(np.linalg.matrix_rank(self.basis.astype(float)))
        assert rank == n, f"Lattice basis must be full rank (got rank {rank} in R^{n})"

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
        v = np.asarray(vector, dtype=float)
        coords = np.linalg.solve(self.basis.astype(float), v)
        return bool(np.allclose(coords, np.round(coords), atol=tol))
