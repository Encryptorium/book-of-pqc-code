"""Chapter 8: The LWE problem.

A pedagogical Python package for the learning with errors (LWE)
problem over Z_q. Chapter 8's inline numpy blocks are simplified
slices of these functions. Chapters 9, 10 and 11 return to LWE
sampling and recovery but rebuild them in their own packages against
their own objects, so nothing outside tests/ch08/ imports this one.
"""

from .params import LWEParams
from .sample import sample_secret, sample_error, sample_lwe, sample_uniform
from .solve import gaussian_eliminate_mod_q
from .qary import qary_lattice_basis

__all__ = [
    "LWEParams",
    "sample_secret",
    "sample_error",
    "sample_lwe",
    "sample_uniform",
    "gaussian_eliminate_mod_q",
    "qary_lattice_basis",
]
