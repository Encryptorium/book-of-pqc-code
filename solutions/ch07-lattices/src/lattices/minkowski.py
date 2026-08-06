"""Minkowski's bound on the first successive minimum.

For a full-rank lattice L in R^n, let lambda_1(L) be the length
of the shortest nonzero vector in L. Minkowski's theorem bounds
this length by
    lambda_1(L) <= sqrt(n) * det(L)^{1/n}.

The proof uses a pigeonhole argument on the scaled fundamental
parallelepiped and is deferred to Chapter 13. Chapter 7 states
the bound, implements it, and uses it to anchor the reader's
intuition that short vectors in a high-dimensional lattice are
not arbitrary.

This is not the tightest form of Minkowski's bound. The sharper
form replaces the constant sqrt(n) with a lattice-dependent
expression involving the Hermite constant, but the sqrt(n) form
is the one the rest of this book cites.
"""

from __future__ import annotations

import math

from .determinant import det


def minkowski_bound(lattice_or_basis) -> float:
    """Return sqrt(n) * det(L)^{1/n} for the given lattice."""
    from .lattice import Lattice
    import numpy as np

    if isinstance(lattice_or_basis, Lattice):
        n = lattice_or_basis.dimension
    else:
        B = np.asarray(lattice_or_basis)
        assert B.ndim == 2, "minkowski_bound requires a 2D basis matrix"
        n = int(B.shape[1])

    volume = det(lattice_or_basis)
    return math.sqrt(n) * (float(volume) ** (1.0 / n))
