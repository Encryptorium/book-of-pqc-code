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
    # EXERCISE: implement this function.
    #
    # Read the dimension n off the input (the number of basis columns, or
    # the Lattice's own dimension), compute the lattice determinant with
    # det, and return sqrt(n) times that determinant raised to the power
    # 1/n.
    #
    # Reference: Chapter 7, 'Successive minima and Minkowski's bound'
    #
    # Proved by:
    #   tests/ch07/test_minkowski.py
    raise NotImplementedError("exercise: minkowski_bound")
