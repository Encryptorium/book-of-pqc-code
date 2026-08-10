"""Core-SVP estimator for an ML-KEM parameter set.

The entry point :func:`estimate_parameter_set` takes a Module-LWE
parameter tuple ``(k, n, q, eta_1)`` and returns the primal-attack
block size together with the classical and quantum core-SVP bit
costs. The tuple shape matches the three ML-KEM parameter sets
standardized in FIPS 203 Section 8, so calling this function on
``(k=2, n=256, q=3329, eta_1=3)`` produces ML-KEM-512's security
estimate; ``(3, 256, 3329, 2)`` produces ML-KEM-768's; and
``(4, 256, 3329, 2)`` produces ML-KEM-1024's.

The secret-error standard deviation for a centered binomial
distribution :math:`B_\\eta` is :math:`\\sqrt{\\eta / 2}`. The
primal attack uses the key-generation noise parameter :math:`\\eta_1`
because the short vector the attacker wants is
:math:`(\\mathbf{s}, \\mathbf{e})` with :math:`\\mathbf{s},
\\mathbf{e} \\sim B_{\\eta_1}`.
"""

from __future__ import annotations

import math
from dataclasses import dataclass

from .core_svp import classical_bits, quantum_bits
from .primal import primal_beta


@dataclass(frozen=True)
class CoreSVPEstimate:
    """Primal core-SVP estimate for one Module-LWE parameter set.

    Fields:
        name: human-readable parameter set name.
        beta: primal-attack block size from equation 9 of the Kyber
            Round 3 submission.
        m_opt: optimal number of LWE samples at block size ``beta``.
        d: lattice attack dimension ``m + k * n + 1``.
        classical: classical core-SVP bit cost
            :math:`\\lfloor 0.292 \\cdot \\beta \\rfloor`.
        quantum: quantum core-SVP bit cost
            :math:`\\lfloor 0.265 \\cdot \\beta \\rfloor`.
    """

    name: str
    beta: int
    m_opt: int
    d: int
    classical: int
    quantum: int


def estimate_parameter_set(
    name: str, k: int, n: int, q: int, eta_1: int,
) -> CoreSVPEstimate:
    """Run the core-SVP primal estimator on one Module-LWE parameter set.

    ``name`` is a label for reporting. ``k`` is the Module rank.
    ``n`` is the polynomial ring degree. ``q`` is the modulus.
    ``eta_1`` is the centered-binomial noise parameter for the secret
    and the key-generation error.

    Returns a :class:`CoreSVPEstimate` with the block size, optimal
    sample count, lattice attack dimension, classical bit cost, and
    quantum bit cost.
    """
    # EXERCISE: implement this function.
    #
    # Assert k, n, q, and eta_1 are in range, then derive the secret-error
    # coefficient standard deviation from the centered binomial parameter as
    # zeta = sqrt(eta_1 / 2). Call primal_beta for (beta, m_opt), set d =
    # m_opt + k * n + 1, and pack everything into a frozen CoreSVPEstimate
    # with classical and quantum truncated to int. Use eta_1 and not eta_2:
    # the vector the primal attack plants is (e, -s, 1), and both s and e
    # are drawn at key generation. At eta_1 = 2 this gives zeta = 1 exactly,
    # which is why the ML-KEM-768 walkthrough carries sigma = 1 throughout.
    #
    # Reference: Chapter 13, 'A core-SVP estimator in Python' (FIPS 203 Section 8 parameter sets)
    #
    # Proved by:
    #   tests/ch13/test_estimator_table.py
    raise NotImplementedError("exercise: estimate_parameter_set")


# The three ML-KEM parameter sets from FIPS 203 Section 8. The Kyber
# Round 3 submission changed eta_1 for Kyber-512 from 2 to 3; the
# other two parameter sets have kept eta_1 = 2 since Round 2.
ML_KEM_PARAMETER_SETS: list[tuple[str, int, int, int, int]] = [
    ("ML-KEM-512", 2, 256, 3329, 3),
    ("ML-KEM-768", 3, 256, 3329, 2),
    ("ML-KEM-1024", 4, 256, 3329, 2),
]


