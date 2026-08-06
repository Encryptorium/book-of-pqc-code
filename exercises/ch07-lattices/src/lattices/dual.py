"""Dual lattice.

For a full-rank integer lattice L in R^n with basis B, the dual
lattice L* is
    L* = { y in R^n : <y, x> in Z for all x in L }.

Expanding x = B @ k for k in Z^n shows that y in L* iff B^T y is
in Z^n, which is equivalent to saying y is an integer combination
of the columns of (B^T)^{-1} = B^{-T}. So L* is the lattice with
basis B^{-T}.

Two facts matter in the chapter. First, dual-of-dual returns the
original lattice: (B^{-T})^{-T} = B. Second, dual basis is
rational in general, not integer, so the returned matrix is a
float64 array.

No Pontryagin duality here. Chapter 7 uses the computational
definition and nothing more.
"""

from __future__ import annotations

import numpy as np

from .lattice import Lattice


def _basis_matrix(lattice_or_basis) -> np.ndarray:
    if isinstance(lattice_or_basis, Lattice):
        return lattice_or_basis.basis.astype(float)
    return np.asarray(lattice_or_basis, dtype=float)


def dual_basis(lattice_or_basis) -> np.ndarray:
    """Return the dual basis B^{-T} as a float64 numpy array.

    Accepts a Lattice instance or a raw numpy/array-like basis. The
    caller is responsible for the basis being square and invertible;
    on a singular input numpy.linalg.inv raises LinAlgError.
    """
    B = _basis_matrix(lattice_or_basis)
    return np.linalg.inv(B).T
