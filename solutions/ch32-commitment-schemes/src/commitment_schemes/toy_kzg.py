"""Toy KZG-like polynomial commitment for Chapter 32.

This module implements a pedagogical single-group KZG sketch. It is not
a working KZG implementation: real KZG requires a pairing-friendly
bilinear group and two source groups, neither of which is built here.
The purpose of this module is to expose the attack surface that Shor's
algorithm targets, which is the trapdoor tau embedded in the structured
reference string.

Trapdoor tau is chosen at setup. The SRS is (g^(tau^0), g^(tau^1), ...,
g^(tau^d)) in a prime-order subgroup of F_p^*. A classical verifier
cannot recover tau from the SRS because discrete logarithm is
classically hard. A quantum adversary solves discrete logarithm via
Shor's algorithm and recovers tau directly, then forges openings
consistent with any evaluation claim. Binding under the d-SDH
assumption collapses to the standard discrete logarithm assumption,
which Shor breaks.

Verification in production KZG uses the pairing equation
e(C - [y]_1, [1]_2) == e(W, [tau]_2 - [z]_2). Since this toy does not
build pairings, verification is implemented as a trapdoor-privileged
check: given tau, the check recomputes the commitment equation
directly in the group. This is pedagogically acceptable because once
Shor recovers tau, the quantum adversary is in the same position as
the trapdoor-privileged oracle, and the forge_opening routine below
exhibits the full binding break.

Parameters use the safe-prime structure p = 2*q + 1 with q prime, so
exponent arithmetic lives in F_q for a prime q = 1013. Coefficients of
the committed polynomial are also elements of F_q. This alignment
between the field of coefficients and the exponent ring is what
production KZG achieves via a pairing-friendly curve with a prime-order
subgroup.
"""

from __future__ import annotations

from dataclasses import dataclass


# Safe-prime structure: DEFAULT_PRIME = 2 * DEFAULT_ORDER + 1 with both
# DEFAULT_ORDER and DEFAULT_PRIME prime. The multiplicative subgroup of
# order DEFAULT_ORDER admits prime-order exponent arithmetic (every
# nonzero exponent is invertible mod DEFAULT_ORDER), which matches the
# structure of a real KZG curve.
DEFAULT_PRIME = 2027
DEFAULT_ORDER = 1013
DEFAULT_GENERATOR = 4  # has order 1013 in F_2027^* (= 2^2 mod 2027).


@dataclass
class SRS:
    """Structured reference string for the toy KZG-like commitment.

    ``powers[i]`` equals ``g^(tau^i) mod prime`` for i in 0..degree,
    with the exponent ``tau^i`` reduced modulo the subgroup order.
    ``prime`` is the field modulus; ``order`` is the prime order of the
    multiplicative subgroup that ``generator`` spans.
    """

    prime: int
    order: int
    generator: int
    powers: list[int]


def setup(
    degree: int,
    tau: int,
    prime: int = DEFAULT_PRIME,
    order: int = DEFAULT_ORDER,
    generator: int = DEFAULT_GENERATOR,
) -> SRS:
    """Build an SRS of length ``degree + 1`` from the trapdoor ``tau``.

    In production, tau is generated in a trusted-setup ceremony and
    then destroyed. In this toy, tau is passed explicitly so the
    attack path is visible. Raises ValueError for invalid inputs
    (negative degree, tau outside the prime-order exponent range).
    """
    if degree < 0:
        raise ValueError("degree must be non-negative")
    if tau <= 0 or tau >= order:
        raise ValueError("tau must be in [1, order - 1]")

    powers: list[int] = []
    tau_power = 1
    for _ in range(degree + 1):
        powers.append(pow(generator, tau_power, prime))
        tau_power = (tau_power * tau) % order
    return SRS(prime=prime, order=order, generator=generator, powers=powers)


def eval_poly(coeffs: list[int], x: int, order: int) -> int:
    """Horner-rule evaluation of a polynomial modulo ``order``.

    Coefficients and evaluation points live in F_order (the exponent
    ring of the commitment's prime-order subgroup). The result is the
    F_order element p(x) mod order.
    """
    result = 0
    for c in reversed(coeffs):
        result = (result * x + c) % order
    return result


def commit(coeffs: list[int], srs: SRS) -> int:
    """Commit to a polynomial p(x) = sum(coeffs[i] * x^i).

    The commitment is g^p(tau) mod prime, computed as
    prod(SRS[i]^coeffs[i]) mod prime without revealing tau. Raises
    ValueError if the polynomial degree exceeds the SRS capacity.
    """
    if len(coeffs) > len(srs.powers):
        raise ValueError("polynomial degree exceeds SRS")
    result = 1
    for c, power in zip(coeffs, srs.powers):
        result = (result * pow(power, c, srs.prime)) % srs.prime
    return result


