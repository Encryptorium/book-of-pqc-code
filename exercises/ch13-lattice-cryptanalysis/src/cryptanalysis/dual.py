"""Dual attack on Module-LWE via short vectors of the dual lattice.

The dual attack searches for a short vector :math:`\\mathbf{w}` in the
dual lattice :math:`\\Lambda^* = \\{\\mathbf{x} \\in \\mathbb{Z}^m :
\\mathbf{A}^{\\top} \\mathbf{x} \\equiv \\mathbf{0} \\bmod q\\}`
of a Module-LWE sample. Given such a vector, the attacker computes
:math:`\\langle \\mathbf{w}, \\mathbf{b} \\rangle \\bmod q` for a fresh
sample :math:`(\\mathbf{A}, \\mathbf{b})`. If :math:`\\mathbf{b}` is
uniformly random, the inner product is uniform on
:math:`\\mathbb{Z}_q`. If :math:`\\mathbf{b} = \\mathbf{A}
\\mathbf{s} + \\mathbf{e}` with small error :math:`\\mathbf{e}`, the
inner product is distributed as :math:`\\langle \\mathbf{w},
\\mathbf{e} \\rangle \\bmod q`, which is itself approximately
Gaussian with standard deviation :math:`\\|\\mathbf{w}\\| \\sigma`,
where :math:`\\sigma` is the LWE error standard deviation.

The CRYSTALS-Kyber Round 3 submission (Section 5.1.3) bounds the
distinguishing advantage between LWE and uniform from above by the
maximal variation distance of those two distributions,

    :math:`\\varepsilon \\le 4 \\exp\\!\\left( -2 \\pi^2 \\tau^2
    \\right), \\quad \\tau = \\|\\mathbf{w}\\| \\sigma / q`.

The underlying Gaussian-to-uniform bound is the Albrecht-Player-Scott
2015 result. This module exposes :func:`dual_advantage`, which
evaluates that bound. The full dual-attack success condition also
requires a short-vector length ``l`` that BKZ-``beta`` can reach in
the dual; the advantage bound here is used inside the Chapter 13
"The dual distinguisher" derivation as the "what happens once a short
dual vector is found" step. The bound is meaningful only when below 1; for
:math:`\\|\\mathbf{w}\\| \\sigma` a small fraction of ``q`` the raw
expression exceeds 1, is capped at 1 in interpretation, and stops
being a meaningful quantitative estimate.
"""

from __future__ import annotations

import math


def dual_advantage(w_norm: float, sigma: float, q: int) -> float:
    """Distinguishing-advantage bound from a single short dual vector.

    Returns the Kyber Round 3 submission Section 5.1.3 upper bound on
    the distinguishing advantage between LWE and uniform, given a dual
    lattice vector ``w`` of Euclidean norm ``w_norm``, LWE noise
    standard deviation ``sigma``, and modulus ``q``. The formula is

        :math:`\\varepsilon = 4 \\exp(-2 \\pi^2 (w_\\text{norm}
        \\sigma / q)^2)`.

    The bound is monotonically decreasing in ``w_norm``; finding a
    shorter dual vector makes the distinguisher better. It is a bound,
    not a probability: for a very short ``w`` it exceeds 1, in which
    range it is capped at 1 in interpretation and is no longer a
    meaningful quantitative estimate. The caller is responsible for
    computing ``w_norm`` from a BKZ-``beta`` output via the GSA, if a
    full dual-attack cost estimate is wanted.
    """
    assert w_norm > 0, f"dual_advantage: w_norm must be positive, got {w_norm}"
    assert sigma > 0, f"dual_advantage: sigma must be positive, got {sigma}"
    assert q > 0, f"dual_advantage: q must be positive, got {q}"

    tau = (w_norm * sigma) / q
    return 4.0 * math.exp(-2.0 * math.pi * math.pi * tau * tau)
