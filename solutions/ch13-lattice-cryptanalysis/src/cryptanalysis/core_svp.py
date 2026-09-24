"""Core-SVP cost model for BKZ-based lattice reduction.

The *core-SVP* methodology comes from the security analysis of the
NewHope key exchange (AlkimDucasPoppelmannSchwabe2016, Section 6),
and the CRYSTALS-Kyber submission takes it from there
(KyberRound3Spec, Section 5.1.1). It ignores the polynomial factor
coming from the number of SVP oracle calls that BKZ makes at block
size ``beta``, and takes the cost of a single SVP oracle call inside a
``beta``-dimensional sub-lattice as the cost of the attack, in the
RAM model, where memory access is free.

The BKZ sub-routine is a sieve. The classical exponent is the
heuristic, asymptotic estimate of Becker, Ducas, Gama, and Laarhoven
(2016), time :math:`(3/2)^{\\beta/2 + o(\\beta)} \\approx 2^{0.292 \\beta + o(\\beta)}`,
assuming the sieve's vectors behave as if uniformly distributed on
the sphere. At that running time their GaussSieve variant also uses
:math:`2^{0.292 \\beta + o(\\beta)}` memory, and keeping the time while
cutting memory to :math:`2^{0.208 \\beta + o(\\beta)}` needs the
Nguyen-Vidick sieve (Section 7). Laarhoven's 2015 thesis (Section
14.2.10) applies quantum search to the sieve's nearest-neighbour step
and gets :math:`(13/9)^{\\beta/2 + o(\\beta)} \\approx 2^{0.265 \\beta + o(\\beta)}`,
also heuristic, for a quantum attacker whose search can address the
classical list like RAM (Section 14.1). The earlier paper of
Laarhoven, Mosca and van de Pol (2015) reaches 0.268 at best, under
the same memory assumption (Section 1.5).

The sub-exponential ``o(beta)`` terms are dropped. The Kyber
submission's own account (Section 5.2) is that they were positive in
the experiments that preceded the dimensions-for-free technique, and
that the technique makes their sign unclear, so the headline can move
in either direction: it is a coarse baseline, not a formal lower
bound. The chapter's section on how the estimator oversimplifies
walks how the refined analyses in the literature change the picture.

This file exposes the closed-form exponents and the Chen 2013
root-Hermite-factor :func:`delta_beta`, which is used inside the
primal-attack success condition in ``primal.py``.
"""

from __future__ import annotations

import math


# Classical sieving exponent, the heuristic estimate of
# Becker-Ducas-Gama-Laarhoven 2016. The exact value is
# log_2(sqrt(3/2)) = 0.29248..., and the rounded headline 0.292 is the
# one the Kyber Round 3 submission states.
CLASSICAL_SIEVE_EXPONENT: float = 0.292

# Quantum sieving exponent, log_2(sqrt(13/9)) = 0.26526... rounded, from
# Laarhoven's 2015 thesis (Section 14.2.10), under its assumption of
# quantumly addressable RAM.
QUANTUM_SIEVE_EXPONENT: float = 0.265


def classical_bits(beta: float) -> float:
    """Classical core-SVP bit cost at block size ``beta``.

    Returns :math:`0.292 \\cdot \\beta`. The caller floors or rounds
    the result; the estimator's published tables in the Kyber Round 3
    submission floor.
    """
    assert beta >= 0, f"classical_bits: beta must be non-negative, got {beta}"
    return CLASSICAL_SIEVE_EXPONENT * beta


def quantum_bits(beta: float) -> float:
    """Quantum core-SVP bit cost at block size ``beta``.

    Returns :math:`0.265 \\cdot \\beta`, the exponent Laarhoven's 2015
    thesis (Section 14.2.10) gives for quantum search inside the BDGL
    2016 sieve.
    """
    assert beta >= 0, f"quantum_bits: beta must be non-negative, got {beta}"
    return QUANTUM_SIEVE_EXPONENT * beta


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