def quotient(coeffs: list[int], z: int, order: int) -> list[int]:
    """Compute q(x) = (p(x) - p(z)) / (x - z) in F_order[x].

    The remainder p(x) mod (x - z) is p(z); the quotient has degree one
    less than p. Coefficients and z live in F_order. Raises ValueError
    on an empty coefficient list.
    """
    if len(coeffs) == 0:
        raise ValueError("coefficient list must be non-empty")
    degree = len(coeffs) - 1
    q: list[int] = [0] * degree
    carry = 0
    for i in range(degree, 0, -1):
        carry = (coeffs[i] + carry * z) % order
        q[i - 1] = carry
    return q


def open_at(coeffs: list[int], z: int, srs: SRS) -> tuple[int, int]:
    """Open the commitment at evaluation point ``z`` in F_order.

    Returns ``(y, witness)`` where ``y = p(z) mod order`` and
    ``witness`` is the commitment to the quotient polynomial
    q(x) = (p(x) - y) / (x - z).
    """
    y = eval_poly(coeffs, z, srs.order)
    q = quotient(coeffs, z, srs.order)
    witness = commit(q, srs)
    return y, witness


def verify_with_trapdoor(
    commitment: int,
    z: int,
    y: int,
    witness: int,
    srs: SRS,
    tau: int,
) -> bool:
    """Trapdoor-privileged verification (pedagogical toy only).

    Real KZG verifies via the pairing equation
    e(C - [y]_1, [1]_2) == e(W, [tau]_2 - [z]_2). This toy does not
    build pairings, so we substitute a check that uses tau directly:
    given tau, recompute g^(p(tau)) = g^y * g^(q(tau) * (tau - z)) and
    compare against the prover's commitment. A production deployment
    would never expose tau; this routine exists only to demonstrate
    correctness and to anchor the attack described in
    ``forge_opening``.
    """
    prime = srs.prime
    order = srs.order
    g = srs.generator

    lhs = (commitment * pow(g, (-y) % order, prime)) % prime
    rhs = pow(witness, (tau - z) % order, prime)
    return lhs == rhs


def shor_recover_tau(srs: SRS) -> int:
    """Simulated Shor attack: recover tau from ``(g, g^tau)``.

    Shor's algorithm solves discrete logarithm in polynomial quantum
    time. In this toy, we recover tau by brute-force search over
    ``[1, order - 1]``, which is tractable for
    ``DEFAULT_ORDER = 1013``. The resulting tau is the same value a
    quantum adversary obtains; the simulation substitutes classical
    brute force for the quantum subroutine without changing the
    attack's output.
    """
    if len(srs.powers) < 2:
        raise ValueError("SRS must have at least g and g^tau")
    g = srs.generator
    g_tau = srs.powers[1]
    prime = srs.prime
    order = srs.order
    for candidate in range(1, order):
        if pow(g, candidate, prime) == g_tau:
            return candidate
    raise ValueError("tau not recoverable (SRS inconsistent)")


def forge_opening(
    commitment: int,
    z: int,
    y_fake: int,
    srs: SRS,
    tau: int,
) -> int:
    """Forge an opening ``(y_fake, W)`` given the trapdoor.

    For any commitment C and any chosen evaluation ``(z, y_fake)`` with
    ``z != tau``, compute W such that the pairing equation (or its
    trapdoor-privileged substitute) accepts. With tau known,
    W = (C * g^{-y_fake})^{1 / (tau - z)} in the group. A classical
    adversary cannot compute this inverse exponent because tau is
    unknown; a Shor-capable adversary recovers tau and then forges at
    will, which is the exact sense in which KZG is Shor-broken.

    Edge case: at z == tau the formula divides by zero. The verification
    equation at that point reduces to ``commitment == g^y``, which
    forces y to equal p(tau); no arbitrary y_fake is acceptable at
    z = tau. Raises ValueError to surface the case rather than
    silently producing nonsense; the forger picks any z != tau.
    """
    prime = srs.prime
    order = srs.order
    g = srs.generator

    if (tau - z) % order == 0:
        raise ValueError(
            "z == tau mod order: forgery formula is undefined; "
            "verification forces y = p(tau) and no y_fake is accepted"
        )

    numerator = (commitment * pow(g, (-y_fake) % order, prime)) % prime
    inv_tz = pow((tau - z) % order, -1, order)
    return pow(numerator, inv_tz, prime)
