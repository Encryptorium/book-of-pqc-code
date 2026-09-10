"""Bit-margin arithmetic for the Chapter 35 case studies.

The chapter prints five of these routines as listings. Three more are here
because the chapter states them in prose but never prints them, or printed
them once and no longer does: the three decoding radii as one function, the
composed FRI budget with its three terms exposed rather than summed away, and
the approximate DFMS20 width earlier editions printed, kept so the gap to the
exact form stays measurable.
"""

import math
from dataclasses import dataclass

__all__ = [
    "REGIMES",
    "MarginTerms",
    "bit_margin_pairing",
    "composed_margin",
    "decoding_radius",
    "dfms20_exact_cbits",
    "dfms20_required_cbits",
    "query_miss_bits",
    "shor_pairing_margin",
    "stark_classical_margin",
]

# The three proximity radii Ch 34 Section 5.1 names, in increasing order.
# BCIKS Theorem 1.2 proves the proximity gap strictly below "johnson", and the
# chapter's model evaluates at it; the capacity radius rests on conjectures
# Crites and Stewart disproved in 2025.
REGIMES = ("unique", "johnson", "capacity")


@dataclass(frozen=True)
class MarginTerms:
    """The composed FRI soundness budget with its terms kept apart.

    ``bad_beta``, ``per_round`` and ``consistency`` are base-2 logarithms of
    probabilities, so all three are negative and the least negative one is
    the term that dominates the sum.
    """

    bad_beta: float
    per_round: float
    consistency: float
    grinding: int
    total: float

    @property
    def dominant(self) -> str:
        """Name the term contributing most of the composed probability.

        The query terms are compared after grinding, because that is the
        form in which they enter the sum (Ch 34 Section 5.5).
        """
        # EXERCISE: implement this function.
        #
        # Name which of bad_beta, per_round and consistency contributes most
        # of the composed probability. The three fields are logarithms of
        # probabilities and therefore negative, so the dominant term is the
        # largest, meaning the least negative, not the smallest. Compare
        # bad_beta against per_round minus grinding and consistency minus
        # grinding, because that is the form in which the three enter the
        # sum: grinding attenuates the two query terms and leaves bad_beta
        # alone. Return its field name as a string. This is the quantity the
        # chapter's prose asks for when it asks which term a parameter
        # change actually moves, and getting the sign convention backwards
        # is the whole difficulty.
        #
        # Reference: Chapter 35, 'The (L2 x L4) grid and bit-margin arithmetic' (Blocks 3 and 4)
        #
        # Proved by:
        #   tests/ch35/test_margins.py
        raise NotImplementedError("exercise: MarginTerms.dominant")


def bit_margin_pairing(field_bit: int) -> int:
    """Post-quantum bit margin of a pairing-based L2, which is zero."""
    if field_bit <= 0:
        raise ValueError("field_bit must be positive")
    return 0


def shor_pairing_margin(curve_bits: int) -> int:
    """The same result named for a concrete deployed curve."""
    if curve_bits <= 0:
        raise ValueError("curve_bits must be positive")
    return 0


def decoding_radius(rho: float, regime: str) -> float:
    """Return the relative decoding radius ``delta_0`` for a code rate.

    ``unique`` is the unique-decoding radius ``(1 - rho) / 2``, ``johnson``
    the Johnson / Guruswami-Sudan list-decoding radius ``1 - sqrt(rho)``,
    and ``capacity`` the capacity bound ``1 - rho``.
    """
    # EXERCISE: implement this function.
    #
    # Return the relative decoding radius delta_0 for a code rate rho. Three
    # regimes, and the chapter's aside names all three: 'unique' is the
    # unique-decoding radius (1 - rho) / 2, below which every received word
    # decodes to at most one codeword; 'johnson' is the Johnson /
    # Guruswami-Sudan list-decoding radius 1 - sqrt(rho), strictly below
    # which BCIKS Theorem 1.2 proves the proximity gap, and at which the
    # chapter's model reads its terms; 'capacity' is 1 - rho, which
    # production pipelines parameterised toward on the strength of
    # conjectures Crites and Stewart disproved in 2025. Reject a rate
    # outside the open interval (0, 1) and a regime name not in REGIMES. The
    # three values are strictly ordered at every rate, and a test holds them
    # that way, so a construction that collapses two of them will fail
    # rather than merely lose precision.
    #
    # Reference: Chapter 35, 'The (L2 x L4) grid and bit-margin arithmetic' (the decoding-radius note)
    #
    # Proved by:
    #   tests/ch35/test_margins.py
    raise NotImplementedError("exercise: decoding_radius")


