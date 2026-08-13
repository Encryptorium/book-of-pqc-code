"""Toy FRI commitment for Chapter 32.

Builds FRI (Fast Reed-Solomon Interactive Oracle Proof of Proximity)
as a commitment primitive over a small prime field. This module is
pedagogical, not production: Chapter 34 covers FRI-from-scratch at the
depth required to wrap it into a STARK. Ch 32's scope is FRI as a
polynomial commitment, demonstrating three things:

1. The folding structure: given f: L -> F, compute f': L^2 -> F of
   roughly half the domain size via f'(y) = (f(x) + f(-x))/2 +
   beta * (f(x) - f(-x))/(2x), where y = x^2 and beta is a verifier-
   supplied challenge.
2. The consistency check: after log_2(|L|) folds, the prover commits
   to a constant; the verifier queries consistency at random points
   along the folding chain.
3. The proximity-gap structure: a function far from low-degree passes
   the consistency check with negligible probability, bounded by the
   Ben-Sasson-Bentov-Horesh-Riabzev proximity argument
   (information-theoretic, unaffected by quantum adversaries on this
   side of the commitment; the quantum pressure on FRI-based SNARKs
   enters via the Merkle layer and the QROM compilation, not via the
   proximity gap itself).

The protocol below is interactive: the verifier sends challenges. A
Fiat-Shamir compilation belongs in Ch 33, and the full STARK pipeline
in Ch 34.
"""

from __future__ import annotations

from dataclasses import dataclass


# Default prime: 97 has p - 1 = 96 = 2^5 * 3. The 2^5 = 32 power-of-two
# subgroup is enough to demonstrate log_2(32) = 5 folding rounds. Fast
# to operate on.
DEFAULT_PRIME = 97


def mod_inv(a: int, prime: int) -> int:
    """Compute the multiplicative inverse of ``a`` modulo ``prime``."""
    if a % prime == 0:
        raise ValueError("no inverse for zero")
    return pow(a, -1, prime)


def eval_poly(coeffs: list[int], x: int, prime: int) -> int:
    """Horner-rule evaluation of a polynomial at ``x`` modulo prime."""
    result = 0
    for c in reversed(coeffs):
        result = (result * x + c) % prime
    return result


def generate_domain(size: int, generator: int, prime: int) -> list[int]:
    """Build a size-``size`` multiplicative subgroup coset.

    ``generator`` must have order at least ``size`` in F_prime^*. The
    resulting domain ``L`` is closed under negation when ``size`` is a
    power of two, which is the requirement for FRI folding to be
    well-defined. Raises ValueError for non-power-of-two sizes or
    when the generator has insufficient order.
    """
    # EXERCISE: implement this function.
    #
    # Collect the powers of generator starting at 1 until the list holds
    # size elements. Reject a size that is not a power of two above one, and
    # reject a generator whose order does not match the requested size:
    # after size steps the running product must be back at 1, and if it is
    # not, the list is not the subgroup it claims to be. The power-of-two
    # structure is what makes the domain closed under negation, so that
    # -domain[i] is domain[i + size/2], which is the pairing the fold relies
    # on.
    #
    # Reference: Chapter 32, 'FRI: proximity as commitment'
    #
    # Proved by:
    #   tests/ch32/test_fri.py
    raise NotImplementedError("exercise: generate_domain")


@dataclass
class FRIFoldRound:
    """One round of the folding chain.

    ``evaluations`` is the function values f_i: L_i -> F. ``domain`` is
    L_i. ``beta`` is the verifier's challenge for this round (the
    challenge that produced ``evaluations`` from the prior round's
    oracle).
    """

    domain: list[int]
    evaluations: list[int]
    beta: int


