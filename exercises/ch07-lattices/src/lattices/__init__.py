"""Chapter 7: Lattices for programmers.

A pedagogical Python package for the algebra of full-rank integer
lattices. Every function in this package is reused by the inline
code blocks of Chapter 7 in simplified form and by Chapters 8, 9,
10, and 11 where the lattice operations return.
"""

from .lattice import Lattice
from .determinant import det
from .dual import dual_basis
from .minkowski import minkowski_bound
from .unimodular import is_unimodular, change_of_basis

__all__ = [
    "Lattice",
    "det",
    "dual_basis",
    "minkowski_bound",
    "is_unimodular",
    "change_of_basis",
]