def composed_margin(field_bits: int, L: int, N: int, mu: int, r_FRI: int,
                    grinding: int, regime: str = "johnson") -> MarginTerms:
    """Compose the FRI soundness budget, keeping the three terms apart.

    ``stark_classical_margin`` is this routine's ``total`` at the Johnson
    radius; the chapter prints that form, and the terms behind it are what
    the prose discusses when it asks which one dominates.
    """
    # EXERCISE: implement this function.
    #
    # Compose the three-term FRI soundness budget of Ch 34 Section 5.5 and
    # return the terms rather than only their sum. The bad-beta union bound
    # over fold rounds is log2(r_FRI * (N + 1)) - field_bits. The per-round
    # proximity term is mu * log2(1 - delta_0), with delta_0 from
    # decoding_radius at the chosen regime. The query-consistency term is mu
    # * log2((L - 1) / N), because two distinct polynomials of degree below
    # L agree at no more than L - 1 of the N LDE points. All three are
    # base-2 logarithms of probabilities, so raise 2 to each, but attenuate
    # only the two query terms by the grinding factor: the composed
    # probability is 2^bad_beta + 2^-grinding * (2^per_round +
    # 2^consistency). Ch 34 Section 5.5 puts the 2^-g factor on eps_query
    # alone, and a forger who wins on a bad fold challenge never re-grinds,
    # so grinding does not touch bad_beta. Take the negative log2 of that
    # sum and round to one decimal. This is the chapter's three-term model,
    # not BCIKS Theorem 1.2's error term, which is undefined at zero slack
    # from the Johnson radius. Validate before computing: every count
    # positive, grinding non-negative, and L strictly less than N. The
    # consistency term is numerically inert at every parameter point the
    # chapter prints, so a test reads it directly rather than through the
    # total.
    #
    # Reference: Chapter 35, 'The (L2 x L4) grid and bit-margin arithmetic' (Blocks 3 and 4)
    #
    # Proved by:
    #   tests/ch35/test_margins.py
    raise NotImplementedError("exercise: composed_margin")


def stark_classical_margin(field_bits: int, L: int, N: int, mu: int,
                           r_FRI: int, grinding: int) -> float:
    """The listing form: the composed margin at the Johnson radius."""
    return composed_margin(field_bits, L, N, mu, r_FRI, grinding,
                           regime="johnson").total


def dfms20_required_cbits(k_target: int, q_bits: int, r_FS: int) -> int:
    """Approximate DFMS20 per-round challenge width, ``2 q + ceil(k / r)``.

    The form earlier editions printed; the chapter now prints the exact one.
    """
    if k_target <= 0 or r_FS <= 0 or q_bits < 0:
        raise ValueError("k_target, r_FS must be positive; q_bits non-negative")
    return 2 * q_bits + math.ceil(k_target / r_FS)


def dfms20_exact_cbits(k_target: int, q_bits: int, r_FS: int) -> int:
    """Exact per-round width under the DFMS20-shaped model, ``2 log2(2q + 1) + k / r``.

    Exact is arithmetic about the model and not a certified QROM bound: the
    model drops the corollary's additive challenge-space term (Ch 33).
    The approximation drops the ``log2(2q + 1)`` correction as well. That log is
    strictly greater than ``q_bits + 1`` by a vanishing amount (Ch 33), so a
    bound whose float value lands on an integer sits just above it and still
    needs the next width up; at these ``q_bits`` the excess is below float
    resolution, so the integer case is tested outright.
    """
    if k_target <= 0 or r_FS <= 0 or q_bits < 0:
        raise ValueError("k_target, r_FS must be positive; q_bits non-negative")
    exact = 2.0 * math.log2(2 * (2 ** q_bits) + 1) + k_target / r_FS
    width = math.ceil(exact)
    return width + 1 if width == exact else width


def query_miss_bits(n_queries: int, pow_bits: int, log_blowup: int,
                    regime: str) -> float:
    """Query-miss margin alone, for a published (queries, grinding, rate) set."""
    if min(n_queries, log_blowup) <= 0 or pow_bits < 0:
        raise ValueError("n_queries, log_blowup positive; pow_bits non-negative")
    delta_0 = decoding_radius(2.0 ** (-log_blowup), regime)
    return round(-n_queries * math.log2(1.0 - delta_0) + pow_bits, 1)
