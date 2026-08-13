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
    # EXERCISE: implement this function.
    #
    # Build the SRS as g^(tau^0), g^(tau^1), ..., g^(tau^degree) in the
    # order-1013 subgroup. Carry the exponent tau^i as a running product
    # reduced modulo the subgroup order, not modulo the prime: exponents
    # live in F_order while group elements live in F_prime, and the
    # safe-prime structure p = 2q + 1 is what keeps those two rings aligned.
    # Reject a negative degree and a tau outside [1, order - 1]. In
    # production tau comes out of a trusted-setup ceremony and is destroyed;
    # here it stays a parameter so the attack path is visible.
    #
    # Reference: Chapter 32, 'KZG: trapdoor in the structured reference string'
    #
    # Proved by:
    #   tests/ch32/test_toy_kzg.py
    raise NotImplementedError("exercise: setup")


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
    # EXERCISE: implement this function.
    #
    # C = g^p(tau), computed without ever knowing tau. SRS entry i is
    # already g^(tau^i), so raising entry i to the power coeffs[i] and
    # multiplying the results together gives g^(sum coeffs[i] * tau^i),
    # which is g^p(tau). The commitment is one group element whatever the
    # degree. Reject a polynomial with more coefficients than the SRS has
    # powers rather than zipping the high terms away silently.
    #
    # Reference: Chapter 32, 'KZG: trapdoor in the structured reference string'
    #
    # Proved by:
    #   tests/ch32/test_toy_kzg.py
    raise NotImplementedError("exercise: commit")


def quotient(coeffs: list[int], z: int, order: int) -> list[int]:
    """Compute q(x) = (p(x) - p(z)) / (x - z) in F_order[x].

    The remainder p(x) mod (x - z) is p(z); the quotient has degree one
    less than p. Coefficients and z live in F_order. Raises ValueError
    on an empty coefficient list.
    """
    # EXERCISE: implement this function.
    #
    # q(x) = (p(x) - p(z)) / (x - z), a polynomial because x - z divides
    # p(x) - p(z). Synthetic division computes it in one downward pass:
    # carry starts at 0, and for each index i from the top down to 1, carry
    # becomes coeffs[i] + carry * z modulo order and lands in q[i - 1]. The
    # pass stops before index 0 because that coefficient is absorbed into
    # the remainder, which is p(z), so the quotient has degree one less than
    # p. Reject an empty coefficient list.
    #
    # Reference: Chapter 32, 'KZG: trapdoor in the structured reference string'
    #
    # Proved by:
    #   tests/ch32/test_toy_kzg.py
    raise NotImplementedError("exercise: quotient")


def open_at(coeffs: list[int], z: int, srs: SRS) -> tuple[int, int]:
    """Open the commitment at evaluation point ``z`` in F_order.

    Returns ``(y, witness)`` where ``y = p(z) mod order`` and
    ``witness`` is the commitment to the quotient polynomial
    q(x) = (p(x) - y) / (x - z).
    """
    # EXERCISE: implement this function.
    #
    # Return (y, W) where y = p(z) in F_order and W is the commitment to the
    # quotient polynomial q(x) = (p(x) - y) / (x - z). The witness is one
    # group element, the same size as the commitment itself, which is what
    # makes KZG openings constant-size in the degree.
    #
    # Reference: Chapter 32, 'KZG: trapdoor in the structured reference string'
    #
    # Proved by:
    #   tests/ch32/test_toy_kzg.py
    raise NotImplementedError("exercise: open_at")


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
    # EXERCISE: implement this function.
    #
    # Real KZG checks the pairing equation e(C / g^y, g_2) = e(W, g_2^tau /
    # g_2^z). This toy builds no pairing, so it evaluates the same identity
    # with tau in hand: compute C * g^(-y) on one side and W^(tau - z) on
    # the other, both in the group, and compare. Reduce the negated y and
    # the difference tau - z modulo the subgroup order before
    # exponentiating. A production verifier never sees tau; this routine
    # exists so correctness can be demonstrated and so forge_opening has
    # something to fool.
    #
    # Reference: Chapter 32, 'KZG: trapdoor in the structured reference string' and Exercise E2
    #
    # Proved by:
    #   tests/ch32/test_toy_kzg.py
    raise NotImplementedError("exercise: verify_with_trapdoor")


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
    # EXERCISE: implement this function.
    #
    # The SRS publishes g at index 0 and g^tau at index 1, so recovering tau
    # is a discrete logarithm and nothing more. Shor solves it in time
    # polynomial in log q; here brute force over [1, order - 1] stands in,
    # 1013 candidates, and returns the identical value a quantum adversary
    # would obtain. Raise ValueError when the SRS is too short to contain
    # g^tau at all rather than returning a value that was never searched
    # for.
    #
    # Reference: Chapter 32, 'KZG: trapdoor in the structured reference string'
    #
    # Proved by:
    #   tests/ch32/test_toy_kzg.py
    raise NotImplementedError("exercise: shor_recover_tau")


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
