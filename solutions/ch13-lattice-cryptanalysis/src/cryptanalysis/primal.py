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
    assert beta >= 2, f"primal_success: beta must be >= 2, got {beta}"
    assert k >= 1, f"primal_success: k must be >= 1, got {k}"
    assert n >= 1, f"primal_success: n must be >= 1, got {n}"
    assert m >= 1, f"primal_success: m must be >= 1, got {m}"
    assert q >= 2, f"primal_success: q must be >= 2, got {q}"
    assert zeta > 0, f"primal_success: zeta must be positive, got {zeta}"

    d = m + k * n + 1
    delta = delta_beta(beta)

    # Right-hand side: GS vector length at rank (d - beta) inside the
    # (d, Vol = q^m) lattice, per the GSA. Taking logs to avoid
    # overflow for large beta and d.
    log_rhs = (2 * beta - d - 1) * math.log(delta) + (m / d) * math.log(q)
    log_lhs = math.log(zeta * math.sqrt(beta))
    return log_lhs <= log_rhs


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
    assert k >= 1, f"primal_beta: k must be >= 1, got {k}"
    assert n >= 1, f"primal_beta: n must be >= 1, got {n}"
    assert q >= 2, f"primal_beta: q must be >= 2, got {q}"
    assert zeta > 0, f"primal_beta: zeta must be positive, got {zeta}"
    assert beta_lo >= 2, f"primal_beta: beta_lo must be >= 2, got {beta_lo}"
    assert beta_lo < beta_hi, f"primal_beta: beta_lo must be < beta_hi, got {beta_lo} and {beta_hi}"

    total_samples = (k + 1) * n if m_max is None else m_max
    assert total_samples >= 1, f"primal_beta: m_max must be >= 1, got {m_max}"
    for beta in range(beta_lo, beta_hi + 1):
        for m in range(1, total_samples + 1):
            if primal_success(beta, k, n, q, zeta, m):
                return beta, m
    raise AssertionError(
        f"primal_beta: no beta in [{beta_lo}, {beta_hi}] satisfies the success "
        f"condition for k={k}, n={n}, q={q}, zeta={zeta}"
    )