def fold_once(
    evaluations: list[int],
    domain: list[int],
    beta: int,
    prime: int,
) -> tuple[list[int], list[int]]:
    """Apply one FRI folding round.

    For each pair ``(x, -x)`` in ``domain``, compute
    ``f'(x^2) = (f(x) + f(-x))/2 + beta * (f(x) - f(-x))/(2x)``, where
    beta is the verifier-supplied challenge. Returns the folded
    evaluations and the new domain ``{x^2 : x in first half of L}``.
    Requires the domain to be ordered so that index i+|L|/2 holds -L[i].
    """
    # EXERCISE: implement this function.
    #
    # For each pair (x, -x), f'(x^2) = (f(x) + f(-x))/2 + beta * (f(x) -
    # f(-x))/(2x). The two halves are the even and odd components of f under
    # the identity f(x) = f_e(x^2) + x * f_o(x^2), and beta is the
    # verifier's linear-combination challenge collapsing them into one
    # function on the squared domain. The subgroup layout puts -domain[i] at
    # index i + n/2, so pair index i against index i + half, and build the
    # new domain by squaring x. Invert 2 and x modulo the prime rather than
    # dividing; the characteristic must not be 2 or 1/2 would not exist.
    # Reject mismatched lengths and a domain size that is not a power of two
    # above one.
    #
    # Reference: Chapter 32, 'FRI: proximity as commitment'
    #
    # Proved by:
    #   tests/ch32/test_fri.py
    raise NotImplementedError("exercise: fold_once")


def commit(
    coeffs: list[int],
    domain: list[int],
    prime: int = DEFAULT_PRIME,
) -> list[int]:
    """Produce the Reed-Solomon codeword over ``domain``.

    The FRI commitment to a polynomial is its evaluation vector on the
    public domain. The prover subsequently commits to this vector (in
    production, via a Merkle root; in this toy, the list is returned
    directly so folding can be inspected).
    """
    return [eval_poly(coeffs, x, prime) for x in domain]


def fold_to_constant(
    initial_evals: list[int],
    initial_domain: list[int],
    betas: list[int],
    prime: int = DEFAULT_PRIME,
) -> list[FRIFoldRound]:
    """Fold an initial evaluation vector down to a constant.

    Applies ``len(betas)`` folding rounds in sequence. The final round
    must have a domain of size 2 and an evaluations list of length 2;
    if the initial codeword is a polynomial of degree strictly less
    than ``2^(log2(N) - len(betas))``, the final folded values are
    constant across the final domain. Returns the list of intermediate
    rounds including the initial state.
    """
    # EXERCISE: implement this function.
    #
    # Run one fold per beta in sequence, each halving the domain. The round
    # count is fixed by the starting size, log2(N) folds to reach a single
    # point, so reject a beta list of any other length rather than stopping
    # the chain early. Return the whole chain including the initial state as
    # round 0 with beta 0, because the verifier's consistency check reads
    # consecutive pairs of rounds and needs the unfolded codeword as the
    # first of them.
    #
    # Reference: Chapter 32, 'FRI: proximity as commitment'
    #
    # Proved by:
    #   tests/ch32/test_fri.py
    raise NotImplementedError("exercise: fold_to_constant")


def query_consistency(
    rounds: list[FRIFoldRound],
    query_index: int,
    prime: int = DEFAULT_PRIME,
) -> bool:
    """Check that consecutive fold rounds are consistent at ``query_index``.

    For each round r and its successor r+1, recompute the folded value
    at the projected index from the two evaluations at the sibling
    pair ``(L[i], L[i + |L|/2])`` of round r, and compare to the
    evaluation at the corresponding index in round r+1. Returns True
    if every consecutive pair is consistent, False otherwise.
    """
    # EXERCISE: implement this function.
    #
    # Re-derive each fold rather than trusting the prover's word for it. For
    # every consecutive pair of rounds, reduce the query index modulo the
    # current half-size to find the pair position, read f(x) and f(-x) at
    # that position and that position plus half, apply the same folding
    # formula using the successor round's beta, and compare against the
    # successor's evaluation at the pair position. Return False on the first
    # mismatch. Carry the pair position forward as the index for the next
    # round. A prover who tampers with one evaluation and leaves the rest of
    # the chain honest fails at exactly the query that touches it, which is
    # the spot-check the proximity-gap argument bounds.
    #
    # Reference: Chapter 32, 'FRI: proximity as commitment'
    #
    # Proved by:
    #   tests/ch32/test_fri.py
    raise NotImplementedError("exercise: query_consistency")
