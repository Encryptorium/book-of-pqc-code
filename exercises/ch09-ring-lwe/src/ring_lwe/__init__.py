"""Chapter 9: Ring-LWE and Module-LWE.

A pedagogical Python package for the polynomial-ring variants of
the learning with errors problem: R_q = Z_q[x]/(x^n + 1) with n a
power of two, schoolbook negacyclic multiplication, the negacyclic
number theoretic transform at any prime q with 2n | q - 1, and
sampling routines for Ring-LWE and Module-LWE instances. The
inline numpy code blocks of Chapter 9 are a simplified slice of
these functions. Chapters 10 and 11 rebuild these ideas rather
than import them: each ships its own package (regev_pke, mlkem),
and nothing outside tests/ch09/ imports ring_lwe.
"""

from .params import RingParams, ModuleParams
from .ring import ring_add, ring_mul_naive
from .ntt import ntt_forward, ntt_inverse, ring_mul_ntt, primitive_2n_root
from .sample import (
    sample_ring_secret,
    sample_ring_error,
    sample_ring_uniform,
    sample_ring_lwe,
    sample_module_lwe,
)

__all__ = [
    "RingParams",
    "ModuleParams",
    "ring_add",
    "ring_mul_naive",
    "ntt_forward",
    "ntt_inverse",
    "ring_mul_ntt",
    "primitive_2n_root",
    "sample_ring_secret",
    "sample_ring_error",
    "sample_ring_uniform",
    "sample_ring_lwe",
    "sample_module_lwe",
]
