"""Bit-margin arithmetic for the Chapter 35 case studies.

The chapter prints four of these routines as listings. Two more are here
because the chapter states them in prose but never prints them: the three
decoding radii as one function, and the composed FRI budget with its three
terms exposed rather than summed away.
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
# Only "johnson" carries a proven proximity gap (BCIKS Theorem 1.2); the
# capacity radius rests on conjectures Crites and Stewart disproved in 2025.
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
        """Name the term contributing most of the composed probability."""
        # EXERCISE: implement this function.
        #
        # Name which of bad_beta, per_round and consistency contributes most
        # of the composed probability. The three fields are logarithms of
        # probabilities and therefore negative, so the dominant term is the
        # largest, meaning the least negative, not the smallest. Return its
        # field name as a string. This is the quantity the chapter's prose
        # asks for when it asks which term a parameter change actually
        # moves, and getting the sign convention backwards is the whole
        # difficulty.
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
    # Guruswami-Sudan list-decoding radius 1 - sqrt(rho), which is where
    # BCIKS Theorem 1.2 proves the proximity gap; 'capacity' is 1 - rho,
    # which production pipelines parameterised toward on the strength of
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
    # base-2 logarithms of probabilities, so raise 2 to each, add, take the
    # negative log2 of the sum, add the grinding bits, and round to one
    # decimal. Validate before computing: every count positive, grinding
    # non-negative, and L strictly less than N. The consistency term is
    # numerically inert at every parameter point the chapter prints, so a
    # test reads it directly rather than through the total.
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
    """Approximate DFMS20 per-round challenge width, ``2 q + ceil(k / r)``."""
    if k_target <= 0 or r_FS <= 0 or q_bits < 0:
        raise ValueError("k_target, r_FS must be positive; q_bits non-negative")
    return 2 * q_bits + math.ceil(k_target / r_FS)


def dfms20_exact_cbits(k_target: int, q_bits: int, r_FS: int) -> int:
    """Exact DFMS20 per-round width, ``2 log2(2q + 1) + k / r``.

    The approximation drops the ``log2(2q + 1)`` correction, which is a
    shade over ``q_bits + 1``. The strict inequality is what forces the
    round up, so an exact bound landing on an integer still needs the next
    width above it.
    """
    # EXERCISE: implement this function.
    #
    # The exact DFMS20 per-round challenge width, c_bits >= 2 log2(2q + 1) +
    # k / r, where the printed dfms20_required_cbits computes the
    # approximation 2 q_bits + ceil(k / r). Take q as 2 raised to q_bits.
    # Because the bound is a strict inequality, an exact value that lands on
    # an integer needs the next width above it, not that integer: compute
    # the ceiling and add one when the ceiling equals the exact value. The
    # gap over the approximation is a little over two bits, which is the
    # correction the chapter's Block 3 comment says the approximation drops.
    # Same validation contract as the approximate form.
    #
    # Reference: Chapter 35, 'The (L2 x L4) grid and bit-margin arithmetic' (Block 3)
    #
    # Proved by:
    #   tests/ch35/test_margins.py
    raise NotImplementedError("exercise: dfms20_exact_cbits")


def query_miss_bits(n_queries: int, pow_bits: int, log_blowup: int,
                    regime: str) -> float:
    """Query-miss margin alone, for a published (queries, grinding, rate) set."""
    if min(n_queries, log_blowup) <= 0 or pow_bits < 0:
        raise ValueError("n_queries, log_blowup positive; pow_bits non-negative")
    delta_0 = decoding_radius(2.0 ** (-log_blowup), regime)
    return round(-n_queries * math.log2(1.0 - delta_0) + pow_bits, 1)