def ml_kem_table() -> list[CoreSVPEstimate]:
    """Run :func:`estimate_parameter_set` on all three ML-KEM parameter sets.

    Returns a list of three :class:`CoreSVPEstimate` records in the
    order ML-KEM-512, ML-KEM-768, ML-KEM-1024.
    """
    return [estimate_parameter_set(*row) for row in ML_KEM_PARAMETER_SETS]


def estimate_ml_dsa_set(
    name: str, k: int, ell: int, n: int, q: int, eta: int,
) -> CoreSVPEstimate:
    """Run the same core-SVP primal estimator on an ML-DSA parameter set.

    ML-DSA's key-recovery problem is Module-LWE over
    :math:`R_q = \\mathbb{Z}_{8380417}[x]/(x^{256}+1)` with
    :math:`\\mathbf{t} = \\mathbf{A} \\mathbf{s}_1 + \\mathbf{s}_2` and
    :math:`\\mathbf{A} \\in R_q^{k \\times \\ell}`. Two things differ
    from the ML-KEM shape and both matter to the estimate.

    The module is not square. The unknowns are :math:`\\mathbf{s}_1`,
    which is ``ell`` ring elements, while the samples are the ``k``
    rows of :math:`\\mathbf{t}`, so the embedding dimension is
    ``m + ell * n + 1`` with ``m`` capped at ``k * n``.

    The secret is uniform, not centered binomial. FIPS 204 draws every
    coefficient of :math:`\\mathbf{s}_1` and :math:`\\mathbf{s}_2`
    uniformly from :math:`[-\\eta, \\eta]`, whose variance is
    :math:`\\eta (\\eta + 1) / 3` rather than the
    :math:`\\eta_1 / 2` of ML-KEM's centered binomial.

    Returns a :class:`CoreSVPEstimate` on the same fields as
    :func:`estimate_parameter_set`.
    """
    assert k >= 1, f"estimate_ml_dsa_set: k must be >= 1, got {k}"
    assert ell >= 1, f"estimate_ml_dsa_set: ell must be >= 1, got {ell}"
    assert n >= 1, f"estimate_ml_dsa_set: n must be >= 1, got {n}"
    assert q >= 2, f"estimate_ml_dsa_set: q must be >= 2, got {q}"
    assert eta >= 1, f"estimate_ml_dsa_set: eta must be >= 1, got {eta}"

    zeta = math.sqrt(eta * (eta + 1) / 3.0)
    beta, m_opt = primal_beta(ell, n, q, zeta, m_max=k * n)
    d = m_opt + ell * n + 1
    return CoreSVPEstimate(
        name=name,
        beta=beta,
        m_opt=m_opt,
        d=d,
        classical=int(classical_bits(beta)),
        quantum=int(quantum_bits(beta)),
    )


# The three ML-DSA parameter sets from FIPS 204 Table 1, as
# (name, k, ell, n, q, eta). The modulus is 2**23 - 2**13 + 1.
ML_DSA_PARAMETER_SETS: list[tuple[str, int, int, int, int, int]] = [
    ("ML-DSA-44", 4, 4, 256, 8380417, 2),
    ("ML-DSA-65", 6, 5, 256, 8380417, 4),
    ("ML-DSA-87", 8, 7, 256, 8380417, 2),
]


def ml_dsa_table() -> list[CoreSVPEstimate]:
    """Run :func:`estimate_ml_dsa_set` on all three ML-DSA parameter sets.

    Returns a list of three :class:`CoreSVPEstimate` records in the
    order ML-DSA-44, ML-DSA-65, ML-DSA-87. These price the Module-LWE
    half of ML-DSA only. The forgery side rests on Module-SIS, which
    needs a different success condition and is out of scope here.
    """
    return [estimate_ml_dsa_set(*row) for row in ML_DSA_PARAMETER_SETS]
