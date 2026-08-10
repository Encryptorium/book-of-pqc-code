"""Primal attack on Module-LWE via Kannan's embedding.

The primal attack constructs a unique-SVP instance from a Module-LWE
sample and runs BKZ-``beta`` until the unique short vector appears.
The embedding of the sample into a lattice is Kannan's construction
(Kannan 1987): given an LWE instance :math:`(\\mathbf{A}, \\mathbf{b} =
\\mathbf{A} \\mathbf{s} + \\mathbf{e})` with
:math:`\\mathbf{A} \\in \\mathbb{Z}_q^{m \\times n}`, embed into the
lattice

    :math:`\\Lambda = \\{(\\mathbf{x}, y) \\in \\mathbb{Z}^m \\times
    \\mathbb{Z}^{n+1} : (\\mathbf{A} \\,|\\, -\\mathbf{I}_m \\,|\\,
    \\mathbf{b}) \\mathbf{x} = 0 \\bmod q\\}`

of dimension :math:`d = m + n + 1` (for flat LWE) or
:math:`d = m + kn + 1` (for Module-LWE at rank ``k`` with polynomial
degree ``n``). The lattice contains the short vector
:math:`\\mathbf{v} = (\\mathbf{e}, -\\mathbf{s}, 1)` of norm
:math:`\\sqrt{\\zeta^2 (kn + m) + 1}` where :math:`\\zeta` is the
standard deviation of the secret-error coefficients. The chapter
prose uses the sign convention :math:`-\\mathbf{s}` in the middle
block, matching the standard Kannan form.

The success condition for BKZ-``beta`` to find this short vector is
equation 9 of the CRYSTALS-Kyber Round 3 submission (Avanzi et al.
2021, Section 5.1.2):

    :math:`\\zeta \\sqrt{\\beta} \\le \\delta(\\beta)^{2\\beta - d - 1}
    \\cdot q^{m/d}`

where :math:`\\delta(\\beta)` is the root-Hermite-factor from
``core_svp.delta_beta``. The attacker optimizes over ``m`` (the number
of LWE samples used) to minimize the required ``beta``.

This module exposes :func:`primal_beta`, the full optimizer.
"""

from __future__ import annotations

import math

from .core_svp import delta_beta


def primal_success(beta: int, k: int, n: int, q: int, zeta: float, m: int) -> bool:
    """Evaluate the primal-attack success condition at fixed ``(beta, m)``.

    Returns ``True`` iff BKZ-``beta`` is predicted to recover the
    planted short vector from a Module-LWE instance with ``m`` samples,
    dimension ``d = m + k * n + 1``, modulus ``q``, and secret-error
    coefficient standard deviation ``zeta``. The condition is from
    equation 9 of the Kyber Round 3 submission.
    """
    # EXERCISE: implement this function.
    #
    # Set d = m + k * n + 1, the Kannan embedding dimension for a Module-LWE
    # instance of rank k and degree n, and take delta = delta_beta(beta).
    # Return True when log(zeta * sqrt(beta)) is at most (2 * beta - d - 1)
    # * log(delta) + (m / d) * log(q). Stay in log space: at Kyber-scale d
    # both delta ** (2 * beta - d - 1) and q ** (m / d) overflow or
    # underflow a float. Note the exponent 2 * beta - d - 1 is negative in
    # this regime, so raising m helps the attacker through q ** (m / d) and
    # hurts through the growing d.
    #
    # Reference: Chapter 13, 'The primal embedding' (Kyber Round 3 submission, equation 9)
    #
    # Proved by:
    #   tests/ch13/test_primal.py
    raise NotImplementedError("exercise: primal_success")


def primal_beta(k: int, n: int, q: int, zeta: float,
                beta_lo: int = 50, beta_hi: int = 1200,
                m_max: int | None = None) -> tuple[int, int]:
    """Smallest block size for which the primal attack succeeds.

    Searches over ``beta`` in ``[beta_lo, beta_hi]`` and, at each
    block size, over the number of LWE samples ``m`` in
    ``[1, m_max]``. Returns the tuple ``(beta, m_opt)`` where
    ``beta`` is the smallest block size at which some ``m`` satisfies
    the primal-attack success condition and ``m_opt`` is the optimal
    ``m`` for that ``beta``.

    ``m_max`` defaults to ``(k + 1) * n``, which is the ceiling the
    Kyber Round 3 submission uses: the attacker has one ring element
    per row of the public key, plus one from the ciphertext. A scheme
    whose public key is not square in the module needs the ceiling
    stated separately, because the number of unknowns and the number
    of samples then come from different module dimensions. ML-DSA is
    the case in point: its secret is ``ell`` ring elements while
    ``t = A s_1 + s_2`` supplies ``k`` rows, so it calls this function
    with ``k=ell`` and ``m_max=k * n``.
    """
    # EXERCISE: implement this function.
    #
    # Sweep beta upward from beta_lo to beta_hi and, inside each beta, sweep
    # m from 1 to (k + 1) * n, returning (beta, m) at the first pair that
    # satisfies primal_success. Ascending order in both loops is what makes
    # the first hit both the smallest workable block size and the smallest
    # optimal sample count at it, so no explicit minimisation is needed.
    # Raise AssertionError if beta_hi is reached with no hit. The (k + 1) *
    # n ceiling is the number of LWE samples the attacker actually holds:
    # one ring element per public-key row plus one from the ciphertext.
    #
    # Reference: Chapter 13, 'A core-SVP estimator in Python' (Kyber Round 3 submission, Section 5.1.2)
    #
    # Proved by:
    #   tests/ch13/test_primal.py
    #   tests/ch13/test_estimator_table.py
    raise NotImplementedError("exercise: primal_beta")
