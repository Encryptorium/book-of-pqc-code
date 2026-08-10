"""Core-SVP cost model for BKZ-based lattice reduction.

The NIST Post-Quantum Cryptography project uses the *core-SVP*
methodology, introduced by the NewHope team
(AlkimDucasPoppelmannSchwabe2016, Section 6), to compare submissions
on a common cost scale. The methodology ignores the polynomial factor
coming from the number of SVP oracle calls that BKZ makes at block
size ``beta``, and takes the cost of a single SVP oracle call inside a
``beta``-dimensional sub-lattice as the conservative lower bound on
the attacker's work.

The BKZ sub-routine is a sieve. Becker, Ducas, Gama, and Laarhoven
(2016) showed that the current best classical sieve runs in time
:math:`2^{0.292 \\beta + o(\\beta)}` and memory
:math:`2^{0.208 \\beta + o(\\beta)}`. A Grover speedup due to Laarhoven
brings the classical exponent down to :math:`2^{0.265 \\beta + o(\\beta)}`
in the quantum setting. These two numbers are the core-SVP cost
exponents that every NIST PQC submission has reported since NewHope.

The sub-exponential ``o(beta)`` terms are positive in practice and
would make the attack cost higher, not lower, so the core-SVP
headline is a conservative lower bound on attack cost. The chapter's
meta section walks how the refined analyses in the literature change
the picture.

This file exposes the closed-form exponents and the Chen 2013
root-Hermite-factor :func:`delta_beta`, which is used inside the
primal-attack success condition in ``primal.py``.
"""

from __future__ import annotations

import math


# Classical sieving exponent from Becker-Ducas-Gama-Laarhoven 2016.
# The exact value in the paper is log_2(sqrt(3/2)) = 0.2925..., the
# rounded headline 0.292 is what the Kyber Round 3 submission cites
# and what every other NIST PQC submission uses.
CLASSICAL_SIEVE_EXPONENT: float = 0.292

# Quantum sieving exponent from the Laarhoven Grover speedup.
QUANTUM_SIEVE_EXPONENT: float = 0.265


def classical_bits(beta: float) -> float:
    """Classical core-SVP bit cost at block size ``beta``.

    Returns :math:`0.292 \\cdot \\beta`. The caller floors or rounds
    the result; the estimator's published tables in the Kyber Round 3
    submission floor.
    """
    # EXERCISE: implement this function.
    #
    # Assert beta is non-negative, then return the module constant
    # CLASSICAL_SIEVE_EXPONENT times beta as an unrounded float. The
    # constant is the Becker-Ducas-Gama-Laarhoven 2016 classical sieving
    # exponent, log_2(sqrt(3/2)) rounded to 0.292. Do not floor here: the
    # published Kyber tables floor the product, and rounding twice is where
    # the well-known one-bit ambiguity at ML-KEM-768 comes from.
    #
    # Reference: Chapter 13, 'The four problems and the two tools' (Becker-Ducas-Gama-Laarhoven 2016)
    #
    # Proved by:
    #   tests/ch13/test_core_svp.py
    raise NotImplementedError("exercise: classical_bits")


def quantum_bits(beta: float) -> float:
    """Quantum core-SVP bit cost at block size ``beta``.

    Returns :math:`0.265 \\cdot \\beta` using the Laarhoven speedup of
    the BDGL 2016 sieve.
    """
    # EXERCISE: implement this function.
    #
    # Same shape as classical_bits, but with QUANTUM_SIEVE_EXPONENT, 0.265,
    # the Laarhoven Grover speedup of the nearest-neighbour search inside
    # the BDGL sieve. It is strictly below the classical exponent, so every
    # parameter set reports fewer quantum bits than classical bits at the
    # same block size.
    #
    # Reference: Chapter 13, 'The four problems and the two tools' (Becker-Ducas-Gama-Laarhoven 2016)
    #
    # Proved by:
    #   tests/ch13/test_core_svp.py
    raise NotImplementedError("exercise: quantum_bits")


def delta_beta(beta: int) -> float:
    """Chen 2013 root-Hermite-factor approximation for BKZ-``beta``.

    The root-Hermite factor quantifies how short the first vector of
    the BKZ output basis is relative to the lattice determinant. For
    a lattice of dimension ``d`` and determinant ``Vol``, BKZ-``beta``
    outputs a short vector of norm approximately
    :math:`\\delta^{d-1} \\cdot \\text{Vol}^{1/d}`.

    The Kyber Round 3 submission states this formula in Section 5.1.2
    and cites Chen's 2013 thesis and Albrecht-Player-Scott 2015 for it.
    Its security script computes delta from the same expression:

        delta(beta) = ((pi * beta) ** (1/beta) * beta / (2 * pi * e))
                      ** (1 / (2 * (beta - 1)))

    The formula is an asymptotic approximation; it is accurate to
    roughly one percent for ``beta`` in the range 50 to 1000, and it
    is what NIST PQC submissions use for parameter calibration.
    """
    assert beta >= 2, f"delta_beta: beta must be >= 2, got {beta}"
    numerator = ((math.pi * beta) ** (1.0 / beta)) * beta
    base = numerator / (2.0 * math.pi * math.e)
    return base ** (1.0 / (2.0 * (beta - 1)))
